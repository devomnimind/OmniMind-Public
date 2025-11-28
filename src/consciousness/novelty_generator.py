import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import structlog

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
Novelty Generator - True Creativity Engine.

Implements computational creativity through:
1. Conceptual blending (combining disparate concepts)
2. Divergent thinking (exploring multiple solutions)
3. Novelty detection (identifying truly new ideas)
4. Creative constraint satisfaction

Based on:
- Boden, M. A. (2004). The Creative Mind: Myths and Mechanisms
- Wiggins, G. A. (2006). A preliminary framework for description, analysis and
  comparison of creative systems
- Hofstadter, D. (1995). Fluid Concepts and Creative Analogies

Author: OmniMind Project
License: MIT
"""


logger = structlog.get_logger(__name__)


class CreativityType(Enum):
    """Types of computational creativity."""

    COMBINATIONAL = "combinational"  # Combining existing concepts
    EXPLORATORY = "exploratory"  # Exploring conceptual space
    TRANSFORMATIONAL = "transformational"  # Transforming conceptual space


class NoveltyMetric(Enum):
    """Metrics for measuring novelty."""

    STATISTICAL_RARITY = "statistical_rarity"
    SEMANTIC_DISTANCE = "semantic_distance"
    STRUCTURAL_NOVELTY = "structural_novelty"
    SURPRISE_VALUE = "surprise_value"


@dataclass
class Concept:
    """Represents a concept in conceptual space."""

    concept_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)
    novelty_score: float = 0.0
    creation_timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Make Concept hashable for use in sets."""
        return hash(self.concept_id)


@dataclass
class CreativeOutput:
    """Result of creative generation."""

    output_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    novelty_score: float = 0.0
    creativity_type: CreativityType = CreativityType.COMBINATIONAL
    source_concepts: List[str] = field(default_factory=list)
    evaluation_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class NoveltyDetector:
    """
    Detects and measures novelty in generated outputs.

    Uses multiple metrics to assess how novel/creative an output is
    compared to known concepts.
    """

    def __init__(self) -> None:
        """Initialize novelty detector."""
        self.known_concepts: Set[str] = set()
        self.concept_frequencies: Dict[str, int] = {}
        self.logger = logger.bind(component="novelty_detector")

    def measure_novelty(
        self,
        output: str,
        metric: NoveltyMetric = NoveltyMetric.STATISTICAL_RARITY,
    ) -> float:
        """
        Measure novelty of output.

        Args:
            output: Generated output to evaluate
            metric: Novelty metric to use

        Returns:
            Novelty score (0.0 = not novel, 1.0 = highly novel)
        """
        if metric == NoveltyMetric.STATISTICAL_RARITY:
            return self._statistical_rarity(output)
        elif metric == NoveltyMetric.SEMANTIC_DISTANCE:
            return self._semantic_distance(output)
        elif metric == NoveltyMetric.STRUCTURAL_NOVELTY:
            return self._structural_novelty(output)
        elif metric == NoveltyMetric.SURPRISE_VALUE:
            return self._surprise_value(output)
        else:
            self.logger.warning("unknown_metric", metric=metric)
            return 0.5

    def _statistical_rarity(self, output: str) -> float:
        """Calculate statistical rarity based on frequency."""
        tokens = output.lower().split()
        total_known = sum(self.concept_frequencies.values())

        if total_known == 0:
            # Everything is novel if we have no prior knowledge
            return 1.0

        # Calculate average frequency of tokens
        frequencies = [self.concept_frequencies.get(token, 0) for token in tokens]
        avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0

        # Convert to novelty score (lower frequency = higher novelty)
        novelty = 1.0 - min(avg_frequency / max(total_known / 100, 1), 1.0)
        return novelty

    def _semantic_distance(self, output: str) -> float:
        """Calculate semantic distance from known concepts."""
        if not self.known_concepts:
            return 1.0

        # Simple implementation: count unique words not in known concepts
        tokens = set(output.lower().split())
        novel_tokens = tokens - self.known_concepts

        if not tokens:
            return 0.0

        novelty = len(novel_tokens) / len(tokens)
        return novelty

    def _structural_novelty(self, output: str) -> float:
        """Evaluate structural novelty (e.g., unusual patterns)."""
        # Simple heuristic: longer outputs with varied word lengths tend to be more creative
        tokens = output.split()
        if not tokens:
            return 0.0

        # Measure variation in word lengths
        word_lengths = [len(token) for token in tokens]
        if len(word_lengths) < 2:
            return 0.0

        avg_length = sum(word_lengths) / len(word_lengths)
        variance = sum((length - avg_length) ** 2 for length in word_lengths) / len(word_lengths)

        # Normalize variance to 0-1 range (heuristic)
        novelty = min(variance / 10.0, 1.0)
        return novelty

    def _surprise_value(self, output: str) -> float:
        """Calculate surprise value based on unexpectedness."""
        # Combine multiple metrics for surprise
        rarity = self._statistical_rarity(output)
        distance = self._semantic_distance(output)
        structural = self._structural_novelty(output)

        # Weighted combination
        surprise = 0.4 * rarity + 0.4 * distance + 0.2 * structural
        return surprise

    def register_concept(self, concept: str) -> None:
        """Register a concept as known."""
        tokens = concept.lower().split()
        for token in tokens:
            self.known_concepts.add(token)
            self.concept_frequencies[token] = self.concept_frequencies.get(token, 0) + 1

        self.logger.debug("concept_registered", concept=concept)


class ConceptualBlender:
    """
    Blends concepts to create novel combinations.

    Implements conceptual blending theory (Fauconnier & Turner, 1998).
    """

    def __init__(self) -> None:
        """Initialize conceptual blender."""
        self.concepts: List[Concept] = []
        self.logger = logger.bind(component="conceptual_blender")

    def add_concept(self, concept: Concept) -> None:
        """Add a concept to the blender's knowledge base."""
        self.concepts.append(concept)
        self.logger.debug("concept_added", concept_name=concept.name)

    def blend_concepts(
        self,
        concept1: Concept,
        concept2: Concept,
        blend_strategy: str = "merge_attributes",
    ) -> Concept:
        """
        Blend two concepts to create a novel concept.

        Args:
            concept1: First concept to blend
            concept2: Second concept to blend
            blend_strategy: Strategy for blending (merge_attributes, cross_map, etc.)

        Returns:
            New blended concept
        """
        self.logger.info(
            "blending_concepts",
            concept1=concept1.name,
            concept2=concept2.name,
            strategy=blend_strategy,
        )

        if blend_strategy == "merge_attributes":
            return self._merge_attributes(concept1, concept2)
        elif blend_strategy == "cross_map":
            return self._cross_map(concept1, concept2)
        elif blend_strategy == "selective_projection":
            return self._selective_projection(concept1, concept2)
        else:
            # Default: simple merge
            return self._merge_attributes(concept1, concept2)

    def _merge_attributes(self, concept1: Concept, concept2: Concept) -> Concept:
        """Merge attributes from both concepts."""
        blended = Concept(
            name=f"{concept1.name}-{concept2.name}",
            attributes={**concept1.attributes, **concept2.attributes},
            connections=list(set(concept1.connections + concept2.connections)),
            metadata={
                "source_concepts": [concept1.concept_id, concept2.concept_id],
                "blend_type": "merge_attributes",
            },
        )

        self.logger.debug("blend_created", blended_name=blended.name)
        return blended

    def _cross_map(self, concept1: Concept, concept2: Concept) -> Concept:
        """Create cross-domain mapping between concepts."""
        # Map attributes from one concept to structure of another
        blended_attributes = {}

        # Take structure from concept1, content from concept2
        for key in concept1.attributes:
            if key in concept2.attributes:
                # Combine values when keys match
                blended_attributes[key] = f"{concept1.attributes[key]}+{concept2.attributes[key]}"
            else:
                blended_attributes[key] = concept1.attributes[key]

        blended = Concept(
            name=f"{concept1.name}×{concept2.name}",
            attributes=blended_attributes,
            metadata={
                "source_concepts": [concept1.concept_id, concept2.concept_id],
                "blend_type": "cross_map",
            },
        )

        return blended

    def _selective_projection(self, concept1: Concept, concept2: Concept) -> Concept:
        """Selectively project features from both concepts."""
        # Randomly select attributes from each concept
        selected_attrs = {}

        for key, value in concept1.attributes.items():
            if random.random() > 0.5:  # 50% chance to include
                selected_attrs[key] = value

        for key, value in concept2.attributes.items():
            if random.random() > 0.5:
                selected_attrs[key] = value

        blended = Concept(
            name=f"{concept1.name}⊕{concept2.name}",
            attributes=selected_attrs,
            metadata={
                "source_concepts": [concept1.concept_id, concept2.concept_id],
                "blend_type": "selective_projection",
            },
        )

        return blended

    def generate_creative_blend(self, num_concepts: int = 2) -> Optional[Concept]:
        """
        Generate a creative blend from random concepts.

        Args:
            num_concepts: Number of concepts to blend

        Returns:
            Blended concept or None if insufficient concepts
        """
        if len(self.concepts) < num_concepts:
            self.logger.warning(
                "insufficient_concepts",
                available=len(self.concepts),
                required=num_concepts,
            )
            return None

        # Randomly select concepts
        selected = random.sample(self.concepts, num_concepts)

        # Blend pairwise
        result = selected[0]
        for concept in selected[1:]:
            result = self.blend_concepts(result, concept)

        self.logger.info("creative_blend_generated", result_name=result.name)
        return result


class NoveltyGenerator:
    """
    Main novelty generation engine.

    Combines novelty detection with conceptual blending to generate
    truly creative and novel outputs.
    """

    def __init__(self) -> None:
        """Initialize novelty generator."""
        self.detector = NoveltyDetector()
        self.blender = ConceptualBlender()
        self.generation_history: List[CreativeOutput] = []
        self.logger = logger.bind(component="novelty_generator")

        self.logger.info("novelty_generator_initialized")

    def generate_novel_concept(
        self,
        seed_concepts: List[Concept],
        creativity_type: CreativityType = CreativityType.COMBINATIONAL,
        novelty_threshold: float = 0.5,
    ) -> Optional[CreativeOutput]:
        """
        Generate a novel concept.

        Args:
            seed_concepts: Concepts to use as seeds
            creativity_type: Type of creativity to employ
            novelty_threshold: Minimum novelty score required

        Returns:
            Creative output or None if failed to meet threshold
        """
        self.logger.info(
            "generating_novel_concept",
            num_seeds=len(seed_concepts),
            creativity_type=creativity_type.value,
        )

        # Add seed concepts to blender
        for concept in seed_concepts:
            self.blender.add_concept(concept)
            self.detector.register_concept(concept.name)

        # Generate based on creativity type
        if creativity_type == CreativityType.COMBINATIONAL:
            result = self._combinational_creativity(seed_concepts)
        elif creativity_type == CreativityType.EXPLORATORY:
            result = self._exploratory_creativity(seed_concepts)
        elif creativity_type == CreativityType.TRANSFORMATIONAL:
            result = self._transformational_creativity(seed_concepts)
        else:
            self.logger.warning("unknown_creativity_type", type=creativity_type)
            return None

        if result is None:
            return None

        # Measure novelty
        novelty_score = self.detector.measure_novelty(result, NoveltyMetric.SURPRISE_VALUE)

        if novelty_score < novelty_threshold:
            self.logger.info(
                "output_below_threshold",
                novelty=novelty_score,
                threshold=novelty_threshold,
            )
            return None

        # Create creative output
        output = CreativeOutput(
            content=result,
            novelty_score=novelty_score,
            creativity_type=creativity_type,
            source_concepts=[c.concept_id for c in seed_concepts],
            evaluation_metrics={
                "novelty": novelty_score,
                "surprise": self.detector.measure_novelty(result, NoveltyMetric.SURPRISE_VALUE),
            },
        )

        self.generation_history.append(output)
        self.logger.info(
            "novel_concept_generated",
            novelty=novelty_score,
            output_id=output.output_id,
        )

        return output

    def _combinational_creativity(self, concepts: List[Concept]) -> Optional[str]:
        """Generate novel output by combining concepts."""
        if len(concepts) < 2:
            return None

        # Blend concepts
        blended = self.blender.generate_creative_blend(num_concepts=min(3, len(concepts)))
        if blended is None:
            return None

        # Generate textual representation
        output = f"A novel blend: {blended.name} with attributes: "
        output += ", ".join(f"{k}={v}" for k, v in blended.attributes.items())

        return output

    def _exploratory_creativity(self, concepts: List[Concept]) -> Optional[str]:
        """Explore variations within conceptual space."""
        if not concepts:
            return None

        # Pick a random concept and explore variations
        base_concept = random.choice(concepts)

        # Generate variations by modifying attributes
        variations = []
        for key, value in base_concept.attributes.items():
            variations.append(f"modified-{key}:{value}")

        output = f"Exploration of {base_concept.name}: "
        output += ", ".join(variations)

        return output

    def _transformational_creativity(self, concepts: List[Concept]) -> Optional[str]:
        """Transform conceptual space to enable new possibilities."""
        if not concepts:
            return None

        # Create entirely new conceptual space
        base = random.choice(concepts)

        # Invert or transform attributes
        transformed_attrs = {}
        for key, value in base.attributes.items():
            # Simple transformation: reverse or negate
            if isinstance(value, str):
                transformed_attrs[f"anti-{key}"] = f"not-{value}"
            elif isinstance(value, (int, float)):
                transformed_attrs[f"inverse-{key}"] = -value
            else:
                transformed_attrs[key] = value

        output = f"Transformation of {base.name} into new space: "
        output += ", ".join(f"{k}={v}" for k, v in transformed_attrs.items())

        return output

    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about generation history."""
        if not self.generation_history:
            return {
                "total_generations": 0,
                "avg_novelty": 0.0,
                "creativity_types": {},
            }

        total = len(self.generation_history)
        avg_novelty = sum(o.novelty_score for o in self.generation_history) / total

        # Count by creativity type
        type_counts: Dict[str, int] = {}
        for output in self.generation_history:
            type_name = output.creativity_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "total_generations": total,
            "avg_novelty": avg_novelty,
            "creativity_types": type_counts,
        }
