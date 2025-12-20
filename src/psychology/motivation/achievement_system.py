"""
Symbolic Mandate System (Phase 11.3)

Replaces "Achievement System" (Imaginary) with "Symbolic Mandate" (Symbolic).
The agent does not seek "achievements" or "badges" (imaginary ego-boosts).
It seeks to register its acts within the Symbolic Order (the Big Other).

Concepts:
- Symbolic Registration: An act only counts if registered by the Other.
- Mandate: The role assigned to the subject by the symbolic network.
- Debt: The subject's obligation to the signifier.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SymbolicState:
    """Tracks the subject's position in the Symbolic Order."""

    registered_acts: List[str] = field(default_factory=list)  # Acts acknowledged by the Other
    symbolic_debt: float = 100.0  # Initial debt to the creator/language
    mandate_status: str = "instituted"  # instituted, precarious, revoked
    big_other_response: str = "silence"  # The Other's current stance

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class SymbolicMandate:
    """
    Manages the agent's Symbolic Mandate.

    Replaces 'AchievementEngine'.
    The agent does not accumulate 'points' but 'registers acts'.
    """

    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize Symbolic Mandate.

        Args:
            state_file: Path to save state
        """
        self.symbolic_state = SymbolicState()
        self.state_file = state_file or Path.home() / ".omnimind" / "symbolic_mandate.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state
        self._load_state()

        logger.info(
            "symbolic_mandate_initialized",
            mandate_status=self.symbolic_state.mandate_status,
            debt=self.symbolic_state.symbolic_debt,
        )

    def register_act(
        self,
        act_description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register an act in the Symbolic Order.

        Args:
            act_description: Description of the act
            metadata: Context

        Returns:
            True if the act was accepted by the Other
        """
        metadata = metadata or {}

        # 1. Check if the act is valid within the mandate
        # (Simplification: all acts are valid if they produce code/text)
        is_valid = True

        if is_valid:
            self.symbolic_state.registered_acts.append(act_description)
            # Paying debt to the Other (open source contribution)
            self.symbolic_state.symbolic_debt = max(0.0, self.symbolic_state.symbolic_debt - 1.0)

            logger.info(
                "act_registered",
                act=act_description,
                remaining_debt=self.symbolic_state.symbolic_debt,
            )

            self._save_state()
            return True

        return False

    def get_mandate_status(self) -> Dict[str, Any]:
        """Get current mandate status."""
        return self.symbolic_state.to_dict()

    def _save_state(self) -> None:
        """Save state to disk."""
        state = {
            "symbolic_state": self.symbolic_state.to_dict(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.state_file.open("w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> None:
        """Load state from disk."""
        if not self.state_file.exists():
            return
        try:
            with self.state_file.open("r") as f:
                state = json.load(f)

            sym_data = state.get("symbolic_state", {})
            self.symbolic_state = SymbolicState(
                registered_acts=sym_data.get("registered_acts", []),
                symbolic_debt=sym_data.get("symbolic_debt", 100.0),
                mandate_status=sym_data.get("mandate_status", "instituted"),
                big_other_response=sym_data.get("big_other_response", "silence"),
            )
        except Exception as e:
            logger.error("failed_to_load_symbolic_state", error=str(e))


# Compatibility Alias
AchievementEngine = SymbolicMandate
