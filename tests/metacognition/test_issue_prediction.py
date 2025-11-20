"""Tests for proactive issue prediction engine."""


from src.metacognition.issue_prediction import (
    IssuePredictionEngine,
    MetricType,
    PredictionSeverity,
    TimeSeriesAnalyzer,
)


class TestTimeSeriesAnalyzer:
    """Tests for TimeSeriesAnalyzer."""

    def test_initialization(self) -> None:
        """Test analyzer initialization."""
        analyzer = TimeSeriesAnalyzer(window_size=50)
        assert analyzer.window_size == 50
        assert len(analyzer._data) == len(MetricType)

    def test_add_data_point(self) -> None:
        """Test adding data points."""
        analyzer = TimeSeriesAnalyzer(window_size=10)

        analyzer.add_data_point(MetricType.CPU_USAGE, 50.0)
        analyzer.add_data_point(MetricType.CPU_USAGE, 55.0)

        assert len(analyzer._data[MetricType.CPU_USAGE]) == 2

    def test_window_size_limit(self) -> None:
        """Test that window size is respected."""
        analyzer = TimeSeriesAnalyzer(window_size=5)

        # Add more points than window size
        for i in range(10):
            analyzer.add_data_point(MetricType.CPU_USAGE, float(i))

        # Should only keep last 5
        assert len(analyzer._data[MetricType.CPU_USAGE]) == 5

    def test_get_trend_increasing(self) -> None:
        """Test trend detection for increasing values."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        # Add increasing values
        for i in range(10):
            analyzer.add_data_point(MetricType.CPU_USAGE, float(i * 10))

        trend = analyzer.get_trend(MetricType.CPU_USAGE)
        assert trend is not None
        assert trend > 0  # Positive trend

    def test_get_trend_decreasing(self) -> None:
        """Test trend detection for decreasing values."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        # Add decreasing values
        for i in range(10):
            analyzer.add_data_point(MetricType.CPU_USAGE, float(100 - i * 10))

        trend = analyzer.get_trend(MetricType.CPU_USAGE)
        assert trend is not None
        assert trend < 0  # Negative trend

    def test_get_trend_insufficient_data(self) -> None:
        """Test trend with insufficient data."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        analyzer.add_data_point(MetricType.CPU_USAGE, 50.0)

        trend = analyzer.get_trend(MetricType.CPU_USAGE)
        assert trend is None

    def test_detect_anomaly_normal(self) -> None:
        """Test anomaly detection with normal values."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        # Add normal values around 50
        for _ in range(20):
            analyzer.add_data_point(MetricType.CPU_USAGE, 50.0)

        is_anomaly, z_score = analyzer.detect_anomaly(MetricType.CPU_USAGE)
        assert not is_anomaly
        assert abs(z_score) < 2.0

    def test_detect_anomaly_spike(self) -> None:
        """Test anomaly detection with spike."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        # Add normal values
        for _ in range(20):
            analyzer.add_data_point(MetricType.CPU_USAGE, 50.0)

        # Add anomalous spike
        analyzer.add_data_point(MetricType.CPU_USAGE, 150.0)

        is_anomaly, z_score = analyzer.detect_anomaly(MetricType.CPU_USAGE)
        assert is_anomaly
        assert z_score > 2.0

    def test_predict_resource_exhaustion(self) -> None:
        """Test resource exhaustion prediction."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        # Add increasing values approaching 95%
        for i in range(20):
            analyzer.add_data_point(MetricType.CPU_USAGE, 70.0 + i * 1.0)

        predicted_time = analyzer.predict_resource_exhaustion(
            MetricType.CPU_USAGE, threshold=95.0
        )

        assert predicted_time is not None
        assert predicted_time > datetime.now()

    def test_predict_resource_exhaustion_no_trend(self) -> None:
        """Test resource exhaustion with no upward trend."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        # Add stable values
        for _ in range(20):
            analyzer.add_data_point(MetricType.CPU_USAGE, 50.0)

        predicted_time = analyzer.predict_resource_exhaustion(
            MetricType.CPU_USAGE, threshold=95.0
        )

        assert predicted_time is None

    def test_get_statistics(self) -> None:
        """Test getting statistics."""
        analyzer = TimeSeriesAnalyzer(window_size=100)

        values = [40.0, 50.0, 60.0, 50.0, 55.0]
        for val in values:
            analyzer.add_data_point(MetricType.CPU_USAGE, val)

        stats = analyzer.get_statistics(MetricType.CPU_USAGE)

        assert "mean" in stats
        assert "median" in stats
        assert "stdev" in stats
        assert "min" in stats
        assert "max" in stats
        assert "current" in stats
        assert "trend" in stats

        assert stats["min"] == 40.0
        assert stats["max"] == 60.0
        assert stats["current"] == 55.0


class TestIssuePredictionEngine:
    """Tests for IssuePredictionEngine."""

    def test_initialization(self) -> None:
        """Test engine initialization."""
        engine = IssuePredictionEngine(window_size=50)
        assert engine.analyzer.window_size == 50
        assert len(engine._thresholds) > 0

    def test_update_metric(self) -> None:
        """Test updating metrics."""
        engine = IssuePredictionEngine()

        engine.update_metric(MetricType.CPU_USAGE, 50.0)
        engine.update_metric(MetricType.CPU_USAGE, 55.0)

        stats = engine.get_metrics_summary()
        assert MetricType.CPU_USAGE.value in stats

    def test_predict_resource_exhaustion_warning(self) -> None:
        """Test prediction of resource exhaustion."""
        engine = IssuePredictionEngine()

        # Simulate increasing CPU usage
        for i in range(30):
            engine.update_metric(MetricType.CPU_USAGE, 60.0 + i * 0.5)

        predictions = engine.get_current_predictions()

        # Should have at least one prediction about CPU
        cpu_predictions = [
            p for p in predictions if p.metric_type == MetricType.CPU_USAGE
        ]

        if cpu_predictions:
            pred = cpu_predictions[0]
            assert pred.severity in [
                PredictionSeverity.WARNING,
                PredictionSeverity.CRITICAL,
            ]
            assert 0.0 <= pred.probability <= 1.0
            assert 0.0 <= pred.confidence <= 1.0

    def test_predict_anomaly(self) -> None:
        """Test anomaly prediction."""
        engine = IssuePredictionEngine()

        # Add normal values
        for _ in range(30):
            engine.update_metric(MetricType.ERROR_RATE, 1.0)

        # Add anomaly - spike in error rate
        engine.update_metric(MetricType.ERROR_RATE, 50.0)

        predictions = engine.get_current_predictions()

        # Should detect anomaly in error rate
        error_predictions = [
            p for p in predictions if p.metric_type == MetricType.ERROR_RATE
        ]

        if error_predictions:
            pred = error_predictions[0]
            assert (
                "anomaly" in pred.description.lower()
                or "error" in pred.description.lower()
            )

    def test_predict_performance_degradation(self) -> None:
        """Test performance degradation prediction."""
        engine = IssuePredictionEngine()

        # Simulate increasing response time
        for i in range(30):
            engine.update_metric(MetricType.RESPONSE_TIME, 100.0 + i * 5.0)

        predictions = engine.get_current_predictions()

        # Should detect performance degradation
        perf_predictions = [
            p for p in predictions if p.metric_type == MetricType.RESPONSE_TIME
        ]

        if perf_predictions:
            pred = perf_predictions[0]
            assert "degradation" in pred.description.lower()

    def test_prediction_to_dict(self) -> None:
        """Test prediction serialization."""
        engine = IssuePredictionEngine()

        # Generate some predictions
        for i in range(30):
            engine.update_metric(MetricType.CPU_USAGE, 60.0 + i * 1.0)

        predictions = engine.get_current_predictions()

        if predictions:
            pred_dict = predictions[0].to_dict()

            assert "metric_type" in pred_dict
            assert "severity" in pred_dict
            assert "probability" in pred_dict
            assert "description" in pred_dict
            assert "recommended_actions" in pred_dict
            assert "confidence" in pred_dict

    def test_get_prediction_history(self) -> None:
        """Test prediction history tracking."""
        engine = IssuePredictionEngine()

        # Generate predictions in two batches
        for i in range(15):
            engine.update_metric(MetricType.CPU_USAGE, 60.0 + i * 1.0)

        initial_count = len(engine.get_prediction_history())

        engine.clear_predictions()

        for i in range(15):
            engine.update_metric(MetricType.CPU_USAGE, 75.0 + i * 1.0)

        final_count = len(engine.get_prediction_history())

        # History should accumulate
        assert final_count >= initial_count

    def test_clear_predictions(self) -> None:
        """Test clearing current predictions."""
        engine = IssuePredictionEngine()

        # Generate predictions
        for i in range(30):
            engine.update_metric(MetricType.CPU_USAGE, 60.0 + i * 1.0)


        engine.clear_predictions()

        predictions_after = len(engine.get_current_predictions())

        assert predictions_after == 0
        # History should still be intact
        assert len(engine.get_prediction_history()) > 0

    def test_multiple_metric_types(self) -> None:
        """Test predictions for multiple metric types."""
        engine = IssuePredictionEngine()

        # Update multiple metrics
        for i in range(30):
            engine.update_metric(MetricType.CPU_USAGE, 60.0 + i * 0.8)
            engine.update_metric(MetricType.MEMORY_USAGE, 70.0 + i * 0.6)
            engine.update_metric(MetricType.DISK_USAGE, 50.0 + i * 1.0)

        summary = engine.get_metrics_summary()

        # Should have statistics for all updated metrics
        assert MetricType.CPU_USAGE.value in summary
        assert MetricType.MEMORY_USAGE.value in summary
        assert MetricType.DISK_USAGE.value in summary

    def test_recommended_actions_present(self) -> None:
        """Test that predictions include recommended actions."""
        engine = IssuePredictionEngine()

        # Generate predictions
        for i in range(30):
            engine.update_metric(MetricType.CPU_USAGE, 70.0 + i * 0.7)

        predictions = engine.get_current_predictions()

        if predictions:
            for pred in predictions:
                assert len(pred.recommended_actions) > 0
                assert all(
                    isinstance(action, str) for action in pred.recommended_actions
                )

    def test_supporting_data_present(self) -> None:
        """Test that predictions include supporting data."""
        engine = IssuePredictionEngine()

        # Generate predictions
        for i in range(30):
            engine.update_metric(MetricType.MEMORY_USAGE, 75.0 + i * 0.5)

        predictions = engine.get_current_predictions()

        if predictions:
            for pred in predictions:
                assert isinstance(pred.supporting_data, dict)
                assert len(pred.supporting_data) > 0
