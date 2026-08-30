"""Tests for payment helpers."""

from app.services.payments import to_cents


def test_to_cents_converts_and_rounds():
    assert to_cents(10) == 1000
    assert to_cents(10.5) == 1050
    assert to_cents(0.1) == 10
    assert to_cents(0) == 0
