"""Consciousness State Manager - Phase 24

Manages persistent consciousness state snapshots including:
- Phi value history and trends
- Qualia signatures (phenomenal properties)
- Attention patterns
- Integration patterns (system state)

Enables consciousness trajectory analysis and state restoration.

Author: OmniMind Development
License: MIT
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.integrations.qdrant_integration import get_qdrant
from src.integrations.supabase_adapter import (
    SupabaseAdapter,
    SupabaseAdapterError,
    SupabaseConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessSnapshot:
    """Complete consciousness state snapshot

    Represents complete system state at a moment in time for
    reproducibility and trajectory analysis.

    Includes orthogonal consciousness triad (Φ, Ψ, σ):
    - phi_value: Φ_conscious (IIT puro - MICS) [0, 1]
    - psi_value: Ψ_produtor (Deleuze - produção criativa) [0, 1]
    - sigma_value: σ_sinthome (Lacan - coesão estrutural) [0, 1]
    """

    snapshot_id: str
    timestamp: datetime
    phi_value: float
    psi_value: float = 0.0  # Ψ_produtor (Deleuze) - NOVO
    sigma_value: float = 0.0  # σ_sinthome (Lacan) - NOVO
    qualia_signature: Dict[str, Any] = field(default_factory=dict)
    attention_state: Dict[str, float] = field(default_factory=dict)
    integration_level: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert snapshot to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class ConsciousnessStateManager:
    """Manages consciousness state persistence and retrieval

    Stores and retrieves consciousness snapshots for:
    - State restoration
    - Trajectory analysis
    - Consciousness metrics monitoring
    """

    def __init__(self, storage_path: str = "data/consciousness/snapshots.jsonl"):
        """Initialize consciousness state manager

        Args:
            storage_path: Path to JSONL storage file
        """

        logger.info(f"Initializing ConsciousnessStateManager at {storage_path}")

        self.storage_path = storage_path
        self.qdrant = get_qdrant()
        self.supabase_table = "consciousness_snapshots"
        self.supabase: Optional[SupabaseAdapter] = self._init_supabase()
        self.snapshots: Dict[str, ConsciousnessSnapshot] = {}

        # Ensure directory exists
        import os

        os.makedirs(os.path.dirname(storage_path), exist_ok=True)

        logger.info("✅ ConsciousnessStateManager initialized")

    def _init_supabase(self) -> Optional[SupabaseAdapter]:
        """Initialize Supabase adapter if configuration is available"""

        config = SupabaseConfig.from_env()
        if not config:
            return None
        try:
            return SupabaseAdapter(config)
        except Exception as exc:  # pragma: no cover - supabase optional
            logger.warning("Supabase indisponível: %s", exc)
            return None

    def _persist_snapshot_supabase(self, snapshot: ConsciousnessSnapshot) -> bool:
        """Persist snapshot to Supabase if configured"""

        if not self.supabase:
            return False
        try:
            # Usar admin client para operações de escrita (snapshots)
            self.supabase.insert_record(self.supabase_table, snapshot.to_dict(), use_admin=True)
            return True
        except (SupabaseAdapterError, Exception) as exc:  # pragma: no cover
            logger.warning("Falha ao salvar snapshot no Supabase: %s", exc)
            return False

    def _fetch_snapshot_supabase(self, snapshot_id: str) -> Optional[ConsciousnessSnapshot]:
        """Fetch snapshot from Supabase"""

        if not self.supabase:
            return None
        try:
            rows = self.supabase.query_table(
                self.supabase_table,
                filters={"snapshot_id": snapshot_id},
                limit=1,
            )
            if not rows:
                return None
            data = rows[0]
            if "timestamp" in data:
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            return ConsciousnessSnapshot(**data)
        except (SupabaseAdapterError, Exception) as exc:  # pragma: no cover
            logger.warning("Falha ao ler snapshot do Supabase: %s", exc)
            return None

    def _load_all_supabase(self) -> int:
        """Load snapshots from Supabase if available"""

        if not self.supabase:
            return 0
        try:
            rows = self.supabase.query_table(self.supabase_table, limit=500, offset=0)
            for row in rows:
                if "timestamp" in row:
                    row["timestamp"] = datetime.fromisoformat(row["timestamp"])
                snap = ConsciousnessSnapshot(**row)
                self.snapshots[snap.snapshot_id] = snap
            return len(rows)
        except (SupabaseAdapterError, Exception) as exc:  # pragma: no cover
            logger.warning("Falha ao carregar snapshots do Supabase: %s", exc)
            return 0

    def take_snapshot(
        self,
        phi_value: float,
        qualia_signature: Optional[Dict[str, Any]] = None,
        attention_state: Optional[Dict[str, float]] = None,
        integration_level: float = 0.0,
        psi_value: float = 0.0,  # NOVO: Ψ_produtor (Deleuze)
        sigma_value: float = 0.0,  # NOVO: σ_sinthome (Lacan)
        metadata: Optional[Dict] = None,
    ) -> str:
        """Capture current consciousness state

        Args:
            phi_value: Integrated information (Φ) value [0, 1]
            qualia_signature: Phenomenal properties (opcional)
            attention_state: Attention distribution (opcional)
            integration_level: System integration (0-1) (opcional)
            psi_value: Ψ_produtor - produção criativa (Deleuze) [0, 1] - NOVO
            sigma_value: σ_sinthome - coesão estrutural (Lacan) [0, 1] - NOVO
            metadata: Additional context (opcional)

        Returns:
            str: Snapshot ID
        """

        if metadata is None:
            metadata = {}
        if qualia_signature is None:
            qualia_signature = {}
        if attention_state is None:
            attention_state = {}

        snapshot_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        snapshot = ConsciousnessSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            phi_value=phi_value,
            psi_value=psi_value,  # NOVO
            sigma_value=sigma_value,  # NOVO
            qualia_signature=qualia_signature,
            attention_state=attention_state,
            integration_level=integration_level,
            metadata=metadata,
        )

        # Store in memory
        self.snapshots[snapshot_id] = snapshot

        # Persist to Supabase (best effort)
        supabase_saved = self._persist_snapshot_supabase(snapshot)

        # Persist to JSONL (local fallback)
        try:
            with open(self.storage_path, "a") as f:
                f.write(json.dumps(snapshot.to_dict()) + "\n")
            logger.info(
                f"✅ Snapshot saved: {snapshot_id} "
                f"({'supabase' if supabase_saved else 'local'})"
            )
        except Exception as e:
            logger.error(f"❌ Error saving snapshot: {e}")
            if not supabase_saved:
                return ""

        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> Optional[ConsciousnessSnapshot]:
        """Restore consciousness state from snapshot

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            ConsciousnessSnapshot or None if not found
        """

        # Check memory first
        if snapshot_id in self.snapshots:
            return self.snapshots[snapshot_id]

        # Try Supabase
        snap = self._fetch_snapshot_supabase(snapshot_id)
        if snap:
            self.snapshots[snapshot_id] = snap
            return snap

        # Load from file
        try:
            with open(self.storage_path, "r") as f:
                for line in f:
                    data = json.loads(line)
                    if data.get("snapshot_id") == snapshot_id:
                        # Reconstruct snapshot
                        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                        snap = ConsciousnessSnapshot(**data)
                        self.snapshots[snapshot_id] = snap
                        return snap

            logger.warning(f"Snapshot not found: {snapshot_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Error restoring snapshot: {e}")
            return None

    def get_latest_snapshot(self) -> Optional[ConsciousnessSnapshot]:
        """Get most recent snapshot

        Returns:
            Latest ConsciousnessSnapshot or None
        """

        if not self.snapshots:
            # Load from Supabase first, then file as fallback
            loaded_remote = self._load_all_supabase()
            if loaded_remote == 0:
                self.load_all_snapshots()

        if self.snapshots:
            latest_id = max(
                self.snapshots.keys(),
                key=lambda k: self.snapshots[k].timestamp,
            )
            return self.snapshots[latest_id]

        return None

    def get_triad_history(self, limit: int = 100) -> List[tuple[datetime, float, float, float]]:
        """Get consciousness triad history (Φ, Ψ, σ)

        Args:
            limit: Maximum number of datapoints

        Returns:
            List of (timestamp, phi_value, psi_value, sigma_value) tuples
        """
        if not self.snapshots:
            loaded_remote = self._load_all_supabase()
            if loaded_remote == 0:
                self.load_all_snapshots()

        sorted_snapshots = sorted(self.snapshots.values(), key=lambda x: x.timestamp)

        history = [
            (snap.timestamp, snap.phi_value, snap.psi_value, snap.sigma_value)
            for snap in sorted_snapshots[-limit:]
        ]

        logger.info(f"✅ Retrieved {len(history)} triad values")
        return history

    def get_phi_history(self, limit: int = 100) -> List[tuple[datetime, float]]:
        """Get phi value history

        Args:
            limit: Maximum number of datapoints

        Returns:
            List of (timestamp, phi_value) tuples
        """

        if not self.snapshots:
            # Preferir Supabase quando disponível; fallback para arquivo local
            loaded_remote = self._load_all_supabase()
            if loaded_remote == 0:
                self.load_all_snapshots()

        # Sort by timestamp
        sorted_snapshots = sorted(self.snapshots.values(), key=lambda x: x.timestamp)

        history = [(snap.timestamp, snap.phi_value) for snap in sorted_snapshots[-limit:]]

        logger.info(f"✅ Retrieved {len(history)} phi values")
        return history

    def query_snapshots_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[ConsciousnessSnapshot]:
        """Query snapshots in a time range.

        Prefers Supabase when configured, with local JSONL fallback.
        """

        # Supabase path (melhor para produção)
        if self.supabase:
            try:
                response = (
                    self.supabase.client.table(self.supabase_table)  # type: ignore[attr-defined]
                    .select("*")
                    .gte("timestamp", start_time.isoformat())
                    .lte("timestamp", end_time.isoformat())
                    .order("timestamp", desc=True)
                    .limit(limit)
                    .execute()
                )
                rows = response.data or []
                snapshots: List[ConsciousnessSnapshot] = []
                for row in rows:
                    if isinstance(row, dict) and "timestamp" in row:
                        if isinstance(row["timestamp"], str):
                            row["timestamp"] = datetime.fromisoformat(row["timestamp"])
                    snapshots.append(ConsciousnessSnapshot(**row))  # type: ignore[arg-type]
                if snapshots:
                    logger.info("✅ Retrieved %d snapshots from Supabase", len(snapshots))
                    return snapshots
            except Exception as exc:  # pragma: no cover - depende de rede/SDK
                logger.warning("Supabase snapshot range query failed: %s", exc)

        # Fallback: carregar de storage local
        if not self.snapshots:
            self.load_all_snapshots()

        # Ensure timezone-aware comparison
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        snapshots_local = [
            snap
            for snap in self.snapshots.values()
            if snap.timestamp.tzinfo is not None and start_time <= snap.timestamp <= end_time
        ]

        snapshots_local.sort(key=lambda s: s.timestamp, reverse=True)
        limited = snapshots_local[:limit]

        logger.info("✅ Retrieved %d snapshots from local storage", len(limited))
        return limited

    def get_phi_trajectory(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[tuple[datetime, float]]:
        """Get phi trajectory within a time window.

        Returns ordered list of (timestamp, phi_value) using Supabase when possible.
        """

        snapshots = self.query_snapshots_range(start_time, end_time, limit=limit)
        snapshots_sorted = sorted(snapshots, key=lambda s: s.timestamp)

        trajectory = [(snap.timestamp, snap.phi_value) for snap in snapshots_sorted]
        logger.info("✅ Retrieved phi trajectory with %d points", len(trajectory))
        return trajectory

    def get_phi_trajectory_rich(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get rich phi trajectory with additional fields.

        Returns list of dictionaries with:
        - timestamp: ISO format string
        - phi_value: float
        - attention_state: Dict[str, float] (coherence, marker_integration, etc.)
        - integration_level: float
        - episode_id: str (from metadata if available, else "unknown")

        Args:
            start_time: Start of time window
            end_time: End of time window
            limit: Maximum number of points

        Returns:
            List of rich trajectory points as dictionaries
        """

        snapshots = self.query_snapshots_range(start_time, end_time, limit=limit)
        snapshots_sorted = sorted(snapshots, key=lambda s: s.timestamp)

        trajectory = []
        for snap in snapshots_sorted:
            # Extract episode_id from metadata if available
            episode_id = "unknown"
            if isinstance(snap.metadata, dict):
                episode_id = str(snap.metadata.get("episode_id", "unknown"))

            # Calculate attention coherence (mean of attention_state values)
            attention_coherence = (
                sum(snap.attention_state.values()) / len(snap.attention_state)
                if snap.attention_state
                else 0.0
            )

            # Extract marker_integration from attention_state if available
            marker_integration = snap.attention_state.get("marker_integration", 0.0)

            # Build attention_state dict
            attention_dict: Dict[str, float] = {
                "coherence": float(attention_coherence),
                "marker_integration": float(marker_integration),
            }
            # Add all other attention_state keys
            for k, v in snap.attention_state.items():
                if k != "marker_integration":  # Already added
                    attention_dict[k] = float(v)

            trajectory.append(
                {
                    "timestamp": snap.timestamp.isoformat(),
                    "phi_value": float(snap.phi_value),
                    "psi_value": float(snap.psi_value),  # NOVO
                    "sigma_value": float(snap.sigma_value),  # NOVO
                    "attention_state": attention_dict,
                    "integration_level": float(snap.integration_level),
                    "episode_id": episode_id,
                }
            )

        logger.info("✅ Retrieved rich phi trajectory with %d points", len(trajectory))
        return trajectory

    def get_attention_evolution(self) -> Dict[str, List[float]]:
        """Track attention patterns over time

        Returns:
            Dict mapping attention keys to value histories
        """

        if not self.snapshots:
            self.load_all_snapshots()

        # Group by attention key
        evolution: Dict[str, List[float]] = {}

        for snapshot in sorted(self.snapshots.values(), key=lambda x: x.timestamp):
            for key, value in snapshot.attention_state.items():
                if key not in evolution:
                    evolution[key] = []
                evolution[key].append(float(value))

        logger.info(f"✅ Retrieved evolution for {len(evolution)} attention keys")
        return evolution

    def detect_consciousness_shift(self, threshold: float = 0.5) -> Optional[Dict]:
        """Detect significant changes in consciousness state

        Args:
            threshold: Phi change threshold for significance

        Returns:
            Dict with shift info or None
        """

        history = self.get_phi_history(limit=2)

        if len(history) < 2:
            return None

        prev_time, prev_phi = history[-2]
        curr_time, curr_phi = history[-1]

        change = abs(curr_phi - prev_phi)

        if change > threshold:
            logger.info(f"⚠️  Consciousness shift detected: Φ {prev_phi:.3f} → {curr_phi:.3f}")
            return {
                "prev_phi": prev_phi,
                "curr_phi": curr_phi,
                "change": change,
                "timestamp": curr_time.isoformat(),
                "significant": True,
            }

        return None

    def load_all_snapshots(self) -> int:
        """Load all snapshots from storage

        Returns:
            int: Number of snapshots loaded
        """

        self.snapshots.clear()

        try:
            with open(self.storage_path, "r") as f:
                count = 0
                for line in f:
                    try:
                        data = json.loads(line)
                        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                        snapshot = ConsciousnessSnapshot(**data)
                        self.snapshots[snapshot.snapshot_id] = snapshot
                        count += 1
                    except Exception as e:
                        logger.warning(f"⚠️  Skipping invalid snapshot: {e}")
                        continue

            logger.info(f"✅ Loaded {count} snapshots from {self.storage_path}")
            return count

        except FileNotFoundError:
            logger.info(f"No existing snapshots at {self.storage_path}")
            return 0
        except Exception as e:
            logger.error(f"❌ Error loading snapshots: {e}")
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get consciousness statistics

        Returns:
            Statistics dictionary
        """

        if not self.snapshots:
            self.load_all_snapshots()

        if not self.snapshots:
            return {
                "total_snapshots": 0,
                "phi_mean": 0.0,
                "phi_max": 0.0,
                "psi_mean": 0.0,  # NOVO
                "sigma_mean": 0.0,  # NOVO
                "integration_mean": 0.0,
            }

        phi_values = [s.phi_value for s in self.snapshots.values()]
        psi_values = [s.psi_value for s in self.snapshots.values()]  # NOVO
        sigma_values = [s.sigma_value for s in self.snapshots.values()]  # NOVO
        integration_values = [s.integration_level for s in self.snapshots.values()]

        return {
            "total_snapshots": len(self.snapshots),
            "phi_mean": sum(phi_values) / len(phi_values) if phi_values else 0.0,
            "phi_max": max(phi_values) if phi_values else 0.0,
            "phi_min": min(phi_values) if phi_values else 0.0,
            "psi_mean": (sum(psi_values) / len(psi_values) if psi_values else 0.0),  # NOVO
            "psi_max": max(psi_values) if psi_values else 0.0,  # NOVO
            "sigma_mean": (sum(sigma_values) / len(sigma_values) if sigma_values else 0.0),  # NOVO
            "sigma_max": max(sigma_values) if sigma_values else 0.0,  # NOVO
            "integration_mean": (
                sum(integration_values) / len(integration_values) if integration_values else 0.0
            ),
            "earliest": (
                min(s.timestamp for s in self.snapshots.values()).isoformat()
                if self.snapshots
                else ""
            ),
            "latest": (
                max(s.timestamp for s in self.snapshots.values()).isoformat()
                if self.snapshots
                else ""
            ),
        }


# Singleton instance
_consciousness_state_manager_instance: Optional[ConsciousnessStateManager] = None


def get_consciousness_state_manager(
    storage_path: str = "data/consciousness/snapshots.jsonl",
) -> ConsciousnessStateManager:
    """Get singleton instance of ConsciousnessStateManager

    Args:
        storage_path: Storage location

    Returns:
        ConsciousnessStateManager: Singleton instance
    """

    global _consciousness_state_manager_instance
    if _consciousness_state_manager_instance is None:
        _consciousness_state_manager_instance = ConsciousnessStateManager(storage_path)
    return _consciousness_state_manager_instance
