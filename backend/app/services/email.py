"""Email sending via SMTP, driven by the Configuration singleton."""

from app.models import Configuration


async def send_email(to: str, subject: str, body: str) -> bool:
    config = await Configuration.find_one({})
    if not config or not config.enable_email or not config.email:
        return False
    from app.integrations.smtp import send_smtp

    try:
        await send_smtp(
            username=config.email,
            password=config.password,
            to=to,
            subject=subject,
            body=body,
        )
        return True
    except Exception:
        return False
