"""Configuration singleton document (business settings)."""

from typing import Optional

from beanie import Document


class Configuration(Document):
    order_id_prefix: str = "ORD"
    email: str = ""
    password: str = ""
    enable_email: bool = False
    client_id: str = ""
    client_secret: str = ""
    sandbox: bool = True
    publishable_key: str = ""
    secret_key: str = ""
    currency: str = "USD"
    currency_symbol: str = "$"
    push_token: Optional[str] = None

    class Settings:
        name = "configurations"
