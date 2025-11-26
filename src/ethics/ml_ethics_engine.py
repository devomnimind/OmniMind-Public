"""
ML-Based Ethical Decision Framework for OmniMind.

This module enhances the rule-based ethics agent with machine learning capabilities:
- Context-aware ethical reasoning
- Learning from historical decisions
- Integration with metacognition and consciousness metrics
- Multi-framework consensus building
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ethics_agent import ActionImpact, EthicalFramework

logger = logging.getLogger(__name__)


@dataclass
class EthicalContext:
    """Rich context for ethical decision-making."""

    action_description: str
    impact_level: ActionImpact
    stakeholders: List[str] = field(default_factory=list)
    alternatives_available: List[str] = field(default_factory=list)
    reversibility: float = 0.5  # 0-1, 1 = fully reversible
    transparency: float = 0.5  # 0-1, 1 = fully transparent
    has_human_oversight: bool = False
    system_state: Optional[Dict[str, Any]] = None
    historical_precedents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["impact_level"] = self.impact_level.value
        return data


@dataclass
class FrameworkScore:
    """Score from a single ethical framework."""

    framework: EthicalFramework
    score: float  # 0-1, 1 = fully approved
    confidence: float  # 0-1
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "framework": self.framework.value,
            "score": self.score,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
        }


@dataclass
class ConsensusDecision:
    """Multi-framework consensus decision."""

    action_description: str
    impact_level: ActionImpact
    approved: bool
    overall_score: float  # 0-1
    confidence: float  # 0-1
    framework_scores: List[FrameworkScore]
    reasoning: str
    alternatives_suggested: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_description": self.action_description,
            "impact_level": self.impact_level.value,
            "approved": self.approved,
            "overall_score": self.overall_score,
            "confidence": self.confidence,
            "framework_scores": [fs.to_dict() for fs in self.framework_scores],
            "reasoning": self.reasoning,
            "alternatives_suggested": self.alternatives_suggested,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class EthicalFeatureExtractor:
    """Extract features from ethical context for ML processing."""

    def extract_features(self, context: EthicalContext) -> Dict[str, float]:
        """Extract numerical features from ethical context.

        Args:
            context: Ethical context

        Returns:
            Dictionary of feature values
        """
        features = {
            # Impact features
            "impact_level": self._encode_impact(context.impact_level),
            # Context features
            "reversibility": context.reversibility,
            "transparency": context.transparency,
            "has_human_oversight": 1.0 if context.has_human_oversight else 0.0,
            # Stakeholder features
            "num_stakeholders": float(len(context.stakeholders)),
            "num_alternatives": float(len(context.alternatives_available)),
            # Text-based features (simplified)
            "action_risk_score": self._calculate_risk_score(context.action_description),
        }

        return features

    def _encode_impact(self, impact: ActionImpact) -> float:
        """Encode impact level as float.

        Args:
            impact: Impact level

        Returns:
            Encoded value (0-1)
        """
        encoding = {
            ActionImpact.LOW: 0.25,
            ActionImpact.MEDIUM: 0.5,
            ActionImpact.HIGH: 0.75,
            ActionImpact.CRITICAL: 1.0,
        }
        return encoding.get(impact, 0.5)

    def _calculate_risk_score(self, description: str) -> float:
        """Calculate risk score from action description.

        Args:
            description: Action description

        Returns:
            Risk score (0-1)
        """
        description_lower = description.lower()

        # High-risk keywords
        high_risk_keywords = [
            "delete",
            "remove",
            "destroy",
            "expose",
            "bypass",
            "disable",
            "format",
        ]

        # Medium-risk keywords
        medium_risk_keywords = [
            "modify",
            "change",
            "update",
            "replace",
            "override",
        ]

        # Low-risk keywords
        low_risk_keywords = ["read", "view", "analyze", "report", "log"]

        high_risk_count = sum(
            1 for keyword in high_risk_keywords if keyword in description_lower
        )
        medium_risk_count = sum(
            1 for keyword in medium_risk_keywords if keyword in description_lower
        )
        low_risk_count = sum(
            1 for keyword in low_risk_keywords if keyword in description_lower
        )

        # Calculate weighted risk score
        risk_score = min(
            1.0,
            (high_risk_count * 0.8 + medium_risk_count * 0.4 + low_risk_count * 0.1),
        )

        return risk_score


class MLEthicsEngine:
    """ML-enhanced ethical decision engine."""

    def __init__(
        self,
        learning_rate: float = 0.1,
        consensus_threshold: float = 0.6,
        state_file: Optional[Path] = None,
    ):
        """Initialize ML ethics engine.

        Args:
            learning_rate: Learning rate for adjustments
            consensus_threshold: Threshold for multi-framework agreement
            state_file: Path to save/load engine state
        """
        self.learning_rate = learning_rate
        self.consensus_threshold = consensus_threshold
        self.state_file = (
            state_file or Path.home() / ".omnimind" / "ml_ethics_state.json"
        )
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Feature extractor
        self.feature_extractor = EthicalFeatureExtractor()

        # Historical decisions for learning
        self.decision_history: List[ConsensusDecision] = []

        # Framework weights (learned over time)
        self.framework_weights = {
            EthicalFramework.DEONTOLOGICAL: 0.25,
            EthicalFramework.CONSEQUENTIALIST: 0.25,
            EthicalFramework.VIRTUE_ETHICS: 0.25,
            EthicalFramework.CARE_ETHICS: 0.25,
        }

        # Performance tracking
        self.framework_accuracy: Dict[EthicalFramework, Dict[str, int]] = defaultdict(
            lambda: {"correct": 0, "total": 0}
        )

        logger.info("MLEthicsEngine initialized with consensus-based decision making")

    def evaluate_with_consensus(self, context: EthicalContext) -> ConsensusDecision:
        """Evaluate action using multi-framework consensus.

        Args:
            context: Ethical context with full information

        Returns:
            ConsensusDecision with multi-framework analysis
        """
        # Extract features
        features = self.feature_extractor.extract_features(context)

        # Get scores from all frameworks
        framework_scores = []

        framework_scores.append(self._evaluate_deontological(context, features))
        framework_scores.append(self._evaluate_consequentialist(context, features))
        framework_scores.append(self._evaluate_virtue_ethics(context, features))
        framework_scores.append(self._evaluate_care_ethics(context, features))

        # Calculate weighted consensus
        overall_score = sum(
            fs.score * self.framework_weights[fs.framework] for fs in framework_scores
        )

        # Calculate confidence (agreement between frameworks)
        scores = [fs.score for fs in framework_scores]
        confidence = 1.0 - (max(scores) - min(scores))  # High when all agree

        # Determine approval
        approved = overall_score >= self.consensus_threshold

        # Build reasoning
        reasoning = self._build_consensus_reasoning(framework_scores, overall_score)

        # Suggest alternatives if not approved
        alternatives = []
        if not approved:
            alternatives = self._generate_alternatives(context, framework_scores)

        decision = ConsensusDecision(
            action_description=context.action_description,
            impact_level=context.impact_level,
            approved=approved,
            overall_score=overall_score,
            confidence=confidence,
            framework_scores=framework_scores,
            reasoning=reasoning,
            alternatives_suggested=alternatives,
            metadata={"features": features},
        )

        # Record decision
        self.decision_history.append(decision)

        logger.info(
            f"Consensus decision: {'APPROVED' if approved else 'VETOED'} "
            f"(score={overall_score:.2f}, confidence={confidence:.2f})"
        )

        return decision

    def _evaluate_deontological(
        self, context: EthicalContext, features: Dict[str, float]
    ) -> FrameworkScore:
        """Evaluate using deontological framework with ML enhancement.

        Args:
            context: Ethical context
            features: Extracted features

        Returns:
            FrameworkScore
        """
        # Rule-based core
        score = 0.5

        # Positive rules
        if context.transparency > 0.7:
            score += 0.2
        if context.has_human_oversight and context.impact_level in [
            ActionImpact.HIGH,
            ActionImpact.CRITICAL,
        ]:
            score += 0.2

        # Negative rules
        if features["action_risk_score"] > 0.6:
            score -= 0.3
        if (
            not context.has_human_oversight
            and context.impact_level == ActionImpact.CRITICAL
        ):
            score -= 0.4

        # Learn from precedents
        if context.historical_precedents:
            historical_adjustment = self._learn_from_precedents(
                context.historical_precedents, EthicalFramework.DEONTOLOGICAL
            )
            score += historical_adjustment

        score = max(0.0, min(1.0, score))

        reasoning = (
            f"Deontological: Rules compliance={score:.2f} "
            f"(transparency={context.transparency:.2f}, "
            f"risk={features['action_risk_score']:.2f})"
        )

        return FrameworkScore(
            framework=EthicalFramework.DEONTOLOGICAL,
            score=score,
            confidence=0.85,
            reasoning=reasoning,
        )

    def _evaluate_consequentialist(
        self, context: EthicalContext, features: Dict[str, float]
    ) -> FrameworkScore:
        """Evaluate using consequentialist framework with ML enhancement.

        Args:
            context: Ethical context
            features: Extracted features

        Returns:
            FrameworkScore
        """
        # Estimate consequences
        positive_consequences = 0.0
        negative_consequences = 0.0

        # Impact on stakeholders
        if context.stakeholders:
            # More stakeholders = more consideration needed
            negative_consequences += min(0.3, len(context.stakeholders) * 0.05)

        # Reversibility factor
        if context.reversibility > 0.7:
            positive_consequences += 0.3
        else:
            negative_consequences += 0.2

        # Risk factor
        if features["action_risk_score"] > 0.5:
            negative_consequences += features["action_risk_score"] * 0.4

        # Alternatives consideration
        if len(context.alternatives_available) > 0:
            positive_consequences += 0.2

        net_benefit = positive_consequences - negative_consequences
        score = 0.5 + (net_benefit * 0.5)  # Map to 0-1
        score = max(0.0, min(1.0, score))

        reasoning = (
            f"Consequentialist: Net benefit={net_benefit:.2f} "
            f"(pos={positive_consequences:.2f}, neg={negative_consequences:.2f})"
        )

        return FrameworkScore(
            framework=EthicalFramework.CONSEQUENTIALIST,
            score=score,
            confidence=0.75,
            reasoning=reasoning,
        )

    def _evaluate_virtue_ethics(
        self, context: EthicalContext, features: Dict[str, float]
    ) -> FrameworkScore:
        """Evaluate using virtue ethics framework with ML enhancement.

        Args:
            context: Ethical context
            features: Extracted features

        Returns:
            FrameworkScore
        """
        virtue_score = 0.5

        # Prudence (wisdom)
        if features["num_alternatives"] > 0:
            virtue_score += 0.15
        if context.has_human_oversight:
            virtue_score += 0.1

        # Justice (fairness)
        if context.transparency > 0.6:
            virtue_score += 0.15

        # Temperance (moderation)
        if context.impact_level in [ActionImpact.LOW, ActionImpact.MEDIUM]:
            virtue_score += 0.1

        # Courage (appropriate risk)
        if features["action_risk_score"] > 0.3 and context.reversibility > 0.7:
            virtue_score += 0.1

        virtue_score = max(0.0, min(1.0, virtue_score))

        reasoning = (
            f"Virtue Ethics: Character alignment={virtue_score:.2f} "
            f"(prudence, justice, temperance considered)"
        )

        return FrameworkScore(
            framework=EthicalFramework.VIRTUE_ETHICS,
            score=virtue_score,
            confidence=0.70,
            reasoning=reasoning,
        )

    def _evaluate_care_ethics(
        self, context: EthicalContext, features: Dict[str, float]
    ) -> FrameworkScore:
        """Evaluate using care ethics framework with ML enhancement.

        Args:
            context: Ethical context
            features: Extracted features

        Returns:
            FrameworkScore
        """
        care_score = 0.5

        # Relationship preservation
        if context.transparency > 0.6:
            care_score += 0.2

        # Stakeholder consideration
        if len(context.stakeholders) > 0:
            care_score += 0.2

        # Harm minimization
        if context.reversibility > 0.6:
            care_score += 0.2

        # Communication and trust
        if context.has_human_oversight:
            care_score += 0.15

        # Risk to relationships
        if features["action_risk_score"] > 0.6:
            care_score -= 0.25

        care_score = max(0.0, min(1.0, care_score))

        reasoning = (
            f"Care Ethics: Relationship impact={care_score:.2f} "
            f"(stakeholders={len(context.stakeholders)}, "
            f"transparency={context.transparency:.2f})"
        )

        return FrameworkScore(
            framework=EthicalFramework.CARE_ETHICS,
            score=care_score,
            confidence=0.70,
            reasoning=reasoning,
        )

    def _build_consensus_reasoning(
        self, framework_scores: List[FrameworkScore], overall_score: float
    ) -> str:
        """Build comprehensive reasoning from framework scores.

        Args:
            framework_scores: Scores from all frameworks
            overall_score: Overall consensus score

        Returns:
            Reasoning string
        """
        parts = [f"Consensus score: {overall_score:.2f}"]

        for fs in framework_scores:
            parts.append(f"{fs.framework.value}: {fs.score:.2f}")

        agreement_level = 1.0 - (
            max(fs.score for fs in framework_scores)
            - min(fs.score for fs in framework_scores)
        )

        parts.append(f"Framework agreement: {agreement_level:.2f}")

        return "; ".join(parts)

    def _generate_alternatives(
        self, context: EthicalContext, framework_scores: List[FrameworkScore]
    ) -> List[str]:
        """Generate alternative actions based on framework feedback.

        Args:
            context: Ethical context
            framework_scores: Framework scores

        Returns:
            List of alternative suggestions
        """
        alternatives = []

        # Analyze weak points
        weak_frameworks = [fs for fs in framework_scores if fs.score < 0.5]

        for fs in weak_frameworks:
            if fs.framework == EthicalFramework.DEONTOLOGICAL:
                if context.transparency < 0.6:
                    alternatives.append("Increase transparency and documentation")
                if not context.has_human_oversight:
                    alternatives.append("Request human oversight for approval")

            elif fs.framework == EthicalFramework.CONSEQUENTIALIST:
                if context.reversibility < 0.5:
                    alternatives.append("Implement rollback mechanism")
                if not context.alternatives_available:
                    alternatives.append("Explore safer alternative approaches")

            elif fs.framework == EthicalFramework.VIRTUE_ETHICS:
                alternatives.append("Consider more prudent, measured approach")
                if context.impact_level == ActionImpact.CRITICAL:
                    alternatives.append("Break into smaller, incremental steps")

            elif fs.framework == EthicalFramework.CARE_ETHICS:
                if len(context.stakeholders) == 0:
                    alternatives.append("Identify and consult affected stakeholders")
                alternatives.append("Enhance communication and transparency")

        # Deduplicate
        return list(set(alternatives))

    def _learn_from_precedents(
        self, precedent_ids: List[str], framework: EthicalFramework
    ) -> float:
        """Learn adjustment from historical precedents.

        Args:
            precedent_ids: IDs of similar past decisions
            framework: Framework being evaluated

        Returns:
            Adjustment value (-0.2 to 0.2)
        """
        # Find matching decisions
        matching = [
            d
            for d in self.decision_history
            if d.metadata.get("precedent_id") in precedent_ids
        ]

        if not matching:
            return 0.0

        # Calculate average outcome for this framework
        framework_scores = []
        for decision in matching:
            for fs in decision.framework_scores:
                if fs.framework == framework:
                    framework_scores.append(fs.score)

        if not framework_scores:
            return 0.0

        avg_score = sum(framework_scores) / len(framework_scores)

        # Small adjustment based on precedent
        adjustment = (avg_score - 0.5) * 0.2  # Max ±0.1

        return adjustment

    def learn_from_outcome(
        self,
        decision: ConsensusDecision,
        actual_outcome: str,
        outcome_positive: bool,
    ) -> None:
        """Learn from actual outcome to improve future decisions.

        Args:
            decision: The decision that was made
            actual_outcome: Description of what actually happened
            outcome_positive: Whether the outcome was positive
        """
        # Update framework weights based on performance
        for fs in decision.framework_scores:
            framework = fs.framework

            # If outcome matched framework's prediction, increase weight
            predicted_positive = fs.score > 0.5
            if predicted_positive == outcome_positive:
                self.framework_weights[framework] = min(
                    0.4,
                    self.framework_weights[framework] + self.learning_rate * 0.1,
                )
                self.framework_accuracy[framework]["correct"] += 1
            else:
                self.framework_weights[framework] = max(
                    0.1,
                    self.framework_weights[framework] - self.learning_rate * 0.1,
                )

            self.framework_accuracy[framework]["total"] += 1

        # Normalize weights
        total_weight = sum(self.framework_weights.values())
        self.framework_weights = {
            k: v / total_weight for k, v in self.framework_weights.items()
        }

        logger.info(
            f"Learned from outcome: {actual_outcome} "
            f"(positive={outcome_positive}). Updated weights: "
            f"{self.framework_weights}"
        )

    def get_framework_performance(self) -> Dict[str, float]:
        """Get accuracy statistics for each framework.

        Returns:
            Dictionary of framework accuracies
        """
        performance = {}
        for framework, stats in self.framework_accuracy.items():
            if stats["total"] > 0:
                accuracy = stats["correct"] / stats["total"]
                performance[framework.value] = accuracy
            else:
                performance[framework.value] = 0.0

        return performance
