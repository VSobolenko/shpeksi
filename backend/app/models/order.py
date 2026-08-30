"""Order, OrderItem, Review, and StatusQueue document models (pickup-only)."""

from datetime import datetime
from typing import List, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class StatusQueue(BaseModel):
    """Timestamps for each stage of the pickup order lifecycle."""

    pending: Optional[str] = None
    preparing: Optional[str] = None
    ready: Optional[str] = None
    completed: Optional[str] = None
    cancelled: Optional[str] = None


class OrderOption(BaseModel):
    """Snapshot of an Option embedded in an order item (immutable price history)."""

    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    title: str = ""
    description: Optional[str] = ""
    price: float = 0.0


class OrderAddon(BaseModel):
    """Snapshot of an Addon embedded in an order item."""

    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    title: str = ""
    description: Optional[str] = ""
    quantity_minimum: int = 0
    quantity_maximum: int = 1
    options: List[OrderOption] = Field(default_factory=list)


class OrderVariation(BaseModel):
    """Snapshot of a Variation embedded in an order item."""

    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    title: str = ""
    price: float = 0.0
    discounted: float = 0.0


class OrderItem(BaseModel):
    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    food: Optional[PydanticObjectId] = None
    variation: Optional[OrderVariation] = None
    addons: List[OrderAddon] = Field(default_factory=list)
    quantity: int = 1


class Review(BaseModel):
    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    rating: int = 0
    description: Optional[str] = ""
    is_active: bool = True
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class Order(Document):
    order_id: str = ""
    user: Optional[PydanticObjectId] = None
    items: List[OrderItem] = Field(default_factory=list)
    order_amount: float = 0.0
    paid_amount: float = 0.0
    payment_method: str = "COD"
    payment_status: str = "PENDING"
    order_status: str = "PENDING"
    status_queue: StatusQueue = Field(default_factory=StatusQueue)
    reason: Optional[str] = None
    review: Optional[Review] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Settings:
        name = "orders"
