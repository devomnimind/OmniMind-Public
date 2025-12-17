"""
Tests for Phase 24 → Phase 25 Φ-trajectory transformation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np
import pytest

from src.quantum_consciousness.phi_trajectory_transformer import (
    PhiTrajectoryPoint,
    PhiTrajectoryTransformer,
    QuantumInputFeatures,
)


class TestPhiTrajectoryPoint:
    """Basic tests for PhiTrajectoryPoint dataclass."""

    def test_create_point(self) -> None:
        """Test creating a trajectory point."""
        point = PhiTrajectoryPoint(
            timestamp=100.0,
            phi_value=0.45,
            attention_coherence=0.8,
            marker_integration=0.7,
            integration_level=0.5,
            episode_id="ep_001",
        )

        assert point.phi_value == pytest.approx(0.45)
        assert point.episode_id == "ep_001"
        assert 0.0 <= point.attention_coherence <= 1.0


class TestPhiTrajectoryTransformer:
    """Tests for PhiTrajectoryTransformer pipeline."""

    @pytest.fixture
    def mock_trajectory_minimal(self) -> List[dict]:
        """Mock Phase 24 trajectory in current flat JSON format."""
        return [
            {"timestamp": "2025-12-05T10:00:00+00:00", "phi_value": 0.3 + i * 0.05}
            for i in range(10)
        ]

    @pytest.fixture
    def mock_trajectory_rich(self) -> List[dict]:
        """Mock Phase 24 trajectory containing optional fields."""
        return [
            {
                "timestamp": 100.0 + i * 10,
                "phi_value": 0.2 + i * 0.03,
                "attention_state": {
                    "coherence": 0.5 + i * 0.01,
                    "marker_integration": 0.6,
                },
                "integration_level": 0.4,
                "episode_id": f"ep_{i:03d}",
            }
            for i in range(12)
        ]

    @pytest.fixture
    def transformer(self, tmp_path: Path) -> PhiTrajectoryTransformer:
        """Create transformer with temporary trajectory file."""
        traj_file = tmp_path / "phi_trajectory.json"
        return PhiTrajectoryTransformer(trajectory_file=traj_file, min_trajectory_length=5)

    def test_init(self, transformer: PhiTrajectoryTransformer) -> None:
        """Test transformer initialization."""
        assert transformer.min_trajectory_length == 5

    def test_load_trajectory_flat_list(
        self, transformer: PhiTrajectoryTransformer, tmp_path: Path
    ) -> None:
        """Test loading current flat-list Phase 24 format."""
        traj_file = tmp_path / "phi_trajectory.json"
        data = [{"timestamp": "2025-12-05T10:00:00+00:00", "phi_value": 0.5}]
        traj_file.write_text(json.dumps(data))

        transformer.trajectory_file = traj_file
        loaded = transformer.load_trajectory()

        assert isinstance(loaded, list)
        assert loaded[0]["phi_value"] == 0.5

    def test_validate_trajectory_success(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_minimal: List[dict]
    ) -> None:
        """Test trajectory validation passes with sufficient points."""
        # Should not raise
        transformer.validate_trajectory(mock_trajectory_minimal)

    def test_validate_trajectory_too_short(self, transformer: PhiTrajectoryTransformer) -> None:
        """Test validation fails when trajectory is too short."""
        short_traj = [
            {"timestamp": "2025-12-05T10:00:00+00:00", "phi_value": 0.5},
        ]
        with pytest.raises(ValueError, match="Trajectory too short"):
            transformer.validate_trajectory(short_traj)

    def test_validate_trajectory_phi_out_of_range(
        self, transformer: PhiTrajectoryTransformer
    ) -> None:
        """Test that out-of-range Φ values are clipped."""
        traj = [
            {"timestamp": "2025-12-05T10:00:00+00:00", "phi_value": -0.5},
            {"timestamp": "2025-12-05T10:10:00+00:00", "phi_value": 1.5},
        ]
        transformer.min_trajectory_length = 2
        transformer.validate_trajectory(traj)

        # Type narrowing: phi_value should be float after validation
        phi0 = traj[0].get("phi_value")
        phi1 = traj[1].get("phi_value")
        assert isinstance(phi0, (int, float)) and 0.0 <= float(phi0) <= 1.0
        assert isinstance(phi1, (int, float)) and 0.0 <= float(phi1) <= 1.0

    def test_parse_trajectory_minimal(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_minimal: List[dict]
    ) -> None:
        """Test parsing minimal flat-list trajectory to typed points."""
        points = transformer.parse_trajectory(mock_trajectory_minimal)

        assert len(points) == len(mock_trajectory_minimal)
        assert isinstance(points[0], PhiTrajectoryPoint)
        assert points[0].episode_id == "unknown"

    def test_parse_trajectory_rich(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_rich: List[dict]
    ) -> None:
        """Test parsing trajectory with optional fields."""
        points = transformer.parse_trajectory(mock_trajectory_rich)

        assert len(points) == len(mock_trajectory_rich)
        assert points[0].attention_coherence > 0.0
        assert points[0].episode_id.startswith("ep_")

    def test_extract_features(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_rich: List[dict]
    ) -> None:
        """Test feature extraction end-to-end."""
        points = transformer.parse_trajectory(mock_trajectory_rich)
        features = transformer.extract_features(points)

        assert isinstance(features, QuantumInputFeatures)
        assert len(features.phi_sequence) == len(points)
        assert 0.0 <= features.phi_mean <= 1.0
        assert features.phi_std >= 0.0
        assert features.quantum_amplitudes.shape == (len(points), 2)

    def test_quantum_amplitudes_normalized(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_rich: List[dict]
    ) -> None:
        """Test that quantum amplitudes are normalized per time step."""
        points = transformer.parse_trajectory(mock_trajectory_rich)
        features = transformer.extract_features(points)

        norms = np.linalg.norm(features.quantum_amplitudes, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-6)

    def test_validate_quantum_features_success(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_rich: List[dict]
    ) -> None:
        """Test quantum features validation passes for valid data."""
        points = transformer.parse_trajectory(mock_trajectory_rich)
        features = transformer.extract_features(points)

        # Should not raise
        transformer.validate_quantum_features(features)

    def test_validate_quantum_features_nan(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_rich: List[dict]
    ) -> None:
        """Test validation catches NaN in Φ sequence."""
        points = transformer.parse_trajectory(mock_trajectory_rich)
        features = transformer.extract_features(points)
        features.phi_sequence[0] = np.nan

        with pytest.raises(ValueError, match="NaN"):
            transformer.validate_quantum_features(features)

    def test_to_dict_structure(
        self, transformer: PhiTrajectoryTransformer, mock_trajectory_rich: List[dict]
    ) -> None:
        """Test exporting features to a JSON-serializable dict."""
        points = transformer.parse_trajectory(mock_trajectory_rich)
        features = transformer.extract_features(points)

        data = transformer.to_dict(features)
        assert "phi_sequence" in data
        assert "quantum_amplitudes_magnitude" in data
        assert isinstance(data["phi_sequence"], list)
        assert data["metadata"]["trajectory_length"] == len(points)

    def test_full_transform_pipeline(self, tmp_path: Path) -> None:
        """Test full transformation pipeline using a temporary JSON file."""
        # Create mock trajectory file with the current Phase 24 format
        traj = [
            {"timestamp": "2025-12-05T10:00:00+00:00", "phi_value": 0.3 + i * 0.02}
            for i in range(15)
        ]
        traj_file = tmp_path / "phi_trajectory.json"
        traj_file.write_text(json.dumps(traj))

        transformer = PhiTrajectoryTransformer(
            trajectory_file=traj_file,
            min_trajectory_length=10,
        )

        features = transformer.transform()

        assert isinstance(features, QuantumInputFeatures)
        assert len(features.phi_sequence) == len(traj)
        assert features.quantum_amplitudes.shape == (len(traj), 2)
