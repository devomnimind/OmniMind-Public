"""Tests for the metrics collector system."""

import pytest

from web.backend.monitoring.metrics_collector import MetricsCollector


@pytest.fixture
def metrics_collector():
    """Create a fresh metrics collector instance."""
    return MetricsCollector()


def test_record_successful_request(metrics_collector):
    """Test recording a successful request."""
    metrics_collector.record_request(
        path="/api/test",
        method="GET",
        latency=0.05,
        status_code=200,
    )

    endpoint_metrics = metrics_collector.get_endpoint_metrics("/api/test", "GET")
    assert endpoint_metrics is not None
    assert endpoint_metrics["total_requests"] == 1
    assert endpoint_metrics["successful_requests"] == 1
    assert endpoint_metrics["failed_requests"] == 0


def test_record_failed_request(metrics_collector):
    """Test recording a failed request."""
    metrics_collector.record_request(
        path="/api/test",
        method="POST",
        latency=0.1,
        status_code=500,
        error="Internal server error",
    )

    endpoint_metrics = metrics_collector.get_endpoint_metrics("/api/test", "POST")
    assert endpoint_metrics["total_requests"] == 1
    assert endpoint_metrics["successful_requests"] == 0
    assert endpoint_metrics["failed_requests"] == 1


def test_latency_tracking(metrics_collector):
    """Test latency tracking."""
    # Record multiple requests with different latencies
    latencies = [0.01, 0.05, 0.1, 0.02, 0.03]
    for latency in latencies:
        metrics_collector.record_request(
            path="/api/latency",
            method="GET",
            latency=latency,
            status_code=200,
        )

    endpoint_metrics = metrics_collector.get_endpoint_metrics("/api/latency", "GET")
    assert endpoint_metrics["min_latency"] == 0.01
    assert endpoint_metrics["max_latency"] == 0.1
    avg = sum(latencies) / len(latencies)
    assert abs(endpoint_metrics["avg_latency"] - avg) < 0.001


def test_success_rate_calculation(metrics_collector):
    """Test success rate calculation."""
    # 7 successful, 3 failed = 70% success rate
    for _ in range(7):
        metrics_collector.record_request("/api/test", "GET", 0.01, 200)
    for _ in range(3):
        metrics_collector.record_request("/api/test", "GET", 0.01, 500)

    endpoint_metrics = metrics_collector.get_endpoint_metrics("/api/test", "GET")
    assert endpoint_metrics["success_rate"] == 70.0


def test_get_all_metrics(metrics_collector):
    """Test getting all metrics."""
    # Record requests to multiple endpoints
    metrics_collector.record_request("/api/users", "GET", 0.01, 200)
    metrics_collector.record_request("/api/tasks", "POST", 0.05, 201)
    metrics_collector.record_request("/api/agents", "GET", 0.02, 200)

    all_metrics = metrics_collector.get_all_metrics()
    assert all_metrics["total_requests"] == 3
    assert all_metrics["successful_requests"] == 3
    assert len(all_metrics["endpoints"]) == 3


def test_recent_requests(metrics_collector):
    """Test getting recent requests."""
    for i in range(10):
        metrics_collector.record_request(
            path=f"/api/test/{i}",
            method="GET",
            latency=0.01,
            status_code=200,
        )

    recent = metrics_collector.get_recent_requests(limit=5)
    assert len(recent) == 5


def test_error_summary(metrics_collector):
    """Test error summary generation."""
    # Record some errors
    metrics_collector.record_request("/api/test", "GET", 0.01, 404)
    metrics_collector.record_request("/api/test", "POST", 0.01, 500)
    metrics_collector.record_request("/api/other", "GET", 0.01, 500)

    error_summary = metrics_collector.get_error_summary()
    assert error_summary["total_errors"] == 3
    assert error_summary["errors_by_path"]["/api/test"] == 2
    assert error_summary["errors_by_code"][404] == 1
    assert error_summary["errors_by_code"][500] == 2


def test_request_history_limit(metrics_collector):
    """Test that request history is limited."""
    # Set a small max history
    metrics_collector._max_history = 10

    # Record more than the limit
    for i in range(20):
        metrics_collector.record_request(f"/api/test/{i}", "GET", 0.01, 200)

    # Should only keep the last 10
    assert len(metrics_collector._request_history) == 10


def test_endpoint_not_found(metrics_collector):
    """Test getting metrics for non-existent endpoint."""
    metrics = metrics_collector.get_endpoint_metrics("/api/nonexistent", "GET")
    assert metrics is None


def test_multiple_methods_same_path(metrics_collector):
    """Test tracking different methods on the same path."""
    metrics_collector.record_request("/api/resource", "GET", 0.01, 200)
    metrics_collector.record_request("/api/resource", "POST", 0.02, 201)
    metrics_collector.record_request("/api/resource", "GET", 0.01, 200)

    get_metrics = metrics_collector.get_endpoint_metrics("/api/resource", "GET")
    post_metrics = metrics_collector.get_endpoint_metrics("/api/resource", "POST")

    assert get_metrics["total_requests"] == 2
    assert post_metrics["total_requests"] == 1


@pytest.mark.asyncio
async def test_metrics_lifecycle(metrics_collector):
    """Test metrics collector lifecycle."""
    await metrics_collector.start()
    assert metrics_collector._running is True

    await metrics_collector.stop()
    assert metrics_collector._running is False
