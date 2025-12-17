#!/bin/bash
# Test runner com auto-restart do servidor e timestamps
# Uso: ./run_tests_with_server.sh [cpu|gpu]

DEVICE="${1:-cpu}"

# Configurar device
if [ "$DEVICE" = "gpu" ]; then
    export CUDA_VISIBLE_DEVICES=0
    export TORCH_HOME=/home/fahbrain/.cache/torch
    export TF_FORCE_GPU_MEMORY_GROWTH=true
    DEVICE_NAME="GPU (NVIDIA GTX 1650)"
else
    export CUDA_VISIBLE_DEVICES=""
    DEVICE_NAME="CPU"
fi

cd /home/fahbrain/projects/omnimind

# Criar diretório de logs
mkdir -p data/test_reports

# Arquivo de log com timestamp
LOG_FILE="data/test_reports/test_$(date +%Y%m%d_%H%M%S).log"

# Função para verificar se servidor está up
check_server() {
    curl -s http://localhost:8000/health/ > /dev/null 2>&1
    return $?
}

# Função para reiniciar servidor
restart_server() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚙️  Reiniciando servidor..." | tee -a "$LOG_FILE"
    
    # Usar subshell para não mudar diretório do script principal
    (
        cd /home/fahbrain/projects/omnimind/deploy
        docker-compose down > /dev/null 2>&1
        docker-compose up -d > /dev/null 2>&1
    )
    
    # Aguardar servidor ficar ready
    for i in {1..60}; do
        if check_server; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Servidor restaurado (tentativa $i)" | tee -a "$LOG_FILE"
            return 0
        fi
        sleep 1
    done
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Servidor não respondeu após 60s" | tee -a "$LOG_FILE"
    return 1
}

# Verificar servidor antes de começar
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔍 Verificando servidor..." | tee "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Device: $DEVICE_NAME" | tee -a "$LOG_FILE"
if ! check_server; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  Servidor offline, iniciando..." | tee -a "$LOG_FILE"
    restart_server
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Servidor OK, iniciando testes..." | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Rodar testes com monitoramento
{
    python -m pytest tests/ -v --tb=short -x --maxfail=1 2>&1 | while IFS= read -r line; do
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] $line"
        
        # Detectar se servidor caiu
        if echo "$line" | grep -q "ConnectionError\|Failed to establish\|refused\|unreachable"; then
            echo "[$timestamp] ⚠️  Servidor pode ter caído, verificando..." 
            if ! check_server; then
                echo "[$timestamp] 🔴 Servidor DOWN! Reiniciando..."
                restart_server
                echo "[$timestamp] Retomando testes..."
            fi
        fi
    done
} | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📁 Log salvo: $LOG_FILE" | tee -a "$LOG_FILE"

# Gerar Assinatura Digital do Log (Validação Científica)
LOG_HASH=$(sha256sum "$LOG_FILE" | awk '{print $1}')
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔐 Assinatura SHA256: $LOG_HASH" | tee -a "$LOG_FILE"
echo "$LOG_HASH" > "${LOG_FILE}.sha256"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📄 Arquivo de assinatura gerado: ${LOG_FILE}.sha256" | tee -a "$LOG_FILE"
