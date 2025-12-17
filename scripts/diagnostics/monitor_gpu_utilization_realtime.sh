#!/bin/bash

# Force locale US para evitar problemas com vírgula decimal em português
export LC_ALL=C
export LANG=en_US.UTF-8

# 🔍 GPU Utilization Monitor - Real-Time Diagnostics
# Mostra EXATAMENTE se GPU está subutilizada enquanto script roda

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo -e "\033[1;36m🔍 GPU UTILIZATION MONITOR - REAL TIME\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Este script monitora:"
echo "   • GPU SM (Stream Multiprocessor) - target: >75%"
echo "   • GPU Memory - target: 20-60%"
echo "   • GPU Clock - deve estar MÁXIMO quando rodando"
echo "   • Context Switches - deve ser ZERO ou muito baixo"
echo ""
echo "⚠️  Se SM < 60%: GPU está SUBUTILIZADA (script problema)"
echo "✅ Se SM > 75%: GPU está bem utilizada (script OK)"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

# Check if nvidia-smi is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. Installing nvidia-utils..."
    sudo apt-get install -y nvidia-utils
fi

# Criar report file
REPORT_FILE="$PROJECT_ROOT/data/reports/gpu_utilization_$(date +%Y%m%d_%H%M%S).csv"
mkdir -p "$(dirname "$REPORT_FILE")"

echo "timestamp,sm_util,mem_util,sm_clock,mem_clock,power_draw,context_switches" > "$REPORT_FILE"

echo "📁 Saving to: $REPORT_FILE"
echo ""

# Counter
count=0
sm_values=()
mem_values=()

while true; do
    # Get GPU stats
    timestamp=$(date +%s)

    # Usar 'nvidia-smi dmon' se disponível (Nvidia driver 418+)
    if nvidia-smi dmon -s pucm -c 1 > /tmp/gpu_stats.txt 2>/dev/null; then
        # Parse dmon output
        sm_util=$(tail -1 /tmp/gpu_stats.txt | awk '{print $3}')
        mem_util=$(tail -1 /tmp/gpu_stats.txt | awk '{print $4}')
    else
        # Fallback para nvidia-smi padrão
        sm_util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
        mem_util=$(nvidia-smi --query-gpu=utilization.memory --format=csv,noheader,nounits)
    fi

    # Sanitize numbers - garantir ponto decimal (replace vírgula com ponto)
    sm_util=$(echo "$sm_util" | tr ',' '.')
    mem_util=$(echo "$mem_util" | tr ',' '.')

    sm_clock=$(nvidia-smi --query-gpu=clocks.current.sm --format=csv,noheader,nounits)
    mem_clock=$(nvidia-smi --query-gpu=clocks.current.memory --format=csv,noheader,nounits)
    power_draw=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits | awk '{print int($1)}' | tr ',' '.')

    # Context switches (from nvidia-smi PCI info)
    ctx_switches=$(nvidia-smi --query-gpu=pstate --format=csv,noheader | grep -o "P[0-9]" | head -1 || echo "N/A")

    # Store values for averaging
    sm_values+=($sm_util)
    mem_values+=($mem_util)

    # Color based on utilization
    if (( $(echo "$sm_util > 75" | bc -l) )); then
        color="\033[0;32m"  # Green - Good
        status="✅"
    elif (( $(echo "$sm_util > 50" | bc -l) )); then
        color="\033[0;33m"  # Yellow - OK
        status="⚠️ "
    else
        color="\033[0;31m"  # Red - Bad (subutilizado)
        status="❌"
    fi

    # Print real-time
    printf "${color}%s [%4.1f%%] GPU Mem: %4.1f%% | Clock: %4d MHz | Memory: %4d MHz | Power: %2d W${color}\033[0m\n" \
        "$status" "$sm_util" "$mem_util" "$sm_clock" "$mem_clock" "$power_draw"

    # Save to CSV
    echo "$timestamp,$sm_util,$mem_util,$sm_clock,$mem_clock,$power_draw,$ctx_switches" >> "$REPORT_FILE"

    count=$((count + 1))

    # Sleep 1 segundo (ou 2 para menos overhead)
    sleep 2

    # A cada 30 amostras (60 segundos), mostrar média
    if (( count % 30 == 0 )); then
        echo ""
        echo "════════════════════════════════════════════════════════════════"

        # Calcular médias
        sm_avg=$(printf '%s\n' "${sm_values[@]}" | awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "0"}')
        mem_avg=$(printf '%s\n' "${mem_values[@]}" | awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "0"}')

        # Diagnóstico
        if (( $(echo "$sm_avg > 75" | bc -l) )); then
            diag="✅ GPU BEM UTILIZADA"
        elif (( $(echo "$sm_avg > 50" | bc -l) )); then
            diag="⚠️  GPU PARCIALMENTE UTILIZADA"
        else
            diag="❌ GPU SUBUTILIZADA (script problem)"
        fi

        echo "📊 STATS (últimos 60s):"
        echo "   • SM Utilization: ${sm_avg}% → $diag"
        echo "   • Memory Usage: ${mem_avg}%"
        echo "   • Samples: $count"
        echo "   • CSV: $REPORT_FILE"
        echo "════════════════════════════════════════════════════════════════"
        echo ""

        # Reset arrays
        sm_values=()
        mem_values=()
    fi
done
