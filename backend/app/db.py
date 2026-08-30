"""MongoDB connection via Motor + Beanie."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from app.config import settings
from app.models import (
    Addon,
    Category,
    Configuration,
    Coupon,
    Food,
    Option,
    Order,
    User,
)

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def init_db() -> None:
    global _client, _database
    _client = AsyncIOMotorClient(settings.mongodb_url)
    _database = _client[settings.mongodb_db_name]
    await init_beanie(
        database=_database,
        document_models=[
            Category,
            Food,
            Addon,
            Option,
            Coupon,
            User,
            Order,
            Configuration,
        ],
    )


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    return _database


async def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
