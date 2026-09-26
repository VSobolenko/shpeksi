"""Configuration singleton document (business settings).

One document per restaurant: settings are looked up and created per tenant so
each store keeps its own currency, payment keys and email credentials.
"""

from typing import Optional

from beanie import Document, PydanticObjectId


class Configuration(Document):
    order_id_prefix: str = "PKP"
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
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "configurations"
