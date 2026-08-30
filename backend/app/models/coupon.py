"""Coupon document model."""

from beanie import Document


class Coupon(Document):
    code: str
    discount: float = 0.0
    enabled: bool = True

    class Settings:
        name = "coupons"
