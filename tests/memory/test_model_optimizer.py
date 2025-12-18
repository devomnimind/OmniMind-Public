"""
Testes para ModelOptimizer e ModelRouter.

Autor: Fabrício da Silva + assistência de IA
"""

from unittest.mock import MagicMock

import pytest

from src.memory.model_optimizer import (
    ModelOptimizer,
    ModelPrecision,
    ModelRouter,
)


class TestModelOptimizer:
    """Testes para ModelOptimizer."""

    def test_init(self):
        """Testa inicialização."""
        optimizer = ModelOptimizer()
        assert optimizer.default_precision == ModelPrecision.FP32
        assert optimizer.enable_kv_cache is True
        assert optimizer.kv_cache_size == 512

    def test_get_set_kv_cache(self):
        """Testa get/set de KV cache."""
        optimizer = ModelOptimizer()
        model_name = "test_model"
        cache_key = "test_key"
        cache_value = {"keys": [1, 2, 3], "values": [4, 5, 6]}

        # Set cache
        optimizer.set_kv_cache(model_name, cache_key, cache_value)

        # Get cache
        retrieved = optimizer.get_kv_cache(model_name, cache_key)
        assert retrieved == cache_value

        # Get non-existent
        assert optimizer.get_kv_cache(model_name, "nonexistent") is None

    def test_clear_kv_cache(self):
        """Testa limpeza de KV cache."""
        optimizer = ModelOptimizer()
        optimizer.set_kv_cache("model1", "key1", {"test": "data"})
        optimizer.set_kv_cache("model2", "key2", {"test": "data"})

        # Clear specific model
        optimizer.clear_kv_cache("model1")
        assert optimizer.get_kv_cache("model1", "key1") is None
        assert optimizer.get_kv_cache("model2", "key2") is not None

        # Clear all
        optimizer.clear_kv_cache()
        assert optimizer.get_kv_cache("model2", "key2") is None

    def test_get_model_stats(self):
        """Testa obtenção de estatísticas."""
        optimizer = ModelOptimizer()
        stats = optimizer.get_model_stats()

        assert "total_models" in stats
        assert "total_caches" in stats
        assert "models" in stats

    @pytest.mark.skipif(True, reason="Requires PyTorch and actual model")
    def test_quantize_model_int8(self):
        """Testa quantização INT8 (requer PyTorch e modelo real)."""
        # Test would require actual PyTorch model

    def test_optimize_embedding_model(self):
        """Testa otimização de modelo de embeddings."""
        optimizer = ModelOptimizer()

        # Mock model
        mock_model = MagicMock()
        mock_model.encode = MagicMock(return_value=[[0.1, 0.2, 0.3]])

        # Optimize
        optimized = optimizer.optimize_embedding_model(
            model_name="test_model",
            model=mock_model,
            precision=ModelPrecision.FP32,
            use_kv_cache=True,
        )

        assert optimized is not None
        assert "test_model" in optimizer.model_configs


class TestModelRouter:
    """Testes para ModelRouter."""

    def test_init(self):
        """Testa inicialização."""
        optimizer = ModelOptimizer()
        router = ModelRouter(optimizer)
        assert router.optimizer == optimizer

    def test_should_use_fast_path(self):
        """Testa decisão de fast path."""
        optimizer = ModelOptimizer()
        router = ModelRouter(optimizer)

        # Simple task, short query
        assert router.should_use_fast_path("simple", 50) is True

        # Complex task
        assert router.should_use_fast_path("complex", 50) is False

        # Requires high precision
        assert router.should_use_fast_path("simple", 50, requires_high_precision=True) is False

    def test_route_embedding(self):
        """Testa roteamento de embedding."""
        optimizer = ModelOptimizer()
        router = ModelRouter(optimizer)

        # Mock models
        fast_model = MagicMock()
        fast_model.encode = MagicMock(return_value=[[0.1, 0.2, 0.3]])

        slow_model = MagicMock()
        slow_model.encode = MagicMock(return_value=[[0.4, 0.5, 0.6]])

        # Route simple task
        result = router.route_embedding(
            model_name="test",
            fast_model=fast_model,
            slow_model=slow_model,
            text="short text",
            task_complexity="simple",
        )

        assert result is not None
        assert router.routing_stats["fast_path"] > 0 or router.routing_stats["slow_path"] > 0

    def test_get_routing_stats(self):
        """Testa obtenção de estatísticas de roteamento."""
        optimizer = ModelOptimizer()
        router = ModelRouter(optimizer)

        router.routing_stats["fast_path"] = 10
        router.routing_stats["slow_path"] = 5

        stats = router.get_routing_stats()

        assert stats["fast_path_count"] == 10
        assert stats["slow_path_count"] == 5
        assert stats["total_requests"] == 15
        assert "fast_path_percentage" in stats
        assert "slow_path_percentage" in stats
