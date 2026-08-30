"""Tests for notification no-op behaviour when Firebase is unconfigured."""

from app.services import notifications


def test_send_push_noop_when_firebase_unconfigured(monkeypatch):
    monkeypatch.setattr(notifications, "get_firebase_app", lambda: None)
    assert notifications.send_push("token", "title", "body") is False


def test_send_push_many_noop_when_firebase_unconfigured(monkeypatch):
    monkeypatch.setattr(notifications, "get_firebase_app", lambda: None)
    assert notifications.send_push_many(["t1", "t2"], "title", "body") == 0
