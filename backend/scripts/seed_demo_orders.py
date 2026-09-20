"""Seed a realistic mix of pickup orders for the Pikupo demo.

Places several customer orders and advances them through the pickup pipeline so
the Admin Dashboard and the CustomerApp order history show a believable spread
of statuses (PENDING / ACCEPTED / READY / COMPLETED) and payment states.

Orders reference the food/variation ids currently in the catalog, so run
`seed_demo.py` first (it recreates the catalog and therefore invalidates any
orders created before it).

Prereqs: a running backend (http://localhost:8000/graphql), a seeded catalog,
and the customer account (customer@example.com) created by `seed_demo.py`.

Usage:
    python scripts/seed_demo_orders.py
    python scripts/seed_demo_orders.py --url http://localhost:8000/graphql

To wipe the existing orders first (needed for a clean demo run) use the
`--clear` flag; it shells out to `docker compose exec mongo mongosh` because
MongoDB is intentionally not published to the host.
"""

import argparse
import os
import subprocess
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
CUSTOMER_EMAIL = "customer@example.com"
CUSTOMER_PASSWORD = "password123"

MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "pikupo")
MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "change-me")
MONGO_DB = os.environ.get("MONGODB_DB_NAME", "pikupo")

# Each entry: food index into the catalog, variation index, quantity, addons and
# the status/payment state the order should end up in. `None` status means the
# order stays PENDING.
DEMO_ORDERS = [
    {"food": 0, "variation": 0, "quantity": 2, "status": "COMPLETED", "payment": "PAID"},
    {"food": 2, "variation": 1, "quantity": 1, "status": "COMPLETED", "payment": "PENDING"},
    {"food": 3, "variation": 0, "quantity": 1, "status": "READY", "payment": "PAID"},
    {"food": 1, "variation": 0, "quantity": 3, "status": "ACCEPTED", "payment": "PENDING"},
    {"food": 4, "variation": 1, "quantity": 2, "status": None, "payment": "PENDING"},
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


def clear_orders() -> None:
    """Delete every order. MongoDB is not published to the host, so run mongosh
    inside the compose container instead of connecting directly."""
    backend_dir = Path(__file__).resolve().parent.parent
    js = f"db = db.getSiblingDB('{MONGO_DB}'); print(db.orders.deleteMany({{}}).deletedCount)"
    cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "mongo",
        "mongosh",
        "-u",
        MONGO_USER,
        "-p",
        MONGO_PASSWORD,
        "--authenticationDatabase",
        "admin",
        "--quiet",
        "--eval",
        js,
    ]
    result = subprocess.run(cmd, cwd=backend_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise SeedError(
            "could not clear orders via docker compose:\n" + (result.stderr or "").strip()
        )
    deleted = (result.stdout or "").strip().splitlines()
    log(f"cleared orders (deleted {deleted[-1] if deleted else '?'})")


def fetch_foods(client: httpx.Client) -> list:
    data = gql(
        client,
        """
        query {
          foods {
            _id
            title
            variations { _id title price }
          }
        }
        """,
    )
    foods = [f for f in data.get("foods", []) if f.get("variations")]
    if not foods:
        raise SeedError("no foods with variations found - run seed_demo.py first")
    # Deterministic order so repeated runs pick the same foods.
    foods.sort(key=lambda f: f["title"])
    return foods


def run(clear: bool) -> None:
    if clear:
        clear_orders()

    with httpx.Client(timeout=30.0) as client:
        # --- Logins ------------------------------------------------------- #
        data = gql(
            client,
            """
            mutation($email: String!, $password: String!) {
              login(email: $email, password: $password, type: "default") { token }
            }
            """,
            {"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASSWORD},
        )
        customer_token = data["login"]["token"]
        log("customer login ok")

        data = gql(
            client,
            """
            mutation($email: String!, $password: String!) {
              adminLogin(email: $email, password: $password) { token }
            }
            """,
            {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        admin_token = data["adminLogin"]["token"]
        log("admin login ok")

        foods = fetch_foods(client)
        log(f"catalog has {len(foods)} foods with variations")

        placed = 0
        for spec in DEMO_ORDERS:
            food = foods[spec["food"] % len(foods)]
            variations = food["variations"]
            variation = variations[spec["variation"] % len(variations)]

            data = gql(
                client,
                """
                mutation($orderInput: [OrderInput!]!, $paymentMethod: String!) {
                  placeOrder(orderInput: $orderInput, paymentMethod: $paymentMethod) {
                    _id
                    order_id
                    order_status
                    order_amount
                  }
                }
                """,
                {
                    "orderInput": [
                        {
                            "food": food["_id"],
                            "quantity": spec["quantity"],
                            "variation": variation["_id"],
                        }
                    ],
                    "paymentMethod": "COD",
                },
                token=customer_token,
            )
            order = data["placeOrder"]
            order_id = order["_id"]
            log(
                f"placed {order['order_id']} - {spec['quantity']}x {food['title']} "
                f"({variation['title']}) = {order['order_amount']}"
            )

            # Walk the pipeline: ACCEPTED -> READY -> COMPLETED. The backend
            # validates transitions, so the statuses must be applied in order.
            pipeline = ["ACCEPTED", "READY", "COMPLETED"]
            target = spec["status"]
            if target:
                for status in pipeline:
                    gql(
                        client,
                        """
                        mutation($id: String!, $status: String!) {
                          updateOrderStatus(id: $id, status: $status) { _id order_status }
                        }
                        """,
                        {"id": order_id, "status": status},
                        token=admin_token,
                    )
                    if status == target:
                        break

            if spec["payment"] == "PAID":
                gql(
                    client,
                    """
                    mutation($id: String!, $status: String!) {
                      updatePaymentStatus(id: $id, status: $status) { _id payment_status }
                    }
                    """,
                    {"id": order_id, "status": "PAID"},
                    token=admin_token,
                )

            placed += 1
            log(f"  -> {target or 'PENDING'} / {spec['payment']}")

    print(f"\nSEED COMPLETE: {placed} orders created", flush=True)


def main() -> int:
    global GRAPHQL_URL
    parser = argparse.ArgumentParser(description="Seed demo orders")
    parser.add_argument("--url", default=GRAPHQL_URL)
    parser.add_argument(
        "--clear",
        action="store_true",
        help="delete every existing order first (uses docker compose exec mongo)",
    )
    args = parser.parse_args()
    GRAPHQL_URL = args.url
    try:
        run(clear=args.clear)
    except SeedError as exc:
        print(f"\nSEED FAILED: {exc}", file=sys.stderr, flush=True)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\nSEED ERROR: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
