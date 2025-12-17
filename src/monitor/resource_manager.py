"""
OmniMind Hybrid Resource Manager
================================

Intelligent allocation system that dynamically distributes tasks between CPU and GPU
based on real-time system load, preventing bottlenecks and optimizing throughput.

Features:
- Real-time monitoring of CPU/GPU/RAM/VRAM
- Dynamic task routing (Tensor vs Numpy)
- Swap usage management
- Singleton pattern for global state management
"""

import logging
from typing import Dict, Literal

import psutil
import torch

logger = logging.getLogger(__name__)


class HybridResourceManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HybridResourceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.gpu_available = torch.cuda.is_available()
        self.device_count = torch.cuda.device_count() if self.gpu_available else 0
        self.gpu_name = torch.cuda.get_device_name(0) if self.gpu_available else "None"

        # Thresholds (Configurable)
        self.cpu_high_threshold = 80.0  # %
        self.gpu_high_threshold = 90.0  # %
        self.ram_high_threshold = 85.0  # %
        self.vram_high_threshold = 90.0  # %

        self._initialized = True
        logger.info(f"HybridResourceManager initialized. GPU: {self.gpu_name}")

    def get_system_status(self) -> Dict[str, float]:
        """Collects real-time system metrics."""
        # CORREÇÃO (2025-12-09): interval=None retorna 0.0% na primeira chamada
        # Usar interval=0.1 para leitura imediata precisa
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        swap = psutil.swap_memory()
        swap_percent = swap.percent

        gpu_util = 0.0
        vram_percent = 0.0

        if self.gpu_available:
            try:
                # Note: torch.cuda.utilization() is not standard, using memory as proxy
                # or relying on external nvidia-smi calls if needed.
                # Here we use memory allocation as a proxy for "load" within the app context
                total_mem = torch.cuda.get_device_properties(0).total_memory
                allocated = torch.cuda.memory_allocated(0)
                vram_percent = (allocated / total_mem) * 100

                # For compute utilization, we'd need pynvml, but let's stick to standard libs
                # Assuming if VRAM is high, GPU is busy.
            except Exception:
                pass

        return {
            "cpu": cpu_percent,
            "ram": ram_percent,
            "swap": swap_percent,
            "gpu_util": gpu_util,  # Placeholder without pynvml
            "vram": vram_percent,
        }

    def allocate_task(self, task_type: str, estimated_size_mb: float) -> Literal["cuda", "cpu"]:
        """
        Decides where to allocate a task based on current load.

        Args:
            task_type: 'math', 'io', 'quantum'
            estimated_size_mb: Estimated memory footprint

        Returns:
            'cuda' or 'cpu'
        """
        if not self.gpu_available:
            return "cpu"

        stats = self.get_system_status()

        # Critical: If VRAM is full, force CPU (or Swap via OS)
        if stats["vram"] > self.vram_high_threshold:
            logger.warning(
                f"VRAM Critical ({stats['vram']:.1f}%), forcing CPU fallback for {task_type}"
            )
            return "cpu"

        # If CPU is choking and GPU has space, offload everything possible
        if stats["cpu"] > self.cpu_high_threshold and stats["vram"] < 70.0:
            return "cuda"

        # Default behavior based on task type
        if task_type in ["math", "quantum", "tensor"]:
            return "cuda"

        return "cpu"

    def suggest_memory_format(self, device: str) -> str:
        """Suggests optimal memory format (pinned, pageable) based on device."""
        if device == "cuda":
            return "pinned"  # Suggest using pin_memory=True in DataLoaders
        return "default"

    def optimize_tensor(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Automatically moves tensor to optimal device.
        """
        target_device = self.allocate_task(
            "tensor", tensor.element_size() * tensor.nelement() / 1024 / 1024
        )
        if target_device == "cuda" and tensor.device.type != "cuda":
            return tensor.to("cuda", non_blocking=True)
        elif target_device == "cpu" and tensor.device.type != "cpu":
            return tensor.cpu()
        return tensor


# Global instance
resource_manager = HybridResourceManager()
