"""Tests for intelligent load balancing with ML prediction."""

import pytest

from src.scaling.intelligent_load_balancer import (
    IntelligentLoadBalancer,
    NodePerformanceMetrics,
    WorkloadPrediction,
)
from src.scaling.multi_node import DistributedTask, NodeInfo, NodeStatus


def test_node_performance_metrics_creation() -> None:
    """Test NodePerformanceMetrics creation."""
    metrics = NodePerformanceMetrics(node_id="node-1")

    assert metrics.node_id == "node-1"
    assert metrics.task_success_rate == 1.0
    assert metrics.success_count == 0
    assert metrics.failure_count == 0
    assert len(metrics.task_completion_times) == 0


def test_node_performance_metrics_update() -> None:
    """Test updating performance metrics."""
    metrics = NodePerformanceMetrics(node_id="node-1")

    # Add successful task
    metrics.update_task_completion(duration=5.0, success=True)
    assert metrics.success_count == 1
    assert metrics.task_success_rate == 1.0
    assert len(metrics.task_completion_times) == 1

    # Add failed task
    metrics.update_task_completion(duration=3.0, success=False)
    assert metrics.failure_count == 1
    assert metrics.task_success_rate == 0.5

    # Add another successful task
    metrics.update_task_completion(duration=4.0, success=True)
    assert metrics.success_count == 2
    assert metrics.failure_count == 1
    assert metrics.task_success_rate == pytest.approx(2 / 3)


def test_node_performance_metrics_average_time() -> None:
    """Test average completion time calculation."""
    metrics = NodePerformanceMetrics(node_id="node-1")

    assert metrics.get_average_completion_time() == 0.0

    metrics.update_task_completion(duration=5.0, success=True)
    metrics.update_task_completion(duration=3.0, success=True)
    metrics.update_task_completion(duration=4.0, success=True)

    assert metrics.get_average_completion_time() == pytest.approx(4.0)


def test_node_performance_metrics_variance() -> None:
    """Test completion time variance calculation."""
    metrics = NodePerformanceMetrics(node_id="node-1")

    assert metrics.get_completion_time_variance() == 0.0

    metrics.update_task_completion(duration=5.0, success=True)
    assert metrics.get_completion_time_variance() == 0.0  # Single value

    metrics.update_task_completion(duration=3.0, success=True)
    metrics.update_task_completion(duration=4.0, success=True)

    variance = metrics.get_completion_time_variance()
    assert variance > 0.0


def test_node_performance_metrics_prediction() -> None:
    """Test next completion time prediction."""
    metrics = NodePerformanceMetrics(node_id="node-1")

    # No data - default estimate
    assert metrics.predict_next_completion_time() == 1.0

    # Single data point
    metrics.update_task_completion(duration=5.0, success=True)
    assert metrics.predict_next_completion_time() == 5.0

    # Multiple data points - should use exponential smoothing
    metrics.update_task_completion(duration=3.0, success=True)
    metrics.update_task_completion(duration=4.0, success=True)

    predicted = metrics.predict_next_completion_time()
    assert 3.0 <= predicted <= 5.0


def test_intelligent_load_balancer_creation() -> None:
    """Test IntelligentLoadBalancer creation."""
    balancer = IntelligentLoadBalancer(strategy="ml_predicted")

    assert balancer.strategy == "ml_predicted"
    assert len(balancer.node_metrics) == 0
    assert len(balancer.task_history) == 0


def test_record_task_completion() -> None:
    """Test recording task completion."""
    balancer = IntelligentLoadBalancer()

    balancer.record_task_completion(
        node_id="node-1",
        task_id="task-1",
        duration=5.0,
        success=True,
    )

    assert "node-1" in balancer.node_metrics
    assert len(balancer.task_history) == 1
    assert balancer.node_metrics["node-1"].success_count == 1


def test_predict_node_workload_no_data() -> None:
    """Test workload prediction with no historical data."""
    balancer = IntelligentLoadBalancer()
    node = NodeInfo(
        node_id="node-1",
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8000,
        max_concurrent_tasks=10,
    )

    prediction = balancer.predict_node_workload(node)

    assert prediction.node_id == "node-1"
    assert prediction.predicted_load == 0.0
    assert prediction.confidence == 0.0


def test_predict_node_workload_with_data() -> None:
    """Test workload prediction with historical data."""
    balancer = IntelligentLoadBalancer()
    node = NodeInfo(
        node_id="node-1",
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8000,
        max_concurrent_tasks=10,
        current_tasks=5,
    )

    # Add some historical data
    for i in range(15):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=5.0 + i * 0.1,
            success=True,
        )

    prediction = balancer.predict_node_workload(node)

    assert prediction.node_id == "node-1"
    assert prediction.predicted_load > 0.0
    assert prediction.confidence > 0.0
    assert prediction.predicted_completion_time > 0.0


def test_calculate_node_score() -> None:
    """Test node score calculation."""
    balancer = IntelligentLoadBalancer()
    node = NodeInfo(
        node_id="node-1",
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8000,
        max_concurrent_tasks=10,
        current_tasks=5,
    )

    # Add historical data
    for i in range(15):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=5.0,
            success=True,
        )

    score = balancer.calculate_node_score(node)

    assert isinstance(score, float)
    assert score >= 0.0


def test_select_node_no_nodes() -> None:
    """Test node selection with no available nodes."""
    balancer = IntelligentLoadBalancer()

    selected = balancer.select_node([])

    assert selected is None


def test_select_node_least_loaded() -> None:
    """Test least loaded node selection."""
    balancer = IntelligentLoadBalancer(strategy="least_loaded")

    nodes = [
        NodeInfo(
            node_id="node-1",
            hostname="worker-1",
            ip_address="192.168.1.10",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=5,
        ),
        NodeInfo(
            node_id="node-2",
            hostname="worker-2",
            ip_address="192.168.1.11",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=2,
        ),
        NodeInfo(
            node_id="node-3",
            hostname="worker-3",
            ip_address="192.168.1.12",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=8,
        ),
    ]

    selected = balancer.select_node(nodes)

    assert selected is not None
    assert selected.node_id == "node-2"  # Least loaded


def test_select_node_round_robin() -> None:
    """Test round robin node selection."""
    balancer = IntelligentLoadBalancer(strategy="round_robin")

    nodes = [
        NodeInfo(
            node_id=f"node-{i}",
            hostname=f"worker-{i}",
            ip_address=f"192.168.1.{10 + i}",
            port=8000,
            max_concurrent_tasks=10,
        )
        for i in range(3)
    ]

    # Should cycle through nodes
    selected_ids = []
    for _ in range(6):
        node = balancer.select_node(nodes)
        assert node is not None
        selected_ids.append(node.node_id)

    assert selected_ids == ["node-0", "node-1", "node-2", "node-0", "node-1", "node-2"]


def test_select_node_ml_predicted_insufficient_data() -> None:
    """Test ML prediction falls back when insufficient data."""
    balancer = IntelligentLoadBalancer(strategy="ml_predicted", min_samples_for_ml=10)

    nodes = [
        NodeInfo(
            node_id="node-1",
            hostname="worker-1",
            ip_address="192.168.1.10",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=5,
        ),
        NodeInfo(
            node_id="node-2",
            hostname="worker-2",
            ip_address="192.168.1.11",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=2,
        ),
    ]

    # Add only 5 tasks (less than min_samples_for_ml)
    for i in range(5):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=5.0,
            success=True,
        )

    selected = balancer.select_node(nodes)

    # Should fall back to least loaded
    assert selected is not None
    assert selected.node_id == "node-2"


def test_select_node_ml_predicted_with_data() -> None:
    """Test ML prediction with sufficient data."""
    balancer = IntelligentLoadBalancer(strategy="ml_predicted", min_samples_for_ml=10)

    nodes = [
        NodeInfo(
            node_id="node-1",
            hostname="worker-1",
            ip_address="192.168.1.10",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=5,
        ),
        NodeInfo(
            node_id="node-2",
            hostname="worker-2",
            ip_address="192.168.1.11",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=5,
        ),
    ]

    # Add performance data - node-1 is slower
    for i in range(15):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=10.0,  # Slower
            success=True,
        )
        balancer.record_task_completion(
            node_id="node-2",
            task_id=f"task-{i + 100}",
            duration=2.0,  # Faster
            success=True,
        )

    selected = balancer.select_node(nodes)

    # Should prefer faster node even with same current load
    assert selected is not None
    assert selected.node_id == "node-2"


def test_select_node_weighted_least_loaded() -> None:
    """Test weighted least loaded selection."""
    balancer = IntelligentLoadBalancer(strategy="weighted_least_loaded")

    nodes = [
        NodeInfo(
            node_id="node-1",
            hostname="worker-1",
            ip_address="192.168.1.10",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=3,
        ),
        NodeInfo(
            node_id="node-2",
            hostname="worker-2",
            ip_address="192.168.1.11",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=5,
        ),
    ]

    # Add performance data - node-1 has low success rate
    for i in range(10):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=5.0,
            success=i % 2 == 0,  # 50% success rate
        )
        balancer.record_task_completion(
            node_id="node-2",
            task_id=f"task-{i + 100}",
            duration=5.0,
            success=True,  # 100% success rate
        )

    selected = balancer.select_node(nodes)

    # Should prefer more reliable node even if more loaded
    assert selected is not None
    assert selected.node_id == "node-2"


def test_select_node_with_capability_filtering() -> None:
    """Test node selection with capability filtering."""
    balancer = IntelligentLoadBalancer()

    nodes = [
        NodeInfo(
            node_id="node-1",
            hostname="worker-1",
            ip_address="192.168.1.10",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=2,
            capabilities={"cpu_tasks"},
        ),
        NodeInfo(
            node_id="node-2",
            hostname="worker-2",
            ip_address="192.168.1.11",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=8,
            capabilities={"gpu_tasks"},
        ),
    ]

    task = DistributedTask(
        task_id="task-1",
        task_type="gpu_tasks",
        payload={},
    )

    selected = balancer.select_node(nodes, task)

    # Should select capable node even if more loaded
    assert selected is not None
    assert selected.node_id == "node-2"


def test_get_cluster_predictions() -> None:
    """Test getting predictions for all nodes."""
    balancer = IntelligentLoadBalancer()

    nodes = [
        NodeInfo(
            node_id=f"node-{i}",
            hostname=f"worker-{i}",
            ip_address=f"192.168.1.{10 + i}",
            port=8000,
            max_concurrent_tasks=10,
        )
        for i in range(3)
    ]

    predictions = balancer.get_cluster_predictions(nodes)

    assert len(predictions) == 3
    assert all(isinstance(p, WorkloadPrediction) for p in predictions.values())


def test_get_performance_summary_no_data() -> None:
    """Test performance summary with no data."""
    balancer = IntelligentLoadBalancer()

    summary = balancer.get_performance_summary()

    assert summary["total_nodes"] == 0
    assert summary["total_tasks"] == 0
    assert "message" in summary


def test_get_performance_summary_with_data() -> None:
    """Test performance summary with data."""
    balancer = IntelligentLoadBalancer()

    # Add some performance data
    for i in range(10):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=5.0,
            success=True,
        )
        balancer.record_task_completion(
            node_id="node-2",
            task_id=f"task-{i + 100}",
            duration=3.0,
            success=True,
        )

    summary = balancer.get_performance_summary()

    assert summary["total_nodes"] == 2
    assert summary["total_tasks"] == 20
    assert summary["avg_completion_time"] == pytest.approx(4.0)
    assert summary["avg_success_rate"] == 1.0
    assert "nodes" in summary


def test_optimize_strategy() -> None:
    """Test automatic strategy optimization."""
    balancer = IntelligentLoadBalancer(min_samples_for_ml=10)

    # No data - should recommend simple strategy
    strategy = balancer.optimize_strategy()
    assert strategy == "least_loaded"

    # Add some data (5-9 tasks)
    for i in range(7):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=5.0,
            success=True,
        )

    strategy = balancer.optimize_strategy()
    assert strategy == "weighted_least_loaded"

    # Add more data (>= 10 tasks)
    for i in range(5):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i + 10}",
            duration=5.0,
            success=True,
        )

    strategy = balancer.optimize_strategy()
    assert strategy == "ml_predicted"


def test_node_selection_all_nodes_busy() -> None:
    """Test node selection when all nodes are at capacity."""
    balancer = IntelligentLoadBalancer()

    nodes = [
        NodeInfo(
            node_id="node-1",
            hostname="worker-1",
            ip_address="192.168.1.10",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=10,  # At capacity
        ),
        NodeInfo(
            node_id="node-2",
            hostname="worker-2",
            ip_address="192.168.1.11",
            port=8000,
            max_concurrent_tasks=10,
            current_tasks=10,  # At capacity
        ),
    ]

    selected = balancer.select_node(nodes)

    assert selected is None


def test_node_selection_offline_nodes() -> None:
    """Test that offline nodes are not selected."""
    balancer = IntelligentLoadBalancer()

    nodes = [
        NodeInfo(
            node_id="node-1",
            hostname="worker-1",
            ip_address="192.168.1.10",
            port=8000,
            status=NodeStatus.OFFLINE,
            max_concurrent_tasks=10,
            current_tasks=0,
        ),
        NodeInfo(
            node_id="node-2",
            hostname="worker-2",
            ip_address="192.168.1.11",
            port=8000,
            status=NodeStatus.ACTIVE,
            max_concurrent_tasks=10,
            current_tasks=5,
        ),
    ]

    selected = balancer.select_node(nodes)

    assert selected is not None
    assert selected.node_id == "node-2"


def test_maxlen_deque_limits() -> None:
    """Test that deque maxlen properly limits stored data."""
    metrics = NodePerformanceMetrics(node_id="node-1")

    # Add 150 tasks (maxlen is 100)
    for i in range(150):
        metrics.update_task_completion(duration=float(i), success=True)

    # Should only keep last 100
    assert len(metrics.task_completion_times) == 100
    assert min(metrics.task_completion_times) == 50.0  # First 50 dropped


def test_task_history_maxlen() -> None:
    """Test that task history maxlen is enforced."""
    balancer = IntelligentLoadBalancer()

    # Add 1100 tasks (maxlen is 1000)
    for i in range(1100):
        balancer.record_task_completion(
            node_id="node-1",
            task_id=f"task-{i}",
            duration=5.0,
            success=True,
        )

    # Should only keep last 1000
    assert len(balancer.task_history) == 1000
