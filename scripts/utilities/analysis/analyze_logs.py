#!/usr/bin/env python3
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

"""
Log Analysis Script for OmniMind

This script analyzes log files to detect anomalies, bugs, and performance issues
that may not be caught by unit tests. It provides automated detection of:

- Error patterns and frequencies
- Performance anomalies (high CPU/memory usage)
- Silent failures (exceptions not properly handled)
- Resource state transitions
- Task execution failures

Usage:
    python scripts/analyze_logs.py [log_directory] [--output report.json]

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
Date: 2025-11-24
"""

import argparse
import json
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd


class LogAnalyzer:
    """Analyzes OmniMind log files for anomalies and bugs."""

    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.patterns = {
            "error": re.compile(r"ERROR|CRITICAL|FATAL", re.IGNORECASE),
            "warning": re.compile(r"WARNING|WARN", re.IGNORECASE),
            "exception": re.compile(r"Exception|Traceback|Error:", re.IGNORECASE),
            "resource_state": re.compile(
                r"Resource state (changed|OPTIMAL|GOOD|WARNING|CRITICAL|EMERGENCY)",
                re.IGNORECASE,
            ),
            "cpu_usage": re.compile(r"CPU[=:](\d+\.?\d*)%"),
            "memory_usage": re.compile(r"Memory[=:](\d+\.?\d*)%"),
            "task_failure": re.compile(r"task.*fail|fail.*task", re.IGNORECASE),
            "throttling": re.compile(r"throttl|emergency.*throttle", re.IGNORECASE),
            "phi_output": re.compile(
                r"phi.*0|phi.*output", re.IGNORECASE
            ),  # Special case for phi-0 detection
            # Entropy warnings - detecta quando entropia excede limites
            "entropy_warning": re.compile(
                r"entropy.*exceeds.*bekenstein.*bound|entropy.*warning|WARNING.*entropy|entropy.*threshold.*exceeded",
                re.IGNORECASE
            ),
            # Meta cognition failures - CRÍTICO: não executar testes
            "metacognition_failure": re.compile(
                r"meta.*cogn.*(?:analysis|action).*failed|metacognition.*(?:analysis|action).*failed|failed.*load.*hash.*chain",
                re.IGNORECASE
            ),
            # Insufficient history - dados insuficientes para cálculos
            "insufficient_history": re.compile(
                r"insufficient.*history|history.*insufficient|insufficient.*data|insufficient.*aligned.*history|insufficient.*valid.*causal.*predictions",
                re.IGNORECASE
            ),
            # Padrões numéricos de insufficient history (ex: "4<10", "7<70")
            "insufficient_history_numeric": re.compile(
                r"(\d+)\s*<\s*(\d+).*insufficient|insufficient.*\((\d+)\s*<\s*(\d+)\)|insufficient.*history.*\((\d+)\s*<\s*(\d+)\)",
                re.IGNORECASE
            ),
        }

    def analyze_logs(self) -> Dict[str, Any]:
        """Main analysis function."""
        if not self.log_dir.exists():
            return {"error": f"Log directory {self.log_dir} does not exist"}

        log_files = list(self.log_dir.glob("*.log")) + list(self.log_dir.glob("*.log.*"))
        if not log_files:
            return {"warning": f"No log files found in {self.log_dir}"}

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "log_directory": str(self.log_dir),
            "files_analyzed": len(log_files),
            "total_lines": 0,
            "anomalies": {},
            "patterns": {},
            "performance": {},
            "recommendations": [],
        }

        for log_file in log_files:
            file_analysis = self._analyze_single_file(log_file)
            analysis["total_lines"] += file_analysis["lines"]

            # Merge patterns
            for pattern_name, matches in file_analysis["patterns"].items():
                if pattern_name not in analysis["patterns"]:
                    analysis["patterns"][pattern_name] = []
                analysis["patterns"][pattern_name].extend(matches)

        # Analyze patterns for anomalies
        analysis["anomalies"] = self._detect_anomalies(analysis["patterns"])
        analysis["performance"] = self._analyze_performance(analysis["patterns"])
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _analyze_single_file(self, log_file: Path) -> Dict[str, Any]:
        """Analyze a single log file."""
        patterns_found = defaultdict(list)

        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            return {
                "error": f"Failed to read {log_file}: {e}",
                "lines": 0,
                "patterns": {},
            }

        for line_num, line in enumerate(lines, 1):
            timestamp_match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)
            timestamp = timestamp_match.group(0) if timestamp_match else "unknown"

            for pattern_name, pattern in self.patterns.items():
                matches = pattern.findall(line)
                if matches:
                    patterns_found[pattern_name].append(
                        {
                            "file": str(log_file.name),
                            "line": line_num,
                            "timestamp": timestamp,
                            "content": line.strip(),
                            "matches": matches,
                        }
                    )

        return {"lines": len(lines), "patterns": dict(patterns_found)}

    def _detect_anomalies(self, patterns: Dict[str, List]) -> Dict[str, Any]:
        """Detect anomalies in log patterns."""
        anomalies = {}

        # High error frequency
        if "error" in patterns and len(patterns["error"]) > 10:
            anomalies["high_error_rate"] = {
                "count": len(patterns["error"]),
                "severity": "HIGH" if len(patterns["error"]) > 50 else "MEDIUM",
                "description": f"Detected {len(patterns['error'])} error entries",
            }

        # Exception patterns
        if "exception" in patterns:
            exception_types = Counter()
            for exc in patterns["exception"]:
                # Extract exception type from content
                exc_match = re.search(r"(\w+Error|\w+Exception)", exc["content"])
                if exc_match:
                    exception_types[exc_match.group(1)] += 1

            if exception_types:
                anomalies["exception_patterns"] = {
                    "types": dict(exception_types.most_common(5)),
                    "total": len(patterns["exception"]),
                    "severity": "HIGH" if len(patterns["exception"]) > 20 else "MEDIUM",
                }

        # Resource state transitions
        if "resource_state" in patterns:
            state_changes = [
                p for p in patterns["resource_state"] if "changed" in p["content"].lower()
            ]
            if len(state_changes) > 50:  # Frequent state changes indicate instability
                anomalies["resource_instability"] = {
                    "state_changes": len(state_changes),
                    "severity": "MEDIUM",
                    "description": "Frequent resource state changes detected",
                }

        # Task failures
        if "task_failure" in patterns:
            anomalies["task_failures"] = {
                "count": len(patterns["task_failure"]),
                "severity": "HIGH",
                "description": f"Detected {len(patterns['task_failure'])} task failures",
            }

        # Phi-0 outputs (special case)
        if "phi_output" in patterns:
            anomalies["phi_zero_detection"] = {
                "count": len(patterns["phi_output"]),
                "severity": "INFO",
                "description": "Phi-0 outputs detected - potential silent bugs",
            }

        return anomalies

    def _analyze_performance(self, patterns: Dict[str, List]) -> Dict[str, Any]:
        """Analyze performance metrics from logs."""
        performance = {}

        # CPU usage analysis
        if "cpu_usage" in patterns:
            cpu_values = []
            for pattern in patterns["cpu_usage"]:
                for match in pattern["matches"]:
                    try:
                        cpu_values.append(float(match))
                    except ValueError:
                        continue

            if cpu_values:
                performance["cpu"] = {
                    "average": sum(cpu_values) / len(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values),
                    "high_usage_count": len([v for v in cpu_values if v > 90]),
                }

        # Memory usage analysis
        if "memory_usage" in patterns:
            mem_values = []
            for pattern in patterns["memory_usage"]:
                for match in pattern["matches"]:
                    try:
                        mem_values.append(float(match))
                    except ValueError:
                        continue

            if mem_values:
                performance["memory"] = {
                    "average": sum(mem_values) / len(mem_values),
                    "max": max(mem_values),
                    "min": min(mem_values),
                    "high_usage_count": len([v for v in mem_values if v > 90]),
                }

        return performance

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        anomalies = analysis.get("anomalies", {})

        if "high_error_rate" in anomalies:
            recommendations.append(
                "🔴 HIGH PRIORITY: Investigate high error rate - check error patterns and root causes"
            )

        if "exception_patterns" in anomalies:
            exc_types = anomalies["exception_patterns"]["types"]
            recommendations.append(
                f"🟡 MEDIUM PRIORITY: Review exception handling for: {', '.join(list(exc_types.keys())[:3])}"
            )

        if "resource_instability" in anomalies:
            recommendations.append(
                "🟡 MEDIUM PRIORITY: Optimize resource management to reduce state transitions"
            )

        if "task_failures" in anomalies:
            recommendations.append(
                "🔴 HIGH PRIORITY: Debug task execution failures in orchestrator"
            )

        if "phi_zero_detection" in anomalies:
            recommendations.append("🔵 INFO: Phi-0 outputs detected - enhance silent bug detection")

        if "entropy_warnings" in anomalies:
            recommendations.append(
                "🟡 MEDIUM PRIORITY: Monitor entropy warnings - entropy exceeds Bekenstein bound"
            )

        if "metacognition_failures" in anomalies:
            recommendations.append(
                "🔴 CRITICAL: Meta cognition failures detected - NÃO EXECUTAR TESTES até resolver"
            )

        performance = analysis.get("performance", {})
        if "cpu" in performance and performance["cpu"]["high_usage_count"] > 10:
            recommendations.append("🟡 MEDIUM PRIORITY: Investigate CPU usage spikes")

        if "memory" in performance and performance["memory"]["high_usage_count"] > 10:
            recommendations.append("🟡 MEDIUM PRIORITY: Investigate memory usage spikes")

        if not recommendations:
            recommendations.append("✅ No critical issues detected - continue monitoring")

        return recommendations


def main():
    parser = argparse.ArgumentParser(description="Analyze OmniMind log files for anomalies")
    parser.add_argument("log_directory", help="Directory containing log files")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for JSON report",
        default="log_analysis_report.json",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    analyzer = LogAnalyzer(args.log_directory)
    analysis = analyzer.analyze_logs()

    # Save JSON report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    if args.verbose:
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    else:
        print(f"Analysis complete. Report saved to {args.output}")
        print(f"Files analyzed: {analysis.get('files_analyzed', 0)}")
        print(f"Total lines: {analysis.get('total_lines', 0)}")
        print(f"Anomalies detected: {len(analysis.get('anomalies', {}))}")

        recommendations = analysis.get("recommendations", [])
        if recommendations:
            print("\n📋 Recommendations:")
            for rec in recommendations:
                print(f"  {rec}")


if __name__ == "__main__":
    main()
