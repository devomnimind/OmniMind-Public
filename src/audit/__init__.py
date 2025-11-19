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

from .immutable_audit import (
    ImmutableAuditSystem,
    get_audit_system,
    log_action,
)
from .compliance_reporter import (
    ComplianceReporter,
    ComplianceStandard,
    generate_lgpd_report,
    generate_gdpr_report,
    export_audit_trail,
)
from .retention_policy import (
    RetentionPolicyManager,
    RetentionPeriod,
    DataCategory,
    set_retention_period,
    archive_old_data,
    generate_retention_report,
)
from .alerting_system import (
    AlertingSystem,
    Alert,
    AlertSeverity,
    AlertCategory,
    get_alerting_system,
    create_alert,
    get_active_alerts,
)
from .log_analyzer import (
    AuditLogAnalyzer,
    QueryFilter,
    query_audit_logs,
    detect_patterns,
    generate_statistics,
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
