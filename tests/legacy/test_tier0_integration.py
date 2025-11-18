import pytest
from unittest.mock import AsyncMock

from DEVBRAIN_V23.memory.agentic_memory import AgenticMemory
from DEVBRAIN_V23.orchestration.langgraph_coordinator import LangGraphCoordinator


@pytest.mark.asyncio
async def test_reactree_langgraph_amem_flow() -> None:
    llm = AsyncMock()
    llm.ainvoke.side_effect = [
        AsyncMock(content="{}"),
        AsyncMock(content='{"issues": [], "severity": "low"}'),
        AsyncMock(content="Integrative summary"),
    ]

    reactree_agent = AsyncMock()
    reactree_agent.decompose_goal.return_value = [
        {"goal": "inspect logs", "control_flow": "sequence"}
    ]

    memory = AgenticMemory(persist_directory=None)
    coordinator = LangGraphCoordinator(llm, reactree_agent=reactree_agent, amem=memory)
    result = await coordinator.run("Maintain service")
    similar = await memory.query_similar_episodes("Maintain service")

    assert result["status"] == "success"
    assert similar
    assert "plan_steps" in result
