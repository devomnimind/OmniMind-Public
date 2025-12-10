"""
Phase 1: Hardware & Environment Check.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HardwareProfile:
    gpu_available: bool
    gpu_name: str
    memory_total: int
    cpu_count: int
    tpu_available: bool = False


def check_hardware() -> HardwareProfile:
    """Checks available hardware resources."""
    logger.info("Phase 1: Checking Hardware...")

    gpu_available = False
    gpu_name = "None"

    # Check for CUDA/Torch
    try:
        import torch

        if torch.cuda.is_available():
            gpu_available = True
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"GPU Detected: {gpu_name}")
    except ImportError:
        logger.warning("Torch not installed, skipping GPU check.")

    # Check System Resources
    import psutil

    mem = psutil.virtual_memory()
    cpu_count = psutil.cpu_count() or 1

    profile = HardwareProfile(
        gpu_available=gpu_available,
        gpu_name=gpu_name,
        memory_total=mem.total,
        cpu_count=cpu_count,
    )

    logger.info(f"Hardware Profile: {profile}")
    return profile
