"""
Tests for IIT refactoring with unconscious preservation.

Tests that the PhiCalculator correctly identifies MICS and preserves
the machinic unconscious.
"""

import pytest

torch = pytest.importorskip("torch")

from src.consciousness.topological_phi import (
    IITResult,
    PhiCalculator,
    SimplicialComplex,
)


class TestIITResult:
    """Test IITResult data structure."""

    def test_initialization(self):
        """Test basic initialization."""
        result = IITResult()

        assert result.conscious_phi == 0.0
        assert isinstance(result.conscious_complex, set)
        assert isinstance(result.machinic_unconscious, list)

    def test_initialization_with_values(self):
        """Test initialization with values."""
        result = IITResult(
            conscious_phi=0.5,
            conscious_complex={1, 2, 3},
            machinic_unconscious=[{"subsystem_nodes": {4, 5}, "phi_value": 0.2}],
        )

        assert result.conscious_phi == 0.5
        assert result.conscious_complex == {1, 2, 3}
        assert len(result.machinic_unconscious) == 1

    def test_total_phi(self):
        """Test total phi calculation."""
        result = IITResult(
            conscious_phi=0.5,
            machinic_unconscious=[
                {"phi_value": 0.2},
                {"phi_value": 0.1},
            ],
        )

        total = result.total_phi()
        assert total == 0.8  # 0.5 + 0.2 + 0.1

    def test_unconscious_ratio(self):
        """Test unconscious ratio calculation."""
        result = IITResult(
            conscious_phi=0.2,
            machinic_unconscious=[
                {"phi_value": 0.8},
            ],
        )

        ratio = result.unconscious_ratio()
        # 0.8 / (0.2 + 0.8) = 0.8
        assert abs(ratio - 0.8) < 0.01

    def test_unconscious_ratio_zero_total(self):
        """Test unconscious ratio with zero total phi."""
        result = IITResult()

        ratio = result.unconscious_ratio()
        assert ratio == 0.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = IITResult(
            conscious_phi=0.5,
            conscious_complex={1, 2},
            machinic_unconscious=[{"phi_value": 0.2}],
        )

        d = result.to_dict()

        assert "conscious_phi" in d
        assert "conscious_complex" in d
        assert "machinic_unconscious" in d
        assert "total_phi" in d
        assert "unconscious_ratio" in d


class TestPhiCalculatorWithUnconscious:
    """Test PhiCalculator with unconscious preservation."""

    def test_calculate_phi_backward_compatibility(self):
        """Test that calculate_phi still works (backward compatibility)."""
        complex = SimplicialComplex()
        complex.add_simplex((0,))
        complex.add_simplex((1,))
        complex.add_simplex((0, 1))

        calculator = PhiCalculator(complex)
        phi = calculator.calculate_phi()

        assert isinstance(phi, float)
        assert 0.0 <= phi <= 1.0

    def test_calculate_phi_with_unconscious_empty(self):
        """Test with empty complex."""
        complex = SimplicialComplex()
        calculator = PhiCalculator(complex)

        result = calculator.calculate_phi_with_unconscious()

        assert result.conscious_phi == 0.0
        assert len(result.conscious_complex) == 0
        assert len(result.machinic_unconscious) == 0

    def test_calculate_phi_with_unconscious_single_vertex(self):
        """Test with single vertex."""
        complex = SimplicialComplex()
        complex.add_simplex((0,))

        calculator = PhiCalculator(complex)
        result = calculator.calculate_phi_with_unconscious()

        # Single vertex has no integration
        assert result.conscious_phi == 0.0

    def test_calculate_phi_with_unconscious_simple_graph(self):
        """Test with simple connected graph."""
        complex = SimplicialComplex()
        # Add vertices
        complex.add_simplex((0,))
        complex.add_simplex((1,))
        complex.add_simplex((2,))
        complex.add_simplex((3,))

        # Add edges (connected graph)
        complex.add_simplex((0, 1))
        complex.add_simplex((1, 2))
        complex.add_simplex((2, 3))

        calculator = PhiCalculator(complex, noise_threshold=0.01)
        result = calculator.calculate_phi_with_unconscious()

        # Should have some integration
        assert result.conscious_phi > 0.0
        assert len(result.conscious_complex) > 0

        # May or may not have unconscious subsystems depending on structure
        assert isinstance(result.machinic_unconscious, list)

    def test_noise_threshold_filtering(self):
        """Test that noise threshold filters out low-phi subsystems."""
        complex = SimplicialComplex()
        for i in range(6):
            complex.add_simplex((i,))
        # Add some edges
        complex.add_simplex((0, 1))
        complex.add_simplex((2, 3))
        complex.add_simplex((4, 5))

        # High threshold - should filter out most unconscious
        calculator_high = PhiCalculator(complex, noise_threshold=0.5)
        result_high = calculator_high.calculate_phi_with_unconscious()

        # Low threshold - should keep more unconscious
        calculator_low = PhiCalculator(complex, noise_threshold=0.01)
        result_low = calculator_low.calculate_phi_with_unconscious()

        # Low threshold should have more or equal unconscious subsystems
        assert len(result_low.machinic_unconscious) >= len(result_high.machinic_unconscious)

    def test_mics_is_maximum(self):
        """Test that MICS (conscious) has maximum phi among all candidates."""
        complex = SimplicialComplex()
        # Create a richer complex
        for i in range(8):
            complex.add_simplex((i,))
        # Add various edges
        for i in range(7):
            complex.add_simplex((i, i + 1))

        calculator = PhiCalculator(complex, noise_threshold=0.01)
        result = calculator.calculate_phi_with_unconscious()

        # Conscious phi should be >= all unconscious phis
        for unconscious in result.machinic_unconscious:
            assert result.conscious_phi >= unconscious["phi_value"]

    def test_iit_result_structure(self):
        """Test that IITResult has expected structure."""
        complex = SimplicialComplex()
        for i in range(4):
            complex.add_simplex((i,))
        complex.add_simplex((0, 1))
        complex.add_simplex((2, 3))

        calculator = PhiCalculator(complex, noise_threshold=0.01)
        result = calculator.calculate_phi_with_unconscious()

        # Verify structure
        assert hasattr(result, "conscious_phi")
        assert hasattr(result, "conscious_complex")
        assert hasattr(result, "machinic_unconscious")

        # Verify types
        assert isinstance(result.conscious_phi, float)
        assert isinstance(result.conscious_complex, set)
        assert isinstance(result.machinic_unconscious, list)

        # Verify unconscious items have required fields
        for unconscious in result.machinic_unconscious:
            assert "subsystem_nodes" in unconscious
            assert "phi_value" in unconscious


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
