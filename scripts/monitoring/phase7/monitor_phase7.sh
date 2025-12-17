#!/bin/bash
# 📊 PHASE 7 MONITORING DASHBOARD
# Real-time monitoring of Zimerman Bonds execution

while true; do
    clear

    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    📊 PHASE 7 MONITORING DASHBOARD                             ║"
    echo "║                      ZIMERMAN BONDS - Live Metrics                             ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"

    # Check execution log
    log_file=$(ls -t logs/phase7_execution_*.log 2>/dev/null | head -1)

    if [ -n "$log_file" ] && [ -f "$log_file" ]; then
        echo ""
        echo "📝 Recent Log Updates:"
        tail -20 "$log_file"
    else
        echo ""
        echo "⏳ Aguardando início da execução..."
        echo "   Procure por: logs/phase7_execution_*.log"
    fi

    # Check system resources
    echo ""
    echo "💻 System Resources:"
    echo "   CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "   Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"

    # Check for Phase 7 data files
    echo ""
    echo "📁 Phase 7 Data Files:"
    if [ -d "data/monitor" ]; then
        phase7_files=$(find data/monitor -name "*phase7*" -o -name "*zimerman*" 2>/dev/null | wc -l)
        echo "   Files found: $phase7_files"
        ls -lh data/monitor/phase7* 2>/dev/null | tail -5 || echo "   (Waiting for data collection...)"
    fi

    # Status line
    echo ""
    echo "═════════════════════════════════════════════════════════════════════════════════"

    if ps aux | grep -q "run_200_cycles.*phase.*7"; then
        echo "✅ Status: RUNNING (Press Ctrl+C to exit dashboard)"
    else
        echo "⏳ Status: IDLE (Phase 7 ready to start)"
    fi

    echo "═════════════════════════════════════════════════════════════════════════════════"

    sleep 10

done
