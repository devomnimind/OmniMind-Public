#!/usr/bin/env python3
"""
Audit Log Analysis Module for OmniMind
Provides query interface, pattern detection, and statistical analysis of audit logs.

Features:
- Powerful query interface for audit logs
- Pattern and anomaly detection
- Statistical analysis and reporting
- Forensic investigation tools
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .immutable_audit import ImmutableAuditSystem


@dataclass
class QueryFilter:
    """Filter criteria for audit log queries."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    categories: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    regex_pattern: Optional[str] = None
    min_severity: Optional[str] = None


class AuditLogAnalyzer:
    """
    Audit log analysis and query system.

    Features:
    - Flexible query interface
    - Pattern detection
    - Anomaly detection
    - Statistical analysis
    - Forensic tools
    """

    def __init__(self, audit_system: Optional[ImmutableAuditSystem] = None):
        """
        Initialize audit log analyzer.

        Args:
            audit_system: Optional audit system instance
        """
        self.audit_system = audit_system or ImmutableAuditSystem()

    def query(
        self,
        filter: Optional[QueryFilter] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs with flexible filtering.

        Args:
            filter: Optional query filter
            limit: Maximum number of results to return

        Returns:
            List of matching audit events
        """
        events = []
        filter = filter or QueryFilter()

        if not self.audit_system.audit_log_file.exists():
            return events

        try:
            with open(self.audit_system.audit_log_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)

                        # Apply filters
                        if not self._matches_filter(event, filter):
                            continue

                        events.append(event)

                        # Check limit
                        if limit and len(events) >= limit:
                            break

                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

        return events

    def _matches_filter(self, event: Dict[str, Any], filter: QueryFilter) -> bool:
        """Check if event matches filter criteria."""
        # Date range filter
        if filter.start_date or filter.end_date:
            try:
                event_time = datetime.fromisoformat(event.get("datetime_utc", ""))

                if filter.start_date and event_time < filter.start_date:
                    return False
                if filter.end_date and event_time > filter.end_date:
                    return False
            except ValueError:
                return False

        # Category filter
        if filter.categories:
            if event.get("category") not in filter.categories:
                return False

        # Action filter
        if filter.actions:
            if event.get("action") not in filter.actions:
                return False

        # Regex pattern filter
        if filter.regex_pattern:
            pattern = re.compile(filter.regex_pattern, re.IGNORECASE)
            event_str = json.dumps(event)
            if not pattern.search(event_str):
                return False

        return True

    def detect_patterns(
        self,
        time_window_hours: int = 24,
        min_frequency: int = 5,
    ) -> Dict[str, Any]:
        """
        Detect patterns in audit logs.

        Args:
            time_window_hours: Time window for pattern detection
            min_frequency: Minimum frequency to report a pattern

        Returns:
            Dict containing detected patterns
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)

        events = self.query(QueryFilter(start_date=cutoff_time))

        # Analyze patterns
        action_frequency = Counter()
        category_frequency = Counter()
        action_sequences = []
        user_actions = defaultdict(list)

        for event in events:
            action = event.get("action", "unknown")
            category = event.get("category", "unknown")

            action_frequency[action] += 1
            category_frequency[category] += 1
            action_sequences.append(action)

            # Track user-specific patterns if available
            user = event.get("details", {}).get("user")
            if user:
                user_actions[user].append(action)

        # Detect repeated sequences
        sequence_patterns = self._detect_sequences(action_sequences)

        # Detect anomalies
        anomalies = self._detect_anomalies(events)

        return {
            "time_window_hours": time_window_hours,
            "total_events": len(events),
            "frequent_actions": [
                {"action": action, "count": count}
                for action, count in action_frequency.most_common(10)
                if count >= min_frequency
            ],
            "frequent_categories": [
                {"category": cat, "count": count}
                for cat, count in category_frequency.most_common(10)
            ],
            "sequence_patterns": sequence_patterns,
            "anomalies": anomalies,
            "user_patterns": {
                user: {
                    "action_count": len(actions),
                    "unique_actions": len(set(actions)),
                    "most_common": Counter(actions).most_common(3),
                }
                for user, actions in user_actions.items()
            },
        }

    def _detect_sequences(
        self, actions: List[str], min_length: int = 3
    ) -> List[Dict[str, Any]]:
        """Detect repeated action sequences."""
        sequences = []
        n = len(actions)

        # Simple n-gram detection
        for length in range(min_length, min(6, n + 1)):
            sequence_counts = Counter()

            for i in range(n - length + 1):
                sequence = tuple(actions[i : i + length])
                sequence_counts[sequence] += 1

            # Report sequences that repeat
            for sequence, count in sequence_counts.items():
                if count >= 2:
                    sequences.append(
                        {
                            "sequence": list(sequence),
                            "length": length,
                            "count": count,
                        }
                    )

        return sorted(sequences, key=lambda x: x["count"], reverse=True)[:10]

    def _detect_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in events."""
        anomalies = []

        # Check for unusual time gaps
        timestamps = [
            datetime.fromisoformat(e.get("datetime_utc", ""))
            for e in events
            if e.get("datetime_utc")
        ]

        if len(timestamps) >= 2:
            timestamps.sort()
            time_gaps = [
                (timestamps[i + 1] - timestamps[i]).total_seconds()
                for i in range(len(timestamps) - 1)
            ]

            # Calculate mean and std dev
            import statistics

            if len(time_gaps) > 1:
                mean_gap = statistics.mean(time_gaps)
                stdev_gap = statistics.stdev(time_gaps)

                # Anomaly: gaps significantly larger than average
                for i, gap in enumerate(time_gaps):
                    if gap > mean_gap + 3 * stdev_gap:
                        anomalies.append(
                            {
                                "type": "unusual_time_gap",
                                "gap_seconds": gap,
                                "mean_gap": mean_gap,
                                "stdev": stdev_gap,
                                "timestamp": timestamps[i].isoformat(),
                            }
                        )

        # Check for rapid repeated actions
        action_times = defaultdict(list)
        for event in events:
            action = event.get("action")
            timestamp = event.get("datetime_utc")
            if action and timestamp:
                action_times[action].append(datetime.fromisoformat(timestamp))

        for action, times in action_times.items():
            if len(times) >= 10:
                times.sort()
                # Check if 10+ actions in 1 minute
                for i in range(len(times) - 9):
                    time_span = (times[i + 9] - times[i]).total_seconds()
                    if time_span < 60:
                        anomalies.append(
                            {
                                "type": "rapid_repeated_action",
                                "action": action,
                                "count": 10,
                                "time_span_seconds": time_span,
                                "timestamp": times[i].isoformat(),
                            }
                        )
                        break

        return anomalies

    def generate_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive statistics from audit logs.

        Args:
            start_date: Start date for analysis (defaults to 30 days ago)
            end_date: End date for analysis (defaults to now)

        Returns:
            Dict containing statistical analysis
        """
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        events = self.query(QueryFilter(start_date=start_date, end_date=end_date))

        if not events:
            return {
                "message": "No events in specified time range",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }

        # Calculate statistics
        action_counts = Counter(e.get("action") for e in events)
        category_counts = Counter(e.get("category") for e in events)

        # Time distribution
        time_distribution = defaultdict(int)
        for event in events:
            try:
                timestamp = datetime.fromisoformat(event.get("datetime_utc", ""))
                hour_bucket = timestamp.hour
                time_distribution[hour_bucket] += 1
            except ValueError:
                pass

        # Day of week distribution
        day_distribution = defaultdict(int)
        for event in events:
            try:
                timestamp = datetime.fromisoformat(event.get("datetime_utc", ""))
                day_name = timestamp.strftime("%A")
                day_distribution[day_name] += 1
            except ValueError:
                pass

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_events": len(events),
            "actions": {
                "total_unique": len(action_counts),
                "most_common": action_counts.most_common(10),
                "distribution": dict(action_counts),
            },
            "categories": {
                "total_unique": len(category_counts),
                "most_common": category_counts.most_common(10),
                "distribution": dict(category_counts),
            },
            "time_distribution": {
                "by_hour": dict(sorted(time_distribution.items())),
                "by_day": dict(day_distribution),
            },
            "events_per_day": len(events) / max(1, (end_date - start_date).days),
        }

    def forensic_search(
        self,
        search_term: str,
        context_events: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search audit logs for forensic investigation.

        Args:
            search_term: Term to search for (supports regex)
            context_events: Number of context events before/after match

        Returns:
            List of matches with context
        """
        all_events = self.query()
        matches = []

        pattern = re.compile(search_term, re.IGNORECASE)

        for i, event in enumerate(all_events):
            event_str = json.dumps(event)

            if pattern.search(event_str):
                # Get context
                start_idx = max(0, i - context_events)
                end_idx = min(len(all_events), i + context_events + 1)
                context = all_events[start_idx:end_idx]

                matches.append(
                    {
                        "match_index": i,
                        "matched_event": event,
                        "context_before": context[:context_events],
                        "context_after": context[context_events + 1 :],
                    }
                )

        return matches

    def get_event_timeline(
        self,
        action: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get chronological timeline of events.

        Args:
            action: Optional action filter
            category: Optional category filter
            limit: Maximum events to return

        Returns:
            Chronologically sorted events
        """
        filter = QueryFilter()
        if action:
            filter.actions = [action]
        if category:
            filter.categories = [category]

        events = self.query(filter, limit=limit)

        # Sort by timestamp
        events.sort(
            key=lambda e: e.get("datetime_utc", ""),
            reverse=True,
        )

        return events


# Convenience functions


def query_audit_logs(
    filter: Optional[QueryFilter] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Query audit logs."""
    analyzer = AuditLogAnalyzer()
    return analyzer.query(filter, limit)


def detect_patterns(time_window_hours: int = 24) -> Dict[str, Any]:
    """Detect patterns in recent audit logs."""
    analyzer = AuditLogAnalyzer()
    return analyzer.detect_patterns(time_window_hours)


def generate_statistics() -> Dict[str, Any]:
    """Generate audit log statistics."""
    analyzer = AuditLogAnalyzer()
    return analyzer.generate_statistics()
