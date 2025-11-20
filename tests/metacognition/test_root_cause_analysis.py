"""Tests for Root Cause Analysis engine."""

from datetime import datetime, timedelta
import pytest

from src.metacognition.root_cause_analysis import (
    ComponentType,
    DependencyGraph,
    FailureType,
    RootCauseEngine,
)


class TestDependencyGraph:
    """Tests for DependencyGraph."""

    def test_initialization(self):
        """Test graph initialization."""
        graph = DependencyGraph()
        assert len(graph._components) == 0

    def test_add_component(self):
        """Test adding components."""
        graph = DependencyGraph()

        comp = graph.add_component(
            "web-1",
            ComponentType.SERVICE,
            "Web Server",
        )

        assert comp.component_id == "web-1"
        assert comp.component_type == ComponentType.SERVICE
        assert comp.name == "Web Server"

    def test_add_dependency(self):
        """Test adding dependencies."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        graph.add_dependency("web-1", "db-1")

        deps = graph.get_dependencies("web-1")
        assert "db-1" in deps

    def test_get_dependents(self):
        """Test getting dependents."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        graph.add_dependency("web-1", "db-1")

        dependents = graph.get_dependents("db-1")
        assert "web-1" in dependents

    def test_get_all_dependencies_transitive(self):
        """Test getting transitive dependencies."""
        graph = DependencyGraph()

        # Create chain: web -> cache -> db
        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("cache-1", ComponentType.CACHE, "Cache")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        graph.add_dependency("web-1", "cache-1")
        graph.add_dependency("cache-1", "db-1")

        all_deps = graph.get_all_dependencies("web-1")
        assert "cache-1" in all_deps
        assert "db-1" in all_deps

    def test_get_all_dependents_transitive(self):
        """Test getting transitive dependents."""
        graph = DependencyGraph()

        # Create chain: web -> cache -> db
        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("cache-1", ComponentType.CACHE, "Cache")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        graph.add_dependency("web-1", "cache-1")
        graph.add_dependency("cache-1", "db-1")

        all_dependents = graph.get_all_dependents("db-1")
        assert "cache-1" in all_dependents
        assert "web-1" in all_dependents

    def test_find_path_exists(self):
        """Test finding path between components."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("cache-1", ComponentType.CACHE, "Cache")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        graph.add_dependency("web-1", "cache-1")
        graph.add_dependency("cache-1", "db-1")

        path = graph.find_path("web-1", "db-1")
        assert path is not None
        assert path == ["web-1", "cache-1", "db-1"]

    def test_find_path_not_exists(self):
        """Test finding path when none exists."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        # No dependency, so no path
        path = graph.find_path("web-1", "db-1")
        assert path is None

    def test_find_path_self(self):
        """Test finding path to self."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")

        path = graph.find_path("web-1", "web-1")
        assert path == ["web-1"]


class TestRootCauseEngine:
    """Tests for RootCauseEngine."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = RootCauseEngine()
        assert engine.graph is not None

    def test_register_component(self):
        """Test registering components."""
        engine = RootCauseEngine()

        engine.register_component(
            "web-1",
            ComponentType.SERVICE,
            "Web Server",
        )

        comp = engine.graph.get_component("web-1")
        assert comp is not None
        assert comp.name == "Web Server"

    def test_register_component_with_dependencies(self):
        """Test registering component with dependencies."""
        engine = RootCauseEngine()

        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.register_component(
            "web-1",
            ComponentType.SERVICE,
            "Web Server",
            dependencies=["db-1"],
        )

        deps = engine.graph.get_dependencies("web-1")
        assert "db-1" in deps

    def test_record_failure(self):
        """Test recording failures."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")

        failure = engine.record_failure(
            "fail-1",
            "web-1",
            FailureType.CRASH,
            "Service crashed unexpectedly",
        )

        assert failure.failure_id == "fail-1"
        assert failure.component_id == "web-1"
        assert failure.failure_type == FailureType.CRASH

    def test_analyze_isolated_failure(self):
        """Test analyzing isolated failure."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")

        engine.record_failure(
            "fail-1",
            "web-1",
            FailureType.CRASH,
            "Service crashed",
        )

        analysis = engine.analyze_failure("fail-1")

        assert analysis.failure_id == "fail-1"
        assert len(analysis.root_causes) > 0
        assert "web-1" in analysis.root_causes

    def test_analyze_cascading_failure(self):
        """Test analyzing cascading failures."""
        engine = RootCauseEngine()

        # Setup dependency chain: web -> cache -> db
        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.register_component(
            "cache-1", ComponentType.CACHE, "Cache", dependencies=["db-1"]
        )
        engine.register_component(
            "web-1", ComponentType.SERVICE, "Web Server", dependencies=["cache-1"]
        )

        # Record failures in sequence (db fails first, then cascade)
        import time

        engine.record_failure("fail-db", "db-1", FailureType.CRASH, "Database crashed")
        time.sleep(0.1)
        engine.record_failure(
            "fail-cache", "cache-1", FailureType.TIMEOUT, "Cache timeout"
        )
        time.sleep(0.1)
        engine.record_failure("fail-web", "web-1", FailureType.ERROR, "Service errors")

        # Analyze the web failure
        analysis = engine.analyze_failure("fail-web")

        assert analysis.failure_id == "fail-web"
        # Database should be identified as root cause
        assert "db-1" in analysis.root_causes
        # Should have a causal chain
        assert len(analysis.causal_chain) > 1

    def test_analysis_to_dict(self):
        """Test analysis serialization."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")
        engine.record_failure("fail-1", "web-1", FailureType.CRASH, "Service crashed")

        analysis = engine.analyze_failure("fail-1")
        analysis_dict = analysis.to_dict()

        assert "failure_id" in analysis_dict
        assert "root_causes" in analysis_dict
        assert "causal_chain" in analysis_dict
        assert "confidence" in analysis_dict
        assert "explanation" in analysis_dict
        assert "recommended_actions" in analysis_dict

    def test_get_analysis(self):
        """Test retrieving existing analysis."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")
        engine.record_failure("fail-1", "web-1", FailureType.CRASH, "Service crashed")

        # Analyze
        analysis1 = engine.analyze_failure("fail-1")

        # Retrieve
        analysis2 = engine.get_analysis("fail-1")

        assert analysis2 is not None
        assert analysis2.failure_id == analysis1.failure_id

    def test_get_component_health(self):
        """Test getting component health status."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")

        # Record some failures
        for i in range(3):
            engine.record_failure(
                f"fail-{i}",
                "web-1",
                FailureType.ERROR,
                f"Error {i}",
            )

        health = engine.get_component_health("web-1")

        assert health["component_id"] == "web-1"
        assert health["recent_failures"] == 3
        assert "health_status" in health

    def test_recommended_actions_generated(self):
        """Test that recommended actions are generated."""
        engine = RootCauseEngine()

        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.record_failure("fail-1", "db-1", FailureType.TIMEOUT, "Database timeout")

        analysis = engine.analyze_failure("fail-1")

        assert len(analysis.recommended_actions) > 0
        assert all(isinstance(action, str) for action in analysis.recommended_actions)

    def test_supporting_evidence_present(self):
        """Test that supporting evidence is collected."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")
        engine.record_failure(
            "fail-1",
            "web-1",
            FailureType.CRASH,
            "Service crashed",
            metrics={"cpu": 95.0, "memory": 98.0},
            symptoms=["high cpu", "memory leak"],
        )

        analysis = engine.analyze_failure("fail-1")

        assert len(analysis.supporting_evidence) > 0

    def test_confidence_calculation(self):
        """Test confidence score is within valid range."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")
        engine.record_failure("fail-1", "web-1", FailureType.CRASH, "Service crashed")

        analysis = engine.analyze_failure("fail-1")

        assert 0.0 <= analysis.confidence <= 1.0

    def test_complex_dependency_graph(self):
        """Test with complex dependency graph."""
        engine = RootCauseEngine()

        # Create complex graph
        # API -> [Web, Queue] -> [Cache, DB]
        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.register_component("cache-1", ComponentType.CACHE, "Cache")
        engine.register_component(
            "web-1", ComponentType.SERVICE, "Web", dependencies=["cache-1", "db-1"]
        )
        engine.register_component(
            "queue-1", ComponentType.QUEUE, "Queue", dependencies=["db-1"]
        )
        engine.register_component(
            "api-1", ComponentType.API, "API", dependencies=["web-1", "queue-1"]
        )

        # Record cascading failures
        import time

        engine.record_failure("fail-db", "db-1", FailureType.CRASH, "DB crashed")
        time.sleep(0.05)
        engine.record_failure("fail-web", "web-1", FailureType.TIMEOUT, "Web timeout")
        time.sleep(0.05)
        engine.record_failure("fail-api", "api-1", FailureType.ERROR, "API errors")

        analysis = engine.analyze_failure("fail-api")

        # Database should be root cause
        assert "db-1" in analysis.root_causes
        assert len(analysis.causal_chain) > 0
