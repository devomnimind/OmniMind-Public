"""
Centralized CUDA Diagnostics for OmniMind.

This module is the SINGLE SOURCE OF TRUTH for GPU availability.
It does NOT attempt to configure the environment (which is the shell script's job).
It only reports what PyTorch sees.
"""

import logging
import os

import torch

logger = logging.getLogger(__name__)


def check_cuda() -> dict:
    """
    Diagnostic check for CUDA availability.
    Returns a dictionary with detailed status.
    """
    try:
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count()
        current_device = torch.cuda.current_device() if cuda_available else None
        device_name = torch.cuda.get_device_name(0) if cuda_available else None

        # Check environment variables (read-only)
        env_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "Not Set")
        env_home = os.environ.get("CUDA_HOME", "Not Set")

        status = {
            "available": cuda_available,
            "device_count": device_count,
            "current_device": current_device,
            "device_name": device_name,
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "env_visible_devices": env_visible,
            "env_cuda_home": env_home,
        }

        if cuda_available:
            logger.info(f"✅ CUDA Active: {device_name} (Count: {device_count})")
        else:
            logger.warning(f"⚠️ CUDA Unavailable. Device count: {device_count}")
            if device_count > 0:
                logger.error(
                    "❌ Mismatch detected: Devices found but CUDA not available. "
                    "Check LD_LIBRARY_PATH."
                )

        return status

    except Exception as e:
        logger.critical(f"🔥 Critical CUDA Check Failure: {e}")
        return {"error": str(e), "available": False}


if __name__ == "__main__":
    # Self-test when run directly
    logging.basicConfig(level=logging.INFO)
    print("--- CUDA DIAGNOSTICS ---")
    report = check_cuda()
    import json

    print(json.dumps(report, indent=2))
