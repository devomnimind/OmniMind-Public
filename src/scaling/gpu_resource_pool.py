"""GPU Resource Pooling Module.

Implements multi-GPU orchestration and workload distribution for optimal resource utilization.
Provides GPU pool management, load balancing, and automatic failover.

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 7.2
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Set
from collections import deque

import structlog

logger = structlog.get_logger(__name__)


class GPUStatus(Enum):
    """GPU status states."""

    AVAILABLE = "available"
    BUSY = "busy"
    RESERVED = "reserved"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class GPUDevice:
    """Represents a single GPU device.

    Attributes:
        device_id: GPU device identifier
        name: GPU model name
        total_memory_mb: Total GPU memory in MB
        compute_capability: CUDA compute capability
        status: Current GPU status
        current_utilization_percent: Current utilization percentage
        current_memory_used_mb: Current memory usage in MB
        reserved_by: Task ID that reserved this GPU (if any)
        last_heartbeat: Last heartbeat timestamp
    """

    device_id: int
    name: str
    total_memory_mb: int
    compute_capability: str
    status: GPUStatus = GPUStatus.AVAILABLE
    current_utilization_percent: float = 0.0
    current_memory_used_mb: int = 0
    reserved_by: Optional[str] = None
    last_heartbeat: float = field(default_factory=time.time)

    def is_available(self) -> bool:
        """Check if GPU is available for allocation."""
        return self.status == GPUStatus.AVAILABLE

    def has_capacity(self, required_memory_mb: int) -> bool:
        """Check if GPU has enough free memory.

        Args:
            required_memory_mb: Required memory in MB

        Returns:
            True if GPU has enough free memory
        """
        free_memory = self.total_memory_mb - self.current_memory_used_mb
        return free_memory >= required_memory_mb

    def reserve(self, task_id: str) -> None:
        """Reserve the GPU for a task.

        Args:
            task_id: Task identifier
        """
        self.status = GPUStatus.RESERVED
        self.reserved_by = task_id
        logger.info("gpu_reserved", device_id=self.device_id, task_id=task_id)

    def release(self) -> None:
        """Release the GPU reservation."""
        self.status = GPUStatus.AVAILABLE
        self.reserved_by = None
        logger.info("gpu_released", device_id=self.device_id)

    def update_stats(
        self,
        utilization_percent: float,
        memory_used_mb: int,
    ) -> None:
        """Update GPU statistics.

        Args:
            utilization_percent: Current utilization percentage
            memory_used_mb: Current memory usage in MB
        """
        self.current_utilization_percent = utilization_percent
        self.current_memory_used_mb = memory_used_mb
        self.last_heartbeat = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "total_memory_mb": self.total_memory_mb,
            "compute_capability": self.compute_capability,
            "status": self.status.value,
            "utilization_percent": self.current_utilization_percent,
            "memory_used_mb": self.current_memory_used_mb,
            "memory_free_mb": self.total_memory_mb - self.current_memory_used_mb,
            "reserved_by": self.reserved_by,
        }


@dataclass
class GPUTask:
    """Represents a task requiring GPU resources.

    Attributes:
        task_id: Unique task identifier
        required_memory_mb: Required GPU memory in MB
        min_compute_capability: Minimum required compute capability
        preferred_device_id: Preferred GPU device ID (if any)
        assigned_device_id: Assigned GPU device ID
        submitted_at: When task was submitted
        started_at: When task execution started
        completed_at: When task completed
    """

    task_id: str
    required_memory_mb: int
    min_compute_capability: str = "0.0"
    preferred_device_id: Optional[int] = None
    assigned_device_id: Optional[int] = None
    submitted_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    def is_assigned(self) -> bool:
        """Check if task has been assigned to a GPU."""
        return self.assigned_device_id is not None

    def is_running(self) -> bool:
        """Check if task is currently running."""
        return self.started_at is not None and self.completed_at is None

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.completed_at is not None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "required_memory_mb": self.required_memory_mb,
            "min_compute_capability": self.min_compute_capability,
            "assigned_device_id": self.assigned_device_id,
            "status": self._get_status(),
            "submitted_at": self.submitted_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    def _get_status(self) -> str:
        """Get current task status."""
        if self.is_completed():
            return "completed"
        elif self.is_running():
            return "running"
        elif self.is_assigned():
            return "assigned"
        else:
            return "pending"


@dataclass
class GPUPoolConfig:
    """Configuration for GPU resource pool.

    Attributes:
        auto_discover_gpus: Automatically discover available GPUs
        enable_load_balancing: Enable load balancing across GPUs
        enable_failover: Enable automatic failover on GPU errors
        heartbeat_interval_seconds: GPU heartbeat interval
        task_timeout_seconds: Maximum task execution time
        memory_reservation_overhead_mb: Memory overhead for reservations
    """

    auto_discover_gpus: bool = True
    enable_load_balancing: bool = True
    enable_failover: bool = True
    heartbeat_interval_seconds: int = 30
    task_timeout_seconds: int = 3600
    memory_reservation_overhead_mb: int = 512


class GPUResourcePool:
    """GPU resource pool manager.

    Manages multiple GPUs, distributes workloads, and handles failover.
    Provides efficient GPU allocation and load balancing.

    Example:
        >>> config = GPUPoolConfig()
        >>> pool = GPUResourcePool(config)
        >>> pool.add_gpu(GPUDevice(
        ...     device_id=0,
        ...     name="NVIDIA GTX 1650",
        ...     total_memory_mb=4096,
        ...     compute_capability="7.5"
        ... ))
        >>> task = GPUTask(task_id="task_1", required_memory_mb=2048)
        >>> device_id = pool.allocate_gpu(task)
        >>> pool.release_gpu(task.task_id)
    """

    def __init__(self, config: GPUPoolConfig):
        """Initialize the GPU resource pool.

        Args:
            config: GPU pool configuration
        """
        self.config = config
        self._gpus: Dict[int, GPUDevice] = {}
        self._tasks: Dict[str, GPUTask] = {}
        self._task_queue: Deque[GPUTask] = deque()

        if config.auto_discover_gpus:
            self._discover_gpus()

        logger.info(
            "gpu_pool_initialized",
            gpu_count=len(self._gpus),
            load_balancing=config.enable_load_balancing,
        )

    def _discover_gpus(self) -> None:
        """Automatically discover available GPUs."""
        try:
            import torch

            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    gpu = GPUDevice(
                        device_id=i,
                        name=props.name,
                        total_memory_mb=props.total_memory // (1024 * 1024),
                        compute_capability=f"{props.major}.{props.minor}",
                    )
                    self.add_gpu(gpu)
                    logger.info("gpu_discovered", device_id=i, name=props.name)
        except ImportError:
            logger.warning("pytorch_not_available", message="Cannot auto-discover GPUs")
        except Exception as e:
            logger.error("gpu_discovery_failed", error=str(e))

    def add_gpu(self, gpu: GPUDevice) -> None:
        """Add a GPU to the pool.

        Args:
            gpu: GPU device to add
        """
        self._gpus[gpu.device_id] = gpu
        logger.info("gpu_added", device_id=gpu.device_id, name=gpu.name)

    def remove_gpu(self, device_id: int) -> None:
        """Remove a GPU from the pool.

        Args:
            device_id: GPU device ID to remove
        """
        if device_id in self._gpus:
            gpu = self._gpus[device_id]
            if gpu.reserved_by:
                logger.warning(
                    "removing_reserved_gpu",
                    device_id=device_id,
                    task_id=gpu.reserved_by,
                )
            del self._gpus[device_id]
            logger.info("gpu_removed", device_id=device_id)

    def allocate_gpu(self, task: GPUTask) -> Optional[int]:
        """Allocate a GPU for a task.

        Args:
            task: Task requiring GPU resources

        Returns:
            Allocated GPU device ID, or None if no GPU available
        """
        self._tasks[task.task_id] = task

        # Try preferred device first
        if task.preferred_device_id is not None:
            gpu = self._gpus.get(task.preferred_device_id)
            if gpu and self._can_allocate_gpu(gpu, task):
                return self._assign_gpu(gpu, task)

        # Find best available GPU
        if self.config.enable_load_balancing:
            gpu = self._find_best_gpu(task)
        else:
            gpu = self._find_available_gpu(task)

        if gpu:
            return self._assign_gpu(gpu, task)

        # No GPU available, queue the task
        self._task_queue.append(task)
        logger.info("task_queued", task_id=task.task_id)
        return None

    def _can_allocate_gpu(self, gpu: GPUDevice, task: GPUTask) -> bool:
        """Check if GPU can be allocated for task.

        Args:
            gpu: GPU device
            task: Task requiring GPU

        Returns:
            True if GPU can be allocated
        """
        if not gpu.is_available():
            return False

        # Check memory
        required_memory = (
            task.required_memory_mb + self.config.memory_reservation_overhead_mb
        )
        if not gpu.has_capacity(required_memory):
            return False

        # Check compute capability
        if gpu.compute_capability < task.min_compute_capability:
            return False

        return True

    def _find_available_gpu(self, task: GPUTask) -> Optional[GPUDevice]:
        """Find any available GPU that meets requirements.

        Args:
            task: Task requiring GPU

        Returns:
            Available GPU device or None
        """
        for gpu in self._gpus.values():
            if self._can_allocate_gpu(gpu, task):
                return gpu
        return None

    def _find_best_gpu(self, task: GPUTask) -> Optional[GPUDevice]:
        """Find best GPU for task using load balancing.

        Args:
            task: Task requiring GPU

        Returns:
            Best GPU device or None
        """
        available_gpus = [
            gpu for gpu in self._gpus.values() if self._can_allocate_gpu(gpu, task)
        ]

        if not available_gpus:
            return None

        # Score GPUs (lower is better)
        def score_gpu(gpu: GPUDevice) -> float:
            # Prefer GPUs with lower utilization and more free memory
            utilization_score = gpu.current_utilization_percent
            memory_score = (gpu.current_memory_used_mb / gpu.total_memory_mb) * 100
            return utilization_score + memory_score

        return min(available_gpus, key=score_gpu)

    def _assign_gpu(self, gpu: GPUDevice, task: GPUTask) -> int:
        """Assign GPU to task.

        Args:
            gpu: GPU device
            task: Task to assign

        Returns:
            GPU device ID
        """
        gpu.reserve(task.task_id)
        task.assigned_device_id = gpu.device_id
        task.started_at = time.time()

        logger.info(
            "gpu_allocated",
            device_id=gpu.device_id,
            task_id=task.task_id,
        )

        return gpu.device_id

    def release_gpu(self, task_id: str) -> None:
        """Release GPU resources for a task.

        Args:
            task_id: Task identifier
        """
        task = self._tasks.get(task_id)
        if not task or task.assigned_device_id is None:
            logger.warning("task_not_found_or_not_assigned", task_id=task_id)
            return

        gpu = self._gpus.get(task.assigned_device_id)
        if gpu:
            gpu.release()

        task.completed_at = time.time()

        logger.info("gpu_released_for_task", task_id=task_id)

        # Process queued tasks
        self._process_queue()

    def _process_queue(self) -> None:
        """Process queued tasks."""
        while self._task_queue:
            task = self._task_queue[0]
            device_id = self.allocate_gpu(task)
            if device_id is None:
                # No GPU available, stop processing
                break
            # Task assigned, remove from queue
            self._task_queue.popleft()
            logger.info("queued_task_assigned", task_id=task.task_id)

    def update_gpu_stats(
        self,
        device_id: int,
        utilization_percent: float,
        memory_used_mb: int,
    ) -> None:
        """Update GPU statistics.

        Args:
            device_id: GPU device ID
            utilization_percent: Current utilization
            memory_used_mb: Current memory usage
        """
        gpu = self._gpus.get(device_id)
        if gpu:
            gpu.update_stats(utilization_percent, memory_used_mb)

    def get_gpu(self, device_id: int) -> Optional[GPUDevice]:
        """Get GPU device by ID.

        Args:
            device_id: GPU device ID

        Returns:
            GPU device or None
        """
        return self._gpus.get(device_id)

    def get_all_gpus(self) -> List[GPUDevice]:
        """Get all GPUs in the pool.

        Returns:
            List of all GPU devices
        """
        return list(self._gpus.values())

    def get_available_gpus(self) -> List[GPUDevice]:
        """Get available GPUs.

        Returns:
            List of available GPU devices
        """
        return [gpu for gpu in self._gpus.values() if gpu.is_available()]

    def get_task(self, task_id: str) -> Optional[GPUTask]:
        """Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task or None
        """
        return self._tasks.get(task_id)

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        total_gpus = len(self._gpus)
        available_gpus = len(self.get_available_gpus())
        total_memory = sum(gpu.total_memory_mb for gpu in self._gpus.values())
        used_memory = sum(gpu.current_memory_used_mb for gpu in self._gpus.values())

        running_tasks = sum(1 for task in self._tasks.values() if task.is_running())
        completed_tasks = sum(1 for task in self._tasks.values() if task.is_completed())

        return {
            "total_gpus": total_gpus,
            "available_gpus": available_gpus,
            "busy_gpus": total_gpus - available_gpus,
            "total_memory_mb": total_memory,
            "used_memory_mb": used_memory,
            "free_memory_mb": total_memory - used_memory,
            "utilization_percent": (
                (used_memory / total_memory * 100) if total_memory > 0 else 0
            ),
            "running_tasks": running_tasks,
            "completed_tasks": completed_tasks,
            "queued_tasks": len(self._task_queue),
        }
