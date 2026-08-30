"""Tests for the in-memory pub/sub fallback used when REDIS_URL is unset."""

import asyncio

from app.graphql.pubsub import InMemoryPubSub


def test_in_memory_pubsub_delivers_messages():
    pubsub = InMemoryPubSub()

    async def run():
        subscriber = await pubsub.subscribe("orders")
        received = []

        async def consume():
            async for msg in subscriber:
                received.append(msg)

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        await pubsub.publish("orders", "order-1")
        await asyncio.sleep(0.01)
        subscriber.close()
        task.cancel()
        return received

    assert asyncio.run(run()) == ["order-1"]
