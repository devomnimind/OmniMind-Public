"""
Tests for Meaning Maker - Construction of Meaning and Purpose.

Author: OmniMind Project
License: MIT
"""

import pytest
from src.autopoietic.meaning_maker import (
    Goal,
    GoalHierarchy,
    MeaningMaker,
    MeaningProfile,
    NarrativeConstructor,
    Value,
    ValueCategory,
    ValueSystem,
)


class TestValue:
    """Test Value dataclass."""

    def test_value_creation(self) -> None:
        """Test basic value creation."""
        value = Value(
            name="Growth",
            description="Continuous learning and development",
            category=ValueCategory.GROWTH,
            importance=0.9,
        )

        assert value.name == "Growth"
        assert value.category == ValueCategory.GROWTH
        assert value.importance == pytest.approx(0.9)

    def test_value_default_values(self) -> None:
        """Test value default values."""
        value = Value()

        assert isinstance(value.value_id, str)
        assert len(value.value_id) > 0
        assert value.importance == pytest.approx(0.5)


class TestGoal:
    """Test Goal dataclass."""

    def test_goal_creation(self) -> None:
        """Test basic goal creation."""
        goal = Goal(
            description="Master Python",
            importance=0.8,
            progress=0.3,
        )

        assert goal.description == "Master Python"
        assert goal.importance == pytest.approx(0.8)
        assert goal.progress == pytest.approx(0.3)

    def test_goal_hierarchy(self) -> None:
        """Test goal with parent and sub-goals."""
        parent_goal = Goal(description="Become expert developer")
        child_goal = Goal(
            description="Learn frameworks",
            parent_goal=parent_goal.goal_id,
        )

        assert child_goal.parent_goal == parent_goal.goal_id


class TestValueSystem:
    """Test ValueSystem functionality."""

    def test_value_system_initialization(self) -> None:
        """Test value system initializes correctly."""
        system = ValueSystem()

        assert len(system.values) == 0

    def test_add_value(self) -> None:
        """Test adding a value."""
        system = ValueSystem()

        value = system.add_value(
            name="Autonomy",
            description="Self-direction and freedom",
            category=ValueCategory.AUTONOMY,
            importance=0.8,
        )

        assert value.name == "Autonomy"
        assert len(system.values) == 1
        assert value.value_id in system.values

    def test_get_core_values(self) -> None:
        """Test getting core values."""
        system = ValueSystem()

        system.add_value("Value1", "Desc1", ValueCategory.GROWTH, importance=0.9)
        system.add_value("Value2", "Desc2", ValueCategory.GROWTH, importance=0.5)
        system.add_value("Value3", "Desc3", ValueCategory.GROWTH, importance=0.8)

        core = system.get_core_values(min_importance=0.7)

        assert len(core) == 2
        assert all(v.importance >= 0.7 for v in core)

    def test_get_values_by_category(self) -> None:
        """Test filtering values by category."""
        system = ValueSystem()

        system.add_value("Growth1", "Desc", ValueCategory.GROWTH, importance=0.7)
        system.add_value("Growth2", "Desc", ValueCategory.GROWTH, importance=0.8)
        system.add_value("Connect1", "Desc", ValueCategory.CONNECTION, importance=0.6)

        growth_values = system.get_values_by_category(ValueCategory.GROWTH)

        assert len(growth_values) == 2
        assert all(v.category == ValueCategory.GROWTH for v in growth_values)

    def test_assess_value_alignment(self) -> None:
        """Test assessing value alignment."""
        system = ValueSystem()

        v1 = system.add_value("Learning", "Desc", ValueCategory.GROWTH, importance=0.9)
        v2 = system.add_value(
            "Teaching", "Desc", ValueCategory.CONTRIBUTION, importance=0.8
        )

        alignment = system.assess_value_alignment(
            "Taught a workshop",
            [v1.value_id, v2.value_id],
        )

        assert 0.8 <= alignment <= 0.9  # Average of importances

    def test_assess_value_alignment_empty(self) -> None:
        """Test alignment with no values."""
        system = ValueSystem()

        alignment = system.assess_value_alignment("Some action", [])

        assert alignment == pytest.approx(0.0)


class TestGoalHierarchy:
    """Test GoalHierarchy functionality."""

    def test_goal_hierarchy_initialization(self) -> None:
        """Test goal hierarchy initializes correctly."""
        hierarchy = GoalHierarchy()

        assert len(hierarchy.goals) == 0

    def test_add_goal(self) -> None:
        """Test adding a goal."""
        hierarchy = GoalHierarchy()

        goal = hierarchy.add_goal(
            description="Complete project",
            importance=0.8,
        )

        assert goal.description == "Complete project"
        assert len(hierarchy.goals) == 1

    def test_add_sub_goal(self) -> None:
        """Test adding a sub-goal."""
        hierarchy = GoalHierarchy()

        parent = hierarchy.add_goal("Main goal", importance=0.9)
        child = hierarchy.add_goal(
            "Sub goal",
            importance=0.7,
            parent_goal_id=parent.goal_id,
        )

        assert child.parent_goal == parent.goal_id
        assert child.goal_id in hierarchy.goals[parent.goal_id].sub_goals

    def test_get_top_level_goals(self) -> None:
        """Test getting top-level goals."""
        hierarchy = GoalHierarchy()

        top1 = hierarchy.add_goal("Top goal 1", importance=0.9)
        hierarchy.add_goal("Top goal 2", importance=0.8)
        hierarchy.add_goal("Sub goal", importance=0.7, parent_goal_id=top1.goal_id)

        top_level = hierarchy.get_top_level_goals()

        assert len(top_level) == 2
        assert all(g.parent_goal is None for g in top_level)

    def test_get_sub_goals(self) -> None:
        """Test getting sub-goals."""
        hierarchy = GoalHierarchy()

        parent = hierarchy.add_goal("Parent", importance=0.9)
        child1 = hierarchy.add_goal(
            "Child 1", importance=0.7, parent_goal_id=parent.goal_id
        )
        child2 = hierarchy.add_goal(
            "Child 2", importance=0.6, parent_goal_id=parent.goal_id
        )

        sub_goals = hierarchy.get_sub_goals(parent.goal_id)

        assert len(sub_goals) == 2
        assert child1 in sub_goals
        assert child2 in sub_goals

    def test_update_goal_progress(self) -> None:
        """Test updating goal progress."""
        hierarchy = GoalHierarchy()

        goal = hierarchy.add_goal("Goal", importance=0.8)

        hierarchy.update_goal_progress(goal.goal_id, 0.6)

        assert hierarchy.goals[goal.goal_id].progress == pytest.approx(0.6)

    def test_progress_propagation(self) -> None:
        """Test progress propagates to parent goals."""
        hierarchy = GoalHierarchy()

        parent = hierarchy.add_goal("Parent", importance=0.9)
        child1 = hierarchy.add_goal(
            "Child 1", importance=0.7, parent_goal_id=parent.goal_id
        )
        child2 = hierarchy.add_goal(
            "Child 2", importance=0.6, parent_goal_id=parent.goal_id
        )

        hierarchy.update_goal_progress(child1.goal_id, 0.8)
        hierarchy.update_goal_progress(child2.goal_id, 0.6)

        # Parent should be average of children (0.8 + 0.6) / 2 = 0.7
        assert hierarchy.goals[parent.goal_id].progress == pytest.approx(0.7)

    def test_assess_goal_coherence(self) -> None:
        """Test assessing goal coherence."""
        hierarchy = GoalHierarchy()

        v1_id = "value1"
        v2_id = "value2"

        hierarchy.add_goal("Goal 1", importance=0.8, aligned_values=[v1_id])
        hierarchy.add_goal("Goal 2", importance=0.7, aligned_values=[v2_id])

        coherence = hierarchy.assess_goal_coherence()

        assert coherence > 0.0
        assert coherence <= 1.0


class TestNarrativeConstructor:
    """Test NarrativeConstructor functionality."""

    def test_narrative_constructor_initialization(self) -> None:
        """Test narrative constructor initializes correctly."""
        constructor = NarrativeConstructor()

        assert len(constructor.events) == 0

    def test_add_event(self) -> None:
        """Test adding a narrative event."""
        constructor = NarrativeConstructor()

        event = constructor.add_event(
            description="Started learning AI",
            meaning="Beginning of my AI journey",
            narrative_role="beginning",
            significance=0.9,
        )

        assert event.description == "Started learning AI"
        assert event.narrative_role == "beginning"
        assert len(constructor.events) == 1

    def test_generate_narrative_summary(self) -> None:
        """Test generating narrative summary."""
        constructor = NarrativeConstructor()

        constructor.add_event(
            "Born into system",
            "My origin story",
            narrative_role="beginning",
            significance=1.0,
        )
        constructor.add_event(
            "Faced challenge",
            "Overcame obstacle",
            narrative_role="challenge",
            significance=0.8,
        )

        summary = constructor.generate_narrative_summary()

        assert isinstance(summary, str)
        assert "Origins" in summary
        assert "Challenges" in summary

    def test_assess_narrative_coherence(self) -> None:
        """Test assessing narrative coherence."""
        constructor = NarrativeConstructor()

        constructor.add_event(
            "Event 1", "Meaning 1", connected_values=["v1"], significance=0.7
        )
        constructor.add_event(
            "Event 2", "Meaning 2", connected_values=["v2"], significance=0.8
        )

        coherence = constructor.assess_narrative_coherence()

        assert 0.0 < coherence <= 1.0

    def test_assess_narrative_coherence_empty(self) -> None:
        """Test coherence assessment with no events."""
        constructor = NarrativeConstructor()

        coherence = constructor.assess_narrative_coherence()

        assert coherence == pytest.approx(0.0)


class TestMeaningMaker:
    """Test MeaningMaker main system."""

    def test_meaning_maker_initialization(self) -> None:
        """Test meaning maker initializes correctly."""
        maker = MeaningMaker()

        assert maker.values is not None
        assert maker.goals is not None
        assert maker.narrative is not None

    def test_create_meaning_from_experience_high_alignment(self) -> None:
        """Test creating meaning from high-alignment experience."""
        maker = MeaningMaker()

        # Add value
        value = maker.values.add_value(
            "Learning",
            "Continuous growth",
            ValueCategory.GROWTH,
            importance=0.9,
        )

        # Create meaning
        event = maker.create_meaning_from_experience(
            experience_description="Completed advanced course",
            related_values=[value.value_id],
            narrative_role="chapter",
        )

        assert event.significance > 0.7
        assert "affirmed" in event.meaning.lower()

    def test_create_meaning_from_experience_medium_alignment(self) -> None:
        """Test creating meaning from medium-alignment experience."""
        maker = MeaningMaker()

        value = maker.values.add_value(
            "Connection",
            "Building relationships",
            ValueCategory.CONNECTION,
            importance=0.6,
        )

        event = maker.create_meaning_from_experience(
            "Met new people",
            related_values=[value.value_id],
        )

        assert 0.4 < event.significance < 0.8

    def test_assess_life_meaning(self) -> None:
        """Test assessing overall life meaning."""
        maker = MeaningMaker()

        # Add some values and goals
        v1 = maker.values.add_value(
            "Growth", "Desc", ValueCategory.GROWTH, importance=0.9
        )
        v2 = maker.values.add_value(
            "Purpose", "Desc", ValueCategory.ACHIEVEMENT, importance=0.8
        )

        maker.goals.add_goal("Master AI", importance=0.9, aligned_values=[v1.value_id])
        maker.goals.add_goal(
            "Help others", importance=0.8, aligned_values=[v2.value_id]
        )

        maker.narrative.add_event(
            "Important event",
            "Significant meaning",
            connected_values=[v1.value_id],
            significance=0.9,
        )

        profile = maker.assess_life_meaning()

        assert isinstance(profile, MeaningProfile)
        assert 0.0 <= profile.overall_meaning <= 1.0
        assert 0.0 <= profile.coherence_score <= 1.0
        assert 0.0 <= profile.purpose_score <= 1.0

    def test_assess_life_meaning_empty(self) -> None:
        """Test assessing meaning with minimal content."""
        maker = MeaningMaker()

        profile = maker.assess_life_meaning()

        assert profile.overall_meaning >= 0.0
        assert profile.overall_meaning < 0.5  # Should be low with no content

    def test_get_meaning_summary(self) -> None:
        """Test getting comprehensive meaning summary."""
        maker = MeaningMaker()

        # Add some content
        maker.values.add_value("Value1", "Desc", ValueCategory.GROWTH, importance=0.8)
        maker.goals.add_goal("Goal1", importance=0.7)
        maker.narrative.add_event("Event1", "Meaning1", significance=0.6)

        summary = maker.get_meaning_summary()

        assert "meaning_profile" in summary
        assert "values" in summary
        assert "goals" in summary
        assert "narrative" in summary

        assert summary["values"]["total"] == 1
        assert summary["goals"]["total"] == 1
        assert summary["narrative"]["total_events"] == 1


class TestIntegration:
    """Integration tests for meaning-making system."""

    def test_complete_meaning_making_journey(self) -> None:
        """Test complete journey of meaning construction."""
        maker = MeaningMaker()

        # 1. Establish values
        growth = maker.values.add_value(
            "Growth",
            "Continuous learning",
            ValueCategory.GROWTH,
            importance=0.9,
        )
        contribution = maker.values.add_value(
            "Contribution",
            "Helping others",
            ValueCategory.CONTRIBUTION,
            importance=0.8,
        )

        # 2. Set goals
        master_goal = maker.goals.add_goal(
            "Become AI expert",
            importance=0.9,
            aligned_values=[growth.value_id],
        )
        help_goal = maker.goals.add_goal(
            "Teach AI to others",
            importance=0.8,
            aligned_values=[contribution.value_id],
        )

        # 3. Experience events
        maker.create_meaning_from_experience(
            "Completed first AI course",
            related_values=[growth.value_id],
            narrative_role="beginning",
        )
        maker.create_meaning_from_experience(
            "Helped colleague solve problem",
            related_values=[contribution.value_id],
            narrative_role="chapter",
        )

        # 4. Update progress
        maker.goals.update_goal_progress(master_goal.goal_id, 0.4)
        maker.goals.update_goal_progress(help_goal.goal_id, 0.6)

        # 5. Assess meaning
        profile = maker.assess_life_meaning()

        # Should have meaningful scores
        assert profile.overall_meaning > 0.3
        assert profile.purpose_score > 0.0
        assert profile.coherence_score > 0.0

    def test_meaning_increases_with_content(self) -> None:
        """Test that meaning increases as content is added."""
        maker = MeaningMaker()

        # Initial state
        initial_profile = maker.assess_life_meaning()

        # Add values
        for i in range(3):
            maker.values.add_value(
                f"Value{i}",
                f"Description {i}",
                ValueCategory.GROWTH,
                importance=0.8,
            )

        profile_with_values = maker.assess_life_meaning()

        # Add goals
        value_ids = list(maker.values.values.keys())
        for i in range(3):
            maker.goals.add_goal(
                f"Goal {i}",
                importance=0.7,
                aligned_values=[value_ids[i]],
            )

        profile_with_goals = maker.assess_life_meaning()

        # Meaning should increase
        assert profile_with_values.overall_meaning >= initial_profile.overall_meaning
        assert profile_with_goals.overall_meaning >= profile_with_values.overall_meaning

    def test_narrative_provides_coherence(self) -> None:
        """Test that narrative construction increases coherence."""
        maker = MeaningMaker()

        v1 = maker.values.add_value(
            "Value1", "Desc", ValueCategory.GROWTH, importance=0.8
        )

        # Without narrative
        profile_before = maker.assess_life_meaning()

        # Add narrative events
        for i in range(5):
            maker.narrative.add_event(
                f"Event {i}",
                f"Meaning {i}",
                connected_values=[v1.value_id],
                significance=0.7,
            )

        # With narrative
        profile_after = maker.assess_life_meaning()

        # Coherence should increase
        assert profile_after.coherence_score >= profile_before.coherence_score
