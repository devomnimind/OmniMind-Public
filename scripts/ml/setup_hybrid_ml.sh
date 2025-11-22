#!/bin/bash
# Setup Script para ML Híbrido - GitHub Models + Hugging Face
# Configura ambiente completo para treinamento otimizado

set -e

echo "🚀 Configurando ambiente ML Híbrido..."
echo "====================================="

# Verifica se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Execute este script do diretório raiz do projeto (omnimind/)"
    exit 1
fi

# 1. Instala dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Verifica se gh CLI está instalado
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI não encontrado. Instale com: sudo apt install gh"
    exit 1
fi

# Verifica autenticação GitHub
echo "🔐 Verificando autenticação GitHub..."
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI não autenticado. Execute: gh auth login"
    exit 1
fi

# Verifica organização
ORG_STATUS=$(gh api /user/orgs --jq '.[] | select(.login=="devomnimind") | .login')
if [ -z "$ORG_STATUS" ]; then
    echo "⚠️  Organização 'devomnimind' não encontrada ou sem acesso"
else
    echo "✅ Organização 'devomnimind' acessível"
fi

# Verifica Hugging Face
echo "🤗 Verificando Hugging Face..."
python -c "
try:
    from huggingface_hub import HfApi
    api = HfApi()
    user = api.whoami()
    print(f'✅ HF autenticado: {user[\"name\"]}')
except Exception as e:
    print(f'❌ Erro HF: {e}')
    print('Configure token: huggingface-cli login')
"

# 2. Cria estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p logs/ml_cache
mkdir -p data/ml/training_data_collection/models
mkdir -p config/ml

# 3. Testa scripts criados
echo "🧪 Testando scripts..."

# Testa otimizador
echo "   Testando hybrid_ml_optimizer.py..."
python -c "from hybrid_ml_optimizer import HybridMLOptimizer; opt = HybridMLOptimizer(); print('✅ Otimizador OK')"

# Testa CLI
echo "   Testando ml_cli_tool.py..."
python scripts/ml/ml_cli_tool.py limits > /dev/null && echo "✅ CLI Tool OK"

# Testa monitor
echo "   Testando ml_monitor.py..."
python -c "from ml_monitor import MLMonitor; m = MLMonitor(); print('✅ Monitor OK')"

# 4. Cria arquivo de configuração
echo "⚙️  Criando configuração ML..."
cat > config/ml/hybrid_config.json << EOF
{
  "github_models": {
    "enabled": true,
    "rate_limit_buffer": 100,
    "preferred_models": {
      "text_classification": "copilot-chat",
      "code_generation": "copilot-chat", 
      "text_generation": "gpt-4o-mini"
    }
  },
  "hugging_face": {
    "enabled": true,
    "cache_dir": "logs/ml_cache",
    "download_limit_buffer": 1000,
    "upload_limit_buffer": 500
  },
  "monitoring": {
    "enabled": true,
    "check_interval_seconds": 30,
    "alert_thresholds": {
      "github_requests": 100,
      "hf_downloads": 1000,
      "hf_uploads_mb": 500
    }
  },
  "optimization": {
    "auto_fallback": true,
    "cost_optimization": true,
    "local_cache_enabled": true
  }
}
