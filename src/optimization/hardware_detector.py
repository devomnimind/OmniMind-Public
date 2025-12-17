"""
Hardware Detection and Auto-Configuration Module

This module automatically detects available hardware (CPU, GPU, RAM) and
configures OmniMind for optimal performance on the current machine.

Implements the auto-optimization strategy from:
docs/autootimizacao-hardware-omnidev.md

Features:
- Hardware capability detection
- Automatic CPU vs GPU selection
- Adaptive batch sizing based on available RAM
- Performance profiling and optimization
- Local-first service configuration
"""

import json
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional

import psutil

if TYPE_CHECKING:
    from psutil import sensors_battery as _typed_sensors_battery
else:

    def _typed_sensors_battery() -> Any:
        return psutil.sensors_battery()


from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class HardwareProfile:
    """Hardware profile with detected capabilities."""

    # CPU
    cpu_cores_physical: int
    cpu_cores_logical: int
    cpu_freq_mhz: float
    cpu_architecture: str

    # Memory
    ram_total_gb: float
    ram_available_gb: float
    swap_total_gb: float

    # GPU (optional)
    gpu_available: bool

    # System
    os_system: str
    os_release: str
    machine_type: str

    # GPU optional fields (must come after required fields)
    gpu_name: Optional[str] = None
    gpu_vram_gb: Optional[float] = None
    gpu_compute_capability: Optional[str] = None

    # Timestamp
    detected_at: str = ""

    def __post_init__(self) -> None:
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, filepath: Optional[Path] = None) -> str:
        """Export to JSON string or file."""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2)

        if filepath:
            filepath.write_text(json_str)

        return json_str


@dataclass
class OptimizationConfig:
    """Configuration optimized for detected hardware."""

    # Execution mode
    device: Literal["cpu", "cuda"]
    use_gpu: bool

    # Batch sizes (adaptive based on RAM)
    llm_batch_size: int
    embedding_batch_size: int
    max_tensor_size: int

    # Memory limits
    max_memory_mb: int
    cache_size_mb: int

    # Threading
    num_workers: int
    async_workers: int

    # Model quantization (for limited RAM)
    use_quantization: bool
    quantization_bits: int

    # Services (local-first)
    vector_db: Literal["chromadb", "qdrant"]
    cache_backend: Literal["fakeredis", "redis"]
    database: Literal["sqlite", "postgresql"]

    # Performance tuning
    cpu_governor: str  # "performance", "powersave", "ondemand"
    enable_profiling: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, filepath: Optional[Path] = None) -> str:
        """Export to JSON string or file."""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2)

        if filepath:
            filepath.write_text(json_str)

        return json_str


class HardwareDetector:
    """Detects hardware capabilities and generates optimized configuration."""

    def __init__(self) -> None:
        self.profile: Optional[HardwareProfile] = None
        self.config: Optional[OptimizationConfig] = None

    def detect_hardware(self) -> HardwareProfile:
        """
        Detect all available hardware capabilities.

        Returns:
            HardwareProfile with detected specs
        """
        # CPU information
        cpu_info = psutil.cpu_freq()
        cpu_cores_physical = psutil.cpu_count(logical=False) or 1
        cpu_cores_logical = psutil.cpu_count(logical=True) or 1

        # Memory information (convert bytes to GB)
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        ram_total_gb = mem.total / (1024**3)
        ram_available_gb = mem.available / (1024**3)
        swap_total_gb = swap.total / (1024**3)

        # System information
        os_system = platform.system()
        os_release = platform.release()
        machine_type = platform.machine()
        cpu_arch = platform.machine()

        # GPU detection (try PyTorch first)
        gpu_available = False
        gpu_name = None
        gpu_vram_gb = None
        gpu_compute_capability = None

        try:
            import torch

            if torch.cuda.is_available():
                gpu_available = True
                gpu_name = torch.cuda.get_device_name(0)

                # Get VRAM (convert bytes to GB)
                gpu_props = torch.cuda.get_device_properties(0)
                gpu_vram_gb = gpu_props.total_memory / (1024**3)

                # Compute capability (e.g., "7.5" for GTX 1650)
                gpu_compute_capability = f"{gpu_props.major}.{gpu_props.minor}"
        except (ImportError, RuntimeError):
            # PyTorch not available or CUDA error
            pass

        # Create profile
        profile = HardwareProfile(
            cpu_cores_physical=cpu_cores_physical,
            cpu_cores_logical=cpu_cores_logical,
            cpu_freq_mhz=cpu_info.current if cpu_info else 0.0,
            cpu_architecture=cpu_arch,
            ram_total_gb=ram_total_gb,
            ram_available_gb=ram_available_gb,
            swap_total_gb=swap_total_gb,
            gpu_available=gpu_available,
            gpu_name=gpu_name,
            gpu_vram_gb=gpu_vram_gb,
            gpu_compute_capability=gpu_compute_capability,
            os_system=os_system,
            os_release=os_release,
            machine_type=machine_type,
        )

        self.profile = profile
        return profile

    def generate_optimal_config(
        self,
        profile: Optional[HardwareProfile] = None,
        prefer_local: bool = True,
    ) -> OptimizationConfig:
        """
        Generate optimal configuration based on hardware profile.

        Args:
            profile: Hardware profile (auto-detect if None)
            prefer_local: Prefer local services over remote (default: True)

        Returns:
            OptimizationConfig optimized for hardware
        """
        if profile is None:
            if self.profile is None:
                self.detect_hardware()
            profile = self.profile

        assert profile is not None

        # Determine device
        device: Literal["cpu", "cuda"]
        if profile.gpu_available:
            device = "cuda"
            use_gpu = True
        else:
            device = "cpu"
            use_gpu = False

        # Calculate batch sizes based on available RAM
        # Conservative estimates to avoid OOM
        ram_available_gb = profile.ram_available_gb

        if use_gpu and profile.gpu_vram_gb:
            # GPU available - batch sizes limited by VRAM
            vram_gb = profile.gpu_vram_gb

            if vram_gb <= 4.0:  # GTX 1650 class
                llm_batch_size = 8
                embedding_batch_size = 64
                max_tensor_size = 5000
            elif vram_gb <= 8.0:  # RTX 3060 class
                llm_batch_size = 16
                embedding_batch_size = 128
                max_tensor_size = 10000
            else:  # High-end GPU
                llm_batch_size = 32
                embedding_batch_size = 256
                max_tensor_size = 20000
        else:
            # CPU-only - batch sizes based on RAM
            if ram_available_gb < 4.0:
                llm_batch_size = 1
                embedding_batch_size = 16
                max_tensor_size = 1000
            elif ram_available_gb < 8.0:
                llm_batch_size = 2
                embedding_batch_size = 32
                max_tensor_size = 2000
            elif ram_available_gb < 16.0:
                llm_batch_size = 4
                embedding_batch_size = 64
                max_tensor_size = 5000
            else:
                llm_batch_size = 8
                embedding_batch_size = 128
                max_tensor_size = 10000

        # Memory limits (use 50% of available RAM for safety)
        max_memory_mb = int(ram_available_gb * 512)  # MB
        cache_size_mb = min(1024, int(ram_available_gb * 128))  # MB

        # Threading (leave 1 core for system)
        num_workers = max(1, profile.cpu_cores_physical - 1)
        async_workers = profile.cpu_cores_logical

        # Quantization (use on low RAM systems)
        use_quantization = ram_available_gb < 8.0
        quantization_bits = 8 if use_quantization else 16

        # Services (local-first by default)
        vector_db: Literal["chromadb", "qdrant"]
        cache_backend: Literal["fakeredis", "redis"]
        database: Literal["sqlite", "postgresql"]
        if prefer_local:
            vector_db = "chromadb"  # Local, no server needed
            cache_backend = "fakeredis"  # In-memory, no Redis server
            database = "sqlite"  # File-based, no server needed
        else:
            vector_db = "qdrant"
            cache_backend = "redis"
            database = "postgresql"

        # CPU governor (performance for servers, powersave for laptops)
        # Detect if on battery (laptop) or AC power
        try:
            battery = _typed_sensors_battery()  # type: ignore[no-untyped-call]
            if battery and not battery.power_plugged:
                cpu_governor = "powersave"
            else:
                cpu_governor = "performance"
        except (AttributeError, RuntimeError):
            # No battery info available (desktop/server)
            cpu_governor = "performance"

        # Enable profiling for development
        enable_profiling = True

        config = OptimizationConfig(
            device=device,
            use_gpu=use_gpu,
            llm_batch_size=llm_batch_size,
            embedding_batch_size=embedding_batch_size,
            max_tensor_size=max_tensor_size,
            max_memory_mb=max_memory_mb,
            cache_size_mb=cache_size_mb,
            num_workers=num_workers,
            async_workers=async_workers,
            use_quantization=use_quantization,
            quantization_bits=quantization_bits,
            vector_db=vector_db,
            cache_backend=cache_backend,
            database=database,
            cpu_governor=cpu_governor,
            enable_profiling=enable_profiling,
        )

        self.config = config
        return config

    def save_config(
        self,
        config_dir: Path = Path("config"),
        profile_filename: str = "hardware_profile.json",
        config_filename: str = "optimization_config.json",
    ) -> tuple[Path, Path]:
        """
        Save detected profile and config to JSON files.

        Args:
            config_dir: Directory to save configs
            profile_filename: Filename for hardware profile
            config_filename: Filename for optimization config

        Returns:
            Tuple of (profile_path, config_path)
        """
        config_dir.mkdir(parents=True, exist_ok=True)

        profile_path = config_dir / profile_filename
        config_path = config_dir / config_filename

        if self.profile:
            self.profile.to_json(profile_path)

        if self.config:
            self.config.to_json(config_path)

        return profile_path, config_path

    def detect_and_configure(
        self,
        save: bool = True,
        prefer_local: bool = True,
    ) -> tuple[HardwareProfile, OptimizationConfig]:
        """
        Convenience method: detect hardware and generate config.

        Args:
            save: Save config files to disk
            prefer_local: Prefer local services

        Returns:
            Tuple of (profile, config)
        """
        profile = self.detect_hardware()
        config = self.generate_optimal_config(profile, prefer_local)

        if save:
            self.save_config()

        return profile, config


def load_hardware_profile(filepath: Path) -> HardwareProfile:
    """Load hardware profile from JSON file."""
    data = json.loads(filepath.read_text())
    return HardwareProfile(**data)


def load_optimization_config(filepath: Path) -> OptimizationConfig:
    """Load optimization config from JSON file."""
    data = json.loads(filepath.read_text())
    return OptimizationConfig(**data)


# Convenience functions for quick usage
def auto_configure(
    save: bool = True,
    prefer_local: bool = True,
) -> tuple[HardwareProfile, OptimizationConfig]:
    """
    Auto-detect hardware and generate optimal configuration.

    Usage:
        profile, config = auto_configure()
        print(f"Device: {config.device}")
        print(f"Batch size: {config.llm_batch_size}")
    """
    detector = HardwareDetector()
    return detector.detect_and_configure(save=save, prefer_local=prefer_local)


if __name__ == "__main__":
    # Demo usage
    print("🔍 Detecting hardware capabilities...")
    profile, config = auto_configure(save=True)

    print("\n📊 Hardware Profile:")
    cpu_info = (
        f"  CPU: {profile.cpu_cores_physical}c/"
        f"{profile.cpu_cores_logical}t @ {profile.cpu_freq_mhz:.0f} MHz"
    )
    print(cpu_info)
    ram_info = (
        f"  RAM: {profile.ram_available_gb:.1f} GB available / "
        f"{profile.ram_total_gb:.1f} GB total"
    )
    print(ram_info)

    if profile.gpu_available:
        print(f"  GPU: {profile.gpu_name} ({profile.gpu_vram_gb:.1f} GB VRAM)")
        print(f"  Compute Capability: {profile.gpu_compute_capability}")
    else:
        print("  GPU: Not available (CPU mode)")

    print("\n⚙️  Optimization Config:")
    print(f"  Device: {config.device}")
    print(f"  LLM Batch Size: {config.llm_batch_size}")
    print(f"  Embedding Batch Size: {config.embedding_batch_size}")
    print(f"  Max Tensor Size: {config.max_tensor_size}")
    print(f"  Workers: {config.num_workers}")
    print(f"  Vector DB: {config.vector_db}")
    print(f"  Cache: {config.cache_backend}")
    print(f"  Database: {config.database}")
    print(f"  Quantization: {config.use_quantization} ({config.quantization_bits}-bit)")

    print("\n✅ Configuration saved to config/")
