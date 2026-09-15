"""Seed a realistic demo catalog for the CustomerApp E2E verification.

Creates a deterministic pickup menu (categories, foods with priced variations
and addons/options), a fixed customer account, and a coupon. Idempotent: it
deletes existing catalog/coupon data first so re-running yields a clean slate.

Prereqs: a running backend (http://localhost:8000/graphql) and the admin
bootstrap credentials (admin@example.com / change-me).

Usage:
    python scripts/seed_demo.py
    python scripts/seed_demo.py --url http://localhost:8000/graphql
"""

import argparse
import os
import sys
from pathlib import Path

import httpx

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience
    load_dotenv = None

if load_dotenv:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GRAPHQL_URL = "http://localhost:8000/graphql"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")

CUSTOMER = {
    "name": "Test Customer",
    "email": "customer@example.com",
    "password": "password123",
    "phone": "+15551234567",
}

COUPON = {"code": "SAVE10", "discount": 10.0}

OPTIONS = [
    {"title": "Cheese", "price": 0.5},
    {"title": "Bacon", "price": 1.5},
    {"title": "Extra Sauce", "price": 0.3},
    {"title": "Pepperoni", "price": 1.0},
]

ADDONS = [
    {
        "title": "Extras",
        "quantity_minimum": 0,
        "quantity_maximum": 3,
        "options": ["Cheese", "Bacon", "Extra Sauce"],
    },
    {
        "title": "Extra Toppings",
        "quantity_minimum": 0,
        "quantity_maximum": 2,
        "options": ["Pepperoni", "Cheese"],
    },
]

CATEGORIES = ["Burgers", "Pizza", "Drinks", "Desserts"]

FOODS = [
    {
        "title": "Classic Burger",
        "description": "Beef patty, lettuce, tomato and our signature sauce.",
        "category": "Burgers",
        "variations": [
            {"title": "Regular", "price": 8.99, "addons": ["Extras"]},
            {"title": "Double", "price": 11.99, "addons": ["Extras"]},
        ],
    },
    {
        "title": "Cheese Burger",
        "description": "Classic burger topped with melted cheddar.",
        "category": "Burgers",
        "variations": [{"title": "Regular", "price": 9.49, "addons": ["Extras"]}],
    },
    {
        "title": "Margherita Pizza",
        "description": "Tomato, mozzarella and fresh basil.",
        "category": "Pizza",
        "variations": [
            {"title": "Medium", "price": 12.99, "addons": ["Extra Toppings"]},
            {"title": "Large", "price": 16.99, "addons": ["Extra Toppings"]},
        ],
    },
    {
        "title": "Pepperoni Pizza",
        "description": "Double pepperoni with extra cheese.",
        "category": "Pizza",
        "variations": [
            {"title": "Medium", "price": 14.99, "addons": ["Extra Toppings"]},
            {"title": "Large", "price": 18.99, "addons": ["Extra Toppings"]},
        ],
    },
    {
        "title": "Cola",
        "description": "Chilled fizzy cola.",
        "category": "Drinks",
        "variations": [
            {"title": "330ml", "price": 2.5},
            {"title": "500ml", "price": 3.5},
        ],
    },
    {
        "title": "Fresh Lemonade",
        "description": "Freshly squeezed lemonade.",
        "category": "Drinks",
        "variations": [{"title": "Regular", "price": 3.99}],
    },
    {
        "title": "Chocolate Cake",
        "description": "Rich chocolate cake slice.",
        "category": "Desserts",
        "variations": [{"title": "Slice", "price": 4.99}],
    },
    {
        "title": "Vanilla Ice Cream",
        "description": "Creamy vanilla ice cream.",
        "category": "Desserts",
        "variations": [{"title": "Cup", "price": 3.49}],
    },
]


class SeedError(Exception):
    pass


def gql(client: httpx.Client, query: str, variables=None, token=None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = client.post(
        GRAPHQL_URL, json={"query": query, "variables": variables}, headers=headers
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise SeedError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def log(msg: str) -> None:
    print(f"[seed] {msg}", flush=True)


def run() -> None:
    with httpx.Client(timeout=30.0) as client:
        data = gql(
            client,
            """
            mutation($email: String!, $password: String!) {
              adminLogin(email: $email, password: $password) { token }
            }
            """,
            {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        token = data["adminLogin"]["token"]
        log("adminLogin ok")

        # --- Clean slate ------------------------------------------------- #
        # Delete mutations return either an object (with `_id`) or a Boolean,
        # so the selection set must match each mutation's return type.
        for typename, q, del_mut, returns_object in [
            ("categories", "query { categories { _id } }", "deleteCategory", True),
            ("foods", "query { foods { _id } }", "deleteFood", True),
            ("options", "query { options { _id } }", "deleteOption", False),
            ("addons", "query { addons { _id } }", "deleteAddon", False),
            ("coupons", "query { coupons { _id } }", "deleteCoupon", False),
        ]:
            items = gql(client, q, token=token).get(typename, [])
            selection = "{ _id }" if returns_object else ""
            for item in items:
                gql(
                    client,
                    f"mutation($id: String!) {{ {del_mut}(id: $id) {selection} }}",
                    {"id": item["_id"]},
                    token=token,
                )
            log(f"deleted {len(items)} {typename}")

        # --- Options ----------------------------------------------------- #
        option_ids = {}
        data = gql(
            client,
            """
            mutation($optionInput: [OptionInput!]) {
              createOptions(optionInput: $optionInput) { _id title price }
            }
            """,
            {"optionInput": OPTIONS},
            token=token,
        )
        for opt in data["createOptions"]:
            option_ids[opt["title"]] = opt["_id"]
        log(f"created {len(option_ids)} options")

        # --- Addons ------------------------------------------------------ #
        addon_ids = {}
        addon_input = []
        for addon in ADDONS:
            addon_input.append(
                {
                    "title": addon["title"],
                    "quantity_minimum": addon["quantity_minimum"],
                    "quantity_maximum": addon["quantity_maximum"],
                    "options": [option_ids[o] for o in addon["options"]],
                    "is_active": True,
                }
            )
        data = gql(
            client,
            """
            mutation($addonInput: [AddonInput!]) {
              createAddons(addonInput: $addonInput) { _id title }
            }
            """,
            {"addonInput": addon_input},
            token=token,
        )
        for addon in data["createAddons"]:
            addon_ids[addon["title"]] = addon["_id"]
        log(f"created {len(addon_ids)} addons")

        # --- Categories --------------------------------------------------- #
        category_ids = {}
        for title in CATEGORIES:
            data = gql(
                client,
                """
                mutation($category: CategoryInput!) {
                  createCategory(category: $category) { _id title }
                }
                """,
                {"category": {"title": title, "description": ""}},
                token=token,
            )
            category_ids[title] = data["createCategory"]["_id"]
        log(f"created {len(category_ids)} categories")

        # --- Foods -------------------------------------------------------- #
        food_count = 0
        for food in FOODS:
            variations = []
            for var in food["variations"]:
                variations.append(
                    {
                        "title": var["title"],
                        "price": var["price"],
                        "discounted": 0,
                        "addons": [addon_ids[a] for a in var.get("addons", [])],
                    }
                )
            data = gql(
                client,
                """
                mutation($foodInput: FoodInput!) {
                  createFood(foodInput: $foodInput) { _id title }
                }
                """,
                {
                    "foodInput": {
                        "title": food["title"],
                        "description": food["description"],
                        "category": category_ids[food["category"]],
                        "variations": variations,
                        "stock": 100,
                    }
                },
                token=token,
            )
            food_count += 1
        log(f"created {food_count} foods")

        # --- Coupon ------------------------------------------------------- #
        gql(
            client,
            """
            mutation($couponInput: CouponInput!) {
              createCoupon(couponInput: $couponInput) { _id code discount enabled }
            }
            """,
            {"couponInput": COUPON},
            token=token,
        )
        log(f"created coupon {COUPON['code']}")

        # --- Customer account -------------------------------------------- #
        try:
            data = gql(
                client,
                """
                mutation($userInput: UserInput!) {
                  createUser(userInput: $userInput) { userId }
                }
                """,
                {"userInput": CUSTOMER},
            )
            log(f"created customer {CUSTOMER['email']}")
        except SeedError as exc:
            log(f"customer already exists or error: {exc}")

        # --- Currency ----------------------------------------------------- #
        gql(
            client,
            """
            mutation($configurationInput: CurrencyConfigurationInput!) {
              saveCurrencyConfiguration(configurationInput: $configurationInput) {
                currency currency_symbol
              }
            }
            """,
            {"configurationInput": {"currency": "USD", "currency_symbol": "$"}},
            token=token,
        )
        log("currency set to USD ($)")

    print("\nSEED COMPLETE", flush=True)


def main() -> int:
    global GRAPHQL_URL
    parser = argparse.ArgumentParser(description="Seed demo catalog")
    parser.add_argument("--url", default=GRAPHQL_URL)
    args = parser.parse_args()
    GRAPHQL_URL = args.url
    try:
        run()
    except SeedError as exc:
        print(f"\nSEED FAILED: {exc}", file=sys.stderr, flush=True)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\nSEED ERROR: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
