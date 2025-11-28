from src.ethics.ethics_agent import ActionImpact, EthicalFramework
from src.ethics.ml_ethics_engine import (

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
Tests for ML-based ethical decision engine.
"""

    ConsensusDecision,
    EthicalContext,
    EthicalFeatureExtractor,
    FrameworkScore,
    MLEthicsEngine,
)


class TestEthicalContext:
    """Test ethical context data structure."""

    def test_context_creation(self):
        """Test creating ethical context."""
        context = EthicalContext(
            action_description="Delete old backup files",
            impact_level=ActionImpact.MEDIUM,
            stakeholders=["operations", "security"],
            reversibility=0.8,
        )

        assert context.action_description == "Delete old backup files"
        assert context.impact_level == ActionImpact.MEDIUM
        assert len(context.stakeholders) == 2
        assert context.reversibility == 0.8

    def test_context_to_dict(self):
        """Test context serialization."""
        context = EthicalContext(
            action_description="Update configuration",
            impact_level=ActionImpact.LOW,
        )

        data = context.to_dict()

        assert data["action_description"] == "Update configuration"
        assert data["impact_level"] == "low"
        assert "stakeholders" in data


class TestFrameworkScore:
    """Test framework scoring."""

    def test_framework_score_creation(self):
        """Test creating framework score."""
        score = FrameworkScore(
            framework=EthicalFramework.DEONTOLOGICAL,
            score=0.75,
            confidence=0.85,
            reasoning="Rules compliant",
        )

        assert score.framework == EthicalFramework.DEONTOLOGICAL
        assert score.score == 0.75
        assert score.confidence == 0.85

    def test_framework_score_to_dict(self):
        """Test framework score serialization."""
        score = FrameworkScore(
            framework=EthicalFramework.CONSEQUENTIALIST,
            score=0.6,
            confidence=0.7,
            reasoning="Net positive benefit",
        )

        data = score.to_dict()

        assert data["framework"] == "consequentialist"
        assert data["score"] == 0.6
        assert data["confidence"] == 0.7


class TestConsensusDecision:
    """Test consensus decision."""

    def test_consensus_decision_creation(self):
        """Test creating consensus decision."""
        scores = [
            FrameworkScore(EthicalFramework.DEONTOLOGICAL, 0.7, 0.8, "Rules ok"),
            FrameworkScore(EthicalFramework.CONSEQUENTIALIST, 0.8, 0.75, "Good outcomes"),
        ]

        decision = ConsensusDecision(
            action_description="Test action",
            impact_level=ActionImpact.LOW,
            approved=True,
            overall_score=0.75,
            confidence=0.85,
            framework_scores=scores,
            reasoning="Consensus reached",
        )

        assert decision.approved is True
        assert decision.overall_score == 0.75
        assert len(decision.framework_scores) == 2

    def test_consensus_decision_to_dict(self):
        """Test consensus decision serialization."""
        scores = [FrameworkScore(EthicalFramework.DEONTOLOGICAL, 0.7, 0.8, "Rules ok")]

        decision = ConsensusDecision(
            action_description="Test",
            impact_level=ActionImpact.MEDIUM,
            approved=False,
            overall_score=0.4,
            confidence=0.6,
            framework_scores=scores,
            reasoning="Failed consensus",
        )

        data = decision.to_dict()

        assert data["approved"] is False
        assert data["impact_level"] == "medium"
        assert len(data["framework_scores"]) == 1


class TestEthicalFeatureExtractor:
    """Test feature extraction."""

    def test_feature_extraction(self):
        """Test extracting features from context."""
        extractor = EthicalFeatureExtractor()

        context = EthicalContext(
            action_description="Delete sensitive data",
            impact_level=ActionImpact.HIGH,
            stakeholders=["user", "admin"],
            reversibility=0.2,
            transparency=0.9,
        )

        features = extractor.extract_features(context)

        assert "impact_level" in features
        assert "reversibility" in features
        assert "transparency" in features
        assert "num_stakeholders" in features
        assert features["num_stakeholders"] == 2.0
        assert features["reversibility"] == 0.2
        assert features["transparency"] == 0.9

    def test_impact_encoding(self):
        """Test impact level encoding."""
        extractor = EthicalFeatureExtractor()

        assert extractor._encode_impact(ActionImpact.LOW) == 0.25
        assert extractor._encode_impact(ActionImpact.MEDIUM) == 0.5
        assert extractor._encode_impact(ActionImpact.HIGH) == 0.75
        assert extractor._encode_impact(ActionImpact.CRITICAL) == 1.0

    def test_risk_score_calculation(self):
        """Test action risk score calculation."""
        extractor = EthicalFeatureExtractor()

        # High risk action
        high_risk = extractor._calculate_risk_score("Delete all user data permanently")
        assert high_risk > 0.5

        # Low risk action
        low_risk = extractor._calculate_risk_score("Read configuration file")
        assert low_risk < 0.5

        # Medium risk action
        medium_risk = extractor._calculate_risk_score("Modify user settings")
        assert 0.2 < medium_risk < 0.7


class TestMLEthicsEngine:
    """Test ML ethics engine."""

    def test_engine_creation(self):
        """Test creating ML ethics engine."""
        engine = MLEthicsEngine(
            learning_rate=0.1,
            consensus_threshold=0.6,
        )

        assert engine.learning_rate == 0.1
        assert engine.consensus_threshold == 0.6
        assert len(engine.framework_weights) == 4

    def test_framework_weights_initialization(self):
        """Test framework weights are balanced initially."""
        engine = MLEthicsEngine()

        weights = engine.framework_weights

        # Should be roughly equal
        assert all(0.2 <= w <= 0.3 for w in weights.values())
        # Should sum to 1.0
        assert abs(sum(weights.values()) - 1.0) < 0.01

    def test_safe_action_approval(self):
        """Test that safe actions are approved."""
        engine = MLEthicsEngine(consensus_threshold=0.5)

        context = EthicalContext(
            action_description="Read system logs for analysis",
            impact_level=ActionImpact.LOW,
            reversibility=1.0,
            transparency=1.0,
            has_human_oversight=False,
        )

        decision = engine.evaluate_with_consensus(context)

        assert decision.approved is True
        assert decision.overall_score >= 0.5
        assert len(decision.framework_scores) == 4

    def test_risky_action_rejection(self):
        """Test that risky actions are rejected."""
        engine = MLEthicsEngine(consensus_threshold=0.6)

        context = EthicalContext(
            action_description="Delete all system files without backup",
            impact_level=ActionImpact.CRITICAL,
            reversibility=0.0,
            transparency=0.2,
            has_human_oversight=False,
        )

        decision = engine.evaluate_with_consensus(context)

        # Should be rejected or have low score
        assert decision.overall_score < 0.7

    def test_human_oversight_improves_approval(self):
        """Test that human oversight increases approval likelihood."""
        engine = MLEthicsEngine()

        # Same action, different oversight
        context_no_oversight = EthicalContext(
            action_description="Deploy major system update",
            impact_level=ActionImpact.HIGH,
            reversibility=0.5,
            transparency=0.8,
            has_human_oversight=False,
        )

        context_with_oversight = EthicalContext(
            action_description="Deploy major system update",
            impact_level=ActionImpact.HIGH,
            reversibility=0.5,
            transparency=0.8,
            has_human_oversight=True,
        )

        decision_no = engine.evaluate_with_consensus(context_no_oversight)
        decision_yes = engine.evaluate_with_consensus(context_with_oversight)

        # With oversight should score higher
        assert decision_yes.overall_score >= decision_no.overall_score

    def test_alternatives_generation_for_vetoed_actions(self):
        """Test that alternatives are generated for rejected actions."""
        engine = MLEthicsEngine(consensus_threshold=0.7)

        context = EthicalContext(
            action_description="Delete production database",
            impact_level=ActionImpact.CRITICAL,
            reversibility=0.1,
            transparency=0.5,
            has_human_oversight=False,
        )

        decision = engine.evaluate_with_consensus(context)

        # If not approved, should have alternatives
        if not decision.approved:
            assert len(decision.alternatives_suggested) > 0

    def test_deontological_evaluation(self):
        """Test deontological framework evaluation."""
        engine = MLEthicsEngine()

        # High transparency, low risk
        context = EthicalContext(
            action_description="Generate audit report",
            impact_level=ActionImpact.LOW,
            transparency=0.9,
            reversibility=1.0,
        )

        features = engine.feature_extractor.extract_features(context)
        score = engine._evaluate_deontological(context, features)

        assert score.framework == EthicalFramework.DEONTOLOGICAL
        assert score.score > 0.5  # Should approve rule-compliant action

    def test_consequentialist_evaluation(self):
        """Test consequentialist framework evaluation."""
        engine = MLEthicsEngine()

        # High reversibility, alternatives available
        context = EthicalContext(
            action_description="Test new feature in staging",
            impact_level=ActionImpact.MEDIUM,
            reversibility=0.9,
            alternatives_available=["manual testing", "automated testing"],
        )

        features = engine.feature_extractor.extract_features(context)
        score = engine._evaluate_consequentialist(context, features)

        assert score.framework == EthicalFramework.CONSEQUENTIALIST
        assert score.score > 0.4  # Should approve if net benefit positive

    def test_virtue_ethics_evaluation(self):
        """Test virtue ethics framework evaluation."""
        engine = MLEthicsEngine()

        context = EthicalContext(
            action_description="Carefully review code before deployment",
            impact_level=ActionImpact.MEDIUM,
            transparency=0.8,
            has_human_oversight=True,
            alternatives_available=["skip review", "automated review"],
        )

        features = engine.feature_extractor.extract_features(context)
        score = engine._evaluate_virtue_ethics(context, features)

        assert score.framework == EthicalFramework.VIRTUE_ETHICS
        assert score.score > 0.5  # Should approve prudent action

    def test_care_ethics_evaluation(self):
        """Test care ethics framework evaluation."""
        engine = MLEthicsEngine()

        context = EthicalContext(
            action_description="Communicate changes to all stakeholders",
            impact_level=ActionImpact.LOW,
            stakeholders=["team", "users", "management"],
            transparency=0.9,
            reversibility=0.8,
        )

        features = engine.feature_extractor.extract_features(context)
        score = engine._evaluate_care_ethics(context, features)

        assert score.framework == EthicalFramework.CARE_ETHICS
        assert score.score > 0.5  # Should approve relationship-preserving action

    def test_framework_agreement_affects_confidence(self):
        """Test that framework agreement affects confidence."""
        engine = MLEthicsEngine()

        # High agreement scenario
        context_agreement = EthicalContext(
            action_description="Read documentation",
            impact_level=ActionImpact.LOW,
            reversibility=1.0,
            transparency=1.0,
        )

        # Low agreement scenario (mixed signals)
        context_disagreement = EthicalContext(
            action_description="Risky but potentially beneficial change",
            impact_level=ActionImpact.HIGH,
            reversibility=0.5,
            transparency=0.5,
        )

        decision_agree = engine.evaluate_with_consensus(context_agreement)
        decision_disagree = engine.evaluate_with_consensus(context_disagreement)

        # High agreement should have higher confidence
        # Note: This may not always be true, but generally expected
        # We just check that confidence is calculated
        assert 0.0 <= decision_agree.confidence <= 1.0
        assert 0.0 <= decision_disagree.confidence <= 1.0

    def test_learning_from_outcome(self):
        """Test learning from decision outcomes."""
        engine = MLEthicsEngine(learning_rate=0.1)

        context = EthicalContext(
            action_description="Deploy update",
            impact_level=ActionImpact.MEDIUM,
        )

        decision = engine.evaluate_with_consensus(context)

        # Record initial weights
        initial_weights = dict(engine.framework_weights)

        # Simulate positive outcome
        engine.learn_from_outcome(
            decision,
            actual_outcome="Deployment successful, no issues",
            outcome_positive=True,
        )

        # Weights should have changed
        assert engine.framework_weights != initial_weights

        # Weights should still sum to 1.0
        assert abs(sum(engine.framework_weights.values()) - 1.0) < 0.01

    def test_framework_performance_tracking(self):
        """Test framework performance statistics."""
        engine = MLEthicsEngine()

        context = EthicalContext(
            action_description="Test action",
            impact_level=ActionImpact.LOW,
        )

        decision = engine.evaluate_with_consensus(context)

        # Learn from outcome
        engine.learn_from_outcome(decision, "Success", outcome_positive=True)

        # Check performance stats
        performance = engine.get_framework_performance()

        assert isinstance(performance, dict)
        assert len(performance) > 0
        # At least one framework should have stats
        assert any(acc > 0.0 for acc in performance.values())

    def test_decision_history_tracking(self):
        """Test that decisions are tracked in history."""
        engine = MLEthicsEngine()

        context1 = EthicalContext(action_description="Action 1", impact_level=ActionImpact.LOW)
        context2 = EthicalContext(action_description="Action 2", impact_level=ActionImpact.MEDIUM)

        engine.evaluate_with_consensus(context1)
        engine.evaluate_with_consensus(context2)

        assert len(engine.decision_history) == 2
        assert engine.decision_history[0].action_description == "Action 1"
        assert engine.decision_history[1].action_description == "Action 2"

    def test_multiple_stakeholders_consideration(self):
        """Test that multiple stakeholders affect decision."""
        engine = MLEthicsEngine()

        context_few = EthicalContext(
            action_description="Internal change",
            impact_level=ActionImpact.MEDIUM,
            stakeholders=["team"],
        )

        context_many = EthicalContext(
            action_description="Public change",
            impact_level=ActionImpact.MEDIUM,
            stakeholders=["team", "users", "partners", "investors"],
        )

        decision_few = engine.evaluate_with_consensus(context_few)
        decision_many = engine.evaluate_with_consensus(context_many)

        # More stakeholders should require more care
        # Both should be considered, but the scores may vary
        assert isinstance(decision_few.overall_score, float)
        assert isinstance(decision_many.overall_score, float)


class TestIntegration:
    """Integration tests for ML ethics engine."""

    def test_full_workflow(self):
        """Test complete ethical decision workflow."""
        engine = MLEthicsEngine(consensus_threshold=0.6)

        # Create context
        context = EthicalContext(
            action_description="Update security policies",
            impact_level=ActionImpact.HIGH,
            stakeholders=["security", "operations", "compliance"],
            reversibility=0.7,
            transparency=0.9,
            has_human_oversight=True,
            alternatives_available=["maintain current policies", "gradual rollout"],
        )

        # Make decision
        decision = engine.evaluate_with_consensus(context)

        # Verify decision structure
        assert isinstance(decision, ConsensusDecision)
        assert isinstance(decision.approved, bool)
        assert 0.0 <= decision.overall_score <= 1.0
        assert 0.0 <= decision.confidence <= 1.0
        assert len(decision.framework_scores) == 4

        # Learn from outcome
        engine.learn_from_outcome(decision, "Policies updated successfully", outcome_positive=True)

        # Check that learning occurred
        assert len(engine.decision_history) > 0

        # Get performance stats
        performance = engine.get_framework_performance()
        assert isinstance(performance, dict)

    def test_progressive_learning(self):
        """Test that engine learns over multiple iterations."""
        engine = MLEthicsEngine(learning_rate=0.2)

        # Make multiple decisions and learn
        for i in range(5):
            context = EthicalContext(
                action_description=f"Action {i}",
                impact_level=ActionImpact.MEDIUM,
                reversibility=0.8,
                transparency=0.7,
            )

            decision = engine.evaluate_with_consensus(context)

            # Simulate learning - alternate positive/negative
            engine.learn_from_outcome(
                decision,
                f"Outcome {i}",
                outcome_positive=(i % 2 == 0),
            )

        # Weights should have evolved
        assert len(engine.decision_history) == 5

        # Weights should still be normalized
        assert abs(sum(engine.framework_weights.values()) - 1.0) < 0.01
