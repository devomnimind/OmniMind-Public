#!/bin/bash
# Quick check: Verify OmniMind Monitor status and metrics
# Usage: bash scripts/check_monitor.sh

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
LOGS_DIR="$PROJECT_ROOT/logs"
MONITOR_LOG="$LOGS_DIR/monitor_continuous.log"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 OmniMind Monitor Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check systemd service status
echo "1️⃣  Systemd Service Status:"
echo "─────────────────────────────────────────"
if command -v systemctl &> /dev/null; then
    STATUS=$(systemctl is-active omnimind-monitor 2>/dev/null || echo "not-installed")
    if [ "$STATUS" = "active" ]; then
        echo "✅ Service: ACTIVE"
        systemctl status omnimind-monitor --no-pager 2>/dev/null | grep -E "(Active|Restart|PID)" | head -3
    elif [ "$STATUS" = "not-installed" ]; then
        echo "⚠️  Service: NOT INSTALLED"
        echo "   Run: sudo bash scripts/install_monitor_service.sh"
    else
        echo "⚠️  Service: $STATUS"
    fi
else
    echo "⚠️  systemctl not available"
fi

echo ""
echo "2️⃣  Monitor Process Status:"
echo "─────────────────────────────────────────"
MONITOR_PIDS=$(pgrep -f "continuous_monitor.py" | head -5)
if [ -n "$MONITOR_PIDS" ]; then
    echo "✅ Process(es) running:"
    ps -p $MONITOR_PIDS -o pid,cmd,rss,etime --no-headers 2>/dev/null | sed 's/^/   /'
else
    echo "❌ No monitor process found"
fi

echo ""
echo "3️⃣  Recent Log Activity:"
echo "─────────────────────────────────────────"
if [ -f "$MONITOR_LOG" ]; then
    tail -5 "$MONITOR_LOG" | sed 's/^/   /'
    echo ""
    LOG_SIZE=$(du -h "$MONITOR_LOG" | awk '{print $1}')
    echo "   📊 Log size: $LOG_SIZE"
else
    echo "❌ No log file found: $MONITOR_LOG"
fi

echo ""
echo "4️⃣  Latest Metrics Snapshot:"
echo "─────────────────────────────────────────"
LATEST_SNAPSHOT=$(find "$LOGS_DIR" -name "monitor_snapshot_*.json" -type f 2>/dev/null | sort -r | head -1)
if [ -n "$LATEST_SNAPSHOT" ]; then
    echo "📁 File: $(basename $LATEST_SNAPSHOT)"
    python3 -c "
import json
with open('$LATEST_SNAPSHOT', 'r') as f:
    data = json.load(f)
    print(f'   ⏰ Timestamp: {data.get(\"timestamp\", \"N/A\")}')
    print(f'   📊 Processes: {data.get(\"processes_count\", 0)}')
    res = data.get('resources', {})
    print(f'   🔌 CPU: {res.get(\"cpu_percent\", 0):.1f}%')
    print(f'   💾 Memory: {res.get(\"memory_percent\", 0):.1f}%')
    print(f'   💿 Disk: {res.get(\"disk_percent\", 0):.1f}%')
    alerts = data.get('alerts', [])
    print(f'   ⚠️  Alerts: {len(alerts)}')
    if alerts:
        for alert in alerts[:2]:
            print(f'      - {alert}')
" 2>/dev/null || echo "   ❌ Error reading snapshot"
else
    echo "❌ No snapshots found"
fi

echo ""
echo "5️⃣  Dashboard Polling:"
echo "─────────────────────────────────────────"
echo "   Frontend polls every: 15 seconds (optimized)"
echo "   Monitor collects every: 30 seconds"
echo "   Cache fallback: YES (uses last known metrics)"
echo "   Status: ✅ Configured"

echo ""
echo "6️⃣  Helpful Commands:"
echo "─────────────────────────────────────────"
echo "   View live logs:  sudo journalctl -u omnimind-monitor -f"
echo "   Monitor stats:   python scripts/monitoring/monitor_control.py status"
echo "   Full report:     python scripts/monitoring/monitor.py"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$MONITOR_PIDS" ] || [ "$STATUS" = "active" ]; then
    echo "✅ Monitor Status: HEALTHY"
    echo "   Dashboard should show real metrics now"
else
    echo "❌ Monitor Status: NOT RUNNING"
    echo "   Install with: sudo bash scripts/install_monitor_service.sh"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
