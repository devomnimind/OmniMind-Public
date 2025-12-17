#!/bin/bash
# Testes de Consciência com GPU obrigatória, monitoramento em tempo real e auditoria

set -e

cd /home/fahbrain/projects/omnimind

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================
export CUDA_VISIBLE_DEVICES=0
export TORCH_HOME=/home/fahbrain/.cache/torch
export PYTHONUNBUFFERED=1

# Criar diretório de logs
mkdir -p data/test_reports

# Nomes de arquivos com timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="data/test_reports/consciousness_gpu_${TIMESTAMP}.log"
GPU_MONITOR_FILE="data/test_reports/gpu_monitor_${TIMESTAMP}.txt"
RESULTS_FILE="data/test_reports/results_${TIMESTAMP}.json"

# ============================================================================
# INÍCIO DO LOG
# ============================================================================
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 OMNIMIND - Testes de Consciência com GPU"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] =========================================="
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 Arquivo de log: $LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📈 Arquivo de métricas GPU: $GPU_MONITOR_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📋 Arquivo de resultados: $RESULTS_FILE"
    echo ""
    
    # ============================================================================
    # VERIFICAÇÃO DE GPU
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔍 Verificando GPU..."
    python3 << 'PYEOF'
import torch
print(f"[CHECK] PyTorch CUDA disponível: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"[CHECK] GPU encontrada: {torch.cuda.get_device_name(0)}")
    print(f"[CHECK] VRAM total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print(f"[CHECK] Compute Capability: {torch.cuda.get_device_capability(0)}")
else:
    print("[ERROR] ❌ GPU NÃO DISPONÍVEL - Testes requerem GPU!")
    exit(1)
PYEOF
    
    GPU_CHECK=$?
    if [ $GPU_CHECK -ne 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ GPU não disponível. Abortando."
        exit 1
    fi
    
    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ GPU verificada e pronta"
    echo ""
    
    # ============================================================================
    # HARDWARE INICIAL
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 Hardware Inicial:"
    echo "---"
    nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv 2>/dev/null || echo "GPU info unavailable"
    echo ""
    free -h
    echo "---"
    echo ""
    
    # ============================================================================
    # INICIAR MONITORAMENTO DE GPU
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🟢 Iniciando monitoramento de GPU em background..."
    python3 scripts/monitor_gpu_tests.py "$GPU_MONITOR_FILE" &
    MONITOR_PID=$!
    sleep 2  # Aguardar monitor inicializar
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Monitor de GPU rodando (PID: $MONITOR_PID)"
    echo ""
    
    # ============================================================================
    # EXECUTAR TESTES COM COLETA DE MÉTRICAS DE Φ
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🧪 Executando testes de consciência..."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 Coletando métricas de Φ em tempo real..."
    echo "=========================================="
    echo ""
    
    # Criar arquivo para métricas de Φ
    PHI_METRICS_FILE="data/test_reports/phi_metrics_${TIMESTAMP}.json"
    
    # Executar pytest com saída colorida, em tempo real, e coleta de Φ
    python -m pytest tests/consciousness/ \
        -v \
        --tb=short \
        --durations=15 \
        --color=yes \
        -s 2>&1 | python scripts/phi_metrics_collector.py || PYTEST_EXIT=$?
    
    PYTEST_EXIT=${PYTEST_EXIT:-0}
    
    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Testes finalizados (exit code: $PYTEST_EXIT)"
    echo ""
    
    # ============================================================================
    # PARAR MONITORAMENTO
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🛑 Parando monitoramento de GPU..."
    kill $MONITOR_PID 2>/dev/null || true
    sleep 2
    
    # ============================================================================
    # HARDWARE FINAL
    # ============================================================================
    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 Hardware Final:"
    echo "---"
    nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.free,temperature.gpu,power.draw --format=csv 2>/dev/null || echo "GPU info unavailable"
    echo ""
    free -h
    echo "---"
    echo ""
    
    # ============================================================================
    # RELATÓRIO FINAL
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📋 Resumo Executivo:"
    echo "=========================================="
    
    if [ $PYTEST_EXIT -eq 0 ]; then
        echo "✅ Status: TODOS OS TESTES PASSARAM"
    else
        echo "❌ Status: ALGUNS TESTES FALHARAM (exit code: $PYTEST_EXIT)"
    fi
    
    echo ""
    echo "Arquivos de saída:"
    echo "  - Log completo: $LOG_FILE"
    echo "  - Métricas GPU: $GPU_MONITOR_FILE"
    echo "  - Detalhes JSON GPU: ${GPU_MONITOR_FILE%.txt}.json"
    echo "  - Métricas Φ JSON: ${PHI_METRICS_FILE}"
    echo "  - Métricas Φ TXT: ${PHI_METRICS_FILE%.json}.txt"
    echo ""
    
    # ============================================================================
    # GERAR ASSINATURA
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔐 Gerando assinatura de auditoria..."
    
    LOG_HASH=$(sha256sum "$LOG_FILE" | awk '{print $1}')
    echo "$LOG_HASH" > "${LOG_FILE}.sha256"
    
    echo "SHA256: $LOG_HASH"
    echo "Arquivo: ${LOG_FILE}.sha256"
    echo ""
    
    # ============================================================================
    # FIM
    # ============================================================================
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Execução Finalizada"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] =========================================="
    
} 2>&1 | tee "$LOG_FILE"

# Capturar exit code do pytest
exit ${PYTEST_EXIT:-0}
