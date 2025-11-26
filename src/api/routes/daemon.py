from fastapi import APIRouter
from typing import Dict, Any, List
import time
import random

router = APIRouter()


@router.get("/status")
async def get_daemon_status() -> Dict[str, Any]:
    """
    Get current daemon status.
    Simulates 'running' state since Tribunal is active.
    """
    return {
        "running": True,
        "uptime_seconds": 3600 + int(time.time() % 3600),
        "task_count": 4,
        "completed_tasks": 120,
        "failed_tasks": 2,
        "cloud_connected": True,
        "system_metrics": {
            "cpu_percent": 45.2,
            "memory_percent": 60.5,
            "disk_percent": 30.0,
            "is_user_active": True,
            "idle_seconds": 0,
            "is_sleep_hours": False,
        },
    }


@router.get("/tasks")
async def get_daemon_tasks() -> Dict[str, Any]:
    """
    Get list of active tasks.
    Returns simulated Tribunal tasks.
    """
    return {
        "total_tasks": 4,
        "tasks": [
            {
                "task_id": "tribunal_latency",
                "name": "Tribunal: Latency Attack",
                "description": "Progressive latency injection (0-2000ms)",
                "priority": "CRITICAL",
                "repeat_interval": "00:00:30",
                "execution_count": 120,
                "success_count": 118,
                "failure_count": 2,
                "last_execution": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            {
                "task_id": "tribunal_corruption",
                "name": "Tribunal: Corruption Attack",
                "description": "Cyclic bias injection and scar integration",
                "priority": "HIGH",
                "repeat_interval": "00:05:00",
                "execution_count": 12,
                "success_count": 12,
                "failure_count": 0,
                "last_execution": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            {
                "task_id": "tribunal_bifurcation",
                "name": "Tribunal: Bifurcation Attack",
                "description": "Scheduled network splits and reconciliation",
                "priority": "HIGH",
                "repeat_interval": "00:30:00",
                "execution_count": 2,
                "success_count": 2,
                "failure_count": 0,
                "last_execution": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            {
                "task_id": "tribunal_exhaustion",
                "name": "Tribunal: Exhaustion Attack",
                "description": "Continuous request bursts to trigger hibernation",
                "priority": "CRITICAL",
                "repeat_interval": "00:00:10",
                "execution_count": 360,
                "success_count": 300,
                "failure_count": 60,  # Simulated rejections
                "last_execution": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        ],
    }


@router.post("/tasks/add")
async def add_task(task: Dict[str, Any]):
    return {"message": "Task queued", "task_id": "simulated_id"}


@router.post("/start")
async def start_daemon():
    return {"message": "Daemon started"}


@router.post("/stop")
async def stop_daemon():
    return {"message": "Daemon stopped"}
