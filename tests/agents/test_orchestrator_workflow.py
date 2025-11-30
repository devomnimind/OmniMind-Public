"""
Tests for FASE 2: Full Workflow Execution

Testa:
- execute_workflow() completo
- Decomposição + Delegação + Execução + Síntese
- Dependency analysis
- Result synthesis
"""

import pytest
from unittest.mock import patch

from src.agents.orchestrator_agent import OrchestratorAgent


class TestExecuteWorkflow:
    """Test full workflow execution."""

    @pytest.mark.asyncio
    @patch("src.agents.orchestrator_agent.OmniMindCore")
    async def test_execute_workflow_structure(self, mock_core):
        """Test that execute_workflow returns correct structure."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        # Mock the methods
        with (
            patch.object(agent, "decompose_task") as mock_decompose,
            patch.object(agent, "execute_plan") as mock_execute,
        ):

            decomposition = {
                "original_task": "Implement feature",
                "subtasks": [
                    {"description": "Design API", "agent": "architect"},
                    {"description": "Implement code", "agent": "code"},
                    {"description": "Review code", "agent": "reviewer"},
                ],
                "complexity": "medium",
                "estimated_duration": 120,
            }

            execution_result = {
                "subtask_results": [
                    {
                        "completed": True,
                        "final_result": "API designed",
                        "agent": "architect",
                    }
                ],
                "overall_success": True,
            }

            mock_decompose.return_value = decomposition
            mock_execute.return_value = execution_result

            result = await agent.execute_workflow("Implement feature")

            assert "workflow_id" in result
            assert result["original_task"] == "Implement feature"
            assert "decomposition" in result
            assert "execution_results" in result
            assert "synthesis" in result
            assert "metrics" in result
            assert "overall_success" in result

    @pytest.mark.asyncio
    @patch("src.agents.orchestrator_agent.OmniMindCore")
    async def test_execute_workflow_with_empty_decomposition(self, mock_core):
        """Test workflow handles empty decomposition."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        with patch.object(agent, "decompose_task") as mock_decompose:
            mock_decompose.return_value = {"subtasks": [], "complexity": "low"}

            result = await agent.execute_workflow("Bad task")

            assert result["overall_success"] is False
            assert "error" in result


class TestDependencyAnalysis:
    """Test task dependency analysis."""

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_analyze_task_dependencies_groups_by_agent(self, mock_core):
        """Test that dependencies are grouped by agent."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        subtasks = [
            {"description": "Implement auth", "agent": "code"},
            {"description": "Design system", "agent": "architect"},
            {"description": "Implement API", "agent": "code"},
            {"description": "Review all", "agent": "reviewer"},
        ]

        plan = agent._analyze_task_dependencies(subtasks)

        assert len(plan) == len(subtasks)
        assert all("order" in p for p in plan)
        assert all("agent" in p for p in plan)
        assert all("can_parallel" in p for p in plan)

        # Check grouping
        agents_in_order = [p["agent"] for p in plan]
        # Code tasks should be together
        code_indices = [i for i, a in enumerate(agents_in_order) if a == "code"]
        architect_indices = [i for i, a in enumerate(agents_in_order) if a == "architect"]
        reviewer_indices = [i for i, a in enumerate(agents_in_order) if a == "reviewer"]

        assert len(code_indices) == 2
        assert len(architect_indices) == 1
        assert len(reviewer_indices) == 1


class TestResultSynthesis:
    """Test result synthesis."""

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_synthesize_results_compiles_outputs(self, mock_core):
        """Test that results are properly synthesized."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        subtasks = [
            {"description": "Implement auth", "agent": "code"},
            {"description": "Design system", "agent": "architect"},
            {"description": "Review all", "agent": "reviewer"},
        ]

        results = [
            {"completed": True, "final_result": "Auth module", "agent": "code"},
            {"completed": True, "final_result": "System design doc", "agent": "architect"},
            {"completed": True, "final_result": "Review passed", "agent": "reviewer"},
        ]

        synthesis = agent._synthesize_results(subtasks, results, "medium")

        assert "code_summary" in synthesis
        assert "architecture_summary" in synthesis
        assert "review_summary" in synthesis
        assert "key_outputs" in synthesis
        assert "issues" in synthesis

        assert len(synthesis["key_outputs"]) == 3
        assert len(synthesis["issues"]) == 0

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_synthesize_results_handles_failures(self, mock_core):
        """Test that synthesis handles failed tasks."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        subtasks = [
            {"description": "Implement auth", "agent": "code"},
            {"description": "Design system", "agent": "architect"},
        ]

        results = [
            {"completed": True, "final_result": "Auth module", "agent": "code"},
            {"completed": False, "final_result": "Design failed: timeout", "agent": "architect"},
        ]

        synthesis = agent._synthesize_results(subtasks, results, "medium")

        assert len(synthesis["key_outputs"]) == 1
        assert len(synthesis["issues"]) == 1
        assert "timeout" in synthesis["issues"][0]


class TestDelegateAndExecute:
    """Test delegation and execution."""

    @pytest.mark.asyncio
    @patch("src.agents.orchestrator_agent.OmniMindCore")
    async def test_delegate_and_execute_runs_sequentially(self, mock_core):
        """Test that tasks execute sequentially."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        execution_plan = [
            {
                "order": 0,
                "agent": "code",
                "subtask_index": 0,
                "subtask": {"description": "Task 1", "agent": "code"},
            },
            {
                "order": 1,
                "agent": "architect",
                "subtask_index": 1,
                "subtask": {"description": "Task 2", "agent": "architect"},
            },
        ]

        with patch.object(agent, "execute_plan") as mock_execute:
            mock_execute.return_value = {
                "subtask_results": [{"completed": True, "final_result": "Done"}],
                "overall_success": True,
            }

            results = await agent._delegate_and_execute(
                "test-wf", execution_plan, enable_monitoring=True, max_concurrent=1
            )

            assert len(results) == 2
            assert all(r.get("completed") or "completed" in r for r in results)
