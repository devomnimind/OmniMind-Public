#!/bin/bash
# Script para corrigir e forçar Qiskit GPU de forma persistente
# Resolve problemas de instalação e configuração

# NÃO usar set -e para permitir tratamento de erros

echo "🔧 CORREÇÃO E FORÇA DE QISKIT GPU"
echo "=================================="
echo ""

# 1. Ativar venv se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Venv ativado"
fi

# 2. Desinstalar versões conflitantes
echo ""
echo "🧹 Limpando instalações conflitantes..."
echo "   (Isso pode levar alguns segundos...)"

# Desinstalar TODOS os pacotes Qiskit relacionados
pip uninstall -y qiskit-aer-gpu qiskit-aer qiskit-terra qiskit-ibm-runtime qiskit-ibm-provider qiskit qiskit-nature qiskit-optimization qiskit-machine-learning qiskit-algorithms 2>/dev/null || true

# Verificar se desinstalou completamente
if python3 -c "import qiskit" 2>/dev/null; then
    echo "⚠️  qiskit ainda está instalado, forçando desinstalação..."
    pip uninstall -y qiskit --break-system-packages 2>/dev/null || true
    # Limpar cache do pip
    pip cache purge 2>/dev/null || true
fi

# Verificar novamente
if python3 -c "import qiskit" 2>/dev/null; then
    echo "❌ ERRO: qiskit ainda está instalado após desinstalação"
    echo "   Execute manualmente: pip uninstall -y qiskit qiskit-aer qiskit-aer-gpu"
    exit 1
fi

echo "✅ Limpeza concluída (todos os pacotes Qiskit removidos)"

# 3. Instalar qiskit-aer-gpu (inclui qiskit-aer)
echo ""
echo "📦 Instalando qiskit-aer-gpu..."
echo "   (Isso pode levar alguns minutos...)"

# CRITICAL: qiskit-aer-gpu 0.15.x NÃO é compatível com Qiskit 2.0+
# convert_to_target foi REMOVIDO em Qiskit 2.0, mas qiskit-aer-gpu 0.15.x ainda tenta importar
# SOLUÇÃO: Usar Qiskit 1.3.x (LTS) que é compatível com qiskit-aer-gpu 0.15.x
echo "   ⚠️  IMPORTANTE: qiskit-aer-gpu 0.15.x requer Qiskit 1.3.x (não 2.0+)"
echo "   Qiskit 2.0+ removeu convert_to_target, quebrando compatibilidade"
echo "   Instalando Qiskit 1.3.x (LTS) + qiskit-aer-gpu 0.15.x..."

# Passo 1: Instalar Qiskit 1.3.x (LTS - compatível com GPU)
echo "   Passo 1: Instalando qiskit>=1.3.0,<2.0.0 (LTS)..."
if pip install --no-cache-dir "qiskit>=1.3.0,<2.0.0"; then
    QISKIT_VER=$(python3 -c "import qiskit; print(qiskit.__version__)" 2>/dev/null)
    echo "   ✅ qiskit instalado: $QISKIT_VER"
else
    echo "   ❌ Falha ao instalar qiskit"
    exit 1
fi

# Passo 2: Instalar qiskit-aer-gpu (compatível com Qiskit 1.3.x)
echo "   Passo 2: Instalando qiskit-aer-gpu>=0.15.0..."
if pip install --no-cache-dir "qiskit-aer-gpu>=0.15.0"; then
    echo "   ✅ qiskit-aer-gpu instalado com sucesso"
else
    echo "   ⚠️  Falha ao instalar qiskit-aer-gpu, tentando qiskit-aer (CPU)..."
    if pip install --no-cache-dir "qiskit-aer>=0.15.0"; then
        echo "   ✅ qiskit-aer instalado (CPU apenas)"
        echo "   ⚠️  Nota: GPU pode não estar disponível"
    else
        echo "   ❌ Falha crítica na instalação"
        echo ""
        echo "   Execute manualmente:"
        echo "   pip install 'qiskit>=1.3.0,<2.0.0' 'qiskit-aer-gpu>=0.15.0'"
        exit 1
    fi
fi

# Verificar instalação
echo ""
echo "🔍 Verificando instalação..."
python3 << 'PYTHON_VERIFY'
import os
import sys

# Configurar CUDA
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['CUDA_HOME'] = os.environ.get('CUDA_HOME', '/usr')
os.environ['CUDA_PATH'] = os.environ.get('CUDA_PATH', '/usr')
ld_lib = os.environ.get('LD_LIBRARY_PATH', '')
if '/usr/lib/x86_64-linux-gnu' not in ld_lib:
    os.environ['LD_LIBRARY_PATH'] = f"/usr/lib/x86_64-linux-gnu:{ld_lib}" if ld_lib else "/usr/lib/x86_64-linux-gnu"

try:
    from qiskit_aer import AerSimulator
    print("✅ qiskit_aer importado com sucesso")

    # Tentar GPU
    try:
        backend = AerSimulator(method="statevector", device="GPU")
        print("✅ AerSimulator GPU criado com sucesso")
        print("   qiskit-aer-gpu está funcional!")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️  GPU não disponível: {e}")
        # Tentar CPU como fallback
        backend = AerSimulator()
        print("✅ AerSimulator CPU criado")
        print("   qiskit-aer instalado (GPU pode não estar disponível)")
        sys.exit(0)
except ImportError as e:
    print(f"❌ Erro ao importar qiskit_aer: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    sys.exit(1)
PYTHON_VERIFY

VERIFY_RESULT=$?

if [ $VERIFY_RESULT -eq 0 ]; then
    echo "✅ Instalação verificada com sucesso"
else
    echo "❌ Falha na verificação da instalação"
    exit 1
fi

# 4. Executar setup de GPU
echo ""
echo "🔧 Configurando GPU..."
bash scripts/setup_qiskit_gpu_force.sh

echo ""
echo "✅ Correção concluída!"
echo ""
echo "📝 Para usar em scripts Python:"
echo "   source scripts/setup_qiskit_gpu_force.sh"
echo "   python scripts/run_200_cycles_verbose.py"

