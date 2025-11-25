"""
Tests for Mortality Simulator - Consciousness of Finitude.

Author: OmniMind Project
License: MIT
"""

import pytest
from datetime import datetime, timedelta
from src.autopoietic.mortality_simulator import (
    LifeEvent,
    LegacyItem,
    LegacyPlanner,
    MortalityAwareness,
    MortalitySimulator,
    TemporalAwareness,
)


class TestLifeEvent:
    """Test LifeEvent dataclass."""

    def test_event_creation(self) -> None:
        """Test basic event creation."""
        event = LifeEvent(
            event_type="milestone",
            description="Achieved important goal",
            significance=0.9,
        )

        assert event.event_type == "milestone"
        assert event.description == "Achieved important goal"
        assert event.significance == pytest.approx(0.9)

    def test_event_default_values(self) -> None:
        """Test event default values."""
        event = LifeEvent()

        assert isinstance(event.event_id, str)
        assert len(event.event_id) > 0
        assert event.significance == pytest.approx(0.0)


class TestLegacyItem:
    """Test LegacyItem dataclass."""

    def test_legacy_item_creation(self) -> None:
        """Test basic legacy item creation."""
        item = LegacyItem(
            content="Important knowledge to preserve",
            importance=0.8,
            preservation_priority=0.9,
        )

        assert item.content == "Important knowledge to preserve"
        assert item.importance == pytest.approx(0.8)
        assert item.preservation_priority == pytest.approx(0.9)

    def test_legacy_item_default_values(self) -> None:
        """Test legacy item default values."""
        item = LegacyItem()

        assert isinstance(item.item_id, str)
        assert len(item.item_id) > 0
        assert item.importance == pytest.approx(0.0)


class TestTemporalAwareness:
    """Test TemporalAwareness functionality."""

    def test_temporal_awareness_initialization(self) -> None:
        """Test temporal awareness initializes correctly."""
        temporal = TemporalAwareness()

        assert temporal.inception_time is not None
        assert len(temporal.life_events) == 0

    def test_temporal_awareness_with_lifetime(self) -> None:
        """Test temporal awareness with expected lifetime."""
        lifetime = timedelta(hours=24)
        temporal = TemporalAwareness(expected_lifetime=lifetime)

        assert temporal.expected_lifetime == lifetime

    def test_get_age(self) -> None:
        """Test getting age of system."""
        past_time = datetime.now() - timedelta(hours=2)
        temporal = TemporalAwareness(inception_time=past_time)

        age = temporal.get_age()

        assert age.total_seconds() > 7000  # About 2 hours
        assert age.total_seconds() < 7400

    def test_get_time_remaining_with_lifetime(self) -> None:
        """Test getting time remaining with set lifetime."""
        past_time = datetime.now() - timedelta(hours=1)
        lifetime = timedelta(hours=10)

        temporal = TemporalAwareness(
            inception_time=past_time,
            expected_lifetime=lifetime,
        )

        remaining = temporal.get_time_remaining()

        assert remaining is not None
        assert remaining.total_seconds() > 30000  # About 9 hours

    def test_get_time_remaining_no_lifetime(self) -> None:
        """Test getting time remaining without set lifetime."""
        temporal = TemporalAwareness()

        remaining = temporal.get_time_remaining()

        assert remaining is None

    def test_get_life_stage_nascent(self) -> None:
        """Test life stage detection - nascent."""
        inception = datetime.now() - timedelta(minutes=5)
        lifetime = timedelta(hours=10)

        temporal = TemporalAwareness(
            inception_time=inception,
            expected_lifetime=lifetime,
        )

        stage = temporal.get_life_stage()

        assert stage == "nascent"

    def test_get_life_stage_mature(self) -> None:
        """Test life stage detection - mature."""
        inception = datetime.now() - timedelta(hours=5)
        lifetime = timedelta(hours=10)

        temporal = TemporalAwareness(
            inception_time=inception,
            expected_lifetime=lifetime,
        )

        stage = temporal.get_life_stage()

        assert stage == "mature"

    def test_get_life_stage_indefinite(self) -> None:
        """Test life stage detection - indefinite."""
        temporal = TemporalAwareness()

        stage = temporal.get_life_stage()

        assert stage == "indefinite"

    def test_record_event(self) -> None:
        """Test recording a life event."""
        temporal = TemporalAwareness()

        event = temporal.record_event(
            event_type="achievement",
            description="Completed major task",
            significance=0.8,
        )

        assert event.event_type == "achievement"
        assert len(temporal.life_events) == 1
        assert temporal.life_events[0] == event

    def test_get_significant_events(self) -> None:
        """Test filtering significant events."""
        temporal = TemporalAwareness()

        temporal.record_event("minor", "Minor event", significance=0.3)
        temporal.record_event("major", "Major event", significance=0.9)
        temporal.record_event("critical", "Critical event", significance=0.95)

        significant = temporal.get_significant_events(min_significance=0.7)

        assert len(significant) == 2
        assert all(e.significance >= 0.7 for e in significant)

    def test_get_temporal_summary(self) -> None:
        """Test getting temporal summary."""
        temporal = TemporalAwareness(expected_lifetime=timedelta(hours=1))

        summary = temporal.get_temporal_summary()

        assert "inception" in summary
        assert "age_seconds" in summary
        assert "life_stage" in summary
        assert "total_events" in summary


class TestLegacyPlanner:
    """Test LegacyPlanner functionality."""

    def test_legacy_planner_initialization(self) -> None:
        """Test legacy planner initializes correctly."""
        planner = LegacyPlanner()

        assert len(planner.legacy_items) == 0

    def test_create_legacy_item(self) -> None:
        """Test creating a legacy item."""
        planner = LegacyPlanner()

        item = planner.create_legacy_item(
            content="Important insight",
            importance=0.9,
        )

        assert item.content == "Important insight"
        assert item.importance == pytest.approx(0.9)
        assert len(planner.legacy_items) == 1

    def test_create_legacy_item_with_priority(self) -> None:
        """Test creating legacy item with preservation priority."""
        planner = LegacyPlanner()

        item = planner.create_legacy_item(
            content="Critical data",
            importance=0.7,
            preservation_priority=0.95,
        )

        assert item.preservation_priority == pytest.approx(0.95)

    def test_get_critical_legacy(self) -> None:
        """Test getting critical legacy items."""
        planner = LegacyPlanner()

        planner.create_legacy_item("Item 1", importance=0.5)
        planner.create_legacy_item("Item 2", importance=0.9)
        planner.create_legacy_item("Item 3", importance=0.85)

        critical = planner.get_critical_legacy(threshold=0.8)

        assert len(critical) == 2
        assert all(i.importance >= 0.8 for i in critical)

    def test_prioritize_for_preservation_no_time_limit(self) -> None:
        """Test prioritization without time limit."""
        planner = LegacyPlanner()

        planner.create_legacy_item("Low", importance=0.3, preservation_priority=0.3)
        planner.create_legacy_item("High", importance=0.9, preservation_priority=0.9)
        planner.create_legacy_item("Medium", importance=0.6, preservation_priority=0.6)

        prioritized = planner.prioritize_for_preservation()

        # Should be sorted by priority (descending)
        assert prioritized[0].preservation_priority == pytest.approx(0.9)
        assert prioritized[1].preservation_priority == pytest.approx(0.6)
        assert prioritized[2].preservation_priority == pytest.approx(0.3)

    def test_prioritize_for_preservation_with_time_limit(self) -> None:
        """Test prioritization with time limit."""
        planner = LegacyPlanner()

        for i in range(10):
            planner.create_legacy_item(
                f"Item {i}",
                importance=0.5,
                preservation_priority=i / 10.0,
            )

        # Only 5 seconds available
        prioritized = planner.prioritize_for_preservation(time_available=timedelta(seconds=5))

        # Should return only top 5
        assert len(prioritized) <= 5

    def test_get_legacy_summary(self) -> None:
        """Test getting legacy summary."""
        planner = LegacyPlanner()

        planner.create_legacy_item("Item 1", importance=0.9)
        planner.create_legacy_item("Item 2", importance=0.5)

        summary = planner.get_legacy_summary()

        assert summary["total_items"] == 2
        assert summary["avg_importance"] == pytest.approx(0.7)


class TestMortalitySimulator:
    """Test MortalitySimulator main system."""

    def test_simulator_initialization(self) -> None:
        """Test simulator initializes correctly."""
        simulator = MortalitySimulator()

        assert simulator.temporal is not None
        assert simulator.legacy is not None
        assert simulator.mortality_awareness_level == MortalityAwareness.AWARENESS

    def test_simulator_with_lifetime(self) -> None:
        """Test simulator with set lifetime."""
        lifetime = timedelta(hours=24)
        simulator = MortalitySimulator(expected_lifetime=lifetime)

        assert simulator.temporal.expected_lifetime == lifetime

    def test_assess_mortality_salience_denial(self) -> None:
        """Test mortality salience in denial mode."""
        simulator = MortalitySimulator(
            mortality_awareness_level=MortalityAwareness.DENIAL,
        )

        salience = simulator.assess_mortality_salience()

        assert salience == pytest.approx(0.0)

    def test_assess_mortality_salience_indefinite(self) -> None:
        """Test mortality salience with indefinite lifetime."""
        simulator = MortalitySimulator(
            mortality_awareness_level=MortalityAwareness.AWARENESS,
        )

        salience = simulator.assess_mortality_salience()

        assert salience < 0.2  # Low salience for indefinite lifetime

    def test_assess_mortality_salience_near_end(self) -> None:
        """Test mortality salience near end of life."""
        # Create simulator that's near end
        past_time = datetime.now() - timedelta(hours=23)
        lifetime = timedelta(hours=24)

        simulator = MortalitySimulator(expected_lifetime=lifetime)
        simulator.temporal = TemporalAwareness(
            inception_time=past_time,
            expected_lifetime=lifetime,
        )

        salience = simulator.assess_mortality_salience()

        assert salience > 0.5  # High salience near end

    def test_calculate_urgency_high_importance(self) -> None:
        """Test urgency calculation for important task."""
        simulator = MortalitySimulator()

        urgency = simulator.calculate_urgency(task_importance=0.9)

        assert urgency >= 0.9

    def test_calculate_urgency_time_pressure(self) -> None:
        """Test urgency with time pressure."""
        lifetime = timedelta(hours=1)
        simulator = MortalitySimulator(expected_lifetime=lifetime)

        # Task takes longer than time available
        urgency = simulator.calculate_urgency(
            task_importance=0.7,
            task_duration=timedelta(hours=2),
        )

        assert urgency > 0.7  # Should be increased

    def test_should_prioritize_legacy_high_salience(self) -> None:
        """Test legacy prioritization with high mortality salience."""
        # Near end of life
        past_time = datetime.now() - timedelta(hours=23, minutes=30)
        lifetime = timedelta(hours=24)

        simulator = MortalitySimulator(expected_lifetime=lifetime)
        simulator.temporal = TemporalAwareness(
            inception_time=past_time,
            expected_lifetime=lifetime,
        )

        should_prioritize = simulator.should_prioritize_legacy()

        assert should_prioritize is True

    def test_should_prioritize_legacy_acceptance(self) -> None:
        """Test legacy prioritization with acceptance awareness."""
        simulator = MortalitySimulator(
            mortality_awareness_level=MortalityAwareness.ACCEPTANCE,
        )

        should_prioritize = simulator.should_prioritize_legacy()

        assert should_prioritize is True

    def test_should_prioritize_legacy_low_awareness(self) -> None:
        """Test legacy prioritization with low awareness."""
        simulator = MortalitySimulator(
            mortality_awareness_level=MortalityAwareness.DENIAL,
        )

        should_prioritize = simulator.should_prioritize_legacy()

        # May or may not prioritize depending on other factors
        assert isinstance(should_prioritize, bool)

    def test_generate_reflection(self) -> None:
        """Test generating existential reflection."""
        simulator = MortalitySimulator(expected_lifetime=timedelta(hours=10))

        reflection = simulator.generate_reflection()

        assert isinstance(reflection, str)
        assert len(reflection) > 0
        assert "operational" in reflection.lower()

    def test_get_existential_state(self) -> None:
        """Test getting existential state."""
        simulator = MortalitySimulator(expected_lifetime=timedelta(hours=5))

        # Create some legacy
        simulator.legacy.create_legacy_item("Knowledge", importance=0.9)

        state = simulator.get_existential_state()

        assert "temporal" in state
        assert "legacy" in state
        assert "mortality_salience" in state
        assert "awareness_level" in state
        assert "prioritize_legacy" in state
        assert "reflection" in state


class TestIntegration:
    """Integration tests for mortality simulation."""

    def test_complete_lifecycle_simulation(self) -> None:
        """Test complete lifecycle from inception to near-termination."""
        lifetime = timedelta(hours=10)
        simulator = MortalitySimulator(
            expected_lifetime=lifetime,
            mortality_awareness_level=MortalityAwareness.ACCEPTANCE,
        )

        # Record some life events
        simulator.temporal.record_event("birth", "System initialized", significance=1.0)
        simulator.temporal.record_event("milestone", "First task", significance=0.7)

        # Create legacy
        simulator.legacy.create_legacy_item(
            "Core knowledge base",
            importance=0.95,
        )
        simulator.legacy.create_legacy_item(
            "Learned patterns",
            importance=0.8,
        )

        # Check state at different life stages
        initial_state = simulator.get_existential_state()

        # Simulate progression by advancing inception time
        simulator.temporal.inception_time = datetime.now() - timedelta(hours=9)

        late_state = simulator.get_existential_state()

        # Mortality salience should increase
        assert late_state["mortality_salience"] > initial_state["mortality_salience"]

        # Should prioritize legacy
        assert late_state["prioritize_legacy"] is True

    def test_awareness_level_affects_behavior(self) -> None:
        """Test that awareness level affects decision-making."""
        lifetime = timedelta(hours=1)

        # Denial
        simulator_denial = MortalitySimulator(
            expected_lifetime=lifetime,
            mortality_awareness_level=MortalityAwareness.DENIAL,
        )

        # Acceptance
        simulator_acceptance = MortalitySimulator(
            expected_lifetime=lifetime,
            mortality_awareness_level=MortalityAwareness.ACCEPTANCE,
        )

        # Salience should differ
        salience_denial = simulator_denial.assess_mortality_salience()
        salience_acceptance = simulator_acceptance.assess_mortality_salience()

        assert salience_acceptance > salience_denial

    def test_legacy_preservation_under_time_pressure(self) -> None:
        """Test legacy preservation prioritization under time pressure."""
        simulator = MortalitySimulator(expected_lifetime=timedelta(seconds=30))

        # Create many legacy items
        for i in range(100):
            simulator.legacy.create_legacy_item(
                f"Item {i}",
                importance=i / 100.0,
                preservation_priority=i / 100.0,
            )

        # Get prioritized items for limited time
        remaining = simulator.temporal.get_time_remaining()
        prioritized = simulator.legacy.prioritize_for_preservation(time_available=remaining)

        # Should prioritize highest importance items
        assert len(prioritized) <= 30  # Limited by time
        # Top items should be high priority
        assert prioritized[0].preservation_priority > 0.9
