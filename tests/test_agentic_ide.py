from pathlib import Path
import pytest
from src.integrations.agentic_ide import (

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
Tests for Agentic IDE module.
"""



    AgenticIDE,
    AgentTask,
    AIModel,
    ArtifactType,
    BrowserVerifier,
    IDEMode,
    ModelSelector,
    SelfImprovementLoop,
    VerifiableArtifact,
)


class TestAgenticIDE:
    """Tests for AgenticIDE."""

    def test_initialization(self, tmp_path: Path) -> None:
        """Test IDE initialization."""
        ide = AgenticIDE(workspace_path=tmp_path)

        assert ide.workspace_path == tmp_path
        assert ide.current_mode == IDEMode.EDITOR
        assert len(ide.tasks) == 0

    def test_mode_switching(self, tmp_path: Path) -> None:
        """Test mode switching."""
        ide = AgenticIDE(workspace_path=tmp_path)

        # Switch to manager
        ide.switch_mode(IDEMode.MANAGER)
        assert ide.current_mode == IDEMode.MANAGER

        # Switch back to editor
        ide.switch_mode(IDEMode.EDITOR)
        assert ide.current_mode == IDEMode.EDITOR

    def test_create_task(self, tmp_path: Path) -> None:
        """Test task creation."""
        ide = AgenticIDE(workspace_path=tmp_path)

        task = ide.create_task(
            description="Implement feature X",
            task_type="code",
            agent_id="test_agent",
            context={"requires_code": True},
        )

        assert task.task_id in ide.tasks
        assert task.description == "Implement feature X"
        assert task.assigned_agent == "test_agent"
        assert task.status == "pending"

    def test_execute_task(self, tmp_path: Path) -> None:
        """Test task execution."""
        ide = AgenticIDE(workspace_path=tmp_path)

        task = ide.create_task(description="Test task", task_type="code", agent_id="test_agent")

        result = ide.execute_task(task.task_id)

        assert result["success"] is True
        assert task.status == "completed"
        assert len(task.artifacts) > 0

    def test_verify_artifact(self, tmp_path: Path) -> None:
        """Test artifact verification."""
        ide = AgenticIDE(workspace_path=tmp_path)

        # Create and execute task
        task = ide.create_task(description="Test", task_type="code", agent_id="test_agent")
        result = ide.execute_task(task.task_id)

        # Verify artifact
        if result.get("artifacts"):
            artifact_id = result["artifacts"][0]
            verified = ide.verify_artifact(artifact_id)

            assert verified is True

    def test_provide_feedback(self, tmp_path: Path) -> None:
        """Test feedback provision."""
        ide = AgenticIDE(workspace_path=tmp_path)

        task = ide.create_task(description="Test", task_type="code", agent_id="test_agent")

        ide.provide_feedback(task_id=task.task_id, feedback_content="Good work", success=True)

        assert task.feedback == "Good work"

    def test_get_insights(self, tmp_path: Path) -> None:
        """Test insights retrieval."""
        ide = AgenticIDE(workspace_path=tmp_path)

        # Create and execute task
        task = ide.create_task(description="Test", task_type="code", agent_id="test_agent")
        ide.execute_task(task.task_id)

        insights = ide.get_insights()

        assert "total_tasks" in insights
        assert insights["total_tasks"] > 0
        assert "total_artifacts" in insights


class TestBrowserVerifier:
    """Tests for BrowserVerifier."""

    def test_initialization(self, tmp_path: Path) -> None:
        """Test verifier initialization."""
        verifier = BrowserVerifier(screenshots_dir=tmp_path)

        assert verifier.screenshots_dir == tmp_path
        assert len(verifier.verifications) == 0

    def test_verify_web_app(self, tmp_path: Path) -> None:
        """Test web app verification."""
        verifier = BrowserVerifier(screenshots_dir=tmp_path)

        verification = verifier.verify_web_app(
            url="http://localhost:3000", expected_elements=[".app"]
        )

        assert verification.url == "http://localhost:3000"
        assert verification.passed is True
        assert len(verifier.verifications) == 1


class TestSelfImprovementLoop:
    """Tests for SelfImprovementLoop."""

    def test_initialization(self) -> None:
        """Test loop initialization."""
        loop = SelfImprovementLoop()

        assert len(loop.feedback_history) == 0
        assert loop.learning_rate == 0.1

    def test_process_feedback(self) -> None:
        """Test feedback processing."""
        loop = SelfImprovementLoop()

        loop.process_feedback(
            task_id="task_1",
            feedback_type="code_quality",
            feedback_content="Good",
            success=True,
        )

        assert len(loop.feedback_history) == 1
        assert "code_quality:True" in loop.learned_patterns

    def test_get_insights(self) -> None:
        """Test insights retrieval."""
        loop = SelfImprovementLoop()

        # Process some feedback
        loop.process_feedback("t1", "good", "Good", True)
        loop.process_feedback("t2", "good", "Good", True)
        loop.process_feedback("t3", "bad", "Bad", False)

        insights = loop.get_learned_insights()

        assert "total_feedback" in insights
        assert insights["total_feedback"] == 3
        assert "learned_patterns" in insights


class TestModelSelector:
    """Tests for ModelSelector."""

    def test_initialization(self) -> None:
        """Test selector initialization."""
        selector = ModelSelector()

        assert len(selector.usage_history) == 0

    def test_select_model(self) -> None:
        """Test model selection."""
        selector = ModelSelector()

        # Select for code task
        model = selector.select_model(task_type="code", context={"requires_code": True})

        assert isinstance(model, AIModel)

    def test_update_performance(self) -> None:
        """Test performance update."""
        selector = ModelSelector()

        # Update performance
        selector.update_performance(task_type="code", model=AIModel.CLAUDE_SONNET_4_5, success=True)

        assert len(selector.usage_history) == 1
        assert selector.usage_history[0]["success"] is True


class TestVerifiableArtifact:
    """Tests for VerifiableArtifact."""

    def test_creation(self) -> None:
        """Test artifact creation."""
        artifact = VerifiableArtifact(
            artifact_id="art_1",
            artifact_type=ArtifactType.CODE,
            content="def test(): pass",
            timestamp=1234567890.0,
            agent_id="agent_1",
        )

        assert artifact.artifact_id == "art_1"
        assert artifact.artifact_type == ArtifactType.CODE
        assert artifact.verified is False
        assert len(artifact.hash) == 64  # SHA-256


class TestAgentTask:
    """Tests for AgentTask."""

    def test_creation(self) -> None:
        """Test task creation."""
        task = AgentTask(
            task_id="task_1",
            description="Test task",
            assigned_agent="agent_1",
            assigned_model=AIModel.GPT_4,
        )

        assert task.task_id == "task_1"
        assert task.status == "pending"
        assert len(task.artifacts) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
