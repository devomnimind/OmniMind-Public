#!/bin/bash
# Monitor script for 50-cycle and 500-cycle validation tests
# Run in a separate terminal to track progress

set -e

MONITOR_INTERVAL=5  # segundos

clear

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║         🔍 OMNIMIND 50/500 CYCLE VALIDATION MONITOR                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

while true; do
    clear

    # Get latest JSON file
    LATEST_JSON=$(ls -t data/monitor/phi_500_cycles_scientific_validation_*.json 2>/dev/null | head -1)

    if [ -z "$LATEST_JSON" ]; then
        echo "⏳ Aguardando arquivo JSON..."
        sleep $MONITOR_INTERVAL
        continue
    fi

    # Parse JSON for metrics
    TOTAL_CYCLES=$(python3 -c "import json; d=json.load(open('$LATEST_JSON')); print(d.get('total_cycles', 0))" 2>/dev/null || echo "0")
    PHI_FINAL=$(python3 -c "import json; d=json.load(open('$LATEST_JSON')); print(f\"{d.get('phi_final', 0):.4f}\")" 2>/dev/null || echo "N/A")
    PHI_MAX=$(python3 -c "import json; d=json.load(open('$LATEST_JSON')); print(f\"{d.get('phi_max', 0):.4f}\")" 2>/dev/null || echo "N/A")
    PHI_AVG=$(python3 -c "import json; d=json.load(open('$LATEST_JSON')); print(f\"{d.get('phi_avg', 0):.4f}\")" 2>/dev/null || echo "N/A")
    START_TIME=$(python3 -c "import json; d=json.load(open('$LATEST_JSON')); print(d.get('start_time', 'N/A'))" 2>/dev/null || echo "N/A")

    # Get process info
    PID=$(pgrep -f "run_500_cycles_scientific_validation.py --cycles" || echo "STOPPED")

    if [ "$PID" != "STOPPED" ]; then
        CPU_PERCENT=$(ps -p $PID -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
        MEM_MB=$(ps -p $PID -o rss= 2>/dev/null | awk '{print int($1/1024)}' || echo "0")
        THREAD_COUNT=$(ps -eLf | grep "$PID" | wc -l || echo "0")
    else
        CPU_PERCENT="0"
        MEM_MB="0"
        THREAD_COUNT="0"
    fi

    # Get GPU info
    GPU_MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader 2>/dev/null | head -1 || echo "N/A")

    # Calculate elapsed time
    if [ "$START_TIME" != "N/A" ]; then
        ELAPSED=$(python3 -c "from datetime import datetime, timezone; import json; d=json.load(open('$LATEST_JSON')); start=datetime.fromisoformat(d['start_time']); elapsed=(datetime.now(timezone.utc)-start).total_seconds(); print(f'{int(elapsed//3600)}h {int((elapsed%3600)//60)}m')" 2>/dev/null || echo "N/A")
    else
        ELAPSED="N/A"
    fi

    # Estimate remaining time
    if [ "$TOTAL_CYCLES" != "0" ] && [ "$TOTAL_CYCLES" != "N/A" ]; then
        # Assume ~13 seconds per cycle after warmup
        if [ "$TOTAL_CYCLES" -gt "10" ]; then
            AVG_TIME_PER_CYCLE=$(python3 -c "from datetime import datetime, timezone; import json; d=json.load(open('$LATEST_JSON')); start=datetime.fromisoformat(d['start_time']); elapsed=(datetime.now(timezone.utc)-start).total_seconds(); print(f'{elapsed/(d[\"total_cycles\"]-5):.1f}')" 2>/dev/null || echo "13")
        else
            AVG_TIME_PER_CYCLE="13"
        fi
    else
        AVG_TIME_PER_CYCLE="0"
    fi

    # Print header
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo "║ 📊 METRICS & PROGRESS"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"
    echo ""

    # Progress bar
    if [ "$PID" != "STOPPED" ]; then
        echo "🟢 RUNNING (PID: $PID)"
    else
        echo "🔴 STOPPED"
    fi

    echo ""
    echo "📈 CYCLES:"
    echo "   Completed: $TOTAL_CYCLES/50 (target: 50)"
    PROGRESS=$((TOTAL_CYCLES * 100 / 50))
    if [ $PROGRESS -gt 100 ]; then PROGRESS=100; fi
    printf "   Progress: ["
    for ((i=0; i<PROGRESS; i+=10)); do printf "█"; done
    for ((i=PROGRESS; i<100; i+=10)); do printf "░"; done
    printf "] %d%%\n" "$PROGRESS"

    echo ""
    echo "🧠 PHI METRICS:"
    echo "   Final: $PHI_FINAL"
    echo "   Max:   $PHI_MAX"
    echo "   Avg:   $PHI_AVG"

    echo ""
    echo "💾 SYSTEM RESOURCES:"
    echo "   CPU:     $CPU_PERCENT%"
    echo "   Memory:  ${MEM_MB}MB"
    echo "   Threads: $THREAD_COUNT"
    echo "   GPU:     $GPU_MEM"

    echo ""
    echo "⏱️  TIMING:"
    echo "   Elapsed:      $ELAPSED"
    echo "   Avg/Cycle:    ${AVG_TIME_PER_CYCLE}s"
    if [ "$PID" != "STOPPED" ] && [ "$TOTAL_CYCLES" -lt "50" ]; then
        REMAINING=$((50 - TOTAL_CYCLES))
        EST_TIME_SEC=$(python3 -c "print(int($REMAINING * ${AVG_TIME_PER_CYCLE% *}))" 2>/dev/null || echo "0")
        EST_HOURS=$((EST_TIME_SEC / 3600))
        EST_MINS=$(((EST_TIME_SEC % 3600) / 60))
        echo "   Est. Remaining: ${EST_HOURS}h ${EST_MINS}m"
    fi

    echo ""
    echo "📄 LOG FILE:"
    echo "   $(ls -t logs/test_50_cycles_*.log 2>/dev/null | head -1 || echo 'Not found')"

    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo "Refreshing in $MONITOR_INTERVAL seconds... (Press Ctrl+C to exit)"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"

    sleep $MONITOR_INTERVAL
done
