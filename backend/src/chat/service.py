import asyncio
import enum
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator
from urllib.parse import urlparse

import asyncio_redis

from .exceptions import Unsubscribed

# import redis.asyncio as redis


class ChatType(enum.Enum):
    saved_messages = 1
    dialogue = 2
    group = 3


class MessageType(enum.Enum):
    text = 1
    voice = 2
    file = 3


class Event:
    def __init__(self, channel: str, message: Any) -> None:
        self.channel = channel
        self.message = message

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Event)
            and self.channel == other.channel
            and self.message == other.message
        )

    def __repr__(self) -> str:
        return f"Event(channel={self.channel!r}, message={self.message!r})"


class Subscriber:
    def __init__(self, queue: asyncio.Queue) -> None:
        self._queue = queue

    async def __aiter__(self) -> AsyncGenerator | None:
        try:
            while True:
                yield await self.get()
        except Unsubscribed:
            pass

    async def get(self) -> Event:
        event = await self._queue.get()
        if event is None:
            raise Unsubscribed()
        return event


class RedisBackend:
    def __init__(self, url: str):
        parsed_url = urlparse(url)
        self._host = parsed_url.hostname or "localhost"
        self._port = parsed_url.port or 6379
        self._password = parsed_url.password or None

    async def connect(self) -> None:
        kwargs = {
            "host": self._host,
            "port": self._port,
            "password": self._password
        }
        self._pub_conn = await asyncio_redis.Connection.create(**kwargs)
        self._sub_conn = await asyncio_redis.Connection.create(**kwargs)
        self._subscriber = await self._sub_conn.start_subscribe()

    async def disconnect(self) -> None:
        self._pub_conn.close()
        self._sub_conn.close()

    async def subscribe(self, channel: str) -> None:
        await self._subscriber.subscribe([channel])

    async def unsubscribe(self, channel: str) -> None:
        await self._subscriber.unsubscribe([channel])

    async def publish(self, channel: str, message) -> None:
        await self._pub_conn.publish(channel, message)

    async def next_published(self) -> Event:
        message = await self._subscriber.next_published()
        return Event(channel=message.channel, message=message.value)

    # def __init__(self, url: str):
    #     self._url = url

    # async def connect(self) -> None:
    #     self._client: redis.Redis = await redis.from_url(self._url)
    #     self._pubsub = self._client.pubsub()

    # async def disconnect(self) -> None:
    #     await self._pubsub.close()
    #     await self._client.close()

    # async def subscribe(self, channel: str) -> None:
    #     await self._pubsub.subscribe(channel)

    # async def unsubscribe(self, channel: str) -> None:
    #     await self._pubsub.unsubscribe(channel)

    # async def publish(self, channel: str, message: Any) -> None:
    #     await self._client.publish(channel, message)

    # async def next_published(self) -> Event:
    #     async for message in self._pubsub.listen():
    #         yield Event(channel=message["channel"],
    #                     message=message["data"].decode())


class Broadcast:
    def __init__(self, url: str):
        self._backend = RedisBackend(url)
        # a dict contaning channel names as keys and a set of queued messages
        self._subscribers: dict[str, set[asyncio.Queue]] = {}

    async def connect(self) -> None:
        await self._backend.connect()
        self._listener_task = asyncio.create_task(self._listen())

    async def disconnect(self) -> None:
        if self._listener_task.done():
            self._listener_task.result()
        else:
            self._listener_task.cancel()
        await self._backend.disconnect()

    async def _listen(self) -> None:
        while True:
            event = await self._backend.next_published()
            for queue in self._subscribers.get(event.channel, set()):
                await queue.put(event)

    async def publish(self, channel: str, message: Any) -> None:
        await self._backend.publish(channel, message)

    @asynccontextmanager
    async def subscribe(
        self, channel: str
    ) -> AsyncIterator[Subscriber]:
        queue = asyncio.Queue()

        try:
            if not self._subscribers.get(channel):
                await self._backend.subscribe(channel)
                self._subscribers[channel] = {queue}
            else:
                self._subscribers[channel].add(queue)
            yield Subscriber(queue)
        finally:
            self._subscribers[channel].remove(queue)
            # no active connections left
            if not self._subscribers.get(channel):
                del self._subscribers[channel]
                await self._backend.unsubscribe(channel)
            # a signal for Subscriber.get() to stop
            await queue.put(None)
