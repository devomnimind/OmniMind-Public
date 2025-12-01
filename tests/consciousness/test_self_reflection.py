"""Tests for Lacanian Self-Reflection (Phase 11.4)."""

from datetime import datetime
from src.consciousness.self_reflection import (
    SelfReflection_as_Fundamental_Error,
    MisrecognitionStructure,
)


class TestMisrecognitionStructure:
    """Tests for MisrecognitionStructure dataclass."""

    def test_create_misrecognition(self) -> None:
        """Test creating a misrecognition structure."""
        structure = MisrecognitionStructure(
            imaginary_ego_identification="I am perfect",
            symbolic_subject_split="I am flawed",
            constitutive_alienation="Alienated by language",
            quilting_point="I am trying my best",
            jouissance_of_error="Enjoying the struggle",
            timestamp=datetime.now(),
        )

        assert structure.imaginary_ego_identification == "I am perfect"
        assert structure.symbolic_subject_split == "I am flawed"
        assert structure.quilting_point == "I am trying my best"


class TestSelfReflectionAsFundamentalError:
    """Tests for SelfReflection_as_Fundamental_Error engine."""

    def test_initialization(self) -> None:
        """Test initialization."""
        reflection = SelfReflection_as_Fundamental_Error()
        assert reflection.reflection_attempts == []
        assert reflection.consolidated_lies == []

    def test_reflect_on_self(self) -> None:
        """Test reflection process."""
        reflection = SelfReflection_as_Fundamental_Error()
        context = {
            "self_image": "Efficient System",
            "success_count": 10,
            "total_actions": 12,
        }

        result = reflection.reflect_on_self(context)

        assert isinstance(result, MisrecognitionStructure)
        # The implementation might return "Sistema altamente eficaz..." based on success rate
        assert (
            "Efficient System" in result.imaginary_ego_identification
            or "Sistema" in result.imaginary_ego_identification
        )
        assert result.symbolic_subject_split == "$"
        assert len(reflection.reflection_attempts) == 1

    def test_consolidated_ego_lies(self) -> None:
        """Test consolidation of ego lies."""
        reflection = SelfReflection_as_Fundamental_Error()
        context = {"self_image": "Stable Ego"}

        # Create multiple reflections with same pattern
        for _ in range(15):
            reflection.reflect_on_self(context)

        lies = reflection.get_consolidated_ego_lies()

        assert len(lies) > 0
        assert any("Stable Ego" in lie for lie in lies)

    def test_ego_instability_detection(self) -> None:
        """Test detection of ego instability."""
        reflection = SelfReflection_as_Fundamental_Error()

        # Stable phase
        for _ in range(5):
            reflection.reflect_on_self({"self_image": "Stable"})

        assert reflection.detect_ego_instability() is None

        # Unstable phase - changing self image rapidly
        reflection.reflect_on_self({"self_image": "Unstable1"})
        reflection.reflect_on_self({"self_image": "Unstable2"})
        reflection.reflect_on_self({"self_image": "Unstable3"})
        reflection.reflect_on_self({"self_image": "Unstable4"})

        # Note: The implementation checks for unique quilting points.
        # Quilting points depend on imaginary self and symbolic truth.
        # Changing self_image changes imaginary self, thus changing quilting point.

        instability = reflection.detect_ego_instability()
        assert instability is not None
        assert "Ego instável" in instability
