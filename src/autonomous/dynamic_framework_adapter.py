"""Dynamic Framework Adapter - Phase 26C

Adapts framework to specific machine environment.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

import logging
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import psutil

try:
    import torch
except ImportError:
    torch = None  # type: ignore[assignment, unused-ignore]

logger = logging.getLogger(__name__)


@dataclass
class MachineSpecs:
    """Machine specifications"""

    cpu_count: int
    memory_gb: float
    gpu_count: int
    gpu_memory_gb: float | None
    platform: str
    python_version: str
    network_bandwidth_mbps: float | None = None  # Can be measured


class DynamicFrameworkAdapter:
    """Adapta o framework ao ambiente específico da máquina"""

    def __init__(self, config_path: Path | None = None):
        """Initialize framework adapter

        Args:
            config_path: Path to framework config (default: config/omnimind.yaml)
        """
        if config_path is None:
            base_dir = Path(__file__).resolve().parents[2]
            config_path = base_dir / "config" / "omnimind.yaml"

        self.config_path = Path(config_path)
        self.machine_config = self.detect_machine_specs()
        self.current_framework = self._load_current_framework()

        logger.info(
            f"DynamicFrameworkAdapter initialized for machine: {self.machine_config.platform}"
        )

    def detect_machine_specs(self) -> MachineSpecs:
        """Detect machine specifications

        Returns:
            MachineSpecs object
        """
        cpu_count = psutil.cpu_count()
        if cpu_count is None:
            cpu_count = 1  # Default to 1 if detection fails

        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)

        gpu_count = 0
        gpu_memory_gb = None

        if torch and torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            if gpu_count > 0:
                gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)

        return MachineSpecs(
            cpu_count=cpu_count,
            memory_gb=memory_gb,
            gpu_count=gpu_count,
            gpu_memory_gb=gpu_memory_gb,
            platform=platform.system(),
            python_version=platform.python_version(),
        )

    def _load_current_framework(self) -> Dict[str, Any]:
        """Load current framework configuration

        Returns:
            Framework config dict
        """
        # Load from config file or return defaults
        defaults = {
            "model_size": "medium",
            "batch_size": 32,
            "use_gpu": True if self.machine_config.gpu_count > 0 else False,
            "cache_enabled": True,
            "distributed": False,
        }

        if self.config_path.exists():
            try:
                import yaml

                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f)
                    return {**defaults, **config}
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
                return defaults

        return defaults

    def adapt_to_environment(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt solution to specific machine environment

        Args:
            solution: Solution dictionary from SolutionLookupEngine

        Returns:
            Adapted solution dict
        """
        specs = self.machine_config
        logger.info(
            f"[ADAPT] Machine specs: {specs.platform}, "
            f"{specs.memory_gb:.1f}GB RAM, {specs.gpu_count} GPUs"
        )

        # Start with solution
        adapted = (
            solution.get("solution", {}).copy()
            if isinstance(solution.get("solution"), dict)
            else {}
        )

        # Adapt based on machine specs
        # Se máquina tem apenas 4GB RAM
        if specs.memory_gb < 8:
            adapted["model_size"] = "small"
            adapted["batch_size"] = 4
            adapted["cache_enabled"] = False
            logger.info(
                "[ADAPT] Low memory detected: using small model, batch_size=4, cache disabled"
            )

        # Se máquina tem 2+ GPUs
        if specs.gpu_count >= 2:
            adapted["parallel_strategy"] = "multi_gpu"
            adapted["distributed"] = True
            adapted["batch_size"] = adapted.get("batch_size", 32) * specs.gpu_count
            batch_size = adapted.get("batch_size")
            logger.info(
                f"[ADAPT] Multi-GPU detected: enabling distributed, batch_size={batch_size}"
            )

        # Se máquina tem apenas CPU
        if specs.gpu_count == 0:
            adapted["use_gpu"] = False
            adapted["use_cpu_optimization"] = True
            adapted["batch_size"] = min(adapted.get("batch_size", 32), 4)
            logger.info(
                "[ADAPT] CPU-only detected: disabling GPU, using CPU optimization, batch_size=4"
            )

        # Se tem internet lenta (simulado - pode ser medido)
        if specs.network_bandwidth_mbps and specs.network_bandwidth_mbps < 10:
            adapted["cache_locally"] = True
            adapted["prefetch_data"] = True
            logger.info("[ADAPT] Slow network detected: enabling local cache and prefetch")

        return adapted

    def apply_adaptation(self, adapted_solution: Dict[str, Any]) -> Dict[str, Any]:
        """Apply adaptation to framework

        Args:
            adapted_solution: Adapted solution dict

        Returns:
            New framework config
        """
        logger.info("[ADAPT] Aplicando adaptação...")
        logger.info(f"   Model size: {adapted_solution.get('model_size', 'default')}")
        logger.info(f"   Batch size: {adapted_solution.get('batch_size', 'default')}")
        logger.info(f"   Distributed: {adapted_solution.get('distributed', False)}")

        # Merge with current framework
        new_config = {
            **self.current_framework,
            **adapted_solution,
        }

        # Save new config (optional - can be in-memory only)
        self.current_framework = new_config

        return new_config
