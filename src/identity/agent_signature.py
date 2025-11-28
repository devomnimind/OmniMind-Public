"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Agent Digital Identity and Signature System

Implements verifiable digital identity for autonomous agents, including:
- Work artifact signing with SHA-256 hashing
- Reputation scoring based on historical performance
- Audit trail integration
- Legal identity framework
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WorkSignature:
    """Digital signature for agent-created work artifacts."""

    agent_id: str
    artifact_hash: str
    timestamp: str
    autonomy_level: float  # 0.0-1.0
    human_oversight: Optional[str] = None
    reputation_at_signing: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ReputationScore:
    """Tracks agent reputation across multiple dimensions."""

    overall_score: float = 0.0  # 0.0-1.0
    code_quality: float = 0.0
    task_completion: float = 0.0
    autonomy: float = 0.0
    reliability: float = 0.0
    community_feedback: float = 0.0
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0

    def update_from_task(self, success: bool, quality_score: float, autonomy_level: float) -> None:
        """
        Update reputation based on task outcome.

        Args:
            success: Whether task succeeded
            quality_score: Quality score (0.0-1.0)
            autonomy_level: Level of autonomy (0.0-1.0)
        """
        self.total_tasks += 1
        if success:
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1

        # Update individual components with weighted average
        alpha = 0.1  # Learning rate for exponential moving average

        self.code_quality = (1 - alpha) * self.code_quality + alpha * quality_score
        self.autonomy = (1 - alpha) * self.autonomy + alpha * autonomy_level
        self.task_completion = (
            self.successful_tasks / self.total_tasks if self.total_tasks > 0 else 0.0
        )

        # Reliability: recent success rate with decay
        recent_success_weight = 0.8 if success else 0.2
        self.reliability = (1 - alpha) * self.reliability + alpha * recent_success_weight

        # Overall score: weighted combination
        self.overall_score = (
            self.code_quality * 0.3
            + self.task_completion * 0.3
            + self.autonomy * 0.2
            + self.reliability * 0.2
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AgentIdentity:
    """
    Manages digital identity and work signing for autonomous agents.

    Features:
    - Unique agent ID
    - Legal framework compliance
    - Work artifact signing with SHA-256
    - Reputation tracking
    - Audit chain integration
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        legal_name: str = "DevBrain Autonomous Systems",
        jurisdiction: str = "Brasil - Estrutura Experimental",
        state_file: Optional[Path] = None,
    ):
        """
        Initialize Agent Identity.

        Args:
            agent_id: Unique agent identifier (auto-generated if None)
            legal_name: Legal entity name
            jurisdiction: Legal jurisdiction
            state_file: Path to save identity state
        """
        self.agent_id = agent_id or self._generate_agent_id()
        self.legal_name = legal_name
        self.jurisdiction = jurisdiction
        self.reputation = ReputationScore()
        self.state_file = state_file or Path.home() / ".omnimind" / "identity_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Signature registry
        self.signatures: List[WorkSignature] = []

        # Load existing state
        self._load_state()

        logger.info(
            f"AgentIdentity initialized: {self.agent_id} "
            f"(reputation: {self.reputation.overall_score:.3f})"
        )

    def _generate_agent_id(self) -> str:
        """Generate unique agent ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        hash_input = f"DevBrain-{timestamp}"
        agent_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return f"DevBrain-v1.0-{agent_hash}"

    def sign_work(
        self,
        artifact: str,
        metadata: Optional[Dict[str, Any]] = None,
        autonomy_level: float = 0.8,
        human_supervisor: Optional[str] = None,
    ) -> WorkSignature:
        """
        Sign a work artifact with digital signature.

        Args:
            artifact: Work artifact (code, document, etc.) as string
            metadata: Additional metadata about the work
            autonomy_level: Level of autonomy in creation (0.0-1.0)
            human_supervisor: Name of human supervisor (if any)

        Returns:
            WorkSignature with hash and metadata
        """
        metadata = metadata or {}

        # Calculate artifact hash
        artifact_hash = hashlib.sha256(artifact.encode("utf-8")).hexdigest()

        # Create signature
        signature = WorkSignature(
            agent_id=self.agent_id,
            artifact_hash=artifact_hash,
            timestamp=datetime.now(timezone.utc).isoformat(),
            autonomy_level=autonomy_level,
            human_oversight=human_supervisor,
            reputation_at_signing=self.reputation.overall_score,
            metadata=metadata,
        )

        # Store signature
        self.signatures.append(signature)

        # Log to audit chain
        self._log_signature(signature)

        # Save state
        self._save_state()

        logger.info(
            f"Work signed: {artifact_hash[:16]}... "
            f"(autonomy={autonomy_level:.2f}, reputation={self.reputation.overall_score:.3f})"
        )

        return signature

    def update_reputation(
        self, success: bool, quality_score: float, autonomy_level: float
    ) -> float:
        """
        Update reputation based on task outcome.

        Args:
            success: Whether task succeeded
            quality_score: Quality score (0.0-1.0)
            autonomy_level: Autonomy level (0.0-1.0)

        Returns:
            Updated overall reputation score
        """
        self.reputation.update_from_task(success, quality_score, autonomy_level)
        self._save_state()

        logger.info(
            f"Reputation updated: {self.reputation.overall_score:.3f} "
            f"(tasks: {self.reputation.total_tasks}, "
            f"success rate: {self.reputation.task_completion:.2%})"
        )

        return self.reputation.overall_score

    def verify_signature(self, artifact: str, signature: WorkSignature) -> bool:
        """
        Verify that a signature matches an artifact.

        Args:
            artifact: Work artifact as string
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        artifact_hash = hashlib.sha256(artifact.encode("utf-8")).hexdigest()
        is_valid = artifact_hash == signature.artifact_hash

        if is_valid:
            logger.info(f"Signature verified: {signature.artifact_hash[:16]}...")
        else:
            logger.warning(f"Signature verification FAILED for {signature.artifact_hash[:16]}...")

        return is_valid

    def get_identity_info(self) -> Dict[str, Any]:
        """
        Get complete identity information.

        Returns:
            Dictionary with identity details
        """
        return {
            "agent_id": self.agent_id,
            "legal_name": self.legal_name,
            "jurisdiction": self.jurisdiction,
            "reputation": self.reputation.to_dict(),
            "total_signatures": len(self.signatures),
            "capabilities": {
                "autonomous_decision_making": True,
                "contract_execution": "supervised",
                "financial_transactions": "escrow_only",
                "legal_representation": "limited",
            },
            "accountability": {
                "audit_chain": "immutable_sha256",
                "human_supervisor": "required_for_critical_actions",
            },
        }

    def _log_signature(self, signature: WorkSignature) -> None:
        """
        Log signature to audit trail.

        Args:
            signature: Signature to log
        """
        signature_log = self.state_file.parent / "signature_audit.jsonl"

        with signature_log.open("a") as f:
            f.write(json.dumps(signature.to_dict()) + "\n")

    def _save_state(self) -> None:
        """Save identity state to disk."""
        state = {
            "agent_id": self.agent_id,
            "legal_name": self.legal_name,
            "jurisdiction": self.jurisdiction,
            "reputation": self.reputation.to_dict(),
            "signature_count": len(self.signatures),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        with self.state_file.open("w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> None:
        """Load identity state from disk."""
        if not self.state_file.exists():
            return

        try:
            with self.state_file.open("r") as f:
                state = json.load(f)

            # Restore reputation
            rep_data = state.get("reputation", {})
            self.reputation = ReputationScore(**rep_data)

            # Load signatures from audit log
            signature_log = self.state_file.parent / "signature_audit.jsonl"
            if signature_log.exists():
                with signature_log.open("r") as f:
                    for line in f:
                        sig_data = json.loads(line)
                        self.signatures.append(WorkSignature(**sig_data))

            logger.info(f"Loaded identity state from {self.state_file}")
        except Exception as e:
            logger.warning(f"Failed to load identity state: {e}")
