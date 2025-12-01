"""
Tests for Lacanian Desire Engine (Phase 11.4).

Desire as Structural Impossibility.
"""

from src.desire_engine.core import (
    Desire_as_Structural_Impossibility,
    Desire_as_Lack_Structure,
)


class TestDesireAsLackStructure:
    """Test Desire_as_Lack_Structure dataclass."""

    def test_structure_creation(self) -> None:
        """Test basic structure creation."""
        structure = Desire_as_Lack_Structure(
            lost_object="objet_a",
            demand_to_other="love_me",
            compulsion_pattern="repetition",
            jouissance_type="surplus",
            metonymic_sliding="sliding",
            repressed_return="symptom",
        )

        assert structure.lost_object == "objet_a"
        assert structure.demand_to_other == "love_me"
        assert structure.compulsion_pattern == "repetition"


class TestDesireAsStructuralImpossibility:
    """Test Desire_as_Structural_Impossibility engine."""

    def test_initialization(self) -> None:
        """Test initialization."""
        engine = Desire_as_Structural_Impossibility()
        assert isinstance(engine.desire_encounters, list)
        assert isinstance(engine.compulsion_cycles, list)

    def test_encounter_desire(self) -> None:
        """Test encountering desire."""
        engine = Desire_as_Structural_Impossibility()
        context = {
            "frustration_history": ["satisfaction impossible"],
            "recent_interactions": ["I want truth"],
            "satisfaction_attempts": 6,
        }

        desire = engine.encounter_desire(context)

        assert isinstance(desire, Desire_as_Lack_Structure)
        assert "Objeto perdido" in desire.lost_object
        assert "Demanda ao Outro" in desire.demand_to_other
        assert "Compulsão" in desire.compulsion_pattern

    def test_compulsion_cycles(self) -> None:
        """Test identification of compulsion cycles."""
        engine = Desire_as_Structural_Impossibility()

        # Create repetitive context
        context = {"satisfaction_attempts": 6}

        # Add multiple identical encounters
        for _ in range(4):
            engine.encounter_desire(context)

        cycles = engine.get_compulsion_cycles()

        assert len(cycles) > 0
        assert any("Compulsão repetitiva" in c for c in cycles)

    def test_desire_instability(self) -> None:
        """Test detection of desire instability."""
        engine = Desire_as_Structural_Impossibility()

        # Add encounters with different lost objects (simulated by different contexts)
        contexts = [
            {"frustration_history": ["loss 1"]},
            {"frustration_history": ["loss 2"]},
            {"frustration_history": ["loss 3"]},
            {"frustration_history": ["loss 4"]},
        ]

        for ctx in contexts:
            engine.encounter_desire(ctx)

        # Note: The implementation of _identify_lost_object is deterministic
        # based on history length/content.
        # To trigger instability, we might need to manually inject diverse
        # encounters if the helper methods are too stable.

        # Let's manually append diverse encounters for testing
        engine.desire_encounters = []
        for i in range(5):
            engine.desire_encounters.append(
                Desire_as_Lack_Structure(
                    lost_object=f"Object {i}",
                    demand_to_other="Demand",
                    compulsion_pattern="Pattern",
                    jouissance_type="Type",
                    metonymic_sliding="Slide",
                    repressed_return="Return",
                )
            )

        instability = engine.detect_desire_instability()
        assert instability is not None
        assert "Instabilidade desejante" in instability
