"""Tests for application configuration and production secret validation."""

import pytest

from app.config import Settings


def test_default_db_name_is_pikupo():
    assert Settings().mongodb_db_name == "pikupo"


def test_development_allows_placeholder_secrets():
    # Development must boot with placeholder secrets (only production is strict).
    Settings().validate_production_secrets()


def test_production_rejects_placeholder_secrets(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "change-me")
    monkeypatch.setenv("ADMIN_PASSWORD", "change-me")
    with pytest.raises(RuntimeError):
        Settings().validate_production_secrets()


def test_production_rejects_unauthenticated_stores(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "a-real-secret-value")
    monkeypatch.setenv("ADMIN_PASSWORD", "a-real-password-value")
    # Default MongoDB URL has no credentials and Redis URL is empty.
    with pytest.raises(RuntimeError):
        Settings().validate_production_secrets()


def test_production_accepts_real_secrets(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "a-real-secret-value")
    monkeypatch.setenv("ADMIN_PASSWORD", "a-real-password-value")
    monkeypatch.setenv(
        "MONGODB_URL", "mongodb://pikupo:secret@mongo:27017"
    )
    monkeypatch.setenv("REDIS_URL", "redis://:secret@redis:6379/0")
    Settings().validate_production_secrets()


def test_url_has_real_password():
    assert Settings._url_has_real_password("mongodb://pikupo:secret@host:27017")
    assert Settings._url_has_real_password("redis://:secret@host:6379/0")
    assert not Settings._url_has_real_password("mongodb://pikupo:change-me@host:27017")
    assert not Settings._url_has_real_password("mongodb://localhost:27017")
    assert not Settings._url_has_real_password("redis://:change-me@host:6379/0")
    assert not Settings._url_has_real_password("")
