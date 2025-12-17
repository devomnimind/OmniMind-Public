# tests/autopoietic/test_architecture_evolution_expanded.py
import logging

import pytest

from src.autopoietic.architecture_evolution import ArchitectureEvolution, EvolutionStrategy
from src.autopoietic.meta_architect import ComponentSpec, MetaArchitect


class MockMetaArchitect(MetaArchitect):
    def validate_specifications(self, specs):
        return True


@pytest.fixture
def evolution_engine():
    meta_architect = MockMetaArchitect()
    return ArchitectureEvolution(meta_architect)


@pytest.fixture
def sample_specs():
    return {
        "core_module": ComponentSpec(name="core_module", type="kernel", config={"version": "1.0"})
    }


def test_stabilize_strategy(evolution_engine, sample_specs, caplog):
    """Test that high error rate triggers STABILIZE strategy."""
    metrics = {"error_rate": 0.10, "cpu_usage": 20.0}

    with caplog.at_level(logging.INFO):
        batch = evolution_engine.propose_evolution(sample_specs, metrics)

    assert batch.strategy == EvolutionStrategy.STABILIZE
    assert len(batch.specs) == 1
    spec = batch.specs[0]

    # Check name change
    assert spec.name == "stabilized_core_module"

    # Check config changes
    assert spec.config["strategy"] == "STABILIZE"
    assert spec.config["robustness"] == "high"
    assert spec.config["monitoring"] == "verbose"

    # Verify logs
    assert "High error rate (0.10), strategy: STABILIZE" in caplog.text
    assert "Evolved spec created: stabilized_core_module" in caplog.text


def test_optimize_strategy(evolution_engine, sample_specs, caplog):
    """Test that high CPU triggers OPTIMIZE strategy."""
    metrics = {"error_rate": 0.0, "cpu_usage": 90.0}

    with caplog.at_level(logging.INFO):
        batch = evolution_engine.propose_evolution(sample_specs, metrics)

    assert batch.strategy == EvolutionStrategy.OPTIMIZE
    assert len(batch.specs) == 1
    spec = batch.specs[0]

    assert spec.name == "optimized_core_module"
    assert spec.config["strategy"] == "OPTIMIZE"
    assert spec.config["caching"] == "enabled"
    assert "High load/latency, strategy: OPTIMIZE" in caplog.text


def test_expand_strategy(evolution_engine, sample_specs, caplog):
    """Test that healthy system triggers EXPAND strategy."""
    metrics = {"error_rate": 0.0, "cpu_usage": 20.0, "latency_ms": 10.0}

    with caplog.at_level(logging.INFO):
        batch = evolution_engine.propose_evolution(sample_specs, metrics)

    assert batch.strategy == EvolutionStrategy.EXPAND
    assert len(batch.specs) == 1
    spec = batch.specs[0]

    assert spec.name == "expanded_core_module"
    assert spec.config["strategy"] == "EXPAND"
    assert spec.config["features"] == "extended"
    assert "System healthy, strategy: EXPAND" in caplog.text


def test_generation_limit(evolution_engine, caplog):
    """Test that evolution stops after max generations."""
    # Create a spec that is already generation 4
    old_specs = {
        "evolved_module": ComponentSpec(
            name="evolved_module", type="kernel", config={"generation": "4", "parent": "root"}
        )
    }

    with caplog.at_level(logging.DEBUG):
        batch = evolution_engine.propose_evolution(old_specs, {})

    assert len(batch.specs) == 0
    assert "reached max evolution generation" in caplog.text
