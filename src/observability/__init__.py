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

"""Observability module for distributed tracing, metrics, and logging.

This module implements comprehensive observability features including:
- Distributed tracing with OpenTelemetry
- Custom metrics exporters for ML workloads
- Advanced log aggregation and analysis
- Continuous performance profiling

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 8
"""

from src.observability.distributed_tracing import (
    DistributedTracer,
    SpanContext,
    TraceConfig,
)
from src.observability.log_aggregator import (
    LogAggregator,
    LogAnalytics,
    LogConfig,
)
from src.observability.metrics_exporter import (
    CustomMetricsExporter,
    MetricsConfig,
    MLMetrics,
)
from src.observability.profiling_tools import (
    ContinuousProfiler,
    FlameGraphGenerator,
    ProfilingConfig,
)

__all__ = [
    # Distributed tracing
    "DistributedTracer",
    "SpanContext",
    "TraceConfig",
    # Metrics
    "CustomMetricsExporter",
    "MLMetrics",
    "MetricsConfig",
    # Logging
    "LogAggregator",
    "LogAnalytics",
    "LogConfig",
    # Profiling
    "ContinuousProfiler",
    "FlameGraphGenerator",
    "ProfilingConfig",
]
