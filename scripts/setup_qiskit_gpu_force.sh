#!/bin/bash
# Script para forçar configuração de GPU para Qiskit de forma persistente
# Independente da máquina - detecta automaticamente paths CUDA

set -e

echo "🔧 Configurando GPU para Qiskit (forçado, independente de máquina)"
echo "=================================================================="

# 1. Detectar CUDA automaticamente
CUDA_PATHS=(
    "/usr/local/cuda"
    "/usr/local/cuda-12.4"
    "/usr/local/cuda-12.0"
    "/usr/local/cuda-11.8"
    "/opt/cuda"
    "/usr"
)

CUDA_HOME_FOUND=""
for path in "${CUDA_PATHS[@]}"; do
    if [ -d "$path" ] && [ -f "$path/bin/nvcc" ] || [ -d "$path/lib64" ]; then
        CUDA_HOME_FOUND="$path"
        echo "✅ CUDA detectado em: $path"
        break
    fi
done

if [ -z "$CUDA_HOME_FOUND" ]; then
    # Fallback: usar /usr (padrão Debian/Kali)
    CUDA_HOME_FOUND="/usr"
    echo "⚠️  CUDA não detectado automaticamente, usando: $CUDA_HOME_FOUND"
fi

# 2. Detectar libs CUDA
CUDA_LIB_PATHS=(
    "$CUDA_HOME_FOUND/lib64"
    "$CUDA_HOME_FOUND/lib"
    "/usr/lib/x86_64-linux-gnu"
    "/usr/local/cuda/lib64"
)

LD_LIBRARY_PATH_NEW=""
for path in "${CUDA_LIB_PATHS[@]}"; do
    if [ -d "$path" ] && [ -f "$path/libcudart.so" ] 2>/dev/null || [ -f "$path/libcudart.so.*" ] 2>/dev/null; then
        if [ -z "$LD_LIBRARY_PATH_NEW" ]; then
            LD_LIBRARY_PATH_NEW="$path"
        else
            LD_LIBRARY_PATH_NEW="$LD_LIBRARY_PATH_NEW:$path"
        fi
        echo "✅ CUDA libs detectadas em: $path"
    fi
done

if [ -z "$LD_LIBRARY_PATH_NEW" ]; then
    LD_LIBRARY_PATH_NEW="/usr/lib/x86_64-linux-gnu"
    echo "⚠️  CUDA libs não detectadas, usando: $LD_LIBRARY_PATH_NEW"
fi

# 3. Configurar variáveis de ambiente
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export CUDA_HOME="$CUDA_HOME_FOUND"
export CUDA_PATH="$CUDA_HOME_FOUND"

# Adicionar ao LD_LIBRARY_PATH existente
if [ -n "$LD_LIBRARY_PATH" ]; then
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH_NEW:$LD_LIBRARY_PATH"
else
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH_NEW"
fi

# 4. Verificar se qiskit-aer-gpu está instalado
echo ""
echo "📦 Verificando qiskit-aer-gpu..."
QISKIT_AER_GPU_INSTALLED=false

# Verificar se pode importar qiskit_aer com device="GPU"
if python3 << 'PYTHON_TEST' 2>/dev/null | grep -q "OK"; then
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['CUDA_HOME'] = '$CUDA_HOME_FOUND'
os.environ['CUDA_PATH'] = '$CUDA_HOME_FOUND'
os.environ['LD_LIBRARY_PATH'] = '$LD_LIBRARY_PATH_NEW'
try:
    from qiskit_aer import AerSimulator
    backend = AerSimulator(method='statevector', device='GPU')
    print('OK')
except Exception:
    pass
PYTHON_TEST
    QISKIT_AER_GPU_INSTALLED=true
    echo "✅ qiskit-aer-gpu está instalado e funcional"
else
    echo "❌ qiskit-aer-gpu NÃO está instalado ou não funciona"
    echo "   Execute: ./scripts/fix_qiskit_gpu.sh"
fi

# 5. Testar Qiskit GPU
echo ""
echo "🧪 Testando Qiskit GPU..."
python3 << 'PYTHON_EOF'
import os
import sys

# Configurar variáveis (já exportadas pelo shell)
os.environ['CUDA_VISIBLE_DEVICES'] = os.environ.get('CUDA_VISIBLE_DEVICES', '0')
os.environ['CUDA_HOME'] = os.environ.get('CUDA_HOME', '/usr')
os.environ['CUDA_PATH'] = os.environ.get('CUDA_PATH', '/usr')
os.environ['LD_LIBRARY_PATH'] = os.environ.get('LD_LIBRARY_PATH', '/usr/lib/x86_64-linux-gnu')

try:
    from qiskit_aer import AerSimulator
    print("✅ qiskit_aer importado")

    try:
        backend = AerSimulator(method="statevector", device="GPU")
        print("✅ AerSimulator GPU criado com sucesso")
        print(f"   Backend: {backend}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro ao criar AerSimulator GPU: {e}")
        print("   Tentando CPU...")
        backend = AerSimulator()
        print("⚠️  AerSimulator CPU criado (GPU falhou)")
        sys.exit(1)
except ImportError as e:
    print(f"❌ Erro ao importar qiskit_aer: {e}")
    print("   Execute: pip install qiskit-aer-gpu")
    sys.exit(1)
PYTHON_EOF

TEST_RESULT=$?

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ Qiskit GPU configurado com sucesso!"
    echo ""
    echo "📝 Para usar em scripts Python, adicione no início:"
    echo "   source $(pwd)/scripts/setup_qiskit_gpu_force.sh"
    echo ""
    echo "   Ou configure manualmente:"
    echo "   export CUDA_VISIBLE_DEVICES=0"
    echo "   export CUDA_HOME=$CUDA_HOME_FOUND"
    echo "   export CUDA_PATH=$CUDA_HOME_FOUND"
    echo "   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
else
    echo "⚠️  Qiskit GPU não pôde ser configurado"
    echo "   Verifique:"
    echo "   1. qiskit-aer-gpu está instalado: pip install qiskit-aer-gpu"
    echo "   2. CUDA está instalado e acessível"
    echo "   3. Variáveis de ambiente estão corretas"
fi

