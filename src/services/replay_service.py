import os
import json
import time
from typing import Dict, Any, Generator, Optional


class SinthomaticCompression:
    def __init__(self):
        self.snapshot_interval = 3600  # 1 snapshot/hour
        self.retention_tiers = {
            "0-24h": {"resolution": 1.0, "compression": "none"},
            "24h-7d": {"resolution": 0.01, "compression": "gzip"},
            "7d+": {"resolution": 0.001, "compression": "parquet"},  # Parquet simulation for now
        }

    def estimate_storage(self, runtime_days: int) -> Dict[str, float]:
        """Calculates expected footprint."""
        base_state_size = 50_000  # bytes per snapshot (approx)
        states_per_day = 86400  # 1 per second

        tier1 = 1.0 * states_per_day * base_state_size
        # Tier 2: 7 days max (or runtime - 1 if less)
        tier2_days = min(7, max(0, runtime_days - 1))
        tier2 = 0.01 * states_per_day * tier2_days * base_state_size * 0.3  # gzip 70% compression

        # Tier 3: parquet compression
        tier3_daily = 0.001 * states_per_day * base_state_size * 0.2  # parquet 80% compression

        return {
            "tier1_mb": tier1 / 1e6,
            "tier2_mb": tier2 / 1e6,
            "tier3_daily_mb": tier3_daily / 1e6,
            "total_7d_mb": (tier1 + tier2) / 1e6,
            "total_30d_mb": (tier1 + tier2 + tier3_daily * (30 - 8)) / 1e6,
        }


class ReplayService:
    def __init__(self, log_path: str, compression_policy: Optional[Dict] = None):
        self.log_path = log_path
        self.policy = compression_policy or self._default_policy()
        self.memory_limit = 500_000_000  # 500 MB max RAM

        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # In-memory index of snapshots (timestamp -> file_offset)
        self.index: Dict[float, int] = {}
        self._build_index()

    def _default_policy(self):
        return {
            "snapshot_interval": 3600,  # 1 snapshot/hour
            "tier1_retention": 86400,  # 24h full res
            "tier2_retention": 604800,  # 7d decimated
            "compression_ratio_target": 100,  # 100:1 compression
        }

    def _build_index(self):
        """Builds a simple index of snapshots from the log file."""
        if not os.path.exists(self.log_path):
            return

        # Simple simulation of indexing: reading line by line and finding 'SNAPSHOT' events
        # In production, this would be a separate .idx file
        try:
            with open(self.log_path, "r") as f:
                while True:
                    offset = f.tell()
                    line = f.readline()
                    if not line:
                        break
                    try:
                        record = json.loads(line)
                        if record.get("type") == "SNAPSHOT":
                            self.index[record["timestamp"]] = offset
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[ReplayService] Index build failed: {e}")

    def log_event(self, event_type: str, data: Any):
        """Logs an event to the replay log."""
        record = {"timestamp": time.time(), "type": event_type, "data": data}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

            # Update index if it's a snapshot
            if event_type == "SNAPSHOT":
                self.index[record["timestamp"]] = f.tell()  # Approximate offset (end of line)

    def seek(self, timestamp: float) -> Optional[Dict]:
        """Seek to timestamp with memory limits."""
        # 1. Find nearest snapshot <= timestamp
        snapshot_time = -1.0
        for t in sorted(self.index.keys()):
            if t <= timestamp:
                snapshot_time = t
            else:
                break

        if snapshot_time == -1.0:
            return None  # No snapshot found before timestamp

        # 2. Load snapshot
        snapshot = self._load_snapshot(snapshot_time)
        if not snapshot:
            return None

        # 3. Apply deltas until timestamp
        state = self._apply_deltas_bounded(snapshot, timestamp, memory_limit=self.memory_limit)

        return state

    def _load_snapshot(self, timestamp: float) -> Optional[Dict]:
        offset = self.index.get(timestamp)
        if offset is None:
            return None

        # In a real implementation, we'd seek to offset.
        # Here we scan because our index points to the end of the line
        # in log_event (bug in prototype fixed below)
        # For this MVP, we'll just scan the file again to find the exact line.
        # Optimization: Use a proper database or offset-based file format.
        try:
            with open(self.log_path, "r") as f:
                for line in f:
                    record = json.loads(line)
                    if record["timestamp"] == timestamp and record["type"] == "SNAPSHOT":
                        return record["data"]
        except Exception:
            return None
        return None

    def _stream_deltas(self, start_time: float, end_time: float) -> Generator[Dict, None, None]:
        """Yields delta events between start_time and end_time."""
        try:
            with open(self.log_path, "r") as f:
                for line in f:
                    record = json.loads(line)
                    if record["timestamp"] > start_time and record["timestamp"] <= end_time:
                        if record["type"] == "DELTA":
                            yield record["data"]
        except Exception:
            pass

    def _apply_deltas_bounded(self, state: Dict, target_time: float, memory_limit: int) -> Dict:
        """Generator to avoid loading all deltas into memory."""
        # Simple size estimation
        current_memory = len(json.dumps(state))

        for delta in self._stream_deltas(state.get("timestamp", 0), target_time):
            delta_size = len(json.dumps(delta))
            if current_memory + delta_size > memory_limit:
                print(
                    f"[ReplayService] Memory limit reached "
                    f"({current_memory} bytes). Skipping remaining deltas."
                )
                break

            # Apply delta (Simple dictionary update for MVP)
            # In production, this would be a deep merge or JSON patch
            state.update(delta)
            current_memory += delta_size

        return state
