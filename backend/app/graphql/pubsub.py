"""Pub/sub for GraphQL subscriptions.

Uses Redis when ``REDIS_URL`` is set so events fan out across multiple backend
processes (production); otherwise falls back to an in-memory implementation for
single-process development.
"""

import asyncio
import json
from typing import Any, AsyncIterator, Callable, Dict, List

from app.config import settings


class Subscriber:
    """Async iterator over the messages of one channel."""

    def __init__(self, iterator: AsyncIterator, close: Callable[[], None] | None = None):
        self._iterator = iterator
        self._close = close

    def __aiter__(self) -> "Subscriber":
        return self

    async def __anext__(self):
        return await self._iterator.__anext__()

    def close(self) -> None:
        if self._close is not None:
            self._close()


class InMemoryPubSub:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    async def publish(self, channel: str, message: Any) -> None:
        for queue in self._subscribers.get(channel, []):
            queue.put_nowait(message)

    async def subscribe(self, channel: str) -> Subscriber:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(channel, []).append(queue)

        async def _iterator() -> AsyncIterator:
            while True:
                yield await queue.get()

        def _close() -> None:
            subscribers = self._subscribers.get(channel)
            if subscribers and queue in subscribers:
                subscribers.remove(queue)

        return Subscriber(_iterator(), _close)


class RedisPubSub:
    def __init__(self, url: str) -> None:
        self._url = url
        self._redis = None

    def _client(self):
        if self._redis is None:
            import redis.asyncio as redis

            self._redis = redis.from_url(self._url, decode_responses=True)
        return self._redis

    async def publish(self, channel: str, message: Any) -> None:
        await self._client().publish(channel, json.dumps(message))

    async def subscribe(self, channel: str) -> Subscriber:
        client = self._client()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)

        async def _iterator() -> AsyncIterator:
            async for raw in pubsub.listen():
                if raw.get("type") == "message":
                    yield json.loads(raw["data"])

        def _close() -> None:
            asyncio.ensure_future(pubsub.unsubscribe(channel))
            asyncio.ensure_future(pubsub.close())

        return Subscriber(_iterator(), _close)


pubsub = RedisPubSub(settings.redis_url) if settings.redis_url else InMemoryPubSub()
