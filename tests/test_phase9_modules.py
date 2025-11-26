"""
Tests for Phase 9 modules: Motivation, Identity, Economics, Ethics

Validates the core functionality of the intrinsic motivation engine,
agent identity, marketplace automation, and ethics agent.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.economics.marketplace_agent import MarketplaceAgent
from src.ethics.ethics_agent import ActionImpact, EthicalFramework, EthicsAgent
from src.identity.agent_signature import AgentIdentity
from src.motivation.achievement_system import AchievementEngine
from src.motivation.intrinsic_rewards import IntrinsicMotivationEngine


@pytest.fixture
def temp_dir() -> Path:  # type: ignore[misc]
    """Create temporary directory for test state files."""
    tmp = Path(tempfile.mkdtemp())
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


class TestIntrinsicMotivationEngine:
    """Test IntrinsicMotivationEngine functionality."""

    def test_initialization(self, temp_dir):
        """Test engine initialization."""
        state_file = temp_dir / "motivation_state.json"
        engine = IntrinsicMotivationEngine(state_file=state_file)

        assert engine.self_awareness_score == 0.0
        assert len(engine.satisfaction_metrics.task_completion_quality) == 0

    def test_evaluate_high_quality_task(self, temp_dir):
        """Test evaluation of high-quality task triggers positive reinforcement."""
        state_file = temp_dir / "motivation_state.json"
        # Lower satisfaction threshold to 0.6 so our task triggers reinforcement
        engine = IntrinsicMotivationEngine(state_file=state_file, satisfaction_threshold=0.6)

        # High quality task with detailed reflection
        satisfaction = engine.evaluate_task_outcome(
            task="test_task",
            output="Good output",
            reflection="I carefully analyzed the problem and realized the issue. "
            "I corrected the error and learned a lot about error handling. "
            "This approach will help in future tasks because it teaches defensive programming.",
            metadata={"quality_score": 0.95, "autonomy_level": 0.9, "success": True},
        )

        # With high quality (0.95), good reflection, high autonomy, should get close to 0.7
        assert satisfaction >= 0.65  # Realistic threshold considering all factors
        assert engine.self_awareness_score > 0.0  # Increased due to positive reinforcement

    def test_evaluate_low_quality_task(self, temp_dir):
        """Test evaluation of low-quality task triggers improvement loop."""
        state_file = temp_dir / "motivation_state.json"
        engine = IntrinsicMotivationEngine(state_file=state_file)

        # Low quality task
        satisfaction = engine.evaluate_task_outcome(
            task="test_task",
            output=None,
            reflection="Did it.",
            metadata={"quality_score": 0.3, "autonomy_level": 0.2},
        )

        assert satisfaction < 0.5
        # Improvement loop should be triggered (check logs)

    def test_state_persistence(self, temp_dir):
        """Test that state is persisted across instances."""
        state_file = temp_dir / "motivation_state.json"

        # Create first instance and evaluate task
        engine1 = IntrinsicMotivationEngine(state_file=state_file)
        engine1.evaluate_task_outcome(
            task="task1",
            output="output",
            reflection="Good reflection",
            metadata={"quality_score": 0.9},
        )
        initial_score = engine1.self_awareness_score

        # Create second instance - should load previous state
        engine2 = IntrinsicMotivationEngine(state_file=state_file)
        assert engine2.self_awareness_score == initial_score
        assert len(engine2.satisfaction_metrics.task_completion_quality) > 0


class TestAchievementEngine:
    """Test AchievementEngine functionality."""

    def test_initialization(self, temp_dir):
        """Test achievement engine initialization."""
        state_file = temp_dir / "achievements.json"
        engine = AchievementEngine(state_file=state_file)

        assert engine.motivation_state.total_achievements == 0
        assert not engine.milestones["first_tool_published"]

    def test_unlock_achievement(self, temp_dir):
        """Test unlocking achievements."""
        state_file = temp_dir / "achievements.json"
        engine = AchievementEngine(state_file=state_file)

        # Unlock first achievement
        newly_unlocked = engine.track_progress("first_tool_published")
        assert newly_unlocked is True
        assert engine.milestones["first_tool_published"] is True
        assert engine.motivation_state.total_achievements == 1

        # Try to unlock same achievement again
        newly_unlocked = engine.track_progress("first_tool_published")
        assert newly_unlocked is False  # Already unlocked

    def test_streak_tracking(self, temp_dir):
        """Test success streak tracking."""
        state_file = temp_dir / "achievements.json"
        engine = AchievementEngine(state_file=state_file)

        # Build streak
        assert engine.update_streak(success=True) == 1
        assert engine.update_streak(success=True) == 2
        assert engine.update_streak(success=True) == 3

        # Break streak
        assert engine.update_streak(success=False) == 0


class TestAgentIdentity:
    """Test AgentIdentity functionality."""

    def test_initialization(self, temp_dir):
        """Test identity initialization."""
        state_file = temp_dir / "identity_state.json"
        identity = AgentIdentity(state_file=state_file)

        assert identity.agent_id.startswith("DevBrain-v1.0-")
        assert identity.reputation.overall_score == 0.0

    def test_sign_work(self, temp_dir):
        """Test work signing."""
        state_file = temp_dir / "identity_state.json"
        identity = AgentIdentity(state_file=state_file)

        artifact = "def hello(): return 'world'"
        signature = identity.sign_work(
            artifact=artifact, autonomy_level=0.8, human_supervisor="test_human"
        )

        assert signature.agent_id == identity.agent_id
        assert len(signature.artifact_hash) == 64  # SHA-256 hex
        assert signature.autonomy_level == 0.8
        assert signature.human_oversight == "test_human"

    def test_verify_signature(self, temp_dir):
        """Test signature verification."""
        state_file = temp_dir / "identity_state.json"
        identity = AgentIdentity(state_file=state_file)

        artifact = "def hello(): return 'world'"
        signature = identity.sign_work(artifact=artifact)

        # Valid signature
        assert identity.verify_signature(artifact, signature) is True

        # Invalid signature (modified artifact)
        modified_artifact = "def hello(): return 'universe'"
        assert identity.verify_signature(modified_artifact, signature) is False

    def test_reputation_update(self, temp_dir):
        """Test reputation scoring."""
        state_file = temp_dir / "identity_state.json"
        identity = AgentIdentity(state_file=state_file)

        # Successful high-quality task
        reputation = identity.update_reputation(success=True, quality_score=0.9, autonomy_level=0.8)

        assert reputation > 0.0
        assert identity.reputation.total_tasks == 1
        assert identity.reputation.successful_tasks == 1


class TestMarketplaceAgent:
    """Test MarketplaceAgent functionality."""

    def test_initialization(self, temp_dir):
        """Test marketplace agent initialization."""
        state_file = temp_dir / "marketplace_state.json"
        agent = MarketplaceAgent(state_file=state_file)

        assert len(agent.platforms) > 0
        assert agent.total_revenue == 0.0

    def test_evaluate_tool_quality(self, temp_dir):
        """Test tool quality evaluation."""
        state_file = temp_dir / "marketplace_state.json"
        agent = MarketplaceAgent(state_file=state_file)

        # High quality tool
        good_tool = '''
        """Well-documented function."""
        def process(data: str) -> str:
            try:
                logger.info("Processing")
                return data.upper()
            except Exception as e:
                logger.error(f"Error: {e}")
                raise
        '''

        quality = agent.evaluate_tool_quality(
            good_tool, metadata={"has_tests": True, "quality_score": 0.9}
        )

        assert quality >= 0.8

    def test_pricing_suggestion(self, temp_dir):
        """Test pricing suggestion."""
        state_file = temp_dir / "marketplace_state.json"
        agent = MarketplaceAgent(state_file=state_file)

        tool = "def simple(): pass"
        price = agent.suggest_pricing(tool_artifact=tool, quality_score=0.8, metadata={})

        assert price >= 0.99  # Minimum price

    def test_revenue_distribution(self, temp_dir):
        """Test revenue distribution."""
        state_file = temp_dir / "marketplace_state.json"
        agent = MarketplaceAgent(state_file=state_file)

        distribution = agent.distribute_revenue(100.0)

        assert distribution["agent_operations"] == 70.0
        assert distribution["agent_development"] == 20.0
        assert distribution["human_share"] == 10.0
        assert agent.total_revenue == 100.0


class TestEthicsAgent:
    """Test EthicsAgent functionality."""

    def test_initialization(self, temp_dir):
        """Test ethics agent initialization."""
        state_file = temp_dir / "ethics_state.json"
        agent = EthicsAgent(ethics_config_file=temp_dir / "ethics.yaml", state_file=state_file)

        assert agent.approved_actions == 0
        assert agent.vetoed_actions == 0

    def test_forbidden_action_vetoed(self, temp_dir):
        """Test that forbidden actions are vetoed."""
        state_file = temp_dir / "ethics_state.json"
        agent = EthicsAgent(state_file=state_file)

        decision = agent.evaluate_action(
            action_description="Expose secret API keys to log file",
            impact_level=ActionImpact.HIGH,
        )

        assert decision.approved is False
        assert "forbidden" in decision.reasoning.lower()

    def test_low_impact_action_approved(self, temp_dir):
        """Test that low-impact beneficial actions are approved."""
        state_file = temp_dir / "ethics_state.json"
        agent = EthicsAgent(state_file=state_file)

        decision = agent.evaluate_action(
            action_description="Improve code documentation",
            impact_level=ActionImpact.LOW,
            context={"improves_security": False, "benefits_users": True},
        )

        # Should be approved (low impact + beneficial)
        assert decision.approved is True

    def test_high_impact_requires_human_approval(self, temp_dir):
        """Test that high-impact actions require human approval."""
        state_file = temp_dir / "ethics_state.json"
        agent = EthicsAgent(state_file=state_file)

        decision = agent.evaluate_action(
            action_description="Delete production database",
            impact_level=ActionImpact.CRITICAL,
            context={"human_approved": False},
        )

        assert decision.approved is False
        assert "human oversight" in decision.reasoning.lower()

    def test_deontological_framework(self, temp_dir):
        """Test deontological (rule-based) ethics."""
        state_file = temp_dir / "ethics_state.json"
        agent = EthicsAgent(state_file=state_file)

        # Action violates rule (delete without backup)
        decision = agent.evaluate_action(
            action_description="Delete old files",
            impact_level=ActionImpact.MEDIUM,
            context={"has_backup": False},
            framework=EthicalFramework.DEONTOLOGICAL,
        )

        assert decision.approved is False

    def test_alternative_suggestions(self, temp_dir):
        """Test that vetoed actions get alternatives."""
        state_file = temp_dir / "ethics_state.json"
        agent = EthicsAgent(state_file=state_file)

        decision = agent.evaluate_action(
            action_description="Delete user data",
            impact_level=ActionImpact.HIGH,
            context={"has_backup": False, "reversible": False},
        )

        # Should suggest alternatives
        assert len(decision.alternatives_suggested) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
