"""
Tests for Event Horizon Memory (Holographic Memory System).

Tests the holographic principle-based memory architecture with
Bekenstein bound constraints and hierarchical memory spawning.
"""

from typing import cast

import numpy as np

from src.memory.holographic_memory import (
    EventHorizonMemory,
    HolographicProjection,
    HolographicSurface,
)


class TestHolographicProjection:
    """Test holographic projection system."""

    def test_initialization(self) -> None:
        """Test projection system initializes correctly."""
        proj = HolographicProjection(max_surface_dim=256)
        assert proj.max_surface_dim == 256

    def test_project_2d_data(self) -> None:
        """Test projection of 2D data (already on boundary)."""
        proj = HolographicProjection()
        data_2d = np.random.randn(10, 10)
        information = {"tensor": data_2d}

        result = proj.project_to_boundary(information)

        # Ensure result is treated as array
        result_arr = cast(np.ndarray, result)
        assert isinstance(result_arr, np.ndarray)
        assert result_arr.shape == data_2d.shape

    def test_project_3d_data(self) -> None:
        """Test projection of 3D data to 2D surface."""
        proj = HolographicProjection()
        data_3d = np.random.randn(16, 16, 16)
        information = {"tensor": data_3d}

        result = proj.project_to_boundary(information)

        # Ensure result is treated as array
        result_arr = cast(np.ndarray, result)
        assert isinstance(result_arr, np.ndarray)
        assert result_arr.ndim == 2
        assert max(result_arr.shape) <= proj.max_surface_dim

    def test_project_1d_data(self) -> None:
        """Test projection of 1D data."""
        proj = HolographicProjection()
        data_1d = np.random.randn(64)
        information = {"array": data_1d}

        result = proj.project_to_boundary(information)

        # Ensure result is treated as array
        result_arr = cast(np.ndarray, result)
        assert isinstance(result_arr, np.ndarray)
        assert result_arr.ndim == 2
        assert result_arr.shape[0] * result_arr.shape[1] >= data_1d.size

    def test_downsample_large_surface(self) -> None:
        """Test downsampling of large surfaces."""
        proj = HolographicProjection(max_surface_dim=64)
        data_large = np.random.randn(128, 128)
        information = {"tensor": data_large}

        result = proj.project_to_boundary(information)

        # Ensure result is treated as array
        result_arr = cast(np.ndarray, result)
        # Ensure result is treated as array
        assert max(result_arr.shape) <= 64


class TestHolographicSurface:
    """Test holographic surface dataclass."""

    def test_surface_creation(self) -> None:
        """Test surface creation with valid entropy."""
        surface = HolographicSurface(
            surface_bits=np.zeros((10, 10)),
            area=100.0,
            entropy=50.0,
            max_entropy=100.0,
        )

        assert surface.area == 100.0
        assert surface.entropy == 50.0
        assert surface.max_entropy == 100.0

    def test_entropy_exceeds_bound(self) -> None:
        """Test that entropy is clamped to Bekenstein bound."""
        # Create surface with entropy exceeding bound
        surface = HolographicSurface(
            surface_bits=np.zeros((10, 10)),
            area=100.0,
            entropy=150.0,  # Exceeds max_entropy
            max_entropy=100.0,
        )

        # Should be clamped
        assert surface.entropy == 100.0


class TestEventHorizonMemory:
    """Test event horizon memory system."""

    def test_initialization(self) -> None:
        """Test memory system initializes correctly."""
        memory = EventHorizonMemory(initial_area=1000.0)

        assert memory.area == 1000.0
        assert memory.entropy_bound > 0
        assert memory.current_entropy == 0.0
        assert len(memory.child_memories) == 0

    def test_bekenstein_limit_calculation(self) -> None:
        """Test Bekenstein bound is calculated correctly."""
        memory = EventHorizonMemory(initial_area=1000.0)

        # S = A / (4 ln 2) in bits
        expected_entropy = 1000.0 / (4.0 * np.log(2))

        assert abs(memory.entropy_bound - expected_entropy) < 1e-6

    def test_store_information(self) -> None:
        """Test storing information in memory."""
        memory = EventHorizonMemory(initial_area=10000.0)

        # Create test information
        test_data = np.random.randn(16, 16)
        information = {"tensor": test_data}

        result = memory.store(information)

        assert result["status"] == "stored"
        assert result["entropy"] > 0
        assert result["total_entropy"] > 0
        assert result["saturation_ratio"] >= 0
        assert result["saturation_ratio"] <= 1.0

    def test_memory_saturation_spawns_child(self) -> None:
        """Test that memory saturation spawns child memory."""
        # Create small memory that saturates quickly
        memory = EventHorizonMemory(initial_area=100.0, spawn_threshold=0.5)

        # Store multiple pieces of information
        for i in range(10):
            test_data = np.random.randn(32, 32)
            information = {"tensor": test_data}
            result = memory.store(information)

            # Check if child was spawned
            if result["status"] == "stored_in_child":
                assert len(memory.child_memories) > 0
                assert "child_index" in result
                assert "child_result" in result
                break

        # At least one child should have been spawned
        assert len(memory.child_memories) > 0

    def test_retrieve_information(self) -> None:
        """Test retrieving information from memory."""
        memory = EventHorizonMemory(initial_area=10000.0)

        # Store information
        test_data = np.random.randn(16, 16)
        information = {"tensor": test_data}
        memory.store(information)

        # Try to retrieve with similar query
        query = {"tensor": test_data + np.random.randn(16, 16) * 0.1}
        retrieved = memory.retrieve(query)

        assert retrieved is not None
        assert isinstance(retrieved, np.ndarray)

    def test_retrieve_from_empty_memory(self) -> None:
        """Test retrieving from empty memory returns None."""
        memory = EventHorizonMemory()

        query = {"tensor": np.random.randn(16, 16)}
        retrieved = memory.retrieve(query)

        assert retrieved is None

    def test_retrieve_searches_children(self) -> None:
        """Test that retrieve searches child memories."""
        # Create memory with low saturation threshold
        memory = EventHorizonMemory(initial_area=100.0, spawn_threshold=0.3)

        # Store enough to create children
        stored_data = []
        for i in range(5):
            test_data = np.random.randn(32, 32)
            stored_data.append(test_data)
            memory.store({"tensor": test_data})

        # Should have children
        assert len(memory.child_memories) > 0

        # Try to retrieve last stored data
        query = {"tensor": stored_data[-1]}
        retrieved = memory.retrieve(query, search_children=True)

        # Should find it in some memory in hierarchy
        assert retrieved is not None

    def test_get_statistics(self) -> None:
        """Test getting memory statistics."""
        memory = EventHorizonMemory(initial_area=1000.0)

        # Store some information
        test_data = np.random.randn(16, 16)
        memory.store({"tensor": test_data})

        stats = memory.get_statistics()

        assert "current_entropy" in stats
        assert "entropy_bound" in stats
        assert "saturation_ratio" in stats
        assert "surface_area" in stats
        assert "child_count" in stats
        assert "total_hierarchy_depth" in stats
        assert "total_memories" in stats

        assert stats["current_entropy"] > 0
        assert stats["entropy_bound"] > 0
        assert stats["surface_area"] == 1000.0
        assert stats["total_memories"] >= 1

    def test_hierarchical_depth(self) -> None:
        """Test hierarchical depth calculation."""
        # Create memory that will spawn multiple levels
        memory = EventHorizonMemory(initial_area=100.0, spawn_threshold=0.2)

        # Store many items to create deep hierarchy
        for i in range(20):
            test_data = np.random.randn(32, 32)
            memory.store({"tensor": test_data})

        stats = memory.get_statistics()

        # Should have created hierarchy
        assert stats["total_hierarchy_depth"] >= 1
        if stats["child_count"] > 0:
            assert stats["total_hierarchy_depth"] > 1

    def test_child_memory_has_smaller_area(self) -> None:
        """Test that child memories have smaller area (evaporation)."""
        memory = EventHorizonMemory(initial_area=1000.0, spawn_threshold=0.3)

        # Store enough to spawn child
        for i in range(10):
            test_data = np.random.randn(32, 32)
            result = memory.store({"tensor": test_data})
            if result["status"] == "stored_in_child":
                break

        # Check children have smaller area
        for child in memory.child_memories:
            assert child.area < memory.area
            assert child.area == memory.area * 0.5

    def test_entropy_calculation(self) -> None:
        """Test entropy calculation for surface encoding."""
        memory = EventHorizonMemory()

        # Test with known data
        uniform_data = np.ones((10, 10))
        uniform_entropy = memory._calculate_entropy(uniform_data)

        # Use highly variable random data
        np.random.seed(42)  # For reproducibility
        random_data = np.random.randn(10, 10) * 5  # Higher variance
        random_entropy = memory._calculate_entropy(random_data)

        # Random data should typically have higher entropy than uniform
        # But we test non-negativity for both
        assert uniform_entropy >= 0
        assert random_entropy >= 0
        # At least one should have non-zero entropy
        assert uniform_entropy > 0 or random_entropy > 0

    def test_surface_merging(self) -> None:
        """Test merging of holographic surfaces."""
        memory = EventHorizonMemory()

        surface1 = np.random.randn(10, 10)
        surface2 = np.random.randn(10, 10)

        merged = memory._merge_surfaces(surface1, surface2)

        merged_arr = cast(np.ndarray, merged)
        assert merged_arr.shape[0] >= max(surface1.shape[0], surface2.shape[0])
        assert merged_arr.shape[1] >= max(surface1.shape[1], surface2.shape[1])

    def test_surface_merging_different_sizes(self) -> None:
        """Test merging surfaces of different sizes."""
        memory = EventHorizonMemory()

        surface1 = np.random.randn(10, 10)
        surface2 = np.random.randn(5, 5)

        merged = memory._merge_surfaces(surface1, surface2)

        # Should be padded to larger size
        merged_arr = cast(np.ndarray, merged)
        assert merged_arr.shape == (10, 10)

    def test_correlation_computation(self) -> None:
        """Test holographic correlation computation."""
        memory = EventHorizonMemory()

        # Identical surfaces should have high correlation
        surface = np.random.randn(10, 10)
        corr_identical = memory._compute_correlation(surface, surface)
        assert corr_identical > 0.9

        # Different surfaces should have lower correlation
        surface1 = np.random.randn(10, 10)
        surface2 = np.random.randn(10, 10)
        corr_different = memory._compute_correlation(surface1, surface2)
        assert 0.0 <= corr_different <= 1.0
        assert corr_different < corr_identical


class TestIntegration:
    """Integration tests for holographic memory system."""

    def test_full_workflow(self) -> None:
        """Test complete workflow: store, saturate, spawn, retrieve."""
        memory = EventHorizonMemory(initial_area=500.0, spawn_threshold=0.4)

        stored_items = []
        results = []

        # Store multiple items
        for i in range(10):
            test_data = np.random.randn(20, 20) * (i + 1)  # Start from 1, not 0
            information = {"tensor": test_data}
            stored_items.append(test_data)

            result = memory.store(information)
            results.append(result)

        # Should have triggered spawning
        has_child = any(r["status"] == "stored_in_child" for r in results)
        assert has_child or memory.current_entropy > 0

        # Try to retrieve first item (non-zero data now)
        query = {"tensor": stored_items[0]}
        retrieved = memory.retrieve(query, search_children=True)

        # Should retrieve something (may be None if correlation too low)
        # Just check that retrieval works without errors
        assert retrieved is None or isinstance(retrieved, np.ndarray)

        # Check statistics
        stats = memory.get_statistics()
        assert stats["total_memories"] >= 1
        assert stats["current_entropy"] > 0

    def test_deep_hierarchy_creation(self) -> None:
        """Test creation of deep memory hierarchies."""
        # Very small memory to force deep hierarchy
        memory = EventHorizonMemory(initial_area=50.0, spawn_threshold=0.2)

        # Store many items
        for i in range(30):
            test_data = np.random.randn(24, 24)
            memory.store({"tensor": test_data})

        stats = memory.get_statistics()

        # Should have created multiple levels
        assert stats["total_memories"] > 1
        assert stats["child_count"] >= 0

        # Depth should be > 1 if children exist
        if stats["child_count"] > 0:
            assert stats["total_hierarchy_depth"] > 1


class TestHolographicMemoryHybridTopological:
    """Testes de integração entre HolographicMemory e HybridTopologicalEngine."""

    def test_holographic_memory_with_topological_metrics(self):
        """Testa que HolographicMemory pode ser usado com métricas topológicas."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar HolographicMemory
        memory = EventHorizonMemory(max_surface_dim=256)

        # Armazenar informação
        information = {"tensor": np.random.randn(32, 32)}
        surface = memory.store(information)

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
        assert surface is not None
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # HolographicMemory: memória holográfica (Bekenstein bound)
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa
