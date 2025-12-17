"""
Backup and Recovery Module for OmniMind.

Provides complete consciousness state snapshots and automated backup functionality.
"""

from .consciousness_snapshot import (
    ConsciousnessSnapshot,
    ConsciousnessSnapshotManager,
    SnapshotComparison,
    SnapshotTag,
)

__all__ = [
    "ConsciousnessSnapshot",
    "ConsciousnessSnapshotManager",
    "SnapshotComparison",
    "SnapshotTag",
]
