"""Admin staff accounts (director-managed workers)."""

from typing import Optional

from beanie import Document


class AdminAccount(Document):
    """Director-created dashboard users. Bootstrap director stays in env."""

    email: str = ""
    password: Optional[str] = None
    name: str = ""
    role: str = "staff"  # "staff" only for DB rows; director is env bootstrap
    is_active: bool = True

    class Settings:
        name = "admin_accounts"
