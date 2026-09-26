"""User (customer) and Address document models."""

from typing import List, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Address(BaseModel):
    """Address embedded in a User document."""

    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    label: Optional[str] = None
    delivery_address: str = ""
    details: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    selected: bool = False


class User(Document):
    name: str = ""
    email: str = ""
    phone: str = ""
    password: Optional[str] = None
    is_active: bool = True
    notificationToken: Optional[str] = None
    is_order_notification: bool = True
    is_offer_notification: bool = True
    addresses: List[Address] = Field(default_factory=list)
    facebookId: Optional[str] = None
    appleId: Optional[str] = None
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "users"
