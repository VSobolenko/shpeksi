"""Regression tests for the dashboard resolvers' date-range filtering.

``getDashboardTotal`` / ``getDashboardSales`` / ``getDashboardOrders`` all share
the ``_filter_orders_by_date`` + ``_daily`` helpers. These tests pin the exact
behavior that previously broke: an order placed later on the *ending* date was
silently excluded because the ending date was compared as midnight of that day.
"""

from datetime import datetime

import asyncio
from types import SimpleNamespace

from app.graphql.query import _daily, _filter_orders_by_date, _parse_date


def _order(created_at, amount=10.0, payment_status="PAID", order_id="PKP-X"):
    return SimpleNamespace(
        createdAt=created_at,
        order_amount=amount,
        payment_status=payment_status,
        order_id=order_id,
    )


def test_filter_includes_order_later_on_ending_day():
    orders = [_order(datetime(2026, 8, 30, 23, 59, 59))]
    start = _parse_date("2026-08-23")
    end = _parse_date("2026-08-30")
    assert len(_filter_orders_by_date(orders, start, end)) == 1


def test_filter_includes_order_on_starting_day():
    orders = [_order(datetime(2026, 8, 23, 0, 0, 1))]
    start = _parse_date("2026-08-23")
    end = _parse_date("2026-08-30")
    assert len(_filter_orders_by_date(orders, start, end)) == 1


def test_filter_excludes_order_after_ending_day():
    orders = [_order(datetime(2026, 8, 31, 0, 0, 0))]
    start = _parse_date("2026-08-23")
    end = _parse_date("2026-08-30")
    assert len(_filter_orders_by_date(orders, start, end)) == 0


def test_filter_excludes_order_before_starting_day():
    orders = [_order(datetime(2026, 8, 22, 23, 59, 59))]
    start = _parse_date("2026-08-23")
    end = _parse_date("2026-08-30")
    assert len(_filter_orders_by_date(orders, start, end)) == 0


def test_filter_excludes_order_without_created_at():
    orders = [_order(None)]
    start = _parse_date("2026-08-23")
    end = _parse_date("2026-08-30")
    assert len(_filter_orders_by_date(orders, start, end)) == 0


def test_filter_without_range_keeps_all_orders():
    orders = [_order(datetime(2026, 8, 30)), _order(datetime(2025, 1, 1))]
    assert len(_filter_orders_by_date(orders, None, None)) == 2


def test_filter_start_only_includes_orders_from_start():
    orders = [_order(datetime(2026, 8, 30)), _order(datetime(2026, 8, 1))]
    start = _parse_date("2026-08-23")
    result = _filter_orders_by_date(orders, start, None)
    assert len(result) == 1
    assert result[0].createdAt == datetime(2026, 8, 30)


def test_daily_buckets_by_day_and_only_paid_amounts():
    orders = [
        _order(datetime(2026, 8, 30, 10, 0), amount=10.0, payment_status="PAID"),
        _order(datetime(2026, 8, 30, 11, 0), amount=20.0, payment_status="PENDING"),
        _order(datetime(2026, 8, 29, 12, 0), amount=5.0, payment_status="PAID"),
    ]
    result = asyncio.run(_daily(orders, with_amount=True))
    by_day = {d.day: d for d in result}
    assert by_day["2026-08-30"].count == 2
    assert by_day["2026-08-30"].amount == 10.0  # PENDING order is excluded
    assert by_day["2026-08-29"].count == 1
    assert by_day["2026-08-29"].amount == 5.0


def test_daily_without_amount_returns_counts_only():
    orders = [_order(datetime(2026, 8, 30), amount=10.0, payment_status="PAID")]
    result = asyncio.run(_daily(orders, with_amount=False))
    assert len(result) == 1
    assert result[0].count == 1
    assert not hasattr(result[0], "amount")
