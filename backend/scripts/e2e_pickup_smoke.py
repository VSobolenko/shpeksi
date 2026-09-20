"""End-to-end pickup-flow smoke test for the Pikupo backend.

Runs the full self-pickup order lifecycle against a live backend + MongoDB:

  1. adminLogin (bootstrap admin account from env)
  2. createCategory + createFood (with a priced variation)
  3. createUser (customer)
  4. WebSocket subscriptions over the legacy `subscriptions-transport-ws`
     (`graphql-ws`) protocol:
       - subscribePlaceOrder
       - orderStatusChanged(customerId)
  5. placeOrder (COD)
  6. allOrders (admin sees the order in real time)
  7. updateOrderStatus: ACCEPTED -> READY -> COMPLETED
  8. customer orders / order(id) reflect COMPLETED
  9. getOrderStatuses returns the pickup-only status set

Prereqs: a running backend (`uvicorn app.main:app --port 8000`) with MongoDB.

Usage:
    python scripts/e2e_pickup_smoke.py
    python scripts/e2e_pickup_smoke.py --url http://localhost:8000/graphql \
                                       --ws ws://localhost:8000/graphql
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

import httpx
from websockets.asyncio.client import connect

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience
    load_dotenv = None

if load_dotenv:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GRAPHQL_URL = "http://localhost:8000/graphql"
WS_URL = "ws://localhost:8000/graphql"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")
# Legacy subscriptions-transport-ws subprotocol (used by apollo-link-ws).
LEGACY_SUBPROTOCOL = "graphql-ws"

PICKUP_STATUSES = ["PENDING", "ACCEPTED", "READY", "COMPLETED", "CANCELLED"]


class SmokeError(Exception):
    pass


def log(ok: bool, msg: str) -> None:
    marker = "PASS" if ok else "FAIL"
    print(f"[{marker}] {msg}", flush=True)
    if not ok:
        raise SmokeError(msg)


async def gql(client: httpx.AsyncClient, query: str, variables=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = await client.post(
        GRAPHQL_URL, json={"query": query, "variables": variables}, headers=headers
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise SmokeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


async def recv_data(ws, msg_id: str, timeout: float = 10.0) -> dict:
    """Read messages until a `data` message for `msg_id` arrives (ignores ka/ack)."""
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout)
        msg = json.loads(raw)
        if msg.get("type") == "data" and msg.get("id") == msg_id:
            return msg["payload"]["data"]
        if msg.get("type") == "error":
            raise SmokeError(f"WS error: {msg}")


async def ws_send(ws, payload: dict) -> None:
    await ws.send(json.dumps(payload))


async def run(url: str, ws_url: str) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"Target: {url}  (ws: {ws_url})", flush=True)
        cust_email = f"smoke-{int(time.time())}@example.com"

        # 1. Admin login
        data = await gql(
            client,
            """
            mutation {
              adminLogin(email: "%s", password: "%s") { token userId }
            }
            """
            % (ADMIN_EMAIL, ADMIN_PASSWORD),
        )
        admin_token = data["adminLogin"]["token"]
        log(bool(admin_token), "adminLogin returned a token")

        # 2. Catalog: category + food with a priced variation
        data = await gql(
            client,
            """
            mutation {
              createCategory(category: { title: "Smoke Category", description: "" }) {
                _id title
              }
            }
            """,
            token=admin_token,
        )
        cat_id = data["createCategory"]["_id"]
        log(bool(cat_id), f"createCategory -> {cat_id}")

        data = await gql(
            client,
            """
            mutation {
              createFood(foodInput: {
                title: "Smoke Burger"
                description: "E2E"
                category: "%s"
                variations: [{ title: "Regular", price: 9.99, discounted: 0 }]
              }) {
                _id title
                variations { _id title price }
              }
            }
            """
            % cat_id,
            token=admin_token,
        )
        food_id = data["createFood"]["_id"]
        variation_id = data["createFood"]["variations"][0]["_id"]
        log(bool(food_id and variation_id), f"createFood -> {food_id} (variation {variation_id})")

        # 3. Customer account
        data = await gql(
            client,
            """
            mutation {
              createUser(userInput: {
                name: "Smoke Customer"
                email: "%s"
                phone: "555-0100"
                password: "secret123"
              }) { userId token }
            }
            """
            % cust_email,
        )
        customer_id = data["createUser"]["userId"]
        customer_token = data["createUser"]["token"]
        log(bool(customer_token), f"createUser -> {customer_id}")

        # 4. WebSocket subscriptions (legacy protocol)
        print(f"[....] opening WS subscription ({LEGACY_SUBPROTOCOL})", flush=True)
        async with connect(ws_url, subprotocols=[LEGACY_SUBPROTOCOL]) as ws:
            await ws_send(ws, {"type": "connection_init", "payload": {}})
            ack = json.loads(await asyncio.wait_for(ws.recv(), 10))
            log(ack.get("type") == "connection_ack", "WS connection_ack received")

            await ws_send(
                ws,
                {
                    "id": "1",
                    "type": "start",
                    "payload": {
                        "query": "subscription { subscribePlaceOrder { origin order { order_id order_status } } }"
                    },
                },
            )
            await ws_send(
                ws,
                {
                    "id": "2",
                    "type": "start",
                    "payload": {
                        "query": (
                            'subscription { orderStatusChanged(userId: "%s")'
                            " { origin order { order_id order_status } } }" % customer_id
                        )
                    },
                },
            )

            # 5. Place the order (COD)
            data = await gql(
                client,
                """
                mutation {
                  placeOrder(
                    orderInput: [{ food: "%s", quantity: 2, variation: "%s" }]
                    paymentMethod: "COD"
                  ) {
                    _id order_id order_amount order_status payment_status
                    status_queue { pending preparing ready completed cancelled }
                  }
                }
                """
                % (food_id, variation_id),
                token=customer_token,
            )
            order = data["placeOrder"]
            order_db_id = order["_id"]
            order_no = order["order_id"]
            log(order["order_status"] == "PENDING", f"placeOrder -> {order_no} (PENDING)")
            log(
                abs(order["order_amount"] - 19.98) < 1e-6,
                f"order_amount == 19.98 (got {order['order_amount']})",
            )
            log(order["status_queue"]["pending"] is not None, "status_queue.pending set")

            # Realtime: subscribePlaceOrder event must arrive
            evt = await recv_data(ws, "1", timeout=10)
            log(
                evt["subscribePlaceOrder"]["order"]["order_id"] == order_no,
                "WS subscribePlaceOrder event received",
            )

            # 6. Admin sees the order
            data = await gql(
                client,
                "query { allOrders { _id order_id order_status } }",
                token=admin_token,
            )
            ids = [o["_id"] for o in data["allOrders"]]
            log(order_db_id in ids, "admin allOrders includes the new order")

            # 7. Status transitions via admin
            for status in ("ACCEPTED", "READY", "COMPLETED"):
                data = await gql(
                    client,
                    """
                    mutation {
                      updateOrderStatus(id: "%s", status: "%s") {
                        _id order_status
                        status_queue { pending preparing ready completed cancelled }
                      }
                    }
                    """
                    % (order_db_id, status),
                    token=admin_token,
                )
                got = data["updateOrderStatus"]
                log(got["order_status"] == status, f"updateOrderStatus -> {status}")

                # Realtime: orderStatusChanged event must arrive for the customer
                evt = await recv_data(ws, "2", timeout=10)
                evt_order = evt["orderStatusChanged"]["order"]
                log(
                    evt_order["order_id"] == order_no
                    and evt_order["order_status"] == status,
                    f"WS orderStatusChanged event for {status}",
                )

            status = data["updateOrderStatus"]["status_queue"]
            log(status["preparing"] is not None, "status_queue.preparing set")
            log(status["ready"] is not None, "status_queue.ready set")
            log(status["completed"] is not None, "status_queue.completed set")

            await ws_send(ws, {"id": "1", "type": "stop"})
            await ws_send(ws, {"id": "2", "type": "stop"})

        # 8. Customer sees the final state
        data = await gql(
            client,
            "query { orders { _id order_id order_status order_amount } }",
            token=customer_token,
        )
        cust_orders = {o["_id"]: o for o in data["orders"]}
        log(
            cust_orders.get(order_db_id, {}).get("order_status") == "COMPLETED",
            "customer orders reflects COMPLETED",
        )

        data = await gql(
            client,
            'query { order(id: "%s") { order_status } }' % order_db_id,
            token=customer_token,
        )
        log(data["order"]["order_status"] == "COMPLETED", "customer order(id) reflects COMPLETED")

        # 9. Self-pickup-only status set
        data = await gql(client, "query { getOrderStatuses }", token=admin_token)
        log(
            data["getOrderStatuses"] == PICKUP_STATUSES,
            f"getOrderStatuses == {PICKUP_STATUSES}",
        )

    print("\nALL E2E CHECKS PASSED", flush=True)


def main() -> int:
    global ADMIN_EMAIL, ADMIN_PASSWORD, GRAPHQL_URL
    parser = argparse.ArgumentParser(description="Self-pickup flow E2E smoke test")
    parser.add_argument("--url", default=GRAPHQL_URL)
    parser.add_argument("--ws", default=WS_URL)
    parser.add_argument("--admin-email", default=ADMIN_EMAIL)
    parser.add_argument("--admin-password", default=ADMIN_PASSWORD)
    args = parser.parse_args()

    ADMIN_EMAIL = args.admin_email
    ADMIN_PASSWORD = args.admin_password
    GRAPHQL_URL = args.url

    try:
        asyncio.run(run(args.url, args.ws))
    except SmokeError as exc:
        print(f"\nE2E FAILED: {exc}", file=sys.stderr, flush=True)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\nE2E ERROR: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
