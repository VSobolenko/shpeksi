"""Firebase Admin SDK initialisation (lazy)."""

import json

import firebase_admin
from firebase_admin import credentials

from app.config import settings

_app = None


def get_firebase_app():
    """Return the Firebase app, or None when not configured."""
    global _app
    if _app is not None:
        return _app
    raw = (settings.firebase_service_account_json or "").strip()
    if not raw:
        return None
    try:
        cred = credentials.Certificate(json.loads(raw))
    except json.JSONDecodeError:
        cred = credentials.Certificate(raw)
    _app = firebase_admin.initialize_app(cred)
    return _app
