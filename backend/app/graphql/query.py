"""GraphQL Query resolvers (catalog, users, orders, config, dashboard)."""

from datetime import datetime, timedelta
from typing import List, Optional

import strawberry
from beanie import PydanticObjectId

from app.graphql.context import (
    ensure_tenant_access,
    require_admin,
    require_director,
    require_restaurant,
    require_superadmin,
    require_user,
)
from app.graphql.types import (
    AddonType,
    AdminStaffType,
    CategoryType,
    ConfigurationType,
    CouponType,
    DashboardData,
    DashboardOrders,
    DashboardSales,
    DashboardTotal,
    DailyOrder,
    DailyOrderData,
    DailySale,
    FoodType,
    OptionType,
    OrderType,
    RestaurantType,
    ReviewType,
    UserType,
    build_addon,
    build_category,
    build_configuration,
    build_food,
    build_option,
    build_order,
    build_restaurant,
    build_user,
    iso,
)
from app.models import (
    Addon,
    AdminAccount,
    Category,
    Coupon,
    Food,
    Option,
    Order,
    Restaurant,
    User,
)
from app.services.configuration import get_or_create_config
from app.services.orders import ORDER_STATUSES, PAYMENT_STATUSES


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _restaurant_oid(info) -> PydanticObjectId:
    """Active restaurant id as an ObjectId (raises RESTAURANT_REQUIRED)."""
    return PydanticObjectId(require_restaurant(info))


def _admin_restaurant_oid(info) -> PydanticObjectId:
    """Restaurant id for a dashboard caller (enforces an admin role first)."""
    require_admin(info)
    return _restaurant_oid(info)


def _director_restaurant_oid(info) -> PydanticObjectId:
    """Restaurant id for a director caller (enforces the director role first)."""
    require_director(info)
    return _restaurant_oid(info)


def _food_price_range(food: Food) -> list[float]:
    return [v.price for v in food.variations]


def _filter_orders_by_date(
    orders: List[Order], start: Optional[datetime], end: Optional[datetime]
) -> List[Order]:
    """Keep orders whose createdAt falls within [start, end) — where ``end`` is
    treated as the whole ending day (exclusive of the next midnight), so orders
    placed later on the ending date are still included."""
    if start:
        orders = [o for o in orders if o.createdAt and o.createdAt >= start]
    if end:
        end_exclusive = end + timedelta(days=1)
        orders = [o for o in orders if o.createdAt and o.createdAt < end_exclusive]
    return orders


async def _orders_in_range(
    restaurant_id: PydanticObjectId,
    starting_date: Optional[str],
    ending_date: Optional[str],
) -> List[Order]:
    orders = await Order.find({"restaurant": restaurant_id}).to_list()
    return _filter_orders_by_date(
        orders, _parse_date(starting_date), _parse_date(ending_date)
    )


async def _daily(orders: List[Order], with_amount: bool):
    buckets: dict = {}
    for o in orders:
        day = o.createdAt.date().isoformat() if o.createdAt else "unknown"
        entry = buckets.setdefault(day, {"count": 0, "amount": 0.0})
        entry["count"] += 1
        entry["amount"] += o.order_amount if o.payment_status == "PAID" else 0.0
    if with_amount:
        return [
            DailyOrderData(day=d, count=v["count"], amount=round(v["amount"], 2))
            for d, v in sorted(buckets.items())
        ]
    return [DailyOrder(day=d, count=v["count"]) for d, v in sorted(buckets.items())]


@strawberry.type
class Query:
    # --- Catalog ---------------------------------------------------------- #

    @strawberry.field
    async def categories(self, info: strawberry.Info) -> List[CategoryType]:
        restaurant = _restaurant_oid(info)
        categories = await Category.find({"restaurant": restaurant}).to_list()
        return [await build_category(c) for c in categories]

    @strawberry.field
    async def allCategories(
        self, info: strawberry.Info, page: Optional[int] = None
    ) -> List[CategoryType]:
        restaurant = _restaurant_oid(info)
        categories = await Category.find({"restaurant": restaurant}).to_list()
        return [await build_category(c) for c in categories]

    @strawberry.field
    async def foods(self, info: strawberry.Info, page: Optional[int] = None) -> List[FoodType]:
        restaurant = _restaurant_oid(info)
        foods = await Food.find({"restaurant": restaurant}).to_list()
        return [await build_food(f) for f in foods]

    @strawberry.field
    async def foodByCategory(
        self,
        info: strawberry.Info,
        category: str,
        onSale: Optional[bool] = None,
        inStock: Optional[bool] = None,
        min: Optional[float] = None,
        max: Optional[float] = None,
        search: Optional[str] = None,
    ) -> List[FoodType]:
        restaurant = _restaurant_oid(info)
        foods = await Food.find(
            {"category": PydanticObjectId(category), "restaurant": restaurant}
        ).to_list()
        result: list[FoodType] = []
        for food in foods:
            prices = _food_price_range(food)
            if inStock and not (food.stock and food.stock > 0):
                continue
            if onSale and not any(v.discounted > 0 for v in food.variations):
                continue
            if min is not None and not any(p >= min for p in prices):
                continue
            if max is not None and not any(p <= max for p in prices):
                continue
            if search and search.lower() not in (food.title or "").lower():
                continue
            result.append(await build_food(food))
        return result

    @strawberry.field
    async def foodByIds(self, info: strawberry.Info, ids: List[str]) -> List[FoodType]:
        restaurant = _restaurant_oid(info)
        foods = await Food.find(
            {"_id": {"$in": [PydanticObjectId(i) for i in ids]}, "restaurant": restaurant}
        ).to_list()
        return [await build_food(f) for f in foods]

    @strawberry.field
    async def addons(self, info: strawberry.Info) -> List[AddonType]:
        restaurant = _restaurant_oid(info)
        addons = await Addon.find({"restaurant": restaurant}).to_list()
        return [await build_addon(a) for a in addons]

    @strawberry.field
    async def allAddons(self, info: strawberry.Info, page: Optional[int] = None) -> List[AddonType]:
        restaurant = _restaurant_oid(info)
        addons = await Addon.find({"restaurant": restaurant}).to_list()
        return [await build_addon(a) for a in addons]

    @strawberry.field
    async def options(self, info: strawberry.Info) -> List[OptionType]:
        restaurant = _restaurant_oid(info)
        options = await Option.find({"restaurant": restaurant}).to_list()
        return [build_option(o) for o in options]

    @strawberry.field
    async def allOptions(self, info: strawberry.Info, page: Optional[int] = None) -> List[OptionType]:
        restaurant = _restaurant_oid(info)
        options = await Option.find({"restaurant": restaurant}).to_list()
        return [build_option(o) for o in options]

    @strawberry.field
    async def coupons(self, info: strawberry.Info) -> List[CouponType]:
        restaurant = _restaurant_oid(info)
        coupons = await Coupon.find({"restaurant": restaurant}).to_list()
        return [
            CouponType(id=str(c.id), code=c.code, discount=c.discount, enabled=c.enabled)
            for c in coupons
        ]

    @strawberry.field
    async def configuration(self, info: strawberry.Info) -> ConfigurationType:
        restaurant = _restaurant_oid(info)
        config = await get_or_create_config(restaurant)
        return build_configuration(config)

    # --- Auth / profile --------------------------------------------------- #

    @strawberry.field
    async def profile(self, info: strawberry.Info) -> UserType:
        user_id = require_user(info)
        user = await User.get(user_id)
        if not user:
            raise Exception("User not found")
        ensure_tenant_access(info, user)
        return build_user(user)

    # --- Orders ----------------------------------------------------------- #

    @strawberry.field
    async def order(self, info: strawberry.Info, id: str) -> OrderType:
        user_id = require_user(info)
        order = await Order.get(id)
        if not order:
            raise Exception("Order not found")
        ensure_tenant_access(info, order)
        if str(order.user) != str(user_id):
            raise Exception("Order not found")
        return await build_order(order)

    @strawberry.field
    async def orders(self, info: strawberry.Info, offset: Optional[int] = 0) -> List[OrderType]:
        user_id = require_user(info)
        restaurant = _restaurant_oid(info)
        orders = (
            await Order.find(
                {"user": PydanticObjectId(user_id), "restaurant": restaurant}
            )
            .sort("-createdAt")
            .skip(offset or 0)
            .limit(10)
            .to_list()
        )
        return [await build_order(o) for o in orders]

    @strawberry.field
    async def allOrders(
        self, info: strawberry.Info, page: Optional[int] = None, rows: Optional[int] = None, search: Optional[str] = None
    ) -> List[OrderType]:
        restaurant = _admin_restaurant_oid(info)
        orders = (
            await Order.find({"restaurant": restaurant}).sort("-createdAt").to_list()
        )
        if search:
            term = search.lower()
            filtered = []
            for o in orders:
                if term in (o.order_id or "").lower():
                    filtered.append(o)
                    continue
                user = await User.get(o.user) if o.user else None
                if user and term in (user.name or "").lower():
                    filtered.append(o)
            orders = filtered
        limit = rows or len(orders)
        return [await build_order(o) for o in orders[:limit]]

    @strawberry.field
    async def orderCount(self, info: strawberry.Info) -> int:
        restaurant = _admin_restaurant_oid(info)
        return await Order.find({"restaurant": restaurant}).count()

    @strawberry.field
    async def users(self, info: strawberry.Info, page: Optional[int] = None) -> List[UserType]:
        restaurant = _admin_restaurant_oid(info)
        users = await User.find({"restaurant": restaurant}).to_list()
        return [build_user(u) for u in users]

    @strawberry.field
    async def allReviews(self, info: strawberry.Info, offset: Optional[int] = 0) -> List[ReviewType]:
        restaurant = _admin_restaurant_oid(info)
        orders = (
            await Order.find({"restaurant": restaurant, "review": {"$ne": None}})
            .sort("-updatedAt")
            .to_list()
        )
        reviews: list[ReviewType] = []
        for order in orders:
            order_obj = await build_order(order, include_review=False)
            review = order.review
            reviews.append(
                ReviewType(
                    id=str(review.id),
                    rating=review.rating,
                    description=review.description,
                    is_active=review.is_active,
                    createdAt=iso(review.createdAt),
                    updatedAt=iso(review.updatedAt),
                    order=order_obj,
                )
            )
        return reviews[(offset or 0):]

    # --- Status enums ----------------------------------------------------- #

    @strawberry.field
    def getOrderStatuses(self, info: strawberry.Info) -> List[str]:
        require_admin(info)
        return list(ORDER_STATUSES)

    @strawberry.field
    def getPaymentStatuses(self, info: strawberry.Info) -> List[str]:
        require_admin(info)
        return list(PAYMENT_STATUSES)

    # --- Tenants (superadmin) --------------------------------------------- #

    @strawberry.field
    async def restaurants(self, info: strawberry.Info) -> List[RestaurantType]:
        require_superadmin(info)
        restaurants = await Restaurant.find_all().sort("name").to_list()
        return [build_restaurant(r) for r in restaurants]

    # --- Dashboard -------------------------------------------------------- #

    @strawberry.field
    async def getDashboardTotal(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardTotal:
        restaurant = _admin_restaurant_oid(info)
        orders = await _orders_in_range(restaurant, starting_date, ending_date)
        total_orders = len(orders)
        total_sales = round(sum(o.order_amount for o in orders if o.payment_status == "PAID"), 2)
        ratings = [o.review.rating for o in orders if o.review]
        total_ratings = len(ratings)
        avg_ratings = round(sum(ratings) / total_ratings, 2) if total_ratings else 0.0
        total_users = await User.find({"restaurant": restaurant}).count()
        return DashboardTotal(
            total_orders=total_orders,
            total_users=total_users,
            total_sales=total_sales,
            total_ratings=total_ratings,
            avg_ratings=avg_ratings,
        )

    @strawberry.field
    async def getDashboardSales(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardSales:
        restaurant = _admin_restaurant_oid(info)
        orders = await _orders_in_range(restaurant, starting_date, ending_date)
        daily = await _daily(orders, with_amount=True)
        return DashboardSales(
            orders=[DailySale(day=d.day, amount=d.amount) for d in daily]
        )

    @strawberry.field
    async def getDashboardOrders(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardOrders:
        restaurant = _admin_restaurant_oid(info)
        orders = await _orders_in_range(restaurant, starting_date, ending_date)
        return DashboardOrders(orders=await _daily(orders, with_amount=False))

    @strawberry.field
    async def getDashboardData(
        self, info: strawberry.Info, starting_date: Optional[str] = None, ending_date: Optional[str] = None
    ) -> DashboardData:
        restaurant = _admin_restaurant_oid(info)
        orders = await _orders_in_range(restaurant, starting_date, ending_date)
        total_sales = round(sum(o.order_amount for o in orders if o.payment_status == "PAID"), 2)
        return DashboardData(
            total_orders=len(orders),
            total_users=await User.find({"restaurant": restaurant}).count(),
            total_sales=total_sales,
            orders=await _daily(orders, with_amount=True),
        )

    @strawberry.field
    async def adminStaffs(self, info: strawberry.Info) -> List[AdminStaffType]:
        restaurant = _director_restaurant_oid(info)
        rows = await AdminAccount.find({"restaurant": restaurant}).to_list()
        return [
            AdminStaffType(
                id=strawberry.ID(str(a.id)),
                email=a.email,
                name=a.name,
                role=a.role,
                is_active=a.is_active,
            )
            for a in rows
        ]
