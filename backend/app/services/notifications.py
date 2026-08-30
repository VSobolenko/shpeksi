"""Push notification helpers via Firebase Cloud Messaging."""

from app.integrations.firebase import get_firebase_app

_messaging = None


def _get_messaging():
    global _messaging
    app = get_firebase_app()
    if app is None:
        return None
    if _messaging is None:
        from firebase_admin import messaging

        _messaging = messaging
    return _messaging


def send_push(token: str, title: str, body: str) -> bool:
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
    except Exception:
        return False


def send_push_many(tokens: list[str], title: str, body: str) -> int:
    sent = 0
    for token in tokens:
        if token and send_push(token, title, body):
            sent += 1
    return sent
