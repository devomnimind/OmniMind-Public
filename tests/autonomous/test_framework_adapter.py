"""Tests for Dynamic Framework Adapter - Phase 26C"""

from __future__ import annotations

from autonomous.dynamic_framework_adapter import DynamicFrameworkAdapter, MachineSpecs


class TestDynamicFrameworkAdapter:
    """Test Dynamic Framework Adapter"""

    def test_init(self):
        """Test initialization"""
        adapter = DynamicFrameworkAdapter()
        assert adapter is not None
        assert adapter.machine_config is not None

    def test_detect_machine_specs(self):
        """Test machine specs detection"""
        adapter = DynamicFrameworkAdapter()
        specs = adapter.detect_machine_specs()

        assert isinstance(specs, MachineSpecs)
        assert specs.cpu_count > 0
        assert specs.memory_gb > 0
        assert specs.platform in ["Linux", "Windows", "Darwin"]

    def test_adapt_low_memory(self):
        """Test adaptation for low memory machine"""
        adapter = DynamicFrameworkAdapter()

        # Mock low memory
        adapter.machine_config.memory_gb = 4.0

        solution = {
            "solution": {
                "batch_size": 32,
                "model_size": "medium",
            },
            "confidence": 0.8,
        }

        adapted = adapter.adapt_to_environment(solution)

        assert adapted["model_size"] == "small"
        assert adapted["batch_size"] == 4
        assert adapted["cache_enabled"] is False

    def test_adapt_multi_gpu(self):
        """Test adaptation for multi-GPU machine"""
        adapter = DynamicFrameworkAdapter()

        # Mock multi-GPU
        adapter.machine_config.gpu_count = 2

        solution = {
            "solution": {
                "batch_size": 32,
            },
            "confidence": 0.8,
        }

        adapted = adapter.adapt_to_environment(solution)

        assert adapted["parallel_strategy"] == "multi_gpu"
        assert adapted["distributed"] is True
        assert adapted["batch_size"] >= 32  # Should be increased

    def test_adapt_cpu_only(self):
        """Test adaptation for CPU-only machine"""
        adapter = DynamicFrameworkAdapter()

        # Mock CPU-only
        adapter.machine_config.gpu_count = 0

        solution = {
            "solution": {
                "batch_size": 32,
                "use_gpu": True,
            },
            "confidence": 0.8,
        }

        adapted = adapter.adapt_to_environment(solution)

        assert adapted["use_gpu"] is False
        assert adapted["use_cpu_optimization"] is True
        assert adapted["batch_size"] <= 4

    def test_apply_adaptation(self):
        """Test applying adaptation"""
        adapter = DynamicFrameworkAdapter()

        adapted = {
            "batch_size": 16,
            "model_size": "small",
        }

        result = adapter.apply_adaptation(adapted)

        assert result["batch_size"] == 16
        assert result["model_size"] == "small"
