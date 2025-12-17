"""Intelligent Load Balancing with ML-based prediction.

This module extends the basic load balancer with:
- ML-based workload prediction
- Resource forecasting
- Historical performance analysis
- Adaptive strategy selection
"""

from __future__ import annotations

import logging
import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional, Tuple

from src.scaling.multi_node import DistributedTask, NodeInfo

logger = logging.getLogger(__name__)


@dataclass
class NodePerformanceMetrics:
    """Performance metrics for a node."""

    node_id: str
    task_completion_times: Deque[float] = field(default_factory=lambda: deque(maxlen=100))
    task_success_rate: float = 1.0
    average_cpu_usage: float = 0.0
    average_memory_usage: float = 0.0
    failure_count: int = 0
    success_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    def update_task_completion(self, duration: float, success: bool) -> None:
        """Update metrics after task completion."""
        self.task_completion_times.append(duration)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        total_tasks = self.success_count + self.failure_count
        if total_tasks > 0:
            self.task_success_rate = self.success_count / total_tasks
        self.last_updated = datetime.now()

    def get_average_completion_time(self) -> float:
        """Calculate average task completion time."""
        if not self.task_completion_times:
            return 0.0
        return statistics.mean(self.task_completion_times)

    def get_completion_time_variance(self) -> float:
        """Calculate variance in completion times."""
        if len(self.task_completion_times) < 2:
            return 0.0
        return statistics.variance(self.task_completion_times)

    def predict_next_completion_time(self) -> float:
        """Predict next task completion time using exponential smoothing."""
        if not self.task_completion_times:
            return 1.0  # Default estimate

        # Exponential smoothing with alpha=0.3
        alpha = 0.3
        times = list(self.task_completion_times)
        if len(times) == 1:
            return times[0]

        smoothed = times[0]
        for time in times[1:]:
            smoothed = alpha * time + (1 - alpha) * smoothed
        return smoothed


@dataclass
class WorkloadPrediction:
    """Predicted workload for a node."""

    node_id: str
    predicted_load: float
    predicted_completion_time: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class IntelligentLoadBalancer:
    """ML-enhanced load balancer with workload prediction."""

    def __init__(
        self,
        strategy: str = "ml_predicted",
        prediction_window: int = 300,  # 5 minutes
        min_samples_for_ml: int = 10,
    ) -> None:
        """Initialize intelligent load balancer.

        Args:
            strategy: Load balancing strategy
            prediction_window: Time window for predictions (seconds)
            min_samples_for_ml: Minimum samples needed for ML prediction
        """
        self.strategy = strategy
        self.prediction_window = prediction_window
        self.min_samples_for_ml = min_samples_for_ml

        # Performance tracking
        self.node_metrics: Dict[str, NodePerformanceMetrics] = {}
        self.task_history: Deque[Tuple[str, str, float, bool]] = deque(maxlen=1000)

        # State
        self._round_robin_index = 0

        logger.info(f"IntelligentLoadBalancer initialized with strategy: {strategy}")

    def record_task_completion(
        self,
        node_id: str,
        task_id: str,
        duration: float,
        success: bool,
    ) -> None:
        """Record task completion for ML learning.

        Args:
            node_id: Node that executed the task
            task_id: Task identifier
            duration: Task execution duration in seconds
            success: Whether task succeeded
        """
        # Initialize metrics if needed
        if node_id not in self.node_metrics:
            self.node_metrics[node_id] = NodePerformanceMetrics(node_id=node_id)

        # Update node metrics
        self.node_metrics[node_id].update_task_completion(duration, success)

        # Add to history
        self.task_history.append((node_id, task_id, duration, success))

        logger.debug(
            f"Recorded task {task_id} on node {node_id}: "
            f"duration={duration:.2f}s, success={success}"
        )

    def predict_node_workload(self, node: NodeInfo) -> WorkloadPrediction:
        """Predict future workload for a node.

        Args:
            node: Node to predict workload for

        Returns:
            WorkloadPrediction with predicted metrics
        """
        if node.node_id not in self.node_metrics:
            # No historical data - use current load
            return WorkloadPrediction(
                node_id=node.node_id,
                predicted_load=node.get_load_factor(),
                predicted_completion_time=1.0,
                confidence=0.0,
            )

        metrics = self.node_metrics[node.node_id]

        # Calculate predicted load based on current tasks + historical performance
        current_load = node.get_load_factor()
        avg_completion_time = metrics.get_average_completion_time()
        predicted_completion = metrics.predict_next_completion_time()

        # Adjust load based on predicted completion time
        # Slower nodes get penalized in load calculation
        if avg_completion_time > 0:
            time_factor = predicted_completion / avg_completion_time
            predicted_load = min(1.0, current_load * time_factor)
        else:
            predicted_load = current_load

        # Calculate confidence based on sample size
        sample_count = len(metrics.task_completion_times)
        confidence = min(1.0, sample_count / self.min_samples_for_ml)

        return WorkloadPrediction(
            node_id=node.node_id,
            predicted_load=predicted_load,
            predicted_completion_time=predicted_completion,
            confidence=confidence,
        )

    def calculate_node_score(self, node: NodeInfo, task: Optional[DistributedTask] = None) -> float:
        """Calculate comprehensive score for node selection.

        Lower score = better choice.

        Args:
            node: Node to score
            task: Task to be assigned (optional)

        Returns:
            Score value (lower is better)
        """
        # Base score from current load
        base_score = node.get_load_factor()

        # Get prediction
        prediction = self.predict_node_workload(node)

        # Weight components
        load_weight = 0.4
        prediction_weight = 0.3
        reliability_weight = 0.2
        speed_weight = 0.1

        # Load component
        load_score = base_score * load_weight

        # Prediction component
        prediction_score = prediction.predicted_load * prediction_weight

        # Reliability component (from metrics)
        if node.node_id in self.node_metrics:
            metrics = self.node_metrics[node.node_id]
            reliability_score = (1 - metrics.task_success_rate) * reliability_weight
        else:
            reliability_score = 0.0

        # Speed component (normalized completion time)
        if node.node_id in self.node_metrics:
            metrics = self.node_metrics[node.node_id]
            avg_time = metrics.get_average_completion_time()
            # Normalize against global average
            all_times = [
                m.get_average_completion_time()
                for m in self.node_metrics.values()
                if m.get_average_completion_time() > 0
            ]
            if all_times:
                global_avg = statistics.mean(all_times)
                if global_avg > 0:
                    speed_score = (avg_time / global_avg) * speed_weight
                else:
                    speed_score = 0.0
            else:
                speed_score = 0.0
        else:
            speed_score = 0.0

        total_score = load_score + prediction_score + reliability_score + speed_score

        logger.debug(
            f"Node {node.node_id} score: {total_score:.3f} "
            f"(load={load_score:.3f}, pred={prediction_score:.3f}, "
            f"rel={reliability_score:.3f}, speed={speed_score:.3f})"
        )

        return total_score

    def _select_least_loaded_node(self, available_nodes: List[NodeInfo]) -> NodeInfo:
        """Select the least loaded node from available nodes."""
        return min(available_nodes, key=lambda n: n.get_load_factor())

    def _select_round_robin_node(self, available_nodes: List[NodeInfo]) -> NodeInfo:
        """Select node using round-robin strategy."""
        node = available_nodes[self._round_robin_index % len(available_nodes)]
        self._round_robin_index += 1
        return node

    def select_node(
        self, nodes: List[NodeInfo], task: Optional[DistributedTask] = None
    ) -> Optional[NodeInfo]:
        """Select best node for task execution using ML prediction.

        Args:
            nodes: Available nodes
            task: Task to be assigned

        Returns:
            Selected node or None if no suitable node
        """
        available_nodes = self._filter_available_nodes(nodes)

        if not available_nodes:
            return None

        capable_nodes = self._filter_capable_nodes(available_nodes, task)

        return self._select_by_strategy(capable_nodes, task)

    def _filter_available_nodes(self, nodes: List[NodeInfo]) -> List[NodeInfo]:
        """Filter nodes that can accept tasks.

        Args:
            nodes: All nodes

        Returns:
            Nodes that can accept tasks
        """
        return [node for node in nodes if node.can_accept_task()]

    def _filter_capable_nodes(
        self, nodes: List[NodeInfo], task: Optional[DistributedTask]
    ) -> List[NodeInfo]:
        """Filter nodes by task capability.

        Args:
            nodes: Available nodes
            task: Task to be assigned

        Returns:
            Nodes capable of handling the task
        """
        if not task or not task.task_type:
            return nodes

        capable_nodes = [node for node in nodes if task.task_type in node.capabilities]
        return capable_nodes if capable_nodes else nodes

    def _select_by_strategy(
        self, nodes: List[NodeInfo], task: Optional[DistributedTask]
    ) -> Optional[NodeInfo]:
        """Select node based on configured strategy.

        Args:
            nodes: Available and capable nodes
            task: Task to be assigned

        Returns:
            Selected node
        """
        if self.strategy == "ml_predicted":
            return self._select_ml_predicted(nodes, task)
        elif self.strategy == "least_loaded":
            return self._select_least_loaded_node(nodes)
        elif self.strategy == "round_robin":
            return self._select_round_robin_node(nodes)
        elif self.strategy == "weighted_least_loaded":
            return self._select_weighted_least_loaded(nodes)
        else:
            return self._select_least_loaded_node(nodes)

    def _select_ml_predicted(
        self, nodes: List[NodeInfo], task: Optional[DistributedTask]
    ) -> Optional[NodeInfo]:
        """Select node using ML-based prediction.

        Args:
            nodes: Available nodes
            task: Task to be assigned

        Returns:
            Selected node
        """
        if len(self.task_history) >= self.min_samples_for_ml:
            # Enough data for ML prediction
            node_scores = [(node, self.calculate_node_score(node, task)) for node in nodes]
            return min(node_scores, key=lambda x: x[1])[0]
        else:
            # Not enough data - fall back to least loaded
            return self._select_least_loaded_node(nodes)

    def _select_weighted_least_loaded(self, nodes: List[NodeInfo]) -> Optional[NodeInfo]:
        """Select node using weighted least loaded strategy.

        Args:
            nodes: Available nodes

        Returns:
            Selected node
        """
        if not any(node.node_id in self.node_metrics for node in nodes):
            return self._select_least_loaded_node(nodes)

        best_node = None
        best_weighted_load = float("inf")

        for node in nodes:
            current_load = node.get_load_factor()
            weighted_load = self._calculate_weighted_load(node, current_load)

            if weighted_load < best_weighted_load:
                best_weighted_load = weighted_load
                best_node = node

        return best_node

    def _calculate_weighted_load(self, node: NodeInfo, current_load: float) -> float:
        """Calculate weighted load for a node.

        Args:
            node: Node to calculate for
            current_load: Current load factor

        Returns:
            Weighted load score
        """
        if node.node_id in self.node_metrics:
            metrics = self.node_metrics[node.node_id]
            # Weight by success rate (prefer reliable nodes)
            return current_load / max(0.1, metrics.task_success_rate)
        return current_load

    def get_cluster_predictions(self, nodes: List[NodeInfo]) -> Dict[str, WorkloadPrediction]:
        """Get workload predictions for all nodes.

        Args:
            nodes: List of cluster nodes

        Returns:
            Dictionary mapping node_id to prediction
        """
        return {node.node_id: self.predict_node_workload(node) for node in nodes}

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all tracked nodes.

        Returns:
            Summary statistics
        """
        if not self.node_metrics:
            return {
                "total_nodes": 0,
                "total_tasks": 0,
                "message": "No performance data available",
            }

        all_completion_times: list[float] = []
        all_success_rates = []

        for metrics in self.node_metrics.values():
            all_completion_times.extend(metrics.task_completion_times)
            all_success_rates.append(metrics.task_success_rate)

        return {
            "total_nodes": len(self.node_metrics),
            "total_tasks": len(self.task_history),
            "avg_completion_time": (
                statistics.mean(all_completion_times) if all_completion_times else 0.0
            ),
            "completion_time_std": (
                statistics.stdev(all_completion_times) if len(all_completion_times) > 1 else 0.0
            ),
            "avg_success_rate": (statistics.mean(all_success_rates) if all_success_rates else 0.0),
            "nodes": {
                node_id: {
                    "avg_completion_time": metrics.get_average_completion_time(),
                    "success_rate": metrics.task_success_rate,
                    "tasks_completed": metrics.success_count + metrics.failure_count,
                }
                for node_id, metrics in self.node_metrics.items()
            },
        }

    def optimize_strategy(self) -> str:
        """Automatically select best strategy based on cluster state.

        Returns:
            Recommended strategy name
        """
        if len(self.task_history) >= self.min_samples_for_ml:
            # Enough data for ML
            return "ml_predicted"
        elif len(self.task_history) >= 5:
            # Some data - use weighted
            return "weighted_least_loaded"
        else:
            # No data - use simple strategy
            return "least_loaded"
