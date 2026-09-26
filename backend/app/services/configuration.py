"""Per-restaurant configuration helpers."""

from beanie import PydanticObjectId

from app.models import Configuration


async def get_or_create_config(restaurant_id) -> Configuration:
    """Return the Configuration document for a restaurant, creating a default.

    Configuration is one-document-per-tenant: the first access for a restaurant
    inserts a defaults document so the admin UI always has something to read.
    """
    restaurant = PydanticObjectId(str(restaurant_id))
    config = await Configuration.find_one({"restaurant": restaurant})
    if config is None:
        config = Configuration(restaurant=restaurant)
        await config.insert()
    return config
