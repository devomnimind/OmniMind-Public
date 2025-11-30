#!/bin/bash
# Script de Otimização para Execução de Testes OmniMind
# Desativa serviços desnecessários, configura PyTorch e executa testes

set -e

# Parâmetros
GENERATE_DATA="${GENERATE_DATA:-false}"

echo "🚀 Iniciando otimização para execução de testes..."
if [[ "$GENERATE_DATA" == "true" ]]; then
    echo "📊 Modo: Com geração de dados de interação"
else
    echo "🧪 Modo: Apenas testes otimizados"
fi

# Função para log
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a /home/fahbrain/projects/omnimind/data/test_reports/optimization.log
}

# Verificar se estamos na raiz do projeto
if [[ ! -d "/home/fahbrain/projects/omnimind" ]]; then
    echo "❌ Erro: Execute este script da raiz do projeto OmniMind"
    exit 1
fi

cd /home/fahbrain/projects/omnimind

# 1. DESATIVAR SERVIÇOS DESNECESSÁRIOS
log "Desativando serviços desnecessários..."

SERVICOS_DESNECESSARIOS=(
    "cups.service"           # Impressora
    "cups-browsed.service"   # Descoberta de impressoras
    "bluetooth.service"      # Bluetooth (se não usado)
    "ModemManager.service"   # Modem Manager
    "pcscd.service"          # Smart Card
    "colord.service"         # Color management
    "accounts-daemon.service" # Accounts service
    "upower.service"         # Power management (pode afetar bateria)
    "udisks2.service"        # Disk manager (se não montar discos externos)
    "clamav-freshclam.service" # Antivirus updates
    "smartmontools.service"  # SMART monitoring
    "ollama.service"         # Ollama (se não usado nos testes)
    "omnimind-frontend.service" # Frontend (não necessário para testes)
    "omnimind-mcp.service"   # MCP servers (não necessário para testes)
    "omnimind-qdrant.service" # Qdrant (se testes não usarem)
)

SERVICOS_PARADOS=()
for servico in "${SERVICOS_DESNECESSARIOS[@]}"; do
    if systemctl is-active --quiet "$servico" 2>/dev/null; then
        log "Parando serviço: $servico"
        sudo systemctl stop "$servico" || log "Aviso: Não conseguiu parar $servico"
        SERVICOS_PARADOS+=("$servico")
    fi
done

# 2. CONFIGURAR PYTORCH PARA ECONOMIA DE MEMÓRIA
log "Configurando PyTorch para otimização de memória..."

export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,garbage_collection_threshold:0.8
export CUDA_LAUNCH_BLOCKING=0
export TORCH_USE_CUDA_DSA=1
export PYTORCH_NO_CUDA_MEMORY_CACHING=0

# Limpar cache CUDA se possível
python -c "
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print('Cache CUDA limpo')
else:
    print('CUDA não disponível')
" 2>/dev/null || log "Aviso: Não conseguiu limpar cache CUDA"

# 3. OTIMIZAR MEMÓRIA DO SISTEMA
log "Otimizando memória do sistema..."

# Liberar cache do sistema
echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null

# Ajustar swappiness para usar mais swap
echo 80 | sudo tee /proc/sys/vm/swappiness >/dev/null

# 4. CRIAR SWAPFILE EXTRA SE NECESSÁRIO (8GB adicional)
if [[ ! -f /swapfile_extra ]]; then
    log "Criando swapfile extra de 8GB..."
    sudo fallocate -l 8G /swapfile_extra
    sudo chmod 600 /swapfile_extra
    sudo mkswap /swapfile_extra
    sudo swapon /swapfile_extra
    echo '/swapfile_extra none swap sw 0 0' | sudo tee -a /etc/fstab
else
    log "Swapfile extra já existe"
fi

# 5. VERIFICAR STATUS ANTES DOS TESTES
log "Status do sistema antes dos testes:"
free -h | tee -a /home/fahbrain/projects/omnimind/data/test_reports/optimization.log
nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader,nounits | tee -a /home/fahbrain/projects/omnimind/data/test_reports/optimization.log

# 6. EXECUTAR TESTES
log "Executando testes..."

# Ativar ambiente virtual
source .venv/bin/activate

# Comando de teste otimizado
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,garbage_collection_threshold:0.8 \
CUDA_LAUNCH_BLOCKING=0 \
TORCH_USE_CUDA_DSA=1 \
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --maxfail=999 \
  --cov-report=json:data/test_reports/coverage.json \
  --cov-report=html:data/test_reports/htmlcov \
  --log-cli-level=DEBUG \
  --durations=20 -W ignore::DeprecationWarning \
  2>&1 | tee data/test_reports/pytest_output_optimized.log

TEST_EXIT_CODE=$?

# 7. RESTAURAR SERVIÇOS
log "Restaurando serviços..."

for servico in "${SERVICOS_PARADOS[@]}"; do
    log "Reiniciando serviço: $servico"
    sudo systemctl start "$servico" || log "Aviso: Não conseguiu reiniciar $servico"
done

# Remover swapfile extra se criado recentemente
if [[ -f /swapfile_extra ]]; then
    log "Removendo swapfile extra..."
    sudo swapoff /swapfile_extra
    sudo rm /swapfile_extra
    sudo sed -i '/\/swapfile_extra/d' /etc/fstab
fi

# 8. GERAR DADOS DE INTERAÇÃO (OPCIONAL)
if [[ "${GENERATE_DATA:-false}" == "true" ]]; then
    log "Gerando dados de interação automatizados..."
    if [[ -f "./generate_interaction_data.sh" ]]; then
        bash ./generate_interaction_data.sh
    else
        log "Script de geração de dados não encontrado"
    fi
fi</content>
<parameter name="filePath">/home/fahbrain/projects/omnimind/optimize_and_test.sh