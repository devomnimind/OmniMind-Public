"""
Testes para OrchestratorEventBus - Sprint 1 Observabilidade.

Valida propagação de trace_id em eventos.
"""

import asyncio
import json
import time
from pathlib import Path

import pytest

from src.orchestrator.event_bus import EventPriority, OrchestratorEvent, OrchestratorEventBus


class TestEventBusTracing:
    """Testes para trace_id em OrchestratorEventBus."""

    @pytest.mark.asyncio
    async def test_event_auto_trace_id_generation(self):
        """Test that trace_id is auto-generated if not provided."""
        bus = OrchestratorEventBus()

        event = OrchestratorEvent(
            event_type="test_event",
            source="test_source",
            priority=EventPriority.MEDIUM,
            data={"key": "value"},
            timestamp=time.time(),
        )

        # trace_id should be None before publishing
        assert event.trace_id is None

        await bus.publish(event)

        # trace_id should be set after publishing
        assert event.trace_id is not None
        assert event.span_id is not None
        assert isinstance(event.trace_id, str)
        assert len(event.trace_id) > 0

    @pytest.mark.asyncio
    async def test_event_preserves_provided_trace_id(self):
        """Test that provided trace_id is preserved."""
        bus = OrchestratorEventBus()

        custom_trace_id = "custom-trace-id-12345"
        custom_span_id = "custom-span-id-67890"

        event = OrchestratorEvent(
            event_type="test_event",
            source="test_source",
            priority=EventPriority.MEDIUM,
            data={"key": "value"},
            timestamp=time.time(),
            trace_id=custom_trace_id,
            span_id=custom_span_id,
        )

        await bus.publish(event)

        # Should preserve custom trace_id
        assert event.trace_id == custom_trace_id
        assert event.span_id == custom_span_id

    @pytest.mark.asyncio
    async def test_event_traced_jsonl_logging(self):
        """Test that events are logged to events_traced.jsonl."""
        bus = OrchestratorEventBus()

        test_trace_id = "test-trace-correlation-123"
        event = OrchestratorEvent(
            event_type="test_correlation",
            source="test_source",
            priority=EventPriority.HIGH,
            data={"test": "correlation"},
            timestamp=time.time(),
            trace_id=test_trace_id,
        )

        await bus.publish(event)

        # Wait a bit for async file write
        await asyncio.sleep(0.1)

        # Check if file was created
        log_file = Path("data/monitor/events_traced.jsonl")
        assert log_file.exists(), "events_traced.jsonl should exist"

        # Read last line and verify trace_id
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) > 0, "events_traced.jsonl should have content"

            last_event = json.loads(lines[-1])
            assert last_event["trace_id"] == test_trace_id
            assert last_event["event_type"] == "test_correlation"
            assert "published_at" in last_event

    @pytest.mark.asyncio
    async def test_multiple_events_unique_trace_ids(self):
        """Test that multiple events get unique trace_ids."""
        bus = OrchestratorEventBus()

        events = []
        for i in range(3):
            event = OrchestratorEvent(
                event_type=f"test_event_{i}",
                source="test_source",
                priority=EventPriority.LOW,
                data={"index": i},
                timestamp=time.time(),
            )
            await bus.publish(event)
            events.append(event)

        # All events should have trace_ids
        for event in events:
            assert event.trace_id is not None

        # All trace_ids should be unique
        trace_ids = [e.trace_id for e in events]
        assert len(trace_ids) == len(set(trace_ids)), "All trace_ids should be unique"
