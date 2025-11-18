import pytest
from unittest.mock import AsyncMock

from DEVBRAIN_V23.reasoning.reactree_agent import (
    ControlFlowType,
    ReAcTreeAgent,
    Thought,
)


class MockResponse:
    def __init__(self, content: str) -> None:
        self.content = content


@pytest.mark.asyncio
async def test_reactree_decomposition() -> None:
    llm = AsyncMock()
    llm.ainvoke.return_value = MockResponse(
        '{"subgoals": [{"goal": "Search Paris flights", "control_flow": "sequence"}]}'
    )
    agent = ReAcTreeAgent(llm)
    subgoals = await agent.decompose_goal("Book Paris trip")

    assert subgoals
    assert subgoals[0]["goal"] == "Search Paris flights"


@pytest.mark.asyncio
async def test_reactree_execution() -> None:
    llm = AsyncMock()
    llm.ainvoke.side_effect = [
        MockResponse('{"reasoning": "complete", "action_type": "direct"}'),
        MockResponse('{"action": "return_result", "params": {"value": "ok"}}'),
    ]
    agent = ReAcTreeAgent(llm)
    result = await agent.execute_tree("Simple task")

    assert result["goal"] == "Simple task"
    assert "tree_depth" in result
    assert "history" in result


@pytest.mark.asyncio
async def test_control_flow_sequence() -> None:
    agent = ReAcTreeAgent(AsyncMock())
    root = Thought(
        id="root",
        goal="Test",
        parent_id=None,
        reasoning="reason",
        action=None,
        observation=None,
        control_flow=ControlFlowType.SEQUENCE,
        status="in_progress",
    )
    child_one = Thought(
        id="child1",
        goal="step1",
        parent_id="root",
        reasoning="",
        action=None,
        observation=None,
        status="success",
        result={"value": 1},
    )
    child_two = Thought(
        id="child2",
        goal="step2",
        parent_id="root",
        reasoning="",
        action=None,
        observation=None,
        status="success",
        result={"value": 2},
    )
    root.subgoals.extend([child_one, child_two])

    result = await agent._execute_control_flow(root)

    assert root.status == "success"
    assert isinstance(result.get("results"), list)
    assert len(result["results"]) == 2
