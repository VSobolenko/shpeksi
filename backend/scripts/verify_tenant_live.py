"""Live tenant-isolation probe against a running Pikupo backend.

Exercises the real HTTP surface (headers, JWTs, superadmin provisioning) rather
than the resolver functions, so it catches wiring mistakes the unit tests
cannot see. Prints PASS/FAIL per assertion and exits non-zero on any failure.

Run inside the app image, e.g.:
    docker compose run --rm -v /opt/pikupo/backend/scripts:/app/scripts app \
        python scripts/verify_tenant_live.py --url http://app:8000/graphql
"""

import argparse
import os
import sys

import httpx

PROBE_SLUG = "isolation-probe"
PROBE_DIRECTOR_EMAIL = "probe-director@example.com"
PROBE_DIRECTOR_PASSWORD = "Probe-Demo!9k3Zq7"
DEMO_SLUG = os.environ.get("DEMO_RESTAURANT_SLUG", "pikupo-demo")
DEMO_DIRECTOR_EMAIL = os.environ.get("DEMO_DIRECTOR_EMAIL", "director@pikupo.com")
DEMO_DIRECTOR_PASSWORD = os.environ.get("DEMO_DIRECTOR_PASSWORD", "Director-Demo!9k3Zq7")
STAFF_EMAIL = "staff@pikupo.com"
STAFF_PASSWORD = "Staff-Demo!9k3Zq7"

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}{(' -> ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)


def error_code(payload: dict) -> str:
    errors = payload.get("errors") or []
    if not errors:
        return ""
    return (errors[0].get("extensions") or {}).get("code", "")


def gql(client, url, query, variables=None, token=None, restaurant=None) -> dict:
    headers = {}
    if token:
        headers["authorization"] = f"Bearer {token}"
    if restaurant:
        headers["x-restaurant-id"] = restaurant
    response = client.post(url, json={"query": query, "variables": variables}, headers=headers)
    return response.json()


def admin_login(client, url, email, password) -> str:
    payload = gql(
        client,
        url,
        "mutation($e:String!,$p:String!){adminLogin(email:$e,password:$p){token role}}",
        {"e": email, "p": password},
    )
    data = payload.get("data") or {}
    if not data.get("adminLogin"):
        raise RuntimeError(f"login failed for {email}: {payload.get('errors')}")
    return data["adminLogin"]["token"]


DEMO_FOODS = "query { foods { _id title } }"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://app:8000/graphql")
    args = parser.parse_args()
    url = args.url

    super_email = os.environ.get("ADMIN_EMAIL")
    super_password = os.environ.get("ADMIN_PASSWORD")
    if not super_email or not super_password:
        print("ADMIN_EMAIL / ADMIN_PASSWORD must be set", file=sys.stderr)
        return 2

    with httpx.Client(timeout=30.0) as client:
        super_token = admin_login(client, url, super_email, super_password)
        check("superadmin can log in", bool(super_token))

        # --- The platform owner is not scoped into any tenant -------------- #
        payload = gql(client, url, DEMO_FOODS, token=super_token)
        check(
            "superadmin has no tenant scope",
            error_code(payload) == "RESTAURANT_REQUIRED",
            error_code(payload),
        )

        # --- Provision a second tenant ------------------------------------ #
        payload = gql(
            client,
            url,
            "mutation($n:String!,$s:String!,$e:String!,$p:String!){"
            " createRestaurant(name:$n,slug:$s,directorEmail:$e,directorPassword:$p)"
            " { _id slug } }",
            {
                "n": "Isolation Probe",
                "s": PROBE_SLUG,
                "e": PROBE_DIRECTOR_EMAIL,
                "p": PROBE_DIRECTOR_PASSWORD,
            },
            token=super_token,
        )
        created = (payload.get("data") or {}).get("createRestaurant")
        if not created:
            # Already provisioned by a previous run: reuse it.
            payload = gql(client, url, "query { restaurants { _id slug } }", token=super_token)
            rows = (payload.get("data") or {}).get("restaurants") or []
            created = next((r for r in rows if r["slug"] == PROBE_SLUG), None)
        check("second restaurant exists", bool(created))
        probe_id = created["_id"]

        # Start from a known state: a previous run deactivates this tenant at the
        # end, so reactivate it before asserting anything about it.
        gql(
            client,
            url,
            "mutation($id:String!,$a:Boolean!){ setRestaurantActive(id:$id,isActive:$a){ _id is_active } }",
            {"id": probe_id, "a": True},
            token=super_token,
        )

        # Idempotent re-provisioning of its director.
        payload = gql(
            client,
            url,
            "mutation($r:String!,$e:String!,$p:String!){"
            " createRestaurantDirector(restaurantId:$r,email:$e,password:$p){ _id role } }",
            {"r": probe_id, "e": PROBE_DIRECTOR_EMAIL, "p": PROBE_DIRECTOR_PASSWORD},
            token=super_token,
        )
        check(
            "superadmin can (re)provision a director",
            bool((payload.get("data") or {}).get("createRestaurantDirector")),
            str(payload.get("errors")),
        )

        # --- Each director only sees their own restaurant ------------------ #
        demo_token = admin_login(client, url, DEMO_DIRECTOR_EMAIL, DEMO_DIRECTOR_PASSWORD)
        probe_token = admin_login(client, url, PROBE_DIRECTOR_EMAIL, PROBE_DIRECTOR_PASSWORD)
        check("demo director can log in", bool(demo_token))
        check("probe director can log in", bool(probe_token))

        demo_foods = gql(client, url, DEMO_FOODS, token=demo_token).get("data", {}).get("foods") or []
        probe_foods = gql(client, url, DEMO_FOODS, token=probe_token).get("data", {}).get("foods") or []
        check("demo director sees the demo catalog", len(demo_foods) > 0, f"{len(demo_foods)} foods")
        check("probe director sees an empty catalog", probe_foods == [], f"{len(probe_foods)} foods")

        demo_orders = (
            gql(client, url, "query { allOrders { _id } }", token=demo_token)
            .get("data", {})
            .get("allOrders")
            or []
        )
        probe_orders = (
            gql(client, url, "query { allOrders { _id } }", token=probe_token)
            .get("data", {})
            .get("allOrders")
            or []
        )
        check("demo director sees the demo orders", len(demo_orders) > 0, f"{len(demo_orders)} orders")
        check("probe director sees no orders", probe_orders == [], f"{len(probe_orders)} orders")

        for field, label in (("users", "users"), ("coupons", "coupons")):
            rows = gql(client, url, f"query {{ {field} {{ _id }} }}", token=probe_token)
            got = (rows.get("data") or {}).get(field)
            check(f"probe director sees no {label}", not got, str(rows.get("errors") or got))

        # A director legitimately sees its own account, so the assertion is not
        # "empty" but "only ours": a leak would surface the other tenant's
        # director or staff email here.
        probe_staff = (
            gql(client, url, "query { adminStaffs { email } }", token=probe_token)
            .get("data", {})
            .get("adminStaffs")
            or []
        )
        probe_staff_emails = {row["email"] for row in probe_staff}
        demo_staff_emails = {
            DEMO_DIRECTOR_EMAIL.lower(),
            STAFF_EMAIL.lower(),
        }
        check(
            "probe director sees only its own staff",
            probe_staff_emails == {PROBE_DIRECTOR_EMAIL.lower()},
            str(sorted(probe_staff_emails)),
        )
        check(
            "probe staff list hides the demo restaurant accounts",
            not (probe_staff_emails & demo_staff_emails),
            str(sorted(probe_staff_emails & demo_staff_emails)),
        )

        demo_staff = (
            gql(client, url, "query { adminStaffs { email } }", token=demo_token)
            .get("data", {})
            .get("adminStaffs")
            or []
        )
        demo_staff_emails_seen = {row["email"] for row in demo_staff}
        check(
            "demo staff list hides the probe director",
            PROBE_DIRECTOR_EMAIL.lower() not in demo_staff_emails_seen,
            str(sorted(demo_staff_emails_seen)),
        )

        # --- Cross-tenant by-id access is refused -------------------------- #
        if demo_orders:
            payload = gql(
                client,
                url,
                "query($id:String!){ order(id:$id){ order_id } }",
                {"id": demo_orders[0]["_id"]},
                token=probe_token,
            )
            check("probe director cannot load a demo order by id", error_code(payload) == "FORBIDDEN", error_code(payload))

        # --- The customer app path: tenant from the header ----------------- #
        payload = gql(client, url, DEMO_FOODS)
        check("anonymous read without a tenant is rejected", error_code(payload) == "RESTAURANT_REQUIRED", error_code(payload))

        payload = gql(client, url, DEMO_FOODS, restaurant=DEMO_SLUG)
        anonymous_foods = (payload.get("data") or {}).get("foods")
        check(
            "anonymous read with x-restaurant-id works (app build)",
            bool(anonymous_foods),
            f"{len(anonymous_foods or [])} foods",
        )

        payload = gql(client, url, DEMO_FOODS, restaurant="no-such-restaurant")
        check("unknown tenant slug is rejected", error_code(payload) == "RESTAURANT_REQUIRED", error_code(payload))

        # --- Staff is orders-only ------------------------------------------ #
        staff_token = admin_login(client, url, STAFF_EMAIL, STAFF_PASSWORD)
        payload = gql(client, url, "query { adminStaffs { _id } }", token=staff_token)
        check("staff cannot read staff accounts", error_code(payload) == "FORBIDDEN", error_code(payload))
        payload = gql(client, url, "query { allOrders { _id } }", token=staff_token)
        staff_orders = (payload.get("data") or {}).get("allOrders") or []
        check("staff can read orders", len(staff_orders) > 0, f"{len(staff_orders)} orders")
        check(
            "staff only sees its own restaurant's orders",
            len(staff_orders) == len(demo_orders),
            f"staff={len(staff_orders)} demo={len(demo_orders)}",
        )

        # --- A deactivated tenant stops resolving --------------------------- #
        payload = gql(
            client,
            url,
            "mutation($id:String!,$a:Boolean!){ setRestaurantActive(id:$id,isActive:$a){ _id is_active } }",
            {"id": probe_id, "a": False},
            token=super_token,
        )
        check("superadmin can deactivate a restaurant", bool((payload.get("data") or {}).get("setRestaurantActive")), str(payload.get("errors")))

        payload = gql(client, url, DEMO_FOODS, restaurant=PROBE_SLUG)
        check(
            "deactivated tenant no longer resolves",
            error_code(payload) == "RESTAURANT_REQUIRED",
            error_code(payload),
        )

    print()
    if FAILURES:
        print(f"{len(FAILURES)} CHECK(S) FAILED: {', '.join(FAILURES)}")
        return 1
    print("ALL LIVE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
