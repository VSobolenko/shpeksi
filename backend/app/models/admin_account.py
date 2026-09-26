"""Admin staff accounts (director-managed workers)."""

from typing import Optional

from beanie import Document, PydanticObjectId


class AdminAccount(Document):
    """Dashboard users created for a restaurant (staff and directors)."""

    email: str = ""
    password: Optional[str] = None
    name: str = ""
    role: str = "staff"  # "staff" or "director" for DB rows
    is_active: bool = True
    restaurant: Optional[PydanticObjectId] = None

    class Settings:
        name = "admin_accounts"
