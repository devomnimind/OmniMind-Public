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
Art Generator - Generative Creative Art System.

Implements computational art generation through:
1. Procedural generation (algorithmic art)
2. Style transfer and synthesis
3. Aesthetic evaluation
4. Emergent artistic patterns

Based on:
- Cohen, H. (1995). The further exploits of AARON, painter
- Machado, P., & Cardoso, A. (1998). Computing aesthetics
- Colton, S., et al. (2001). Automated theory formation in pure mathematics

Author: OmniMind Project
License: MIT
"""

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


class ArtStyle(Enum):
    """Artistic styles supported."""

    ABSTRACT = "abstract"
    GEOMETRIC = "geometric"
    ORGANIC = "organic"
    MINIMALIST = "minimalist"
    EXPRESSIONIST = "expressionist"
    SURREALIST = "surrealist"


class AestheticDimension(Enum):
    """Dimensions for aesthetic evaluation."""

    COMPLEXITY = "complexity"
    SYMMETRY = "symmetry"
    HARMONY = "harmony"
    CONTRAST = "contrast"
    NOVELTY = "novelty"
    COHERENCE = "coherence"


@dataclass
class ArtElement:
    """Basic element in an art piece."""

    element_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    element_type: str = "shape"  # shape, color, pattern, texture
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Tuple[float, float] = (0.0, 0.0)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArtPiece:
    """Generated art piece."""

    piece_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    style: ArtStyle = ArtStyle.ABSTRACT
    elements: List[ArtElement] = field(default_factory=list)
    aesthetic_scores: Dict[str, float] = field(default_factory=dict)
    generation_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AestheticEvaluator:
    """
    Evaluates aesthetic qualities of generated art.

    Uses computational aesthetics principles to assess
    various dimensions of artistic quality.
    """

    def __init__(self) -> None:
        """Initialize aesthetic evaluator."""
        self.evaluation_history: List[Tuple[str, Dict[str, float]]] = []
        self.logger = logger.bind(component="aesthetic_evaluator")

    def evaluate_complexity(self, art_piece: ArtPiece) -> float:
        """
        Evaluate complexity of art piece.

        Args:
            art_piece: Art piece to evaluate

        Returns:
            Complexity score (0.0-1.0)
        """
        num_elements = len(art_piece.elements)

        # Count unique element types
        unique_types = len(set(e.element_type for e in art_piece.elements))

        # Complexity based on number and diversity of elements
        base_complexity = min(num_elements / 20.0, 1.0)
        diversity_bonus = unique_types / 10.0

        complexity = min(base_complexity + diversity_bonus * 0.3, 1.0)

        return complexity

    def evaluate_symmetry(self, art_piece: ArtPiece) -> float:
        """
        Evaluate symmetry of art piece.

        Args:
            art_piece: Art piece to evaluate

        Returns:
            Symmetry score (0.0-1.0)
        """
        if not art_piece.elements:
            return 0.0

        # Simple heuristic: check position distribution
        positions = [e.position for e in art_piece.elements]

        # Check if positions are symmetric around center (0.5, 0.5)
        center = (0.5, 0.5)

        symmetry_score = 0.0
        for x, y in positions:
            # Distance from center
            ((x - center[0]) ** 2 + (y - center[1]) ** 2) ** 0.5

            # Check if there's a symmetric counterpart
            mirror_x = 2 * center[0] - x
            mirror_y = 2 * center[1] - y

            # Look for element near mirror position
            has_mirror = any(
                ((px - mirror_x) ** 2 + (py - mirror_y) ** 2) ** 0.5 < 0.1 for px, py in positions
            )

            if has_mirror:
                symmetry_score += 1.0

        # Normalize
        symmetry = symmetry_score / len(positions) if positions else 0.0

        return min(symmetry, 1.0)

    def evaluate_harmony(self, art_piece: ArtPiece) -> float:
        """
        Evaluate harmony (color, composition) of art piece.

        Args:
            art_piece: Art piece to evaluate

        Returns:
            Harmony score (0.0-1.0)
        """
        if not art_piece.elements:
            return 0.0

        # Extract colors if available
        colors = [
            e.properties.get("color", "") for e in art_piece.elements if "color" in e.properties
        ]

        if not colors:
            # No color info, use positional harmony
            return 0.5

        # Count color occurrences
        color_counts: Dict[str, int] = {}
        for color in colors:
            color_counts[color] = color_counts.get(color, 0) + 1

        # Harmony is higher when colors are balanced
        max_count = max(color_counts.values())
        min_count = min(color_counts.values())

        # Perfect balance: 1.0, complete imbalance: 0.0
        if max_count == 0:
            return 0.0

        harmony = 1.0 - (max_count - min_count) / max_count

        return harmony

    def evaluate_contrast(self, art_piece: ArtPiece) -> float:
        """
        Evaluate contrast in art piece.

        Args:
            art_piece: Art piece to evaluate

        Returns:
            Contrast score (0.0-1.0)
        """
        if len(art_piece.elements) < 2:
            return 0.0

        # Measure diversity of properties
        types = set(e.element_type for e in art_piece.elements)
        colors = set(
            e.properties.get("color", "") for e in art_piece.elements if "color" in e.properties
        )

        # More diversity = more contrast
        type_diversity = len(types) / max(len(art_piece.elements), 1)
        color_diversity = len(colors) / max(len(art_piece.elements), 1)

        contrast = (type_diversity + color_diversity) / 2.0

        return min(contrast, 1.0)

    def evaluate_novelty(self, art_piece: ArtPiece) -> float:
        """
        Evaluate novelty compared to previous works.

        Args:
            art_piece: Art piece to evaluate

        Returns:
            Novelty score (0.0-1.0)
        """
        if not self.evaluation_history:
            # First piece is novel
            return 1.0

        # Compare to previous pieces
        # Simple heuristic: different style or element count
        art_piece.style
        current_count = len(art_piece.elements)

        similar_count = sum(
            1
            for _, scores in self.evaluation_history
            if scores.get("element_count") == current_count
        )

        # More unique = more novel
        novelty = 1.0 - (similar_count / len(self.evaluation_history))

        return max(novelty, 0.0)

    def evaluate_coherence(self, art_piece: ArtPiece) -> float:
        """
        Evaluate coherence (consistency of theme/style).

        Args:
            art_piece: Art piece to evaluate

        Returns:
            Coherence score (0.0-1.0)
        """
        if not art_piece.elements:
            return 0.0

        # Elements should share similar properties for coherence
        # Count consistency of element types
        type_counts: Dict[str, int] = {}
        for elem in art_piece.elements:
            type_counts[elem.element_type] = type_counts.get(elem.element_type, 0) + 1

        # Higher coherence if dominated by few types
        if not type_counts:
            return 0.0

        max_count = max(type_counts.values())
        total = len(art_piece.elements)

        coherence = max_count / total if total > 0 else 0.0

        return coherence

    def evaluate(self, art_piece: ArtPiece) -> Dict[str, float]:
        """
        Comprehensive aesthetic evaluation.

        Args:
            art_piece: Art piece to evaluate

        Returns:
            Dictionary of aesthetic scores
        """
        scores = {
            "complexity": self.evaluate_complexity(art_piece),
            "symmetry": self.evaluate_symmetry(art_piece),
            "harmony": self.evaluate_harmony(art_piece),
            "contrast": self.evaluate_contrast(art_piece),
            "novelty": self.evaluate_novelty(art_piece),
            "coherence": self.evaluate_coherence(art_piece),
        }

        # Store element count for novelty evaluation
        scores["element_count"] = len(art_piece.elements)

        # Overall aesthetic score (weighted average)
        overall = (
            0.2 * scores["complexity"]
            + 0.15 * scores["symmetry"]
            + 0.2 * scores["harmony"]
            + 0.15 * scores["contrast"]
            + 0.15 * scores["novelty"]
            + 0.15 * scores["coherence"]
        )

        scores["overall"] = overall

        # Record in history
        self.evaluation_history.append((art_piece.piece_id, scores))

        self.logger.info(
            "aesthetic_evaluation_complete",
            piece_id=art_piece.piece_id,
            overall=overall,
        )

        return scores


class ProceduralGenerator:
    """
    Generates art procedurally using algorithms.

    Implements various procedural generation techniques
    for creating algorithmic art.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize procedural generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

        self.logger = logger.bind(component="procedural_generator")

    def generate_abstract(
        self,
        num_elements: int = 10,
        color_palette: Optional[List[str]] = None,
    ) -> ArtPiece:
        """
        Generate abstract art.

        Args:
            num_elements: Number of elements to generate
            color_palette: Optional color palette

        Returns:
            Generated abstract art piece
        """
        if color_palette is None:
            color_palette = ["red", "blue", "green", "yellow", "purple", "orange"]

        elements = []
        for i in range(num_elements):
            element = ArtElement(
                element_type=random.choice(["circle", "square", "triangle", "line"]),
                properties={
                    "color": random.choice(color_palette),
                    "size": random.uniform(0.05, 0.2),
                    "opacity": random.uniform(0.5, 1.0),
                },
                position=(random.random(), random.random()),
            )
            elements.append(element)

        piece = ArtPiece(
            title=f"Abstract Composition #{random.randint(1, 9999)}",
            description="Algorithmically generated abstract art",
            style=ArtStyle.ABSTRACT,
            elements=elements,
            generation_params={
                "num_elements": num_elements,
                "color_palette": color_palette,
            },
        )

        self.logger.info("abstract_art_generated", num_elements=num_elements)

        return piece

    def generate_geometric(
        self,
        num_elements: int = 15,
        enforce_symmetry: bool = True,
    ) -> ArtPiece:
        """
        Generate geometric art with regular shapes.

        Args:
            num_elements: Number of elements
            enforce_symmetry: Whether to enforce symmetry

        Returns:
            Generated geometric art piece
        """
        elements = []

        for i in range(num_elements):
            x, y = random.random(), random.random()

            element = ArtElement(
                element_type=random.choice(["square", "triangle", "hexagon", "circle"]),
                properties={
                    "color": random.choice(["black", "white", "gray"]),
                    "size": random.uniform(0.05, 0.15),
                },
                position=(x, y),
            )
            elements.append(element)

            if enforce_symmetry:
                # Create symmetric counterpart
                mirror = ArtElement(
                    element_type=element.element_type,
                    properties=element.properties.copy(),
                    position=(1.0 - x, 1.0 - y),  # Mirror around center
                )
                elements.append(mirror)

        piece = ArtPiece(
            title=f"Geometric Pattern #{random.randint(1, 9999)}",
            description="Symmetric geometric composition",
            style=ArtStyle.GEOMETRIC,
            elements=elements,
            generation_params={
                "num_elements": num_elements,
                "enforce_symmetry": enforce_symmetry,
            },
        )

        self.logger.info(
            "geometric_art_generated",
            num_elements=len(elements),
            symmetric=enforce_symmetry,
        )

        return piece

    def generate_organic(
        self,
        seed_points: int = 5,
        growth_iterations: int = 3,
    ) -> ArtPiece:
        """
        Generate organic art with growth patterns.

        Args:
            seed_points: Number of seed points
            growth_iterations: Number of growth iterations

        Returns:
            Generated organic art piece
        """
        elements = []

        # Create seed points
        seeds = [(random.random(), random.random()) for _ in range(seed_points)]

        for seed_x, seed_y in seeds:
            # Growth from each seed
            current_x, current_y = seed_x, seed_y

            for _ in range(growth_iterations):
                element = ArtElement(
                    element_type="organic_blob",
                    properties={
                        "color": random.choice(["green", "brown", "beige"]),
                        "size": random.uniform(0.03, 0.1),
                    },
                    position=(current_x, current_y),
                )
                elements.append(element)

                # Move to next position (organic growth)
                current_x += random.uniform(-0.1, 0.1)
                current_y += random.uniform(-0.1, 0.1)

                # Keep in bounds
                current_x = max(0.0, min(1.0, current_x))
                current_y = max(0.0, min(1.0, current_y))

        piece = ArtPiece(
            title=f"Organic Growth #{random.randint(1, 9999)}",
            description="Simulation of organic growth patterns",
            style=ArtStyle.ORGANIC,
            elements=elements,
            generation_params={
                "seed_points": seed_points,
                "growth_iterations": growth_iterations,
            },
        )

        self.logger.info(
            "organic_art_generated",
            seed_points=seed_points,
            iterations=growth_iterations,
        )

        return piece


class ArtGenerator:
    """
    Main art generation system.

    Orchestrates procedural generation with aesthetic evaluation
    to create high-quality generative art.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize art generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.generator = ProceduralGenerator(seed=seed)
        self.evaluator = AestheticEvaluator()
        self.gallery: List[ArtPiece] = []
        self.logger = logger.bind(component="art_generator")

        self.logger.info("art_generator_initialized")

    def generate_art(
        self,
        style: ArtStyle = ArtStyle.ABSTRACT,
        num_elements: Optional[int] = None,
        **kwargs: Any,
    ) -> ArtPiece:
        """
        Generate art piece in specified style.

        Args:
            style: Artistic style to use
            num_elements: Number of elements (style-dependent)
            **kwargs: Additional style-specific parameters

        Returns:
            Generated art piece with aesthetic evaluation
        """
        self.logger.info("generating_art", style=style.value)

        # Generate based on style
        if style == ArtStyle.ABSTRACT:
            piece = self.generator.generate_abstract(
                num_elements=num_elements or 10,
                color_palette=kwargs.get("color_palette"),
            )
        elif style == ArtStyle.GEOMETRIC:
            piece = self.generator.generate_geometric(
                num_elements=num_elements or 15,
                enforce_symmetry=kwargs.get("enforce_symmetry", True),
            )
        elif style == ArtStyle.ORGANIC:
            piece = self.generator.generate_organic(
                seed_points=num_elements or 5,
                growth_iterations=kwargs.get("growth_iterations", 3),
            )
        else:
            # Default to abstract
            piece = self.generator.generate_abstract(num_elements=num_elements or 10)

        # Evaluate aesthetics
        scores = self.evaluator.evaluate(piece)
        piece.aesthetic_scores = scores

        # Add to gallery
        self.gallery.append(piece)

        self.logger.info(
            "art_generated",
            piece_id=piece.piece_id,
            overall_score=scores.get("overall", 0.0),
        )

        return piece

    def generate_batch(
        self,
        num_pieces: int,
        style: ArtStyle = ArtStyle.ABSTRACT,
        **kwargs: Any,
    ) -> List[ArtPiece]:
        """
        Generate batch of art pieces.

        Args:
            num_pieces: Number of pieces to generate
            style: Artistic style
            **kwargs: Style-specific parameters

        Returns:
            List of generated art pieces
        """
        pieces = []
        for _ in range(num_pieces):
            piece = self.generate_art(style=style, **kwargs)
            pieces.append(piece)

        return pieces

    def get_best_pieces(self, n: int = 10) -> List[ArtPiece]:
        """
        Get best pieces from gallery by aesthetic score.

        Args:
            n: Number of pieces to return

        Returns:
            Top N art pieces
        """
        sorted_pieces = sorted(
            self.gallery,
            key=lambda p: p.aesthetic_scores.get("overall", 0.0),
            reverse=True,
        )

        return sorted_pieces[:n]

    def get_gallery_statistics(self) -> Dict[str, Any]:
        """Get statistics about the gallery."""
        if not self.gallery:
            return {
                "total_pieces": 0,
                "avg_overall_score": 0.0,
                "styles": {},
            }

        total = len(self.gallery)
        avg_score = sum(p.aesthetic_scores.get("overall", 0.0) for p in self.gallery) / total

        # Count by style
        style_counts: Dict[str, int] = {}
        for piece in self.gallery:
            style_name = piece.style.value
            style_counts[style_name] = style_counts.get(style_name, 0) + 1

        return {
            "total_pieces": total,
            "avg_overall_score": avg_score,
            "styles": style_counts,
            "avg_complexity": sum(p.aesthetic_scores.get("complexity", 0.0) for p in self.gallery)
            / total,
            "avg_harmony": sum(p.aesthetic_scores.get("harmony", 0.0) for p in self.gallery)
            / total,
        }
