"""Beanie/Pydantic document models for the catalog (menu) entities."""

from typing import List, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Category(Document):
    title: str
    description: Optional[str] = ""
    img_menu: Optional[str] = None
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "categories"


class Variation(BaseModel):
    """Variation embedded in a Food document (size/portion with its own price)."""

    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    title: str
    price: float = 0.0
    discounted: float = 0.0
    addons: List[PydanticObjectId] = Field(default_factory=list)


class Food(Document):
    title: str
    description: Optional[str] = ""
    img_url: Optional[str] = None
    stock: Optional[int] = 0
    tag: Optional[str] = None
    variations: List[Variation] = Field(default_factory=list)
    category: Optional[PydanticObjectId] = None
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "foods"


class Option(Document):
    title: str
    description: Optional[str] = ""
    price: float = 0.0
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "options"


class Addon(Document):
    title: str
    description: Optional[str] = ""
    quantity_minimum: int = 0
    quantity_maximum: int = 1
    options: List[PydanticObjectId] = Field(default_factory=list)
    is_active: bool = True
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "addons"
