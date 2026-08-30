"""Smoke tests for the GraphQL schema contract (pickup-only)."""

from app.graphql.schema import schema


def test_schema_exposes_pickup_operations():
    sdl = schema.as_str()
    for fragment in [
        "subscribePlaceOrder",
        "orderStatusChanged",
        "placeOrder",
        "adminLogin",
        "configuration",
        "getOrderStatuses",
        "getPaymentStatuses",
        "order_id_prefix",
    ]:
        assert fragment in sdl


def test_schema_has_no_rider_or_delivery_charges():
    sdl = schema.as_str()
    assert "Rider" not in sdl
    assert "delivery_charges" not in sdl
