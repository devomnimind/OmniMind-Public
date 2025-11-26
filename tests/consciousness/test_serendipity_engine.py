"""
Tests for Serendipity Engine - Unexpected Discovery System.

Author: OmniMind Project
License: MIT
"""

import pytest
from src.consciousness.serendipity_engine import (
    Connection,
    ConnectionDetector,
    Discovery,
    InsightGenerator,
    InsightType,
    SerendipityEngine,
    SerendipityType,
)


class TestConnection:
    """Test Connection dataclass."""

    def test_connection_creation(self) -> None:
        """Test basic connection creation."""
        connection = Connection(
            source_concept="AI",
            target_concept="Biology",
            connection_type="analogy",
            strength=0.8,
            surprise_value=0.6,
        )

        assert connection.source_concept == "AI"
        assert connection.target_concept == "Biology"
        assert connection.connection_type == "analogy"
        assert connection.strength == pytest.approx(0.8)
        assert connection.surprise_value == pytest.approx(0.6)

    def test_connection_default_values(self) -> None:
        """Test connection default values."""
        connection = Connection()

        assert isinstance(connection.connection_id, str)
        assert len(connection.connection_id) > 0
        assert connection.source_concept == ""
        assert connection.strength == pytest.approx(0.0)


class TestDiscovery:
    """Test Discovery dataclass."""

    def test_discovery_creation(self) -> None:
        """Test basic discovery creation."""
        discovery = Discovery(
            content="A surprising connection",
            serendipity_type=SerendipityType.WALTZIAN,
            insight_type=InsightType.ANALOGY,
            value_score=0.7,
            surprise_score=0.9,
        )

        assert discovery.content == "A surprising connection"
        assert discovery.serendipity_type == SerendipityType.WALTZIAN
        assert discovery.insight_type == InsightType.ANALOGY
        assert discovery.value_score == pytest.approx(0.7)
        assert discovery.surprise_score == pytest.approx(0.9)

    def test_discovery_default_values(self) -> None:
        """Test discovery default values."""
        discovery = Discovery()

        assert isinstance(discovery.discovery_id, str)
        assert len(discovery.discovery_id) > 0
        assert discovery.connections == []
        assert discovery.metadata == {}


class TestConnectionDetector:
    """Test ConnectionDetector functionality."""

    def test_detector_initialization(self) -> None:
        """Test detector initializes correctly."""
        detector = ConnectionDetector()

        assert len(detector.concept_network) == 0
        assert len(detector.connection_history) == 0

    def test_add_concept_simple(self) -> None:
        """Test adding a simple concept."""
        detector = ConnectionDetector()
        detector.add_concept("AI")

        assert "AI" in detector.concept_network
        assert len(detector.concept_network["AI"]) == 0

    def test_add_concept_with_relations(self) -> None:
        """Test adding a concept with relations."""
        detector = ConnectionDetector()
        detector.add_concept("AI", related_to=["ML", "DL"])

        assert "AI" in detector.concept_network
        assert "ML" in detector.concept_network["AI"]
        assert "DL" in detector.concept_network["AI"]
        # Bidirectional
        assert "AI" in detector.concept_network["ML"]
        assert "AI" in detector.concept_network["DL"]

    def test_find_connections_direct(self) -> None:
        """Test finding direct connections."""
        detector = ConnectionDetector()
        detector.add_concept("A", related_to=["B"])

        paths = detector.find_connections("A", "B")

        assert len(paths) >= 1
        assert ["A", "B"] in paths

    def test_find_connections_indirect(self) -> None:
        """Test finding indirect connections."""
        detector = ConnectionDetector()
        detector.add_concept("A", related_to=["B"])
        detector.add_concept("B", related_to=["C"])

        paths = detector.find_connections("A", "C")

        assert len(paths) >= 1
        # Should find path A -> B -> C
        assert any(len(path) == 3 for path in paths)

    def test_find_connections_no_path(self) -> None:
        """Test finding connections when no path exists."""
        detector = ConnectionDetector()
        detector.add_concept("A")
        detector.add_concept("B")

        paths = detector.find_connections("A", "B")

        assert len(paths) == 0

    def test_find_connections_max_length(self) -> None:
        """Test path length limit."""
        detector = ConnectionDetector()
        # Create long chain: A -> B -> C -> D
        detector.add_concept("A", related_to=["B"])
        detector.add_concept("B", related_to=["C"])
        detector.add_concept("C", related_to=["D"])

        # With max_path_length=2, should not find A -> D
        paths = detector.find_connections("A", "D", max_path_length=2)

        assert all(len(path) <= 2 for path in paths)

    def test_detect_emergent_connection_success(self) -> None:
        """Test detecting emergent connection."""
        detector = ConnectionDetector()
        detector.add_concept("quantum", related_to=["physics"])
        detector.add_concept("physics", related_to=["consciousness"])

        connection = detector.detect_emergent_connection("quantum", "consciousness")

        assert connection is not None
        assert connection.source_concept == "quantum"
        assert connection.target_concept == "consciousness"
        assert connection.strength > 0.0
        assert connection.surprise_value > 0.0

    def test_detect_emergent_connection_no_path(self) -> None:
        """Test detecting connection when none exists."""
        detector = ConnectionDetector()
        detector.add_concept("A")
        detector.add_concept("B")

        connection = detector.detect_emergent_connection("A", "B")

        assert connection is None

    def test_get_network_statistics_empty(self) -> None:
        """Test statistics on empty network."""
        detector = ConnectionDetector()

        stats = detector.get_network_statistics()

        assert stats["total_concepts"] == 0
        assert stats["total_connections"] == 0
        assert stats["avg_connections_per_concept"] == pytest.approx(0.0)

    def test_get_network_statistics_with_data(self) -> None:
        """Test statistics with network data."""
        detector = ConnectionDetector()
        detector.add_concept("A", related_to=["B", "C"])
        detector.add_concept("D", related_to=["E"])

        stats = detector.get_network_statistics()

        assert stats["total_concepts"] == 5  # A, B, C, D, E
        assert stats["total_connections"] >= 2  # At least A-B, A-C, D-E
        assert stats["avg_connections_per_concept"] > 0.0


class TestInsightGenerator:
    """Test InsightGenerator functionality."""

    def test_generator_initialization(self) -> None:
        """Test generator initializes correctly."""
        generator = InsightGenerator()

        assert len(generator.insights) == 0

    def test_generate_analogy(self) -> None:
        """Test generating analogy insight."""
        generator = InsightGenerator()

        connection = Connection(
            source_concept="neuron",
            target_concept="transistor",
            strength=0.7,
            surprise_value=0.5,
        )

        discovery = generator.generate_analogy("biology", "computing", connection)

        assert discovery.insight_type == InsightType.ANALOGY
        assert discovery.serendipity_type == SerendipityType.MERTONIAN
        assert "analogy" in discovery.content.lower()
        assert len(generator.insights) == 1

    def test_generate_synthesis(self) -> None:
        """Test generating synthesis insight."""
        generator = InsightGenerator()

        connections = [
            Connection(source_concept="A", target_concept="B", strength=0.8, surprise_value=0.6),
            Connection(source_concept="B", target_concept="C", strength=0.7, surprise_value=0.5),
        ]

        discovery = generator.generate_synthesis(["A", "B", "C"], connections)

        assert discovery.insight_type == InsightType.SYNTHESIS
        assert discovery.serendipity_type == SerendipityType.BUSHIAN
        assert "synthesis" in discovery.content.lower()
        assert discovery.value_score > 0.0
        assert len(generator.insights) == 1

    def test_generate_inversion(self) -> None:
        """Test generating inversion insight."""
        generator = InsightGenerator()

        discovery = generator.generate_inversion(
            "more is better",
            "less is better",
        )

        assert discovery.insight_type == InsightType.INVERSION
        assert discovery.serendipity_type == SerendipityType.STEPHANIAN
        assert "inversion" in discovery.content.lower()
        assert discovery.surprise_score > 0.5
        assert len(generator.insights) == 1

    def test_get_insights_by_type(self) -> None:
        """Test filtering insights by type."""
        generator = InsightGenerator()

        # Generate different types
        connection = Connection(
            source_concept="A", target_concept="B", strength=0.5, surprise_value=0.5
        )
        generator.generate_analogy("domain1", "domain2", connection)
        generator.generate_inversion("assumption1", "assumption2")

        analogies = generator.get_insights_by_type(InsightType.ANALOGY)
        inversions = generator.get_insights_by_type(InsightType.INVERSION)

        assert len(analogies) == 1
        assert len(inversions) == 1

    def test_get_top_insights(self) -> None:
        """Test getting top insights."""
        generator = InsightGenerator()

        # Generate multiple insights with different scores
        for i in range(5):
            connection = Connection(
                source_concept=f"A{i}",
                target_concept=f"B{i}",
                strength=0.5 + i * 0.1,
                surprise_value=0.5 + i * 0.05,
            )
            generator.generate_analogy("domain1", "domain2", connection)

        top_3 = generator.get_top_insights(n=3)

        assert len(top_3) == 3
        # Should be sorted by score (descending)
        scores = [d.value_score * 0.6 + d.surprise_score * 0.4 for d in top_3]
        assert scores == sorted(scores, reverse=True)


class TestSerendipityEngine:
    """Test SerendipityEngine main orchestrator."""

    def test_engine_initialization(self) -> None:
        """Test engine initializes correctly."""
        engine = SerendipityEngine()

        assert engine.detector is not None
        assert engine.generator is not None
        assert engine.enable_random_exploration is True

    def test_engine_initialization_no_random(self) -> None:
        """Test engine with random exploration disabled."""
        engine = SerendipityEngine(enable_random_exploration=False)

        assert engine.enable_random_exploration is False

    def test_add_knowledge(self) -> None:
        """Test adding knowledge to engine."""
        engine = SerendipityEngine()

        engine.add_knowledge("concept1", related_concepts=["concept2", "concept3"])

        stats = engine.get_discovery_statistics()
        assert stats["network"]["total_concepts"] == 3

    def test_explore_connections_success(self) -> None:
        """Test exploring connections successfully."""
        engine = SerendipityEngine()

        engine.add_knowledge("quantum", related_concepts=["physics"])
        engine.add_knowledge("physics", related_concepts=["reality"])

        discovery = engine.explore_connections("quantum", "reality")

        assert discovery is not None
        assert discovery.content

    def test_explore_connections_no_path(self) -> None:
        """Test exploring connections when no path exists."""
        engine = SerendipityEngine()

        engine.add_knowledge("A")
        engine.add_knowledge("B")

        discovery = engine.explore_connections("A", "B")

        assert discovery is None

    def test_facilitate_happy_accident(self) -> None:
        """Test facilitating happy accident."""
        engine = SerendipityEngine()

        discovery = engine.facilitate_happy_accident(
            original_goal="find cure for disease X",
            actual_result="discovered new adhesive material",
        )

        assert discovery is not None
        assert discovery.serendipity_type == SerendipityType.WALTZIAN
        assert discovery.surprise_score == pytest.approx(1.0)
        assert "while seeking" in discovery.content.lower()

    def test_cross_domain_transfer(self) -> None:
        """Test cross-domain concept transfer."""
        engine = SerendipityEngine()

        discovery = engine.cross_domain_transfer(
            source_domain="biology",
            target_domain="computing",
            concept_to_transfer="neural network",
        )

        assert discovery is not None
        assert discovery.insight_type == InsightType.ANALOGY
        assert "biology" in discovery.metadata["source_domain"]
        assert "computing" in discovery.metadata["target_domain"]

    def test_invert_assumption(self) -> None:
        """Test assumption inversion."""
        engine = SerendipityEngine()

        discovery = engine.invert_assumption("more data is always better")

        assert discovery is not None
        assert discovery.insight_type == InsightType.INVERSION
        assert "less" in discovery.content.lower() or "opposite" in discovery.content.lower()

    def test_random_exploration_disabled(self) -> None:
        """Test that random exploration can be disabled."""
        engine = SerendipityEngine(enable_random_exploration=False)

        # Add some concepts
        engine.add_knowledge("A", related_concepts=["B"])
        engine.add_knowledge("C", related_concepts=["D"])

        result = engine.random_exploration()

        assert result is None  # Should return None when disabled

    def test_random_exploration_insufficient_concepts(self) -> None:
        """Test random exploration with insufficient concepts."""
        engine = SerendipityEngine()

        # Only one concept
        engine.add_knowledge("A")

        result = engine.random_exploration()

        assert result is None

    def test_get_discovery_statistics_empty(self) -> None:
        """Test statistics with no discoveries."""
        engine = SerendipityEngine()

        stats = engine.get_discovery_statistics()

        assert stats["total_discoveries"] == 0
        assert stats["avg_surprise"] == pytest.approx(0.0)
        assert stats["avg_value"] == pytest.approx(0.0)

    def test_get_discovery_statistics_with_data(self) -> None:
        """Test statistics with discoveries."""
        engine = SerendipityEngine()

        # Make some discoveries
        engine.facilitate_happy_accident("goal1", "result1")
        engine.invert_assumption("assumption1")

        stats = engine.get_discovery_statistics()

        assert stats["total_discoveries"] == 2
        assert stats["avg_surprise"] > 0.0
        assert stats["avg_value"] > 0.0
        assert len(stats["serendipity_types"]) > 0
        assert len(stats["insight_types"]) > 0

    def test_get_top_discoveries(self) -> None:
        """Test getting top discoveries."""
        engine = SerendipityEngine()

        # Create multiple discoveries
        for i in range(5):
            engine.facilitate_happy_accident(f"goal{i}", f"result{i}")

        top_3 = engine.get_top_discoveries(n=3)

        assert len(top_3) == 3
        assert all(isinstance(d, Discovery) for d in top_3)


class TestIntegration:
    """Integration tests for the complete serendipity system."""

    def test_end_to_end_discovery_pipeline(self) -> None:
        """Test complete discovery pipeline."""
        engine = SerendipityEngine()

        # Build knowledge network
        engine.add_knowledge("consciousness", related_concepts=["awareness", "experience"])
        engine.add_knowledge("awareness", related_concepts=["perception", "cognition"])
        engine.add_knowledge("quantum", related_concepts=["superposition", "entanglement"])
        engine.add_knowledge("superposition", related_concepts=["states", "measurement"])

        # Explore connections
        discovery1 = engine.explore_connections("consciousness", "cognition")
        discovery2 = engine.explore_connections("quantum", "measurement")

        # Should find at least one connection
        assert discovery1 is not None or discovery2 is not None

        # Cross-domain transfer
        discovery3 = engine.cross_domain_transfer(
            "quantum_physics",
            "consciousness_studies",
            "superposition",
        )

        assert discovery3 is not None

        # Check statistics
        stats = engine.get_discovery_statistics()
        assert stats["total_discoveries"] >= 1
        assert stats["network"]["total_concepts"] >= 4

    def test_multiple_serendipity_types(self) -> None:
        """Test that different serendipity types can be generated."""
        engine = SerendipityEngine()

        # Waltzian: happy accident
        d1 = engine.facilitate_happy_accident("find X", "found Y")

        # Stephanian: inversion
        d2 = engine.invert_assumption("assumption")

        # Mertonian/Bushian: exploration
        engine.add_knowledge("A", related_concepts=["B"])
        engine.add_knowledge("B", related_concepts=["C"])
        d3 = engine.explore_connections("A", "C")

        discoveries = [d for d in [d1, d2, d3] if d is not None]

        # Should have discoveries of different types
        serendipity_types = {d.serendipity_type for d in discoveries}
        assert len(serendipity_types) >= 2

    def test_knowledge_accumulation(self) -> None:
        """Test that knowledge accumulates over time."""
        engine = SerendipityEngine()

        initial_stats = engine.get_discovery_statistics()
        initial_concepts = initial_stats["network"]["total_concepts"]

        # Add knowledge progressively
        for i in range(10):
            engine.add_knowledge(f"concept_{i}", related_concepts=[f"related_{i}"])

        final_stats = engine.get_discovery_statistics()
        final_concepts = final_stats["network"]["total_concepts"]

        # Should have more concepts
        assert final_concepts > initial_concepts
        assert final_concepts >= 20  # 10 concepts + 10 related

    def test_surprise_value_varies(self) -> None:
        """Test that surprise values vary based on connection distance."""
        engine = SerendipityEngine()

        # Create short and long paths
        engine.add_knowledge("A", related_concepts=["B"])  # Distance 1
        engine.add_knowledge("X", related_concepts=["Y"])
        engine.add_knowledge("Y", related_concepts=["Z"])
        engine.add_knowledge("Z", related_concepts=["W"])  # Distance 3+

        conn_short = engine.detector.detect_emergent_connection("A", "B")
        conn_long = engine.detector.detect_emergent_connection("X", "W")

        if conn_short and conn_long:
            # Longer path should have higher surprise
            assert conn_long.surprise_value > conn_short.surprise_value
