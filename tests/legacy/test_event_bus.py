import asyncio
from unittest.mock import patch

import fakeredis
import pytest

from DEVBRAIN_V23.infrastructure.event_bus import EventBusRedis


@pytest.mark.asyncio
async def test_event_bus_delivers_messages() -> None:
    fake_client = fakeredis.FakeRedis(decode_responses=True)
    with patch(
        "DEVBRAIN_V23.infrastructure.event_bus.redis.from_url", return_value=fake_client
    ):
        bus = EventBusRedis()
        received: list[dict] = []
        received_event = asyncio.Event()

        async def handler(payload: dict) -> None:
            received.append(payload)
            received_event.set()

        await bus.subscribe("devbrain", handler)
        await bus.publish("devbrain", {"status": "ok"})
        await asyncio.wait_for(received_event.wait(), timeout=2.0)
        assert received and received[0]["status"] == "ok"
        await bus.close()
