"""
Tests for biological metrics module.

Tests Lempel-Ziv Complexity and Phase Lag Index implementations.
"""

import pytest

# Skip if numpy not available
np = pytest.importorskip("numpy")

from src.consciousness.biological_metrics import (  # noqa: E402
    BiologicalMetricsAnalyzer,
    LempelZivComplexity,
    PhaseLagIndex,
)


class TestLempelZivComplexity:
    """Test Lempel-Ziv Complexity calculations."""

    def test_binarize_signal(self):
        """Test signal binarization."""
        signal = np.array([1, 2, 3, 4, 5])  # Mean = 3
        binary = LempelZivComplexity.binarize_signal(signal)

        # Values >= 3 should be '1', < 3 should be '0'
        # [1 < 3 → 0, 2 < 3 → 0, 3 >= 3 → 1, 4 >= 3 → 1, 5 >= 3 → 1]
        assert binary == "00111"

    def test_binarize_with_custom_threshold(self):
        """Test binarization with custom threshold."""
        signal = np.array([1, 2, 3, 4, 5])
        binary = LempelZivComplexity.binarize_signal(signal, threshold=2.5)

        # Values >= 2.5 should be '1'
        assert binary == "00111"

    def test_calculate_complexity_simple(self):
        """Test LZ complexity on simple sequence."""
        binary_seq = "010101"
        result = LempelZivComplexity.calculate_complexity(binary_seq)

        assert 0.0 <= result.complexity <= 1.0
        assert result.unique_patterns > 0
        assert result.signal_length == 6
        assert result.binary_sequence == "010101"

    def test_calculate_complexity_empty(self):
        """Test LZ complexity on empty sequence."""
        result = LempelZivComplexity.calculate_complexity("")

        assert result.complexity == 0.0
        assert result.unique_patterns == 0
        assert result.signal_length == 0

    def test_from_signal(self):
        """Test LZ complexity calculated directly from signal."""
        signal = np.random.rand(100)
        result = LempelZivComplexity.from_signal(signal)

        assert 0.0 <= result.complexity <= 1.0
        assert result.unique_patterns > 0
        assert result.signal_length == 100

    def test_high_vs_low_complexity(self):
        """Test that random signal has higher complexity than repetitive."""
        # Repetitive signal (low complexity)
        repetitive = np.array([1, 2, 1, 2, 1, 2, 1, 2] * 10)
        result_rep = LempelZivComplexity.from_signal(repetitive)

        # Random signal (high complexity)
        random = np.random.rand(80)
        result_rand = LempelZivComplexity.from_signal(random)

        # Random should have higher or equal complexity
        assert result_rand.complexity >= result_rep.complexity


class TestPhaseLagIndex:
    """Test Phase Lag Index calculations."""

    def test_calculate_pli_perfect_sync(self):
        """Test PLI for perfectly synchronized signals."""
        # Same phase difference throughout
        phase_diff = np.ones(100) * 0.5  # All positive
        pli = PhaseLagIndex.calculate_pli(phase_diff)

        # Should be close to 1 (perfect phase lock)
        assert 0.9 <= pli <= 1.0

    def test_calculate_pli_no_sync(self):
        """Test PLI for unsynchronized signals."""
        # Random phase differences
        np.random.seed(42)
        phase_diff = np.random.randn(100) * 2 * np.pi
        pli = PhaseLagIndex.calculate_pli(phase_diff)

        # Should be close to 0 (no consistent phase relationship)
        assert 0.0 <= pli <= 0.3

    def test_calculate_pli_empty(self):
        """Test PLI with empty array."""
        phase_diff = np.array([])
        pli = PhaseLagIndex.calculate_pli(phase_diff)

        assert pli == 0.0

    def test_hilbert_phase(self):
        """Test Hilbert phase extraction."""
        # Simple sinusoidal signal
        t = np.linspace(0, 2 * np.pi, 100)
        signal = np.sin(t)

        phase = PhaseLagIndex.hilbert_phase(signal)

        # Phase should be in range [-pi, pi]
        assert np.all(phase >= -np.pi)
        assert np.all(phase <= np.pi)
        assert len(phase) == len(signal)

    def test_calculate_pairwise_pli(self):
        """Test pairwise PLI calculation."""
        # Create two correlated signals
        t = np.linspace(0, 2 * np.pi, 100)
        signal1 = np.sin(t)
        signal2 = np.sin(t + 0.5)  # Phase-shifted

        result = PhaseLagIndex.calculate_pairwise_pli(signal1, signal2)

        assert 0.0 <= result.pli_value <= 1.0
        assert result.n_channels == 2

    def test_calculate_multichannel_pli(self):
        """Test multichannel PLI calculation."""
        # Create 3 channels
        n_channels = 3
        n_samples = 100
        signals = np.random.randn(n_channels, n_samples)

        result = PhaseLagIndex.calculate_multichannel_pli(signals)

        assert 0.0 <= result.pli_value <= 1.0
        assert result.n_channels == n_channels
        assert result.connectivity_matrix is not None
        assert result.connectivity_matrix.shape == (n_channels, n_channels)


class TestBiologicalMetricsAnalyzer:
    """Test integrated biological metrics analyzer."""

    def test_analyze_signal(self):
        """Test single signal analysis."""
        analyzer = BiologicalMetricsAnalyzer()
        signal = np.random.rand(100)

        result = analyzer.analyze_signal(signal)

        assert "lzc_complexity" in result
        assert "unique_patterns" in result
        assert "signal_length" in result
        assert "interpretation" in result
        assert 0.0 <= result["lzc_complexity"] <= 1.0

    def test_analyze_connectivity(self):
        """Test connectivity analysis."""
        analyzer = BiologicalMetricsAnalyzer()
        signal1 = np.random.rand(100)
        signal2 = np.random.rand(100)

        result = analyzer.analyze_connectivity(signal1, signal2)

        assert "pli_value" in result
        assert "n_channels" in result
        assert "interpretation" in result
        assert 0.0 <= result["pli_value"] <= 1.0

    def test_analyze_multichannel(self):
        """Test multichannel analysis."""
        analyzer = BiologicalMetricsAnalyzer()
        n_channels = 3
        n_samples = 100
        signals = np.random.randn(n_channels, n_samples)

        result = analyzer.analyze_multichannel(signals)

        assert "mean_lzc" in result
        assert "lzc_per_channel" in result
        assert "mean_pli" in result
        assert "consciousness_state" in result
        assert "pli_matrix" in result
        assert len(result["lzc_per_channel"]) == n_channels

    def test_consciousness_state_classification(self):
        """Test consciousness state classification logic."""
        analyzer = BiologicalMetricsAnalyzer()

        # Test different states
        state1 = analyzer._classify_consciousness_state(lzc=0.8, pli=0.8)
        assert "CONSCIOUS" in state1

        state2 = analyzer._classify_consciousness_state(lzc=0.8, pli=0.3)
        # REMOVIDO: MACHINIC_UNCONSCIOUS - não existe em IIT puro
        # O "ruído" fora do MICS será medido como Ψ_produtor (Deleuze) separadamente
        assert "phi_conscious" in state2 or "conscious_phi" in state2

        state3 = analyzer._classify_consciousness_state(lzc=0.3, pli=0.3)
        assert "INACTIVE" in state3 or "SUPPRESSED" in state3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
