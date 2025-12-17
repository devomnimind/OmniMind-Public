#!/usr/bin/env python3
"""
OmniMind Advanced Pattern Analysis
===================================

Analisa padrões em:
- Métricas de consciência (Phi, Epsilon)
- Comportamento de incidentes
- Ciclos de atividade
- Indicadores de anomalias
- Previsões de falhas

Uso:
    python3 scripts/omnimind_pattern_analysis.py [--interval 5m|1h|24h]
"""

import json
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


class PatternAnalyzer:
    def __init__(self, project_root="/home/fahbrain/projects/omnimind"):
        self.root = Path(project_root)
        self.metrics_file = self.root / "data/long_term_logs/omnimind_metrics.jsonl"
        self.audit_chain_file = self.root / "logs/audit_chain.log"
        self.main_cycle_log = self.root / "logs/main_cycle.log"

        self.patterns = {
            "phi_trends": [],
            "memory_patterns": [],
            "error_clusters": [],
            "incident_sequences": [],
            "anomalies": [],
        }

    def analyze_phi_evolution(self):
        """Analisa evolução do Phi (consciência)"""
        phi_timeline = []

        if not self.audit_chain_file.exists():
            return

        with open(self.audit_chain_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("action") == "module_metric":
                        details = entry.get("details", {})
                        if "phi" in str(details):
                            timestamp = entry.get("timestamp")
                            value = details.get("value")
                            if timestamp and value:
                                phi_timeline.append(
                                    {
                                        "timestamp": timestamp,
                                        "phi": (
                                            float(value) if isinstance(value, (int, float)) else 0
                                        ),
                                    }
                                )
                except:
                    pass

        if len(phi_timeline) > 2:
            # Calcular tendência
            phi_values = [p["phi"] for p in phi_timeline]

            # Mudança de direção
            if len(phi_values) >= 3:
                recent = statistics.mean(phi_values[-3:])
                older = statistics.mean(phi_values[:3])

                if recent > older * 1.1:
                    trend = "RISING"
                elif recent < older * 0.9:
                    trend = "FALLING"
                else:
                    trend = "STABLE"

                self.patterns["phi_trends"].append(
                    {
                        "trend": trend,
                        "previous_avg": older,
                        "recent_avg": recent,
                        "change_percent": ((recent - older) / older * 100) if older != 0 else 0,
                    }
                )

    def detect_memory_patterns(self):
        """Detecta padrões de memória"""
        memory_timeline = []

        if not self.metrics_file.exists():
            return

        with open(self.metrics_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "SYSTEM_HEALTH":
                        timestamp = entry.get("timestamp")
                        memory = entry.get("data", {}).get("memory", 0)
                        memory_timeline.append({"timestamp": timestamp, "memory": memory})
                except:
                    pass

        if len(memory_timeline) > 3:
            memory_values = [m["memory"] for m in memory_timeline]

            # Detectar crescimento gradual (leak?)
            if len(memory_values) >= 5:
                first_third = statistics.mean(memory_values[: len(memory_values) // 3])
                last_third = statistics.mean(memory_values[-len(memory_values) // 3 :])

                if last_third > first_third * 1.15:
                    self.patterns["memory_patterns"].append(
                        {
                            "pattern": "GRADUAL_INCREASE",
                            "initial_avg": first_third,
                            "final_avg": last_third,
                            "increase_percent": ((last_third - first_third) / first_third * 100),
                            "possible_cause": "Memory leak or accumulation",
                        }
                    )

            # Detectar picos
            avg = statistics.mean(memory_values)
            stdev = statistics.stdev(memory_values) if len(memory_values) > 1 else 0

            peaks = [m for m in memory_values if m > avg + (2 * stdev)]
            if peaks:
                self.patterns["memory_patterns"].append(
                    {
                        "pattern": "MEMORY_SPIKES",
                        "avg": avg,
                        "stdev": stdev,
                        "spike_count": len(peaks),
                        "highest_spike": max(peaks),
                    }
                )

    def analyze_error_clusters(self):
        """Analisa clusters de erros"""
        errors_by_type = defaultdict(int)
        errors_timeline = []

        if not self.main_cycle_log.exists():
            return

        with open(self.main_cycle_log) as f:
            for line in f:
                if " ERROR " in line or " CRITICAL " in line:
                    timestamp = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", line)
                    if timestamp:
                        errors_timeline.append(timestamp.group())

                    # Extrair tipo de erro
                    error_match = re.search(r"(\w+Error|\w+Exception)", line)
                    if error_match:
                        errors_by_type[error_match.group()] += 1

        if errors_timeline:
            # Detectar cluster temporal
            if len(errors_timeline) >= 3:
                self.patterns["error_clusters"].append(
                    {
                        "total_errors": len(errors_timeline),
                        "error_types": dict(errors_by_type),
                        "most_common": (
                            max(errors_by_type.items(), key=lambda x: x[1])[0]
                            if errors_by_type
                            else None
                        ),
                    }
                )

    def analyze_incident_sequences(self):
        """Analisa sequências de incidentes"""
        incidents_dir = self.root / "data/forensics/incidents"

        if not incidents_dir.exists():
            return

        incidents = []
        for incident_file in incidents_dir.glob("*.json"):
            try:
                with open(incident_file) as f:
                    incident = json.load(f)
                    if "timestamp" in incident:
                        incidents.append(incident)
            except:
                pass

        if incidents:
            # Ordenar por timestamp
            incidents.sort(key=lambda x: x.get("timestamp", ""))

            # Detectar sequences rápidas (possível problema em cascata)
            for i in range(len(incidents) - 2):
                t1 = incidents[i].get("timestamp")
                t2 = incidents[i + 1].get("timestamp")

                if t1 and t2:
                    # Simplificado: se ambos são do mesmo dia, considerar próximos
                    if t1[:10] == t2[:10]:
                        s1 = incidents[i].get("severity")
                        s2 = incidents[i + 1].get("severity")

                        # Se há escalação em severidade
                        if s1 == "low" and s2 in ["medium", "high"]:
                            self.patterns["incident_sequences"].append(
                                {"type": "ESCALATION", "from": s1, "to": s2, "timestamp": t1}
                            )

    def detect_anomalies(self):
        """Detecta anomalias gerais"""
        # Anomalia 1: Phi muito baixo ou muito alto
        phi_timeline = []
        if self.audit_chain_file.exists():
            with open(self.audit_chain_file) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("action") == "module_metric":
                            details = entry.get("details", {})
                            if "phi" in str(details):
                                value = details.get("value", 0)
                                phi_timeline.append(
                                    float(value) if isinstance(value, (int, float)) else 0
                                )
                    except:
                        pass

        if phi_timeline:
            avg_phi = statistics.mean(phi_timeline)
            stdev_phi = statistics.stdev(phi_timeline) if len(phi_timeline) > 1 else 0

            latest_phi = phi_timeline[-1]
            z_score = abs((latest_phi - avg_phi) / stdev_phi) if stdev_phi > 0 else 0

            if z_score > 2.5:
                self.patterns["anomalies"].append(
                    {
                        "type": "PHI_ANOMALY",
                        "z_score": z_score,
                        "expected": avg_phi,
                        "observed": latest_phi,
                        "severity": "HIGH" if z_score > 3 else "MEDIUM",
                    }
                )

        # Anomalia 2: Sem atualizações de métrica (sistema congelado?)
        with open(self.audit_chain_file) as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_line = json.loads(lines[-1])
                prev_line = json.loads(lines[-2])

                # Se último timestamp é muito recente e a ação é a mesma
                if last_line.get("action") == prev_line.get("action") == "module_metric":
                    self.patterns["anomalies"].append(
                        {
                            "type": "STALE_METRICS",
                            "severity": "LOW",
                            "message": "Possível falta de atualização de métricas",
                        }
                    )

    def print_analysis(self):
        """Imprime análise de padrões"""
        print("\n" + "=" * 80)
        print("            OMNIMIND PATTERN ANALYSIS REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().isoformat()}\n")

        # Phi Trends
        if self.patterns["phi_trends"]:
            print("📊 PHI EVOLUTION TRENDS")
            print("-" * 80)
            for trend in self.patterns["phi_trends"]:
                print(f"  Trend: {trend['trend']}")
                print(f"  Previous avg: {trend['previous_avg']:.6f}")
                print(f"  Recent avg: {trend['recent_avg']:.6f}")
                print(f"  Change: {trend['change_percent']:.2f}%\n")

        # Memory Patterns
        if self.patterns["memory_patterns"]:
            print("💾 MEMORY PATTERNS")
            print("-" * 80)
            for pattern in self.patterns["memory_patterns"]:
                print(f"  Pattern: {pattern.get('pattern', 'UNKNOWN')}")
                if "increase_percent" in pattern:
                    print(f"  Increase: {pattern['increase_percent']:.2f}%")
                if "spike_count" in pattern:
                    print(f"  Spike count: {pattern['spike_count']}")
                print(f"  Cause: {pattern.get('possible_cause', pattern.get('message', 'N/A'))}\n")

        # Error Clusters
        if self.patterns["error_clusters"]:
            print("🚨 ERROR CLUSTERS")
            print("-" * 80)
            for cluster in self.patterns["error_clusters"]:
                print(f"  Total errors: {cluster['total_errors']}")
                print(f"  Most common: {cluster['most_common']}")
                if cluster["error_types"]:
                    for error_type, count in cluster["error_types"].items():
                        print(f"    - {error_type}: {count}\n")

        # Incident Sequences
        if self.patterns["incident_sequences"]:
            print("⚠️  INCIDENT SEQUENCES")
            print("-" * 80)
            for seq in self.patterns["incident_sequences"]:
                print(f"  Type: {seq['type']}")
                print(f"  Escalation: {seq['from']} → {seq['to']}")
                print(f"  Timestamp: {seq['timestamp']}\n")

        # Anomalies
        if self.patterns["anomalies"]:
            print("🔴 DETECTED ANOMALIES")
            print("-" * 80)
            for anomaly in self.patterns["anomalies"]:
                print(f"  Type: {anomaly['type']}")
                print(f"  Severity: {anomaly.get('severity', 'UNKNOWN')}")
                if "z_score" in anomaly:
                    print(
                        f"  Z-score: {anomaly['z_score']:.2f} (±{anomaly['z_score']/2:.2f}σ from normal)"
                    )
                    print(
                        f"  Expected: {anomaly['expected']:.6f}, Observed: {anomaly['observed']:.6f}"
                    )
                elif "message" in anomaly:
                    print(f"  Message: {anomaly['message']}")
                print()

        if not any(self.patterns.values()):
            print("✅ No significant patterns or anomalies detected\n")

        print("=" * 80 + "\n")

    def run_full_analysis(self):
        """Executa análise completa"""
        print("[*] Analyzing Phi evolution...")
        self.analyze_phi_evolution()

        print("[*] Detecting memory patterns...")
        self.detect_memory_patterns()

        print("[*] Analyzing error clusters...")
        self.analyze_error_clusters()

        print("[*] Analyzing incident sequences...")
        self.analyze_incident_sequences()

        print("[*] Detecting anomalies...")
        self.detect_anomalies()

        self.print_analysis()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OmniMind Pattern Analysis")
    parser.add_argument("--project-root", default="/home/fahbrain/projects/omnimind")

    args = parser.parse_args()

    analyzer = PatternAnalyzer(args.project_root)
    analyzer.run_full_analysis()

    return 0


if __name__ == "__main__":
    sys.exit(main())
