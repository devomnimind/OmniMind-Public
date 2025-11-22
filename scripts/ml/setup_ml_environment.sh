#!/bin/bash
# Script de Setup para Treinamento ML Local/Remoto

echo "🚀 Iniciando setup de ambiente ML/AI..."

# Instalar PyTorch CPU-only
echo "📦 Instalando PyTorch CPU..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Instalar bibliotecas essenciais
echo "📦 Instalando bibliotecas ML..."
pip install transformers accelerate peft datasets evaluate

# Instalar ferramentas de desenvolvimento
echo "🛠️ Instalando ferramentas de desenvolvimento..."
pip install jupyterlab mlflow streamlit gradio

# Configurar GitHub CLI (se disponível)
echo "🔑 Configurando GitHub CLI..."
if command -v gh &> /dev/null; then
    echo "GitHub CLI encontrado. Execute: gh auth login"
else
    echo "GitHub CLI não encontrado. Instale com: sudo apt install gh"
fi

# Verificar instalação
echo "✅ Verificando instalação..."
python3 -c "
import torch
import transformers
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
print(f'Transformers: {transformers.__version__}')
print('Setup concluído!')
"

echo "🎯 Setup completo! Próximos passos:"
echo "1. Configure tokens API (GitHub, etc.)"
echo "2. Teste com dados de treinamento"
echo "3. Comece experimentos locais"
