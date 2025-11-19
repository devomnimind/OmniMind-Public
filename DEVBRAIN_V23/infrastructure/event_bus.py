from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional

import redis

EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventBusRedis:
    """Redis Streams event bus usado pelo DevBrain para comunicação entre agentes."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_client: Optional[Any] = None,
    ) -> None:
        self._redis = redis_client or redis.from_url(redis_url, decode_responses=True)
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._listen_tasks: Dict[str, asyncio.Task[None]] = {}
        self._running = True

    async def publish(self, channel: str, event: Dict[str, Any]) -> None:
        """Publica um evento em um canal redis stream."""
        await asyncio.to_thread(self._redis.xadd, channel, event)

    async def subscribe(self, channel: str, handler: EventHandler) -> None:
        """Se inscreve e dispara um listener em background."""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(handler)
        if channel not in self._listen_tasks:
            task = asyncio.create_task(self._listen(channel))
            self._listen_tasks[channel] = task

    async def _listen(self, channel: str) -> None:
        last_id = "0"
        while self._running:
            entries = await asyncio.to_thread(
                self._redis.xread, {channel: last_id}, count=10, block=1000
            )
            if not entries:
                await asyncio.sleep(0.05)
                continue
            for _, messages in entries:
                for msg_id, payload in messages:
                    handlers = self._subscribers.get(channel, [])
                    for handler in handlers:
                        await handler(payload)
                    last_id = msg_id

    async def close(self) -> None:
        """Fecha os listeners e cancela tarefas em background."""
        self._running = False
        tasks = list(self._listen_tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
