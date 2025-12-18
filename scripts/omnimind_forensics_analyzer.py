#!/usr/bin/env python3
"""
OmniMind Forensics Incident Analyzer
=====================================

Analisa por que incidentes forensics estão sendo criados.
Verifica:
- Origem dos incidentes
- Padrão temporal
- Sistema de recovery
- Auto-isolamento

Uso:
    python3 scripts/omnimind_forensics_analyzer.py
"""

import json
from collections import defaultdict
from pathlib import Path


class ForensicsAnalyzer:
    def __init__(self, project_root="/home/fahbrain/projects/omnimind"):
        self.root = Path(project_root)
        self.incidents_dir = self.root / "data/forensics/incidents"
        self.audit_chain = self.root / "logs/audit_chain.log"

    def analyze_incident_patterns(self):
        """Analisa padrões de criação de incidentes"""
        print("\n" + "=" * 80)
        print("FORENSICS INCIDENT PATTERN ANALYSIS")
        print("=" * 80)

        incidents = []
        incident_sources = defaultdict(int)
        incident_types = defaultdict(int)

        # Ler todos os incidentes
        for incident_file in sorted(self.incidents_dir.glob("*.json")):
            try:
                with open(incident_file) as f:
                    incident = json.load(f)
                    incidents.append(incident)

                    # Registrar fonte
                    source = incident.get("source", "UNKNOWN")
                    incident_sources[source] += 1

                    # Registrar tipo
                    itype = incident.get("type", "UNKNOWN")
                    incident_types[itype] += 1
            except:
                pass

        print(f"\nTotal Incidents: {len(incidents)}")
        print(f"Date Range: {len(incidents)} arquivos processados\n")

        # Analisar fontes
        print("📊 Incidents by Source:")
        print("-" * 80)
        if incident_sources:
            for source, count in sorted(incident_sources.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(incidents)) * 100
                print(f"  {source:40} {count:4}  ({percentage:5.1f}%)")
        else:
            print("  ⚠️  NO SOURCES IDENTIFIED (All incidents have 'source' missing)")

        # Analisar tipos
        print("\n📋 Incidents by Type:")
        print("-" * 80)
        if any(t != "UNKNOWN" for t in incident_types.keys()):
            for itype, count in sorted(incident_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(incidents)) * 100
                print(f"  {itype:40} {count:4}  ({percentage:5.1f}%)")
        else:
            print("  ⚠️  ALL INCIDENTS HAVE TYPE='UNKNOWN' (Possible logging issue)")

        # Analisar severidade
        print("\n🔴 Incidents by Severity:")
        print("-" * 80)
        severity_counts = defaultdict(int)
        for incident in incidents:
            sev = incident.get("severity", "unknown").lower()
            severity_counts[sev] += 1

        for sev in ["high", "medium", "low", "unknown"]:
            count = severity_counts[sev]
            if count > 0:
                percentage = (count / len(incidents)) * 100
                emoji = {"high": "🔴", "medium": "🟠", "low": "🟡", "unknown": "⚪"}.get(sev, "?")
                print(f"  {emoji} {sev.upper():10} {count:4}  ({percentage:5.1f}%)")

        # Analisar se há recovery actions
        print("\n🔄 Recovery Actions Detected:")
        print("-" * 80)
        recovery_actions = 0

        if self.audit_chain.exists():
            with open(self.audit_chain) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if "recover" in entry.get("action", "").lower():
                            recovery_actions += 1
                    except:
                        pass

        if recovery_actions > 0:
            print(f"  ✅ Found {recovery_actions} recovery/repair actions in audit chain")
            print(f"     → System IS attempting self-healing")
        else:
            print(f"  ⚠️  No explicit recovery actions logged")
            print(f"     → May need to enable auto-repair daemon")

        # Recomendações
        print("\n" + "=" * 80)
        print("DIAGNOSTIC RECOMMENDATIONS")
        print("=" * 80)

        recommendations = []

        # Rec 1: Problema de tipo UNKNOWN
        if incident_types.get("UNKNOWN", 0) == len(incidents):
            recommendations.append(
                "🔴 CRITICAL: All incidents have type='UNKNOWN'\n"
                "   → Incident creation function is not setting 'type' field\n"
                "   → Location: Check where incidents are being created\n"
                "   → File: data/forensics/incidents/*.json"
            )

        # Rec 2: Taxa de incidentes
        if len(incidents) > 100:
            rate = len(incidents) / 7  # Assumindo 7 dias
            recommendations.append(
                f"🟠 HIGH FREQUENCY: ~{rate:.0f} incidents/day\n"
                f"   → This is excessive for normal operation\n"
                f"   → Either: (1) System has issues, or (2) Logging too verbose\n"
                f"   → Recommendation: Review incident creation logic"
            )

        # Rec 3: Recovery actions
        if recovery_actions == 0 and any(s in ["high", "medium"] for s in severity_counts.keys()):
            recommendations.append(
                "⚠️  MISSING RECOVERY: High/Medium severity incidents without auto-repair\n"
                f"   → Total critical incidents: {severity_counts['high'] + severity_counts['medium']}\n"
                f"   → But no recovery actions logged\n"
                f"   → Recommendation: Enable auto-repair daemon:\n"
                f"      python3 scripts/omnimind_auto_repair.py --daemon"
            )

        # Rec 4: Frontend/Dashboard
        if incident_sources.get("frontend", 0) > 20:
            recommendations.append(
                "🟡 FRONTEND ISSUES: Many incidents from frontend\n"
                f"   → Consider rebuilding/restarting frontend\n"
                f"   → Dashboard should be accessible for monitoring"
            )

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec}")
        else:
            print("\n✅ No critical issues detected in incident patterns")

        return {
            "total_incidents": len(incidents),
            "incident_sources": dict(incident_sources),
            "incident_types": dict(incident_types),
            "severity_distribution": dict(severity_counts),
            "recovery_actions": recovery_actions,
        }

    def check_system_isolation(self):
        """Verifica se sistema está isolado ou auto-reparando"""
        print("\n" + "=" * 80)
        print("SYSTEM ISOLATION & RECOVERY STATUS")
        print("=" * 80)

        # Verificar se há processos principais rodando
        import subprocess

        try:
            result = subprocess.run(
                "ps aux | grep -E 'omnimind|backend|frontend' | grep -v grep",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
            )

            processes = result.stdout.strip().split("\n") if result.stdout.strip() else []

            print(f"\n🔍 Active OmniMind Processes: {len([p for p in processes if p])}")
            print("-" * 80)

            if processes:
                for proc in processes:
                    if proc.strip():
                        # Extrair informação relevante
                        parts = proc.split()
                        if len(parts) > 10:
                            print(f"  ✅ {parts[10]}")
            else:
                print("  ⚠️  No OmniMind processes found!")

            # Verificar portas
            print("\n🔌 Service Ports Status:")
            print("-" * 80)
            ports = {
                8000: "Backend Primary",
                8080: "Backend Secondary",
                3001: "Backend Fallback",
                3000: "Frontend",
                6379: "Redis",
            }

            for port, name in ports.items():
                import socket

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(("127.0.0.1", port))
                    sock.close()

                    if result == 0:
                        print(f"  ✅ {name:20} (:{port}) - RUNNING")
                    else:
                        print(f"  ❌ {name:20} (:{port}) - OFFLINE")
                except:
                    print(f"  ❌ {name:20} (:{port}) - ERROR")

        except Exception as e:
            print(f"  Error checking system: {e}")

        # Verificar se há "isolation" logs
        print("\n🔐 Isolation Status:")
        print("-" * 80)

        main_cycle_log = self.root / "logs/main_cycle.log"
        if main_cycle_log.exists():
            with open(main_cycle_log) as f:
                content = f.read()

            isolation_mentions = (
                content.count("isolation") + content.count("isolat") + content.count("quarantine")
            )
            recovery_mentions = (
                content.count("recover") + content.count("repair") + content.count("restart")
            )

            print(f"  Isolation references: {isolation_mentions}")
            print(f"  Recovery references: {recovery_mentions}")

            if recovery_mentions > isolation_mentions:
                print(f"  ✅ System is actively recovering/repairing")
            else:
                print(f"  ⚠️  More isolation than recovery activity")

        print()


def main():
    analyzer = ForensicsAnalyzer()
    stats = analyzer.analyze_incident_patterns()
    analyzer.check_system_isolation()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY & ACTION ITEMS")
    print("=" * 80)

    print(
        f"""
Total Incidents: {stats['total_incidents']}
  • HIGH severity: {stats['severity_distribution'].get('high', 0)}
  • MEDIUM severity: {stats['severity_distribution'].get('medium', 0)}
  • LOW severity: {stats['severity_distribution'].get('low', 0)}

Recovery Status: {stats['recovery_actions']} actions logged

ACTION ITEMS:
  1. If frontend dashboard needed:
     → bash scripts/start_development.sh (starts frontend on port 3000)

  2. If auto-repair not active:
     → python3 scripts/omnimind_auto_repair.py --daemon --check-interval 60

  3. For metrics collection (2min critical, 5min secondary):
     → python3 scripts/omnimind_metrics_collector.py --daemon

  4. Monitor incidents in real-time:
     → watch -n 5 'ls -la data/forensics/incidents | tail -10'
"""
    )

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
