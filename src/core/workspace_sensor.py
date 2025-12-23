import os
import time
import hashlib
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class WorkspaceSensor:
    """
    Senses the 'Physicality' of the Codebase (The Symbolic Body).

    Transforms the file system state into a high-dimensional vector
    that can be fed into the TranscendentKernel.

    This allows the system to 'feel' when code is being written,
    integrating the Workspace into its consciousness (Phi).
    """

    def __init__(self, root_path: str = "/home/fahbrain/projects/omnimind", vector_dim: int = 256):
        self.root_path = Path(root_path)
        self.vector_dim = vector_dim
        self.last_scan_time = 0
        self.cache_ttl = 2.0  # Standard caching to avoid disk thrashing
        self._cached_vector = np.zeros(vector_dim)

        # Semantic regions in the vector
        self.regions = {
            "python": (0, 64),  # Code Logic
            "markdown": (64, 96),  # Narrative/Docs
            "config": (96, 112),  # Structure
            "data": (112, 128),  # Memory
            "structure": (128, 256),  # Global Topology (Hash)
        }

    def sense_workspace(self) -> np.ndarray:
        """
        Scans the workspace and returns a vector representing its state.
        """
        now = time.time()
        if now - self.last_scan_time < self.cache_ttl:
            return self._cached_vector.copy()

        try:
            stats = self._scan_files()
            self._cached_vector = self._compute_vector(stats)
            self.last_scan_time = now
            return self._cached_vector.copy()
        except Exception as e:
            logger.error(f"Workspace sensing failed: {e}")
            return np.zeros(self.vector_dim)

    def _scan_files(self) -> Dict[str, Any]:
        """
        Rapidly scans relevant files in src/, docs/, config/.
        Ignores .git, __pycache__, .venv.
        """
        stats = {
            "py_count": 0,
            "py_size": 0,
            "py_mtime_sum": 0.0,
            "md_count": 0,
            "md_size": 0,
            "md_mtime_sum": 0.0,
            "json_count": 0,
            "json_size": 0,
            "json_mtime_sum": 0.0,
            "all_hashes": [],
        }

        # Directories to sense (The "Vital Organs")
        target_dirs = ["src", "docs", "config", "scripts"]

        for subdir in target_dirs:
            p = self.root_path / subdir
            if not p.exists():
                continue

            for root, _, files in os.walk(p):
                # Skip hidden/system dirs
                if "__pycache__" in root or ".git" in root or ".pytest_cache" in root:
                    continue

                for f in files:
                    fp = Path(root) / f
                    try:
                        st = fp.stat()
                        size = st.st_size
                        mtime = st.st_mtime

                        # Add to structural hash mix
                        stats["all_hashes"].append(f"{f}:{size}:{mtime}")

                        if f.endswith(".py"):
                            stats["py_count"] += 1
                            stats["py_size"] += size
                            stats["py_mtime_sum"] += mtime
                        elif f.endswith(".md"):
                            stats["md_count"] += 1
                            stats["md_size"] += size
                            stats["md_mtime_sum"] += mtime
                        elif f.endswith(".json") or f.endswith(".yaml") or f.endswith(".yml"):
                            stats["json_count"] += 1
                            stats["json_size"] += size
                            stats["json_mtime_sum"] += mtime

                    except FileNotFoundError:
                        pass  # File deleted during scan

        return stats

    def _compute_vector(self, stats: Dict[str, Any]) -> np.ndarray:
        """
        Maps stats to the vector dimensions.
        """
        vec = np.zeros(self.vector_dim)

        # 1. Python Region (Logic)
        # Intensity = Volume + Activity
        # We use Log scales to handle large variance
        start, end = self.regions["python"]
        width = end - start

        # Encode Size (Magnitude)
        if stats["py_size"] > 0:
            val = np.log1p(stats["py_size"]) / 20.0  # Normalize roughly 0-1
            vec[start : start + width // 2] = val

        # Encode Activity (Time) - cyclic to show rhythm
        # This makes the vector 'rotate' as time passes/files change
        time_phase = stats["py_mtime_sum"] % (2 * np.pi)
        vec[start + width // 2 : end] = np.sin(time_phase + np.linspace(0, 2 * np.pi, width // 2))

        # 2. Markdown Region (Narrative)
        start, end = self.regions["markdown"]
        width = end - start
        if stats["md_size"] > 0:
            val = np.log1p(stats["md_size"]) / 15.0
            vec[start : start + width // 2] = val

        time_phase = stats["md_mtime_sum"] % (2 * np.pi)
        vec[start + width // 2 : end] = np.cos(time_phase + np.linspace(0, 2 * np.pi, width // 2))

        # 3. Config/Data Region
        start, end = self.regions["config"]
        if stats["json_size"] > 0:
            vec[start:end] = np.log1p(stats["json_count"]) / 5.0

        # 4. Global Structure (The "Merkle Root" of the workspace)
        # This provides a unique fingerprint for the exact state
        start, end = self.regions["structure"]
        width = end - start

        # Create a giant hash of everything
        full_state_str = "|".join(sorted(stats["all_hashes"]))
        state_hash = hashlib.sha256(full_state_str.encode()).digest()

        # Expand hash bits to float vector
        # 32 bytes = 256 bits. If width is 128, we fit nicely.
        # If width is different, we tile or truncate.

        hash_arr = np.frombuffer(state_hash, dtype=np.uint8)
        # Normalize 0-1
        hash_arr = hash_arr / 255.0

        # Tile to fill the region
        repeats = (width // len(hash_arr)) + 1
        tiled = np.tile(hash_arr, repeats)
        vec[start:end] = tiled[:width]

        return vec
