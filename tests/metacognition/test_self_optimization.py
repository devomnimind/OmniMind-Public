"""Tests for Self-Optimization Engine."""

from datetime import datetime
import pytest

from src.metacognition.self_optimization import (
    ABTest,
    Configuration,
    ExperimentStatus,
    PerformanceMetrics,
    SelfOptimizationEngine,
)


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics."""

    def test_get_score_default_weights(self) -> None:
        """Test score calculation with default weights."""
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            response_time_ms=100.0,
            throughput_rps=50.0,
            error_rate=0.01,
            cpu_usage=50.0,
            memory_usage=60.0,
        )

        score = metrics.get_score()
        assert 0.0 <= score <= 1.0

    def test_get_score_custom_weights(self) -> None:
        """Test score calculation with custom weights."""
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            response_time_ms=100.0,
            throughput_rps=50.0,
            error_rate=0.01,
            cpu_usage=50.0,
            memory_usage=60.0,
        )

        weights = {
            "response_time": 0.5,
            "throughput": 0.2,
            "error_rate": 0.2,
            "resource_usage": 0.1,
        }

        score = metrics.get_score(weights)
        assert 0.0 <= score <= 1.0

    def test_to_dict(self) -> None:
        """Test metrics serialization."""
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            response_time_ms=100.0,
            throughput_rps=50.0,
            error_rate=0.01,
            cpu_usage=50.0,
            memory_usage=60.0,
        )

        metrics_dict = metrics.to_dict()

        assert "response_time_ms" in metrics_dict
        assert "throughput_rps" in metrics_dict
        assert "error_rate" in metrics_dict
        assert "score" in metrics_dict


class TestConfiguration:
    """Tests for Configuration."""

    def test_initialization(self) -> None:
        """Test configuration initialization."""
        config = Configuration(
            config_id="config-1",
            name="Test Config",
            parameters={"threads": 10, "timeout": 30},
        )

        assert config.config_id == "config-1"
        assert config.name == "Test Config"
        assert config.parameters["threads"] == 10

    def test_to_dict(self) -> None:
        """Test configuration serialization."""
        config = Configuration(
            config_id="config-1",
            name="Test Config",
            parameters={"threads": 10},
        )

        config_dict = config.to_dict()

        assert "config_id" in config_dict
        assert "name" in config_dict
        assert "parameters" in config_dict


class TestABTest:
    """Tests for ABTest."""

    def test_initialization(self) -> None:
        """Test AB test initialization."""
        control = Configuration("control", "Control", {"threads": 10})
        treatment = Configuration("treatment", "Treatment", {"threads": 20})

        test = ABTest(
            test_id="test-1",
            name="Thread count test",
            control_config=control,
            treatment_config=treatment,
            started_at=datetime.now(),
        )

        assert test.test_id == "test-1"
        assert test.status == ExperimentStatus.PLANNING

    def test_add_metrics(self) -> None:
        """Test adding metrics."""
        control = Configuration("control", "Control", {"threads": 10})
        treatment = Configuration("treatment", "Treatment", {"threads": 20})

        test = ABTest(
            test_id="test-1",
            name="Test",
            control_config=control,
            treatment_config=treatment,
            started_at=datetime.now(),
            min_samples=10,
        )

        # Add control metrics
        for _ in range(15):
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time_ms=100.0,
                throughput_rps=50.0,
                error_rate=0.01,
                cpu_usage=50.0,
                memory_usage=60.0,
            )
            test.add_control_metric(metrics)

        # Add treatment metrics
        for _ in range(15):
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time_ms=80.0,  # Better performance
                throughput_rps=60.0,
                error_rate=0.005,
                cpu_usage=45.0,
                memory_usage=55.0,
            )
            test.add_treatment_metric(metrics)

        assert len(test.control_metrics) == 15
        assert len(test.treatment_metrics) == 15
        assert test.has_sufficient_data()

    def test_get_results_insufficient_data(self) -> None:
        """Test getting results with insufficient data."""
        control = Configuration("control", "Control", {"threads": 10})
        treatment = Configuration("treatment", "Treatment", {"threads": 20})

        test = ABTest(
            test_id="test-1",
            name="Test",
            control_config=control,
            treatment_config=treatment,
            started_at=datetime.now(),
            min_samples=100,
        )

        results = test.get_results()
        assert results["status"] == "insufficient_data"

    def test_get_results_with_winner(self) -> None:
        """Test getting results with a clear winner."""
        control = Configuration("control", "Control", {"threads": 10})
        treatment = Configuration("treatment", "Treatment", {"threads": 20})

        test = ABTest(
            test_id="test-1",
            name="Test",
            control_config=control,
            treatment_config=treatment,
            started_at=datetime.now(),
            min_samples=10,
        )

        # Add control metrics (lower performance)
        for _ in range(20):
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time_ms=200.0,
                throughput_rps=30.0,
                error_rate=0.02,
                cpu_usage=70.0,
                memory_usage=75.0,
            )
            test.add_control_metric(metrics)

        # Add treatment metrics (better performance)
        for _ in range(20):
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time_ms=80.0,
                throughput_rps=70.0,
                error_rate=0.005,
                cpu_usage=40.0,
                memory_usage=45.0,
            )
            test.add_treatment_metric(metrics)

        results = test.get_results()

        assert results["status"] == "complete"
        assert "winner" in results
        assert "improvement" in results
        assert results["treatment_mean"] > results["control_mean"]


class TestSelfOptimizationEngine:
    """Tests for SelfOptimizationEngine."""

    def test_initialization(self) -> None:
        """Test engine initialization."""
        engine = SelfOptimizationEngine()
        assert len(engine._active_tests) == 0

    def test_set_baseline_configuration(self) -> None:
        """Test setting baseline configuration."""
        engine = SelfOptimizationEngine()

        config = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(config)

        assert engine.get_current_configuration() == config

    def test_create_ab_test(self) -> None:
        """Test creating an A/B test."""
        engine = SelfOptimizationEngine()

        baseline = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(baseline)

        treatment = Configuration("treatment", "Treatment", {"threads": 20})
        test = engine.create_ab_test("test-1", "Thread test", treatment)

        assert test.test_id == "test-1"
        assert test.control_config == baseline
        assert test.treatment_config == treatment

    def test_create_ab_test_without_baseline(self) -> None:
        """Test that creating test without baseline raises error."""
        engine = SelfOptimizationEngine()

        treatment = Configuration("treatment", "Treatment", {"threads": 20})

        with pytest.raises(ValueError):
            engine.create_ab_test("test-1", "Thread test", treatment)

    def test_start_test(self) -> None:
        """Test starting an A/B test."""
        engine = SelfOptimizationEngine()

        baseline = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(baseline)

        treatment = Configuration("treatment", "Treatment", {"threads": 20})
        engine.create_ab_test("test-1", "Thread test", treatment)

        engine.start_test("test-1")

        active_tests = engine.get_active_tests()
        assert len(active_tests) == 1
        assert active_tests[0].status == ExperimentStatus.RUNNING

    def test_record_metrics(self) -> None:
        """Test recording metrics."""
        engine = SelfOptimizationEngine()

        baseline = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(baseline)

        treatment = Configuration("treatment", "Treatment", {"threads": 20})
        engine.create_ab_test("test-1", "Thread test", treatment)
        engine.start_test("test-1")

        # Record metrics
        for is_treatment in [False, True]:
            for _ in range(10):
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time_ms=100.0,
                    throughput_rps=50.0,
                    error_rate=0.01,
                    cpu_usage=50.0,
                    memory_usage=60.0,
                )
                engine.record_metrics("test-1", metrics, is_treatment)

        active_tests = engine.get_active_tests()
        assert len(active_tests[0].control_metrics) == 10
        assert len(active_tests[0].treatment_metrics) == 10

    def test_analyze_test(self) -> None:
        """Test analyzing a test."""
        engine = SelfOptimizationEngine()

        baseline = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(baseline)

        treatment = Configuration("treatment", "Treatment", {"threads": 20})
        engine.create_ab_test("test-1", "Thread test", treatment)
        engine.start_test("test-1")

        # Record sufficient metrics
        for is_treatment in [False, True]:
            for _ in range(10):
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time_ms=100.0,
                    throughput_rps=50.0,
                    error_rate=0.01,
                    cpu_usage=50.0,
                    memory_usage=60.0,
                )
                engine.record_metrics("test-1", metrics, is_treatment)

        results = engine.analyze_test("test-1")

        assert "status" in results
        assert results["status"] == "complete"

    def test_apply_winner(self) -> None:
        """Test applying winner configuration."""
        engine = SelfOptimizationEngine()

        baseline = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(baseline)

        treatment = Configuration("treatment", "Treatment", {"threads": 20})
        engine.create_ab_test("test-1", "Thread test", treatment)
        engine.start_test("test-1")

        # Record metrics showing treatment wins
        for _ in range(10):
            engine.record_metrics(
                "test-1",
                PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time_ms=200.0,
                    throughput_rps=30.0,
                    error_rate=0.02,
                    cpu_usage=70.0,
                    memory_usage=75.0,
                ),
                is_treatment=False,
            )

        for _ in range(10):
            engine.record_metrics(
                "test-1",
                PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time_ms=80.0,
                    throughput_rps=70.0,
                    error_rate=0.005,
                    cpu_usage=40.0,
                    memory_usage=45.0,
                ),
                is_treatment=True,
            )

        engine.analyze_test("test-1")

        # Winner should be applied
        assert engine.get_current_configuration().config_id in ["baseline", "treatment"]

    def test_rollback(self) -> None:
        """Test rolling back a test."""
        engine = SelfOptimizationEngine()

        baseline = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(baseline)

        treatment = Configuration("treatment", "Treatment", {"threads": 20})
        engine.create_ab_test("test-1", "Thread test", treatment, min_samples=10)
        engine.start_test("test-1")

        # Rollback
        control_config = engine.rollback("test-1")

        assert control_config == baseline
        assert engine.get_current_configuration() == baseline

    def test_get_optimization_history(self) -> None:
        """Test getting optimization history."""
        engine = SelfOptimizationEngine()

        baseline = Configuration("baseline", "Baseline", {"threads": 10})
        engine.set_baseline_configuration(baseline)

        treatment = Configuration("treatment", "Treatment", {"threads": 20})
        engine.create_ab_test("test-1", "Thread test", treatment, min_samples=10)
        engine.start_test("test-1")

        # Record and analyze
        for is_treatment in [False, True]:
            for _ in range(10):
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time_ms=100.0,
                    throughput_rps=50.0,
                    error_rate=0.01,
                    cpu_usage=50.0,
                    memory_usage=60.0,
                )
                engine.record_metrics("test-1", metrics, is_treatment)

        engine.analyze_test("test-1")

        history = engine.get_optimization_history()
        assert len(history) > 0
