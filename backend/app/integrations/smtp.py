"""SMTP integration (Gmail by default)."""

from email.message import EmailMessage

import aiosmtplib


async def send_smtp(
    username: str,
    password: str,
    to: str,
    subject: str,
    body: str,
    host: str = "smtp.gmail.com",
    port: int = 587,
) -> None:
    message = EmailMessage()
    message["From"] = username
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    await aiosmtplib.send(
        message,
        hostname=host,
        port=port,
        username=username,
        password=password,
        start_tls=True,
    )
