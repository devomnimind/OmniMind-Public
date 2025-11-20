"""
Intelligent Decision Trees for Autonomous Decision Making.

This module implements advanced decision tree structures that can:
- Learn from experience
- Adapt to changing conditions
- Integrate with ethical frameworks
- Provide explainable decisions

Author: OmniMind Project
License: MIT
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

logger = structlog.get_logger(__name__)


class DecisionCriterion(Enum):
    """Types of criteria for decision making."""

    THRESHOLD = "threshold"  # Numerical threshold comparison
    CATEGORY = "category"  # Categorical matching
    PROBABILITY = "probability"  # Probabilistic selection
    UTILITY = "utility"  # Utility maximization
    ETHICAL = "ethical"  # Ethics-based decision
    LEARNED = "learned"  # ML-learned criterion


@dataclass
class DecisionOutcome:
    """Represents the outcome of a decision."""

    action: str
    confidence: float
    explanation: str
    path: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Validate outcome data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class DecisionNode:
    """A node in the decision tree."""

    node_id: str
    criterion_type: DecisionCriterion
    question: str
    threshold: Optional[float] = None
    categories: Optional[Set[str]] = None
    children: Dict[str, "DecisionNode"] = field(default_factory=dict)
    action: Optional[str] = None  # Leaf nodes have actions
    confidence: float = 1.0
    learned_weights: Dict[str, float] = field(default_factory=dict)
    visit_count: int = 0
    success_count: int = 0

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.action is not None

    def update_statistics(self, success: bool) -> None:
        """Update node statistics based on outcome."""
        self.visit_count += 1
        if success:
            self.success_count += 1
        # Update confidence based on success rate
        if self.visit_count > 0:
            self.confidence = self.success_count / self.visit_count

    def get_success_rate(self) -> float:
        """Get the success rate of this node."""
        if self.visit_count == 0:
            return 0.5  # Neutral prior
        return self.success_count / self.visit_count


class DecisionTree:
    """
    Intelligent decision tree with learning capabilities.

    Features:
    - Adaptive thresholds based on experience
    - Integration with ethical frameworks
    - Explainable decision paths
    - Online learning from outcomes
    """

    def __init__(
        self,
        root: DecisionNode,
        name: str = "decision_tree",
        learning_rate: float = 0.1,
        enable_adaptation: bool = True,
    ):
        """
        Initialize decision tree.

        Args:
            root: Root node of the tree
            name: Name of the decision tree
            learning_rate: Rate of adaptation (0-1)
            enable_adaptation: Whether to adapt based on feedback
        """
        self.root = root
        self.name = name
        self.learning_rate = learning_rate
        self.enable_adaptation = enable_adaptation
        self.decision_history: List[Tuple[DecisionOutcome, bool]] = []
        self.logger = logger.bind(tree_name=name)

    def decide(self, context: Dict[str, Any]) -> DecisionOutcome:
        """
        Make a decision based on current context.

        Args:
            context: Dictionary containing decision context

        Returns:
            DecisionOutcome with action and explanation
        """
        path: List[str] = []
        current_node = self.root
        explanation_parts: List[str] = []

        self.logger.info("starting_decision", context_keys=list(context.keys()))

        while not current_node.is_leaf():
            path.append(current_node.node_id)
            current_node.visit_count += 1

            # Evaluate criterion
            next_key = self._evaluate_criterion(current_node, context)
            explanation_parts.append(f"{current_node.question} -> {next_key}")

            if next_key not in current_node.children:
                # Default to first child if key not found
                next_key = list(current_node.children.keys())[0]
                self.logger.warning(
                    "criterion_key_not_found",
                    node=current_node.node_id,
                    key=next_key,
                )

            current_node = current_node.children[next_key]

        # Reached leaf node
        path.append(current_node.node_id)
        current_node.visit_count += 1

        outcome = DecisionOutcome(
            action=current_node.action or "no_action",
            confidence=current_node.confidence,
            explanation=" | ".join(explanation_parts),
            path=path,
            metadata={"context": context},
        )

        self.logger.info(
            "decision_made",
            action=outcome.action,
            confidence=outcome.confidence,
            path_length=len(path),
        )

        return outcome

    def _evaluate_criterion(self, node: DecisionNode, context: Dict[str, Any]) -> str:
        """Evaluate node criterion and return next branch key."""
        if node.criterion_type == DecisionCriterion.THRESHOLD:
            return self._evaluate_threshold(node, context)
        elif node.criterion_type == DecisionCriterion.CATEGORY:
            return self._evaluate_category(node, context)
        elif node.criterion_type == DecisionCriterion.PROBABILITY:
            return self._evaluate_probability(node, context)
        elif node.criterion_type == DecisionCriterion.UTILITY:
            return self._evaluate_utility(node, context)
        elif node.criterion_type == DecisionCriterion.ETHICAL:
            return self._evaluate_ethical(node, context)
        elif node.criterion_type == DecisionCriterion.LEARNED:
            return self._evaluate_learned(node, context)
        else:
            # Default to first child
            return list(node.children.keys())[0]

    def _evaluate_threshold(self, node: DecisionNode, context: Dict[str, Any]) -> str:
        """Evaluate threshold-based criterion."""
        # Extract value from context (simplified)
        value = context.get("value", 0.5)
        threshold = node.threshold or 0.5

        if value >= threshold:
            return "high"
        else:
            return "low"

    def _evaluate_category(self, node: DecisionNode, context: Dict[str, Any]) -> str:
        """Evaluate category-based criterion."""
        category = str(context.get("category", "unknown"))
        if node.categories and category in node.categories:
            return category
        return "unknown"

    def _evaluate_probability(self, node: DecisionNode, context: Dict[str, Any]) -> str:
        """Evaluate probabilistic criterion."""
        import random

        probability = context.get("probability", 0.5)
        if random.random() < probability:
            return "yes"
        else:
            return "no"

    def _evaluate_utility(self, node: DecisionNode, context: Dict[str, Any]) -> str:
        """Evaluate utility-based criterion."""
        utilities = context.get("utilities", {})
        if not utilities:
            return list(node.children.keys())[0]

        # Select child with highest utility
        max_utility = -float("inf")
        best_child = list(node.children.keys())[0]

        for child_key in node.children:
            utility = utilities.get(child_key, 0)
            if utility > max_utility:
                max_utility = utility
                best_child = child_key

        return best_child

    def _evaluate_ethical(self, node: DecisionNode, context: Dict[str, Any]) -> str:
        """Evaluate ethics-based criterion."""
        ethical_score = context.get("ethical_score", 0.5)
        if ethical_score >= 0.7:
            return "ethical"
        elif ethical_score >= 0.4:
            return "neutral"
        else:
            return "unethical"

    def _evaluate_learned(self, node: DecisionNode, context: Dict[str, Any]) -> str:
        """Evaluate learned criterion using weights."""
        if not node.learned_weights:
            return list(node.children.keys())[0]

        # Compute weighted sum
        score = 0.0
        for key, value in context.items():
            if isinstance(value, (int, float)):
                weight = node.learned_weights.get(key, 0.0)
                score += weight * value

        # Map score to child
        if score >= 0.5:
            return "high"
        else:
            return "low"

    def provide_feedback(self, outcome: DecisionOutcome, success: bool) -> None:
        """
        Provide feedback to improve decision making.

        Args:
            outcome: The decision outcome
            success: Whether the decision was successful
        """
        self.decision_history.append((outcome, success))

        if not self.enable_adaptation:
            return

        # Update statistics for nodes in the path
        current = self.root
        for node_id in outcome.path:
            if current.node_id == node_id:
                current.update_statistics(success)

            # Find child matching next node_id
            for child in current.children.values():
                if child.node_id == node_id:
                    current = child
                    break

        self.logger.info(
            "feedback_processed",
            success=success,
            path_length=len(outcome.path),
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the tree."""
        total_decisions = len(self.decision_history)
        if total_decisions == 0:
            return {
                "total_decisions": 0,
                "success_rate": 0.0,
                "average_confidence": 0.0,
            }

        successful_decisions = sum(1 for _, success in self.decision_history if success)
        avg_confidence = (
            sum(outcome.confidence for outcome, _ in self.decision_history)
            / total_decisions
        )

        return {
            "total_decisions": total_decisions,
            "success_rate": successful_decisions / total_decisions,
            "average_confidence": avg_confidence,
            "tree_depth": self._calculate_depth(self.root),
            "total_nodes": self._count_nodes(self.root),
        }

    def _calculate_depth(self, node: DecisionNode, current_depth: int = 0) -> int:
        """Calculate tree depth."""
        if node.is_leaf():
            return current_depth

        max_child_depth = current_depth
        for child in node.children.values():
            child_depth = self._calculate_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _count_nodes(self, node: DecisionNode) -> int:
        """Count total nodes in tree."""
        count = 1
        for child in node.children.values():
            count += self._count_nodes(child)
        return count


class DecisionTreeBuilder:
    """Builder for creating decision trees."""

    def __init__(self, name: str = "decision_tree"):
        """Initialize builder."""
        self.name = name
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_id: Optional[str] = None

    def add_node(
        self,
        node_id: str,
        criterion_type: DecisionCriterion,
        question: str,
        threshold: Optional[float] = None,
        categories: Optional[Set[str]] = None,
        action: Optional[str] = None,
    ) -> "DecisionTreeBuilder":
        """Add a node to the tree."""
        node = DecisionNode(
            node_id=node_id,
            criterion_type=criterion_type,
            question=question,
            threshold=threshold,
            categories=categories,
            action=action,
        )
        self.nodes[node_id] = node

        if self.root_id is None:
            self.root_id = node_id

        return self

    def add_edge(
        self, parent_id: str, child_id: str, edge_label: str
    ) -> "DecisionTreeBuilder":
        """Add an edge between nodes."""
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node {parent_id} not found")
        if child_id not in self.nodes:
            raise ValueError(f"Child node {child_id} not found")

        parent = self.nodes[parent_id]
        child = self.nodes[child_id]
        parent.children[edge_label] = child

        return self

    def build(
        self,
        learning_rate: float = 0.1,
        enable_adaptation: bool = True,
    ) -> DecisionTree:
        """Build the decision tree."""
        if self.root_id is None:
            raise ValueError("No root node defined")

        root = self.nodes[self.root_id]
        return DecisionTree(
            root=root,
            name=self.name,
            learning_rate=learning_rate,
            enable_adaptation=enable_adaptation,
        )
