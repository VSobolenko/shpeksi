"""Seed one COMPLETED order for the seeded customer so the Rate & Review flow is testable.

The CustomerApp only shows the "Write a review" button on an order that is
COMPLETED and has not yet been reviewed. A freshly placed pickup order is
PENDING, so this script places a COD order and advances it to COMPLETED via the
admin `updateOrderStatus` mutation.

Prereqs: a running backend (http://localhost:8000/graphql) seeded with a catalog
(see `seed_demo.py`). The customer account (customer@example.com) must exist.

Usage:
    python scripts/seed_completed_order.py
    python scripts/seed_completed_order.py --url http://localhost:8000/graphql
"""

import argparse
import sys

import httpx

GRAPHQL_URL = "http://localhost:8000/graphql"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "change-me"
CUSTOMER_EMAIL = "customer@example.com"
CUSTOMER_PASSWORD = "password123"


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


def run() -> None:
    with httpx.Client(timeout=30.0) as client:
        # 1. Customer login
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
        print("[seed] customer login ok", flush=True)

        # 2. Pick any food with a variation
        data = gql(client, "query { foods { _id variations { _id } } }")
        foods = data.get("foods", [])
        if not foods:
            raise SeedError("no foods found - run seed_demo.py first")
        food = foods[0]
        food_id = food["_id"]
        variation_id = food["variations"][0]["_id"]

        # 3. Place a COD order
        data = gql(
            client,
            """
            mutation($orderInput: [OrderInput!]!, $paymentMethod: String!) {
              placeOrder(orderInput: $orderInput, paymentMethod: $paymentMethod) {
                _id order_id order_status
              }
            }
            """,
            {
                "orderInput": [
                    {"food": food_id, "quantity": 1, "variation": variation_id}
                ],
                "paymentMethod": "COD",
            },
            token=customer_token,
        )
        order = data["placeOrder"]
        order_db_id = order["_id"]
        order_no = order["order_id"]
        print(f"[seed] placed order {order_no} ({order['order_status']})", flush=True)

        # 4. Admin login
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
        print("[seed] admin login ok", flush=True)

        # 5. Advance to COMPLETED
        for status in ("ACCEPTED", "READY", "COMPLETED"):
            data = gql(
                client,
                """
                mutation($id: String!, $status: String!) {
                  updateOrderStatus(id: $id, status: $status) { _id order_status }
                }
                """,
                {"id": order_db_id, "status": status},
                token=admin_token,
            )
            print(f"[seed] {status} -> {data['updateOrderStatus']['order_status']}", flush=True)

    print(f"\nSEED COMPLETE: order {order_no} is COMPLETED for {CUSTOMER_EMAIL}", flush=True)


def main() -> int:
    global GRAPHQL_URL
    parser = argparse.ArgumentParser(description="Seed a COMPLETED order")
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
