"""Unit tests for auth utilities (hashing and JWT)."""

from jose import JWTError

from app.services.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    hashed = hash_password("s3cret")
    assert hashed != "s3cret"
    assert verify_password("s3cret", hashed)
    assert not verify_password("wrong", hashed)


def test_password_verify_rejects_invalid_hash():
    assert not verify_password("s3cret", None)
    assert not verify_password("s3cret", "not-a-hash")


def test_jwt_round_trip():
    token = create_access_token(subject="user-123", role="customer")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "customer"
    assert "exp" in payload


def test_jwt_rejects_tampered_token():
    token = create_access_token(subject="user-123", role="customer")
    try:
        decode_token(token[:-2] + "xx")
        assert False, "expected JWTError"
    except JWTError:
        pass
