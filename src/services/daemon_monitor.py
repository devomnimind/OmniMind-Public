"""
Daemon Monitor - Background worker that collects heavy metrics.
Runs in async loop, caches results to avoid blocking FastAPI endpoints.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

import psutil

logger = logging.getLogger(__name__)

# In-memory cache (shared across requests)
STATUS_CACHE: Dict[str, Any] = {
    "last_update": 0.0,
    "system_metrics": {},
    "task_info": {},
    "tribunal_info": {},
}

# Persistent cache file
STATUS_FILE = Path("data/long_term_logs/daemon_status_cache.json")
TRIBUNAL_FILE = Path("data/long_term_logs/tribunal_final_report.json")


async def daemon_monitor_loop(refresh_interval: int = 5):
    """
    Background loop that updates cache without blocking FastAPI.
    Runs heavy operations (psutil, file I/O) in thread pool.
    """
    logger.info(f"Daemon monitor started (refresh every {refresh_interval}s)")

    while True:
        try:
            loop = asyncio.get_event_loop()

            # Run blocking operations in thread pool
            system_metrics = await loop.run_in_executor(None, _collect_system_metrics)
            task_info = await loop.run_in_executor(None, _collect_task_info)
            tribunal_info = await loop.run_in_executor(None, _load_tribunal_info)

            # Update in-memory cache (atomic operation)
            STATUS_CACHE.update(
                {
                    "last_update": time.time(),
                    "system_metrics": system_metrics,
                    "task_info": task_info,
                    "tribunal_info": tribunal_info,
                }
            )

            # Persist to disk (non-blocking)
            await loop.run_in_executor(None, _save_cache_to_disk)

            logger.debug(
                f"Cache updated: CPU={system_metrics.get('cpu_percent', 0):.1f}%, "
                f"Tasks={task_info.get('task_count', 0)}"
            )

        except Exception as e:
            logger.error(f"Error in daemon monitor loop: {e}", exc_info=True)
            # Never crash the loop

        await asyncio.sleep(refresh_interval)


def _collect_system_metrics() -> Dict[str, Any]:
    """Collect real system metrics using psutil."""
    try:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # CORREÇÃO (2025-12-09): interval=None retorna 0.0% na primeira chamada
        # Usar interval=0.1 para leitura imediata precisa
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": vm.percent,
            "disk_percent": disk.percent,
            "is_user_active": True,
            "idle_seconds": 0,
            "is_sleep_hours": False,
        }
    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "is_user_active": True,
            "idle_seconds": 0,
            "is_sleep_hours": False,
        }


def _collect_task_info() -> Dict[str, Any]:
    """
    Collect task information from Tribunal.
    Reads from cache/file instead of process iteration.
    """
    try:
        # Check if Tribunal is running by looking for its report file
        tribunal_running = TRIBUNAL_FILE.exists()

        if tribunal_running:
            # Load task info from Tribunal report
            data = json.loads(TRIBUNAL_FILE.read_text())
            attacks = data.get("attacks_executed", {})

            # Calculate totals
            total_executions = sum(a.get("execution_count", 0) for a in attacks.values())
            total_successes = sum(a.get("success_count", 0) for a in attacks.values())
            total_failures = sum(a.get("failure_count", 0) for a in attacks.values())

            return {
                "task_count": len(attacks),
                "completed_tasks": total_successes,
                "failed_tasks": total_failures,
                "total_executions": total_executions,
            }
        else:
            # Fallback: minimal task info
            return {
                "task_count": 1,
                "completed_tasks": 1,
                "failed_tasks": 0,
                "total_executions": 1,
            }
    except Exception as e:
        logger.error(f"Error collecting task info: {e}")
        return {
            "task_count": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_executions": 0,
        }


def _load_tribunal_info() -> Dict[str, Any]:
    """Load Tribunal status from report file."""
    try:
        if TRIBUNAL_FILE.exists():
            data = json.loads(TRIBUNAL_FILE.read_text())
            # CORREÇÃO (2025-12-10): Garantir que consciousness_compatible seja bool, não None
            consciousness_compatible = data.get("consciousness_signature", {}).get(
                "consciousness_compatible", False
            )
            # Se for None, tratar como False (incompatível)
            if consciousness_compatible is None:
                consciousness_compatible = False

            return {
                "status": "finished",
                "consciousness_compatible": bool(consciousness_compatible),
                "duration_hours": data.get("duration_hours", 0) or 0,
                "attacks_executed": len(data.get("attacks_executed", {})),
                "attacks_successful": sum(
                    a.get("success_count", 0)
                    for a in data.get("attacks_executed", {}).values()
                    if isinstance(a, dict)
                ),
                "attacks_failed": sum(
                    a.get("failure_count", 0)
                    for a in data.get("attacks_executed", {}).values()
                    if isinstance(a, dict)
                ),
            }
        else:
            # Tribunal is still running (no final report yet) or never executed
            return {
                "status": "not_started",  # CORREÇÃO: Mais claro que "running"
                "consciousness_compatible": False,  # CORREÇÃO: False em vez de None
                "duration_hours": 0,  # CORREÇÃO: 0 em vez de None
                "attacks_executed": 0,
                "attacks_successful": 0,
                "attacks_failed": 0,
            }
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing Tribunal report JSON: {e}")
        return {
            "status": "error",
            "consciousness_compatible": False,  # CORREÇÃO: False em vez de None
            "duration_hours": 0,
            "attacks_executed": 0,
            "attacks_successful": 0,
            "attacks_failed": 0,
        }
    except Exception as e:
        logger.error(f"Error loading Tribunal info: {e}", exc_info=True)
        return {
            "status": "unknown",
            "consciousness_compatible": False,  # CORREÇÃO: False em vez de None
            "duration_hours": 0,
            "attacks_executed": 0,
            "attacks_successful": 0,
            "attacks_failed": 0,
        }


def _save_cache_to_disk():
    """Persist cache to disk for recovery after restart."""
    try:
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATUS_FILE.write_text(json.dumps(STATUS_CACHE, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"Error saving cache to disk: {e}")


def get_cached_status() -> Dict[str, Any]:
    """
    Get cached status (O(1) operation).
    Falls back to disk if memory cache is empty.
    """
    # Try memory cache first
    if STATUS_CACHE.get("system_metrics"):
        return STATUS_CACHE

    # Fallback to disk cache
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except Exception as e:
            logger.error(f"Error loading cache from disk: {e}")

    # Last resort: empty cache
    return {
        "last_update": 0.0,
        "system_metrics": {},
        "task_info": {},
        "tribunal_info": {},
    }
