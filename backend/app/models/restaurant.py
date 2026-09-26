"""Restaurant (tenant) document model.

One backend serves many restaurant clients. Every tenant-owned document carries
a ``restaurant`` reference back to one of these documents, and each client app
build ships with the restaurant's ``slug`` so requests can be scoped.
"""

from beanie import Document


class Restaurant(Document):
    name: str = ""
    slug: str = ""  # unique, URL-safe; baked into each client app build
    is_active: bool = True

    class Settings:
        name = "restaurants"
