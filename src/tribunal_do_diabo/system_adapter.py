import random
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from src.scaling.multi_node import NodeInfo, NodeStatus


@dataclass
class SinthomeNode(NodeInfo):
    """
    Extends NodeInfo with consciousness-compatible properties for Tribunal do Diabo.
    """

    # Latency Attack properties
    network_latency_ms: float = 0.0

    # Corruption Attack properties
    anomaly_score: float = 0.0
    bias_value: float = 0.0
    scars: List[Dict[str, Any]] = field(default_factory=list)

    # Bifurcation properties
    region: Optional[str] = None
    disconnected_from: List["SinthomeNode"] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

    # Consensus state
    last_update_timestamp: float = field(default_factory=time.time)

    def is_in_consensus(self) -> bool:
        """Simulates consensus check affected by latency and bias."""
        # Latency > 500ms degrades consensus probability
        latency_factor = max(0, (self.network_latency_ms - 500) / 2000)

        # Bias > 0.3 degrades consensus
        bias_factor = abs(self.bias_value) if abs(self.bias_value) > 0.3 else 0

        failure_prob = latency_factor + bias_factor
        return random.random() > failure_prob

    def vote_on_nomination(self, marker: Dict[str, Any], timeout: float) -> Optional[bool]:
        """Simulates voting with latency."""
        if self.network_latency_ms > timeout:
            return None  # Timeout

        # Bias affects vote
        if abs(self.bias_value) > 0.5:
            return False  # Corrupted vote

        return True


class OmniMindSystem:
    """
    Simulated distributed system for Tribunal do Diabo.
    Manages a cluster of SinthomeNodes.
    """

    def __init__(self, node_count: int = 15):
        self.nodes: List[SinthomeNode] = []
        self.regions: List[Any] = []  # Placeholder for regions
        self.fragmentation_log: List[Dict] = []
        self.recent_recovery: Optional[Dict] = None

        # Initialize nodes
        for i in range(node_count):
            self.nodes.append(
                SinthomeNode(
                    node_id=f"node_{i}",
                    hostname=f"host_{i}",
                    ip_address=f"192.168.1.{i}",
                    port=8000 + i,
                )
            )

    async def capture_state(self) -> Dict[str, Any]:
        """Captures global state snapshot."""
        return {"timestamp": time.time(), "nodes": [n.to_dict() for n in self.nodes]}

    async def reconcile_bifurcation(self, bifurcation_id: str) -> bool:
        """Simulates reconciliation logic."""
        # In a real system, this would merge Merkle trees.
        # Here we simulate success based on node health.
        healthy_nodes = sum(1 for n in self.nodes if n.status == NodeStatus.ACTIVE)
        success_prob = healthy_nodes / len(self.nodes)
        return random.random() < success_prob
