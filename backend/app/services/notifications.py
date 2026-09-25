"""Push notification helpers — Expo Push API + optional Firebase FCM."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from app.integrations.firebase import get_firebase_app

logger = logging.getLogger(__name__)

_messaging = None
EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def _get_messaging():
    global _messaging
    app = get_firebase_app()
    if app is None:
        return None
    if _messaging is None:
        from firebase_admin import messaging

        _messaging = messaging
    return _messaging


def _is_expo_token(token: str) -> bool:
    t = (token or "").strip()
    return t.startswith("ExponentPushToken[") or t.startswith("ExpoPushToken[")


def _send_expo(token: str, title: str, body: str) -> bool:
    payload = {
        "to": token,
        "title": title or "Pikupo",
        "body": body or "",
        "sound": "default",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        EXPO_PUSH_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
            # Expo returns { data: { status: "ok"|"error", ... } }
            data_obj = parsed.get("data") or {}
            if isinstance(data_obj, list):
                data_obj = data_obj[0] if data_obj else {}
            status = data_obj.get("status")
            if status == "error":
                logger.warning("Expo push error: %s", data_obj)
                return False
            return True
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Expo push failed: %s", exc)
        return False


def _send_fcm(token: str, title: str, body: str) -> bool:
    messaging = _get_messaging()
    if messaging is None or not token:
        return False
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        messaging.send(message)
        return True
    except Exception as exc:
        logger.warning("FCM push failed: %s", exc)
        return False


def send_push(token: str, title: str, body: str) -> bool:
    if not token:
        return False
    if _is_expo_token(token):
        return _send_expo(token, title, body)
    return _send_fcm(token, title, body)


def send_push_many(tokens: list[str], title: str, body: str) -> int:
    sent = 0
    for token in tokens:
        if token and send_push(token, title, body):
            sent += 1
    return sent
