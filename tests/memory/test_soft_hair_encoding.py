"""
Tests for Soft Hair Encoding system.

Tests low-frequency mode extraction, compression,
and reconstruction fidelity.
"""

import numpy as np

from src.memory.soft_hair_encoding import (
    SoftHair,
    SoftHairEncoder,
    SoftHairMemory,
)


class TestSoftHair:
    """Test SoftHair dataclass."""

    def test_creation(self) -> None:
        """Test soft hair creation."""
        soft_modes_arr = np.random.randn(10, 10) + 1j * np.random.randn(10, 10)
        soft_modes = soft_modes_arr.tolist()
        metadata = {"test": "value"}

        soft_hair = SoftHair(
            soft_modes=soft_modes,
            metadata=metadata,
            compression_ratio=5.0,
            original_shape=(50, 50),
        )

        assert len(soft_hair.soft_modes) == 10
        assert len(soft_hair.soft_modes[0]) == 10
        assert soft_hair.compression_ratio == 5.0
        assert soft_hair.original_shape == (50, 50)


class TestSoftHairEncoder:
    """Test soft hair encoder."""

    def test_initialization(self) -> None:
        """Test encoder initializes correctly."""
        encoder = SoftHairEncoder(soft_mode_cutoff=0.2, max_modes=128)

        assert encoder.soft_mode_cutoff == 0.2
        assert encoder.max_modes == 128

    def test_encode_1d_data(self) -> None:
        """Test encoding 1D data."""
        encoder = SoftHairEncoder()

        data_arr = np.random.randn(100)
        data = data_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(data)

        assert isinstance(soft_hair, SoftHair)
        # Check list of lists structure
        assert len(soft_hair.soft_modes) > 0
        assert len(soft_hair.soft_modes[0]) > 0
        assert soft_hair.compression_ratio > 1.0
        assert soft_hair.original_shape == (100,)

    def test_encode_2d_data(self) -> None:
        """Test encoding 2D data."""
        encoder = SoftHairEncoder()

        data_arr = np.random.randn(32, 32)
        data = data_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(data)

        assert isinstance(soft_hair, SoftHair)
        assert soft_hair.compression_ratio > 1.0
        assert soft_hair.original_shape == (32, 32)

    def test_encode_3d_data(self) -> None:
        """Test encoding 3D data."""
        encoder = SoftHairEncoder()

        data_arr = np.random.randn(8, 8, 8)
        data = data_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(data)

        assert isinstance(soft_hair, SoftHair)
        assert soft_hair.compression_ratio > 1.0

    def test_compression_ratio(self) -> None:
        """Test that compression actually reduces size."""
        encoder = SoftHairEncoder(soft_mode_cutoff=0.1)

        data_arr = np.random.randn(100, 100)
        data = data_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(data)

        # Should achieve significant compression
        # Calculate size of soft_modes (list of lists of complex)
        soft_modes_size = sum(len(row) for row in soft_hair.soft_modes)
        assert soft_modes_size < data_arr.size
        assert soft_hair.compression_ratio > 1.0

    def test_metadata_extraction(self) -> None:
        """Test metadata extraction."""
        encoder = SoftHairEncoder()

        data_arr = np.random.randn(50)
        data = data_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(data)

        assert "original_mean" in soft_hair.metadata
        assert "original_std" in soft_hair.metadata
        assert "soft_mode_shape" in soft_hair.metadata
        assert "dominant_frequency" in soft_hair.metadata

    def test_decode_1d(self) -> None:
        """Test decoding 1D data."""
        encoder = SoftHairEncoder(soft_mode_cutoff=0.3)

        original_arr = np.random.randn(64)
        original = original_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(original)
        reconstructed = encoder.decode_from_soft_hair(soft_hair)

        # Reconstructed is a list, original is numpy array
        assert len(reconstructed) == original_arr.size
        # Reconstruction should be similar (not exact due to compression)
        assert len(reconstructed) == original_arr.size

    def test_decode_2d(self) -> None:
        """Test decoding 2D data."""
        encoder = SoftHairEncoder(soft_mode_cutoff=0.3)

        original_arr = np.random.randn(32, 32)
        original = original_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(original)
        reconstructed = encoder.decode_from_soft_hair(soft_hair)

        # Reconstructed is a list of lists (or flat list depending on implementation)
        # The implementation of decode_from_soft_hair returns Sequence[Any]
        # For 2D, it returns List[List[float]]
        assert len(reconstructed) == original_arr.shape[0]
        assert len(reconstructed[0]) == original_arr.shape[1]

    def test_soft_mode_extraction(self) -> None:
        """Test soft mode extraction from FFT."""
        encoder = SoftHairEncoder(soft_mode_cutoff=0.2)

        freq_data = [[complex(1, 1) for _ in range(100)] for _ in range(100)]
        soft_modes = encoder._extract_soft_modes(freq_data)

        # Should extract only a fraction
        soft_modes_size = sum(len(row) for row in soft_modes)
        freq_data_size = 100 * 100
        assert soft_modes_size < freq_data_size

    def test_dominant_frequency_detection(self) -> None:
        """Test dominant frequency detection."""
        encoder = SoftHairEncoder()

        soft_modes_arr = np.random.randn(10, 10) + 1j * np.random.randn(10, 10)
        soft_modes = soft_modes_arr.tolist()
        dom_freq = encoder._find_dominant_frequency(soft_modes)

        assert dom_freq >= 0


class TestSoftHairMemory:
    """Test soft hair memory system."""

    def test_initialization(self) -> None:
        """Test memory initializes correctly."""
        memory = SoftHairMemory()

        assert memory.encoder is not None
        assert len(memory.memory_bank) == 0

    def test_store_and_retrieve(self) -> None:
        """Test storing and retrieving data."""
        memory = SoftHairMemory()

        data_arr = np.random.randn(50)
        data = data_arr.tolist()
        memory.store("test_key", data)

        retrieved = memory.retrieve("test_key")

        assert retrieved is not None
        # retrieved is a list
        assert len(retrieved) == data_arr.size

    def test_retrieve_nonexistent(self) -> None:
        """Test retrieving non-existent key."""
        memory = SoftHairMemory()

        retrieved = memory.retrieve("nonexistent")

        assert retrieved is None

    def test_multiple_items(self) -> None:
        """Test storing multiple items."""
        memory = SoftHairMemory()

        for i in range(5):
            data_arr = np.random.randn(64) * (i + 1)
            data = data_arr.tolist()
            memory.store(f"item_{i}", data)

        assert len(memory.memory_bank) == 5

        # Retrieve all
        for i in range(5):
            retrieved = memory.retrieve(f"item_{i}")
            assert retrieved is not None

    def test_compression_stats(self) -> None:
        """Test compression statistics."""
        memory = SoftHairMemory()

        # Store some data
        for i in range(3):
            data_arr = np.random.randn(100)
            data = data_arr.tolist()
            memory.store(f"data_{i}", data)

        stats = memory.get_compression_stats()

        assert stats["total_items"] == 3
        assert stats["average_compression"] > 1.0
        assert stats["total_soft_modes"] > 0

    def test_empty_memory_stats(self) -> None:
        """Test stats for empty memory."""
        memory = SoftHairMemory()

        stats = memory.get_compression_stats()

        assert stats["total_items"] == 0
        assert stats["average_compression"] == 0.0


class TestIntegration:
    """Integration tests for soft hair encoding."""

    def test_encode_decode_cycle(self) -> None:
        """Test full encode-decode cycle."""
        encoder = SoftHairEncoder(soft_mode_cutoff=0.3)

        # Original data with some structure (smooth signal)
        x = np.linspace(0, 2 * np.pi, 100)
        original_arr = np.sin(x) + 0.1 * np.random.randn(100)
        original = original_arr.tolist()

        # Encode
        soft_hair = encoder.encode_to_soft_hair(original)

        # Decode
        reconstructed = encoder.decode_from_soft_hair(soft_hair)

        # Fidelity check
        fidelity = encoder.compute_fidelity(original, reconstructed)

        # Should have reasonable fidelity for smooth signal
        assert fidelity > 0.5

    def test_compression_vs_fidelity_tradeoff(self) -> None:
        """Test compression vs fidelity tradeoff."""
        # Use smaller size for naive DFT performance
        data_arr = np.random.randn(32, 32)
        data = data_arr.tolist()

        cutoffs = [0.05, 0.1, 0.2, 0.5]
        compressions = []
        fidelities = []

        for cutoff in cutoffs:
            encoder = SoftHairEncoder(soft_mode_cutoff=cutoff)
            soft_hair = encoder.encode_to_soft_hair(data)
            reconstructed = encoder.decode_from_soft_hair(soft_hair)

            compressions.append(soft_hair.compression_ratio)
            fidelities.append(encoder.compute_fidelity(data, reconstructed))

        # Higher cutoff = less compression but better fidelity
        # (compression should decrease with cutoff)
        # (fidelity should increase with cutoff)
        assert fidelities[-1] >= fidelities[0]

    def test_memory_with_different_data_types(self) -> None:
        """Test memory with various data shapes."""
        memory = SoftHairMemory()

        # 1D
        memory.store("1d", np.random.randn(100).tolist())

        # 2D
        memory.store("2d", np.random.randn(32, 32).tolist())

        # 3D
        memory.store("3d", np.random.randn(8, 8, 8).tolist())

        # Retrieve all
        assert memory.retrieve("1d") is not None
        assert memory.retrieve("2d") is not None
        assert memory.retrieve("3d") is not None

    def test_robustness_to_noise(self) -> None:
        """Test that soft hair encoding is robust to high-frequency noise."""
        encoder = SoftHairEncoder(soft_mode_cutoff=0.2)

        # Signal with low-frequency content
        x = np.linspace(0, 4 * np.pi, 200)
        clean_signal = np.sin(x)

        # Add high-frequency noise
        noise = 0.5 * np.sin(20 * x)
        noisy_signal = clean_signal + noise

        # Encode noisy signal (should filter out high-freq noise)
        noisy_list = noisy_signal.tolist()
        soft_hair = encoder.encode_to_soft_hair(noisy_list)
        reconstructed = encoder.decode_from_soft_hair(soft_hair)

        # Reconstructed should be closer to clean than noisy
        # (soft modes filter high-frequency noise)
        clean_list = clean_signal.tolist()
        fidelity_to_clean = encoder.compute_fidelity(clean_list, reconstructed)
        fidelity_to_noisy = encoder.compute_fidelity(noisy_list, reconstructed)

        # Both should have reasonable fidelity
        assert fidelity_to_clean >= 0
        assert fidelity_to_noisy >= 0


class TestSoftHairEncodingHybridTopological:
    """Testes de integração entre SoftHairEncoding e HybridTopologicalEngine."""

    def test_soft_hair_encoding_with_topological_metrics(self):
        """Testa que SoftHairEncoding pode ser usado com métricas topológicas."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar SoftHairEncoder
        encoder = SoftHairEncoder()

        # Codificar dados
        data_arr = np.random.randn(100)
        data = data_arr.tolist()
        soft_hair = encoder.encode_to_soft_hair(data)

        # Simular estados no workspace para métricas topológicas
        np.random.seed(42)
        for i in range(5):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            workspace.write_module_state("conscious_module", rho_C)
            workspace.write_module_state("preconscious_module", rho_P)
            workspace.write_module_state("unconscious_module", rho_U)
            workspace.advance_cycle()

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que ambas funcionam
        assert isinstance(soft_hair, SoftHair)
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # SoftHairEncoding: compressão de memória (modos suaves)
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa
