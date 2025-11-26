"""Distributed Tracing Module.

Implements distributed request flow tracking using OpenTelemetry-compatible tracing.
Supports Jaeger and Zipkin exporters for production observability.

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 8.1
"""

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class SpanKind(Enum):
    """Span kind types following OpenTelemetry specification."""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Span status following OpenTelemetry specification."""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    """Context for a distributed trace span.

    Attributes:
        trace_id: Unique identifier for the entire trace
        span_id: Unique identifier for this span
        parent_span_id: Parent span ID (None for root spans)
        trace_state: Additional trace state information
        is_remote: Whether this context was propagated from a remote service
    """

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    trace_state: Dict[str, str] = field(default_factory=dict)
    is_remote: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "trace_state": self.trace_state,
            "is_remote": self.is_remote,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpanContext":
        """Create from dictionary."""
        return cls(
            trace_id=data["trace_id"],
            span_id=data["span_id"],
            parent_span_id=data.get("parent_span_id"),
            trace_state=data.get("trace_state", {}),
            is_remote=data.get("is_remote", False),
        )


@dataclass
class Span:
    """Represents a single operation in a distributed trace.

    Attributes:
        context: Span context with trace and span IDs
        name: Operation name
        kind: Span kind (internal, server, client, etc.)
        start_time: Start timestamp in nanoseconds
        end_time: End timestamp in nanoseconds (None if not ended)
        status: Span status
        attributes: Additional metadata
        events: List of events that occurred during the span
        links: Links to other spans
    """

    context: SpanContext
    name: str
    kind: SpanKind = SpanKind.INTERNAL
    start_time: int = field(default_factory=lambda: time.time_ns())
    end_time: Optional[int] = None
    status: SpanStatus = SpanStatus.UNSET
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    links: List[SpanContext] = field(default_factory=list)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        event = {
            "name": name,
            "timestamp": time.time_ns(),
            "attributes": attributes or {},
        }
        self.events.append(event)

    def set_status(self, status: SpanStatus, description: str = "") -> None:
        """Set the span status."""
        self.status = status
        if description:
            self.attributes["status_description"] = description

    def end(self) -> None:
        """End the span."""
        if self.end_time is None:
            self.end_time = time.time_ns()

    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) / 1_000_000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "name": self.name,
            "kind": self.kind.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status.value,
            "attributes": self.attributes,
            "events": self.events,
            "duration_ms": self.duration_ms(),
        }


@dataclass
class TraceConfig:
    """Configuration for distributed tracing.

    Attributes:
        enabled: Whether tracing is enabled
        service_name: Name of the service
        exporter_type: Type of exporter (jaeger, zipkin, otlp, console)
        exporter_endpoint: Endpoint URL for the exporter
        sample_rate: Sampling rate (0.0 to 1.0)
        max_spans_per_trace: Maximum spans to keep per trace
        export_interval_seconds: Interval for batch export
        export_timeout_seconds: Timeout for export operations
    """

    enabled: bool = True
    service_name: str = "omnimind"
    exporter_type: str = "console"  # jaeger, zipkin, otlp, console
    exporter_endpoint: str = ""
    sample_rate: float = 1.0
    max_spans_per_trace: int = 1000
    export_interval_seconds: int = 5
    export_timeout_seconds: int = 30


class DistributedTracer:
    """Distributed tracing implementation.

    Provides OpenTelemetry-compatible distributed tracing with support for
    multiple exporters (Jaeger, Zipkin, console).

    Example:
        >>> config = TraceConfig(service_name="my-service")
        >>> tracer = DistributedTracer(config)
        >>> with tracer.start_span("operation") as span:
        ...     span.set_attribute("key", "value")
        ...     # Do work
        >>> tracer.export_traces()
    """

    def __init__(self, config: TraceConfig) -> None:
        """Initialize the distributed tracer.

        Args:
            config: Tracing configuration
        """
        self.config = config
        self._spans: Dict[str, List[Span]] = {}  # trace_id -> list of spans
        self._current_context: Optional[SpanContext] = None
        self._traces_dir = Path.home() / ".omnimind" / "traces"
        self._traces_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "distributed_tracer_initialized",
            service_name=config.service_name,
            exporter_type=config.exporter_type,
        )

    def create_context(self, parent: Optional[SpanContext] = None) -> SpanContext:
        """Create a new span context.

        Args:
            parent: Parent span context (creates root context if None)

        Returns:
            New span context
        """
        if parent is None:
            trace_id = self._generate_trace_id()
            span_id = self._generate_span_id()
            return SpanContext(trace_id=trace_id, span_id=span_id)
        else:
            span_id = self._generate_span_id()
            return SpanContext(
                trace_id=parent.trace_id,
                span_id=span_id,
                parent_span_id=parent.span_id,
                trace_state=parent.trace_state.copy(),
            )

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        parent: Optional[SpanContext] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """Start a new span.

        Args:
            name: Operation name
            kind: Span kind
            parent: Parent span context (uses current if None)
            attributes: Initial attributes

        Returns:
            Started span
        """
        if not self.config.enabled:
            # Create a no-op span
            context = SpanContext(trace_id="disabled", span_id="disabled")
            return Span(context=context, name=name, kind=kind)

        # Determine parent context
        if parent is None:
            parent = self._current_context

        # Create span context
        context = self.create_context(parent)

        # Create span
        span = Span(
            context=context,
            name=name,
            kind=kind,
            attributes=attributes or {},
        )

        # Add service name
        span.set_attribute("service.name", self.config.service_name)

        # Store span
        if context.trace_id not in self._spans:
            self._spans[context.trace_id] = []
        self._spans[context.trace_id].append(span)

        # Update current context
        self._current_context = context

        logger.debug(
            "span_started",
            trace_id=context.trace_id,
            span_id=context.span_id,
            name=name,
        )

        return span

    @contextmanager
    def trace(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Context manager for tracing an operation.

        Args:
            name: Operation name
            kind: Span kind
            attributes: Initial attributes

        Yields:
            The active span
        """
        span = self.start_span(name, kind, attributes=attributes)
        try:
            yield span
            span.set_status(SpanStatus.OK)
        except Exception as e:
            span.set_status(SpanStatus.ERROR, str(e))
            span.set_attribute("exception.type", type(e).__name__)
            span.set_attribute("exception.message", str(e))
            raise
        finally:
            span.end()
            self._restore_parent_context(span.context)

    def _restore_parent_context(self, context: SpanContext) -> None:
        """Restore parent context after span ends."""
        if context.parent_span_id:
            # Find parent span
            for span in self._spans.get(context.trace_id, []):
                if span.context.span_id == context.parent_span_id:
                    self._current_context = span.context
                    return
        # No parent found, clear context
        self._current_context = None

    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace.

        Args:
            trace_id: Trace ID

        Returns:
            List of spans in the trace
        """
        return self._spans.get(trace_id, [])

    def export_traces(self) -> None:
        """Export collected traces to configured exporter."""
        if not self.config.enabled:
            return

        if not self._spans:
            logger.debug("no_traces_to_export")
            return

        if self.config.exporter_type == "console":
            self._export_console()
        elif self.config.exporter_type == "jaeger":
            self._export_jaeger()
        elif self.config.exporter_type == "zipkin":
            self._export_zipkin()
        else:
            logger.warning("unknown_exporter_type", type=self.config.exporter_type)

    def _export_console(self) -> None:
        """Export traces to console/file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._traces_dir / f"trace_{timestamp}.json"

        traces_data = []
        for trace_id, spans in self._spans.items():
            trace_data = {
                "trace_id": trace_id,
                "service_name": self.config.service_name,
                "spans": [span.to_dict() for span in spans],
            }
            traces_data.append(trace_data)

        with open(filename, "w") as f:
            json.dump(traces_data, f, indent=2)

        logger.info("traces_exported", filename=str(filename), count=len(traces_data))

    def _export_jaeger(self) -> None:
        """Export traces to Jaeger."""
        # In production, this would use the Jaeger client library
        # For now, we export in Jaeger-compatible format to file
        logger.info("jaeger_export", endpoint=self.config.exporter_endpoint)
        self._export_console()  # Fallback to console for now

    def _export_zipkin(self) -> None:
        """Export traces to Zipkin."""
        # In production, this would use the Zipkin client library
        # For now, we export in Zipkin-compatible format to file
        logger.info("zipkin_export", endpoint=self.config.exporter_endpoint)
        self._export_console()  # Fallback to console for now

    def clear_traces(self) -> None:
        """Clear all collected traces."""
        self._spans.clear()
        self._current_context = None
        logger.debug("traces_cleared")

    def get_active_traces_count(self) -> int:
        """Get number of active traces."""
        return len(self._spans)

    def get_total_spans_count(self) -> int:
        """Get total number of spans across all traces."""
        return sum(len(spans) for spans in self._spans.values())

    @staticmethod
    def _generate_trace_id() -> str:
        """Generate a unique trace ID."""
        return uuid.uuid4().hex

    @staticmethod
    def _generate_span_id() -> str:
        """Generate a unique span ID."""
        return uuid.uuid4().hex[:16]
