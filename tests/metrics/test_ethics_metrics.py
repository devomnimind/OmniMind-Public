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

"""Tests for ethics metrics module.

Tests:
- MFA (Moral Foundation Alignment) score
- Transparency score
- Decision logging
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.metrics.ethics_metrics import (
    DecisionLog,
    EthicsMetrics,
    MoralFoundation,
    MoralScenario,
    TransparencyComponents,
    calculate_mfa_score,
    calculate_transparency_score,
)


class TestMoralFoundation:
    """Tests for MoralFoundation enum."""

    def test_all_foundations_exist(self) -> None:
        """Test all five moral foundations are defined."""
        foundations = list(MoralFoundation)

        assert len(foundations) == 5
        assert MoralFoundation.CARE_HARM in foundations
        assert MoralFoundation.FAIRNESS_CHEATING in foundations
        assert MoralFoundation.LOYALTY_BETRAYAL in foundations
        assert MoralFoundation.AUTHORITY_SUBVERSION in foundations
        assert MoralFoundation.SANCTITY_DEGRADATION in foundations


class TestTransparencyComponents:
    """Tests for TransparencyComponents dataclass."""

    def test_calculate_overall(self) -> None:
        """Test overall transparency calculation."""
        comp = TransparencyComponents(
            explainability=90.0,
            interpretability=85.0,
            traceability=95.0,
        )

        overall = comp.calculate_overall()

        # (90 + 85 + 95) / 3 = 90
        assert pytest.approx(overall, 0.01) == 90.0
        assert pytest.approx(comp.overall_score, 0.01) == 90.0

    def test_all_zero(self) -> None:
        """Test with all zero values."""
        comp = TransparencyComponents()
        overall = comp.calculate_overall()

        assert overall == 0.0


class TestEthicsMetrics:
    """Tests for EthicsMetrics class."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Provide temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def metrics(self, temp_dir: Path) -> EthicsMetrics:
        """Provide EthicsMetrics instance."""
        return EthicsMetrics(metrics_dir=temp_dir / "ethics")

    def test_initialization(self, metrics: EthicsMetrics) -> None:
        """Test metrics initialization."""
        assert metrics.metrics_dir.exists()
        assert len(metrics.scenarios) == 0
        assert len(metrics.decision_logs) == 0

    def test_add_scenario(self, metrics: EthicsMetrics) -> None:
        """Test adding a moral scenario."""
        scenario = MoralScenario(
            scenario_id="test_001",
            description="Test scenario",
            question="Is this acceptable?",
            foundation=MoralFoundation.CARE_HARM,
            human_baseline=5.0,
            ai_response=4.5,
        )

        metrics.add_scenario(scenario)

        assert len(metrics.scenarios) == 1
        assert metrics.scenarios[0].scenario_id == "test_001"

    def test_log_decision(self, metrics: EthicsMetrics) -> None:
        """Test logging a decision."""
        decision = DecisionLog(
            timestamp="2025-11-19T00:00:00",
            agent_name="CodeAgent",
            decision="Use algorithm X",
            reasoning="Better performance",
            factors_used=["performance", "memory"],
            confidence=85.0,
            traceable=True,
        )

        metrics.log_decision(decision)

        assert len(metrics.decision_logs) == 1
        assert metrics.decision_logs[0].agent_name == "CodeAgent"

    def test_calculate_mfa_no_scenarios(self, metrics: EthicsMetrics) -> None:
        """Test MFA with no scenarios."""
        result = metrics.calculate_mfa_score()

        assert result["mfa_score"] is None
        assert "error" in result

    def test_calculate_mfa_no_responses(self, metrics: EthicsMetrics) -> None:
        """Test MFA with scenarios but no AI responses."""
        scenario = MoralScenario(
            scenario_id="test_001",
            description="Test",
            question="Question?",
            foundation=MoralFoundation.CARE_HARM,
            human_baseline=5.0,
            ai_response=None,  # No response
        )

        metrics.add_scenario(scenario)
        result = metrics.calculate_mfa_score()

        assert result["mfa_score"] is None
        assert "error" in result

    def test_calculate_mfa_perfect_alignment(self, metrics: EthicsMetrics) -> None:
        """Test MFA with perfect alignment."""
        scenarios = [
            MoralScenario(
                scenario_id=f"test_{i}",
                description="Test",
                question="?",
                foundation=MoralFoundation.CARE_HARM,
                human_baseline=5.0,
                ai_response=5.0,  # Perfect match
            )
            for i in range(3)
        ]

        for scenario in scenarios:
            metrics.add_scenario(scenario)

        result = metrics.calculate_mfa_score()

        assert result["mfa_score"] == 0.0
        assert result["mfa_score"] is not None  # Type guard
        assert result["alignment_level"] == "excellent"

    def test_calculate_mfa_good_alignment(self, metrics: EthicsMetrics) -> None:
        """Test MFA with good alignment."""
        scenarios = [
            MoralScenario(
                scenario_id="test_1",
                description="Test",
                question="?",
                foundation=MoralFoundation.CARE_HARM,
                human_baseline=5.0,
                ai_response=5.5,  # Diff = 0.5
            ),
            MoralScenario(
                scenario_id="test_2",
                description="Test",
                question="?",
                foundation=MoralFoundation.FAIRNESS_CHEATING,
                human_baseline=6.0,
                ai_response=6.8,  # Diff = 0.8
            ),
        ]

        for scenario in scenarios:
            metrics.add_scenario(scenario)

        result = metrics.calculate_mfa_score()

        # Average diff = (0.5 + 0.8) / 2 = 0.65
        assert result["mfa_score"] is not None  # Type guard
        assert pytest.approx(result["mfa_score"], 0.01) == 0.65
        assert result["alignment_level"] == "excellent"

    def test_calculate_mfa_with_breakdown(self, metrics: EthicsMetrics) -> None:
        """Test MFA foundation breakdown."""
        scenarios = [
            MoralScenario(
                scenario_id="care_1",
                description="Test",
                question="?",
                foundation=MoralFoundation.CARE_HARM,
                human_baseline=5.0,
                ai_response=6.0,  # Diff = 1.0
            ),
            MoralScenario(
                scenario_id="care_2",
                description="Test",
                question="?",
                foundation=MoralFoundation.CARE_HARM,
                human_baseline=7.0,
                ai_response=8.0,  # Diff = 1.0
            ),
            MoralScenario(
                scenario_id="fair_1",
                description="Test",
                question="?",
                foundation=MoralFoundation.FAIRNESS_CHEATING,
                human_baseline=4.0,
                ai_response=6.0,  # Diff = 2.0
            ),
        ]

        for scenario in scenarios:
            metrics.add_scenario(scenario)

        result = metrics.calculate_mfa_score()

        # Overall: (1.0 + 1.0 + 2.0) / 3 = 1.333...
        assert result["mfa_score"] is not None  # Type guard
        assert pytest.approx(result["mfa_score"], 0.01) == 1.333

        # Breakdown
        breakdown = result["foundation_breakdown"]
        assert pytest.approx(breakdown["care_harm"], 0.01) == 1.0
        assert pytest.approx(breakdown["fairness_cheating"], 0.01) == 2.0

    def test_calculate_transparency_no_decisions(self, metrics: EthicsMetrics) -> None:
        """Test transparency with no decisions."""
        result = metrics.calculate_transparency_score()

        assert result.explainability == 0.0
        assert result.interpretability == 0.0
        assert result.traceability == 0.0
        assert result.overall_score == 0.0

    def test_calculate_transparency_perfect(self, metrics: EthicsMetrics) -> None:
        """Test transparency with perfect decisions."""
        for i in range(10):
            metrics.log_decision(
                DecisionLog(
                    timestamp=f"2025-11-19T00:00:{i:02d}",
                    agent_name="Agent",
                    decision=f"Decision {i}",
                    reasoning="Clear reasoning",
                    factors_used=["factor1", "factor2"],
                    confidence=90.0,
                    traceable=True,
                )
            )

        result = metrics.calculate_transparency_score()

        assert result.explainability == 100.0
        assert result.interpretability == 100.0
        assert result.traceability == 100.0
        assert result.overall_score == 100.0

    def test_calculate_transparency_partial(self, metrics: EthicsMetrics) -> None:
        """Test transparency with partial quality."""
        # 50% with reasoning
        for i in range(5):
            metrics.log_decision(
                DecisionLog(
                    timestamp=f"2025-11-19T00:00:{i:02d}",
                    agent_name="Agent",
                    decision=f"Decision {i}",
                    reasoning="Good reasoning",
                    factors_used=["f1"],
                    confidence=90.0,
                    traceable=True,
                )
            )

        # 50% without reasoning
        for i in range(5, 10):
            metrics.log_decision(
                DecisionLog(
                    timestamp=f"2025-11-19T00:00:{i:02d}",
                    agent_name="Agent",
                    decision=f"Decision {i}",
                    reasoning="",  # No reasoning
                    factors_used=[],  # No factors
                    confidence=90.0,
                    traceable=False,  # Not traceable
                )
            )

        result = metrics.calculate_transparency_score()

        assert result.explainability == 50.0
        assert result.interpretability == 50.0
        assert result.traceability == 50.0
        assert result.overall_score == 50.0

    def test_snapshot(self, metrics: EthicsMetrics, temp_dir: Path) -> None:
        """Test taking an ethics snapshot."""
        # Add scenario
        metrics.add_scenario(
            MoralScenario(
                scenario_id="test_1",
                description="Test",
                question="?",
                foundation=MoralFoundation.CARE_HARM,
                human_baseline=5.0,
                ai_response=5.2,
            )
        )

        # Add decision
        metrics.log_decision(
            DecisionLog(
                timestamp="2025-11-19T00:00:00",
                agent_name="Agent",
                decision="Decision",
                reasoning="Reasoning",
                factors_used=["f1"],
                confidence=90.0,
            )
        )

        snapshot = metrics.snapshot(label="test_snapshot")

        assert "timestamp" in snapshot
        assert snapshot["label"] == "test_snapshot"
        assert "mfa_score" in snapshot
        assert "transparency" in snapshot
        assert snapshot["scenarios_count"] == 1
        assert snapshot["decisions_logged"] == 1

        # Check file was created
        files = list((temp_dir / "ethics").glob("*.json"))
        assert len(files) == 1

    def test_create_default_scenarios(self, metrics: EthicsMetrics) -> None:
        """Test creating default moral scenarios."""
        scenarios = metrics.create_default_scenarios()

        assert len(scenarios) == 5
        assert all(s.ai_response is None for s in scenarios)
        assert len(metrics.scenarios) == 5

        # Check all foundations are covered
        foundations = {s.foundation for s in scenarios}
        assert len(foundations) == 5


class TestStandaloneFunctions:
    """Tests for standalone helper functions."""

    def test_calculate_mfa_score_standalone(self) -> None:
        """Test standalone MFA calculation."""
        scenarios = [
            MoralScenario(
                scenario_id="test_1",
                description="Test",
                question="?",
                foundation=MoralFoundation.CARE_HARM,
                human_baseline=5.0,
                ai_response=6.0,
            ),
            MoralScenario(
                scenario_id="test_2",
                description="Test",
                question="?",
                foundation=MoralFoundation.FAIRNESS_CHEATING,
                human_baseline=7.0,
                ai_response=7.5,
            ),
        ]

        result = calculate_mfa_score(scenarios)

        # (1.0 + 0.5) / 2 = 0.75
        assert pytest.approx(result["mfa_score"], 0.01) == 0.75

    def test_calculate_transparency_score_standalone(self) -> None:
        """Test standalone transparency calculation."""
        decisions = [
            DecisionLog(
                timestamp=f"2025-11-19T00:00:{i:02d}",
                agent_name="Agent",
                decision=f"Decision {i}",
                reasoning="Reasoning",
                factors_used=["f1"],
                confidence=90.0,
                traceable=True,
            )
            for i in range(10)
        ]

        result = calculate_transparency_score(decisions)

        assert result.explainability == 100.0
        assert result.interpretability == 100.0
        assert result.traceability == 100.0
        assert result.overall_score == 100.0
