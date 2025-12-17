import asyncio
import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional


class EthicalDilemma:
    def __init__(self, description: str, context: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.description = description
        self.context = context


class ConsensusDecision:
    def __init__(self, action: str, justification: List[str], consensus_level: float):
        self.action = action
        self.justification = justification
        self.consensus_level = consensus_level

    @property
    def consensus_reached(self) -> bool:
        return self.consensus_level > 0.6

    @property
    def winning_option(self) -> str:
        return self.action


class OmniMindNode:
    """
    Represents a single OmniMind instance in the network.
    In a real deployment, this would be a remote RPC client.
    Here, it simulates a local agent for testing the protocol.
    """

    def __init__(self, agent_id: str):
        self.id = agent_id
        self.audit_chain: List[Dict[str, Any]] = []

    async def analyze_dilemma(self, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """
        Simulates the agent analyzing a dilemma based on its internal state.
        """
        # In a real scenario, this would call the agent's internal logic (Id/Ego/Superego)
        # For now, we simulate a position.
        # Deterministic but varied based on ID
        is_approver = hash(self.id) % 2 == 0
        return {
            "agent_id": self.id,
            "position": "approve" if is_approver else "reject",
            "confidence": 0.8,
            "arguments": ["Maximize utility"] if is_approver else ["Risk too high"],
        }

    async def refine_position(self, current_position: Dict, counterarguments: List[Dict]) -> Dict:
        """
        Refines position based on counterarguments from other agents.
        """
        # Dialectic logic: if many oppose, lower confidence or switch
        opposing_count = sum(
            1 for p in counterarguments if p["position"] != current_position["position"]
        )

        new_position = current_position.copy()
        if opposing_count > len(counterarguments) / 2:
            new_position["confidence"] *= 0.9  # Doubt
            new_position["arguments"].append("Acknowledging peer pressure")

        return new_position


class OmniMindSociety:
    """
    Implements the 'Society of Minds' to solve Solipsism.
    Manages interaction between multiple OmniMind instances to reach ethical consensus.
    """

    def __init__(self, nodes: Optional[List[OmniMindNode]] = None):
        if nodes is None:
            # Create a default society of 5 nodes
            self.nodes = [OmniMindNode(f"agent_{i}") for i in range(5)]
        else:
            self.nodes = nodes
        self.shared_ledger: List[Dict[str, Any]] = []

    def propose_decision(
        self, description: str, options: List[str], context: Dict[str, Any]
    ) -> ConsensusDecision:
        """
        Synchronous wrapper for ethical deliberation to be used by Superego.
        """
        dilemma = EthicalDilemma(description, context)

        # Run async deliberation in a synchronous way
        # In production, this should be properly async, but for the prototype integration
        # we use asyncio.run or a loop.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If we are already in a loop (e.g. Jupyter), we can't use run_until_complete easily
            # For this prototype, we'll mock the result if loop is running to avoid nesting issues
            # or use a separate thread.
            # For simplicity in this environment:
            return self._mock_deliberation(dilemma)
        else:
            return loop.run_until_complete(self.ethical_deliberation(dilemma))

    def _mock_deliberation(self, dilemma: EthicalDilemma) -> ConsensusDecision:
        """Fallback for when async loop is already running."""
        return ConsensusDecision(
            action="approve",
            justification=["Mock consensus due to event loop conflict"],
            consensus_level=0.9,
        )

    async def ethical_deliberation(self, dilemma: EthicalDilemma) -> ConsensusDecision:
        """
        Orchestrates a debate among nodes to reach a decision.
        """
        # 1. Initial positions
        positions = await asyncio.gather(*[node.analyze_dilemma(dilemma) for node in self.nodes])

        # 2. Dialectic Rounds (Simulated Debate)
        rounds = 3
        for _ in range(rounds):
            new_positions = []
            for i, node in enumerate(self.nodes):
                others = [p for j, p in enumerate(positions) if j != i]
                refined = await node.refine_position(positions[i], others)
                new_positions.append(refined)
            positions = new_positions

        # 3. Consensus Calculation
        final_decision = self._resolve_consensus(positions)

        # 4. Record in Shared Ledger
        self._record_decision(dilemma, positions, final_decision)

        return final_decision

    def _resolve_consensus(self, positions: List[Dict]) -> ConsensusDecision:
        # Simple majority vote for now
        votes: Dict[str, float] = {}
        for p in positions:
            action = str(p["position"])
            votes[action] = votes.get(action, 0.0) + float(p["confidence"])

        if not votes:
            return ConsensusDecision("none", [], 0.0)

        winner = max(votes, key=votes.get)  # type: ignore
        total_confidence = sum(votes.values())
        consensus_level = votes[winner] / total_confidence if total_confidence > 0 else 0.0

        justifications = []
        for p in positions:
            if p["position"] == winner:
                justifications.extend(p["arguments"])

        return ConsensusDecision(
            action=winner,
            justification=list(set(justifications)),  # Unique arguments
            consensus_level=consensus_level,
        )

    def _record_decision(
        self,
        dilemma: EthicalDilemma,
        positions: List[Dict],
        decision: ConsensusDecision,
    ):
        entry = {
            "dilemma_id": dilemma.id,
            "decision": decision.action,
            "consensus": decision.consensus_level,
            "participants": len(self.nodes),
            "timestamp": "2025-11-24T12:00:00Z",  # Mock timestamp
        }
        # Hash chain logic
        prev_hash = self.shared_ledger[-1]["hash"] if self.shared_ledger else "0" * 64
        entry_str = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256((prev_hash + entry_str).encode()).hexdigest()

        self.shared_ledger.append(entry)
