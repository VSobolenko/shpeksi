"""Tenant (restaurant) isolation tests.

The backend talks to MongoDB through Beanie, but the test suite has no database
available. To still verify resolver behaviour (restaurant filtering and the
FORBIDDEN guards) these tests replace the Beanie query surface with a small
in-memory store. Every tenant filter in the resolvers is a plain dict, which
keeps the fake simple and makes the tests independent of the Beanie version.
"""

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from beanie import PydanticObjectId
from graphql import GraphQLError

from app.graphql.context import Context, get_context, resolve_restaurant
from app.graphql.schema import schema
from app.models import (
    Addon,
    AdminAccount,
    Category,
    Configuration,
    Coupon,
    Food,
    Option,
    Order,
    Restaurant,
    User,
)
from app.services.auth import create_access_token

MODELS = [
    Addon,
    AdminAccount,
    Category,
    Configuration,
    Coupon,
    Food,
    Option,
    Order,
    Restaurant,
    User,
]


# --------------------------------------------------------------------------- #
# In-memory Beanie query stub
# --------------------------------------------------------------------------- #


def _eq(actual, expected) -> bool:
    if actual is None or expected is None:
        return actual is None and expected is None
    return str(actual) == str(expected)


def _matches(doc, query: dict) -> bool:
    for key, expected in query.items():
        actual = getattr(doc, "id", None) if key == "_id" else getattr(doc, key, None)
        if isinstance(expected, dict):
            if "$in" in expected and not any(_eq(actual, v) for v in expected["$in"]):
                return False
            if "$ne" in expected and _eq(actual, expected["$ne"]):
                return False
        elif not _eq(actual, expected):
            return False
    return True


class FakeQuery:
    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, key):
        reverse = key.startswith("-")
        field = key[1:] if reverse else key
        self._docs.sort(key=lambda d: (getattr(d, field, None) is None, str(getattr(d, field, None))), reverse=reverse)
        return self

    def skip(self, count):
        self._docs = self._docs[count:]
        return self

    def limit(self, count):
        self._docs = self._docs[:count]
        return self

    async def to_list(self):
        return list(self._docs)

    async def count(self):
        return len(self._docs)


class FakeDB:
    def __init__(self):
        self.data: dict = {}

    def docs(self, model) -> list:
        return self.data.setdefault(model, [])

    @staticmethod
    def _merge(filters) -> dict:
        query: dict = {}
        for expr in filters:
            if isinstance(expr, dict):
                query.update(expr)
        return query

    def find(self, model, *filters) -> FakeQuery:
        query = self._merge(filters)
        return FakeQuery([d for d in self.docs(model) if _matches(d, query)])

    def find_all(self, model) -> FakeQuery:
        return FakeQuery(list(self.docs(model)))

    def find_one(self, model, *filters):
        query = self._merge(filters)
        for doc in self.docs(model):
            if _matches(doc, query):
                return doc
        return None

    def get(self, model, document_id):
        for doc in self.docs(model):
            if _eq(getattr(doc, "id", None), document_id):
                return doc
        return None

    def insert(self, doc):
        if getattr(doc, "id", None) is None:
            doc.id = PydanticObjectId()
        self.docs(type(doc)).append(doc)
        return doc

    def save(self, doc):
        if doc not in self.docs(type(doc)):
            self.docs(type(doc)).append(doc)
        return doc

    def delete(self, doc):
        rows = self.docs(type(doc))
        if doc in rows:
            rows.remove(doc)


def _make_find_one(model, store):
    async def _find_one(*filters):
        return store.find_one(model, *filters)

    return _find_one


def _make_get(model, store):
    async def _get(document_id, *args):
        return store.get(model, document_id)

    return _get


def _make_insert(store):
    async def _insert(self):
        return store.insert(self)

    return _insert


def _make_save(store):
    async def _save(self):
        return store.save(self)

    return _save


def _make_delete(store):
    async def _delete(self):
        return store.delete(self)

    return _delete


class _OfflineSettings:
    """Stand-in for Beanie's ItemSettings with no database behind it.

    Constructing any Beanie Document calls ``cls.get_motor_collection()`` from
    ``Document.__init__`` (beanie/odm/documents.py), which reads
    ``settings.motor_collection``. Nothing here is ever used for real I/O — every
    query method below is replaced by the in-memory store — so unknown handles
    resolve to a placeholder instead of exploding.
    """

    name = "offline"
    bson_encoders: dict = {}

    def __getattr__(self, item):
        return object()


@pytest.fixture
def db(monkeypatch):
    store = FakeDB()
    for model in MODELS:
        monkeypatch.setattr(model, "_document_settings", _OfflineSettings())
        monkeypatch.setattr(model, "find", lambda *a, m=model, s=store: s.find(m, *a))
        monkeypatch.setattr(model, "find_all", lambda *a, m=model, s=store: s.find_all(m))
        monkeypatch.setattr(model, "find_one", _make_find_one(model, store))
        monkeypatch.setattr(model, "get", _make_get(model, store))
        monkeypatch.setattr(model, "insert", _make_insert(store))
        monkeypatch.setattr(model, "save", _make_save(store))
        monkeypatch.setattr(model, "delete", _make_delete(store))
    return store


@pytest.fixture
def data(db):
    """Two fully-populated restaurants (A and B)."""
    a = PydanticObjectId()
    b = PydanticObjectId()

    restaurant_a = Restaurant(name="Restaurant A", slug="resto-a", is_active=True)
    restaurant_a.id = a
    restaurant_b = Restaurant(name="Restaurant B", slug="resto-b", is_active=True)
    restaurant_b.id = b
    db.insert(restaurant_a)
    db.insert(restaurant_b)

    user_a = User(name="User A", email="user-a@x.com", restaurant=a)
    user_b = User(name="User B", email="user-b@x.com", restaurant=b)
    db.insert(user_a)
    db.insert(user_b)

    food_a = Food(title="Food A", restaurant=a)
    food_b = Food(title="Food B", restaurant=b)
    db.insert(food_a)
    db.insert(food_b)

    category_a = Category(title="Category A", restaurant=a)
    db.insert(category_a)

    order_a = Order(
        order_id="A-1",
        user=user_a.id,
        restaurant=a,
        createdAt=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
    )
    order_b = Order(
        order_id="B-1",
        user=user_b.id,
        restaurant=b,
        createdAt=datetime(2026, 9, 1, 11, 0, tzinfo=timezone.utc),
    )
    db.insert(order_a)
    db.insert(order_b)

    staff_a = AdminAccount(email="staff-a@x.com", role="staff", restaurant=a)
    staff_b = AdminAccount(email="staff-b@x.com", role="staff", restaurant=b)
    db.insert(staff_a)
    db.insert(staff_b)

    coupon_a = Coupon(code="A10", discount=10.0, restaurant=a)
    coupon_b = Coupon(code="B10", discount=10.0, restaurant=b)
    db.insert(coupon_a)
    db.insert(coupon_b)

    return SimpleNamespace(
        a=a,
        b=b,
        user_a=user_a,
        user_b=user_b,
        food_a=food_a,
        food_b=food_b,
        category_a=category_a,
        order_a=order_a,
        order_b=order_b,
        staff_a=staff_a,
        coupon_a=coupon_a,
        coupon_b=coupon_b,
    )


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


class _FakeRequest:
    def __init__(self, headers=None):
        self.headers = headers or {}


def make_ctx(role, restaurant=None, user_id="caller-1") -> Context:
    ctx = Context()
    ctx.user_id = user_id
    ctx.role = role
    ctx.restaurant_id = str(restaurant) if restaurant else None
    return ctx


def run(query, ctx=None, variables=None):
    return asyncio.run(
        schema.execute(query, variable_values=variables, context_value=ctx)
    )


def error_code(result) -> str:
    assert result.errors, "expected a GraphQL error"
    return result.errors[0].extensions.get("code")


# --------------------------------------------------------------------------- #
# Director isolation
# --------------------------------------------------------------------------- #


def test_director_only_sees_own_orders(data):
    result = run("query { allOrders { _id order_id } }", make_ctx("director", data.a))
    assert result.errors is None
    assert [o["_id"] for o in result.data["allOrders"]] == [str(data.order_a.id)]


def test_director_order_count_is_scoped(data):
    result = run("query { orderCount }", make_ctx("director", data.a))
    assert result.errors is None
    assert result.data["orderCount"] == 1


def test_director_only_sees_own_users(data):
    result = run("query { users { _id } }", make_ctx("director", data.a))
    assert result.errors is None
    assert [u["_id"] for u in result.data["users"]] == [str(data.user_a.id)]


def test_director_only_sees_own_foods(data):
    result = run("query { foods { _id title } }", make_ctx("director", data.a))
    assert result.errors is None
    assert [f["title"] for f in result.data["foods"]] == ["Food A"]


def test_director_only_sees_own_staff(data):
    result = run("query { adminStaffs { _id email } }", make_ctx("director", data.a))
    assert result.errors is None
    assert [s["email"] for s in result.data["adminStaffs"]] == ["staff-a@x.com"]


def test_director_cannot_load_other_restaurant_order_by_id(data):
    result = run(
        "query($id: String!) { order(id: $id) { order_id } }",
        make_ctx("customer", data.a, user_id=str(data.user_a.id)),
        {"id": str(data.order_b.id)},
    )
    assert error_code(result) == "FORBIDDEN"


def test_director_cannot_delete_other_restaurant_food(data):
    result = run(
        "mutation($id: String!) { deleteFood(id: $id) { _id } }",
        make_ctx("director", data.a),
        {"id": str(data.food_b.id)},
    )
    assert error_code(result) == "FORBIDDEN"


def test_food_by_ids_filters_other_restaurant(data):
    result = run(
        "query($ids: [String!]!) { foodByIds(ids: $ids) { _id title } }",
        make_ctx("customer", data.a),
        {"ids": [str(data.food_a.id), str(data.food_b.id)]},
    )
    assert result.errors is None
    assert [f["_id"] for f in result.data["foodByIds"]] == [str(data.food_a.id)]


# --------------------------------------------------------------------------- #
# Roles
# --------------------------------------------------------------------------- #


def test_staff_cannot_call_director_resolver(data):
    result = run("query { adminStaffs { _id } }", make_ctx("staff", data.a))
    assert error_code(result) == "FORBIDDEN"


def test_missing_restaurant_context_is_rejected(data):
    result = run("query { foods { _id } }", make_ctx("customer"))
    assert error_code(result) == "RESTAURANT_REQUIRED"


# --------------------------------------------------------------------------- #
# Customer app (x-restaurant-id header)
# --------------------------------------------------------------------------- #


def test_customer_header_scopes_catalog(data):
    ctx = asyncio.run(get_context(_FakeRequest({"x-restaurant-id": "resto-a"})))
    assert ctx.restaurant_id == str(data.a)
    assert ctx.restaurant_slug == "resto-a"
    result = run("query { foods { _id } }", ctx)
    assert result.errors is None
    assert [f["_id"] for f in result.data["foods"]] == [str(data.food_a.id)]


def test_token_restaurant_wins_over_header(data):
    token = create_access_token("director-b", "director", restaurant_id=str(data.b))
    ctx = asyncio.run(
        get_context(
            _FakeRequest(
                {"x-restaurant-id": "resto-a", "authorization": f"Bearer {token}"}
            )
        )
    )
    assert ctx.restaurant_id == str(data.b)


# --------------------------------------------------------------------------- #
# Websocket subscriptions
#
# get_context runs when the connection opens, which for a websocket is *before*
# connection_init delivers its payload — so the tenant has to be resolvable at
# resolver time as well, or subscriptions would run unscoped.
# --------------------------------------------------------------------------- #


def _info(ctx):
    return SimpleNamespace(context=ctx)


def test_websocket_slug_in_connection_params_resolves_restaurant(data):
    ctx = Context()
    assert ctx.restaurant_id is None
    ctx.connection_params = {"restaurant": "resto-b"}
    assert asyncio.run(resolve_restaurant(_info(ctx))) == str(data.b)


def test_websocket_token_in_connection_params_beats_slug(data):
    token = create_access_token("director-a", "director", restaurant_id=str(data.a))
    ctx = Context()
    ctx.connection_params = {
        "authorization": f"Bearer {token}",
        "restaurant": "resto-b",
    }
    assert asyncio.run(resolve_restaurant(_info(ctx))) == str(data.a)


def test_websocket_without_tenant_is_rejected(data):
    ctx = Context()
    ctx.connection_params = {"restaurant": "does-not-exist"}
    with pytest.raises(GraphQLError) as excinfo:
        asyncio.run(resolve_restaurant(_info(ctx)))
    assert excinfo.value.extensions.get("code") == "RESTAURANT_REQUIRED"


# --------------------------------------------------------------------------- #
# Configuration is one document per restaurant
# --------------------------------------------------------------------------- #


def test_configuration_is_created_per_restaurant(data, db):
    result = run("query { configuration { _id order_id_prefix } }", make_ctx("director", data.a))
    assert result.errors is None
    created = db.find_one(Configuration, {"restaurant": data.a})
    assert created is not None
    assert db.find_one(Configuration, {"restaurant": data.b}) is None


# --------------------------------------------------------------------------- #
# Writes stamp the tenant
# --------------------------------------------------------------------------- #


def test_create_category_stamps_restaurant(data, db):
    result = run(
        'mutation { createCategory(category: { title: "New", description: "" }) { _id } }',
        make_ctx("director", data.a),
    )
    assert result.errors is None
    created = db.get(Category, result.data["createCategory"]["_id"])
    assert str(created.restaurant) == str(data.a)


def test_create_admin_staff_binds_restaurant(data, db):
    result = run(
        'mutation { createAdminStaff(email: "new-staff@x.com", password: "secret", name: "New") { _id } }',
        make_ctx("director", data.a),
    )
    assert result.errors is None
    account = db.find_one(AdminAccount, {"email": "new-staff@x.com"})
    assert str(account.restaurant) == str(data.a)


# --------------------------------------------------------------------------- #
# Superadmin restaurant management
# --------------------------------------------------------------------------- #


def test_create_restaurant_requires_superadmin(data):
    result = run(
        "mutation($n: String!, $s: String!, $e: String!, $p: String!) {"
        " createRestaurant(name: $n, slug: $s, directorEmail: $e, directorPassword: $p) { _id } }",
        make_ctx("director", data.a),
        {"n": "New", "s": "new-resto", "e": "d@x.com", "p": "secret"},
    )
    assert error_code(result) == "FORBIDDEN"


def test_create_restaurant_rejects_duplicate_slug(data):
    result = run(
        "mutation($n: String!, $s: String!, $e: String!, $p: String!) {"
        " createRestaurant(name: $n, slug: $s, directorEmail: $e, directorPassword: $p) { _id } }",
        make_ctx("superadmin"),
        {"n": "Dup", "s": "resto-a", "e": "d@x.com", "p": "secret"},
    )
    assert result.errors
    assert "slug already exists" in str(result.errors[0])


def test_create_restaurant_binds_director(data, db):
    result = run(
        "mutation($n: String!, $s: String!, $e: String!, $p: String!) {"
        " createRestaurant(name: $n, slug: $s, directorEmail: $e, directorPassword: $p) { _id slug } }",
        make_ctx("superadmin"),
        {"n": "New", "s": "new-resto", "e": "director-new@x.com", "p": "secret"},
    )
    assert result.errors is None
    director = db.find_one(AdminAccount, {"email": "director-new@x.com"})
    assert director is not None
    assert str(director.restaurant) == result.data["createRestaurant"]["_id"]
    assert director.role == "director"


def test_create_restaurant_director_requires_superadmin(data):
    result = run(
        "mutation($r: String!, $e: String!, $p: String!) {"
        " createRestaurantDirector(restaurantId: $r, email: $e, password: $p) { _id } }",
        make_ctx("director", data.a),
        {"r": str(data.a), "e": "new-d@x.com", "p": "secret"},
    )
    assert error_code(result) == "FORBIDDEN"


def test_create_restaurant_director_promotes_existing_account(data, db):
    """Recovering a tenant whose director was lost must not need a new email."""
    result = run(
        "mutation($r: String!, $e: String!, $p: String!) {"
        " createRestaurantDirector(restaurantId: $r, email: $e, password: $p) { _id role } }",
        make_ctx("superadmin"),
        {"r": str(data.b), "e": "staff-b@x.com", "p": "new-secret"},
    )
    assert result.errors is None
    account = db.find_one(AdminAccount, {"email": "staff-b@x.com"})
    assert account.role == "director"
    assert str(account.restaurant) == str(data.b)


# --------------------------------------------------------------------------- #
# Deleting a category that is still in use
# --------------------------------------------------------------------------- #


def test_delete_category_refuses_while_foods_reference_it(data):
    """Foods hold their category as a plain id, so deleting the category would
    orphan them (they vanish from the storefront and break the food list)."""
    data.food_a.category = data.category_a.id
    result = run(
        'mutation { deleteCategory(id: "%s") { _id } }' % data.category_a.id,
        make_ctx("director", data.a),
    )
    assert error_code(result) == "CATEGORY_NOT_EMPTY"
    assert result.errors[0].extensions.get("count") == 1


def test_delete_category_ignores_foods_of_other_restaurants(data, db):
    """A food in another tenant must not block the deletion."""
    food_b = db.find_one(Food, {"title": "Food B"})
    food_b.category = data.category_a.id
    result = run(
        'mutation { deleteCategory(id: "%s") { _id title } }' % data.category_a.id,
        make_ctx("director", data.a),
    )
    assert result.errors is None
    assert result.data["deleteCategory"]["title"] == "Category A"
    assert db.get(Category, data.category_a.id) is None


def test_delete_category_succeeds_once_the_foods_are_gone(data, db):
    data.food_a.category = data.category_a.id
    db.delete(data.food_a)
    result = run(
        'mutation { deleteCategory(id: "%s") { _id } }' % data.category_a.id,
        make_ctx("director", data.a),
    )
    assert result.errors is None
    assert db.get(Category, data.category_a.id) is None
