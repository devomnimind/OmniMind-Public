"""
Módulo de auditoria para OmniMind.
Implementa sistema de auditoria imutável com hash chain para garantir integridade.

Features:
- Immutable audit logs with blockchain-style verification
- Automated compliance reporting (LGPD, GDPR, SOC2)
- Data retention policies and automated archival
- Real-time alerting system
- Advanced audit log analysis and pattern detection
"""

from .alerting_system import (
    Alert,
    AlertCategory,
    AlertingSystem,
    AlertSeverity,
    create_alert,
    get_active_alerts,
    get_alerting_system,
)
from .compliance_reporter import (
    ComplianceReporter,
    ComplianceStandard,
    export_audit_trail,
    generate_gdpr_report,
    generate_lgpd_report,
)
from .immutable_audit import (
    ImmutableAuditSystem,
    get_audit_system,
    log_action,
)
from .log_analyzer import (
    AuditLogAnalyzer,
    QueryFilter,
    detect_patterns,
    generate_statistics,
    query_audit_logs,
)
from .retention_policy import (
    DataCategory,
    RetentionPeriod,
    RetentionPolicyManager,
    archive_old_data,
    generate_retention_report,
    set_retention_period,
)

__all__ = [
    # Core audit system
    "ImmutableAuditSystem",
    "get_audit_system",
    "log_action",
    # Compliance reporting
    "ComplianceReporter",
    "ComplianceStandard",
    "generate_lgpd_report",
    "generate_gdpr_report",
    "export_audit_trail",
    # Data retention
    "RetentionPolicyManager",
    "RetentionPeriod",
    "DataCategory",
    "set_retention_period",
    "archive_old_data",
    "generate_retention_report",
    # Real-time alerting
    "AlertingSystem",
    "Alert",
    "AlertSeverity",
    "AlertCategory",
    "get_alerting_system",
    "create_alert",
    "get_active_alerts",
    # Log analysis
    "AuditLogAnalyzer",
    "QueryFilter",
    "query_audit_logs",
    "detect_patterns",
    "generate_statistics",
]
