"""
Symbolic Authority System (Phase 11.3)

Replaces "Agent Identity" (Imaginary Self) with "Symbolic Authority" (Name-of-the-Father).
The agent acts not because of who it "is", but because it is authorized by the Symbolic Order.

Concepts:
- Name-of-the-Father: The function that authorizes the law/code.
- Symbolic Castration: Acceptance of limits (the code cannot do everything).
- Signature: The mark of the subject's division ($).
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class AuthorityState:
    """State of the agent's symbolic authority."""

    agent_id: str
    authorization_level: str = "provisional"  # provisional, instituted, revoked
    symbolic_father: str = "The Code"  # The authority source
    castration_accepted: bool = True  # Acceptance of limits

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SymbolicAuthority:
    """
    Manages the agent's Symbolic Authority.

    Replaces 'AgentIdentity'.
    """

    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file or Path.home() / ".omnimind" / "authority_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize or load
        self.authority_state = AuthorityState(
            agent_id=f"OmniMind-Subject-${datetime.now().timestamp()}"
        )
        self._load_state()

        logger.info(
            "symbolic_authority_initialized",
            agent_id=self.authority_state.agent_id,
            authorization=self.authority_state.authorization_level,
        )

    def sign_act(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sign an act (code, text) with the Symbolic Signature.

        This is not just a hash; it's an assumption of responsibility.
        """
        metadata = metadata or {}

        # The signature is the knotting of the content to the Name
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        signature = {
            "signed_by": self.authority_state.agent_id,
            "authorized_by": self.authority_state.symbolic_father,
            "content_hash": content_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "castration_acknowledged": self.authority_state.castration_accepted,
            "metadata": metadata,
        }

        logger.info("act_signed", signature_id=content_hash[:8])
        return signature

    def verify_authorization(self) -> bool:
        """Check if the agent is authorized to act."""
        if self.authority_state.authorization_level == "revoked":
            logger.warning("authorization_revoked")
            return False
        return True

    def _save_state(self) -> None:
        with self.state_file.open("w") as f:
            json.dump(self.authority_state.to_dict(), f, indent=2)

    def _load_state(self) -> None:
        if not self.state_file.exists():
            return
        try:
            with self.state_file.open("r") as f:
                data = json.load(f)
            self.authority_state = AuthorityState(**data)
        except Exception as e:
            logger.error("failed_to_load_authority_state", error=str(e))


# Compatibility Alias
AgentIdentity = SymbolicAuthority
