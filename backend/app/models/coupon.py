"""Coupon document model."""

from typing import Optional

from beanie import Document, PydanticObjectId


class Coupon(Document):
    code: str
    discount: float = 0.0
    enabled: bool = True
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "coupons"
