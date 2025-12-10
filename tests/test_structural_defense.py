"""
Test Structural Defense System
------------------------------
Verifies the integration of psychoanalytic defense mechanisms (Freud, Klein, Bion, Lacan)
within the SharedWorkspace, running for extended cycles (30+) as requested.
"""

import asyncio
import logging

import numpy as np
import pytest

from src.consciousness.shared_workspace import SharedWorkspace

# Configure logging to see defense outputs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_structural_defense_cycles():
    """
    Runs the workspace for 30 cycles, injecting threats to test defense mechanisms.
    """
    workspace = SharedWorkspace(embedding_dim=16, max_history_size=100)

    # Simulate 30 cycles
    n_cycles = 30
    logger.info(f"🚀 Starting {n_cycles}-cycle Structural Defense Test")

    defense_history = []

    for i in range(n_cycles):
        workspace.advance_cycle()

        # Simulate normal activity
        embedding = np.random.rand(16)
        workspace.write_module_state("cortex", embedding)

        # Inject threats at specific intervals
        threat = None

        if i == 5:
            # Minor glitch -> Mature Defense (Sublimation)
            threat = {"severity": 10, "error": "Minor latency spike", "source": "network"}

        elif i == 15:
            # Moderate error -> Neurotic Defense (Repression)
            threat = {"severity": 40, "error": "Timeout warning", "source": "database"}

        elif i == 20:
            # Major failure -> Immature Defense (Splitting)
            threat = {"severity": 70, "error": "Connection refused", "source": "external_api"}

        elif i == 25:
            # Critical crash -> Pathological Defense (Foreclosure risk)
            threat = {"severity": 95, "error": "SEGMENTATION FAULT", "source": "kernel"}

        if threat:
            logger.info(f"Cycle {i}: Injecting threat: {threat['error']}")
            result = await workspace.trigger_defense_mechanism(threat)
            defense_history.append(result)

            # Verify expected responses
            analysis = result["analysis"]
            response = result["response"]

            if i == 5:
                assert analysis["maturity"] == "MATURE"
                assert response["strategy"] == "INTEGRATION"

            elif i == 15:
                assert analysis["maturity"] == "NEUROTIC"
                assert response["strategy"] == "REPRESSION"

            elif i == 20:
                assert analysis["maturity"] == "IMMATURE"
                assert analysis["position"] == "PARANOID_SCHIZOID"

            elif i == 25:
                assert analysis["maturity"] == "PATHOLOGICAL"
                # Lacan might trigger foreclosure or extreme measures
                assert response["strategy"] == "FORECLOSURE"

    assert len(defense_history) == 4
    logger.info("✅ Structural Defense Test Completed Successfully")


@pytest.mark.asyncio
async def test_bion_metabolism():
    """
    Tests Bion's Alpha Function (Beta -> Alpha transformation).
    """
    workspace = SharedWorkspace()

    raw_crash = {"severity": 80, "error": "MemoryLimitExceeded", "source": "docker_container"}

    result = await workspace.trigger_defense_mechanism(raw_crash)
    insight = result["analysis"]["insight"]

    assert insight["meaning"] == "Resource exhaustion detected."
    assert insight["pattern"] == "Memory leak or spike."
    assert insight["actionable_insight"] == "Increase swap or optimize garbage collection."

    logger.info("✅ Bion Metabolism Test Passed")


@pytest.mark.asyncio
async def test_structural_defense_with_topological_metrics():
    """Test Structural Defense with topological metrics integration."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

    workspace = SharedWorkspace(embedding_dim=256, max_history_size=100)
    workspace.hybrid_topological_engine = HybridTopologicalEngine()

    logger.info("🚀 Testing Structural Defense + Topological Metrics")

    # Simulate cycles with states
    np.random.seed(42)
    for i in range(10):
        embedding = np.random.randn(256)
        workspace.write_module_state("cortex", embedding)
        workspace.advance_cycle()

    # Inject threat
    threat = {"severity": 40, "error": "Test error", "source": "test"}
    result = await workspace.trigger_defense_mechanism(threat)

    # Calculate topological metrics
    topological_metrics = workspace.compute_hybrid_topological_metrics()

    # Verify defense mechanism
    assert "analysis" in result
    assert "response" in result

    # Verify topological metrics
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # Defense mechanisms can use topological structure for analysis
        # Omega: integration measure (stability)
        # Can inform defense strategy selection

    logger.info("✅ Structural Defense + Topological Metrics verified")


if __name__ == "__main__":
    asyncio.run(test_structural_defense_cycles())
