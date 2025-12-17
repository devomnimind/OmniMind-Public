#!/bin/bash

# 🔧 OMNIMIND SYSTEM DIAGNOSTIC - Voltar aos pilares
# Verificar tudo desde o começo

set +e  # Não parar em erros

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

echo "════════════════════════════════════════════════════════════════"
echo "🔧 OMNIMIND SYSTEM DIAGNOSTIC - Verificação Completa"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 1. SERVIÇOS ESSENCIAIS
echo "1️⃣ SERVIÇOS ESSENCIAIS"
echo "─────────────────────────────────────────────────────────────────"

check_service() {
    local name=$1
    local port=$2
    local host=${3:-localhost}

    if timeout 2 bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        echo "✅ $name: Rodando em $host:$port"
        return 0
    else
        echo "❌ $name: NÃO RODANDO (porta $port)"
        return 1
    fi
}

SERVICES_OK=0
check_service "Qdrant" "6333" && SERVICES_OK=$((SERVICES_OK + 1))
check_service "Redis" "6379" && SERVICES_OK=$((SERVICES_OK + 1))
check_service "FastAPI" "8000" || true

echo "   → $SERVICES_OK/2 serviços essenciais rodando"
echo ""

# 2. VARIÁVEIS DE AMBIENTE
echo "2️⃣ VARIÁVEIS DE AMBIENTE"
echo "─────────────────────────────────────────────────────────────────"

env_vars=(
    "PYTORCH_ALLOC_CONF"
    "PYTORCH_DISABLE_DYNAMO"
    "CUDA_VISIBLE_DEVICES"
    "CUDA_LAUNCH_BLOCKING"
    "QISKIT_IN_PARALLEL"
    "OMP_NUM_THREADS"
    "OMNIMIND_DISABLE_RESOURCE_PROTECTOR"
)

for var in "${env_vars[@]}"; do
    value=${!var}
    if [ -z "$value" ]; then
        echo "⚠️  $var: (não set)"
    else
        echo "✅ $var=$value"
    fi
done
echo ""

# 3. PYTHON & DEPENDENCIES
echo "3️⃣ PYTHON & DEPENDENCIES"
echo "─────────────────────────────────────────────────────────────────"

python_version=$(python --version 2>&1)
echo "Python: $python_version"

# Verificar imports críticos
python3 << 'PYTHON_CHECK'
import sys
critical_imports = [
    "torch",
    "qiskit",
    "qiskit_aer",
    "qdrant_client",
    "redis",
    "structlog",
]

for module in critical_imports:
    try:
        __import__(module)
        print(f"✅ {module}: Importável")
    except ImportError as e:
        print(f"❌ {module}: ERRO - {str(e)[:60]}")
        sys.exit(1)
PYTHON_CHECK

echo ""

# 4. CUDA & GPU
echo "4️⃣ CUDA & GPU"
echo "─────────────────────────────────────────────────────────────────"

if command -v nvidia-smi &> /dev/null; then
    echo "✅ nvidia-smi disponível"
    nvidia_info=$(nvidia-smi --query-gpu=name,memory.total,memory.free,utilization.gpu --format=csv,noheader,nounits | head -1)
    echo "   GPU Info: $nvidia_info"

    # Verificar CUDA Capability
    cuda_version=$(nvcc --version 2>/dev/null | grep "release" | awk '{print $5}')
    echo "   CUDA Version: ${cuda_version:-unknown}"
else
    echo "❌ nvidia-smi não encontrado"
fi
echo ""

# 5. MEMORIA & RECURSOS
echo "5️⃣ MEMÓRIA & RECURSOS"
echo "─────────────────────────────────────────────────────────────────"

total_mem=$(free -m | awk 'NR==2{print $2}')
used_mem=$(free -m | awk 'NR==2{print $3}')
free_mem=$(free -m | awk 'NR==2{print $7}')
mem_percent=$((used_mem * 100 / total_mem))

echo "RAM Total: ${total_mem}MB"
echo "RAM Usado: ${used_mem}MB (${mem_percent}%)"
echo "RAM Livre: ${free_mem}MB"

if [ "$mem_percent" -gt 80 ]; then
    echo "⚠️  AVISO: Memória >80% utilizada"
fi

echo ""
echo "Ulimits:"
echo "  Virtual Memory (ulimit -v): $(ulimit -v)"
echo "  Data Segment (ulimit -d): $(ulimit -d)"
echo "  Max Processes (ulimit -u): $(ulimit -u)"
echo ""

# 6. SISTEMA DE ARQUIVOS
echo "6️⃣ SISTEMA DE ARQUIVOS"
echo "─────────────────────────────────────────────────────────────────"

disk_usage=$(df -h "$PROJECT_ROOT" | awk 'NR==2{print $5}' | sed 's/%//')
echo "Uso de disco: ${disk_usage}%"

if [ "$disk_usage" -gt 80 ]; then
    echo "⚠️  AVISO: Disco >80% preenchido"
fi

# Verificar se diretórios críticos existem
for dir in logs data config src; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/: Existe"
    else
        echo "❌ $dir/: FALTA"
    fi
done
echo ""

# 7. PROCESSOS OMNIMIND RODANDO
echo "7️⃣ PROCESSOS OMNIMIND RODANDO"
echo "─────────────────────────────────────────────────────────────────"

omnimind_procs=$(ps aux | grep -E "(omnimind|python.*main)" | grep -v grep | wc -l)
echo "Processos OmniMind: $omnimind_procs"

python_procs=$(ps aux | grep python | grep -v grep | wc -l)
echo "Total processos Python: $python_procs"
echo ""

# 8. VERIFICAÇÃO RÁPIDA DE IMPORTS
echo "8️⃣ IMPORTS CRÍTICOS"
echo "─────────────────────────────────────────────────────────────────"

python3 << 'IMPORT_CHECK'
import sys
sys.path.insert(0, 'src')

try:
    from consciousness.integration_loop import IntegrationLoop
    print("✅ IntegrationLoop: Importável")

    loop = IntegrationLoop()
    print("✅ IntegrationLoop: Instanciável")

    # Verificar método
    if hasattr(loop, 'execute_cycle_sync'):
        print("✅ execute_cycle_sync(): Disponível")
    else:
        print("❌ execute_cycle_sync(): NÃO ENCONTRADO")

except Exception as e:
    print(f"❌ Erro ao carregar IntegrationLoop: {str(e)[:100]}")
    import traceback
    traceback.print_exc()
IMPORT_CHECK

echo ""

# 9. TESTE MÍNIMO
echo "9️⃣ TESTE MÍNIMO (1 ciclo)"
echo "─────────────────────────────────────────────────────────────────"

python3 << 'MINIMAL_TEST'
import sys
import time
sys.path.insert(0, 'src')

try:
    from consciousness.integration_loop import IntegrationLoop

    print("Iniciando IntegrationLoop...")
    loop = IntegrationLoop()

    print("Executando 1 ciclo...")
    start = time.time()
    result = loop.execute_cycle_sync(collect_metrics=True)
    elapsed = time.time() - start

    print(f"✅ Ciclo 1 completado em {elapsed:.1f}s")
    print(f"   Φ={result.phi_estimate:.4f}")
    print(f"   Duration: {result.cycle_duration_ms:.1f}ms")

except Exception as e:
    print(f"❌ ERRO NO TESTE: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
MINIMAL_TEST

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ DIAGNÓSTICO COMPLETO"
echo "════════════════════════════════════════════════════════════════"
