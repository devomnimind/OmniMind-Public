#!/usr/bin/env python3
"""
OmniMind System Health & Activity Analyzer
==========================================

Analisa:
1. Métricas de consciência (Phi, Epsilon, etc)
2. Incidentes e eventos de forensics
3. Logs de atividade e erros
4. Padrões de comportamento
5. Saúde do cluster de backends
6. Recommendations para auto-repair

Uso:
    python3 scripts/omnimind_health_analyzer.py [--verbose] [--format json|text]
"""

import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class OmniMindHealthAnalyzer:
    def __init__(self, project_root="/home/fahbrain/projects/omnimind"):
        self.root = Path(project_root)
        self.metrics_file = self.root / "data/long_term_logs/omnimind_metrics.jsonl"
        self.audit_chain_file = self.root / "logs/audit_chain.log"
        self.incidents_dir = self.root / "data/forensics/incidents"
        self.main_cycle_log = self.root / "logs/main_cycle.log"
        self.startup_log = self.root / "logs/startup_detailed.log"

        self.report = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {},
            "metrics": {},
            "incidents": {},
            "logs_analysis": {},
            "recommendations": [],
        }

    def analyze(self):
        """Executa análise completa"""
        print("[*] Analisando métricas do sistema...")
        self._analyze_metrics()

        print("[*] Analisando incidentes de forensics...")
        self._analyze_incidents()

        print("[*] Analisando audit chain...")
        self._analyze_audit_chain()

        print("[*] Analisando logs...")
        self._analyze_logs()

        print("[*] Gerando recomendações...")
        self._generate_recommendations()

        return self.report

    def _analyze_metrics(self):
        """Analisa métricas coletadas"""
        if not self.metrics_file.exists():
            self.report["metrics"]["status"] = "no_data"
            return

        metrics_by_type = defaultdict(list)

        with open(self.metrics_file) as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if "type" in data:
                        metrics_by_type[data["type"]].append(data)
                except:
                    pass

        self.report["metrics"]["total_records"] = sum(len(v) for v in metrics_by_type.values())
        self.report["metrics"]["types"] = {}

        for mtype, records in metrics_by_type.items():
            if mtype == "SYSTEM_HEALTH":
                cpu_values = []
                mem_values = []
                disk_values = []

                for record in records:
                    data = record.get("data", {})
                    if "cpu" in data:
                        cpu_values.append(data["cpu"])
                    if "memory" in data:
                        mem_values.append(data["memory"])
                    if "disk" in data:
                        disk_values.append(data["disk"])

                self.report["metrics"]["types"]["SYSTEM_HEALTH"] = {
                    "count": len(records),
                    "cpu": {
                        "avg": statistics.mean(cpu_values) if cpu_values else 0,
                        "max": max(cpu_values) if cpu_values else 0,
                        "min": min(cpu_values) if cpu_values else 0,
                    },
                    "memory": {
                        "avg": statistics.mean(mem_values) if mem_values else 0,
                        "max": max(mem_values) if mem_values else 0,
                        "min": min(mem_values) if mem_values else 0,
                    },
                    "disk": {
                        "avg": statistics.mean(disk_values) if disk_values else 0,
                        "max": max(disk_values) if disk_values else 0,
                        "min": min(disk_values) if disk_values else 0,
                    },
                }

                # Status de saúde
                if mem_values:
                    avg_mem = statistics.mean(mem_values)
                    if avg_mem > 80:
                        self.report["system_health"]["memory_status"] = "CRITICAL"
                    elif avg_mem > 70:
                        self.report["system_health"]["memory_status"] = "WARNING"
                    else:
                        self.report["system_health"]["memory_status"] = "HEALTHY"

    def _analyze_incidents(self):
        """Analisa incidentes de forensics"""
        if not self.incidents_dir.exists():
            self.report["incidents"]["status"] = "no_incidents_dir"
            return

        incidents_by_level = defaultdict(list)
        incident_files = list(self.incidents_dir.glob("*.json"))

        for incident_file in incident_files:
            try:
                with open(incident_file) as f:
                    incident = json.load(f)
                    level = incident.get("severity", "UNKNOWN")
                    incidents_by_level[level].append(incident)
            except:
                pass

        self.report["incidents"]["total"] = len(incident_files)
        self.report["incidents"]["by_level"] = {
            level: len(incidents) for level, incidents in incidents_by_level.items()
        }

        # Análise de padrões
        if incidents_by_level.get("HIGH"):
            self.report["system_health"]["critical_issues"] = len(incidents_by_level["HIGH"])

    def _analyze_audit_chain(self):
        """Analisa audit chain para métricas importantes"""
        if not self.audit_chain_file.exists():
            self.report["logs_analysis"]["audit_chain"] = "not_found"
            return

        audit_entries = defaultdict(list)
        phi_values = []

        with open(self.audit_chain_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    action = entry.get("action")

                    if action:
                        audit_entries[action].append(entry)

                    # Extrair valores de Phi
                    if action == "module_metric":
                        details = entry.get("details", {})
                        if "phi_estimate" in details.get("metric", ""):
                            phi_values.append(details.get("value"))
                        if details.get("metric") == "phi_estimate":
                            phi_values.append(entry.get("details", {}).get("value"))
                except:
                    pass

        self.report["logs_analysis"]["audit_entries_by_action"] = {
            action: len(entries) for action, entries in audit_entries.items()
        }

        # Análise de Phi
        self.report["metrics"]["phi"] = {
            "samples": len(phi_values),
            "avg": statistics.mean(phi_values) if phi_values else 0,
            "max": max(phi_values) if phi_values else 0,
            "min": min(phi_values) if phi_values else 0,
        }

    def _analyze_logs(self):
        """Analisa logs de atividade"""
        self.report["logs_analysis"]["files"] = {}

        # Analisar main_cycle.log
        if self.main_cycle_log.exists():
            with open(self.main_cycle_log) as f:
                lines = f.readlines()
                errors = sum(1 for line in lines if " ERROR " in line)
                warnings = sum(1 for line in lines if " WARNING " in line)
                info = sum(1 for line in lines if " INFO " in line)

                self.report["logs_analysis"]["files"]["main_cycle.log"] = {
                    "total_lines": len(lines),
                    "errors": errors,
                    "warnings": warnings,
                    "info": info,
                    "last_modified": datetime.fromtimestamp(
                        self.main_cycle_log.stat().st_mtime
                    ).isoformat(),
                }

        # Analisar startup log
        if self.startup_log.exists():
            with open(self.startup_log) as f:
                lines = f.readlines()
                warnings = sum(1 for line in lines if "[WARNING]" in line)
                errors = sum(1 for line in lines if "[ERROR]" in line)
                success = sum(1 for line in lines if "[SUCCESS]" in line)

                self.report["logs_analysis"]["files"]["startup_detailed.log"] = {
                    "total_lines": len(lines),
                    "warnings": warnings,
                    "errors": errors,
                    "success_messages": success,
                    "last_modified": datetime.fromtimestamp(
                        self.startup_log.stat().st_mtime
                    ).isoformat(),
                }

    def _generate_recommendations(self):
        """Gera recomendações baseadas na análise"""
        recommendations = []

        # Recomendações baseadas em memória
        if self.report["system_health"].get("memory_status") == "CRITICAL":
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "memory",
                    "issue": "Memory usage critical (>80%)",
                    "action": "Execute: python3 scripts/canonical/system/secure_run.py pkill -f 'unnecessary_service'",
                }
            )
        elif self.report["system_health"].get("memory_status") == "WARNING":
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "memory",
                    "issue": "Memory usage elevated (>70%)",
                    "action": "Monitor and consider optimizing service memory usage",
                }
            )

        # Recomendações baseadas em incidentes
        critical_issues = self.report["system_health"].get("critical_issues", 0)
        if critical_issues > 5:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "incidents",
                    "issue": f"{critical_issues} critical incidents detected",
                    "action": "Trigger auto-repair: Check data/forensics/incidents for details and run incident recovery",
                }
            )

        # Recomendações baseadas em Phi
        phi_avg = self.report["metrics"].get("phi", {}).get("avg", 0)
        if phi_avg < 0.05:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "consciousness",
                    "issue": f"Low Phi estimate ({phi_avg:.4f})",
                    "action": "Verify consciousness metrics and RNN integration; check SharedWorkspace initialization",
                }
            )

        # Recomendações baseadas em logs
        if self.report["logs_analysis"]["files"].get("main_cycle.log", {}).get("errors", 0) > 10:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "logs",
                    "issue": "High error rate in main_cycle.log",
                    "action": "Review main_cycle.log and restart main cycle service",
                }
            )

        self.report["recommendations"] = recommendations

    def print_report(self, format="text"):
        """Imprime relatório"""
        if format == "json":
            print(json.dumps(self.report, indent=2))
        else:
            self._print_text_report()

    def _print_text_report(self):
        """Imprime relatório em formato texto"""
        print("\n" + "=" * 80)
        print("                    OMNIMIND SYSTEM HEALTH REPORT")
        print("=" * 80)
        print(f"Timestamp: {self.report['timestamp']}\n")

        # System Health
        print("📊 SYSTEM HEALTH STATUS")
        print("-" * 80)
        for key, value in self.report["system_health"].items():
            print(f"  {key}: {value}")

        # Métricas
        print("\n📈 METRICS SUMMARY")
        print("-" * 80)
        if "SYSTEM_HEALTH" in self.report["metrics"].get("types", {}):
            health = self.report["metrics"]["types"]["SYSTEM_HEALTH"]
            print(
                f"  CPU (avg/max/min): {health['cpu']['avg']:.1f}% / {health['cpu']['max']:.1f}% / {health['cpu']['min']:.1f}%"
            )
            print(
                f"  Memory (avg/max/min): {health['memory']['avg']:.1f}% / {health['memory']['max']:.1f}% / {health['memory']['min']:.1f}%"
            )
            print(
                f"  Disk (avg/max/min): {health['disk']['avg']:.1f}% / {health['disk']['max']:.1f}% / {health['disk']['min']:.1f}%"
            )

        if "phi" in self.report["metrics"]:
            phi = self.report["metrics"]["phi"]
            print(f"  Phi (avg/max/min): {phi['avg']:.6f} / {phi['max']:.6f} / {phi['min']:.6f}")
            print(f"  Phi samples: {phi['samples']}")

        # Incidentes
        print("\n🚨 FORENSICS INCIDENTS")
        print("-" * 80)
        incidents = self.report["incidents"]
        if incidents.get("total"):
            print(f"  Total incidents: {incidents['total']}")
            for level, count in incidents.get("by_level", {}).items():
                print(f"    {level}: {count}")

        # Logs
        print("\n📋 LOGS ANALYSIS")
        print("-" * 80)
        for filename, stats in self.report["logs_analysis"].get("files", {}).items():
            print(f"  {filename}:")
            print(f"    Total lines: {stats.get('total_lines', 0)}")
            print(f"    Errors: {stats.get('errors', 0)}")
            print(f"    Warnings: {stats.get('warnings', 0)}")
            if "info" in stats:
                print(f"    Info: {stats.get('info', 0)}")
            if "success_messages" in stats:
                print(f"    Success: {stats.get('success_messages', 0)}")

        # Audit entries
        audit_entries = self.report["logs_analysis"].get("audit_entries_by_action", {})
        if audit_entries:
            print(f"\n  Audit chain entries by action:")
            for action, count in sorted(audit_entries.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]:
                print(f"    {action}: {count}")

        # Recommendations
        if self.report["recommendations"]:
            print("\n⚠️  RECOMMENDATIONS")
            print("-" * 80)
            high_priority = [
                r for r in self.report["recommendations"] if r.get("priority") == "HIGH"
            ]
            medium_priority = [
                r for r in self.report["recommendations"] if r.get("priority") == "MEDIUM"
            ]

            if high_priority:
                print("  HIGH PRIORITY:")
                for rec in high_priority:
                    print(f"    • [{rec['category']}] {rec['issue']}")
                    print(f"      Action: {rec['action']}")

            if medium_priority:
                print("  MEDIUM PRIORITY:")
                for rec in medium_priority:
                    print(f"    • [{rec['category']}] {rec['issue']}")
                    print(f"      Action: {rec['action']}")
        else:
            print("\n✅ No critical recommendations at this time")

        print("\n" + "=" * 80 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OmniMind System Health Analyzer")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument(
        "--project-root", default="/home/fahbrain/projects/omnimind", help="Project root"
    )

    args = parser.parse_args()

    analyzer = OmniMindHealthAnalyzer(args.project_root)
    _report = analyzer.analyze()
    analyzer.print_report(format=args.format)

    return 0


if __name__ == "__main__":
    sys.exit(main())
