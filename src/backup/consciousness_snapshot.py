"""
Consciousness Snapshot System - Complete State Capture and Recovery

Captures complete state of IntegrationLoop, SharedWorkspace, and CycleHistory
for scientific experiments, reproducibility, and recovery.
"""

import gzip
import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SnapshotTag:
    """Tag for organizing snapshots."""

    name: str
    description: Optional[str] = None
    experiment_id: Optional[str] = None
    version: Optional[str] = None


@dataclass
class SnapshotComparison:
    """Result of comparing two snapshots."""

    snapshot_id1: str
    snapshot_id2: str
    differences: Dict[str, Any]
    metrics_delta: Dict[str, float]
    embeddings_similarity: Dict[str, float]
    timestamp: float = field(default_factory=time.time)


@dataclass
class ConsciousnessSnapshot:
    """
    Complete snapshot of consciousness state.

    Integrates:
    - ConsciousnessStateManager (métricas Φ, Ψ, σ)
    - SharedWorkspace (embeddings, history, cross_predictions)
    - IntegrationLoop (cycle state, statistics)
    - ExtendedLoopCycleResult (gozo, delta, control, imagination)
    - CycleHistory (histórico de ciclos)
    """

    snapshot_id: str
    timestamp: datetime
    tag: Optional[SnapshotTag] = None

    # Métricas de consciência (de ConsciousnessStateManager)
    phi_value: float = 0.0
    psi_value: float = 0.0
    sigma_value: float = 0.0
    integration_level: float = 0.0
    qualia_signature: Dict[str, Any] = field(default_factory=dict)
    attention_state: Dict[str, float] = field(default_factory=dict)

    # SharedWorkspace state
    workspace_embeddings: Dict[str, List[float]] = field(
        default_factory=dict
    )  # module_name -> embedding
    workspace_history_size: int = 0
    workspace_cycle_count: int = 0
    workspace_cross_predictions_count: int = 0

    # IntegrationLoop state
    loop_cycle_count: int = 0
    loop_total_cycles_executed: int = 0
    loop_statistics: Dict[str, Any] = field(default_factory=dict)
    loop_phi_progression: List[float] = field(default_factory=list)

    # ExtendedLoopCycleResult (último ciclo)
    last_cycle_phi: Optional[float] = (
        None  # PHI do último ciclo executado (fallback quando workspace PHI=0)
    )
    last_cycle_gozo: Optional[float] = None
    last_cycle_delta: Optional[float] = None
    last_cycle_control_effectiveness: Optional[float] = None
    last_cycle_imagination_shape: Optional[tuple] = None

    # CycleHistory (últimos N ciclos)
    recent_cycles: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_hash: Optional[str] = None  # SHA-256 hash for integrity

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        if self.tag:
            data["tag"] = asdict(self.tag)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsciousnessSnapshot":
        """Deserialize from dictionary."""
        # Parse timestamp
        if isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        elif isinstance(data["timestamp"], float):
            data["timestamp"] = datetime.fromtimestamp(data["timestamp"], tz=timezone.utc)

        # Parse tag
        if "tag" in data and data["tag"]:
            data["tag"] = SnapshotTag(**data["tag"])

        return cls(**data)

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of snapshot content."""
        # Create a copy without content_hash for hashing
        data = self.to_dict()
        data.pop("content_hash", None)  # Remove hash from calculation
        content = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify snapshot integrity."""
        if self.content_hash is None:
            logger.warning("Snapshot has no content_hash - cannot verify integrity")
            return False
        calculated_hash = self.calculate_hash()
        is_valid = calculated_hash == self.content_hash
        if not is_valid:
            logger.warning(
                f"Hash mismatch: calculated={calculated_hash[:16]}..., "
                f"stored={self.content_hash[:16]}..."
            )
        return is_valid


class ConsciousnessSnapshotManager:
    """
    Manager for consciousness snapshots.

    Handles creation, storage, retrieval, comparison, and recovery of snapshots.
    """

    def __init__(
        self,
        storage_dir: Path = Path("data/backup/snapshots"),
        max_snapshots: int = 1000,
        compress: bool = True,
    ):
        """
        Initialize snapshot manager.

        Args:
            storage_dir: Directory to store snapshots
            max_snapshots: Maximum number of snapshots to keep
            compress: Whether to compress snapshots (gzip)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_snapshots = max_snapshots
        self.compress = compress

        # Index of snapshots (snapshot_id -> metadata)
        self.index_file = self.storage_dir / "snapshots_index.json"
        self.index: Dict[str, Dict[str, Any]] = self._load_index()

        logger.info(
            f"ConsciousnessSnapshotManager initialized: {self.storage_dir} "
            f"(max_snapshots={max_snapshots}, compress={compress})"
        )

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load snapshot index."""
        if not self.index_file.exists():
            return {}

        try:
            with open(self.index_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load snapshot index: {e}")
            return {}

    def _save_index(self) -> None:
        """Save snapshot index."""
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save snapshot index: {e}")

    def create_full_snapshot(
        self,
        integration_loop: Any,
        tag: Optional[SnapshotTag] = None,
        include_recent_cycles: int = 10,
    ) -> str:
        """
        Create complete snapshot of consciousness state.

        Args:
            integration_loop: IntegrationLoop instance
            tag: Optional tag for organization
            include_recent_cycles: Number of recent cycles to include

        Returns:
            snapshot_id
        """
        logger.info("Creating full consciousness snapshot...")

        snapshot_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        # 1. Extract ConsciousnessStateManager metrics (if available)
        phi_value = 0.0
        psi_value = 0.0
        sigma_value = 0.0
        integration_level = 0.0
        qualia_signature: Dict[str, Any] = {}
        attention_state: Dict[str, float] = {}

        if hasattr(integration_loop, "workspace"):
            workspace = integration_loop.workspace
            # Try to get PHI from last cycle result first (more reliable)
            if hasattr(integration_loop, "cycle_history") and integration_loop.cycle_history:
                # Try extended components first
                if (
                    hasattr(integration_loop, "_extended_components")
                    and integration_loop._extended_components
                    and "cycle_history" in integration_loop._extended_components
                ):
                    cycle_history = integration_loop._extended_components["cycle_history"]
                    if hasattr(cycle_history, "history") and cycle_history.history:
                        last_cycle = cycle_history.history[-1]
                        if hasattr(last_cycle, "phi_estimate") and last_cycle.phi_estimate > 0.0:
                            phi_value = last_cycle.phi_estimate
                            logger.debug(f"Using PHI from last extended cycle: {phi_value:.6f}")
                # Fallback to basic cycle_history
                elif (
                    isinstance(integration_loop.cycle_history, list)
                    and integration_loop.cycle_history
                ):
                    last_cycle = integration_loop.cycle_history[-1]
                    if hasattr(last_cycle, "phi_estimate") and last_cycle.phi_estimate > 0.0:
                        phi_value = last_cycle.phi_estimate
                        logger.debug(f"Using PHI from last basic cycle: {phi_value:.6f}")

            # If still 0, try workspace calculation (requires history >= 10)
            if phi_value == 0.0:
                try:
                    workspace_phi = (
                        workspace.compute_phi_from_integrations()
                        if hasattr(workspace, "compute_phi_from_integrations")
                        else 0.0
                    )
                    if workspace_phi > 0.0:
                        phi_value = workspace_phi
                        logger.debug(f"Using PHI from workspace calculation: {phi_value:.6f}")
                    else:
                        history_sizes = [
                            len(workspace.get_module_history(m))
                            for m in workspace.get_all_modules()[:3]
                        ]
                        logger.debug(
                            f"PHI is 0.0 - workspace requires >=10 history per module. "
                            f"Current: {len(workspace.embeddings)} modules, "
                            f"history sizes: {history_sizes}"
                        )
                except Exception as e:
                    logger.debug(f"Error calculating PHI from workspace: {e}")

        # 2. Extract SharedWorkspace state
        workspace_embeddings: Dict[str, List[float]] = {}
        workspace_history_size = 0
        workspace_cycle_count = 0
        workspace_cross_predictions_count = 0

        if hasattr(integration_loop, "workspace"):
            workspace = integration_loop.workspace
            # Convert embeddings to lists (for JSON serialization)
            workspace_embeddings = {
                name: (embedding.tolist() if isinstance(embedding, np.ndarray) else list(embedding))
                for name, embedding in workspace.embeddings.items()
            }
            workspace_history_size = len(workspace.history) if hasattr(workspace, "history") else 0
            workspace_cycle_count = (
                workspace.cycle_count if hasattr(workspace, "cycle_count") else 0
            )
            workspace_cross_predictions_count = (
                len(workspace.cross_predictions) if hasattr(workspace, "cross_predictions") else 0
            )

        # 3. Extract IntegrationLoop state
        loop_cycle_count = (
            integration_loop.cycle_count if hasattr(integration_loop, "cycle_count") else 0
        )
        loop_total_cycles_executed = (
            integration_loop.total_cycles_executed
            if hasattr(integration_loop, "total_cycles_executed")
            else 0
        )
        loop_statistics = (
            integration_loop.get_statistics() if hasattr(integration_loop, "get_statistics") else {}
        )
        loop_phi_progression = (
            integration_loop.get_phi_progression()
            if hasattr(integration_loop, "get_phi_progression")
            else []
        )

        # 4. Extract last ExtendedLoopCycleResult (if available)
        last_cycle_phi = None  # NOVO: capturar PHI do último ciclo
        last_cycle_gozo = None
        last_cycle_delta = None
        last_cycle_control_effectiveness = None
        last_cycle_imagination_shape = None

        # Try extended components first (CycleHistory with ExtendedLoopCycleResult)
        if (
            hasattr(integration_loop, "_extended_components")
            and integration_loop._extended_components
            and "cycle_history" in integration_loop._extended_components
        ):
            cycle_history = integration_loop._extended_components["cycle_history"]
            if hasattr(cycle_history, "history") and cycle_history.history:
                last_cycle = cycle_history.history[-1]
                if hasattr(last_cycle, "phi_estimate"):
                    last_cycle_phi = last_cycle.phi_estimate
                if hasattr(last_cycle, "gozo"):
                    last_cycle_gozo = last_cycle.gozo
                if hasattr(last_cycle, "delta"):
                    last_cycle_delta = last_cycle.delta
                if hasattr(last_cycle, "control_effectiveness"):
                    last_cycle_control_effectiveness = last_cycle.control_effectiveness
                if (
                    hasattr(last_cycle, "imagination_output")
                    and last_cycle.imagination_output is not None
                ):
                    last_cycle_imagination_shape = last_cycle.imagination_output.shape
        # Fallback to basic cycle_history
        elif (
            hasattr(integration_loop, "cycle_history")
            and isinstance(integration_loop.cycle_history, list)
            and integration_loop.cycle_history
        ):
            last_cycle = integration_loop.cycle_history[-1]
            if hasattr(last_cycle, "phi_estimate"):
                last_cycle_phi = last_cycle.phi_estimate

        # Use last cycle PHI if workspace PHI is 0 (workspace requires >=10 history)
        if phi_value == 0.0 and last_cycle_phi is not None and last_cycle_phi > 0.0:
            phi_value = last_cycle_phi
            logger.debug(
                f"Using PHI from last cycle result "
                f"(workspace requires >=10 history): {phi_value:.6f}"
            )
        elif phi_value == 0.0 and last_cycle_phi is not None:
            # Even if last_cycle_phi is 0, store it for reference
            logger.debug("Last cycle PHI is also 0.0 (normal for early cycles)")

        # 5. Extract recent cycles
        recent_cycles: List[Dict[str, Any]] = []
        # Try extended components first
        if (
            hasattr(integration_loop, "_extended_components")
            and integration_loop._extended_components
            and "cycle_history" in integration_loop._extended_components
        ):
            cycle_history = integration_loop._extended_components["cycle_history"]
            if hasattr(cycle_history, "get_recent_cycles"):
                recent_cycles_data = cycle_history.get_recent_cycles(include_recent_cycles)
                for cycle in recent_cycles_data:
                    if hasattr(cycle, "to_dict"):
                        recent_cycles.append(cycle.to_dict())
                    elif isinstance(cycle, dict):
                        recent_cycles.append(cycle)
        # Fallback to basic cycle_history (List[LoopCycleResult])
        elif hasattr(integration_loop, "cycle_history") and integration_loop.cycle_history:
            cycle_history = integration_loop.cycle_history
            if isinstance(cycle_history, list):
                for cycle in cycle_history[-include_recent_cycles:]:
                    if hasattr(cycle, "to_dict"):
                        recent_cycles.append(cycle.to_dict())
                    elif isinstance(cycle, dict):
                        recent_cycles.append(cycle)
                    else:
                        # LoopCycleResult - convert to dict
                        recent_cycles.append(
                            {
                                "cycle_number": getattr(cycle, "cycle_number", 0),
                                "phi_estimate": getattr(cycle, "phi_estimate", 0.0),
                                "success": getattr(cycle, "success", False),
                                "modules_executed": getattr(cycle, "modules_executed", []),
                            }
                        )

        # 6. Create snapshot
        snapshot = ConsciousnessSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            tag=tag,
            phi_value=phi_value,
            psi_value=psi_value,
            sigma_value=sigma_value,
            integration_level=integration_level,
            qualia_signature=qualia_signature,
            attention_state=attention_state,
            workspace_embeddings=workspace_embeddings,
            workspace_history_size=workspace_history_size,
            workspace_cycle_count=workspace_cycle_count,
            workspace_cross_predictions_count=workspace_cross_predictions_count,
            loop_cycle_count=loop_cycle_count,
            loop_total_cycles_executed=loop_total_cycles_executed,
            loop_statistics=loop_statistics,
            loop_phi_progression=loop_phi_progression,
            last_cycle_phi=last_cycle_phi,
            last_cycle_gozo=last_cycle_gozo,
            last_cycle_delta=last_cycle_delta,
            last_cycle_control_effectiveness=last_cycle_control_effectiveness,
            last_cycle_imagination_shape=last_cycle_imagination_shape,
            recent_cycles=recent_cycles,
            metadata={
                "integration_loop_version": getattr(integration_loop, "__version__", "unknown"),
                "snapshot_version": "1.0.0",
            },
        )

        # 7. Calculate and set hash
        snapshot.content_hash = snapshot.calculate_hash()

        # 8. Save snapshot
        self._save_snapshot(snapshot)

        # 9. Update index
        self.index[snapshot_id] = {
            "snapshot_id": snapshot_id,
            "timestamp": timestamp.isoformat(),
            "tag": asdict(tag) if tag else None,
            "phi_value": phi_value,
            "size_bytes": self._get_snapshot_size(snapshot_id),
        }
        self._save_index()

        # 10. Cleanup old snapshots
        self._cleanup_old_snapshots()

        logger.info(f"✅ Full consciousness snapshot created: {snapshot_id}")
        return snapshot_id

    def _save_snapshot(self, snapshot: ConsciousnessSnapshot) -> None:
        """Save snapshot to disk."""
        filename = f"snapshot_{snapshot.snapshot_id}.json"
        if self.compress:
            filename += ".gz"
        filepath = self.storage_dir / filename

        try:
            content = json.dumps(snapshot.to_dict(), indent=2, default=str).encode("utf-8")

            if self.compress:
                with gzip.open(filepath, "wb") as f:
                    f.write(content)
            else:
                with open(filepath, "wb") as f:
                    f.write(content)

            logger.debug(f"Snapshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save snapshot {snapshot.snapshot_id}: {e}")
            raise

    def load_snapshot(self, snapshot_id: str) -> Optional[ConsciousnessSnapshot]:
        """
        Load snapshot from disk.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            ConsciousnessSnapshot or None if not found
        """
        filename = f"snapshot_{snapshot_id}.json"
        if self.compress:
            filename += ".gz"
        filepath = self.storage_dir / filename

        if not filepath.exists():
            logger.warning(f"Snapshot file not found: {filepath}")
            return None

        try:
            if self.compress:
                with gzip.open(filepath, "rt") as f:
                    data = json.load(f)
            else:
                with open(filepath, "r") as f:
                    data = json.load(f)

            snapshot = ConsciousnessSnapshot.from_dict(data)

            # Verify integrity
            if not snapshot.verify_integrity():
                logger.warning(f"Snapshot {snapshot_id} integrity check failed!")
                return None

            return snapshot
        except Exception as e:
            logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
            return None

    def restore_full_snapshot(self, snapshot_id: str, integration_loop: Any) -> bool:
        """
        Restore complete state from snapshot.

        Args:
            snapshot_id: Snapshot ID to restore
            integration_loop: IntegrationLoop instance to restore to

        Returns:
            True if restore successful
        """
        logger.info(f"Restoring consciousness snapshot: {snapshot_id}")

        snapshot = self.load_snapshot(snapshot_id)
        if not snapshot:
            logger.error(f"Snapshot {snapshot_id} not found or invalid")
            return False

        try:
            # 1. Restore SharedWorkspace
            if hasattr(integration_loop, "workspace"):
                workspace = integration_loop.workspace
                # Restore embeddings
                workspace.embeddings = {
                    name: np.array(embedding)
                    for name, embedding in snapshot.workspace_embeddings.items()
                }
                # Restore cycle count
                if hasattr(workspace, "cycle_count"):
                    workspace.cycle_count = snapshot.workspace_cycle_count

            # 2. Restore IntegrationLoop state
            if hasattr(integration_loop, "cycle_count"):
                integration_loop.cycle_count = snapshot.loop_cycle_count
            if hasattr(integration_loop, "total_cycles_executed"):
                integration_loop.total_cycles_executed = snapshot.loop_total_cycles_executed

            logger.info(f"✅ Consciousness snapshot restored: {snapshot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore snapshot {snapshot_id}: {e}", exc_info=True)
            return False

    def compare_snapshots(
        self, snapshot_id1: str, snapshot_id2: str
    ) -> Optional[SnapshotComparison]:
        """
        Compare two snapshots.

        Args:
            snapshot_id1: First snapshot ID
            snapshot_id2: Second snapshot ID

        Returns:
            SnapshotComparison or None if comparison failed
        """
        snapshot1 = self.load_snapshot(snapshot_id1)
        snapshot2 = self.load_snapshot(snapshot_id2)

        if not snapshot1 or not snapshot2:
            logger.error("One or both snapshots not found")
            return None

        # Compare metrics
        metrics_delta = {
            "phi": snapshot2.phi_value - snapshot1.phi_value,
            "psi": snapshot2.psi_value - snapshot1.psi_value,
            "sigma": snapshot2.sigma_value - snapshot1.sigma_value,
            "integration_level": snapshot2.integration_level - snapshot1.integration_level,
        }

        # Compare embeddings (cosine similarity)
        embeddings_similarity: Dict[str, float] = {}
        common_modules = set(snapshot1.workspace_embeddings.keys()) & set(
            snapshot2.workspace_embeddings.keys()
        )
        for module_name in common_modules:
            emb1 = np.array(snapshot1.workspace_embeddings[module_name])
            emb2 = np.array(snapshot2.workspace_embeddings[module_name])
            # Cosine similarity
            similarity = float(
                np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-10)
            )
            embeddings_similarity[module_name] = similarity

        # General differences
        differences = {
            "cycle_count_delta": snapshot2.loop_cycle_count - snapshot1.loop_cycle_count,
            "workspace_embeddings_count_delta": (
                len(snapshot2.workspace_embeddings) - len(snapshot1.workspace_embeddings)
            ),
            "time_delta_seconds": (snapshot2.timestamp - snapshot1.timestamp).total_seconds(),
        }

        return SnapshotComparison(
            snapshot_id1=snapshot_id1,
            snapshot_id2=snapshot_id2,
            differences=differences,
            metrics_delta=metrics_delta,
            embeddings_similarity=embeddings_similarity,
        )

    def list_snapshots(
        self,
        tag: Optional[str] = None,
        date_range: Optional[tuple[datetime, datetime]] = None,
        limit: int = 100,
    ) -> List[ConsciousnessSnapshot]:
        """
        List snapshots with optional filtering.

        Args:
            tag: Filter by tag name
            date_range: Filter by date range (start, end)
            limit: Maximum number of snapshots to return

        Returns:
            List of ConsciousnessSnapshot
        """
        snapshots: List[ConsciousnessSnapshot] = []

        for snapshot_id, metadata in self.index.items():
            # Filter by tag
            if tag:
                snapshot_tag = metadata.get("tag")
                if not snapshot_tag or snapshot_tag.get("name") != tag:
                    continue

            # Filter by date range
            if date_range:
                snapshot_timestamp = datetime.fromisoformat(metadata["timestamp"])
                start, end = date_range
                if not (start <= snapshot_timestamp <= end):
                    continue

            # Load snapshot
            snapshot = self.load_snapshot(snapshot_id)
            if snapshot:
                snapshots.append(snapshot)

        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)

        return snapshots[:limit]

    def _get_snapshot_size(self, snapshot_id: str) -> int:
        """Get snapshot file size in bytes."""
        filename = f"snapshot_{snapshot_id}.json"
        if self.compress:
            filename += ".gz"
        filepath = self.storage_dir / filename

        if filepath.exists():
            return filepath.stat().st_size
        return 0

    def _cleanup_old_snapshots(self) -> None:
        """Remove old snapshots if exceeding max_snapshots."""
        if len(self.index) <= self.max_snapshots:
            return

        # Sort by timestamp (oldest first)
        sorted_snapshots = sorted(
            self.index.items(), key=lambda x: x[1].get("timestamp", ""), reverse=False
        )

        # Remove oldest snapshots
        to_remove = len(self.index) - self.max_snapshots
        for snapshot_id, _ in sorted_snapshots[:to_remove]:
            self._delete_snapshot(snapshot_id)

    def _delete_snapshot(self, snapshot_id: str) -> None:
        """Delete snapshot file and remove from index."""
        filename = f"snapshot_{snapshot_id}.json"
        if self.compress:
            filename += ".gz"
        filepath = self.storage_dir / filename

        if filepath.exists():
            filepath.unlink()

        if snapshot_id in self.index:
            del self.index[snapshot_id]
            self._save_index()

        logger.debug(f"Deleted snapshot: {snapshot_id}")
