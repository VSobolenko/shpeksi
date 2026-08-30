"""Tests for structured JSON logging."""

import json
import logging

from app.logging_config import JsonFormatter


def test_json_formatter_emits_valid_json():
    record = logging.LogRecord(
        name="app", level=logging.INFO, pathname=__file__, lineno=1,
        msg="hello", args=(), exc_info=None,
    )
    payload = json.loads(JsonFormatter().format(record))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "app"
    assert payload["message"] == "hello"
    assert "ts" in payload


def test_json_formatter_does_not_add_extra_fields():
    record = logging.LogRecord(
        name="app", level=logging.INFO, pathname=__file__, lineno=1,
        msg="secret-free message", args=(), exc_info=None,
    )
    payload = json.loads(JsonFormatter().format(record))
    assert set(payload) == {"ts", "level", "logger", "message"}
