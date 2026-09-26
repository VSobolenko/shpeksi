"""GraphQL Subscription resolvers (realtime order events)."""

from typing import AsyncGenerator

import strawberry

from app.graphql.context import resolve_restaurant
from app.graphql.pubsub import pubsub
from app.graphql.types import OrderEvent, OrderStatusEvent, build_order
from app.models import Order


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def subscribePlaceOrder(self, info: strawberry.Info) -> AsyncGenerator[OrderEvent, None]:
        # The pubsub channel is global, so every subscriber receives every new
        # order id. The tenant check here is what keeps restaurant A's orders
        # out of restaurant B's dashboard.
        restaurant = await resolve_restaurant(info)
        subscriber = await pubsub.subscribe("place_order")
        try:
            async for order_id in subscriber:
                order = await Order.get(order_id)
                if order and str(order.restaurant) == str(restaurant):
                    yield OrderEvent(order=await build_order(order), origin="CUSTOMER")
        finally:
            subscriber.close()

    @strawberry.subscription
    async def orderStatusChanged(
        self, info: strawberry.Info, userId: str
    ) -> AsyncGenerator[OrderStatusEvent, None]:
        restaurant = await resolve_restaurant(info)
        subscriber = await pubsub.subscribe(f"order_status:{userId}")
        try:
            async for order_id in subscriber:
                order = await Order.get(order_id)
                if order and str(order.restaurant) == str(restaurant):
                    yield OrderStatusEvent(
                        userId=userId, origin="ADMIN", order=await build_order(order)
                    )
        finally:
            subscriber.close()
