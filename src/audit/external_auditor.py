import json
import os
import sys
from datetime import datetime, timedelta

# Configuration
LOG_DIR = "data/long_term_logs"
METRICS_FILE = os.path.join(LOG_DIR, "omnimind_metrics.jsonl")
REPORT_FILE = os.path.join(LOG_DIR, "audit_report_latest.md")


class ExternalAuditor:
    def __init__(self):
        self.anomalies = []
        self.stats = {"total_logs": 0, "uptime_minutes": 0, "avg_cpu": 0}

    def load_logs(self):
        """Load the last 24h of logs."""
        if not os.path.exists(METRICS_FILE):
            print("No metrics file found.")
            return []

        logs = []
        with open(METRICS_FILE, "r") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
        return logs

    def analyze(self, logs):
        if not logs:
            return

        self.stats["total_logs"] = len(logs)
        cpu_sum = 0
        cpu_count = 0

        start_time = datetime.fromisoformat(logs[0]["timestamp"])
        end_time = datetime.fromisoformat(logs[-1]["timestamp"])
        self.stats["uptime_minutes"] = (end_time - start_time).total_seconds() / 60

        for log in logs:
            data = log.get("data", {})

            # 1. System Health Check
            if log["type"] == "SYSTEM_HEALTH":
                cpu = data.get("cpu", 0)
                cpu_sum += cpu
                cpu_count += 1

                if cpu > 90:
                    self.anomalies.append(f"High CPU Usage: {cpu}% at {log['timestamp']}")

                if data.get("disk", 0) > 95:
                    self.anomalies.append(
                        f"Critical Disk Usage: {data.get('disk')}% at {log['timestamp']}"
                    )

        if cpu_count > 0:
            self.stats["avg_cpu"] = round(cpu_sum / cpu_count, 2)

    def generate_report(self, short=False):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ HEALTHY" if not self.anomalies else "⚠️ ANOMALIES DETECTED"

        if short:
            print(
                f"[{timestamp}] Status: {status} | Logs: {self.stats['total_logs']} | CPU: {self.stats['avg_cpu']}%"
            )
            if self.anomalies:
                print(f"Anomalies: {len(self.anomalies)}")
            return

        report = f"""# OmniMind External Audit Report
**Date:** {timestamp}
**Status:** {status}

## Statistics
- **Uptime Analyzed:** {self.stats['uptime_minutes']:.2f} minutes
- **Total Logs:** {self.stats['total_logs']}
- **Average CPU:** {self.stats['avg_cpu']}%

## Anomalies Detected
"""
        if not self.anomalies:
            report += "- No anomalies detected.\n"
        else:
            for anomaly in self.anomalies:
                report += f"- {anomaly}\n"

        with open(REPORT_FILE, "w") as f:
            f.write(report)
        print(f"Audit report generated: {REPORT_FILE}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze_recent_logs", action="store_true", help="Analyze recent logs")
    parser.add_argument(
        "--summary_report_short", action="store_true", help="Print short summary to stdout"
    )
    args = parser.parse_args()

    auditor = ExternalAuditor()
    logs = auditor.load_logs()
    auditor.analyze(logs)

    if args.analyze_recent_logs:
        auditor.generate_report(short=args.summary_report_short)
    else:
        auditor.generate_report()
