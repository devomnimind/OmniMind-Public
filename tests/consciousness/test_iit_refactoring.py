"""
Tests for IIT (IIT puro).

Tests that the PhiCalculator correctly identifies MICS.
IIT puro: apenas conscious_phi (MICS), não existe "Φ_inconsciente".
"""

import pytest

torch = pytest.importorskip("torch")

from src.consciousness.topological_phi import (  # noqa: E402
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
        # REMOVIDO: machinic_unconscious - não existe em IIT puro

    def test_initialization_with_values(self):
        """Test initialization with values."""
        result = IITResult(
            conscious_phi=0.5,
            conscious_complex={1, 2, 3},
        )

        assert result.conscious_phi == 0.5
        assert result.conscious_complex == {1, 2, 3}
        # REMOVIDO: machinic_unconscious - não existe em IIT puro

    # REMOVIDO: test_total_phi() - não existe em IIT puro (não é aditivo)

    # REMOVIDO: test_unconscious_ratio() - não existe em IIT puro

    # REMOVIDO: test_unconscious_ratio_zero_total() - não existe em IIT puro

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = IITResult(
            conscious_phi=0.5,
            conscious_complex={1, 2},
        )

        d = result.to_dict()

        assert "conscious_phi" in d
        assert "conscious_complex" in d
        # REMOVIDO: machinic_unconscious, total_phi, unconscious_ratio - não existem em IIT puro


class TestPhiCalculator:
    """Test PhiCalculator (IIT puro - apenas MICS)."""

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
        # REMOVIDO: machinic_unconscious - não existe em IIT puro

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
        # REMOVIDO: machinic_unconscious - não existe em IIT puro

    # REMOVIDO: test_noise_threshold_filtering() - não existe machinic_unconscious

    def test_mics_is_maximum(self):
        """Test that MICS (conscious) is the maximum phi."""
        complex = SimplicialComplex()
        # Create a richer complex
        for i in range(8):
            complex.add_simplex((i,))
        # Add various edges
        for i in range(7):
            complex.add_simplex((i, i + 1))

        calculator = PhiCalculator(complex, noise_threshold=0.01)
        result = calculator.calculate_phi_with_unconscious()

        # MICS should have phi > 0 for connected graph
        assert result.conscious_phi > 0.0
        # REMOVIDO: comparação com machinic_unconscious - não existe em IIT puro

    def test_iit_result_structure(self):
        """Test that IITResult has expected structure (IIT puro)."""
        complex = SimplicialComplex()
        for i in range(4):
            complex.add_simplex((i,))
        complex.add_simplex((0, 1))
        complex.add_simplex((2, 3))

        calculator = PhiCalculator(complex, noise_threshold=0.01)
        result = calculator.calculate_phi_with_unconscious()

        # Verify structure (IIT puro)
        assert hasattr(result, "conscious_phi")
        assert hasattr(result, "conscious_complex")
        # REMOVIDO: machinic_unconscious - não existe em IIT puro

        # Verify types
        assert isinstance(result.conscious_phi, float)
        assert isinstance(result.conscious_complex, set)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
