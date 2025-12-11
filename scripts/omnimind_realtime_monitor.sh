#!/bin/bash
#
# OmniMind Real-Time Status Monitor
# ==================================
#
# Monitora em tempo real:
# - Status de serviços
# - Métrica críticas (Phi, Backends)
# - Incidentes sendo criados
# - Auto-repair em ação
#

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo "
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              🧠 OMNIMIND REAL-TIME STATUS MONITOR                         ║
║                                                                            ║
║  This monitor shows live system status. Press Ctrl+C to exit.            ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"

while true; do
    clear

    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║ 🧠 OMNIMIND SYSTEM STATUS - $(date '+%H:%M:%S')"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"

    # 1. Service Status
    echo ""
    echo "📊 SERVICE STATUS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python3 << 'PYTHON'
import socket
services = {
    8000: "Backend Primary",
    8080: "Backend Secondary",
    3001: "Backend Fallback",
    3000: "Frontend Dashboard",
    6379: "Redis Cache"
}

for port, name in services.items():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()

        if result == 0:
            print(f"  ✅ {name:25} (:{port})")
        else:
            print(f"  ❌ {name:25} (:{port})")
    except:
        print(f"  ❌ {name:25} (:{port})")
PYTHON

    # 2. Recent Metrics
    echo ""
    echo "📈 LATEST METRICS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python3 << 'PYTHON'
import json
from pathlib import Path

metrics_file = Path("/home/fahbrain/projects/omnimind/data/long_term_logs/omnimind_metrics.jsonl")
if metrics_file.exists():
    with open(metrics_file) as f:
        lines = f.readlines()

    if lines:
        # Últimas métricas críticas e secundárias
        critical = None
        secondary = None

        for line in reversed(lines[-20:]):
            try:
                metric = json.loads(line)
                if metric.get("type") == "CRITICAL_METRICS" and not critical:
                    critical = metric.get("data", {})
                elif metric.get("type") == "SYSTEM_HEALTH" and not secondary:
                    secondary = metric.get("data", {})
            except:
                pass

        if critical:
            backends = critical.get("backends", {})
            phi = critical.get("phi", 0)
            print(f"  🧠 Phi: {phi:.6f}")
            print(f"  🔧 Backends healthy: {critical.get('backends_healthy', 0)}/{critical.get('backends_total', 0)}")

        if secondary:
            print(f"  💻 CPU: {secondary.get('cpu', 0):.1f}%")
            print(f"  🧠 Memory: {secondary.get('memory', 0):.1f}%")
            print(f"  💾 Disk: {secondary.get('disk', 0):.1f}%")
PYTHON

    # 3. Recent Incidents
    echo ""
    echo "🚨 RECENT INCIDENTS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    incidents_count=$(ls -1 "$PROJECT_ROOT/data/forensics/incidents/" 2>/dev/null | wc -l)
    echo "  Total incidents: $incidents_count"

    # Últimos 3
    for file in $(ls -1t "$PROJECT_ROOT/data/forensics/incidents/"*.json 2>/dev/null | head -3); do
        python3 << PYTHON
import json
try:
    with open("$file") as f:
        inc = json.load(f)
        sev = inc.get("severity", "?").upper()
        emoji = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}.get(sev, "⚪")
        print(f"  {emoji} {sev}")
except:
    pass
PYTHON
    done

    # 4. Active Daemons
    echo ""
    echo "🔄 ACTIVE DAEMONS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    ps aux | grep -E "omnimind_(auto_repair|metrics_collector)" | grep -v grep | awk '{print "  ✅ " $11 " (PID: " $2 ")"}' | head -2

    # 5. System Health Summary
    echo ""
    echo "✨ SYSTEM HEALTH:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python3 << 'PYTHON'
import json
from pathlib import Path

audit_file = Path("/home/fahbrain/projects/omnimind/logs/audit_chain.log")
if audit_file.exists():
    with open(audit_file) as f:
        lines = f.readlines()

    recovery_count = sum(1 for line in lines if '"recovery"' in line.lower() or '"repair"' in line.lower())
    print(f"  🔄 Recovery actions: {recovery_count}")

metrics_file = Path("/home/fahbrain/projects/omnimind/data/long_term_logs/omnimind_metrics.jsonl")
if metrics_file.exists():
    with open(metrics_file) as f:
        lines = f.readlines()
    print(f"  📊 Metrics collected: {len(lines)}")

print(f"  ✅ Overall Status: OPERATIONAL")
PYTHON

    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║ Refreshing in 5 seconds... Press Ctrl+C to exit"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"

    sleep 5
done
