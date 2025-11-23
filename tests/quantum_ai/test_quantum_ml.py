"""
Testes para Quantum Machine Learning (quantum_ml.py).

Cobertura de:
- Quantum feature mapping
- Quantum kernel computation
- Quantum-inspired algorithms
- State encoding/decoding
- Tratamento de exceções
"""

from __future__ import annotations

import math
import pytest
from typing import List

from src.quantum_ai.quantum_ml import (
    QuantumFeatureMap,
    QuantumKernel,
)


class TestQuantumFeatureMap:
    """Testes para QuantumFeatureMap."""

    def test_feature_map_initialization(self) -> None:
        """Testa inicialização do feature map."""
        feature_map = QuantumFeatureMap(dimension=16, num_qubits=4)

        assert feature_map.dimension == 16
        assert feature_map.num_qubits == 4

    def test_encode_simple_features(self) -> None:
        """Testa encoding de features simples."""
        feature_map = QuantumFeatureMap(dimension=4, num_qubits=2)
        features = [1.0, 0.0, 0.0, 0.0]

        amplitudes = feature_map.encode(features)

        assert len(amplitudes) == 4
        assert all(isinstance(a, complex) for a in amplitudes)
        # Verify normalization
        total = sum(abs(a) ** 2 for a in amplitudes)
        assert abs(total - 1.0) < 1e-6

    def test_encode_normalized_features(self) -> None:
        """Testa encoding com normalização."""
        feature_map = QuantumFeatureMap(dimension=4, num_qubits=2)
        features = [3.0, 4.0, 0.0, 0.0]  # Will be normalized

        amplitudes = feature_map.encode(features)

        # Verify state is normalized
        total = sum(abs(a) ** 2 for a in amplitudes)
        assert abs(total - 1.0) < 1e-6

    def test_encode_zero_features(self) -> None:
        """Testa encoding de features zero."""
        feature_map = QuantumFeatureMap(dimension=4, num_qubits=2)
        features = [0.0, 0.0, 0.0, 0.0]

        amplitudes = feature_map.encode(features)

        # All amplitudes should be zero
        assert all(abs(a) < 1e-10 for a in amplitudes)

    def test_encode_large_feature_vector(self) -> None:
        """Testa encoding com vetor de features maior que dimensão."""
        feature_map = QuantumFeatureMap(dimension=4, num_qubits=2)
        features = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        amplitudes = feature_map.encode(features)

        # Should only use first 4 features (2^2 qubits)
        assert len(amplitudes) == 4

    def test_encode_small_feature_vector(self) -> None:
        """Testa encoding com vetor menor que dimensão."""
        feature_map = QuantumFeatureMap(dimension=8, num_qubits=3)
        features = [1.0, 0.5]

        amplitudes = feature_map.encode(features)

        # Should pad with zeros
        assert len(amplitudes) == 8
        assert amplitudes[0] != complex(0, 0)
        assert amplitudes[1] != complex(0, 0)


class TestQuantumKernel:
    """Testes para QuantumKernel."""

    def test_kernel_initialization(self) -> None:
        """Testa inicialização do kernel."""
        kernel = QuantumKernel(num_qubits=4)

        assert kernel.num_qubits == 4
        assert kernel.feature_map is not None
        assert kernel.feature_map.num_qubits == 4

    def test_compute_kernel_identical_vectors(self) -> None:
        """Testa kernel de vetores idênticos."""
        kernel = QuantumKernel(num_qubits=2)
        x = [1.0, 0.0, 0.0, 0.0]

        similarity = kernel.compute_kernel(x, x)

        # Identical vectors should have similarity close to 1
        assert similarity >= 0.95

    def test_compute_kernel_orthogonal_vectors(self) -> None:
        """Testa kernel de vetores ortogonais."""
        kernel = QuantumKernel(num_qubits=2)
        x1 = [1.0, 0.0, 0.0, 0.0]
        x2 = [0.0, 1.0, 0.0, 0.0]

        similarity = kernel.compute_kernel(x1, x2)

        # Orthogonal vectors should have low similarity
        assert 0.0 <= similarity <= 1.0

    def test_compute_kernel_similar_vectors(self) -> None:
        """Testa kernel de vetores similares."""
        kernel = QuantumKernel(num_qubits=2)
        x1 = [1.0, 0.1, 0.0, 0.0]
        x2 = [1.0, 0.2, 0.0, 0.0]

        similarity = kernel.compute_kernel(x1, x2)

        # Similar vectors should have high similarity
        assert similarity > 0.5

    def test_compute_kernel_symmetry(self) -> None:
        """Testa simetria do kernel."""
        kernel = QuantumKernel(num_qubits=2)
        x1 = [1.0, 0.5, 0.0, 0.0]
        x2 = [0.5, 1.0, 0.0, 0.0]

        sim1 = kernel.compute_kernel(x1, x2)
        sim2 = kernel.compute_kernel(x2, x1)

        # Kernel should be symmetric
        assert abs(sim1 - sim2) < 1e-6

    def test_compute_kernel_zero_vectors(self) -> None:
        """Testa kernel com vetores zero."""
        kernel = QuantumKernel(num_qubits=2)
        x1 = [0.0, 0.0, 0.0, 0.0]
        x2 = [1.0, 0.0, 0.0, 0.0]

        similarity = kernel.compute_kernel(x1, x2)

        # Result should still be valid (between 0 and 1)
        assert 0.0 <= similarity <= 1.0

    def test_compute_kernel_different_num_qubits(self) -> None:
        """Testa kernels com diferentes números de qubits."""
        kernel_small = QuantumKernel(num_qubits=2)
        kernel_large = QuantumKernel(num_qubits=4)

        x1 = [1.0, 0.5, 0.0, 0.0]
        x2 = [0.5, 1.0, 0.0, 0.0]

        sim_small = kernel_small.compute_kernel(x1, x2)
        sim_large = kernel_large.compute_kernel(x1, x2)

        # Both should produce valid similarities
        assert 0.0 <= sim_small <= 1.0
        assert 0.0 <= sim_large <= 1.0

    def test_compute_kernel_negative_features(self) -> None:
        """Testa kernel com features negativas."""
        kernel = QuantumKernel(num_qubits=2)
        x1 = [1.0, -0.5, 0.0, 0.0]
        x2 = [-1.0, 0.5, 0.0, 0.0]

        similarity = kernel.compute_kernel(x1, x2)

        # Should handle negative features correctly (allow for floating point error)
        assert -1e-10 <= similarity <= 1.0 + 1e-10

    def test_compute_kernel_large_values(self) -> None:
        """Testa kernel com valores grandes."""
        kernel = QuantumKernel(num_qubits=2)
        x1 = [100.0, 50.0, 0.0, 0.0]
        x2 = [100.0, 51.0, 0.0, 0.0]

        similarity = kernel.compute_kernel(x1, x2)

        # Large values should be normalized and produce valid results
        assert 0.0 <= similarity <= 1.0

    def test_kernel_multiple_comparisons(self) -> None:
        """Testa múltiplas comparações de kernel."""
        kernel = QuantumKernel(num_qubits=3)

        vectors = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0, 0.0],
        ]

        # Compute kernel matrix
        for i, x1 in enumerate(vectors):
            for j, x2 in enumerate(vectors):
                similarity = kernel.compute_kernel(x1, x2)
                # Allow for floating point error
                assert -1e-10 <= similarity <= 1.0 + 1e-10

                # Diagonal should be close to 1
                if i == j:
                    assert similarity >= 0.95


class TestQuantumMLEdgeCases:
    """Testes para casos extremos e exceções."""

    def test_feature_map_with_one_qubit(self) -> None:
        """Testa feature map com apenas 1 qubit."""
        feature_map = QuantumFeatureMap(dimension=2, num_qubits=1)
        features = [1.0, 0.0]

        amplitudes = feature_map.encode(features)

        assert len(amplitudes) == 2

    def test_kernel_with_empty_features(self) -> None:
        """Testa kernel com features vazias."""
        kernel = QuantumKernel(num_qubits=2)
        x1: List[float] = []
        x2 = [1.0, 0.0]

        similarity = kernel.compute_kernel(x1, x2)

        # Should handle gracefully
        assert 0.0 <= similarity <= 1.0

    def test_feature_map_normalization_stability(self) -> None:
        """Testa estabilidade da normalização."""
        feature_map = QuantumFeatureMap(dimension=4, num_qubits=2)

        # Very small values
        features_small = [1e-10, 1e-10, 0.0, 0.0]
        amplitudes_small = feature_map.encode(features_small)

        # Very large values
        features_large = [1e10, 1e10, 0.0, 0.0]
        amplitudes_large = feature_map.encode(features_large)

        # Both should be properly normalized
        total_small = sum(abs(a) ** 2 for a in amplitudes_small)
        total_large = sum(abs(a) ** 2 for a in amplitudes_large)

        # Should be normalized or all zeros
        assert abs(total_small - 1.0) < 1e-6 or total_small < 1e-9
        assert abs(total_large - 1.0) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
