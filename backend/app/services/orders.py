"""Order business logic: id generation, pricing, and order placement."""

import secrets
from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.models import (
    Addon,
    Configuration,
    Coupon,
    Food,
    Option,
    Order,
    OrderAddon,
    OrderItem,
    OrderOption,
    OrderVariation,
    Review,
    StatusQueue,
)

ORDER_STATUSES = ("PENDING", "ACCEPTED", "READY", "COMPLETED", "CANCELLED")
PAYMENT_STATUSES = ("PENDING", "PAID")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt) -> str | None:
    return dt.isoformat() if dt else None


async def generate_order_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(4).upper()}"


async def build_order_items(order_input: list[dict]) -> list[OrderItem]:
    """Resolve the submitted items into immutable snapshots stored on the order."""
    items: list[OrderItem] = []
    for entry in order_input:
        food = None
        if entry.get("food"):
            food = await Food.get(PydanticObjectId(entry["food"]))

        variation_snapshot = None
        if entry.get("variation") and food:
            for v in food.variations:
                if str(v.id) == str(entry["variation"]):
                    variation_snapshot = OrderVariation(
                        id=v.id, title=v.title, price=v.price, discounted=v.discounted
                    )
                    break

        addon_snapshots: list[OrderAddon] = []
        for raw_addon in entry.get("addons") or []:
            addon = await Addon.get(PydanticObjectId(raw_addon["_id"]))
            if not addon:
                continue
            options: list[OrderOption] = []
            for option_id in raw_addon.get("options") or []:
                option = await Option.get(PydanticObjectId(option_id))
                if option:
                    options.append(
                        OrderOption(
                            id=option.id,
                            title=option.title,
                            description=option.description or "",
                            price=option.price,
                        )
                    )
            addon_snapshots.append(
                OrderAddon(
                    id=addon.id,
                    title=addon.title,
                    description=addon.description or "",
                    quantity_minimum=addon.quantity_minimum,
                    quantity_maximum=addon.quantity_maximum,
                    options=options,
                )
            )

        items.append(
            OrderItem(
                food=food.id if food else None,
                variation=variation_snapshot,
                addons=addon_snapshots,
                quantity=int(entry.get("quantity") or 1),
            )
        )
    return items


def compute_subtotal(items: list[OrderItem]) -> float:
    total = 0.0
    for item in items:
        variation = item.variation
        base = (variation.discounted or variation.price) if variation else 0.0
        addon_total = sum(option.price for addon in item.addons for option in addon.options)
        total += (base + addon_total) * item.quantity
    return total


async def place_order(
    user_id: str,
    order_input: list[dict],
    payment_method: str,
    coupon_code: str | None = None,
) -> Order:
    config = await Configuration.find_one({})
    prefix = (config.order_id_prefix or "PKP") if config else "PKP"

    items = await build_order_items(order_input)
    subtotal = compute_subtotal(items)

    discount_percent = 0.0
    if coupon_code:
        coupon = await Coupon.find_one(
            Coupon.code == coupon_code, Coupon.enabled == True  # noqa: E712
        )
        if coupon:
            discount_percent = coupon.discount or 0.0

    order_amount = round(subtotal * (1 - discount_percent / 100.0), 2)
    now = utc_now()

    order = Order(
        order_id=await generate_order_id(prefix),
        user=PydanticObjectId(user_id),
        items=items,
        order_amount=order_amount,
        paid_amount=0.0,
        payment_method=payment_method,
        payment_status="PENDING",
        order_status="PENDING",
        status_queue=StatusQueue(pending=iso(now)),
        review=Review(rating=0, createdAt=now, updatedAt=now),
        createdAt=now,
        updatedAt=now,
    )
    await order.insert()
    return order
