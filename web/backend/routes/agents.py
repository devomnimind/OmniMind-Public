"""API routes for agent status and monitoring."""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


class AgentStatus(str, Enum):
    """Agent operational status."""

    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentType(str, Enum):
    """Types of agents in the system."""

    ORCHESTRATOR = "orchestrator"
    CODE = "code"
    ARCHITECT = "architect"
    DEBUG = "debug"
    REVIEWER = "reviewer"
    PSYCHOANALYST = "psychoanalyst"
    SECURITY = "security"
    METACOGNITION = "metacognition"


class AgentInfo(BaseModel):
    """Agent information model."""

    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    current_task: str | None = Field(None, description="Current task description")
    tasks_completed: int = Field(0, description="Total tasks completed")
    tasks_failed: int = Field(0, description="Total tasks failed")
    uptime: float = Field(..., description="Uptime in seconds")
    last_active: float = Field(..., description="Last activity timestamp")
    cpu_usage: float = Field(0.0, ge=0.0, le=100.0, description="CPU usage %")
    memory_usage: float = Field(0.0, ge=0.0, le=100.0, description="Memory usage %")
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Mock agent data (would be replaced with actual agent monitoring)
_agents: Dict[str, Dict[str, Any]] = {
    "orchestrator-1": {
        "agent_id": "orchestrator-1",
        "agent_type": AgentType.ORCHESTRATOR,
        "status": AgentStatus.ACTIVE,
        "current_task": None,
        "tasks_completed": 0,
        "tasks_failed": 0,
        "uptime": 0.0,
        "last_active": time.time(),
        "cpu_usage": 0.0,
        "memory_usage": 0.0,
        "metadata": {},
    }
}


@router.get("/", response_model=List[AgentInfo])
async def list_agents() -> List[AgentInfo]:
    """List all agents in the system."""
    current_time = time.time()

    # Update uptime for all agents
    for agent in _agents.values():
        agent["uptime"] = current_time - (
            agent.get("start_time", current_time - agent["uptime"])
        )

    return [AgentInfo(**agent) for agent in _agents.values()]


@router.get("/status", response_model=Dict[str, Any])
async def get_agents_status() -> Dict[str, Any]:
    """Get overall agent system status."""
    total = len(_agents)
    active = sum(1 for a in _agents.values() if a["status"] == AgentStatus.ACTIVE)
    idle = sum(1 for a in _agents.values() if a["status"] == AgentStatus.IDLE)
    busy = sum(1 for a in _agents.values() if a["status"] == AgentStatus.BUSY)
    error = sum(1 for a in _agents.values() if a["status"] == AgentStatus.ERROR)

    return {
        "total_agents": total,
        "active": active,
        "idle": idle,
        "busy": busy,
        "error": error,
        "timestamp": time.time(),
    }


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str) -> AgentInfo:
    """Get detailed information about a specific agent."""
    if agent_id not in _agents:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    agent = _agents[agent_id]
    current_time = time.time()
    agent["uptime"] = current_time - (
        agent.get("start_time", current_time - agent["uptime"])
    )

    return AgentInfo(**agent)


@router.get("/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str) -> Dict[str, Any]:
    """Get performance metrics for a specific agent."""
    if agent_id not in _agents:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    agent = _agents[agent_id]

    return {
        "agent_id": agent_id,
        "tasks_completed": agent["tasks_completed"],
        "tasks_failed": agent["tasks_failed"],
        "success_rate": (
            agent["tasks_completed"]
            / (agent["tasks_completed"] + agent["tasks_failed"])
            if (agent["tasks_completed"] + agent["tasks_failed"]) > 0
            else 0.0
        ),
        "cpu_usage": agent["cpu_usage"],
        "memory_usage": agent["memory_usage"],
        "uptime": agent["uptime"],
        "timestamp": time.time(),
    }


async def update_agent_status(
    agent_id: str, status: AgentStatus, current_task: str | None = None
) -> None:
    """Update agent status (internal use)."""
    if agent_id in _agents:
        _agents[agent_id]["status"] = status
        _agents[agent_id]["last_active"] = time.time()
        if current_task is not None:
            _agents[agent_id]["current_task"] = current_task

        # Broadcast status update via WebSocket
        from web.backend.websocket_manager import MessageType, ws_manager

        await ws_manager.broadcast(
            MessageType.AGENT_STATUS,
            {
                "agent_id": agent_id,
                "status": status.value,
                "current_task": current_task,
                "timestamp": time.time(),
            },
            channel="agents",
        )


async def register_agent(agent_id: str, agent_type: AgentType) -> None:
    """Register a new agent."""
    if agent_id not in _agents:
        _agents[agent_id] = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "status": AgentStatus.IDLE,
            "current_task": None,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "uptime": 0.0,
            "start_time": time.time(),
            "last_active": time.time(),
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "metadata": {},
        }
        logger.info(f"Registered agent: {agent_id} ({agent_type.value})")


async def increment_task_counter(agent_id: str, success: bool) -> None:
    """Increment task completion/failure counter."""
    if agent_id in _agents:
        if success:
            _agents[agent_id]["tasks_completed"] += 1
        else:
            _agents[agent_id]["tasks_failed"] += 1
