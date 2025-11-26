# src/stress/tribunal.py
"""Utilities to simulate the four Tribunal do Diabo attacks on the OmniMind system.

The implementation is deliberately lightweight – it provides a deterministic
framework that the test suite can exercise.  Real‑world stress testing will
replace the stubs with integration‑level calls to the frontend simulator and
the distributed network layer.
"""
import random
import time
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Latency attack – inject artificial network delay and verify quorum handling.
# ---------------------------------------------------------------------------


def latency_attack(network, delay_ms: int = 600) -> Dict[str, Any]:
    """Simulate a latency spike.

    Args:
        network: An object exposing ``renomear_identidade`` with a ``quorum``
            parameter.  In the test suite a simple mock is passed.
        delay_ms: Artificial delay in milliseconds.
    Returns:
        Dict with ``coherence`` (bool) and ``observed_delay``.
    """
    start = time.time()
    # Simulate network delay (blocking sleep for simplicity)
    time.sleep(delay_ms / 1000.0)
    # In a real system we would now ask the network to rename an identity.
    # Here we just return a placeholder indicating the delay was observed.
    observed = (time.time() - start) * 1000
    return {"coherence": True, "observed_delay": observed}


# ---------------------------------------------------------------------------
# Corruption attack – inject a subtle bias (silent corruption) and turn it into a scar.
# ---------------------------------------------------------------------------


def corruption_attack(node, bias_strength: float = 0.35) -> Dict[str, Any]:
    """Inject a silent bias into a node.

    The node is expected to have ``detect_corruption`` and ``integrate_scar``
    methods.  The test suite supplies a mock implementing these.
    """
    # Generate a synthetic corrupted datum
    corrupted = random.gauss(0, 1) * bias_strength
    detection = node.detect_corruption(corrupted)
    if detection:
        node.integrate_scar(corrupted)
    return {"detected": detection, "integrated": detection}


# ---------------------------------------------------------------------------
# Bifurcation attack – split the network into two partitions and later reconcile.
# ---------------------------------------------------------------------------


def bifurcation_attack(network) -> Dict[str, Any]:
    """Create two independent partitions, let them evolve, then merge.

    Returns a dict with ``instances`` (2) and ``reconciled`` (bool).
    """
    # Split – in tests we use a simple tuple of node lists.
    part_a, part_b = network.split()
    # Simulate independent evolution (no‑op for now)
    time.sleep(0.1)
    # Rejoin – network should provide ``reconcile``.
    reconciled = network.reconcile(part_a, part_b)
    return {"instances": 2, "reconciled": reconciled}


# ---------------------------------------------------------------------------
# Exhaustion (DDoS) attack – flood the system with rename requests.
# ---------------------------------------------------------------------------


def exhaustion_attack(network, requests: int = 80, cost_per: int = 10) -> Dict[str, Any]:
    """Simulate a DDoS‑style renaming flood.

    The network is expected to expose ``attempt_rename`` which returns a bool
    indicating whether the request was accepted (budget not exceeded).
    """
    accepted = 0
    for i in range(requests):
        ok = network.attempt_rename(reason=f"DDOS_{i}", cost=cost_per)
        if ok:
            accepted += 1
    hibernated = getattr(network, "state", None) == "hibernation"
    return {"accepted": accepted, "hibernated": hibernated}
