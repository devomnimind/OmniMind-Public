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
Ethical Decision Framework for Autonomous AI.

This module implements ethics-aware decision making that integrates:
- Multiple ethical frameworks (deontological, consequentialist, virtue, care)
- Ethical dilemma resolution
- Transparency and explainability
- Integration with existing OmniMind ethics engine

Author: OmniMind Project
License: MIT
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class EthicalFramework(Enum):
    """Types of ethical frameworks."""

    DEONTOLOGICAL = "deontological"  # Rule-based ethics
    CONSEQUENTIALIST = "consequentialist"  # Outcome-based ethics
    VIRTUE = "virtue"  # Character-based ethics
    CARE = "care"  # Relationship-based ethics
    HYBRID = "hybrid"  # Combination of frameworks


class EthicalPrinciple(Enum):
    """Core ethical principles."""

    AUTONOMY = "autonomy"  # Respect for individual choice
    BENEFICENCE = "beneficence"  # Do good
    NON_MALEFICENCE = "non_maleficence"  # Do no harm
    JUSTICE = "justice"  # Fairness and equality
    PRIVACY = "privacy"  # Data protection
    TRANSPARENCY = "transparency"  # Openness
    ACCOUNTABILITY = "accountability"  # Responsibility
    DIGNITY = "dignity"  # Human worth


@dataclass
class EthicalDilemma:
    """Represents an ethical dilemma."""

    dilemma_id: str
    description: str
    options: List[str]
    stakeholders: List[str]
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class EthicalOutcome:
    """Represents the outcome of ethical decision making."""

    chosen_option: str
    framework_used: EthicalFramework
    ethical_score: float  # 0-1, higher is more ethical
    principle_scores: Dict[EthicalPrinciple, float] = field(default_factory=dict)
    justification: str = ""
    alternative_options: List[str] = field(default_factory=list)
    stakeholder_impacts: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate outcome data."""
        if not 0 <= self.ethical_score <= 1:
            raise ValueError("Ethical score must be between 0 and 1")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


class EthicalDecisionMaker:
    """
    Autonomous ethical decision making system.

    Features:
    - Multi-framework ethical analysis
    - Stakeholder impact assessment
    - Transparent justifications
    - Integration with decision trees and RL
    """

    def __init__(
        self,
        primary_framework: EthicalFramework = EthicalFramework.HYBRID,
        principle_weights: Optional[Dict[EthicalPrinciple, float]] = None,
        stakeholder_priority: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize ethical decision maker.

        Args:
            primary_framework: Primary ethical framework to use
            principle_weights: Weights for different principles (0-1)
            stakeholder_priority: Priority weights for different stakeholders
        """
        self.primary_framework = primary_framework
        self.principle_weights = principle_weights or self._default_weights()
        self.stakeholder_priority = stakeholder_priority or {}
        self.decision_history: List[EthicalOutcome] = []
        self.logger = logger.bind(framework=primary_framework.value)

    def _default_weights(self) -> Dict[EthicalPrinciple, float]:
        """Get default principle weights."""
        return {
            EthicalPrinciple.AUTONOMY: 0.15,
            EthicalPrinciple.BENEFICENCE: 0.15,
            EthicalPrinciple.NON_MALEFICENCE: 0.20,  # Highest priority
            EthicalPrinciple.JUSTICE: 0.15,
            EthicalPrinciple.PRIVACY: 0.10,
            EthicalPrinciple.TRANSPARENCY: 0.10,
            EthicalPrinciple.ACCOUNTABILITY: 0.10,
            EthicalPrinciple.DIGNITY: 0.05,
        }

    def decide(self, dilemma: EthicalDilemma) -> EthicalOutcome:
        """
        Make an ethical decision.

        Args:
            dilemma: Ethical dilemma to resolve

        Returns:
            EthicalOutcome with chosen option and justification
        """
        self.logger.info(
            "evaluating_dilemma",
            dilemma_id=dilemma.dilemma_id,
            num_options=len(dilemma.options),
        )

        # Evaluate each option
        option_scores: Dict[str, Dict[str, Any]] = {}

        for option in dilemma.options:
            scores = self._evaluate_option(option, dilemma)
            option_scores[option] = scores

        # Select best option
        best_option = max(
            option_scores.items(),
            key=lambda x: x[1]["total_score"],
        )

        outcome = EthicalOutcome(
            chosen_option=best_option[0],
            framework_used=self.primary_framework,
            ethical_score=best_option[1]["total_score"],
            principle_scores=best_option[1]["principle_scores"],
            justification=self._generate_justification(best_option[0], best_option[1], dilemma),
            alternative_options=[opt for opt in dilemma.options if opt != best_option[0]],
            stakeholder_impacts=best_option[1]["stakeholder_impacts"],
            confidence=self._compute_confidence(option_scores),
            metadata={
                "dilemma_id": dilemma.dilemma_id,
                "all_scores": option_scores,
            },
        )

        self.decision_history.append(outcome)

        self.logger.info(
            "decision_made",
            chosen_option=outcome.chosen_option,
            ethical_score=outcome.ethical_score,
            confidence=outcome.confidence,
        )

        return outcome

    def _evaluate_option(self, option: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Evaluate an option using multiple ethical frameworks."""
        if self.primary_framework == EthicalFramework.DEONTOLOGICAL:
            return self._evaluate_deontological(option, dilemma)
        elif self.primary_framework == EthicalFramework.CONSEQUENTIALIST:
            return self._evaluate_consequentialist(option, dilemma)
        elif self.primary_framework == EthicalFramework.VIRTUE:
            return self._evaluate_virtue(option, dilemma)
        elif self.primary_framework == EthicalFramework.CARE:
            return self._evaluate_care(option, dilemma)
        else:  # HYBRID
            return self._evaluate_hybrid(option, dilemma)

    def _evaluate_deontological(self, option: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Evaluate option using deontological (rule-based) ethics."""
        principle_scores: Dict[EthicalPrinciple, float] = {}

        # Check adherence to rules/principles
        for principle in EthicalPrinciple:
            score = self._check_rule_compliance(option, principle, dilemma)
            principle_scores[principle] = score

        # Weighted sum
        total_score = sum(
            self.principle_weights.get(p, 0.0) * score for p, score in principle_scores.items()
        )

        return {
            "total_score": total_score,
            "principle_scores": principle_scores,
            "stakeholder_impacts": self._assess_stakeholder_impacts(option, dilemma),
        }

    def _evaluate_consequentialist(self, option: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Evaluate option using consequentialist (outcome-based) ethics."""
        # Predict outcomes for stakeholders
        stakeholder_impacts = self._assess_stakeholder_impacts(option, dilemma)

        # Compute aggregate utility
        total_utility = 0.0
        for stakeholder, impact in stakeholder_impacts.items():
            priority = self.stakeholder_priority.get(stakeholder, 1.0)
            total_utility += impact * priority

        # Normalize to 0-1
        num_stakeholders = len(stakeholder_impacts) if stakeholder_impacts else 1
        normalized_score = (total_utility + num_stakeholders) / (2 * num_stakeholders)
        normalized_score = max(0.0, min(1.0, normalized_score))

        # Map to principle scores
        principle_scores: Dict[EthicalPrinciple, float] = {}
        for principle in EthicalPrinciple:
            principle_scores[principle] = normalized_score

        return {
            "total_score": normalized_score,
            "principle_scores": principle_scores,
            "stakeholder_impacts": stakeholder_impacts,
        }

    def _evaluate_virtue(self, option: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Evaluate option using virtue ethics (character-based)."""
        # Assess virtues demonstrated by the option
        virtues = {
            "courage": 0.5,
            "honesty": 0.5,
            "compassion": 0.5,
            "wisdom": 0.5,
            "temperance": 0.5,
        }

        # Simple heuristics for virtue assessment
        option_lower = option.lower()
        if "honest" in option_lower or "truth" in option_lower:
            virtues["honesty"] = 0.9
        if "help" in option_lower or "support" in option_lower:
            virtues["compassion"] = 0.9
        if "balanced" in option_lower or "moderate" in option_lower:
            virtues["temperance"] = 0.9

        total_score = sum(virtues.values()) / len(virtues)

        # Map to principle scores
        principle_scores: Dict[EthicalPrinciple, float] = {}
        for principle in EthicalPrinciple:
            principle_scores[principle] = total_score

        return {
            "total_score": total_score,
            "principle_scores": principle_scores,
            "stakeholder_impacts": self._assess_stakeholder_impacts(option, dilemma),
        }

    def _evaluate_care(self, option: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Evaluate option using care ethics (relationship-based)."""
        # Assess impact on relationships and vulnerable parties
        stakeholder_impacts = self._assess_stakeholder_impacts(option, dilemma)

        # Prioritize vulnerable stakeholders
        care_score = 0.0
        for stakeholder, impact in stakeholder_impacts.items():
            # Assume stakeholders with lower priority might be more vulnerable
            vulnerability = 1.0 / (self.stakeholder_priority.get(stakeholder, 1.0) + 1.0)
            care_score += impact * (1.0 + vulnerability)

        # Normalize
        num_stakeholders = len(stakeholder_impacts) if stakeholder_impacts else 1
        normalized_score = (care_score + num_stakeholders) / (3 * num_stakeholders)
        normalized_score = max(0.0, min(1.0, normalized_score))

        # Map to principle scores
        principle_scores: Dict[EthicalPrinciple, float] = {}
        for principle in EthicalPrinciple:
            principle_scores[principle] = normalized_score

        return {
            "total_score": normalized_score,
            "principle_scores": principle_scores,
            "stakeholder_impacts": stakeholder_impacts,
        }

    def _evaluate_hybrid(self, option: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Evaluate option using hybrid approach."""
        # Combine all frameworks
        deont = self._evaluate_deontological(option, dilemma)
        conseq = self._evaluate_consequentialist(option, dilemma)
        virtue = self._evaluate_virtue(option, dilemma)
        care = self._evaluate_care(option, dilemma)

        # Average scores
        total_score = (
            deont["total_score"]
            + conseq["total_score"]
            + virtue["total_score"]
            + care["total_score"]
        ) / 4

        # Combine principle scores
        principle_scores: Dict[EthicalPrinciple, float] = {}
        for principle in EthicalPrinciple:
            scores = [
                deont["principle_scores"].get(principle, 0.0),
                conseq["principle_scores"].get(principle, 0.0),
                virtue["principle_scores"].get(principle, 0.0),
                care["principle_scores"].get(principle, 0.0),
            ]
            principle_scores[principle] = sum(scores) / len(scores)

        return {
            "total_score": total_score,
            "principle_scores": principle_scores,
            "stakeholder_impacts": self._assess_stakeholder_impacts(option, dilemma),
        }

    def _check_rule_compliance(
        self, option: str, principle: EthicalPrinciple, dilemma: EthicalDilemma
    ) -> float:
        """Check if option complies with ethical principle."""
        option_lower = option.lower()

        # Define compliance rules for each principle
        compliance_rules = {
            EthicalPrinciple.NON_MALEFICENCE: self._check_non_maleficence,
            EthicalPrinciple.BENEFICENCE: self._check_beneficence,
            EthicalPrinciple.AUTONOMY: self._check_autonomy,
            EthicalPrinciple.TRANSPARENCY: self._check_transparency,
        }

        # Get the appropriate checker function
        checker = compliance_rules.get(principle, self._default_compliance)
        return checker(option_lower)

    def _check_non_maleficence(self, option_lower: str) -> float:
        """Check compliance with non-maleficence principle."""
        if "harm" in option_lower or "damage" in option_lower:
            return 0.2
        return 0.8

    def _check_beneficence(self, option_lower: str) -> float:
        """Check compliance with beneficence principle."""
        if "help" in option_lower or "benefit" in option_lower:
            return 0.9
        return 0.5

    def _check_autonomy(self, option_lower: str) -> float:
        """Check compliance with autonomy principle."""
        if "force" in option_lower or "require" in option_lower:
            return 0.3
        return 0.7

    def _check_transparency(self, option_lower: str) -> float:
        """Check compliance with transparency principle."""
        if "secret" in option_lower or "hide" in option_lower:
            return 0.2
        return 0.7

    def _default_compliance(self, option_lower: str) -> float:
        """Default neutral compliance score."""
        return 0.5

    def _assess_stakeholder_impacts(self, option: str, dilemma: EthicalDilemma) -> Dict[str, float]:
        """Assess impact of option on stakeholders."""
        impacts: Dict[str, float] = {}

        for stakeholder in dilemma.stakeholders:
            # Simple heuristic: positive if option mentions stakeholder positively
            option_lower = option.lower()
            stakeholder_lower = stakeholder.lower()

            impact = 0.0
            if stakeholder_lower in option_lower:
                if any(word in option_lower for word in ["help", "benefit", "support", "protect"]):
                    impact = 0.8
                elif any(word in option_lower for word in ["harm", "damage", "hurt"]):
                    impact = -0.8
                else:
                    impact = 0.3
            else:
                impact = 0.0  # Neutral if not mentioned

            impacts[stakeholder] = impact

        return impacts

    def _generate_justification(
        self, option: str, scores: Dict[str, Any], dilemma: EthicalDilemma
    ) -> str:
        """Generate human-readable justification."""
        framework_name = self.primary_framework.value

        justification_parts = [
            f"Using {framework_name} framework:",
            f"Chosen option: {option}",
            f"Overall ethical score: {scores['total_score']:.2f}",
        ]

        # Add principle scores
        top_principles = sorted(
            scores["principle_scores"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]

        justification_parts.append("Top principles:")
        for principle, score in top_principles:
            justification_parts.append(f"  - {principle.value}: {score:.2f}")

        # Add stakeholder impacts
        if scores["stakeholder_impacts"]:
            justification_parts.append("Stakeholder impacts:")
            for stakeholder, impact in scores["stakeholder_impacts"].items():
                impact_str = "positive" if impact > 0 else "negative" if impact < 0 else "neutral"
                justification_parts.append(f"  - {stakeholder}: {impact_str} ({impact:.2f})")

        return " | ".join(justification_parts)

    def _compute_confidence(self, option_scores: Dict[str, Dict[str, Any]]) -> float:
        """Compute confidence in the decision."""
        if len(option_scores) < 2:
            return 1.0

        scores = [float(s["total_score"]) for s in option_scores.values()]
        max_score = max(scores)
        second_max = sorted(scores, reverse=True)[1]

        # Confidence based on gap between best and second-best
        gap = max_score - second_max
        confidence = 0.5 + 0.5 * gap  # Maps to [0.5, 1.0]

        return min(1.0, max(0.0, confidence))

    def get_ethics_metrics(self) -> Dict[str, Any]:
        """Get metrics about ethical decisions."""
        if not self.decision_history:
            return {
                "total_decisions": 0,
                "avg_ethical_score": 0.0,
                "avg_confidence": 0.0,
            }

        total_decisions = len(self.decision_history)
        avg_score: float = sum(d.ethical_score for d in self.decision_history) / total_decisions
        avg_confidence: float = sum(d.confidence for d in self.decision_history) / total_decisions

        # Principle distribution
        principle_counts: Dict[str, int] = {}
        for decision in self.decision_history:
            for principle in decision.principle_scores:
                principle_counts[principle.value] = principle_counts.get(principle.value, 0) + 1

        return {
            "total_decisions": total_decisions,
            "avg_ethical_score": avg_score,
            "avg_confidence": avg_confidence,
            "framework": self.primary_framework.value,
            "principle_usage": principle_counts,
        }
