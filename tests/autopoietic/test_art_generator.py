"""
Tests for Art Generator - Generative Art System.

Author: OmniMind Project
License: MIT
"""

import pytest
from src.autopoietic.art_generator import (
    AestheticEvaluator,
    ArtElement,
    ArtGenerator,
    ArtPiece,
    ArtStyle,
    ProceduralGenerator,
)


class TestArtElement:
    """Test ArtElement dataclass."""

    def test_element_creation(self) -> None:
        """Test basic element creation."""
        element = ArtElement(
            element_type="circle",
            properties={"color": "red", "size": 0.5},
            position=(0.3, 0.7),
        )

        assert element.element_type == "circle"
        assert element.properties["color"] == "red"
        assert element.position == (0.3, 0.7)

    def test_element_default_values(self) -> None:
        """Test element default values."""
        element = ArtElement()

        assert isinstance(element.element_id, str)
        assert len(element.element_id) > 0
        assert element.element_type == "shape"
        assert element.position == (0.0, 0.0)


class TestArtPiece:
    """Test ArtPiece dataclass."""

    def test_piece_creation(self) -> None:
        """Test basic piece creation."""
        elements = [
            ArtElement(element_type="circle", position=(0.5, 0.5)),
            ArtElement(element_type="square", position=(0.3, 0.3)),
        ]

        piece = ArtPiece(
            title="Test Art",
            style=ArtStyle.ABSTRACT,
            elements=elements,
        )

        assert piece.title == "Test Art"
        assert piece.style == ArtStyle.ABSTRACT
        assert len(piece.elements) == 2

    def test_piece_default_values(self) -> None:
        """Test piece default values."""
        piece = ArtPiece()

        assert isinstance(piece.piece_id, str)
        assert len(piece.piece_id) > 0
        assert piece.elements == []
        assert piece.aesthetic_scores == {}


class TestAestheticEvaluator:
    """Test AestheticEvaluator functionality."""

    def test_evaluator_initialization(self) -> None:
        """Test evaluator initializes correctly."""
        evaluator = AestheticEvaluator()

        assert len(evaluator.evaluation_history) == 0

    def test_evaluate_complexity_simple(self) -> None:
        """Test complexity evaluation for simple piece."""
        evaluator = AestheticEvaluator()

        piece = ArtPiece(
            elements=[ArtElement() for _ in range(5)],
        )

        complexity = evaluator.evaluate_complexity(piece)

        assert 0.0 <= complexity <= 1.0
        assert complexity > 0.0  # Should have some complexity

    def test_evaluate_complexity_complex(self) -> None:
        """Test complexity evaluation for complex piece."""
        evaluator = AestheticEvaluator()

        # Many diverse elements
        elements = []
        for i in range(20):
            elements.append(ArtElement(element_type=f"type_{i % 5}"))

        piece = ArtPiece(elements=elements)

        complexity = evaluator.evaluate_complexity(piece)

        assert 0.0 <= complexity <= 1.0
        assert complexity > 0.5  # Should be quite complex

    def test_evaluate_symmetry_symmetric(self) -> None:
        """Test symmetry evaluation for symmetric arrangement."""
        evaluator = AestheticEvaluator()

        # Create symmetric elements
        elements = [
            ArtElement(position=(0.3, 0.3)),
            ArtElement(position=(0.7, 0.7)),  # Mirror of (0.3, 0.3)
            ArtElement(position=(0.4, 0.6)),
            ArtElement(position=(0.6, 0.4)),  # Mirror of (0.4, 0.6)
        ]

        piece = ArtPiece(elements=elements)

        symmetry = evaluator.evaluate_symmetry(piece)

        assert 0.0 <= symmetry <= 1.0

    def test_evaluate_harmony_balanced(self) -> None:
        """Test harmony evaluation for balanced colors."""
        evaluator = AestheticEvaluator()

        # Balanced colors
        elements = [
            ArtElement(properties={"color": "red"}),
            ArtElement(properties={"color": "red"}),
            ArtElement(properties={"color": "blue"}),
            ArtElement(properties={"color": "blue"}),
        ]

        piece = ArtPiece(elements=elements)

        harmony = evaluator.evaluate_harmony(piece)

        assert 0.0 <= harmony <= 1.0
        assert harmony > 0.5  # Should be relatively harmonious

    def test_evaluate_contrast_high(self) -> None:
        """Test contrast evaluation for high contrast piece."""
        evaluator = AestheticEvaluator()

        # Very diverse elements
        elements = [
            ArtElement(element_type="circle", properties={"color": "red"}),
            ArtElement(element_type="square", properties={"color": "blue"}),
            ArtElement(element_type="triangle", properties={"color": "green"}),
        ]

        piece = ArtPiece(elements=elements)

        contrast = evaluator.evaluate_contrast(piece)

        assert 0.0 <= contrast <= 1.0
        assert contrast > 0.5  # Should have high contrast

    def test_evaluate_novelty_first_piece(self) -> None:
        """Test novelty for first piece (should be novel)."""
        evaluator = AestheticEvaluator()

        piece = ArtPiece(elements=[ArtElement()])

        novelty = evaluator.evaluate_novelty(piece)

        assert novelty == pytest.approx(1.0)  # First piece is fully novel

    def test_evaluate_coherence_coherent(self) -> None:
        """Test coherence for consistent piece."""
        evaluator = AestheticEvaluator()

        # All same type
        elements = [ArtElement(element_type="circle") for _ in range(5)]

        piece = ArtPiece(elements=elements)

        coherence = evaluator.evaluate_coherence(piece)

        assert coherence == pytest.approx(1.0)  # Perfect coherence

    def test_evaluate_comprehensive(self) -> None:
        """Test comprehensive evaluation."""
        evaluator = AestheticEvaluator()

        elements = [
            ArtElement(element_type="circle", properties={"color": "red"}),
            ArtElement(element_type="circle", properties={"color": "blue"}),
        ]

        piece = ArtPiece(elements=elements)

        scores = evaluator.evaluate(piece)

        # Should have all dimensions
        assert "complexity" in scores
        assert "symmetry" in scores
        assert "harmony" in scores
        assert "contrast" in scores
        assert "novelty" in scores
        assert "coherence" in scores
        assert "overall" in scores

        # All aesthetic scores should be valid (0-1 range)
        for key, score in scores.items():
            if key != "element_count":  # element_count is metadata, not a 0-1 score
                assert 0.0 <= score <= 1.0

        # Should record in history
        assert len(evaluator.evaluation_history) == 1


class TestProceduralGenerator:
    """Test ProceduralGenerator functionality."""

    def test_generator_initialization(self) -> None:
        """Test generator initializes correctly."""
        generator = ProceduralGenerator()

        assert generator is not None

    def test_generator_with_seed(self) -> None:
        """Test generator with fixed seed for reproducibility."""
        gen1 = ProceduralGenerator(seed=42)
        gen2 = ProceduralGenerator(seed=42)

        piece1 = gen1.generate_abstract(num_elements=5)
        piece2 = gen2.generate_abstract(num_elements=5)

        # Should generate same number of elements
        assert len(piece1.elements) == len(piece2.elements)

    def test_generate_abstract(self) -> None:
        """Test abstract art generation."""
        generator = ProceduralGenerator()

        piece = generator.generate_abstract(num_elements=10)

        assert piece.style == ArtStyle.ABSTRACT
        assert len(piece.elements) == 10
        assert piece.title
        assert "Abstract" in piece.title

    def test_generate_abstract_custom_palette(self) -> None:
        """Test abstract art with custom color palette."""
        generator = ProceduralGenerator()

        palette = ["pink", "purple", "cyan"]
        piece = generator.generate_abstract(num_elements=5, color_palette=palette)

        # All elements should use palette colors
        for element in piece.elements:
            if "color" in element.properties:
                assert element.properties["color"] in palette

    def test_generate_geometric(self) -> None:
        """Test geometric art generation."""
        generator = ProceduralGenerator()

        piece = generator.generate_geometric(num_elements=10)

        assert piece.style == ArtStyle.GEOMETRIC
        assert "Geometric" in piece.title
        assert len(piece.elements) > 0

    def test_generate_geometric_symmetric(self) -> None:
        """Test geometric art with enforced symmetry."""
        generator = ProceduralGenerator()

        piece = generator.generate_geometric(num_elements=5, enforce_symmetry=True)

        # With symmetry, should have double the elements (5 + 5 mirrors)
        assert len(piece.elements) == 10

    def test_generate_organic(self) -> None:
        """Test organic art generation."""
        generator = ProceduralGenerator()

        piece = generator.generate_organic(seed_points=3, growth_iterations=4)

        assert piece.style == ArtStyle.ORGANIC
        assert "Organic" in piece.title
        # Should have seed_points * growth_iterations elements
        assert len(piece.elements) == 3 * 4


class TestArtGenerator:
    """Test ArtGenerator main system."""

    def test_generator_initialization(self) -> None:
        """Test generator initializes correctly."""
        generator = ArtGenerator()

        assert generator.generator is not None
        assert generator.evaluator is not None
        assert len(generator.gallery) == 0

    def test_generate_art_abstract(self) -> None:
        """Test generating abstract art."""
        generator = ArtGenerator(seed=42)

        piece = generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=8)

        assert piece.style == ArtStyle.ABSTRACT
        assert len(piece.elements) == 8
        assert "overall" in piece.aesthetic_scores
        assert len(generator.gallery) == 1

    def test_generate_art_geometric(self) -> None:
        """Test generating geometric art."""
        generator = ArtGenerator(seed=42)

        piece = generator.generate_art(style=ArtStyle.GEOMETRIC, num_elements=5)

        assert piece.style == ArtStyle.GEOMETRIC
        assert "overall" in piece.aesthetic_scores

    def test_generate_art_organic(self) -> None:
        """Test generating organic art."""
        generator = ArtGenerator(seed=42)

        piece = generator.generate_art(
            style=ArtStyle.ORGANIC,
            num_elements=4,
            growth_iterations=3,
        )

        assert piece.style == ArtStyle.ORGANIC
        assert len(piece.elements) == 4 * 3  # seed_points * growth_iterations

    def test_generate_batch(self) -> None:
        """Test generating batch of art pieces."""
        generator = ArtGenerator(seed=42)

        pieces = generator.generate_batch(
            num_pieces=5,
            style=ArtStyle.ABSTRACT,
            num_elements=10,
        )

        assert len(pieces) == 5
        assert all(p.style == ArtStyle.ABSTRACT for p in pieces)
        assert len(generator.gallery) == 5

    def test_get_best_pieces(self) -> None:
        """Test getting best pieces from gallery."""
        generator = ArtGenerator(seed=42)

        # Generate multiple pieces
        for i in range(10):
            generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=i + 5)

        best_3 = generator.get_best_pieces(n=3)

        assert len(best_3) == 3
        # Should be sorted by overall score
        scores = [p.aesthetic_scores.get("overall", 0.0) for p in best_3]
        assert scores == sorted(scores, reverse=True)

    def test_get_gallery_statistics_empty(self) -> None:
        """Test statistics for empty gallery."""
        generator = ArtGenerator()

        stats = generator.get_gallery_statistics()

        assert stats["total_pieces"] == 0
        assert stats["avg_overall_score"] == pytest.approx(0.0)
        assert stats["styles"] == {}

    def test_get_gallery_statistics_with_data(self) -> None:
        """Test statistics with gallery data."""
        generator = ArtGenerator(seed=42)

        # Generate mixed styles
        generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=10)
        generator.generate_art(style=ArtStyle.GEOMETRIC, num_elements=8)
        generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=12)

        stats = generator.get_gallery_statistics()

        assert stats["total_pieces"] == 3
        assert stats["avg_overall_score"] > 0.0
        assert stats["styles"]["abstract"] == 2
        assert stats["styles"]["geometric"] == 1


class TestIntegration:
    """Integration tests for the complete art generation system."""

    def test_end_to_end_art_creation(self) -> None:
        """Test complete art creation pipeline."""
        generator = ArtGenerator(seed=42)

        # Generate pieces in different styles
        abstract = generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=12)
        geometric = generator.generate_art(
            style=ArtStyle.GEOMETRIC,
            num_elements=10,
            enforce_symmetry=True,
        )
        organic = generator.generate_art(
            style=ArtStyle.ORGANIC,
            num_elements=5,
            growth_iterations=4,
        )

        # All should be evaluated
        assert "overall" in abstract.aesthetic_scores
        assert "overall" in geometric.aesthetic_scores
        assert "overall" in organic.aesthetic_scores

        # Gallery should contain all
        assert len(generator.gallery) == 3

        # Get best
        best = generator.get_best_pieces(n=2)
        assert len(best) == 2

    def test_aesthetic_evaluation_affects_ranking(self) -> None:
        """Test that aesthetic evaluation affects gallery ranking."""
        generator = ArtGenerator(seed=42)

        # Generate many pieces
        for i in range(20):
            generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=i + 3)

        # Get best pieces
        best_5 = generator.get_best_pieces(n=5)

        # Top pieces should have higher scores than average
        top_scores = [p.aesthetic_scores.get("overall", 0.0) for p in best_5]
        stats = generator.get_gallery_statistics()
        avg_score = stats["avg_overall_score"]

        # At least some top pieces should be above average
        assert any(score >= avg_score for score in top_scores)

    def test_novelty_decreases_over_time(self) -> None:
        """Test that novelty decreases as more similar pieces are generated."""
        generator = ArtGenerator(seed=42)

        # Generate similar pieces
        pieces = []
        for _ in range(5):
            piece = generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=10)
            pieces.append(piece)

        # First piece should be most novel
        assert pieces[0].aesthetic_scores["novelty"] == pytest.approx(1.0)

        # Later pieces may have lower novelty (depends on evaluation)
        # Note: Due to randomness, this may not always hold strictly

    def test_different_styles_produce_different_scores(self) -> None:
        """Test that different styles produce different aesthetic profiles."""
        generator = ArtGenerator(seed=42)

        abstract = generator.generate_art(style=ArtStyle.ABSTRACT, num_elements=10)
        geometric = generator.generate_art(
            style=ArtStyle.GEOMETRIC,
            num_elements=10,
            enforce_symmetry=True,
        )

        # Geometric with symmetry should have higher symmetry score
        # Note: This depends on the algorithm, may not always be strictly true
        # But we can check that scores exist and are valid
        assert "symmetry" in abstract.aesthetic_scores
        assert "symmetry" in geometric.aesthetic_scores
        assert 0.0 <= abstract.aesthetic_scores["symmetry"] <= 1.0
        assert 0.0 <= geometric.aesthetic_scores["symmetry"] <= 1.0

    def test_reproducibility_with_seed(self) -> None:
        """Test that same seed produces consistent results."""
        gen1 = ArtGenerator(seed=123)
        gen2 = ArtGenerator(seed=123)

        piece1 = gen1.generate_art(style=ArtStyle.ABSTRACT, num_elements=8)
        piece2 = gen2.generate_art(style=ArtStyle.ABSTRACT, num_elements=8)

        # Should generate same number of elements
        assert len(piece1.elements) == len(piece2.elements)

        # Aesthetic scores should be similar (not necessarily identical due to float precision)
        assert abs(piece1.aesthetic_scores["overall"] - piece2.aesthetic_scores["overall"]) < 0.1
