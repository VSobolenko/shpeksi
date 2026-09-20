"""Tests for model field defaults (Pikupo branding and sensible defaults)."""

from app.models import Addon, Configuration, Coupon, Food, Option


def _default(model, field):
    return model.model_fields[field].default


def test_configuration_defaults_are_pikupo():
    assert _default(Configuration, "order_id_prefix") == "PKP"
    assert _default(Configuration, "enable_email") is False
    assert _default(Configuration, "sandbox") is True
    assert _default(Configuration, "currency") == "USD"


def test_coupon_defaults():
    assert _default(Coupon, "discount") == 0.0
    assert _default(Coupon, "enabled") is True


def test_food_defaults():
    assert _default(Food, "stock") == 0
    assert _default(Food, "category") is None
    assert Food.model_fields["variations"].default_factory is not None


def test_catalog_defaults():
    assert _default(Addon, "is_active") is True
    assert _default(Option, "price") == 0.0
