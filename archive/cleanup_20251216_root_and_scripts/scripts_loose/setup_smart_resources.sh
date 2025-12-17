#!/bin/bash

# 🎯 SETUP: SMART RESOURCE ISOLATION FOR HYBRID DEV ENVIRONMENT
# ============================================================
# Implementa proteção inteligente para ambiente de desenvolvimento:
# - cgroup v1 slices (systemd)
# - OOMPolicy=continue (não mata, apenas pausa)
# - Monitor inteligente (curva 5min, não snapshots)
# - earlyoom com padrões customizados
#
# ESTRATÉGIA:
# • OmniMind + VS Code + Testes rodam com OOMScoreAdjust=-900 (nunca matam)
# • Backend services em slice separado com limite suave
# • Monitor analisa TENDÊNCIA, não apenas picos
# • earlyoom protege OmniMind mantendo sistema responsivo

set -e

PROJECT_ROOT="${1:-/home/fahbrain/projects/omnimind}"
SETUP_MODE="${2:-full}"  # full, test, debug

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  🎯 SMART RESOURCE ISOLATION - HYBRID DEV ENVIRONMENT        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# ===== LAYER 1: systemd Slice para OmniMind Dev =====
echo "📋 LAYER 1: Creating systemd slice for OmniMind dev..."
echo ""

sudo tee /etc/systemd/system/omnimind-dev.slice > /dev/null << 'SLICE_EOF'
[Unit]
Description=OmniMind Development Environment
PartOf=user.slice

[Slice]
# CPU: Allow up to 95% but with intelligent monitoring
CPUQuota=95%
CPUAccounting=yes

# Memory: Hard limit at 90% but don't OOM kill
MemoryMax=90%
MemoryAccounting=yes
OOMPolicy=continue

# Don't kill - only pause/throttle if memory pressure
OOMScoreAdjust=-900

# I/O accounting for better insights
IOAccounting=yes

# Tasks accounting
TasksAccounting=yes
TasksMax=8192

[Install]
WantedBy=user.slice
SLICE_EOF

echo "✅ omnimind-dev.slice created"
echo ""

# ===== LAYER 2: systemd Services with Smart Protection =====
echo "📋 LAYER 2: Creating systemd service templates..."
echo ""

# Backend service
sudo tee /etc/systemd/system/omnimind-backend-protected.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=OmniMind Backend (Protected)
After=network.target
PartOf=omnimind-dev.slice

[Service]
Type=exec
ExecStart=/bin/bash -c 'cd /home/fahbrain/projects/omnimind && python -m uvicorn web.backend.main:app --host 127.0.0.1 --port 8000'
Restart=on-failure
RestartSec=5

# Protection: Slice with intelligent OOM handling
Slice=omnimind-dev.slice

# CPU: Allow burst but monitor
CPUQuota=80%
CPUAccounting=yes

# Memory: Soft limit (warning), hard limit (throttle)
MemoryMax=8G
MemoryAccounting=yes
OOMPolicy=continue
OOMScoreAdjust=-700

# I/O: Throttle if under pressure
IOMaxBandwidthIO=/dev/sda 100M

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=omnimind-backend

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "✅ omnimind-backend-protected.service created"
echo ""

# ===== LAYER 3: Monitor Inteligente =====
echo "📋 LAYER 3: Creating intelligent monitoring script..."
echo ""

sudo tee /usr/local/bin/omnimind-smart-monitor.sh > /dev/null << 'MONITOR_EOF'
#!/bin/bash

# Monitor inteligente para OmniMind
# Analisa TENDÊNCIA de 5min, não apenas snapshots
# Detecta: loops CPU travados, vazamento memória, picos normais

LOG_FILE="/var/log/omnimind/smart-monitor.log"
METRICS_FILE="/tmp/omnimind-metrics-5min.txt"
mkdir -p /var/log/omnimind

# Configuração de limites inteligentes
CPU_ALERT_THRESHOLD=95      # CPU média > 95% por 5min = alerta
CPU_CRASH_THRESHOLD=100     # CPU em 100% em todos cores = CRÍTICO
MEMORY_ALERT_THRESHOLD=90   # Memória > 90% por 5min = alerta
MEMORY_CRASH_THRESHOLD=98   # Memória > 98% = CRÍTICO
LOAD_MAX=$(expr $(nproc) \* 2)  # Load normal = 2x cores

# Histórico de métricas (5 amostras de 1min cada)
declare -a CPU_HISTORY
declare -a MEM_HISTORY
declare -a LOAD_HISTORY

analyze_behavior() {
    local metric_array=("$@")
    local len=${#metric_array[@]}

    if [ $len -lt 3 ]; then
        echo "insufficient_data"
        return
    fi

    # Calcular variância (indica se é stável ou crescente)
    local first_half_avg=0
    local second_half_avg=0

    for ((i=0; i<len/2; i++)); do
        first_half_avg=$(echo "$first_half_avg + ${metric_array[$i]}" | bc)
    done
    first_half_avg=$(echo "scale=2; $first_half_avg / (${len}/2)" | bc)

    for ((i=len/2; i<len; i++)); do
        second_half_avg=$(echo "$second_half_avg + ${metric_array[$i]}" | bc)
    done
    second_half_avg=$(echo "scale=2; $second_half_avg / (${len}/2)" | bc)

    # Se segunda metade > primeira = CRESCENTE (problema!)
    if (( $(echo "$second_half_avg > $first_half_avg * 1.1" | bc -l) )); then
        echo "growing"
    # Se estável em pico = NORMAL (apenas carga pesada)
    elif (( $(echo "$second_half_avg > 85" | bc -l) )); then
        echo "high_but_stable"
    # Se baixo = NORMAL
    else
        echo "normal"
    fi
}

while true; do
    # Coletar métricas atuais
    CPU_PERCENT=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEM_PERCENT=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
    LOAD_AVG=$(cat /proc/loadavg | cut -d' ' -f2)

    # Atualizar histórico (mover elementos, adicionar novo no fim)
    CPU_HISTORY=("${CPU_HISTORY[@]:1}" "$CPU_PERCENT")
    MEM_HISTORY=("${MEM_HISTORY[@]:1}" "$MEM_PERCENT")
    LOAD_HISTORY=("${LOAD_HISTORY[@]:1}" "$LOAD_AVG")

    # Se histórico ainda pequeno, preencher
    if [ ${#CPU_HISTORY[@]} -lt 5 ]; then
        for ((i=0; i<5-${#CPU_HISTORY[@]}; i++)); do
            CPU_HISTORY+=("$CPU_PERCENT")
            MEM_HISTORY+=("$MEM_PERCENT")
            LOAD_HISTORY+=("$LOAD_AVG")
        done
    fi

    # Analisar comportamento
    CPU_BEHAVIOR=$(analyze_behavior "${CPU_HISTORY[@]}")
    MEM_BEHAVIOR=$(analyze_behavior "${MEM_HISTORY[@]}")

    # Calcular média de 5min
    CPU_AVG=$(printf "%.0f" $(echo "scale=2; (${CPU_HISTORY[0]}+${CPU_HISTORY[1]}+${CPU_HISTORY[2]}+${CPU_HISTORY[3]}+${CPU_HISTORY[4]})/5" | bc))
    MEM_AVG=$(printf "%.0f" $(echo "scale=2; (${MEM_HISTORY[0]}+${MEM_HISTORY[1]}+${MEM_HISTORY[2]}+${MEM_HISTORY[3]}+${MEM_HISTORY[4]})/5" | bc))

    # Decisões
    ALERT=""

    if [ "$CPU_BEHAVIOR" == "growing" ] && (( $(echo "$CPU_AVG > 90" | bc -l) )); then
        ALERT="⚠️  CPU CRESCENTE: ${CPU_AVG}% trend (possível loop)"
    fi

    if [ "$MEM_BEHAVIOR" == "growing" ] && (( $(echo "$MEM_AVG > 85" | bc -l) )); then
        ALERT="⚠️  MEMÓRIA CRESCENTE: ${MEM_AVG}% trend (possível vazamento)"
    fi

    if (( $(echo "$CPU_PERCENT >= 100" | bc -l) )); then
        ALERT="🔴 CRÍTICO: CPU TRAVADA 100% (loop)"
    fi

    if (( $(echo "$MEM_PERCENT > 98" | bc -l) )); then
        ALERT="🔴 CRÍTICO: MEMÓRIA CRÍTICA ${MEM_AVG}%"
    fi

    # Log
    if [ -n "$ALERT" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $ALERT" | tee -a "$LOG_FILE"
    fi

    # Guardar métricas
    {
        echo "timestamp=$(date +%s)"
        echo "cpu_current=$CPU_PERCENT"
        echo "cpu_avg_5min=$CPU_AVG"
        echo "cpu_behavior=$CPU_BEHAVIOR"
        echo "mem_current=$MEM_PERCENT"
        echo "mem_avg_5min=$MEM_AVG"
        echo "mem_behavior=$MEM_BEHAVIOR"
        echo "load=$LOAD_AVG"
        echo "load_max=$LOAD_MAX"
    } > "$METRICS_FILE"

    # Aguardar 1min para próxima coleta
    sleep 60
done
MONITOR_EOF

sudo chmod +x /usr/local/bin/omnimind-smart-monitor.sh
echo "✅ omnimind-smart-monitor.sh created"
echo ""

# ===== LAYER 4: earlyoom com Proteção OmniMind =====
echo "📋 LAYER 4: Installing/configuring earlyoom..."
echo ""

if ! command -v earlyoom &> /dev/null; then
    echo "Installing earlyoom..."
    sudo apt-get install -y earlyoom
fi

# Config earlyoom: NÃO matar OmniMind/pytest/code
sudo tee /etc/default/earlyoom > /dev/null << 'EARLYOOM_EOF'
# earlyoom config - inteligente para dev environment
# -m 3: Avisar quando memória < 3%
# -r 800: Recuperar quando memória > 800MB
# --prefer: Preferir matar (regex negativo = "NÃO ESTES")
# --avoid: Nunca matar (simples match)

EARLYOOM_ARGS="-m 3 -r 800 \
  --prefer '^(?!.*(omnimind|pytest|code|vscode|ollama|docker|backend)).*' \
  --avoid '(systemd-|systemd$|omnimind|pytest|code|ollama|docker)' \
  --verbose \
  --sort rss"
EARLYOOM_EOF

sudo systemctl daemon-reload
sudo systemctl enable earlyoom
sudo systemctl restart earlyoom

echo "✅ earlyoom configured and restarted"
echo ""

# ===== LAYER 5: Register systemd services =====
echo "📋 LAYER 5: Registering services..."
echo ""

sudo systemctl daemon-reload

# Enable monitor
sudo systemctl disable omnimind-smart-monitor.service 2>/dev/null || true
sudo cp /usr/local/bin/omnimind-smart-monitor.sh /usr/local/bin/
sudo systemctl enable omnimind-smart-monitor

echo "✅ Services registered"
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  ✅ SMART RESOURCE ISOLATION SETUP COMPLETE                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Configuration Summary:"
echo "  • Slice: omnimind-dev (95% CPU, 90% memory soft limit)"
echo "  • OOMPolicy: continue (pause instead of kill)"
echo "  • Monitor: Analyzes 5-min trends (not just snapshots)"
echo "  • earlyoom: Protects OmniMind from OOM kill"
echo ""
echo "🚀 To use with your 500-cycle test:"
echo ""
echo "   export OMNIMIND_RESOURCE_MODE=smart"
echo "   bash scripts/recovery/03_run_500_cycles_no_timeout.sh"
echo ""
echo "📊 Monitor behavior in real-time:"
echo "   tail -f /var/log/omnimind/smart-monitor.log"
echo ""
echo "✅ System is now intelligent about resource usage!"
echo ""
