"""
Testes para Observability - Distributed Tracing.

Group 15: Learning & Monitoring - observability/
"""

import time

from src.observability.distributed_tracing import (
    DistributedTracer,
    Span,
    SpanContext,
    SpanKind,
    SpanStatus,
)


class TestSpanContext:
    """Testa SpanContext para contexto de traces."""

    def test_initialization(self) -> None:
        """Testa inicialização de SpanContext."""
        ctx = SpanContext(
            trace_id="trace123",
            span_id="span456",
            parent_span_id="parent789",
            trace_state={"key": "value"},
            is_remote=True,
        )

        assert ctx.trace_id == "trace123"
        assert ctx.span_id == "span456"
        assert ctx.parent_span_id == "parent789"
        assert ctx.trace_state == {"key": "value"}
        assert ctx.is_remote is True

    def test_to_dict(self) -> None:
        """Testa conversão para dicionário."""
        ctx = SpanContext(
            trace_id="trace123",
            span_id="span456",
        )

        ctx_dict = ctx.to_dict()

        assert isinstance(ctx_dict, dict)
        assert ctx_dict["trace_id"] == "trace123"
        assert ctx_dict["span_id"] == "span456"
        assert "parent_span_id" in ctx_dict
        assert "is_remote" in ctx_dict

    def test_from_dict(self) -> None:
        """Testa criação a partir de dicionário."""
        data = {
            "trace_id": "trace123",
            "span_id": "span456",
            "parent_span_id": "parent789",
            "trace_state": {"key": "value"},
            "is_remote": False,
        }

        ctx = SpanContext.from_dict(data)

        assert ctx.trace_id == "trace123"
        assert ctx.span_id == "span456"
        assert ctx.parent_span_id == "parent789"
        assert ctx.trace_state == {"key": "value"}
        assert ctx.is_remote is False

    def test_roundtrip_serialization(self) -> None:
        """Testa serialização ida e volta."""
        original = SpanContext(
            trace_id="trace123",
            span_id="span456",
            parent_span_id="parent789",
        )

        ctx_dict = original.to_dict()
        restored = SpanContext.from_dict(ctx_dict)

        assert restored.trace_id == original.trace_id
        assert restored.span_id == original.span_id
        assert restored.parent_span_id == original.parent_span_id


class TestSpan:
    """Testa Span para representação de operações."""

    def test_initialization(self) -> None:
        """Testa inicialização de Span."""
        context = SpanContext(trace_id="trace123", span_id="span456")

        span = Span(
            name="test_operation",
            context=context,
            kind=SpanKind.SERVER,
        )

        assert span.name == "test_operation"
        assert span.context == context
        assert span.kind == SpanKind.SERVER
        assert span.status == SpanStatus.UNSET
        assert span.attributes == {}
        assert span.events == []

    def test_set_attribute(self) -> None:
        """Testa definição de atributo."""
        context = SpanContext(trace_id="trace123", span_id="span456")
        span = Span(name="test", context=context)

        span.set_attribute("key", "value")

        assert span.attributes["key"] == "value"

    def test_set_multiple_attributes(self) -> None:
        """Testa definição de múltiplos atributos."""
        context = SpanContext(trace_id="trace123", span_id="span456")
        span = Span(name="test", context=context)

        span.set_attribute("key1", "value1")
        span.set_attribute("key2", 42)
        span.set_attribute("key3", True)

        assert span.attributes["key1"] == "value1"
        assert span.attributes["key2"] == 42
        assert span.attributes["key3"] is True

    def test_add_event(self) -> None:
        """Testa adição de evento."""
        context = SpanContext(trace_id="trace123", span_id="span456")
        span = Span(name="test", context=context)

        span.add_event("event_name", {"detail": "value"})

        assert len(span.events) == 1
        assert span.events[0]["name"] == "event_name"
        assert span.events[0]["attributes"]["detail"] == "value"
        assert "timestamp" in span.events[0]

    def test_set_status(self) -> None:
        """Testa definição de status."""
        context = SpanContext(trace_id="trace123", span_id="span456")
        span = Span(name="test", context=context)

        span.set_status(SpanStatus.OK)

        assert span.status == SpanStatus.OK

    def test_set_error_status(self) -> None:
        """Testa definição de status de erro."""
        context = SpanContext(trace_id="trace123", span_id="span456")
        span = Span(name="test", context=context)

        span.set_status(SpanStatus.ERROR, "Error message")

        assert span.status == SpanStatus.ERROR
        assert span.attributes["status_description"] == "Error message"

    def test_end_span(self) -> None:
        """Testa finalização de span."""
        context = SpanContext(trace_id="trace123", span_id="span456")
        span = Span(name="test", context=context)

        start_time = span.start_time
        time.sleep(0.01)  # Small delay
        span.end()

        assert span.end_time is not None
        assert span.end_time > start_time
        assert span.duration_ms() > 0.0

    def test_to_dict(self) -> None:
        """Testa conversão para dicionário."""
        context = SpanContext(trace_id="trace123", span_id="span456")
        span = Span(name="test_operation", context=context)
        span.set_attribute("key", "value")
        span.add_event("event1")
        span.end()

        span_dict = span.to_dict()

        assert isinstance(span_dict, dict)
        assert span_dict["name"] == "test_operation"
        assert span_dict["trace_id"] == "trace123"
        assert span_dict["attributes"]["key"] == "value"


class TestDistributedTracer:
    """Testa DistributedTracer para rastreamento distribuído."""

    def test_initialization(self) -> None:
        """Testa inicialização de DistributedTracer."""
        from src.observability.distributed_tracing import TraceConfig

        config = TraceConfig(service_name="test_service")
        tracer = DistributedTracer(config)

        assert tracer.config.service_name == "test_service"

    def test_start_span(self) -> None:
        """Testa início de span."""
        from src.observability.distributed_tracing import TraceConfig

        config = TraceConfig(service_name="test_service")
        tracer = DistributedTracer(config)

        span = tracer.start_span(name="test_operation")

        assert isinstance(span, Span)
        assert span.name == "test_operation"
        assert span.context.trace_id is not None
        assert span.context.span_id is not None

    def test_start_child_span(self) -> None:
        """Testa início de span filho."""
        from src.observability.distributed_tracing import TraceConfig

        config = TraceConfig(service_name="test_service")
        tracer = DistributedTracer(config)

        parent_span = tracer.start_span(name="parent")
        child_span = tracer.start_span(name="child", parent=parent_span.context)

        assert child_span.context.parent_span_id == parent_span.context.span_id
        assert child_span.context.trace_id == parent_span.context.trace_id

    def test_get_trace_by_id(self) -> None:
        """Testa obtenção de trace completo."""
        from src.observability.distributed_tracing import TraceConfig

        config = TraceConfig(service_name="test_service")
        tracer = DistributedTracer(config)

        parent = tracer.start_span(name="parent")

        trace_id = parent.context.trace_id
        trace_spans = tracer.get_trace(trace_id)

        assert len(trace_spans) >= 1
        assert all(s.context.trace_id == trace_id for s in trace_spans)

    def test_span_kinds(self) -> None:
        """Testa diferentes tipos de spans."""
        from src.observability.distributed_tracing import TraceConfig

        config = TraceConfig(service_name="test_service")
        tracer = DistributedTracer(config)

        server_span = tracer.start_span(name="server", kind=SpanKind.SERVER)
        client_span = tracer.start_span(name="client", kind=SpanKind.CLIENT)
        internal_span = tracer.start_span(name="internal", kind=SpanKind.INTERNAL)

        assert server_span.kind == SpanKind.SERVER
        assert client_span.kind == SpanKind.CLIENT
        assert internal_span.kind == SpanKind.INTERNAL

    def test_span_hierarchy(self) -> None:
        """Testa hierarquia de spans."""
        from src.observability.distributed_tracing import TraceConfig

        config = TraceConfig(service_name="test_service")
        tracer = DistributedTracer(config)

        root = tracer.start_span(name="root")
        child = tracer.start_span(name="child", parent=root.context)
        grandchild = tracer.start_span(name="grandchild", parent=child.context)

        # Todos devem ter o mesmo trace_id
        assert child.context.trace_id == root.context.trace_id
        assert grandchild.context.trace_id == root.context.trace_id

        # Parent IDs devem formar hierarquia
        assert child.context.parent_span_id == root.context.span_id
        assert grandchild.context.parent_span_id == child.context.span_id

    def test_create_context(self) -> None:
        """Testa criação de contexto."""
        from src.observability.distributed_tracing import TraceConfig

        config = TraceConfig(service_name="test_service")
        tracer = DistributedTracer(config)

        # Context sem parent (root)
        ctx1 = tracer.create_context()
        assert ctx1.trace_id is not None
        assert ctx1.span_id is not None
        assert ctx1.parent_span_id is None

        # Context com parent
        ctx2 = tracer.create_context(parent=ctx1)
        assert ctx2.trace_id == ctx1.trace_id  # Mesmo trace
        assert ctx2.parent_span_id == ctx1.span_id  # Parent correto
