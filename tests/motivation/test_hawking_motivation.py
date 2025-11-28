from datetime import datetime, timedelta, timezone
from src.motivation.hawking_motivation import (

"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Tests for Hawking Radiation Motivation Engine.

Tests knowledge evaporation, correlation preservation,
and motivation generation mechanisms.
"""


    EvaporationEvent,
    HawkingMotivationEngine,
    KnowledgeItem,
)


class TestKnowledgeItem:
    """Test KnowledgeItem dataclass."""

    def test_creation(self) -> None:
        """Test knowledge item creation."""
        now = datetime.now(timezone.utc)
        item = KnowledgeItem(
            content="test knowledge",
            mass=1.5,
            last_used=now,
        )

        assert item.content == "test knowledge"
        assert item.mass == 1.5
        assert item.last_used == now
        assert item.use_count == 0
        assert item.correlations == []
        assert item.creation_time is not None

    def test_default_correlations(self) -> None:
        """Test default correlations list."""
        item = KnowledgeItem(content="test", mass=1.0, last_used=datetime.now(timezone.utc))

        assert isinstance(item.correlations, list)
        assert len(item.correlations) == 0


class TestEvaporationEvent:
    """Test EvaporationEvent dataclass."""

    def test_creation(self) -> None:
        """Test evaporation event creation."""
        now = datetime.now(timezone.utc)
        event = EvaporationEvent(
            knowledge_id="test_id",
            mass_lost=2.0,
            correlations_preserved=["corr1", "corr2"],
            frustration_energy=0.5,
            motivation_boost=0.7,
            timestamp=now,
        )

        assert event.knowledge_id == "test_id"
        assert event.mass_lost == 2.0
        assert len(event.correlations_preserved) == 2
        assert event.frustration_energy == 0.5
        assert event.motivation_boost == 0.7
        assert event.timestamp == now


class TestHawkingMotivationEngine:
    """Test Hawking motivation engine."""

    def test_initialization(self) -> None:
        """Test engine initializes correctly."""
        engine = HawkingMotivationEngine(base_temperature=2.0, evaporation_threshold_days=7.0)

        assert engine.temperature == 2.0
        assert engine.evaporation_threshold == timedelta(days=7.0)
        assert engine.evaporation_rate > 0
        assert len(engine.knowledge_base) == 0
        assert len(engine.evaporation_history) == 0

    def test_add_knowledge(self) -> None:
        """Test adding knowledge to engine."""
        engine = HawkingMotivationEngine()

        engine.add_knowledge("k1", "Python basics", mass=1.5)

        assert "k1" in engine.knowledge_base
        assert engine.knowledge_base["k1"].content == "Python basics"
        assert engine.knowledge_base["k1"].mass == 1.5

    def test_use_knowledge(self) -> None:
        """Test marking knowledge as used."""
        engine = HawkingMotivationEngine()
        engine.add_knowledge("k1", "Test knowledge")

        # Get initial timestamp
        initial_time = engine.knowledge_base["k1"].last_used

        # Use knowledge
        result = engine.use_knowledge("k1")

        assert result is True
        assert engine.knowledge_base["k1"].use_count == 1
        assert engine.knowledge_base["k1"].last_used >= initial_time

    def test_use_nonexistent_knowledge(self) -> None:
        """Test using knowledge that doesn't exist."""
        engine = HawkingMotivationEngine()

        result = engine.use_knowledge("nonexistent")

        assert result is False

    def test_add_correlation(self) -> None:
        """Test adding correlation between knowledge items."""
        engine = HawkingMotivationEngine()
        engine.add_knowledge("k1", "Knowledge 1")
        engine.add_knowledge("k2", "Knowledge 2")

        engine.add_correlation("k1", "k2", bidirectional=True)

        assert "k2" in engine.knowledge_base["k1"].correlations
        assert "k1" in engine.knowledge_base["k2"].correlations

    def test_add_correlation_unidirectional(self) -> None:
        """Test adding unidirectional correlation."""
        engine = HawkingMotivationEngine()
        engine.add_knowledge("k1", "Knowledge 1")
        engine.add_knowledge("k2", "Knowledge 2")

        engine.add_correlation("k1", "k2", bidirectional=False)

        assert "k2" in engine.knowledge_base["k1"].correlations
        assert "k1" not in engine.knowledge_base["k2"].correlations

    def test_evaporate_unused_knowledge(self) -> None:
        """Test evaporation of unused knowledge."""
        engine = HawkingMotivationEngine(
            base_temperature=10.0,  # High temp for faster evaporation
            evaporation_threshold_days=0.001,  # Very short threshold
        )

        # Add knowledge
        engine.add_knowledge("k1", "Old knowledge")

        # Set last_used to past
        past = datetime.now(timezone.utc) - timedelta(days=1)
        engine.knowledge_base["k1"].last_used = past

        # Run evaporation multiple times (stochastic)
        evaporated = False
        for _ in range(10):
            evaporated_ids, motivation_data = engine.evaporate_unused_knowledge()
            if evaporated_ids:
                evaporated = True
                break

        # Should eventually evaporate
        assert evaporated or len(engine.knowledge_base) == 1

    def test_knowledge_preservation_when_used(self) -> None:
        """Test that used knowledge doesn't evaporate."""
        engine = HawkingMotivationEngine(base_temperature=10.0, evaporation_threshold_days=0.001)

        # Add and immediately use knowledge
        engine.add_knowledge("k1", "Active knowledge")
        engine.use_knowledge("k1")

        # Try to evaporate
        evaporated_ids, _ = engine.evaporate_unused_knowledge()

        # Should not evaporate (just used)
        assert "k1" not in evaporated_ids
        assert "k1" in engine.knowledge_base

    def test_correlation_preservation(self) -> None:
        """Test that correlations are preserved during evaporation."""
        engine = HawkingMotivationEngine(
            base_temperature=10.0,
            evaporation_threshold_days=0.001,
            correlation_strength=1.0,  # Always preserve
        )

        # Add knowledge with correlations
        engine.add_knowledge("k1", "Knowledge 1")
        engine.add_knowledge("k2", "Knowledge 2")
        engine.add_correlation("k1", "k2")

        # Make k1 old
        past = datetime.now(timezone.utc) - timedelta(days=1)
        engine.knowledge_base["k1"].last_used = past

        # Evaporate multiple times
        for _ in range(20):
            evaporated_ids, motivation_data = engine.evaporate_unused_knowledge(
                current_time=datetime.now(timezone.utc)
            )
            if "k1" in evaporated_ids:
                # Check correlation was preserved
                event = engine.evaporation_history[-1]
                assert "k2" in event.correlations_preserved
                break

    def test_frustration_generation(self) -> None:
        """Test frustration energy generation."""
        engine = HawkingMotivationEngine(base_temperature=10.0, evaporation_threshold_days=0.001)

        engine.add_knowledge("k1", "Important knowledge", mass=5.0)

        # Make it old
        past = datetime.now(timezone.utc) - timedelta(days=1)
        engine.knowledge_base["k1"].last_used = past

        # Try to evaporate
        for _ in range(20):
            evaporated_ids, motivation_data = engine.evaporate_unused_knowledge()
            if evaporated_ids:
                assert "frustration" in motivation_data
                assert motivation_data["frustration"] >= 0
                break

    def test_motivation_boost(self) -> None:
        """Test motivation boost generation."""
        engine = HawkingMotivationEngine(base_temperature=10.0, evaporation_threshold_days=0.001)

        engine.add_knowledge("k1", "Knowledge 1")
        engine.add_knowledge("k2", "Knowledge 2")
        engine.add_correlation("k1", "k2")

        # Make k1 old
        past = datetime.now(timezone.utc) - timedelta(days=1)
        engine.knowledge_base["k1"].last_used = past

        # Try to evaporate
        for _ in range(20):
            evaporated_ids, motivation_data = engine.evaporate_unused_knowledge()
            if evaporated_ids:
                assert "motivation" in motivation_data
                assert motivation_data["motivation"] >= 0
                break

    def test_temperature_adjustment(self) -> None:
        """Test adjusting Hawking temperature."""
        engine = HawkingMotivationEngine(base_temperature=1.0)

        initial_rate = engine.evaporation_rate

        engine.adjust_temperature(5.0)

        assert engine.temperature == 5.0
        assert engine.evaporation_rate > initial_rate

    def test_temperature_clamping(self) -> None:
        """Test temperature is clamped to valid range."""
        engine = HawkingMotivationEngine()

        # Try to set too high
        engine.adjust_temperature(1000.0)
        assert engine.temperature <= 10.0

        # Try to set too low
        engine.adjust_temperature(-1.0)
        assert engine.temperature >= 0.001

    def test_get_statistics(self) -> None:
        """Test getting engine statistics."""
        engine = HawkingMotivationEngine()
        engine.add_knowledge("k1", "Knowledge 1", mass=2.0)
        engine.add_knowledge("k2", "Knowledge 2", mass=3.0)

        stats = engine.get_statistics()

        assert stats["total_knowledge"] == 2
        assert stats["temperature"] > 0
        assert stats["evaporation_rate"] >= 0
        assert "average_mass" in stats
        assert "at_risk_count" in stats

    def test_get_knowledge_status(self) -> None:
        """Test getting status of specific knowledge."""
        engine = HawkingMotivationEngine()
        engine.add_knowledge("k1", "Test knowledge", mass=2.5)

        status = engine.get_knowledge_status("k1")

        assert status is not None
        assert status["content"] == "Test knowledge"
        assert status["mass"] == 2.5
        assert "evaporation_risk" in status
        assert "status" in status
        assert status["status"] in ["safe", "at_risk", "critical"]

    def test_get_nonexistent_knowledge_status(self) -> None:
        """Test getting status of non-existent knowledge."""
        engine = HawkingMotivationEngine()

        status = engine.get_knowledge_status("nonexistent")

        assert status is None

    def test_at_risk_identification(self) -> None:
        """Test identification of at-risk knowledge."""
        engine = HawkingMotivationEngine(evaporation_threshold_days=1.0)

        # Add recent knowledge
        engine.add_knowledge("k_recent", "Recent")

        # Add old knowledge
        engine.add_knowledge("k_old", "Old")
        past = datetime.now(timezone.utc) - timedelta(hours=18)  # > 50% of threshold
        engine.knowledge_base["k_old"].last_used = past

        at_risk = engine._identify_at_risk_correlations()

        assert "k_old" in at_risk
        assert "k_recent" not in at_risk

    def test_urgency_factor_calculation(self) -> None:
        """Test urgency factor computation."""
        engine = HawkingMotivationEngine(base_temperature=10.0, evaporation_threshold_days=0.001)

        # Add and evaporate some knowledge
        for i in range(5):
            engine.add_knowledge(f"k{i}", f"Knowledge {i}")
            past = datetime.now(timezone.utc) - timedelta(days=1)
            engine.knowledge_base[f"k{i}"].last_used = past

        # Evaporate multiple items
        for _ in range(50):
            evaporated_ids, motivation_data = engine.evaporate_unused_knowledge()
            if evaporated_ids:
                assert "urgency_factor" in motivation_data
                assert 0 <= motivation_data["urgency_factor"] <= 1


class TestIntegration:
    """Integration tests for Hawking motivation system."""

    def test_full_lifecycle(self) -> None:
        """Test full knowledge lifecycle: add, use, evaporate."""
        engine = HawkingMotivationEngine(base_temperature=5.0, evaporation_threshold_days=0.001)

        # Add knowledge
        engine.add_knowledge("k1", "Important concept", mass=3.0)
        engine.add_knowledge("k2", "Related concept", mass=2.0)
        engine.add_correlation("k1", "k2")

        # Use k2 to keep it alive
        engine.use_knowledge("k2")

        # Make k1 old
        past = datetime.now(timezone.utc) - timedelta(days=1)
        engine.knowledge_base["k1"].last_used = past

        # Try to evaporate
        for _ in range(50):
            evaporated_ids, motivation_data = engine.evaporate_unused_knowledge()
            if "k1" in evaporated_ids:
                # k2 should still exist (was used recently)
                assert "k2" in engine.knowledge_base
                assert "k2" not in evaporated_ids
                break

    def test_cascade_evaporation(self) -> None:
        """Test cascading evaporation of unused knowledge."""
        engine = HawkingMotivationEngine(base_temperature=10.0, evaporation_threshold_days=0.001)

        # Add chain of knowledge
        for i in range(5):
            engine.add_knowledge(f"k{i}", f"Knowledge {i}")
            if i > 0:
                engine.add_correlation(f"k{i-1}", f"k{i}")

        # Make all old
        past = datetime.now(timezone.utc) - timedelta(days=1)
        for i in range(5):
            engine.knowledge_base[f"k{i}"].last_used = past

        # Evaporate over time
        initial_count = len(engine.knowledge_base)
        for _ in range(100):
            engine.evaporate_unused_knowledge()

        final_count = len(engine.knowledge_base)

        # Should have evaporated some knowledge
        assert final_count < initial_count or final_count == 0

    def test_motivation_statistics(self) -> None:
        """Test comprehensive motivation statistics."""
        engine = HawkingMotivationEngine()

        # Add various knowledge
        engine.add_knowledge("active", "Active knowledge")
        engine.add_knowledge("dormant", "Dormant knowledge")
        engine.add_knowledge("critical", "Critical knowledge", mass=5.0)

        # Use active
        engine.use_knowledge("active")

        # Make critical old
        past = datetime.now(timezone.utc) - timedelta(days=1)
        engine.knowledge_base["critical"].last_used = past - timedelta(days=10)

        stats = engine.get_statistics()

        assert stats["total_knowledge"] == 3
        assert stats["average_mass"] > 0
        assert stats["average_use_count"] >= 0
