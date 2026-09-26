"""Backfill tenant references onto pre-multi-tenant documents.

Creates a default restaurant (``Pikupo Demo`` / ``pikupo-demo``) when none
exists and stamps every tenant-owned document that has ``restaurant = None``
with that restaurant's id. Idempotent and batched, so it is safe to run more
than once against a live database (the second run updates nothing).

Usage:
    python scripts/migrate_tenants.py
    python scripts/migrate_tenants.py --slug pikupo-demo --name "Pikupo Demo"
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience
    load_dotenv = None

if load_dotenv:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Running a file directly puts *its own folder* on sys.path, not the project
# root, so `import app` would fail — both locally and inside the deploy
# container, where it is invoked as `python scripts/migrate_tenants.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import close_db, init_db
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

DEFAULT_SLUG = os.environ.get("DEMO_RESTAURANT_SLUG", "pikupo-demo")
DEFAULT_NAME = os.environ.get("DEMO_RESTAURANT_NAME", "Pikupo Demo")

# Every collection that carries a tenant reference.
TENANT_MODELS = [
    Category,
    Food,
    Option,
    Addon,
    Coupon,
    Order,
    User,
    AdminAccount,
    Configuration,
]

BATCH_SIZE = 200


async def ensure_restaurant(slug: str, name: str) -> Restaurant:
    restaurant = await Restaurant.find_one({"slug": slug})
    if restaurant:
        print(f"[migrate] using existing restaurant {slug} ({restaurant.id})", flush=True)
        return restaurant
    restaurant = Restaurant(name=name, slug=slug, is_active=True)
    await restaurant.insert()
    print(f"[migrate] created restaurant {slug} ({restaurant.id})", flush=True)
    return restaurant


async def backfill(model, restaurant: Restaurant) -> int:
    """Stamp every document missing a restaurant, in bounded batches."""
    total = 0
    while True:
        docs = await model.find({"restaurant": None}).limit(BATCH_SIZE).to_list()
        if not docs:
            break
        for doc in docs:
            doc.restaurant = restaurant.id
            await doc.save()
        total += len(docs)
    print(f"[migrate] {model.__name__}: stamped {total}", flush=True)
    return total


async def run(slug: str, name: str) -> None:
    await init_db()
    try:
        restaurant = await ensure_restaurant(slug, name)
        grand_total = 0
        for model in TENANT_MODELS:
            grand_total += await backfill(model, restaurant)
        print(f"[migrate] done - {grand_total} documents updated", flush=True)
    finally:
        await close_db()


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill tenant references")
    parser.add_argument("--slug", default=DEFAULT_SLUG)
    parser.add_argument("--name", default=DEFAULT_NAME)
    args = parser.parse_args()
    try:
        asyncio.run(run(args.slug, args.name))
    except Exception as exc:  # noqa: BLE001
        print(f"[migrate] ERROR: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
