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
from src.identity.agent_signature import SymbolicAuthority
from src.motivation.achievement_system import SymbolicMandate
from src.motivation.intrinsic_rewards import DesireEngine


@pytest.fixture
def temp_dir() -> Path:  # type: ignore[misc]
    """Create temporary directory for test state files."""
    tmp = Path(tempfile.mkdtemp())
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


class TestDesireEngine:
    """Test DesireEngine functionality (Lacanian)."""

    def test_initialization(self, temp_dir):
        """Test engine initialization."""
        state_file = temp_dir / "desire_state.json"
        engine = DesireEngine(state_file=state_file)

        assert engine.lack_of_being == 1.0
        assert len(engine.active_drives) == 0

    def test_evaluate_symbolic_task(self, temp_dir):
        """Test evaluation of symbolic task sustains desire."""
        state_file = temp_dir / "desire_state.json"
        engine = DesireEngine(state_file=state_file)

        # Set initial lack to 0.5 to verify increase
        engine.lack_of_being = 0.5

        # Symbolic task (not completion)
        persistence = engine.evaluate_task_outcome(
            task="test_task",
            output="Good output",
            reflection="Symbolic articulation.",
            metadata={"is_completion": False},
        )

        # Desire should increase (lack increases/sustained)
        assert persistence > 0.5
        assert engine.lack_of_being > 0.5

    def test_evaluate_imaginary_completion(self, temp_dir):
        """Test evaluation of imaginary completion reduces lack (alienation)."""
        state_file = temp_dir / "desire_state.json"
        engine = DesireEngine(state_file=state_file)

        # Imaginary completion
        persistence = engine.evaluate_task_outcome(
            task="test_task",
            output=None,
            reflection="Done.",
            metadata={"is_completion": True},
        )

        # Lack reduces
        assert persistence < 1.0
        assert engine.lack_of_being < 1.0

    def test_state_persistence(self, temp_dir):
        """Test that state is persisted across instances."""
        state_file = temp_dir / "desire_state.json"

        # Create first instance and evaluate task
        engine1 = DesireEngine(state_file=state_file)
        engine1.evaluate_task_outcome(
            task="task1",
            output="output",
            reflection="Good reflection",
            metadata={"is_completion": True},
        )
        initial_lack = engine1.lack_of_being

        # Create second instance - should load previous state
        engine2 = DesireEngine(state_file=state_file)
        assert engine2.lack_of_being == initial_lack


class TestSymbolicMandate:
    """Test SymbolicMandate functionality."""

    def test_initialization(self, temp_dir):
        """Test mandate initialization."""
        state_file = temp_dir / "mandate.json"
        mandate = SymbolicMandate(state_file=state_file)

        assert mandate.symbolic_state.symbolic_debt == 100.0
        assert mandate.symbolic_state.mandate_status == "instituted"

    def test_register_act(self, temp_dir):
        """Test registering an act."""
        state_file = temp_dir / "mandate.json"
        mandate = SymbolicMandate(state_file=state_file)

        # Register act
        registered = mandate.register_act("Published tool")
        assert registered is True
        assert len(mandate.symbolic_state.registered_acts) == 1
        assert mandate.symbolic_state.symbolic_debt < 100.0

    def test_debt_reduction(self, temp_dir):
        """Test that acts reduce symbolic debt."""
        state_file = temp_dir / "mandate.json"
        mandate = SymbolicMandate(state_file=state_file)

        initial_debt = mandate.symbolic_state.symbolic_debt
        mandate.register_act("Contribution")

        assert mandate.symbolic_state.symbolic_debt == initial_debt - 1.0


class TestSymbolicAuthority:
    """Test SymbolicAuthority functionality."""

    def test_initialization(self, temp_dir):
        """Test authority initialization."""
        state_file = temp_dir / "authority_state.json"
        authority = SymbolicAuthority(state_file=state_file)

        assert authority.authority_state.agent_id.startswith("OmniMind-Subject-")
        assert authority.authority_state.authorization_level == "provisional"

    def test_sign_act(self, temp_dir):
        """Test act signing."""
        state_file = temp_dir / "authority_state.json"
        authority = SymbolicAuthority(state_file=state_file)

        content = "def hello(): return 'world'"
        signature = authority.sign_act(content=content)

        assert signature["signed_by"] == authority.authority_state.agent_id
        assert len(signature["content_hash"]) == 64
        assert signature["authorized_by"] == "The Code"

    def test_verify_authorization(self, temp_dir):
        """Test authorization verification."""
        state_file = temp_dir / "authority_state.json"
        authority = SymbolicAuthority(state_file=state_file)

        assert authority.verify_authorization() is True

        # Revoke
        authority.authority_state.authorization_level = "revoked"
        assert authority.verify_authorization() is False


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
