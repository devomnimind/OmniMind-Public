import shutil
import time
from typing import Any, Dict
import psutil
from fastapi import APIRouter

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


router = APIRouter()


@router.get("/")
async def get_health() -> Dict[str, Any]:
    """
    Get overall system health status.
    """
    # Check system resources
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = shutil.disk_usage("/")

    # Determine status
    status = "healthy"
    unhealthy_count = 0
    degraded_count = 0

    if cpu_usage > 90 or memory.percent > 90:
        status = "degraded"
        degraded_count += 1

    checks = {
        "cpu": {
            "name": "cpu",
            "dependency_type": "cpu",
            "status": "healthy" if cpu_usage < 90 else "degraded",
            "response_time_ms": 0.1,
            "details": {"usage": f"{cpu_usage}%"},
            "timestamp": time.time(),
            "threshold_breached": cpu_usage > 90,
        },
        "memory": {
            "name": "memory",
            "dependency_type": "memory",
            "status": "healthy" if memory.percent < 90 else "degraded",
            "response_time_ms": 0.1,
            "details": {
                "usage": f"{memory.percent}%",
                "available": f"{memory.available / 1024 / 1024 / 1024:.2f}GB",
            },
            "timestamp": time.time(),
            "threshold_breached": memory.percent > 90,
        },
        "disk": {
            "name": "disk",
            "dependency_type": "filesystem",
            "status": "healthy" if (disk.used / disk.total) < 0.9 else "degraded",
            "response_time_ms": 0.1,
            "details": {
                "usage": f"{(disk.used / disk.total) * 100:.1f}%",
                "free": f"{disk.free / 1024 / 1024 / 1024:.2f}GB",
            },
            "timestamp": time.time(),
            "threshold_breached": (disk.used / disk.total) > 0.9,
        },
    }

    return {
        "overall_status": status,
        "checks": checks,
        "timestamp": time.time(),
        "total_checks": len(checks),
        "healthy_count": len(checks) - degraded_count - unhealthy_count,
        "degraded_count": degraded_count,
        "unhealthy_count": unhealthy_count,
    }


@router.get("/{check_name}/trend")
async def get_health_trend(check_name: str) -> Dict[str, Any]:
    """
    Get health trend for a specific check.
    """
    return {
        "check_name": check_name,
        "trend": "stable",
        "prediction": "stable",
        "health_score": 100.0,
        "recent_statuses": {"healthy": 10},
        "avg_response_time_ms": 0.1,
    }
