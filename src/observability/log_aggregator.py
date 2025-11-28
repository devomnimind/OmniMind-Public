"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""Log Aggregation and Analysis Module.

Implements advanced log aggregation, analysis, and alerting with ELK stack compatibility.
Provides structured logging, pattern detection, and anomaly identification.

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 8.3
"""

import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple

import structlog

logger = structlog.get_logger(__name__)


class LogLevel(Enum):
    """Log severity levels."""

    TRACE = 10
    DEBUG = 20
    INFO = 30
    WARNING = 40
    ERROR = 50
    CRITICAL = 60


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry.

    Attributes:
        timestamp: When the log was created
        level: Log severity level
        message: Log message
        logger_name: Name of the logger
        module: Module that created the log
        function: Function that created the log
        line: Line number
        extra: Additional structured data
    """

    timestamp: float
    level: LogLevel
    message: str
    logger_name: str = ""
    module: str = ""
    function: str = ""
    line: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "level": self.level.name,
            "message": self.message,
            "logger": self.logger_name,
            "module": self.module,
            "function": self.function,
            "line": self.line,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create from dictionary."""
        return cls(
            timestamp=data.get("timestamp", time.time()),
            level=LogLevel[data.get("level", "INFO")],
            message=data.get("message", ""),
            logger_name=data.get("logger", ""),
            module=data.get("module", ""),
            function=data.get("function", ""),
            line=data.get("line", 0),
            extra=data.get("extra", {}),
        )


@dataclass
class LogPattern:
    """Represents a log pattern for detection.

    Attributes:
        name: Pattern name
        regex: Regular expression pattern
        severity: Alert severity if pattern matches
        description: Description of what this pattern detects
        action: Optional action to take when pattern matches
    """

    name: str
    regex: str
    severity: AlertSeverity
    description: str
    action: Optional[str] = None
    _compiled: Optional[Pattern[str]] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Compile the regex pattern."""
        self._compiled = re.compile(self.regex, re.IGNORECASE)

    def matches(self, message: str) -> bool:
        """Check if the pattern matches a log message.

        Args:
            message: Log message to check

        Returns:
            True if pattern matches
        """
        if self._compiled is None:
            self._compiled = re.compile(self.regex, re.IGNORECASE)
        return bool(self._compiled.search(message))


@dataclass
class LogAlert:
    """Represents a log-based alert.

    Attributes:
        timestamp: When the alert was created
        pattern_name: Name of the pattern that triggered
        severity: Alert severity
        message: Alert message
        log_entries: Log entries that triggered the alert
        metadata: Additional metadata
    """

    timestamp: float
    pattern_name: str
    severity: AlertSeverity
    message: str
    log_entries: List[LogEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "pattern": self.pattern_name,
            "severity": self.severity.value,
            "message": self.message,
            "log_count": len(self.log_entries),
            "logs": [log.to_dict() for log in self.log_entries],
            "metadata": self.metadata,
        }


@dataclass
class LogConfig:
    """Configuration for log aggregation.

    Attributes:
        enabled: Whether log aggregation is enabled
        log_level: Minimum log level to aggregate
        max_log_entries: Maximum log entries to keep in memory
        retention_hours: How long to keep logs
        enable_pattern_detection: Enable pattern-based alerting
        enable_anomaly_detection: Enable anomaly detection
        aggregation_interval_seconds: Interval for log aggregation
    """

    enabled: bool = True
    log_level: LogLevel = LogLevel.INFO
    max_log_entries: int = 10000
    retention_hours: int = 24
    enable_pattern_detection: bool = True
    enable_anomaly_detection: bool = True
    aggregation_interval_seconds: int = 60


class LogAnalytics:
    """Log analytics and insights.

    Provides statistical analysis and insights from aggregated logs.
    """

    def __init__(self, log_entries: List[LogEntry]):
        """Initialize analytics with log entries.

        Args:
            log_entries: List of log entries to analyze
        """
        self.log_entries = log_entries

    def get_level_distribution(self) -> Dict[str, int]:
        """Get distribution of log levels.

        Returns:
            Dictionary mapping level name to count
        """
        counter = Counter(entry.level.name for entry in self.log_entries)
        return dict(counter)

    def get_top_loggers(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top loggers by volume.

        Args:
            limit: Maximum number of loggers to return

        Returns:
            List of (logger_name, count) tuples
        """
        counter = Counter(entry.logger_name for entry in self.log_entries)
        return counter.most_common(limit)

    def get_error_rate(self, window_seconds: int = 3600) -> float:
        """Calculate error rate in the specified time window.

        Args:
            window_seconds: Time window in seconds

        Returns:
            Error rate (errors per second)
        """
        cutoff_time = time.time() - window_seconds
        errors = sum(
            1
            for entry in self.log_entries
            if entry.timestamp >= cutoff_time and entry.level in (LogLevel.ERROR, LogLevel.CRITICAL)
        )

        if window_seconds > 0:
            return errors / window_seconds
        return 0.0

    def get_timeline(self, bucket_size_seconds: int = 300) -> Dict[str, List[int]]:
        """Get log timeline bucketed by time.

        Args:
            bucket_size_seconds: Size of each time bucket

        Returns:
            Dictionary mapping level to list of counts per bucket
        """
        if not self.log_entries:
            return {}

        # Find time range
        min_time = min(entry.timestamp for entry in self.log_entries)
        max_time = max(entry.timestamp for entry in self.log_entries)

        # Create buckets
        num_buckets = int((max_time - min_time) / bucket_size_seconds) + 1
        timeline: Dict[str, List[int]] = defaultdict(lambda: [0] * num_buckets)

        # Fill buckets
        for entry in self.log_entries:
            bucket_idx = int((entry.timestamp - min_time) / bucket_size_seconds)
            timeline[entry.level.name][bucket_idx] += 1

        return dict(timeline)

    def find_anomalies(self, threshold: float = 2.0) -> List[str]:
        """Find anomalous patterns in logs.

        Uses simple statistical methods to find unusual log patterns.

        Args:
            threshold: Z-score threshold for anomaly detection

        Returns:
            List of anomalous patterns detected
        """
        anomalies = []

        # Analyze message patterns (first word)
        message_starts = [
            entry.message.split()[0] if entry.message else "" for entry in self.log_entries
        ]
        counter = Counter(message_starts)

        if counter:
            # Calculate mean and stddev
            counts = list(counter.values())
            mean = sum(counts) / len(counts)
            variance = sum((x - mean) ** 2 for x in counts) / len(counts)
            stddev = variance**0.5

            # Find outliers
            for pattern, count in counter.items():
                if stddev > 0:
                    z_score = abs((count - mean) / stddev)
                    if z_score > threshold:
                        anomalies.append(f"Unusual frequency of '{pattern}': {count} occurrences")

        return anomalies

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary.

        Returns:
            Dictionary with analytics summary
        """
        return {
            "total_logs": len(self.log_entries),
            "level_distribution": self.get_level_distribution(),
            "top_loggers": self.get_top_loggers(),
            "error_rate_per_second": self.get_error_rate(),
            "anomalies": self.find_anomalies(),
        }


class LogAggregator:
    """Log aggregation and analysis system.

    Provides centralized log collection, pattern detection, and alerting
    with ELK stack compatibility.

    Example:
        >>> config = LogConfig()
        >>> aggregator = LogAggregator(config)
        >>> aggregator.add_pattern(LogPattern(
        ...     name="error_detection",
        ...     regex=r"error|exception|failed",
        ...     severity=AlertSeverity.HIGH,
        ...     description="Detects error messages"
        ... ))
        >>> aggregator.log(LogLevel.ERROR, "Operation failed")
        >>> alerts = aggregator.get_alerts()
    """

    def __init__(self, config: LogConfig):
        """Initialize the log aggregator.

        Args:
            config: Log aggregation configuration
        """
        self.config = config
        self._log_entries: List[LogEntry] = []
        self._patterns: List[LogPattern] = []
        self._alerts: List[LogAlert] = []
        self._logs_dir = Path.home() / ".omnimind" / "logs" / "aggregated"
        self._logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize default patterns
        if config.enable_pattern_detection:
            self._initialize_default_patterns()

        logger.info(
            "log_aggregator_initialized",
            log_level=config.log_level.name,
            pattern_detection=config.enable_pattern_detection,
        )

    def _initialize_default_patterns(self) -> None:
        """Initialize default log patterns for common issues."""
        default_patterns = [
            LogPattern(
                name="critical_error",
                regex=r"critical|fatal|panic",
                severity=AlertSeverity.CRITICAL,
                description="Critical system errors",
            ),
            LogPattern(
                name="authentication_failure",
                regex=r"authentication failed|login failed|unauthorized",
                severity=AlertSeverity.HIGH,
                description="Authentication failures",
            ),
            LogPattern(
                name="memory_pressure",
                regex=r"out of memory|memory exhausted|oom",
                severity=AlertSeverity.HIGH,
                description="Memory pressure issues",
            ),
            LogPattern(
                name="connection_error",
                regex=r"connection refused|connection timeout|connection lost",
                severity=AlertSeverity.MEDIUM,
                description="Connection issues",
            ),
            LogPattern(
                name="performance_degradation",
                regex=r"slow query|timeout|performance|degraded",
                severity=AlertSeverity.MEDIUM,
                description="Performance issues",
            ),
        ]

        for pattern in default_patterns:
            self.add_pattern(pattern)

    def add_pattern(self, pattern: LogPattern) -> None:
        """Add a log pattern for detection.

        Args:
            pattern: Log pattern to add
        """
        self._patterns.append(pattern)
        logger.debug("pattern_added", name=pattern.name, severity=pattern.severity.value)

    def log(
        self,
        level: LogLevel,
        message: str,
        logger_name: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a log entry.

        Args:
            level: Log level
            message: Log message
            logger_name: Logger name
            extra: Additional structured data
        """
        if not self.config.enabled:
            return

        if level.value < self.config.log_level.value:
            return

        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            logger_name=logger_name,
            extra=extra or {},
        )

        self._log_entries.append(entry)

        # Check patterns
        if self.config.enable_pattern_detection:
            self._check_patterns(entry)

        # Cleanup old entries
        self._cleanup_old_logs()

    def _check_patterns(self, entry: LogEntry) -> None:
        """Check log entry against registered patterns.

        Args:
            entry: Log entry to check
        """
        for pattern in self._patterns:
            if pattern.matches(entry.message):
                alert = LogAlert(
                    timestamp=entry.timestamp,
                    pattern_name=pattern.name,
                    severity=pattern.severity,
                    message=f"Pattern '{pattern.name}' detected: {pattern.description}",
                    log_entries=[entry],
                    metadata={"pattern_regex": pattern.regex},
                )
                self._alerts.append(alert)

                logger.warning(
                    "log_pattern_detected",
                    pattern=pattern.name,
                    severity=pattern.severity.value,
                    message=entry.message,
                )

    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """Get aggregated logs.

        Args:
            level: Filter by log level (None for all)
            limit: Maximum number of logs to return (None for all)

        Returns:
            List of log entries
        """
        logs = self._log_entries

        if level is not None:
            logs = [log for log in logs if log.level == level]

        if limit is not None:
            logs = logs[-limit:]

        return logs

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
    ) -> List[LogAlert]:
        """Get triggered alerts.

        Args:
            severity: Filter by severity (None for all)

        Returns:
            List of alerts
        """
        alerts = self._alerts

        if severity is not None:
            alerts = [alert for alert in alerts if alert.severity == severity]

        return alerts

    def analyze(self) -> LogAnalytics:
        """Create analytics instance for current logs.

        Returns:
            LogAnalytics instance
        """
        return LogAnalytics(self._log_entries)

    def export_logs(self, format: str = "json") -> str:
        """Export logs in specified format.

        Args:
            format: Export format (json or elasticsearch)

        Returns:
            Formatted logs string
        """
        if format == "json":
            data = {
                "timestamp": datetime.now().isoformat(),
                "log_count": len(self._log_entries),
                "logs": [log.to_dict() for log in self._log_entries],
            }
            return json.dumps(data, indent=2)
        elif format == "elasticsearch":
            # Elasticsearch bulk format
            lines = []
            for log in self._log_entries:
                # Index metadata
                lines.append(
                    json.dumps(
                        {
                            "index": {
                                "_index": "omnimind-logs",
                                "_type": "_doc",
                            }
                        }
                    )
                )
                # Document
                lines.append(json.dumps(log.to_dict()))
            return "\n".join(lines)
        else:
            raise ValueError(f"Unknown format: {format}")

    def save_logs(self) -> None:
        """Save aggregated logs to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._logs_dir / f"logs_{timestamp}.json"

        with open(filename, "w") as f:
            f.write(self.export_logs("json"))

        logger.info("logs_saved", filename=str(filename), count=len(self._log_entries))

    def _cleanup_old_logs(self) -> None:
        """Remove logs older than retention period."""
        if len(self._log_entries) > self.config.max_log_entries:
            # Remove oldest entries
            self._log_entries = self._log_entries[-self.config.max_log_entries :]

        # Remove by time
        cutoff_time = time.time() - (self.config.retention_hours * 3600)
        self._log_entries = [log for log in self._log_entries if log.timestamp >= cutoff_time]

        # Cleanup alerts
        self._alerts = [alert for alert in self._alerts if alert.timestamp >= cutoff_time]

    def clear_logs(self) -> None:
        """Clear all aggregated logs and alerts."""
        self._log_entries.clear()
        self._alerts.clear()
        logger.info("logs_cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics.

        Returns:
            Dictionary with statistics
        """
        analytics = self.analyze()
        return {
            "total_logs": len(self._log_entries),
            "total_alerts": len(self._alerts),
            "patterns_registered": len(self._patterns),
            "analytics": analytics.get_summary(),
        }
