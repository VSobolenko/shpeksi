"""GraphQL Subscription resolvers (realtime order events)."""

from typing import AsyncGenerator

import strawberry

from app.graphql.pubsub import pubsub
from app.graphql.types import OrderEvent, OrderStatusEvent, build_order
from app.models import Order


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def subscribePlaceOrder(self, info: strawberry.Info) -> AsyncGenerator[OrderEvent, None]:
        subscriber = await pubsub.subscribe("place_order")
        try:
            async for order_id in subscriber:
                order = await Order.get(order_id)
                if order:
                    yield OrderEvent(order=await build_order(order), origin="CUSTOMER")
        finally:
            subscriber.close()

    @strawberry.subscription
    async def orderStatusChanged(
        self, info: strawberry.Info, userId: str
    ) -> AsyncGenerator[OrderStatusEvent, None]:
        subscriber = await pubsub.subscribe(f"order_status:{userId}")
        try:
            async for order_id in subscriber:
                order = await Order.get(order_id)
                if order:
                    yield OrderStatusEvent(
                        userId=userId, origin="ADMIN", order=await build_order(order)
                    )
        finally:
            subscriber.close()
