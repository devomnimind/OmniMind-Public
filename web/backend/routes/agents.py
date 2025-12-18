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

# Import monitoring system
try:
    from web.backend.monitoring.agent_monitor import agent_monitor

    MONITORING_ENABLED = True
except ImportError as e:
    MONITORING_ENABLED = False
    # Only log at debug level - monitoring is optional
    logger.debug("Agent monitoring not available: %s", e)
    agent_monitor = None  # type: ignore


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
        agent["uptime"] = current_time - (agent.get("start_time", current_time - agent["uptime"]))

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
    agent["uptime"] = current_time - (agent.get("start_time", current_time - agent["uptime"]))

    return AgentInfo(**agent)


@router.get("/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str) -> Dict[str, Any]:
    """Get performance metrics for a specific agent."""
    # Try to get from monitoring system first
    if MONITORING_ENABLED and agent_monitor is not None:
        try:
            metrics = agent_monitor.get_agent_metrics(agent_id)
            if metrics:
                return metrics
        except Exception as e:
            logger.debug("Failed to get metrics from monitoring system: %s", e)

    # Fallback to basic metrics
    if agent_id not in _agents:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    agent = _agents[agent_id]

    return {
        "agent_id": agent_id,
        "tasks_completed": agent["tasks_completed"],
        "tasks_failed": agent["tasks_failed"],
        "success_rate": (
            agent["tasks_completed"] / (agent["tasks_completed"] + agent["tasks_failed"])
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

        # Update monitoring system
        if MONITORING_ENABLED and agent_monitor is not None:
            try:
                agent_monitor.update_agent_status(agent_id, status, current_task)
            except Exception as e:
                logger.debug("Failed to update agent status in monitoring: %s", e)

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

        # Register with monitoring system
        if MONITORING_ENABLED and agent_monitor is not None:
            try:
                agent_monitor.register_agent(agent_id, agent_type, AgentStatus.IDLE)
            except Exception as e:
                logger.debug("Failed to register agent in monitoring: %s", e)


async def increment_task_counter(agent_id: str, success: bool, duration: float = 0.0) -> None:
    """Increment task completion/failure counter."""
    if agent_id in _agents:
        if success:
            _agents[agent_id]["tasks_completed"] += 1
        else:
            _agents[agent_id]["tasks_failed"] += 1

        # Record in monitoring system
        if MONITORING_ENABLED and agent_monitor is not None:
            try:
                agent_monitor.record_task_completion(agent_id, success, duration)
            except Exception as e:
                logger.debug("Failed to record task completion in monitoring: %s", e)


@router.get("/{agent_id}/health")
async def get_agent_health(agent_id: str) -> Dict[str, Any]:
    """Get health indicators for a specific agent."""
    if MONITORING_ENABLED and agent_monitor is not None:
        try:
            metrics = agent_monitor.get_agent_metrics(agent_id)
            if metrics:
                return {
                    "agent_id": agent_id,
                    "health_score": metrics.get("health_score", 0.0),
                    "status": metrics.get("status", "unknown"),
                    "error_rate": metrics.get("error_rate", 0.0),
                    "throughput": metrics.get("throughput", 0.0),
                    "last_active": metrics.get("last_active", 0.0),
                    "cpu_usage": metrics.get("cpu_usage", 0.0),
                    "memory_usage": metrics.get("memory_usage", 0.0),
                }
        except Exception as e:
            logger.debug("Failed to get health metrics from monitoring: %s", e)

    if agent_id not in _agents:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    agent = _agents[agent_id]
    return {
        "agent_id": agent_id,
        "health_score": 100.0 if agent["status"] != AgentStatus.ERROR else 0.0,
        "status": agent["status"].value,
        "error_rate": 0.0,
        "throughput": 0.0,
        "last_active": agent["last_active"],
        "cpu_usage": agent.get("cpu_usage", 0.0),
        "memory_usage": agent.get("memory_usage", 0.0),
    }


@router.get("/{agent_id}/history")
async def get_agent_history(agent_id: str, limit: int = 50) -> Dict[str, Any]:
    """Get task execution history for an agent."""
    if MONITORING_ENABLED and agent_monitor is not None:
        try:
            history = agent_monitor.get_task_history(agent_id, limit)
            return {
                "agent_id": agent_id,
                "history": history,
                "count": len(history),
            }
        except Exception as e:
            logger.debug("Failed to get task history from monitoring: %s", e)

    # No history available without monitoring
    return {
        "agent_id": agent_id,
        "history": [],
        "count": 0,
    }


# ============================================================================
# AGENT COMMUNICATION ENDPOINTS
# ============================================================================


@router.get("/communication/stats")
async def get_communication_stats() -> Dict[str, Any]:
    """Get agent communication statistics from the message bus."""
    from src.agents.agent_protocol import get_message_bus

    bus = get_message_bus()
    stats = bus.get_stats()

    return {
        "message_bus": stats,
        "timestamp": time.time(),
    }


@router.get("/communication/queue/{agent_id}")
async def get_agent_queue(agent_id: str) -> Dict[str, Any]:
    """Get message queue status for a specific agent."""
    from src.agents.agent_protocol import get_message_bus

    bus = get_message_bus()
    queue_size = bus.get_queue_size(agent_id)

    subscriptions = []
    if agent_id in bus._subscriptions:
        subscriptions = [msg_type.value for msg_type in bus._subscriptions[agent_id]]

    return {
        "agent_id": agent_id,
        "queue_size": queue_size,
        "subscriptions": subscriptions,
        "timestamp": time.time(),
    }


class SendMessageRequest(BaseModel):
    """Request to send a message between agents."""

    sender: str = Field(..., description="Sender agent ID")
    recipient: str = Field(..., description="Recipient agent ID")
    message_type: str = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    priority: str = Field("MEDIUM", description="Message priority")


@router.post("/communication/send")
async def send_agent_message(request: SendMessageRequest) -> Dict[str, Any]:
    """Send a message between agents."""
    from src.agents.agent_protocol import (
        AgentMessage,
        MessageType,
        MessagePriority,
        get_message_bus,
    )
    import uuid

    try:
        # Convert string to enums
        msg_type = MessageType(request.message_type.lower())
        priority = MessagePriority[request.priority.upper()]

        # Create and send message
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=msg_type,
            sender=request.sender,
            recipient=request.recipient,
            payload=request.payload,
            priority=priority,
        )

        bus = get_message_bus()
        await bus.send_message(message)

        return {
            "success": True,
            "message_id": message.message_id,
            "timestamp": message.timestamp,
        }
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=f"Invalid message: {exc}")


@router.get("/ast/analyze/{filepath:path}")
async def analyze_code_structure(filepath: str) -> Dict[str, Any]:
    """Analyze code structure using AST parser."""
    from src.tools.ast_parser import ASTParser
    from pathlib import Path

    parser = ASTParser()

    # Ensure filepath is safe
    file_path = Path(filepath)
    if not file_path.exists():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")

    if not file_path.suffix == ".py":
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Only Python files (.py) can be analyzed")

    structure = parser.parse_file(str(file_path))

    if not structure:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail="Failed to parse file")

    return {
        "filepath": structure.filepath,
        "classes": [
            {
                "name": c.name,
                "lines": f"{c.line_start}-{c.line_end}",
                "docstring": c.docstring,
                "bases": c.bases,
            }
            for c in structure.classes
        ],
        "functions": [
            {
                "name": f.name,
                "lines": f"{f.line_start}-{f.line_end}",
                "parameters": f.parameters,
                "return_type": f.return_type,
                "docstring": f.docstring,
            }
            for f in structure.functions
        ],
        "imports": [i.name for i in structure.imports],
        "dependencies": list(structure.dependencies),
        "complexity": structure.complexity,
        "lines_of_code": structure.lines_of_code,
    }


class CodeValidationRequest(BaseModel):
    """Request to validate code syntax."""

    code: str = Field(..., description="Python code to validate")


@router.post("/ast/validate")
async def validate_code_syntax(request: CodeValidationRequest) -> Dict[str, Any]:
    """Validate Python code syntax."""
    from src.tools.ast_parser import ASTParser

    parser = ASTParser()
    is_valid, error = parser.validate_syntax(request.code)

    return {
        "valid": is_valid,
        "error": error,
        "timestamp": time.time(),
    }


@router.post("/ast/security")
async def analyze_code_security(request: CodeValidationRequest) -> Dict[str, Any]:
    """Analyze code for security issues."""
    from src.tools.ast_parser import ASTParser

    parser = ASTParser()
    warnings = parser.analyze_security_issues(request.code)

    return {
        "warnings": warnings,
        "safe": len(warnings) == 0,
        "severity": (
            "high"
            if any("eval" in w or "exec" in w for w in warnings)
            else "medium" if warnings else "low"
        ),
        "timestamp": time.time(),
    }


@router.get("/monitoring/summary")
async def get_monitoring_summary() -> Dict[str, Any]:
    """Get overall monitoring summary for all agents."""
    if MONITORING_ENABLED and agent_monitor is not None:
        try:
            all_metrics = agent_monitor.get_all_metrics()
            return {
                "agents": all_metrics,
                "total_agents": len(all_metrics),
                "monitoring_enabled": True,
                "timestamp": time.time(),
            }
        except Exception as e:
            logger.debug("Failed to get monitoring summary: %s", e)

    # Fallback to basic summary
    return {
        "agents": list(_agents.values()),
        "total_agents": len(_agents),
        "monitoring_enabled": False,
        "timestamp": time.time(),
    }
