"""
Phase 24 → Phase 25 Bridge: Convert Φ-trajectory to quantum input features.

Author: OmniMind Autonomous Development (Fabrício da Silva + IA)
Date: 2025-12-05

Purpose:
    - Read Phase 24 Φ-trajectory JSON exported by `scripts/export_phi_trajectory.py`
    - Extract quantum-relevant features (Φ values, basic temporal dynamics)
    - Prepare normalized amplitude vectors suitable as input for Phase 25
      hybrid quantum Φ calculators.

Notes on OmniMind-specific adaptation:
    - The current Phase 24 export format is a flat JSON list:
          [{"timestamp": "...", "phi_value": ...}, ...]
      We DO NOT assume richer fields like attention_state/integration_level
      are present yet. When those fields appear in future exports, this
      transformer will make best-effort use of them, but it already works
      with the existing minimal format.

Status (2025-12-05):
    - ✅ `export_phi_trajectory.py` expanded to include rich fields (--rich flag)
    - ✅ `ConsciousnessStateManager.get_phi_trajectory_rich()` implemented
    - ✅ Transformer now consumes rich format when available
    - ✅ Backward compatible with simple format (timestamp + phi_value only)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PhiTrajectoryPoint:
    """Single point in consciousness trajectory.

    Attributes:
        timestamp: POSIX timestamp (seconds since epoch)
        phi_value: Φ value in [0, 1] (clipped if needed)
        attention_coherence: optional coherence proxy (0–1, default 0.0)
        marker_integration: optional marker integration proxy (0–1, default 0.0)
        integration_level: optional integration proxy (0–1, default 0.0)
        episode_id: identifier for episode (if available, else "unknown")
    """

    timestamp: float
    phi_value: float
    attention_coherence: float
    marker_integration: float
    integration_level: float
    episode_id: str


@dataclass
class QuantumInputFeatures:
    """Features extracted for quantum computation."""

    phi_sequence: np.ndarray  # [T,] Φ values over time
    phi_mean: float
    phi_std: float
    phi_trend: float  # Linear slope of Φ over index

    coherence_sequence: np.ndarray  # [T,] attention coherence
    coherence_mean: float

    integration_sequence: np.ndarray  # [T,] integration level proxy
    integration_mean: float

    timestamps: np.ndarray  # [T,] time points (float seconds)
    episode_ids: List[str]  # Episode identifiers (or "unknown")

    quantum_amplitudes: np.ndarray  # [T, 2] complex amplitudes |ψ⟩


class PhiTrajectoryTransformer:
    """Convert Phase 24 Φ-trajectory to Phase 25 quantum input.

    Pipeline:
        1. Load Phase 24 trajectory JSON (current format: list of dicts)
        2. Parse and validate numerical data
        3. Extract quantum-relevant features
        4. Normalize for quantum computation
        5. Generate quantum amplitude vectors

    This implementation is deliberately conservative and aligned
    with the current OmniMind codebase. It does not assume extra
    fields beyond those exported by `export_phi_trajectory.py`,
    but it will consume them if present.
    """

    def __init__(
        self,
        trajectory_file: Path | None = None,
        min_trajectory_length: int = 5,
    ) -> None:
        """Initialize transformer.

        Args:
            trajectory_file: Path to Phase 24 trajectory JSON
            min_trajectory_length: Minimum number of points required
        """

        if trajectory_file is None:
            # Default: latest trajectory exported by scripts/export_phi_trajectory.py
            # We don't guess the timestamped name, this is only for explicit use.
            trajectory_file = Path("data/test_reports/phi_trajectory_latest.json")

        self.trajectory_file = trajectory_file
        self.min_trajectory_length = min_trajectory_length

    # --------------------------- Load & Validate --------------------------- #

    def load_trajectory(self) -> List[Dict[str, Any]]:
        """Load Phase 24 Φ-trajectory from JSON.

        Supports current OmniMind format:
            [
              {"timestamp": "2025-12-05T10:00:00+00:00", "phi_value": 0.42},
              ...
            ]

        As a forward-compatible fallback, if the JSON is a dict with key
        "trajectory", we read from that field instead.
        """

        if not self.trajectory_file.exists():
            raise FileNotFoundError(
                f"Trajectory file not found: {self.trajectory_file}. "
                "Use scripts/export_phi_trajectory.py to generate it."
            )

        logger.info("Loading Φ-trajectory from %s", self.trajectory_file)
        raw: Any = json.loads(self.trajectory_file.read_text())

        data: List[Dict[str, Any]]
        if isinstance(raw, dict) and "trajectory" in raw:
            traj = raw.get("trajectory", [])
            if not isinstance(traj, list):
                raise ValueError("trajectory field must be a list")
            data = [dict(p) for p in traj]
        elif isinstance(raw, list):
            data = [dict(p) for p in raw]
        else:
            raise ValueError(f"Unexpected trajectory JSON structure: {type(raw)!r}")

        logger.info("Loaded %d trajectory points", len(data))
        return data

    def validate_trajectory(self, trajectory: Sequence[Dict[str, Any]]) -> None:
        """Validate trajectory structure and values.

        - Requires at least `min_trajectory_length` points
        - Requires keys: "timestamp" and "phi_value"
        - Clips Φ values into [0, 1]
        """

        length = len(trajectory)
        if length < self.min_trajectory_length:
            raise ValueError(f"Trajectory too short: {length} (min: {self.min_trajectory_length})")

        required_keys = {"timestamp", "phi_value"}
        for point in trajectory:
            if not required_keys.issubset(point.keys()):
                raise ValueError(f"Missing keys in trajectory point: {point}")

            phi = float(point["phi_value"])
            if not (0.0 <= phi <= 1.0):
                logger.warning("Φ out of range [0,1]: %s (clipping)", phi)
                point["phi_value"] = float(np.clip(phi, 0.0, 1.0))

        logger.info("✅ Trajectory validation passed")

    # --------------------------- Parsing & Features --------------------------- #

    def _parse_timestamp(self, ts: str | float | int) -> float:
        """Parse timestamp from ISO string or numeric into POSIX seconds."""

        if isinstance(ts, (float, int)):
            return float(ts)

        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.timestamp()
        except Exception:
            logger.warning("Unrecognized timestamp format %r, using 0.0", ts)
            return 0.0

    def parse_trajectory(
        self,
        trajectory: Sequence[Dict[str, Any]],
    ) -> List[PhiTrajectoryPoint]:
        """Parse trajectory dicts to typed PhiTrajectoryPoint instances."""

        points: List[PhiTrajectoryPoint] = []

        for point in trajectory:
            attention = point.get("attention_state") or {}
            timestamp = self._parse_timestamp(point["timestamp"])
            phi_value = float(point["phi_value"])

            parsed = PhiTrajectoryPoint(
                timestamp=timestamp,
                phi_value=phi_value,
                attention_coherence=float(attention.get("coherence", 0.0)),
                marker_integration=float(attention.get("marker_integration", 0.0)),
                integration_level=float(point.get("integration_level", 0.0)),
                episode_id=str(point.get("episode_id", "unknown")),
            )
            points.append(parsed)

        return points

    def extract_features(self, points: Sequence[PhiTrajectoryPoint]) -> QuantumInputFeatures:
        """Extract quantum-relevant features from trajectory."""

        if not points:
            raise ValueError("No points to extract features from")

        phi_seq = np.array([p.phi_value for p in points], dtype=float)
        coh_seq = np.array([p.attention_coherence for p in points], dtype=float)
        integ_seq = np.array([p.integration_level for p in points], dtype=float)
        timestamps = np.array([p.timestamp for p in points], dtype=float)
        episode_ids = [p.episode_id for p in points]

        phi_mean = float(np.mean(phi_seq))
        phi_std = float(np.std(phi_seq))

        # Linear trend of Φ over index
        if len(phi_seq) > 1:
            x = np.arange(len(phi_seq), dtype=float)
            coeffs = np.polyfit(x, phi_seq, 1)
            phi_trend = float(coeffs[0])
        else:
            phi_trend = 0.0

        coherence_mean = float(np.mean(coh_seq))
        integration_mean = float(np.mean(integ_seq))

        quantum_amplitudes = self._generate_quantum_amplitudes(phi_seq, coh_seq)

        features = QuantumInputFeatures(
            phi_sequence=phi_seq,
            phi_mean=phi_mean,
            phi_std=phi_std,
            phi_trend=phi_trend,
            coherence_sequence=coh_seq,
            coherence_mean=coherence_mean,
            integration_sequence=integ_seq,
            integration_mean=integration_mean,
            timestamps=timestamps,
            episode_ids=episode_ids,
            quantum_amplitudes=quantum_amplitudes,
        )

        logger.info(
            "✅ Features extracted: Φ_mean=%.4f, Φ_std=%.4f, Φ_trend=%.6f, "
            "coherence_mean=%.4f, integration_mean=%.4f",
            phi_mean,
            phi_std,
            phi_trend,
            coherence_mean,
            integration_mean,
        )
        return features

    def _generate_quantum_amplitudes(
        self,
        phi_seq: np.ndarray,
        coherence_seq: np.ndarray,
    ) -> np.ndarray:
        """Generate 2D quantum amplitudes from Φ and coherence proxies.

        We map to a simple single-qubit state:

            |ψ⟩ = cos(θ)|0⟩ + sin(φ)|1⟩

        where:
            θ ∝ Φ_value  (scaled from [0,1] to [0, π])
            φ ∝ coherence (scaled from [0,1] to [0, π])
        """

        length = phi_seq.shape[0]
        amplitudes: np.ndarray = np.zeros((length, 2), dtype=complex)

        for idx in range(length):
            theta = float(np.pi * np.clip(phi_seq[idx], 0.0, 1.0))
            phi_angle = float(np.pi * np.clip(coherence_seq[idx], 0.0, 1.0))

            amplitudes[idx, 0] = np.cos(theta)
            amplitudes[idx, 1] = np.sin(phi_angle)

        # Normalize each state
        norms = np.linalg.norm(amplitudes, axis=1, keepdims=True)
        amplitudes = amplitudes / (norms + 1e-12)

        return amplitudes

    # --------------------------- Validation & IO --------------------------- #

    def validate_quantum_features(self, features: QuantumInputFeatures) -> None:
        """Validate that quantum features are numerically sound."""

        if np.any(np.isnan(features.phi_sequence)):
            raise ValueError("NaN in phi_sequence")
        if np.any(np.isinf(features.phi_sequence)):
            raise ValueError("Inf in phi_sequence")

        norms = np.linalg.norm(features.quantum_amplitudes, axis=1)
        if not np.allclose(norms, 1.0, atol=1e-6):
            logger.warning("Quantum amplitudes not perfectly normalized: %s", norms)

        if not (0.0 <= features.phi_mean <= 1.0):
            raise ValueError(f"Φ mean out of expected range [0,1]: {features.phi_mean}")
        if features.phi_std < 0.0:
            raise ValueError("Φ std must be non-negative")

        logger.info("✅ Quantum features validation passed")

    def transform(self) -> QuantumInputFeatures:
        """Full pipeline: Load → Validate → Parse → Extract → Validate."""

        logger.info("Starting Phase 24 → Phase 25 Φ-trajectory transformation")
        raw = self.load_trajectory()
        self.validate_trajectory(raw)
        points = self.parse_trajectory(raw)
        features = self.extract_features(points)
        self.validate_quantum_features(features)
        logger.info("✅ Phase 24 → Phase 25 transformation complete")
        return features

    def to_dict(self, features: QuantumInputFeatures) -> Dict[str, Any]:
        """Export features to a JSON-serializable dictionary."""

        return {
            "phi_sequence": features.phi_sequence.tolist(),
            "phi_mean": float(features.phi_mean),
            "phi_std": float(features.phi_std),
            "phi_trend": float(features.phi_trend),
            "coherence_sequence": features.coherence_sequence.tolist(),
            "coherence_mean": float(features.coherence_mean),
            "integration_sequence": features.integration_sequence.tolist(),
            "integration_mean": float(features.integration_mean),
            "timestamps": features.timestamps.tolist(),
            "episode_ids": features.episode_ids,
            "quantum_amplitudes_magnitude": np.abs(features.quantum_amplitudes).tolist(),
            "metadata": {
                "trajectory_length": int(features.phi_sequence.shape[0]),
                # quantum_bins not explicitly used yet – reserved for future expansion
                "transformed_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    def save_features(
        self,
        features: QuantumInputFeatures,
        output_file: Path | None = None,
    ) -> Path:
        """Save features to JSON file for Phase 25 consumption."""

        if output_file is None:
            output_file = Path("exports/quantum_input_features.json")

        output_file.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict(features)
        output_file.write_text(json.dumps(data, indent=2))

        logger.info("✅ Quantum input features saved to %s", output_file)
        return output_file


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    transformer = PhiTrajectoryTransformer()
    try:
        feats = transformer.transform()
        out_path = transformer.save_features(feats)

        print(f"\n✅ Quantum input features ready at: {out_path}")
        print(f"   Φ values: {len(feats.phi_sequence)} points")
        print(f"   Φ range: [{feats.phi_sequence.min():.4f}, " f"{feats.phi_sequence.max():.4f}]")
        print(f"   Quantum amplitudes: shape {feats.quantum_amplitudes.shape}")
    except Exception as exc:  # pragma: no cover - CLI convenience
        logger.error("❌ Transformation failed: %s", exc)
        raise
