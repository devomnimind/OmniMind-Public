#!/bin/bash
#
# OmniMind Clean Start - No Redundant Sudo
# =========================================
#
# Inicia o sistema sem solicitar senha sudoers duas vezes
# Gerencia: Backend Primary, Auto-Repair, Metrics, Frontend
#

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🚀 OMNIMIND CLEAN START (No Redundant Sudo)              ║${NC}"
echo -e "${GREEN}║  $(date '+%Y-%m-%d %H:%M:%S')                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# PHASE 1: STOP OLD PROCESSES
# ============================================================================

echo -e "${BLUE}[Phase 1]${NC} Stopping old processes..."

# Kill old daemons (gracefully)
pkill -f "omnimind_auto_repair.py" 2>/dev/null || true
pkill -f "omnimind_metrics_collector.py" 2>/dev/null || true
pkill -f "http.server 3000" 2>/dev/null || true
pkill -f "start_omnimind_system" 2>/dev/null || true

sleep 2

echo -e "${GREEN}      ✓ Old processes stopped${NC}"

# ============================================================================
# PHASE 2: BACKEND INITIALIZATION (via v2 wrapper - handles internally)
# ============================================================================

echo ""
echo -e "${BLUE}[Phase 2]${NC} Starting Backend Services..."
echo -e "      Executing: bash scripts/start_omnimind_system_wrapper_v2.sh"

if bash "$PROJECT_ROOT/scripts/start_omnimind_system_wrapper_v2.sh"; then
    echo -e "${GREEN}      ✓ Backend Services started successfully${NC}"
else
    EXIT_CODE=$?
    echo -e "${RED}      ✗ Backend startup failed (exit code: $EXIT_CODE)${NC}"
    exit $EXIT_CODE
fi

# ============================================================================
# PHASE 3: VERIFY ALL SERVICES RUNNING
# ============================================================================

echo ""
echo -e "${BLUE}[Phase 3]${NC} Verifying Services..."
echo ""

python3 << 'PYTHON'
import socket
import time

services = {
    8000: ("Backend Primary", "critical"),
    3000: ("Frontend Dashboard", "critical"),
    6379: ("Redis", "secondary"),
    8080: ("Backend Secondary", "optional"),
    3001: ("Backend Fallback", "optional"),
}

print("Service Status:")
print("─" * 60)

all_healthy = True
for port, (name, severity) in services.items():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()

        if result == 0:
            print(f"  ✅ {name:25} (:{port:5}) - RUNNING")
        else:
            status_str = f"OFFLINE ({severity})"
            symbol = "❌" if severity == "critical" else "⚠️ "
            print(f"  {symbol} {name:25} (:{port:5}) - {status_str}")
            if severity == "critical":
                all_healthy = False
    except Exception as e:
        print(f"  ❌ {name:25} (:{port:5}) - ERROR: {str(e)}")
        if severity == "critical":
            all_healthy = False

print("─" * 60)

if all_healthy:
    print("\n✅ All critical services RUNNING")
else:
    print("\n❌ Some critical services offline - check logs")

# Check daemons
import os
import subprocess

print("\nDaemon Status:")
print("─" * 60)

result = subprocess.run(
    "ps aux | grep -E 'omnimind_(auto_repair|metrics_collector)' | grep -v grep",
    shell=True,
    capture_output=True,
    text=True
)

if result.stdout.strip():
    for line in result.stdout.strip().split('\n'):
        parts = line.split()
        if len(parts) > 1:
            print(f"  ✅ {parts[10]}")
else:
    print("  ⚠️  No daemons detected (may be still starting)")

print("─" * 60)

PYTHON

# ============================================================================
# FINAL STATUS
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ OmniMind Initialization Complete${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${BLUE}📊 Dashboard Access:${NC}"
echo -e "   http://127.0.0.1:3000/dashboard_metrics.html"
echo ""
echo -e "${BLUE}🔍 Monitoring Commands:${NC}"
echo -e "   • Real-time monitor: bash scripts/omnimind_realtime_monitor.sh"
echo -e "   • Health check: python3 scripts/omnimind_health_analyzer.py"
echo -e "   • Forensics: python3 scripts/omnimind_forensics_analyzer.py"
echo ""
echo -e "${BLUE}📝 Log Files:${NC}"
echo -e "   • Auto-Repair: logs/auto_repair_daemon.log"
echo -e "   • Metrics: logs/metrics_collector_daemon.log"
echo -e "   • Dashboard: logs/dashboard_server.log"
echo -e "   • Startup: logs/startup_detailed.log"
echo ""

exit 0
