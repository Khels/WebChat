import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import asyncio_redis

from .exceptions import UnsubscribedError


class Event:
    def __init__(self: "Event", channel: str, message: str) -> None:
        self.channel = channel
        self.message = message

    def __eq__(self: "Event", other: object) -> bool:
        return (
            isinstance(other, Event)
            and self.channel == other.channel
            and self.message == other.message
        )

    def __repr__(self: "Event") -> str:
        return f"Event(channel={self.channel!r}, message={self.message!r})"


class Subscriber:
    def __init__(self: "Subscriber", queue: asyncio.Queue) -> None:
        self._queue = queue

    async def __aiter__(self: "Subscriber") -> AsyncGenerator | None:
        try:
            while True:
                yield await self.get()
        except UnsubscribedError:
            pass

    async def get(self: "Subscriber") -> Event:
        event = await self._queue.get()
        if event is None:
            raise UnsubscribedError
        return event


class RedisBackend:
    def __init__(self: "RedisBackend", url: str) -> None:
        parsed_url = urlparse(url)
        self._host = parsed_url.hostname or "localhost"
        self._port = parsed_url.port or 6379
        self._password = parsed_url.password or None

    async def connect(self: "RedisBackend") -> None:
        kwargs = {
            "host": self._host,
            "port": self._port,
            "password": self._password,
        }
        self._pub_conn = await asyncio_redis.Connection.create(**kwargs)
        self._sub_conn = await asyncio_redis.Connection.create(**kwargs)
        self._subscriber = await self._sub_conn.start_subscribe()

    async def disconnect(self: "RedisBackend") -> None:
        self._pub_conn.close()
        self._sub_conn.close()

    async def subscribe(self: "RedisBackend", channel: str) -> None:
        await self._subscriber.subscribe([channel])

    async def unsubscribe(self: "RedisBackend", channel: str) -> None:
        await self._subscriber.unsubscribe([channel])

    async def publish(self: "RedisBackend", channel: str, message: str) -> None:
        await self._pub_conn.publish(channel, message)

    async def next_published(self: "RedisBackend") -> Event:
        message = await self._subscriber.next_published()
        return Event(channel=message.channel, message=message.value)


class Broadcast:
    def __init__(self: "Broadcast", url: str) -> None:
        self._backend = RedisBackend(url)
        # a dict contaning channel names as keys and a set of queued messages
        self._subscribers: dict[str, set[asyncio.Queue]] = {}

    async def connect(self: "Broadcast") -> None:
        await self._backend.connect()
        self._listener_task = asyncio.create_task(self._listen())

    async def disconnect(self: "Broadcast") -> None:
        if self._listener_task.done():
            self._listener_task.result()
        else:
            self._listener_task.cancel()
        await self._backend.disconnect()

    async def _listen(self: "Broadcast") -> None:
        while True:
            event = await self._backend.next_published()
            for queue in self._subscribers.get(event.channel, set()):
                await queue.put(event)

    async def publish(self: "Broadcast", channel: str, message: str) -> None:
        await self._backend.publish(channel, message)

    @asynccontextmanager
    async def subscribe(
        self: "Broadcast",
        channel: str,
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
