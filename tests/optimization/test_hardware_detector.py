import json
from pathlib import Path
from src.optimization.hardware_detector import (

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

"""
Tests for hardware detection and auto-configuration.
"""


    HardwareDetector,
    HardwareProfile,
    OptimizationConfig,
    auto_configure,
    load_hardware_profile,
    load_optimization_config,
)


class TestHardwareProfile:
    """Test HardwareProfile dataclass."""

    def test_creation(self) -> None:
        """Test creating a hardware profile."""
        profile = HardwareProfile(
            cpu_cores_physical=4,
            cpu_cores_logical=8,
            cpu_freq_mhz=2500.0,
            cpu_architecture="x86_64",
            ram_total_gb=16.0,
            ram_available_gb=12.0,
            swap_total_gb=8.0,
            gpu_available=True,
            gpu_name="NVIDIA GTX 1650",
            gpu_vram_gb=4.0,
            gpu_compute_capability="7.5",
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        assert profile.cpu_cores_physical == 4
        assert profile.cpu_cores_logical == 8
        assert profile.gpu_available is True
        assert profile.gpu_name == "NVIDIA GTX 1650"

    def test_to_dict(self) -> None:
        """Test converting profile to dictionary."""
        profile = HardwareProfile(
            cpu_cores_physical=4,
            cpu_cores_logical=8,
            cpu_freq_mhz=2500.0,
            cpu_architecture="x86_64",
            ram_total_gb=16.0,
            ram_available_gb=12.0,
            swap_total_gb=8.0,
            gpu_available=False,
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        data = profile.to_dict()
        assert isinstance(data, dict)
        assert data["cpu_cores_physical"] == 4
        assert data["gpu_available"] is False
        assert "detected_at" in data

    def test_to_json(self, tmp_path: Path) -> None:
        """Test JSON serialization."""
        profile = HardwareProfile(
            cpu_cores_physical=4,
            cpu_cores_logical=8,
            cpu_freq_mhz=2500.0,
            cpu_architecture="x86_64",
            ram_total_gb=16.0,
            ram_available_gb=12.0,
            swap_total_gb=8.0,
            gpu_available=False,
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        # Test JSON string
        json_str = profile.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["cpu_cores_physical"] == 4

        # Test JSON file
        filepath = tmp_path / "profile.json"
        profile.to_json(filepath)
        assert filepath.exists()

        # Load and verify
        loaded_profile = load_hardware_profile(filepath)
        assert loaded_profile.cpu_cores_physical == 4
        assert loaded_profile.gpu_available is False


class TestOptimizationConfig:
    """Test OptimizationConfig dataclass."""

    def test_creation(self) -> None:
        """Test creating optimization config."""
        config = OptimizationConfig(
            device="cuda",
            use_gpu=True,
            llm_batch_size=8,
            embedding_batch_size=64,
            max_tensor_size=5000,
            max_memory_mb=4096,
            cache_size_mb=512,
            num_workers=3,
            async_workers=8,
            use_quantization=False,
            quantization_bits=16,
            vector_db="chromadb",
            cache_backend="fakeredis",
            database="sqlite",
            cpu_governor="performance",
            enable_profiling=True,
        )

        assert config.device == "cuda"
        assert config.use_gpu is True
        assert config.llm_batch_size == 8
        assert config.vector_db == "chromadb"

    def test_to_json(self, tmp_path: Path) -> None:
        """Test JSON serialization."""
        config = OptimizationConfig(
            device="cpu",
            use_gpu=False,
            llm_batch_size=4,
            embedding_batch_size=32,
            max_tensor_size=2000,
            max_memory_mb=2048,
            cache_size_mb=256,
            num_workers=2,
            async_workers=4,
            use_quantization=True,
            quantization_bits=8,
            vector_db="chromadb",
            cache_backend="fakeredis",
            database="sqlite",
            cpu_governor="powersave",
            enable_profiling=True,
        )

        # Test JSON string
        json_str = config.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["device"] == "cpu"

        # Test JSON file
        filepath = tmp_path / "config.json"
        config.to_json(filepath)
        assert filepath.exists()

        # Load and verify
        loaded_config = load_optimization_config(filepath)
        assert loaded_config.device == "cpu"
        assert loaded_config.use_quantization is True


class TestHardwareDetector:
    """Test HardwareDetector class."""

    def test_detect_hardware_cpu_only(self) -> None:
        """Test hardware detection without GPU."""
        detector = HardwareDetector()

        # Just detect hardware (GPU status depends on actual system)
        profile = detector.detect_hardware()

        assert isinstance(profile, HardwareProfile)
        assert profile.cpu_cores_physical > 0
        assert profile.cpu_cores_logical >= profile.cpu_cores_physical
        assert profile.ram_total_gb > 0
        assert profile.ram_available_gb > 0
        assert profile.os_system in ["Linux", "Windows", "Darwin"]
        # GPU availability depends on actual system
        assert isinstance(profile.gpu_available, bool)

    def test_detect_hardware_with_gpu(self) -> None:
        """Test hardware detection - GPU test depends on system."""
        detector = HardwareDetector()
        profile = detector.detect_hardware()

        # Just verify the structure is correct
        assert isinstance(profile, HardwareProfile)
        assert isinstance(profile.gpu_available, bool)

        # If GPU is available, check optional fields are populated
        if profile.gpu_available:
            assert profile.gpu_name is not None
            assert profile.gpu_vram_gb is not None
            assert profile.gpu_vram_gb > 0
            assert profile.gpu_compute_capability is not None
        else:
            # On CPU-only systems, these should be None
            assert profile.gpu_name is None
            assert profile.gpu_vram_gb is None
            assert profile.gpu_compute_capability is None

    def test_generate_optimal_config_cpu(self) -> None:
        """Test config generation for CPU-only system."""
        # Create a low-spec CPU profile
        profile = HardwareProfile(
            cpu_cores_physical=2,
            cpu_cores_logical=4,
            cpu_freq_mhz=2000.0,
            cpu_architecture="x86_64",
            ram_total_gb=8.0,
            ram_available_gb=6.0,
            swap_total_gb=4.0,
            gpu_available=False,
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        detector = HardwareDetector()
        config = detector.generate_optimal_config(profile, prefer_local=True)

        assert config.device == "cpu"
        assert config.use_gpu is False
        assert config.llm_batch_size <= 4  # Small batch for limited RAM
        assert config.vector_db == "chromadb"  # Local-first
        assert config.cache_backend == "fakeredis"  # Local-first
        assert config.database == "sqlite"  # Local-first
        assert config.num_workers == 1  # 2 cores - 1 for system

    def test_generate_optimal_config_gpu(self) -> None:
        """Test config generation for GPU system."""
        # Create a GPU profile (GTX 1650 specs)
        profile = HardwareProfile(
            cpu_cores_physical=4,
            cpu_cores_logical=8,
            cpu_freq_mhz=2500.0,
            cpu_architecture="x86_64",
            ram_total_gb=24.0,
            ram_available_gb=20.0,
            swap_total_gb=24.0,
            gpu_available=True,
            gpu_name="NVIDIA GTX 1650",
            gpu_vram_gb=4.0,
            gpu_compute_capability="7.5",
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        detector = HardwareDetector()
        config = detector.generate_optimal_config(profile, prefer_local=True)

        assert config.device == "cuda"
        assert config.use_gpu is True
        assert config.llm_batch_size == 8  # 4GB VRAM
        assert config.embedding_batch_size == 64
        assert config.max_tensor_size == 5000
        assert config.vector_db == "chromadb"

    def test_generate_optimal_config_high_end_gpu(self) -> None:
        """Test config generation for high-end GPU."""
        profile = HardwareProfile(
            cpu_cores_physical=8,
            cpu_cores_logical=16,
            cpu_freq_mhz=3600.0,
            cpu_architecture="x86_64",
            ram_total_gb=64.0,
            ram_available_gb=60.0,
            swap_total_gb=32.0,
            gpu_available=True,
            gpu_name="NVIDIA RTX 4090",
            gpu_vram_gb=24.0,
            gpu_compute_capability="8.9",
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        detector = HardwareDetector()
        config = detector.generate_optimal_config(profile)

        assert config.device == "cuda"
        assert config.llm_batch_size == 32  # Large batch for 24GB VRAM
        assert config.embedding_batch_size == 256
        assert config.max_tensor_size == 20000

    def test_save_config(self, tmp_path: Path) -> None:
        """Test saving config to files."""
        detector = HardwareDetector()
        detector.detect_hardware()
        detector.generate_optimal_config()

        profile_path, config_path = detector.save_config(
            config_dir=tmp_path,
            profile_filename="test_profile.json",
            config_filename="test_config.json",
        )

        assert profile_path.exists()
        assert config_path.exists()

        # Verify can load
        loaded_profile = load_hardware_profile(profile_path)
        loaded_config = load_optimization_config(config_path)

        assert loaded_profile.cpu_cores_physical > 0
        assert loaded_config.device in ["cpu", "cuda"]

    def test_detect_and_configure(self, tmp_path: Path) -> None:
        """Test convenience method."""
        detector = HardwareDetector()

        # Don't save to avoid conflicts
        profile, config = detector.detect_and_configure(save=False)

        assert isinstance(profile, HardwareProfile)
        assert isinstance(config, OptimizationConfig)
        assert profile.cpu_cores_physical > 0
        assert config.device in ["cpu", "cuda"]


class TestAutoConfigureFunction:
    """Test auto_configure convenience function."""

    def test_auto_configure(self) -> None:
        """Test auto_configure function."""
        # Don't save to avoid conflicts
        profile, config = auto_configure(save=False, prefer_local=True)

        assert isinstance(profile, HardwareProfile)
        assert isinstance(config, OptimizationConfig)
        assert config.vector_db == "chromadb"
        assert config.cache_backend == "fakeredis"
        assert config.database == "sqlite"


class TestQuantizationConfig:
    """Test quantization configuration."""

    def test_quantization_low_ram(self) -> None:
        """Test quantization is enabled on low RAM systems."""
        profile = HardwareProfile(
            cpu_cores_physical=2,
            cpu_cores_logical=4,
            cpu_freq_mhz=2000.0,
            cpu_architecture="x86_64",
            ram_total_gb=4.0,  # Low RAM
            ram_available_gb=3.0,
            swap_total_gb=2.0,
            gpu_available=False,
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        detector = HardwareDetector()
        config = detector.generate_optimal_config(profile)

        assert config.use_quantization is True
        assert config.quantization_bits == 8

    def test_no_quantization_high_ram(self) -> None:
        """Test quantization is disabled on high RAM systems."""
        profile = HardwareProfile(
            cpu_cores_physical=4,
            cpu_cores_logical=8,
            cpu_freq_mhz=2500.0,
            cpu_architecture="x86_64",
            ram_total_gb=32.0,  # High RAM
            ram_available_gb=28.0,
            swap_total_gb=16.0,
            gpu_available=False,
            os_system="Linux",
            os_release="6.16.8",
            machine_type="x86_64",
        )

        detector = HardwareDetector()
        config = detector.generate_optimal_config(profile)

        assert config.use_quantization is False
        assert config.quantization_bits == 16
