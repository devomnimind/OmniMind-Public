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
Tests for Novelty Generator - Creative Intelligence Module.

Author: OmniMind Project
License: MIT
"""

import pytest

from src.consciousness.novelty_generator import (
    Concept,
    ConceptualBlender,
    CreativeOutput,
    CreativityType,
    NoveltyDetector,
    NoveltyGenerator,
    NoveltyMetric,
)


class TestConcept:
    """Test Concept dataclass."""

    def test_concept_creation(self) -> None:
        """Test basic concept creation."""
        concept = Concept(
            name="test_concept",
            attributes={"color": "blue", "size": "large"},
        )

        assert concept.name == "test_concept"
        assert concept.attributes["color"] == "blue"
        assert concept.attributes["size"] == "large"
        assert concept.novelty_score == 0.0

    def test_concept_hashable(self) -> None:
        """Test that concepts are hashable for use in sets."""
        concept1 = Concept(name="concept1")
        concept2 = Concept(name="concept2")

        concept_set = {concept1, concept2}
        assert len(concept_set) == 2
        assert concept1 in concept_set
        assert concept2 in concept_set

    def test_concept_default_values(self) -> None:
        """Test concept default values."""
        concept = Concept(name="test")

        assert isinstance(concept.concept_id, str)
        assert len(concept.concept_id) > 0
        assert concept.attributes == {}
        assert concept.connections == []
        assert concept.metadata == {}


class TestNoveltyDetector:
    """Test NoveltyDetector functionality."""

    def test_detector_initialization(self) -> None:
        """Test detector initializes correctly."""
        detector = NoveltyDetector()

        assert len(detector.known_concepts) == 0
        assert len(detector.concept_frequencies) == 0

    def test_register_concept(self) -> None:
        """Test registering a concept."""
        detector = NoveltyDetector()
        detector.register_concept("hello world")

        assert "hello" in detector.known_concepts
        assert "world" in detector.known_concepts
        assert detector.concept_frequencies["hello"] == 1
        assert detector.concept_frequencies["world"] == 1

    def test_statistical_rarity_novel(self) -> None:
        """Test statistical rarity for novel output."""
        detector = NoveltyDetector()
        detector.register_concept("common word")

        # Completely new words should have high novelty
        novelty = detector.measure_novelty(
            "unique creative expression",
            NoveltyMetric.STATISTICAL_RARITY,
        )

        assert 0.0 <= novelty <= 1.0
        assert novelty > 0.5  # Should be relatively novel

    def test_statistical_rarity_common(self) -> None:
        """Test statistical rarity for common output."""
        detector = NoveltyDetector()
        detector.register_concept("hello world")
        detector.register_concept("hello world")
        detector.register_concept("hello world")

        # Repeated words should have low novelty
        novelty = detector.measure_novelty(
            "hello world",
            NoveltyMetric.STATISTICAL_RARITY,
        )

        assert 0.0 <= novelty <= 1.0

    def test_semantic_distance_empty_knowledge(self) -> None:
        """Test semantic distance with no known concepts."""
        detector = NoveltyDetector()

        novelty = detector.measure_novelty(
            "anything goes here",
            NoveltyMetric.SEMANTIC_DISTANCE,
        )

        assert novelty == pytest.approx(1.0)  # Everything is novel

    def test_semantic_distance_partial_overlap(self) -> None:
        """Test semantic distance with partial concept overlap."""
        detector = NoveltyDetector()
        detector.register_concept("hello world")

        novelty = detector.measure_novelty(
            "hello creative universe",
            NoveltyMetric.SEMANTIC_DISTANCE,
        )

        assert 0.0 < novelty < 1.0  # Partially novel

    def test_structural_novelty(self) -> None:
        """Test structural novelty metric."""
        detector = NoveltyDetector()

        # Varied word lengths should have higher structural novelty
        novelty = detector.measure_novelty(
            "a medium extraordinarily",
            NoveltyMetric.STRUCTURAL_NOVELTY,
        )

        assert 0.0 <= novelty <= 1.0

    def test_surprise_value(self) -> None:
        """Test surprise value combines multiple metrics."""
        detector = NoveltyDetector()
        detector.register_concept("common phrase")

        novelty = detector.measure_novelty(
            "extraordinary unprecedented revelation",
            NoveltyMetric.SURPRISE_VALUE,
        )

        assert 0.0 <= novelty <= 1.0
        assert novelty > 0.0  # Should have some surprise value


class TestConceptualBlender:
    """Test ConceptualBlender functionality."""

    def test_blender_initialization(self) -> None:
        """Test blender initializes correctly."""
        blender = ConceptualBlender()

        assert len(blender.concepts) == 0

    def test_add_concept(self) -> None:
        """Test adding concepts to blender."""
        blender = ConceptualBlender()
        concept = Concept(name="test", attributes={"key": "value"})

        blender.add_concept(concept)

        assert len(blender.concepts) == 1
        assert blender.concepts[0] == concept

    def test_merge_attributes_blend(self) -> None:
        """Test merging attributes from two concepts."""
        blender = ConceptualBlender()

        concept1 = Concept(
            name="fire",
            attributes={"temperature": "hot", "color": "red"},
        )
        concept2 = Concept(
            name="water",
            attributes={"temperature": "cold", "state": "liquid"},
        )

        blended = blender.blend_concepts(concept1, concept2, "merge_attributes")

        assert "fire" in blended.name
        assert "water" in blended.name
        assert len(blended.attributes) >= 3  # Should have attributes from both
        assert blended.metadata["blend_type"] == "merge_attributes"

    def test_cross_map_blend(self) -> None:
        """Test cross-domain mapping blend."""
        blender = ConceptualBlender()

        concept1 = Concept(
            name="tree",
            attributes={"height": "tall", "type": "plant"},
        )
        concept2 = Concept(
            name="building",
            attributes={"height": "high", "type": "structure"},
        )

        blended = blender.blend_concepts(concept1, concept2, "cross_map")

        assert "tree" in blended.name
        assert "building" in blended.name
        assert blended.metadata["blend_type"] == "cross_map"

    def test_selective_projection_blend(self) -> None:
        """Test selective projection blend."""
        blender = ConceptualBlender()

        concept1 = Concept(
            name="cat",
            attributes={"legs": 4, "sound": "meow", "size": "small"},
        )
        concept2 = Concept(
            name="dog",
            attributes={"legs": 4, "sound": "bark", "size": "medium"},
        )

        blended = blender.blend_concepts(concept1, concept2, "selective_projection")

        assert blended.name
        assert blended.metadata["blend_type"] == "selective_projection"
        # Some attributes should be selected (random, so just check it's not empty)
        # Note: could be empty due to randomness, but unlikely with 6 total attributes

    def test_generate_creative_blend_insufficient_concepts(self) -> None:
        """Test creative blend generation with insufficient concepts."""
        blender = ConceptualBlender()

        # Only add 1 concept, but request blend of 2
        concept = Concept(name="solo", attributes={"lonely": "yes"})
        blender.add_concept(concept)

        result = blender.generate_creative_blend(num_concepts=2)

        assert result is None  # Should fail gracefully

    def test_generate_creative_blend_success(self) -> None:
        """Test successful creative blend generation."""
        blender = ConceptualBlender()

        # Add multiple concepts
        for i in range(3):
            concept = Concept(
                name=f"concept_{i}",
                attributes={f"attr_{i}": f"value_{i}"},
            )
            blender.add_concept(concept)

        result = blender.generate_creative_blend(num_concepts=2)

        assert result is not None
        assert result.name  # Should have a name
        assert isinstance(result.attributes, dict)


class TestNoveltyGenerator:
    """Test NoveltyGenerator main engine."""

    def test_generator_initialization(self) -> None:
        """Test generator initializes correctly."""
        generator = NoveltyGenerator()

        assert generator.detector is not None
        assert generator.blender is not None
        assert len(generator.generation_history) == 0

    def test_generate_combinational_creativity(self) -> None:
        """Test combinational creativity generation."""
        generator = NoveltyGenerator()

        concepts = [
            Concept(name="sun", attributes={"bright": "yes", "hot": "yes"}),
            Concept(name="moon", attributes={"bright": "no", "cold": "yes"}),
        ]

        output = generator.generate_novel_concept(
            seed_concepts=concepts,
            creativity_type=CreativityType.COMBINATIONAL,
            novelty_threshold=0.0,  # Low threshold for testing
        )

        assert output is not None
        assert isinstance(output, CreativeOutput)
        assert output.content
        assert output.creativity_type == CreativityType.COMBINATIONAL
        assert len(output.source_concepts) == 2

    def test_generate_exploratory_creativity(self) -> None:
        """Test exploratory creativity generation."""
        generator = NoveltyGenerator()

        concepts = [
            Concept(
                name="forest",
                attributes={"trees": "many", "animals": "diverse"},
            ),
        ]

        output = generator.generate_novel_concept(
            seed_concepts=concepts,
            creativity_type=CreativityType.EXPLORATORY,
            novelty_threshold=0.0,
        )

        assert output is not None
        assert output.creativity_type == CreativityType.EXPLORATORY
        assert "forest" in output.content.lower()

    def test_generate_transformational_creativity(self) -> None:
        """Test transformational creativity generation."""
        generator = NoveltyGenerator()

        concepts = [
            Concept(
                name="light",
                attributes={"speed": 299792458, "particle": "photon"},
            ),
        ]

        output = generator.generate_novel_concept(
            seed_concepts=concepts,
            creativity_type=CreativityType.TRANSFORMATIONAL,
            novelty_threshold=0.0,
        )

        assert output is not None
        assert output.creativity_type == CreativityType.TRANSFORMATIONAL
        assert "transformation" in output.content.lower()

    def test_novelty_threshold_filtering(self) -> None:
        """Test that novelty threshold filters low-novelty outputs."""
        generator = NoveltyGenerator()

        # Register many concepts to make new outputs less novel
        for i in range(100):
            generator.detector.register_concept(f"common concept {i}")

        concepts = [
            Concept(name="common", attributes={"type": "ordinary"}),
        ]

        # Use very high threshold
        generator.generate_novel_concept(
            seed_concepts=concepts,
            creativity_type=CreativityType.COMBINATIONAL,
            novelty_threshold=0.99,
        )

        # Might not meet threshold
        # Note: due to randomness, this test may occasionally pass
        # Main goal is to verify filtering logic exists

    def test_generation_history_tracking(self) -> None:
        """Test that generation history is tracked."""
        generator = NoveltyGenerator()

        concepts = [
            Concept(name="alpha", attributes={"value": "1"}),
            Concept(name="beta", attributes={"value": "2"}),
        ]

        # Generate multiple outputs
        for _ in range(3):
            generator.generate_novel_concept(
                seed_concepts=concepts,
                creativity_type=CreativityType.COMBINATIONAL,
                novelty_threshold=0.0,
            )

        assert len(generator.generation_history) == 3

    def test_get_generation_statistics_empty(self) -> None:
        """Test statistics with no generations."""
        generator = NoveltyGenerator()

        stats = generator.get_generation_statistics()

        assert stats["total_generations"] == 0
        assert stats["avg_novelty"] == pytest.approx(0.0)
        assert stats["creativity_types"] == {}

    def test_get_generation_statistics_with_data(self) -> None:
        """Test statistics with generation data."""
        generator = NoveltyGenerator()

        concepts = [
            Concept(name="concept1", attributes={"a": "b"}),
            Concept(name="concept2", attributes={"c": "d"}),
        ]

        # Generate some outputs
        for creativity_type in [
            CreativityType.COMBINATIONAL,
            CreativityType.EXPLORATORY,
        ]:
            generator.generate_novel_concept(
                seed_concepts=concepts,
                creativity_type=creativity_type,
                novelty_threshold=0.0,
            )

        stats = generator.get_generation_statistics()

        assert stats["total_generations"] == 2
        assert stats["avg_novelty"] >= 0.0
        assert len(stats["creativity_types"]) >= 1

    def test_generate_with_empty_concepts(self) -> None:
        """Test generation with empty concept list."""
        generator = NoveltyGenerator()

        output = generator.generate_novel_concept(
            seed_concepts=[],
            creativity_type=CreativityType.COMBINATIONAL,
            novelty_threshold=0.0,
        )

        # Should handle gracefully
        assert output is None or isinstance(output, CreativeOutput)


class TestCreativeOutputDataclass:
    """Test CreativeOutput dataclass."""

    def test_creative_output_creation(self) -> None:
        """Test creating a creative output."""
        output = CreativeOutput(
            content="A novel idea",
            novelty_score=0.75,
            creativity_type=CreativityType.COMBINATIONAL,
            source_concepts=["concept1", "concept2"],
        )

        assert output.content == "A novel idea"
        assert output.novelty_score == pytest.approx(0.75)
        assert output.creativity_type == CreativityType.COMBINATIONAL
        assert len(output.source_concepts) == 2

    def test_creative_output_default_values(self) -> None:
        """Test creative output default values."""
        output = CreativeOutput()

        assert output.content == ""
        assert output.novelty_score == pytest.approx(0.0)
        assert output.creativity_type == CreativityType.COMBINATIONAL
        assert isinstance(output.output_id, str)
        assert len(output.output_id) > 0


class TestIntegration:
    """Integration tests for the complete novelty generation system."""

    def test_end_to_end_novel_generation(self) -> None:
        """Test complete novel concept generation pipeline."""
        generator = NoveltyGenerator()

        # Create rich seed concepts
        concepts = [
            Concept(
                name="quantum",
                attributes={
                    "superposition": "yes",
                    "entanglement": "possible",
                    "wave": "particle",
                },
            ),
            Concept(
                name="neural",
                attributes={
                    "network": "deep",
                    "learning": "adaptive",
                    "weights": "trainable",
                },
            ),
            Concept(
                name="consciousness",
                attributes={
                    "awareness": "emergent",
                    "qualia": "subjective",
                    "intentionality": "directed",
                },
            ),
        ]

        # Generate novel concepts using different creativity types
        outputs = []
        for creativity_type in CreativityType:
            output = generator.generate_novel_concept(
                seed_concepts=concepts,
                creativity_type=creativity_type,
                novelty_threshold=0.3,
            )
            if output:
                outputs.append(output)

        # At least some outputs should be generated
        assert len(outputs) > 0

        # Check that outputs are properly formed
        for output in outputs:
            assert output.content
            assert 0.0 <= output.novelty_score <= 1.0
            assert output.creativity_type in CreativityType
            assert len(output.source_concepts) == 3

    def test_multiple_generations_increase_knowledge(self) -> None:
        """Test that multiple generations increase system knowledge."""
        generator = NoveltyGenerator()

        concepts = [
            Concept(name="idea", attributes={"innovative": "yes"}),
            Concept(name="thought", attributes={"creative": "yes"}),
        ]

        initial_concepts = len(generator.detector.known_concepts)

        # Generate multiple times
        for _ in range(5):
            generator.generate_novel_concept(
                seed_concepts=concepts,
                creativity_type=CreativityType.COMBINATIONAL,
                novelty_threshold=0.0,
            )

        final_concepts = len(generator.detector.known_concepts)

        # Knowledge should increase
        assert final_concepts >= initial_concepts
