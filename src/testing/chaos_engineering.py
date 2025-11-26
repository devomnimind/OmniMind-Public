"""
Chaos Engineering Framework for OmniMind

Implements failure injection and resilience testing.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, cast

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures to inject."""

    LATENCY = "latency"  # Add artificial latency
    EXCEPTION = "exception"  # Raise exceptions
    TIMEOUT = "timeout"  # Cause timeouts
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # Exhaust resources
    NETWORK_PARTITION = "network_partition"  # Simulate network issues
    DATA_CORRUPTION = "data_corruption"  # Corrupt data
    SERVICE_UNAVAILABLE = "service_unavailable"  # Make service unavailable


@dataclass
class ChaosExperiment:
    """Configuration for a chaos experiment."""

    name: str
    description: str
    failure_type: FailureType
    target_component: str  # Component to target (e.g., "database", "api", "llm")
    probability: float = 0.1  # Probability of failure (0.0-1.0)
    duration_seconds: float = 60.0  # How long to run experiment
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class ChaosMonkey:
    """
    Chaos Monkey for OmniMind.

    Injects failures to test system resilience.
    """

    def __init__(self, enabled: bool = False):
        """
        Initialize Chaos Monkey.

        Args:
            enabled: Whether chaos engineering is enabled
        """
        self.enabled = enabled
        self.experiments: List[ChaosExperiment] = []
        self.active_experiments: List[ChaosExperiment] = []
        self.failure_log: List[Dict[str, Any]] = []

        logger.info(f"Chaos Monkey initialized (enabled={enabled})")

    def register_experiment(self, experiment: ChaosExperiment) -> None:
        """
        Register a chaos experiment.

        Args:
            experiment: Experiment configuration
        """
        self.experiments.append(experiment)
        logger.info(f"Registered chaos experiment: {experiment.name}")

    def inject_failure(
        self, component: str, operation: str = "unknown"
    ) -> Optional[Exception]:
        """
        Inject failure if chaos is enabled and conditions are met.

        Args:
            component: Component being tested
            operation: Operation being performed

        Returns:
            Exception to raise, or None if no failure
        """
        if not self.enabled:
            return None

        # Find applicable experiments
        applicable = [
            exp
            for exp in self.active_experiments
            if exp.target_component == component and exp.enabled
        ]

        for experiment in applicable:
            # Roll dice to see if failure occurs
            if random.random() < experiment.probability:
                failure = self._generate_failure(experiment, operation)

                # Log failure
                self.failure_log.append(
                    {
                        "timestamp": time.time(),
                        "experiment": experiment.name,
                        "component": component,
                        "operation": operation,
                        "failure_type": experiment.failure_type.value,
                    }
                )

                logger.warning(
                    f"Chaos injection: {experiment.name} on {component}.{operation}"
                )

                return failure

        return None

    def _generate_failure(
        self, experiment: ChaosExperiment, operation: str
    ) -> Optional[Exception]:
        """Generate failure based on experiment type."""
        if experiment.failure_type == FailureType.LATENCY:
            # Inject latency
            delay = experiment.parameters.get("delay_seconds", 5.0)
            time.sleep(delay)
            return None

        elif experiment.failure_type == FailureType.EXCEPTION:
            # Raise exception
            message = experiment.parameters.get(
                "message", f"Chaos injection: {experiment.name}"
            )
            exception_class = cast(
                Type[Exception],
                experiment.parameters.get("exception_class", Exception),
            )
            return exception_class(message)

        elif experiment.failure_type == FailureType.TIMEOUT:
            # Simulate timeout
            message = f"Operation timeout (chaos injection: {experiment.name})"
            return TimeoutError(message)

        elif experiment.failure_type == FailureType.SERVICE_UNAVAILABLE:
            # Service unavailable
            message = f"Service unavailable (chaos injection: {experiment.name})"
            return ConnectionError(message)

        elif experiment.failure_type == FailureType.DATA_CORRUPTION:
            # This would corrupt data, but we don't want to actually do that
            # Instead, return an error indicating corrupted data detected
            message = f"Data corruption detected (chaos injection: {experiment.name})"
            return ValueError(message)

        return None

    async def start_experiment(self, experiment_name: str) -> None:
        """
        Start a chaos experiment.

        Args:
            experiment_name: Name of experiment to start
        """
        experiment = next(
            (exp for exp in self.experiments if exp.name == experiment_name), None
        )

        if not experiment:
            logger.error(f"Experiment not found: {experiment_name}")
            return

        self.active_experiments.append(experiment)
        logger.info(f"Started chaos experiment: {experiment_name}")

        # Schedule experiment end
        await asyncio.sleep(experiment.duration_seconds)
        await self.stop_experiment(experiment_name)

    async def stop_experiment(self, experiment_name: str) -> None:
        """
        Stop a chaos experiment.

        Args:
            experiment_name: Name of experiment to stop
        """
        self.active_experiments = [
            exp for exp in self.active_experiments if exp.name != experiment_name
        ]
        logger.info(f"Stopped chaos experiment: {experiment_name}")

    def get_failure_report(self) -> Dict[str, Any]:
        """Get report of all failures injected."""
        return {
            "total_failures": len(self.failure_log),
            "failures_by_type": self._count_by_type(),
            "failures_by_component": self._count_by_component(),
            "recent_failures": self.failure_log[-10:],
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count failures by type."""
        counts: Dict[str, int] = {}
        for failure in self.failure_log:
            failure_type = failure["failure_type"]
            counts[failure_type] = counts.get(failure_type, 0) + 1
        return counts

    def _count_by_component(self) -> Dict[str, int]:
        """Count failures by component."""
        counts: Dict[str, int] = {}
        for failure in self.failure_log:
            component = failure["component"]
            counts[component] = counts.get(component, 0) + 1
        return counts


# Global chaos monkey instance
chaos_monkey = ChaosMonkey(enabled=False)


def enable_chaos(enabled: bool = True) -> None:
    """
    Enable or disable chaos engineering globally.

    Args:
        enabled: Whether to enable chaos
    """
    chaos_monkey.enabled = enabled
    logger.info(f"Chaos engineering {'enabled' if enabled else 'disabled'}")


def inject_chaos(component: str, operation: str = "unknown") -> None:
    """
    Inject chaos if enabled.

    Args:
        component: Component being tested
        operation: Operation being performed

    Raises:
        Exception: If chaos injection determines a failure should occur
    """
    failure = chaos_monkey.inject_failure(component, operation)
    if failure:
        raise failure


# Pre-defined chaos experiments


def create_database_latency_experiment() -> ChaosExperiment:
    """Create experiment for database latency."""
    return ChaosExperiment(
        name="database_latency",
        description="Add latency to database operations",
        failure_type=FailureType.LATENCY,
        target_component="database",
        probability=0.2,
        duration_seconds=300,
        parameters={"delay_seconds": 2.0},
    )


def create_api_timeout_experiment() -> ChaosExperiment:
    """Create experiment for API timeouts."""
    return ChaosExperiment(
        name="api_timeout",
        description="Cause API request timeouts",
        failure_type=FailureType.TIMEOUT,
        target_component="api",
        probability=0.1,
        duration_seconds=180,
    )


def create_llm_failure_experiment() -> ChaosExperiment:
    """Create experiment for LLM failures."""
    return ChaosExperiment(
        name="llm_failure",
        description="Simulate LLM service failures",
        failure_type=FailureType.SERVICE_UNAVAILABLE,
        target_component="llm",
        probability=0.15,
        duration_seconds=120,
    )


def create_memory_exhaustion_experiment() -> ChaosExperiment:
    """Create experiment for memory exhaustion."""
    return ChaosExperiment(
        name="memory_exhaustion",
        description="Simulate memory exhaustion",
        failure_type=FailureType.RESOURCE_EXHAUSTION,
        target_component="system",
        probability=0.05,
        duration_seconds=60,
        parameters={"resource": "memory"},
    )


def register_default_experiments() -> None:
    """Register default chaos experiments."""
    chaos_monkey.register_experiment(create_database_latency_experiment())
    chaos_monkey.register_experiment(create_api_timeout_experiment())
    chaos_monkey.register_experiment(create_llm_failure_experiment())
    chaos_monkey.register_experiment(create_memory_exhaustion_experiment())

    logger.info("Registered default chaos experiments")


# Decorator for chaos-aware functions


def chaos_aware(component: str, operation: Optional[str] = None) -> Callable[..., Any]:
    """
    Decorator to make a function chaos-aware.

    Args:
        component: Component name
        operation: Operation name (defaults to function name)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        op_name = operation or func.__name__

        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            inject_chaos(component, op_name)
            return await func(*args, **kwargs)

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            inject_chaos(component, op_name)
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Example usage:
# @chaos_aware("database", "query")
# async def query_database(query: str):
#     # This function will have chaos injected
#     return await db.execute(query)
