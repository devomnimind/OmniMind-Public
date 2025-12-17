"""
OmniMind Daemon Module

24/7 autonomous background service for OmniMind.
Works proactively while the user sleeps.
"""

from .omnimind_daemon import (
    DaemonState,
    DaemonTask,
    OmniMindDaemon,
    SystemMetrics,
    TaskPriority,
    create_default_tasks,
)

__all__ = [
    "DaemonState",
    "DaemonTask",
    "OmniMindDaemon",
    "SystemMetrics",
    "TaskPriority",
    "create_default_tasks",
]
