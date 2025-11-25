#!/usr/bin/env python3
"""
Tests for enhanced audit trail features.
Tests compliance reporting, retention policies, alerting, and log analysis.
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.audit.compliance_reporter import ComplianceReporter
from src.audit.retention_policy import (
    RetentionPolicyManager,
    RetentionPeriod,
    DataCategory,
)
from src.audit.alerting_system import (
    AlertingSystem,
    Alert,
    AlertSeverity,
    AlertCategory,
)
from src.audit.log_analyzer import (
    AuditLogAnalyzer,
    QueryFilter,
)
from src.audit.immutable_audit import ImmutableAuditSystem


class TestComplianceReporter:
    """Test compliance reporting functionality."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            # Add some test events
            audit.log_action("test_action", {"data": "test1"}, "general")
            audit.log_action("user_data_access", {"user": "test"}, "security")
            audit.log_action("user_consent_granted", {"user": "test"}, "compliance")
            yield audit

    def test_compliance_reporter_initialization(self, temp_audit_system):
        """Test compliance reporter initialization."""
        reporter = ComplianceReporter(temp_audit_system)
        assert reporter.audit_system == temp_audit_system
        assert reporter.report_dir.exists()

    def test_generate_lgpd_report(self, temp_audit_system):
        """Test LGPD compliance report generation."""
        reporter = ComplianceReporter(temp_audit_system)
        report = reporter.generate_lgpd_report()

        assert report["standard"] == "LGPD"
        assert "report_id" in report
        assert "compliance_checks" in report
        assert "summary" in report

        # Check required LGPD checks
        assert "data_minimization" in report["compliance_checks"]
        assert "transparency" in report["compliance_checks"]
        assert "security" in report["compliance_checks"]
        assert "user_rights" in report["compliance_checks"]
        assert "consent" in report["compliance_checks"]
        assert "retention" in report["compliance_checks"]

        # Check summary
        assert "compliance_score" in report["summary"]
        assert "status" in report["summary"]
        assert 0 <= report["summary"]["compliance_score"] <= 100

    def test_generate_gdpr_report(self, temp_audit_system):
        """Test GDPR compliance report generation."""
        reporter = ComplianceReporter(temp_audit_system)
        report = reporter.generate_gdpr_report()

        assert report["standard"] == "GDPR"
        assert "compliance_checks" in report

        # Check GDPR-specific checks
        assert "lawfulness" in report["compliance_checks"]
        assert "purpose_limitation" in report["compliance_checks"]
        assert "accountability" in report["compliance_checks"]

    def test_export_audit_trail_json(self, temp_audit_system):
        """Test audit trail export in JSON format."""
        reporter = ComplianceReporter(temp_audit_system)
        export_path = reporter.export_audit_trail(format="json")

        assert Path(export_path).exists()
        assert export_path.endswith(".json")

        # Verify exported content
        with open(export_path, "r") as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0

    def test_export_audit_trail_csv(self, temp_audit_system):
        """Test audit trail export in CSV format."""
        reporter = ComplianceReporter(temp_audit_system)
        export_path = reporter.export_audit_trail(format="csv")

        assert Path(export_path).exists()
        assert export_path.endswith(".csv")

    def test_compliance_checks_valid_chain(self, temp_audit_system):
        """Test compliance checks with valid audit chain."""
        reporter = ComplianceReporter(temp_audit_system)

        # Verify chain integrity
        integrity = temp_audit_system.verify_chain_integrity()
        assert integrity["valid"]

        # Generate report
        report = reporter.generate_lgpd_report()

        # Security check should pass with valid chain
        assert report["compliance_checks"]["security"]["compliant"]


class TestRetentionPolicyManager:
    """Test data retention policy management."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    def test_retention_manager_initialization(self, temp_audit_system):
        """Test retention manager initialization."""
        manager = RetentionPolicyManager(temp_audit_system)
        assert manager.audit_system == temp_audit_system
        assert manager.archive_dir.exists()
        assert manager.config is not None

    def test_default_retention_policies(self, temp_audit_system):
        """Test default retention policies are set."""
        manager = RetentionPolicyManager(temp_audit_system)

        # Check default policies exist
        assert DataCategory.AUDIT_LOGS.value in manager.config["retention_policies"]
        assert DataCategory.SECURITY_EVENTS.value in manager.config["retention_policies"]

        # Verify reasonable defaults
        audit_retention = manager.get_retention_period(DataCategory.AUDIT_LOGS)
        assert audit_retention > 0  # Should have retention period

    def test_set_retention_period(self, temp_audit_system):
        """Test setting retention period."""
        manager = RetentionPolicyManager(temp_audit_system)

        manager.set_retention_period(DataCategory.USER_DATA, RetentionPeriod.DAYS_90)

        period = manager.get_retention_period(DataCategory.USER_DATA)
        assert period == RetentionPeriod.DAYS_90.value

    def test_archive_old_data_dry_run(self, temp_audit_system):
        """Test archive dry run (no actual archiving)."""
        manager = RetentionPolicyManager(temp_audit_system)

        result = manager.archive_old_data(DataCategory.AUDIT_LOGS, dry_run=True)

        assert result["action"] == "dry_run" or result["action"] == "skipped"
        if result["action"] == "dry_run":
            assert "files_to_archive" in result

    def test_generate_retention_report(self, temp_audit_system):
        """Test retention policy report generation."""
        manager = RetentionPolicyManager(temp_audit_system)
        report = manager.generate_retention_report()

        assert "generated_at" in report
        assert "policies" in report
        assert "statistics" in report

        # Check policies section
        assert len(report["policies"]) > 0

    def test_purge_requires_confirmation(self, temp_audit_system):
        """Test purge requires explicit confirmation."""
        manager = RetentionPolicyManager(temp_audit_system)

        # Without confirmation, should be blocked
        result = manager.purge_old_data(DataCategory.SYSTEM_METRICS, confirm=False)

        assert result["action"] == "blocked" or result["action"] == "skipped"


class TestAlertingSystem:
    """Test real-time alerting system."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    def test_alerting_system_initialization(self, temp_audit_system):
        """Test alerting system initialization."""
        alerting = AlertingSystem(temp_audit_system)
        assert alerting.audit_system == temp_audit_system
        assert alerting.alerts_dir.exists()

    def test_create_alert(self, temp_audit_system):
        """Test alert creation."""
        alerting = AlertingSystem(temp_audit_system)

        alert = alerting.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SECURITY,
            title="Test Alert",
            message="This is a test alert",
            details={"key": "value"},
        )

        assert alert.id is not None
        assert alert.severity == AlertSeverity.WARNING
        assert alert.category == AlertCategory.SECURITY
        assert alert.title == "Test Alert"
        assert not alert.acknowledged
        assert not alert.resolved

    def test_acknowledge_alert(self, temp_audit_system):
        """Test alert acknowledgment."""
        alerting = AlertingSystem(temp_audit_system)

        alert = alerting.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Test",
        )

        success = alerting.acknowledge_alert(alert.id)
        assert success

        # Verify alert is acknowledged
        assert alerting.active_alerts[alert.id].acknowledged

    def test_resolve_alert(self, temp_audit_system):
        """Test alert resolution."""
        alerting = AlertingSystem(temp_audit_system)

        alert = alerting.create_alert(
            severity=AlertSeverity.ERROR,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Test",
        )

        success = alerting.resolve_alert(alert.id, "Fixed the issue")
        assert success

        # Alert should be removed from active alerts
        assert alert.id not in alerting.active_alerts

    def test_get_active_alerts(self, temp_audit_system):
        """Test getting active alerts."""
        alerting = AlertingSystem(temp_audit_system)

        # Create alerts with different severities
        alerting.create_alert(
            AlertSeverity.INFO, AlertCategory.SYSTEM, "Info Alert", "Info message"
        )
        alerting.create_alert(
            AlertSeverity.CRITICAL,
            AlertCategory.SECURITY,
            "Critical Alert",
            "Critical message",
        )

        # Get all active alerts
        all_alerts = alerting.get_active_alerts()
        assert len(all_alerts) >= 2

        # Filter by severity
        critical_alerts = alerting.get_active_alerts(severity=AlertSeverity.CRITICAL)
        assert len(critical_alerts) >= 1
        assert all(a.severity == AlertSeverity.CRITICAL for a in critical_alerts)

        # Filter by category
        security_alerts = alerting.get_active_alerts(category=AlertCategory.SECURITY)
        assert all(a.category == AlertCategory.SECURITY for a in security_alerts)

    def test_get_statistics(self, temp_audit_system):
        """Test alert statistics."""
        alerting = AlertingSystem(temp_audit_system)

        # Create some alerts
        for i in range(3):
            alerting.create_alert(
                AlertSeverity.WARNING,
                AlertCategory.SYSTEM,
                f"Alert {i}",
                f"Message {i}",
            )

        stats = alerting.get_statistics()

        assert "total_alerts" in stats
        assert "active_alerts" in stats
        assert "by_severity" in stats
        assert "by_category" in stats
        assert stats["total_alerts"] >= 3

    def test_alert_subscription(self, temp_audit_system):
        """Test alert subscription mechanism."""
        alerting = AlertingSystem(temp_audit_system)
        received_alerts = []

        def callback(alert: Alert):
            received_alerts.append(alert)

        # Subscribe to alerts
        alerting.subscribe(callback)

        # Create an alert
        alerting.create_alert(AlertSeverity.INFO, AlertCategory.SYSTEM, "Test", "Test")

        # Callback should have been called
        assert len(received_alerts) == 1

        # Unsubscribe
        alerting.unsubscribe(callback)


class TestAuditLogAnalyzer:
    """Test audit log analysis functionality."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)

            # Add test events
            for i in range(10):
                audit.log_action(
                    f"action_{i % 3}",
                    {"index": i, "data": f"test{i}"},
                    f"category_{i % 2}",
                )

            yield audit

    def test_analyzer_initialization(self, temp_audit_system):
        """Test analyzer initialization."""
        analyzer = AuditLogAnalyzer(temp_audit_system)
        assert analyzer.audit_system == temp_audit_system

    def test_query_all_events(self, temp_audit_system):
        """Test querying all events."""
        analyzer = AuditLogAnalyzer(temp_audit_system)
        events = analyzer.query()

        assert len(events) >= 10  # Should have at least our test events

    def test_query_with_filter(self, temp_audit_system):
        """Test querying with filters."""
        analyzer = AuditLogAnalyzer(temp_audit_system)

        # Filter by category
        filter = QueryFilter(categories=["category_0"])
        events = analyzer.query(filter)

        assert all(e["category"] == "category_0" for e in events)

    def test_query_with_date_range(self, temp_audit_system):
        """Test querying with date range."""
        analyzer = AuditLogAnalyzer(temp_audit_system)

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)

        filter = QueryFilter(start_date=start_date, end_date=end_date)
        events = analyzer.query(filter)

        # All events should be within range
        for event in events:
            event_time = datetime.fromisoformat(event["datetime_utc"])
            assert start_date <= event_time <= end_date

    def test_detect_patterns(self, temp_audit_system):
        """Test pattern detection."""
        analyzer = AuditLogAnalyzer(temp_audit_system)
        patterns = analyzer.detect_patterns(time_window_hours=24)

        assert "total_events" in patterns
        assert "frequent_actions" in patterns
        assert "frequent_categories" in patterns
        assert patterns["total_events"] >= 10

    def test_generate_statistics(self, temp_audit_system):
        """Test statistics generation."""
        analyzer = AuditLogAnalyzer(temp_audit_system)
        stats = analyzer.generate_statistics()

        assert "total_events" in stats
        assert "actions" in stats
        assert "categories" in stats
        assert stats["total_events"] >= 10

        # Check action statistics
        assert "total_unique" in stats["actions"]
        assert "most_common" in stats["actions"]

    def test_forensic_search(self, temp_audit_system):
        """Test forensic search functionality."""
        analyzer = AuditLogAnalyzer(temp_audit_system)

        # Search for specific term
        results = analyzer.forensic_search("action_0", context_events=2)

        assert len(results) > 0
        for result in results:
            assert "matched_event" in result
            assert "context_before" in result
            assert "context_after" in result

    def test_get_event_timeline(self, temp_audit_system):
        """Test event timeline retrieval."""
        analyzer = AuditLogAnalyzer(temp_audit_system)

        timeline = analyzer.get_event_timeline(limit=5)

        assert len(timeline) <= 5
        # Timeline should be sorted by timestamp (newest first)
        if len(timeline) > 1:
            for i in range(len(timeline) - 1):
                time1 = timeline[i]["datetime_utc"]
                time2 = timeline[i + 1]["datetime_utc"]
                assert time1 >= time2


class TestIntegration:
    """Integration tests for all audit enhancements."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    def test_full_compliance_workflow(self, temp_audit_system):
        """Test complete compliance workflow."""
        # 1. Create events
        temp_audit_system.log_action("user_data_access", {"user": "test"}, "compliance")
        temp_audit_system.log_action("data_exported", {"format": "json"}, "compliance")

        # 2. Generate compliance report
        reporter = ComplianceReporter(temp_audit_system)
        report = reporter.generate_lgpd_report()
        assert report["summary"]["compliance_score"] >= 0

        # 3. Check retention policy
        manager = RetentionPolicyManager(temp_audit_system)
        retention_report = manager.generate_retention_report()
        assert "policies" in retention_report

        # 4. Analyze logs
        analyzer = AuditLogAnalyzer(temp_audit_system)
        stats = analyzer.generate_statistics()
        assert stats["total_events"] >= 2

    def test_alert_on_compliance_issue(self, temp_audit_system):
        """Test alerting on compliance issues."""
        alerting = AlertingSystem(temp_audit_system)

        # Simulate compliance issue
        alert = alerting.create_alert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.COMPLIANCE,
            title="LGPD Violation Detected",
            message="Unauthorized data access",
            details={"user": "test", "data_type": "pii"},
        )

        # Verify alert was created
        assert alert.id in alerting.active_alerts
        assert alert.severity == AlertSeverity.CRITICAL

        # Check statistics
        stats = alerting.get_statistics()
        assert stats["critical_active"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
