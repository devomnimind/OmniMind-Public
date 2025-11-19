"""
Tests for Chaos Engineering Framework.
"""

import asyncio
import pytest

from src.testing.chaos_engineering import (
    ChaosExperiment,
    ChaosMonkey,
    FailureType,
    chaos_aware,
    create_api_timeout_experiment,
    create_database_latency_experiment,
    enable_chaos,
    inject_chaos,
)


@pytest.fixture
def chaos_monkey():
    """Create a fresh chaos monkey instance for each test."""
    monkey = ChaosMonkey(enabled=True)
    yield monkey
    # Cleanup
    monkey.enabled = False
    monkey.experiments.clear()
    monkey.active_experiments.clear()
    monkey.failure_log.clear()


def test_chaos_monkey_initialization():
    """Test chaos monkey initializes correctly."""
    monkey = ChaosMonkey(enabled=False)
    assert monkey.enabled is False
    assert len(monkey.experiments) == 0
    assert len(monkey.active_experiments) == 0


def test_register_experiment(chaos_monkey):
    """Test registering chaos experiments."""
    experiment = ChaosExperiment(
        name="test_experiment",
        description="Test experiment",
        failure_type=FailureType.LATENCY,
        target_component="test",
    )

    chaos_monkey.register_experiment(experiment)

    assert len(chaos_monkey.experiments) == 1
    assert chaos_monkey.experiments[0].name == "test_experiment"


@pytest.mark.asyncio
async def test_start_stop_experiment(chaos_monkey):
    """Test starting and stopping experiments."""
    experiment = ChaosExperiment(
        name="test_experiment",
        description="Test",
        failure_type=FailureType.LATENCY,
        target_component="test",
        duration_seconds=0.1,
    )

    chaos_monkey.register_experiment(experiment)

    # Start experiment
    task = asyncio.create_task(chaos_monkey.start_experiment("test_experiment"))

    # Wait a bit
    await asyncio.sleep(0.05)

    # Should be active
    assert len(chaos_monkey.active_experiments) == 1

    # Wait for it to complete
    await task

    # Should be stopped
    assert len(chaos_monkey.active_experiments) == 0


def test_inject_failure_when_disabled():
    """Test that no failures are injected when disabled."""
    monkey = ChaosMonkey(enabled=False)

    experiment = ChaosExperiment(
        name="test",
        description="Test",
        failure_type=FailureType.EXCEPTION,
        target_component="test",
        probability=1.0,  # 100% chance
    )

    monkey.register_experiment(experiment)
    monkey.active_experiments.append(experiment)

    # Should not inject failure when disabled
    failure = monkey.inject_failure("test", "operation")
    assert failure is None


def test_inject_latency_failure(chaos_monkey):
    """Test injecting latency failures."""
    import time

    experiment = ChaosExperiment(
        name="latency_test",
        description="Test latency",
        failure_type=FailureType.LATENCY,
        target_component="test",
        probability=1.0,
        parameters={"delay_seconds": 0.1},
    )

    chaos_monkey.register_experiment(experiment)
    chaos_monkey.active_experiments.append(experiment)

    start = time.time()
    failure = chaos_monkey.inject_failure("test", "operation")
    duration = time.time() - start

    # Should have injected latency
    assert duration >= 0.1
    assert failure is None  # Latency doesn't raise exception


def test_inject_exception_failure(chaos_monkey):
    """Test injecting exception failures."""
    experiment = ChaosExperiment(
        name="exception_test",
        description="Test exception",
        failure_type=FailureType.EXCEPTION,
        target_component="test",
        probability=1.0,
        parameters={"message": "Test error"},
    )

    chaos_monkey.register_experiment(experiment)
    chaos_monkey.active_experiments.append(experiment)

    failure = chaos_monkey.inject_failure("test", "operation")

    assert failure is not None
    assert isinstance(failure, Exception)
    assert "Test error" in str(failure)


def test_inject_timeout_failure(chaos_monkey):
    """Test injecting timeout failures."""
    experiment = ChaosExperiment(
        name="timeout_test",
        description="Test timeout",
        failure_type=FailureType.TIMEOUT,
        target_component="test",
        probability=1.0,
    )

    chaos_monkey.register_experiment(experiment)
    chaos_monkey.active_experiments.append(experiment)

    failure = chaos_monkey.inject_failure("test", "operation")

    assert failure is not None
    assert isinstance(failure, TimeoutError)


def test_failure_logging(chaos_monkey):
    """Test that failures are logged."""
    experiment = ChaosExperiment(
        name="log_test",
        description="Test logging",
        failure_type=FailureType.EXCEPTION,
        target_component="test",
        probability=1.0,
    )

    chaos_monkey.register_experiment(experiment)
    chaos_monkey.active_experiments.append(experiment)

    # Inject failure
    chaos_monkey.inject_failure("test", "operation")

    # Should be logged
    assert len(chaos_monkey.failure_log) == 1
    assert chaos_monkey.failure_log[0]["component"] == "test"
    assert chaos_monkey.failure_log[0]["operation"] == "operation"


def test_failure_report(chaos_monkey):
    """Test getting failure report."""
    experiment = ChaosExperiment(
        name="report_test",
        description="Test report",
        failure_type=FailureType.EXCEPTION,
        target_component="test",
        probability=1.0,
    )

    chaos_monkey.register_experiment(experiment)
    chaos_monkey.active_experiments.append(experiment)

    # Inject some failures
    for i in range(5):
        chaos_monkey.inject_failure("test", f"operation_{i}")

    report = chaos_monkey.get_failure_report()

    assert report["total_failures"] == 5
    assert "exception" in report["failures_by_type"]
    assert "test" in report["failures_by_component"]


def test_probability_filtering(chaos_monkey):
    """Test that probability affects injection."""
    experiment = ChaosExperiment(
        name="prob_test",
        description="Test probability",
        failure_type=FailureType.EXCEPTION,
        target_component="test",
        probability=0.0,  # 0% chance
    )

    chaos_monkey.register_experiment(experiment)
    chaos_monkey.active_experiments.append(experiment)

    # Should never inject failure with 0% probability
    failures = 0
    for _ in range(100):
        if chaos_monkey.inject_failure("test", "operation"):
            failures += 1

    assert failures == 0


def test_component_filtering(chaos_monkey):
    """Test that component filtering works."""
    experiment = ChaosExperiment(
        name="filter_test",
        description="Test filtering",
        failure_type=FailureType.EXCEPTION,
        target_component="database",
        probability=1.0,
    )

    chaos_monkey.register_experiment(experiment)
    chaos_monkey.active_experiments.append(experiment)

    # Should not inject for different component
    failure = chaos_monkey.inject_failure("api", "operation")
    assert failure is None

    # Should inject for matching component
    failure = chaos_monkey.inject_failure("database", "operation")
    assert failure is not None


def test_chaos_aware_decorator():
    """Test chaos_aware decorator."""
    enable_chaos(True)

    experiment = ChaosExperiment(
        name="decorator_test",
        description="Test decorator",
        failure_type=FailureType.EXCEPTION,
        target_component="test_component",
        probability=1.0,
    )

    from src.testing.chaos_engineering import chaos_monkey as global_monkey

    global_monkey.register_experiment(experiment)
    global_monkey.active_experiments.append(experiment)

    @chaos_aware("test_component", "test_operation")
    def test_function():
        return "success"

    # Should raise exception due to chaos injection
    with pytest.raises(Exception):
        test_function()

    # Cleanup
    enable_chaos(False)
    global_monkey.active_experiments.clear()


def test_pre_defined_experiments():
    """Test pre-defined experiment creators."""
    db_exp = create_database_latency_experiment()
    assert db_exp.name == "database_latency"
    assert db_exp.failure_type == FailureType.LATENCY
    assert db_exp.target_component == "database"

    api_exp = create_api_timeout_experiment()
    assert api_exp.name == "api_timeout"
    assert api_exp.failure_type == FailureType.TIMEOUT
    assert api_exp.target_component == "api"
