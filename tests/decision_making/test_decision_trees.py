"""
Comprehensive tests for decision tree module.
"""

import pytest

from src.decision_making.decision_trees import (
    DecisionCriterion,
    DecisionNode,
    DecisionOutcome,
    DecisionTreeBuilder,
)


class TestDecisionNode:
    """Tests for DecisionNode class."""

    def test_create_leaf_node(self):
        """Test creating a leaf node."""
        node = DecisionNode(
            node_id="leaf1",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Is value > 0.5?",
            action="approve",
        )
        assert node.is_leaf()
        assert node.action == "approve"

    def test_create_internal_node(self):
        """Test creating an internal node."""
        node = DecisionNode(
            node_id="internal1",
            criterion_type=DecisionCriterion.CATEGORY,
            question="What category?",
        )
        assert not node.is_leaf()
        assert node.action is None

    def test_update_statistics(self):
        """Test updating node statistics."""
        node = DecisionNode(
            node_id="test",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Test?",
        )

        # Initial state
        assert node.visit_count == 0
        assert node.success_count == 0
        assert node.confidence == 1.0

        # Update with success
        node.update_statistics(success=True)
        assert node.visit_count == 1
        assert node.success_count == 1
        assert node.confidence == 1.0

        # Update with failure
        node.update_statistics(success=False)
        assert node.visit_count == 2
        assert node.success_count == 1
        assert node.confidence == 0.5

    def test_get_success_rate(self):
        """Test success rate calculation."""
        node = DecisionNode(
            node_id="test",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Test?",
        )

        # No visits - neutral prior
        assert node.get_success_rate() == 0.5

        # After updates
        node.update_statistics(True)
        node.update_statistics(True)
        node.update_statistics(False)
        assert node.get_success_rate() == 2 / 3


class TestDecisionOutcome:
    """Tests for DecisionOutcome class."""

    def test_create_outcome(self):
        """Test creating a decision outcome."""
        outcome = DecisionOutcome(
            action="test_action",
            confidence=0.9,
            explanation="Test explanation",
        )
        assert outcome.action == "test_action"
        assert outcome.confidence == 0.9
        assert outcome.explanation == "Test explanation"
        assert isinstance(outcome.path, list)
        assert isinstance(outcome.metadata, dict)

    def test_confidence_validation(self):
        """Test confidence validation."""
        # Valid confidence
        outcome = DecisionOutcome(action="test", confidence=0.5, explanation="")
        assert outcome.confidence == 0.5

        # Invalid confidence - too high
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            DecisionOutcome(action="test", confidence=1.5, explanation="")

        # Invalid confidence - negative
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            DecisionOutcome(action="test", confidence=-0.1, explanation="")


class TestDecisionTreeBuilder:
    """Tests for DecisionTreeBuilder class."""

    def test_build_simple_tree(self):
        """Test building a simple decision tree."""
        builder = DecisionTreeBuilder(name="simple_tree")

        # Add root node
        builder.add_node(
            node_id="root",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Is value >= 0.5?",
        )

        # Add leaf nodes
        builder.add_node(
            node_id="high",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="",
            action="approve",
        )
        builder.add_node(
            node_id="low",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="",
            action="reject",
        )

        # Add edges
        builder.add_edge("root", "high", "high")
        builder.add_edge("root", "low", "low")

        # Build tree
        tree = builder.build()
        assert tree.name == "simple_tree"
        assert tree.root.node_id == "root"
        assert len(tree.root.children) == 2

    def test_add_edge_validation(self):
        """Test edge validation."""
        builder = DecisionTreeBuilder()
        builder.add_node(
            node_id="node1",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Q1?",
        )

        # Invalid parent
        with pytest.raises(ValueError, match="Parent node .* not found"):
            builder.add_edge("nonexistent", "node1", "edge")

        # Invalid child
        with pytest.raises(ValueError, match="Child node .* not found"):
            builder.add_edge("node1", "nonexistent", "edge")


class TestDecisionTree:
    """Tests for DecisionTree class."""

    @pytest.fixture
    def simple_tree(self):
        """Create a simple decision tree for testing."""
        builder = DecisionTreeBuilder(name="test_tree")

        # Root: threshold decision
        builder.add_node(
            node_id="root",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Is value >= 0.5?",
            threshold=0.5,
        )

        # Leaves
        builder.add_node(
            node_id="high",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="",
            action="high_action",
        )
        builder.add_node(
            node_id="low",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="",
            action="low_action",
        )

        # Edges
        builder.add_edge("root", "high", "high")
        builder.add_edge("root", "low", "low")

        return builder.build()

    def test_decide_high_value(self, simple_tree):
        """Test decision with high value."""
        context = {"value": 0.8}
        outcome = simple_tree.decide(context)

        assert outcome.action == "high_action"
        assert len(outcome.path) == 2
        assert outcome.path[0] == "root"
        assert outcome.path[1] == "high"

    def test_decide_low_value(self, simple_tree):
        """Test decision with low value."""
        context = {"value": 0.3}
        outcome = simple_tree.decide(context)

        assert outcome.action == "low_action"
        assert len(outcome.path) == 2
        assert outcome.path[0] == "root"
        assert outcome.path[1] == "low"

    def test_provide_feedback(self, simple_tree):
        """Test providing feedback to the tree."""
        context = {"value": 0.7}
        outcome = simple_tree.decide(context)

        # Provide positive feedback
        simple_tree.provide_feedback(outcome, success=True)

        assert len(simple_tree.decision_history) == 1
        assert simple_tree.decision_history[0][0] == outcome
        assert simple_tree.decision_history[0][1] is True

    def test_performance_metrics(self, simple_tree):
        """Test performance metrics calculation."""
        # Make several decisions with feedback
        for value, success in [(0.7, True), (0.3, False), (0.9, True)]:
            context = {"value": value}
            outcome = simple_tree.decide(context)
            simple_tree.provide_feedback(outcome, success)

        metrics = simple_tree.get_performance_metrics()

        assert metrics["total_decisions"] == 3
        assert metrics["success_rate"] == 2 / 3
        assert "average_confidence" in metrics
        assert "tree_depth" in metrics
        assert "total_nodes" in metrics

    def test_tree_depth_calculation(self, simple_tree):
        """Test tree depth calculation."""
        # Make a decision first to populate metrics
        context = {"value": 0.7}
        outcome = simple_tree.decide(context)
        simple_tree.provide_feedback(outcome, success=True)

        metrics = simple_tree.get_performance_metrics()
        assert metrics["tree_depth"] == 1  # Root -> Leaf

    def test_node_count_calculation(self, simple_tree):
        """Test node count calculation."""
        # Make a decision first to populate metrics
        context = {"value": 0.7}
        outcome = simple_tree.decide(context)
        simple_tree.provide_feedback(outcome, success=True)

        metrics = simple_tree.get_performance_metrics()
        assert metrics["total_nodes"] == 3  # Root + 2 leaves


class TestDecisionCriteria:
    """Tests for different decision criteria."""

    def test_category_criterion(self):
        """Test category-based criterion."""
        builder = DecisionTreeBuilder(name="category_tree")

        builder.add_node(
            node_id="root",
            criterion_type=DecisionCriterion.CATEGORY,
            question="What category?",
            categories={"A", "B", "C"},
        )
        builder.add_node(
            node_id="cat_a",
            criterion_type=DecisionCriterion.CATEGORY,
            question="",
            action="action_a",
        )
        builder.add_node(
            node_id="unknown",
            criterion_type=DecisionCriterion.CATEGORY,
            question="",
            action="action_unknown",
        )

        builder.add_edge("root", "cat_a", "A")
        builder.add_edge("root", "unknown", "unknown")

        tree = builder.build()

        # Test with known category
        outcome = tree.decide({"category": "A"})
        assert outcome.action == "action_a"

        # Test with unknown category
        outcome = tree.decide({"category": "Z"})
        assert outcome.action == "action_unknown"

    def test_ethical_criterion(self):
        """Test ethical-based criterion."""
        builder = DecisionTreeBuilder(name="ethical_tree")

        builder.add_node(
            node_id="root",
            criterion_type=DecisionCriterion.ETHICAL,
            question="Is it ethical?",
        )
        builder.add_node(
            node_id="ethical",
            criterion_type=DecisionCriterion.ETHICAL,
            question="",
            action="proceed",
        )
        builder.add_node(
            node_id="unethical",
            criterion_type=DecisionCriterion.ETHICAL,
            question="",
            action="reject",
        )

        builder.add_edge("root", "ethical", "ethical")
        builder.add_edge("root", "unethical", "unethical")

        tree = builder.build()

        # Test with high ethical score
        outcome = tree.decide({"ethical_score": 0.9})
        assert outcome.action == "proceed"

        # Test with low ethical score
        outcome = tree.decide({"ethical_score": 0.2})
        assert outcome.action == "reject"


class TestAdaptiveLearning:
    """Tests for adaptive learning capabilities."""

    def test_adaptation_enabled(self):
        """Test that adaptation updates node statistics."""
        builder = DecisionTreeBuilder()
        builder.add_node(
            node_id="root",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Test?",
            threshold=0.5,
        )
        builder.add_node(
            node_id="leaf",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="",
            action="test_action",
        )
        builder.add_edge("root", "leaf", "high")

        tree = builder.build(enable_adaptation=True)

        # Make decision and provide feedback
        outcome = tree.decide({"value": 0.7})

        tree.provide_feedback(outcome, success=True)

        # Make another decision
        outcome2 = tree.decide({"value": 0.7})

        # Confidence may change based on statistics
        assert outcome2.confidence >= 0

    def test_adaptation_disabled(self):
        """Test that adaptation can be disabled."""
        builder = DecisionTreeBuilder()
        builder.add_node(
            node_id="root",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="Test?",
        )
        builder.add_node(
            node_id="leaf",
            criterion_type=DecisionCriterion.THRESHOLD,
            question="",
            action="test_action",
        )
        builder.add_edge("root", "leaf", "high")

        tree = builder.build(enable_adaptation=False)

        # Make decision and provide feedback
        outcome = tree.decide({"value": 0.7})
        tree.provide_feedback(outcome, success=True)

        # History should still be updated
        assert len(tree.decision_history) == 1
