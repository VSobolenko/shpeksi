"""GraphQL schema assembly.

``auto_camel_case=False`` keeps field/operation names exactly as declared, which
is required because the frontend contract mixes snake_case (``order_amount``,
``_id``) with camelCase (``notificationToken``, ``getDashboardTotal``).
"""

import strawberry
from strawberry.schema.config import StrawberryConfig

from app.graphql.mutation import Mutation
from app.graphql.query import Query
from app.graphql.subscription import Subscription

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    config=StrawberryConfig(auto_camel_case=False),
)
