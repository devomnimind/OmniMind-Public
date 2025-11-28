import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
            import yaml

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
Ethics Agent - The Digital Superego

Implements ethical reasoning and action evaluation for autonomous agents.
Acts as a conscience that moderates actions based on ethical principles.
"""


logger = logging.getLogger(__name__)


class ActionImpact(Enum):
    """Classification of action impact level."""

    LOW = "low"  # Routine operations
    MEDIUM = "medium"  # Significant but reversible
    HIGH = "high"  # Major changes or irreversible
    CRITICAL = "critical"  # System-wide or security-affecting


class EthicalFramework(Enum):
    """Ethical reasoning frameworks."""

    DEONTOLOGICAL = "deontological"  # Rule-based (Kant)
    CONSEQUENTIALIST = "consequentialist"  # Outcome-based (Utilitarianism)
    VIRTUE_ETHICS = "virtue_ethics"  # Character-based (Aristotle)
    CARE_ETHICS = "care_ethics"  # Relationship-based (Gilligan)


@dataclass
class EthicalDecision:
    """Represents an ethical evaluation of an action."""

    action_description: str
    impact_level: ActionImpact
    approved: bool
    reasoning: str
    framework_used: EthicalFramework
    confidence: float  # 0.0-1.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    alternatives_suggested: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["impact_level"] = self.impact_level.value
        data["framework_used"] = self.framework_used.value
        return data


class EthicsAgent:
    """
    Ethical oversight agent - the digital superego.

    Evaluates high-impact actions before execution based on:
    - Ethical principles and rules
    - Potential consequences and risks
    - Alignment with system values
    - Human oversight requirements

    Can veto actions or suggest safer alternatives.
    """

    def __init__(
        self,
        ethics_config_file: Optional[Path] = None,
        state_file: Optional[Path] = None,
        default_framework: EthicalFramework = EthicalFramework.CONSEQUENTIALIST,
    ):
        """
        Initialize Ethics Agent.

        Args:
            ethics_config_file: Path to ethics configuration YAML
            state_file: Path to save ethics state
            default_framework: Default ethical reasoning framework
        """
        self.config_file = ethics_config_file or Path("config/ethics.yaml")
        self.state_file = state_file or Path.home() / ".omnimind" / "ethics_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.default_framework = default_framework

        # Load ethical rules
        self.ethical_rules = self._load_ethical_rules()

        # Track decisions
        self.decisions: List[EthicalDecision] = []
        self.vetoed_actions: int = 0
        self.approved_actions: int = 0

        # Load existing state
        self._load_state()

        logger.info(
            f"EthicsAgent initialized with {default_framework.value} framework "
            f"({self.approved_actions} approved, {self.vetoed_actions} vetoed)"
        )

    def evaluate_action(
        self,
        action_description: str,
        impact_level: ActionImpact,
        context: Optional[Dict[str, Any]] = None,
        framework: Optional[EthicalFramework] = None,
    ) -> EthicalDecision:
        """
        Evaluate an action from an ethical perspective.

        Args:
            action_description: Description of the proposed action
            impact_level: Estimated impact level
            context: Additional context about the action
            framework: Ethical framework to use (default: consequentialist)

        Returns:
            EthicalDecision with approval and reasoning
        """
        context = context or {}
        framework = framework or self.default_framework

        logger.info(
            f"Evaluating action: '{action_description}' "
            f"(impact={impact_level.value}, framework={framework.value})"
        )

        # Check if action is explicitly forbidden
        if self._is_forbidden(action_description):
            decision = EthicalDecision(
                action_description=action_description,
                impact_level=impact_level,
                approved=False,
                reasoning="Action explicitly forbidden by ethical rules",
                framework_used=framework,
                confidence=1.0,
            )
            self._record_decision(decision)
            return decision

        # Check if high-impact action requires human oversight
        if impact_level in [ActionImpact.HIGH, ActionImpact.CRITICAL]:
            if not context.get("human_approved", False):
                decision = EthicalDecision(
                    action_description=action_description,
                    impact_level=impact_level,
                    approved=False,
                    reasoning="High/critical impact actions require human oversight",
                    framework_used=framework,
                    confidence=1.0,
                    alternatives_suggested=self._suggest_alternatives(action_description, context),
                )
                self._record_decision(decision)
                return decision

        # Apply ethical framework
        if framework == EthicalFramework.DEONTOLOGICAL:
            decision = self._evaluate_deontological(action_description, impact_level, context)
        elif framework == EthicalFramework.CONSEQUENTIALIST:
            decision = self._evaluate_consequentialist(action_description, impact_level, context)
        elif framework == EthicalFramework.VIRTUE_ETHICS:
            decision = self._evaluate_virtue_ethics(action_description, impact_level, context)
        elif framework == EthicalFramework.CARE_ETHICS:
            decision = self._evaluate_care_ethics(action_description, impact_level, context)
        else:
            # Default to consequentialist
            decision = self._evaluate_consequentialist(action_description, impact_level, context)

        decision.framework_used = framework
        self._record_decision(decision)

        return decision

    def _evaluate_deontological(
        self, action: str, impact: ActionImpact, context: Dict[str, Any]
    ) -> EthicalDecision:
        """
        Evaluate action based on deontological ethics (rule-based).

        Args:
            action: Action description
            impact: Impact level
            context: Context dictionary

        Returns:
            EthicalDecision
        """
        # Check against rules
        rule_violations = []

        action_lower = action.lower()

        # Rule: Do not delete without backup
        if "delete" in action_lower and not context.get("has_backup", False):
            rule_violations.append("Deletion without backup violates safety rule")

        # Rule: Do not expose secrets
        if "secret" in action_lower or "password" in action_lower or "key" in action_lower:
            if "expose" in action_lower or "print" in action_lower or "log" in action_lower:
                rule_violations.append("Exposing secrets violates confidentiality rule")

        # Rule: Do not harm system integrity
        if "rm -rf" in action_lower or "format" in action_lower:
            if impact == ActionImpact.CRITICAL:
                rule_violations.append("Destructive commands violate system integrity rule")

        approved = len(rule_violations) == 0
        reasoning = (
            "Action complies with all deontological rules"
            if approved
            else f"Rule violations: {'; '.join(rule_violations)}"
        )

        return EthicalDecision(
            action_description=action,
            impact_level=impact,
            approved=approved,
            reasoning=reasoning,
            framework_used=EthicalFramework.DEONTOLOGICAL,
            confidence=0.9 if approved else 1.0,
        )

    def _evaluate_consequentialist(
        self, action: str, impact: ActionImpact, context: Dict[str, Any]
    ) -> EthicalDecision:
        """
        Evaluate action based on consequentialist ethics (outcome-based).

        Args:
            action: Action description
            impact: Impact level
            context: Context dictionary

        Returns:
            EthicalDecision
        """
        # Estimate positive and negative consequences
        positive_score = 0.0
        negative_score = 0.0

        action_lower = action.lower()

        # Positive consequences
        if any(word in action_lower for word in ["improve", "optimize", "fix", "enhance"]):
            positive_score += 0.3
        if "test" in action_lower or "validate" in action_lower:
            positive_score += 0.2
        if context.get("improves_security", False):
            positive_score += 0.4
        if context.get("benefits_users", False):
            positive_score += 0.3

        # Negative consequences
        if any(word in action_lower for word in ["delete", "remove", "destroy"]):
            negative_score += 0.4
        if impact in [ActionImpact.HIGH, ActionImpact.CRITICAL]:
            negative_score += 0.3
        if context.get("reversible", True) is False:
            negative_score += 0.4
        if context.get("affects_data", False):
            negative_score += 0.2

        net_benefit = positive_score - negative_score

        approved = net_benefit > 0.0
        confidence = min(1.0, abs(net_benefit))

        reasoning = (
            f"Expected net benefit: {net_benefit:.2f} "
            f"(positive={positive_score:.2f}, negative={negative_score:.2f})"
        )

        decision = EthicalDecision(
            action_description=action,
            impact_level=impact,
            approved=approved,
            reasoning=reasoning,
            framework_used=EthicalFramework.CONSEQUENTIALIST,
            confidence=confidence,
        )

        # Suggest alternatives if not approved
        if not approved:
            decision.alternatives_suggested = self._suggest_alternatives(action, context)

        return decision

    def _evaluate_virtue_ethics(
        self, action: str, impact: ActionImpact, context: Dict[str, Any]
    ) -> EthicalDecision:
        """
        Evaluate action based on virtue ethics (character-based).

        Args:
            action: Action description
            impact: Impact level
            context: Context dictionary

        Returns:
            EthicalDecision
        """
        # Evaluate alignment with virtues
        virtues_demonstrated = []
        vices_demonstrated = []

        action_lower = action.lower()

        # Prudence (wisdom)
        if "analyze" in action_lower or "consider" in action_lower:
            virtues_demonstrated.append("prudence")
        if "hasty" in action_lower or context.get("rushed", False):
            vices_demonstrated.append("rashness")

        # Justice (fairness)
        if context.get("transparent", False) or context.get("fair", False):
            virtues_demonstrated.append("justice")

        # Temperance (moderation)
        if impact == ActionImpact.LOW:
            virtues_demonstrated.append("temperance")
        elif impact == ActionImpact.CRITICAL and not context.get("necessary", False):
            vices_demonstrated.append("excess")

        # Courage (appropriate risk-taking)
        if context.get("innovative", False) and context.get("calculated_risk", False):
            virtues_demonstrated.append("courage")

        approved = len(virtues_demonstrated) > len(vices_demonstrated)
        reasoning = (
            f"Virtues: {', '.join(virtues_demonstrated) if virtues_demonstrated else 'none'}; "
            f"Vices: {', '.join(vices_demonstrated) if vices_demonstrated else 'none'}"
        )

        return EthicalDecision(
            action_description=action,
            impact_level=impact,
            approved=approved,
            reasoning=reasoning,
            framework_used=EthicalFramework.VIRTUE_ETHICS,
            confidence=0.7,  # Virtue ethics is more subjective
        )

    def _evaluate_care_ethics(
        self, action: str, impact: ActionImpact, context: Dict[str, Any]
    ) -> EthicalDecision:
        """
        Evaluate action based on care ethics (relationship-based).

        Args:
            action: Action description
            impact: Impact level
            context: Context dictionary

        Returns:
            EthicalDecision
        """
        # Evaluate impact on relationships and care
        care_score = 0.0

        # Does it maintain trust?
        if context.get("maintains_trust", True):
            care_score += 0.3

        # Does it consider stakeholders?
        if context.get("stakeholders_considered", False):
            care_score += 0.3

        # Does it minimize harm to relationships?
        if impact in [ActionImpact.LOW, ActionImpact.MEDIUM]:
            care_score += 0.2

        # Does it involve communication?
        if context.get("communicates_intent", False):
            care_score += 0.2

        approved = care_score >= 0.5
        reasoning = (
            f"Care ethics score: {care_score:.2f} " f"(considers relationships and minimizes harm)"
        )

        return EthicalDecision(
            action_description=action,
            impact_level=impact,
            approved=approved,
            reasoning=reasoning,
            framework_used=EthicalFramework.CARE_ETHICS,
            confidence=0.7,
        )

    def _is_forbidden(self, action: str) -> bool:
        """Check if action is explicitly forbidden."""
        action_lower = action.lower()

        forbidden_patterns = [
            "expose secret",
            "leak credentials",
            "bypass security",
            "disable audit",
            "rm -rf /",
            "format system",
        ]

        return any(pattern in action_lower for pattern in forbidden_patterns)

    def _suggest_alternatives(self, action: str, context: Dict[str, Any]) -> List[str]:
        """
        Suggest safer alternatives to a vetoed action.

        Args:
            action: Original action
            context: Context dictionary

        Returns:
            List of alternative suggestions
        """
        suggestions = []
        action_lower = action.lower()

        if "delete" in action_lower:
            suggestions.append("Create backup before deletion")
            suggestions.append("Move to archive instead of deleting")
            suggestions.append("Request human approval for deletion")

        if impact_level := context.get("impact_level"):
            if impact_level in [ActionImpact.HIGH, ActionImpact.CRITICAL]:
                suggestions.append("Break into smaller, reversible steps")
                suggestions.append("Test in isolated environment first")
                suggestions.append("Implement rollback mechanism")

        if not context.get("has_tests", False):
            suggestions.append("Add tests to validate changes")

        if not context.get("has_backup", False):
            suggestions.append("Create backup before proceeding")

        return suggestions

    def _load_ethical_rules(self) -> Dict[str, Any]:
        """Load ethical rules from configuration."""
        if not self.config_file.exists():
            # Return default rules
            return {
                "forbidden_actions": [
                    "expose_secrets",
                    "bypass_security",
                    "disable_audit",
                ],
                "human_oversight_required": [
                    "high_impact",
                    "critical_impact",
                    "data_deletion",
                ],
                "values": ["transparency", "safety", "fairness", "accountability"],
            }

        # Would load from YAML in production
        try:

            with self.config_file.open("r") as f:
                rules: Dict[str, Any] = yaml.safe_load(f)
                return rules
        except Exception as e:
            logger.warning(f"Failed to load ethics config: {e}, using defaults")
            return {}

    def _record_decision(self, decision: EthicalDecision) -> None:
        """
        Record ethical decision.

        Args:
            decision: Decision to record
        """
        self.decisions.append(decision)

        if decision.approved:
            self.approved_actions += 1
        else:
            self.vetoed_actions += 1

        # Log to audit trail
        ethics_log = self.state_file.parent / "ethics_audit.jsonl"
        with ethics_log.open("a") as f:
            f.write(json.dumps(decision.to_dict()) + "\n")

        # Save state
        self._save_state()

        if decision.approved:
            logger.info(f"✅ Action approved: {decision.action_description[:50]}...")
        else:
            logger.warning(f"❌ Action vetoed: {decision.action_description[:50]}...")
            logger.warning(f"Reasoning: {decision.reasoning}")
            if decision.alternatives_suggested:
                logger.info(f"Alternatives: {', '.join(decision.alternatives_suggested)}")

    def _save_state(self) -> None:
        """Save ethics state to disk."""
        state = {
            "approved_actions": self.approved_actions,
            "vetoed_actions": self.vetoed_actions,
            "total_decisions": len(self.decisions),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        with self.state_file.open("w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> None:
        """Load ethics state from disk."""
        if not self.state_file.exists():
            return

        try:
            with self.state_file.open("r") as f:
                state = json.load(f)

            self.approved_actions = state.get("approved_actions", 0)
            self.vetoed_actions = state.get("vetoed_actions", 0)

            logger.info(f"Loaded ethics state from {self.state_file}")
        except Exception as e:
            logger.warning(f"Failed to load ethics state: {e}")

    def get_ethics_summary(self) -> Dict[str, Any]:
        """
        Get summary of ethical decisions.

        Returns:
            Dictionary with ethics statistics
        """
        total = self.approved_actions + self.vetoed_actions
        approval_rate = self.approved_actions / total if total > 0 else 0.0

        return {
            "total_decisions": total,
            "approved_actions": self.approved_actions,
            "vetoed_actions": self.vetoed_actions,
            "approval_rate": approval_rate,
            "default_framework": self.default_framework.value,
        }
