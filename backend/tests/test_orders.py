"""Tests for order id generation and pricing helpers."""

import asyncio

from app.models.order import OrderItem, OrderVariation
from app.services.orders import (
    ORDER_STATUSES,
    PAYMENT_STATUSES,
    compute_subtotal,
    generate_order_id,
)


def test_generate_order_id_uses_given_prefix():
    order_id = asyncio.run(generate_order_id("ORD"))
    assert order_id.startswith("ORD-")
    assert len(order_id) > len("ORD-")


def test_pickup_status_sets():
    assert ORDER_STATUSES == ("PENDING", "ACCEPTED", "READY", "COMPLETED", "CANCELLED")
    assert PAYMENT_STATUSES == ("PENDING", "PAID")


def test_compute_subtotal_flat_variation():
    item = OrderItem(
        food=None,
        variation=OrderVariation(title="Regular", price=10.0, discounted=0.0),
        addons=[],
        quantity=2,
    )
    assert compute_subtotal([item]) == 20.0


def test_compute_subtotal_uses_discounted_price_when_set():
    item = OrderItem(
        food=None,
        variation=OrderVariation(title="Regular", price=10.0, discounted=8.0),
        addons=[],
        quantity=1,
    )
    assert compute_subtotal([item]) == 8.0


def test_compute_subtotal_without_variation_is_zero():
    item = OrderItem(food=None, variation=None, addons=[], quantity=3)
    assert compute_subtotal([item]) == 0.0
