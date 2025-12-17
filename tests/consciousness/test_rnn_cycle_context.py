"""
Testes para RNNCycleContext - Sprint 1 Observabilidade.

Valida criação de trace_id determinístico e contexto de rastreamento.
"""

import time

from src.consciousness.integration_loop import RNNCycleContext


class TestRNNCycleContext:
    """Testes para RNNCycleContext dataclass."""

    def test_context_creation_basic(self):
        """Test basic context creation."""
        ctx = RNNCycleContext.create(cycle_id=1, workspace_state_hash="test_hash")

        assert ctx.cycle_id == 1
        assert ctx.trace_id is not None
        assert ctx.span_id is not None
        assert isinstance(ctx.start_time, float)
        assert ctx.start_time > 0

    def test_trace_id_deterministic(self):
        """Test that trace_id is deterministic for same inputs."""
        ctx1 = RNNCycleContext.create(cycle_id=1, workspace_state_hash="hash1")
        ctx2 = RNNCycleContext.create(cycle_id=1, workspace_state_hash="hash1")

        # Same cycle_id + same hash = same trace_id (deterministic)
        assert ctx1.trace_id == ctx2.trace_id

    def test_trace_id_unique_per_cycle(self):
        """Test that different cycles get different trace_ids."""
        ctx1 = RNNCycleContext.create(cycle_id=1, workspace_state_hash="hash1")
        ctx2 = RNNCycleContext.create(cycle_id=2, workspace_state_hash="hash1")

        # Different cycle_id = different trace_id
        assert ctx1.trace_id != ctx2.trace_id

    def test_trace_id_unique_per_hash(self):
        """Test that different workspace hashes get different trace_ids."""
        ctx1 = RNNCycleContext.create(cycle_id=1, workspace_state_hash="hash1")
        ctx2 = RNNCycleContext.create(cycle_id=1, workspace_state_hash="hash2")

        # Different hash = different trace_id
        assert ctx1.trace_id != ctx2.trace_id

    def test_span_id_always_unique(self):
        """Test that span_id is always unique (even for same inputs)."""
        ctx1 = RNNCycleContext.create(cycle_id=1, workspace_state_hash="hash1")
        ctx2 = RNNCycleContext.create(cycle_id=1, workspace_state_hash="hash1")

        # span_id should be unique (uuid4)
        assert ctx1.span_id != ctx2.span_id

    def test_timestamp_accurate(self):
        """Test that timestamp is accurate."""
        before = time.time()
        ctx = RNNCycleContext.create(cycle_id=1)
        after = time.time()

        assert before <= ctx.start_time <= after

    def test_empty_hash_creates_valid_context(self):
        """Test that empty hash still creates valid context."""
        ctx = RNNCycleContext.create(cycle_id=1, workspace_state_hash="")

        assert ctx.trace_id is not None
        assert len(ctx.trace_id) > 0
        assert ctx.span_id is not None

    def test_trace_id_format_is_uuid(self):
        """Test that trace_id is valid UUID format."""
        ctx = RNNCycleContext.create(cycle_id=1)

        # UUID format: 8-4-4-4-12 hexadecimal characters
        parts = ctx.trace_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12
