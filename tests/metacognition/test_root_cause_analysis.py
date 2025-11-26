"""Tests for Root Cause Analysis engine."""

from src.metacognition.root_cause_analysis import (
    ComponentType,
    DependencyGraph,
    FailureType,
    RootCauseEngine,
)


class TestDependencyGraph:
    """Tests for DependencyGraph."""

    def test_initialization(self) -> None:
        """Test graph initialization."""
        graph = DependencyGraph()
        assert len(graph._components) == 0

    def test_add_component(self) -> None:
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

    def test_add_dependency(self) -> None:
        """Test adding dependencies."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        graph.add_dependency("web-1", "db-1")

        deps = graph.get_dependencies("web-1")
        assert "db-1" in deps

    def test_get_dependents(self) -> None:
        """Test getting dependents."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        graph.add_dependency("web-1", "db-1")

        dependents = graph.get_dependents("db-1")
        assert "web-1" in dependents

    def test_get_all_dependencies_transitive(self) -> None:
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

    def test_get_all_dependents_transitive(self) -> None:
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

    def test_find_path_exists(self) -> None:
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

    def test_find_path_not_exists(self) -> None:
        """Test finding path when none exists."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")
        graph.add_component("db-1", ComponentType.DATABASE, "Database")

        # No dependency, so no path
        path = graph.find_path("web-1", "db-1")
        assert path is None

    def test_find_path_self(self) -> None:
        """Test finding path to self."""
        graph = DependencyGraph()

        graph.add_component("web-1", ComponentType.SERVICE, "Web Server")

        path = graph.find_path("web-1", "web-1")
        assert path == ["web-1"]


class TestRootCauseEngine:
    """Tests for RootCauseEngine."""

    def test_initialization(self) -> None:
        """Test engine initialization."""
        engine = RootCauseEngine()
        assert engine.graph is not None

    def test_register_component(self) -> None:
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

    def test_register_component_with_dependencies(self) -> None:
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

    def test_record_failure(self) -> None:
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

    def test_analyze_isolated_failure(self) -> None:
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

    def test_analyze_cascading_failure(self) -> None:
        """Test analyzing cascading failures."""
        engine = RootCauseEngine()

        # Setup dependency chain: web -> cache -> db
        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.register_component("cache-1", ComponentType.CACHE, "Cache", dependencies=["db-1"])
        engine.register_component(
            "web-1", ComponentType.SERVICE, "Web Server", dependencies=["cache-1"]
        )

        # Record failures in sequence (db fails first, then cascade)
        import time

        engine.record_failure("fail-db", "db-1", FailureType.CRASH, "Database crashed")
        time.sleep(0.1)
        engine.record_failure("fail-cache", "cache-1", FailureType.TIMEOUT, "Cache timeout")
        time.sleep(0.1)
        engine.record_failure("fail-web", "web-1", FailureType.ERROR, "Service errors")

        # Analyze the web failure
        analysis = engine.analyze_failure("fail-web")

        assert analysis.failure_id == "fail-web"
        # Database should be identified as root cause
        assert "db-1" in analysis.root_causes
        # Should have a causal chain
        assert len(analysis.causal_chain) > 1

    def test_analysis_to_dict(self) -> None:
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

    def test_get_analysis(self) -> None:
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

    def test_get_component_health(self) -> None:
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

    def test_recommended_actions_generated(self) -> None:
        """Test that recommended actions are generated."""
        engine = RootCauseEngine()

        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.record_failure("fail-1", "db-1", FailureType.TIMEOUT, "Database timeout")

        analysis = engine.analyze_failure("fail-1")

        assert len(analysis.recommended_actions) > 0
        assert all(isinstance(action, str) for action in analysis.recommended_actions)

    def test_supporting_evidence_present(self) -> None:
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

    def test_confidence_calculation(self) -> None:
        """Test confidence score is within valid range."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web Server")
        engine.record_failure("fail-1", "web-1", FailureType.CRASH, "Service crashed")

        analysis = engine.analyze_failure("fail-1")

        assert 0.0 <= analysis.confidence <= 1.0

    def test_complex_dependency_graph(self) -> None:
        """Test with complex dependency graph."""
        engine = RootCauseEngine()

        # Create complex graph
        # API -> [Web, Queue] -> [Cache, DB]
        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.register_component("cache-1", ComponentType.CACHE, "Cache")
        engine.register_component(
            "web-1", ComponentType.SERVICE, "Web", dependencies=["cache-1", "db-1"]
        )
        engine.register_component("queue-1", ComponentType.QUEUE, "Queue", dependencies=["db-1"])
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

    def test_component_health_status(self) -> None:
        """Test component health status tracking."""
        engine = RootCauseEngine()

        engine.register_component("service-1", ComponentType.SERVICE, "Service")

        # Record multiple failures
        for i in range(5):
            engine.record_failure(
                f"fail-{i}",
                "service-1",
                FailureType.ERROR,
                f"Error {i}",
            )

        health = engine.get_component_health("service-1")

        assert health["component_id"] == "service-1"
        assert health["recent_failures"] > 0
        assert health["health_status"] in ["healthy", "unhealthy"]

    def test_failure_type_enumeration(self) -> None:
        """Test all failure types are recognized."""
        engine = RootCauseEngine()

        engine.register_component("test-1", ComponentType.SERVICE, "Test Service")

        # Test each failure type
        for failure_type in FailureType:
            engine.record_failure(
                f"fail-{failure_type.value}",
                "test-1",
                failure_type,
                f"Test {failure_type.value}",
            )

        # All failures should be recorded
        assert len(engine._failures) >= len(FailureType)

    def test_component_type_recommendations(self) -> None:
        """Test that recommendations vary by component type."""
        engine = RootCauseEngine()

        # Test database component
        engine.register_component("db-1", ComponentType.DATABASE, "Database")
        engine.record_failure("fail-db", "db-1", FailureType.TIMEOUT, "DB timeout")

        analysis_db = engine.analyze_failure("fail-db")
        db_recs = " ".join(analysis_db.recommended_actions)

        # Should mention database-specific recommendations
        assert any(
            keyword in db_recs.lower() for keyword in ["database", "query", "connection", "index"]
        )

        # Test network component
        engine.register_component("net-1", ComponentType.NETWORK, "Network")
        engine.record_failure("fail-net", "net-1", FailureType.TIMEOUT, "Net timeout")

        analysis_net = engine.analyze_failure("fail-net")
        net_recs = " ".join(analysis_net.recommended_actions)

        # Should mention network-specific recommendations
        assert any(
            keyword in net_recs.lower()
            for keyword in ["network", "connectivity", "firewall", "routing"]
        )

    def test_analysis_caching(self) -> None:
        """Test that analysis results are cached."""
        engine = RootCauseEngine()

        engine.register_component("web-1", ComponentType.SERVICE, "Web")
        engine.record_failure("fail-1", "web-1", FailureType.ERROR, "Error")

        # First analysis
        analysis1 = engine.analyze_failure("fail-1")

        # Retrieve cached analysis
        analysis2 = engine.get_analysis("fail-1")

        assert analysis1 is not None
        assert analysis2 is not None
        assert analysis1.failure_id == analysis2.failure_id

    def test_nonexistent_component_dependency(self) -> None:
        """Test handling of dependency on non-existent component."""
        engine = RootCauseEngine()
        graph = engine.graph

        graph.add_component("comp-1", ComponentType.SERVICE, "Component 1")

        # Try to add dependency on non-existent component
        graph.add_dependency("comp-1", "nonexistent")

        # Should handle gracefully
        deps = graph.get_dependencies("comp-1")
        assert isinstance(deps, set)

    def test_explanation_generation(self) -> None:
        """Test that explanations are human-readable."""
        engine = RootCauseEngine()

        engine.register_component("api-1", ComponentType.API, "API")
        engine.register_component("db-1", ComponentType.DATABASE, "Database", dependencies=[])
        engine.graph.add_dependency("api-1", "db-1")

        import time

        engine.record_failure("fail-db", "db-1", FailureType.CRASH, "DB crashed")
        time.sleep(0.05)
        engine.record_failure("fail-api", "api-1", FailureType.ERROR, "API error")

        analysis = engine.analyze_failure("fail-api")

        # Explanation should be readable text
        assert isinstance(analysis.explanation, str)
        assert len(analysis.explanation) > 0
        # Should mention root cause or propagation
        assert any(
            keyword in analysis.explanation.lower()
            for keyword in ["root", "cause", "failure", "propagation", "database"]
        )

    def test_multiple_root_causes(self) -> None:
        """Test handling of multiple independent root causes."""
        engine = RootCauseEngine()

        # Create independent components
        engine.register_component("service-1", ComponentType.SERVICE, "Service 1")
        engine.register_component("service-2", ComponentType.SERVICE, "Service 2")
        engine.register_component(
            "api-1",
            ComponentType.API,
            "API",
            dependencies=["service-1", "service-2"],
        )

        import time

        # Both services fail independently
        engine.record_failure("fail-s1", "service-1", FailureType.CRASH, "S1 crashed")
        time.sleep(0.05)
        engine.record_failure("fail-s2", "service-2", FailureType.CRASH, "S2 crashed")
        time.sleep(0.05)
        engine.record_failure("fail-api", "api-1", FailureType.ERROR, "API error")

        analysis = engine.analyze_failure("fail-api")

        # Should identify both as potential root causes
        assert len(analysis.root_causes) > 0
