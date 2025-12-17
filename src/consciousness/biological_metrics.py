"""
Biological Metrics for Consciousness Measurement.

Implements efficient algorithms for:
1. Lempel-Ziv Complexity (LZC): Measures structural richness of signal
2. Phase Lag Index (PLI): Measures functional connectivity immune to volume conduction

Based on canonical documentation: docs/canonical/NEURAL_SYSTEMS_COMPARISON_2016-2025.md
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

try:
    import numpy as np
    from numpy.typing import NDArray
except ImportError:
    np = None  # type: ignore
    NDArray = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class LZCResult:
    """Result of Lempel-Ziv Complexity calculation."""

    complexity: float  # Normalized LZ complexity (0-1)
    binary_sequence: str  # Binarized signal
    unique_patterns: int  # Number of unique patterns found
    signal_length: int  # Length of original signal


@dataclass
class PLIResult:
    """Result of Phase Lag Index calculation."""

    pli_value: float  # PLI value (0-1), higher = stronger connectivity
    n_channels: int  # Number of channels analyzed
    connectivity_matrix: Optional["NDArray"] = None  # Full pairwise connectivity


class LempelZivComplexity:
    """
    Lempel-Ziv Complexity (LZC) calculator.

    Measures the 'riqueza' (richness) structural do sinal, independent of integration.
    Used to validate if regions have activity even when disconnected (unconscious activity).

    References:
    - Sarasso et al. (Neuron 2021)
    - Ma et al. (2024 PMC)
    - Used clinically to detect consciousness levels
    """

    @staticmethod
    def binarize_signal(signal: "NDArray", threshold: Optional[float] = None) -> str:
        """
        Binarize signal using mean threshold.

        Args:
            signal: 1D array of signal values
            threshold: Optional custom threshold (default: mean of signal)

        Returns:
            Binary string representation
        """
        if np is None:
            raise ImportError("NumPy is required for biological metrics")

        if threshold is None:
            threshold = float(np.mean(signal))

        binary = "".join(["1" if x >= threshold else "0" for x in signal])
        return binary

    @staticmethod
    def calculate_complexity(binary_sequence: str) -> LZCResult:
        """
        Calculate Lempel-Ziv complexity of binary sequence.

        Algorithm:
        1. Scan sequence from left to right
        2. Identify smallest substring not seen before
        3. Count unique patterns
        4. Normalize by theoretical maximum

        Args:
            binary_sequence: Binary string (e.g., "01001110")

        Returns:
            LZCResult with complexity metrics
        """
        if not binary_sequence:
            return LZCResult(
                complexity=0.0,
                binary_sequence="",
                unique_patterns=0,
                signal_length=0,
            )

        n = len(binary_sequence)
        unique_patterns = 1  # Start with first symbol
        i = 0
        current_dict: List[str] = []

        while i < n:
            # Find smallest new substring
            j = i + 1
            substring = binary_sequence[i:j]

            # Extend substring until we find a new pattern
            while substring in current_dict and j <= n:
                j += 1
                substring = binary_sequence[i:j]

            current_dict.append(substring)
            unique_patterns += 1
            i = j

        # Normalize by theoretical maximum
        # For binary sequence of length n, max complexity ~ n / log2(n)
        if n > 1 and np is not None:
            max_complexity = n / np.log2(n)
            normalized_complexity = unique_patterns / max_complexity
        elif n > 1:
            # Fallback without numpy: simple linear normalization
            max_complexity = n / 2.0  # Rough approximation
            normalized_complexity = unique_patterns / max_complexity
        else:
            normalized_complexity = 1.0

        return LZCResult(
            complexity=min(normalized_complexity, 1.0),
            binary_sequence=binary_sequence,
            unique_patterns=unique_patterns,
            signal_length=n,
        )

    @classmethod
    def from_signal(cls, signal: "NDArray", threshold: Optional[float] = None) -> LZCResult:
        """
        Calculate LZ complexity directly from signal.

        Args:
            signal: 1D array of signal values
            threshold: Optional binarization threshold

        Returns:
            LZCResult with complexity metrics
        """
        binary_seq = cls.binarize_signal(signal, threshold)
        return cls.calculate_complexity(binary_seq)


class PhaseLagIndex:
    """
    Phase Lag Index (PLI) calculator.

    Measures functional connectivity immune to volume conduction.
    Used to validate if "disconnected" regions still have internal activity (unconscious).

    Properties:
    - Immune to zero-phase lag (volume conduction artifact)
    - Values: 0 (no connectivity) to 1 (perfect phase-locked)
    - Asymmetric measure: PLI(A,B) may differ from PLI(B,A)

    References:
    - Stam et al. (2007) "Phase lag index: Assessment of functional connectivity..."
    - Used in consciousness research to detect unconscious processing
    """

    @staticmethod
    def calculate_pli(phase_diff: "NDArray") -> float:
        """
        Calculate PLI from phase differences.

        PLI = |E[sign(Δφ)]| where Δφ is phase difference

        Args:
            phase_diff: Array of phase differences in radians

        Returns:
            PLI value (0-1)
        """
        if np is None:
            raise ImportError("NumPy is required for biological metrics")

        if len(phase_diff) == 0:
            return 0.0

        # PLI is absolute value of mean of sign of phase differences
        pli = abs(float(np.mean(np.sign(phase_diff))))
        return pli

    @staticmethod
    def hilbert_phase(signal: "NDArray") -> "NDArray":
        """
        Extract instantaneous phase using Hilbert transform.

        Args:
            signal: 1D array of signal values

        Returns:
            Array of instantaneous phases in radians

        Note:
            If scipy is not available, falls back to simplified phase estimation
            using arctan2. The fallback is significantly less accurate and should
            only be used when scipy cannot be installed.
        """
        if np is None:
            raise ImportError("NumPy is required for biological metrics")

        try:
            from scipy.signal import hilbert

            analytic_signal = hilbert(signal)
            phase = np.angle(analytic_signal)
            return phase
        except ImportError:
            logger.warning(
                "scipy not available, using simplified phase estimation "
                "(significantly less accurate than Hilbert transform)"
            )
            # Simplified phase estimation without scipy
            # This is less accurate but provides a fallback
            return np.arctan2(signal - np.mean(signal), np.gradient(signal - np.mean(signal)))

    @classmethod
    def calculate_pairwise_pli(cls, signal1: "NDArray", signal2: "NDArray") -> PLIResult:
        """
        Calculate PLI between two signals.

        Args:
            signal1: First signal channel
            signal2: Second signal channel

        Returns:
            PLIResult with connectivity metrics
        """
        if np is None:
            raise ImportError("NumPy is required for biological metrics")

        # Extract phases
        phase1 = cls.hilbert_phase(signal1)
        phase2 = cls.hilbert_phase(signal2)

        # Calculate phase difference
        phase_diff = phase1 - phase2

        # Calculate PLI
        pli_value = cls.calculate_pli(phase_diff)

        return PLIResult(pli_value=pli_value, n_channels=2, connectivity_matrix=None)

    @classmethod
    def calculate_multichannel_pli(cls, signals: "NDArray") -> PLIResult:
        """
        Calculate PLI for all pairs in multichannel data.

        Args:
            signals: 2D array of shape (n_channels, n_samples)

        Returns:
            PLIResult with full connectivity matrix
        """
        if np is None:
            raise ImportError("NumPy is required for biological metrics")

        n_channels = signals.shape[0]

        if n_channels < 2:
            return PLIResult(pli_value=0.0, n_channels=n_channels, connectivity_matrix=None)

        # Calculate pairwise PLI for all channel pairs
        pli_matrix = np.zeros((n_channels, n_channels))

        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                result = cls.calculate_pairwise_pli(signals[i], signals[j])
                pli_matrix[i, j] = result.pli_value
                # PLI can be asymmetric, but for simplicity we make it symmetric here
                pli_matrix[j, i] = result.pli_value

        # Average PLI across all pairs
        mean_pli = float(
            np.mean(pli_matrix[np.triu_indices(n_channels, k=1)])
        )  # Upper triangle only

        return PLIResult(pli_value=mean_pli, n_channels=n_channels, connectivity_matrix=pli_matrix)


class BiologicalMetricsAnalyzer:
    """
    Combined analyzer for biological consciousness metrics.

    Integrates LZC and PLI to provide comprehensive consciousness assessment:
    - LZC: Detects structural richness (independent of integration)
    - PLI: Detects functional connectivity (unconscious processing)

    Use case for hybrid consciousness:
    - High LZC + Low PLI = Machinic Unconscious (active but not integrated)
    - High LZC + High PLI = Conscious (MICS - integrated and active)
    - Low LZC = Inactive/Suppressed
    """

    def __init__(self) -> None:
        self.lzc_calculator = LempelZivComplexity()
        self.pli_calculator = PhaseLagIndex()

    def analyze_signal(self, signal: "NDArray", threshold: Optional[float] = None) -> dict:
        """
        Analyze single signal for complexity and structure.

        Args:
            signal: 1D signal array
            threshold: Optional binarization threshold for LZC

        Returns:
            Dictionary with LZC metrics
        """
        lzc_result = self.lzc_calculator.from_signal(signal, threshold)

        return {
            "lzc_complexity": lzc_result.complexity,
            "unique_patterns": lzc_result.unique_patterns,
            "signal_length": lzc_result.signal_length,
            "interpretation": self._interpret_lzc(lzc_result.complexity),
        }

    def analyze_connectivity(self, signal1: "NDArray", signal2: "NDArray") -> dict:
        """
        Analyze functional connectivity between two signals.

        Args:
            signal1: First signal channel
            signal2: Second signal channel

        Returns:
            Dictionary with PLI metrics
        """
        pli_result = self.pli_calculator.calculate_pairwise_pli(signal1, signal2)

        return {
            "pli_value": pli_result.pli_value,
            "n_channels": pli_result.n_channels,
            "interpretation": self._interpret_pli(pli_result.pli_value),
        }

    def analyze_multichannel(self, signals: "NDArray") -> dict:
        """
        Comprehensive analysis of multichannel data.

        Args:
            signals: 2D array of shape (n_channels, n_samples)

        Returns:
            Dictionary with combined LZC and PLI metrics
        """
        if np is None:
            raise ImportError("NumPy is required for biological metrics")

        n_channels = signals.shape[0]

        # Calculate LZC for each channel
        lzc_per_channel = []
        for i in range(n_channels):
            lzc_result = self.lzc_calculator.from_signal(signals[i])
            lzc_per_channel.append(lzc_result.complexity)

        mean_lzc = float(np.mean(lzc_per_channel))

        # Calculate PLI across all channels
        pli_result = self.pli_calculator.calculate_multichannel_pli(signals)

        # Classify consciousness state
        consciousness_state = self._classify_consciousness_state(mean_lzc, pli_result.pli_value)

        return {
            "mean_lzc": mean_lzc,
            "lzc_per_channel": lzc_per_channel,
            "mean_pli": pli_result.pli_value,
            "n_channels": n_channels,
            "consciousness_state": consciousness_state,
            "pli_matrix": pli_result.connectivity_matrix,
        }

    def _interpret_lzc(self, lzc: float) -> str:
        """Interpret LZC value."""
        if lzc > 0.7:
            return "High complexity - Rich internal structure"
        elif lzc > 0.4:
            return "Moderate complexity - Some structure present"
        else:
            return "Low complexity - Limited structural richness"

    def _interpret_pli(self, pli: float) -> str:
        """Interpret PLI value."""
        if pli > 0.7:
            return "Strong connectivity - High integration"
        elif pli > 0.4:
            return "Moderate connectivity - Partial integration"
        else:
            return "Weak connectivity - Low integration"

    def _classify_consciousness_state(self, lzc: float, pli: float) -> str:
        """
        Classify consciousness state based on LZC and PLI.

        Hybrid consciousness theory:
        - MICS (Conscious): High LZC + High PLI
        - Machinic Unconscious: High LZC + Low PLI (active but not integrated)
        - Suppressed/Inactive: Low LZC
        """
        if lzc > 0.6 and pli > 0.6:
            return "CONSCIOUS (MICS) - High complexity + High integration"
        elif lzc > 0.6 and pli <= 0.6:
            return (
                "LOW_INTEGRATION - High complexity but low integration "
                # REMOVIDO: MACHINIC_UNCONSCIOUS - não existe em IIT puro
                # O "ruído" fora do MICS será medido como Ψ_produtor (Deleuze) separadamente
                "(active but not in MICS)"
            )
        elif lzc <= 0.6 and pli > 0.6:
            return "INTEGRATED_BUT_SIMPLE - Integrated but low structural richness"
        else:
            return "INACTIVE/SUPPRESSED - Low complexity and low integration"
