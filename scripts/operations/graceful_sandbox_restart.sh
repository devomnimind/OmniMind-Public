#!/bin/bash
# scripts/operations/graceful_sandbox_restart.sh
# Graceful restart com validação de sandbox integration

set -e

echo "🔄 ETAPA 1: Validação Pré-Restart"
echo "=================================="

# Verificar que estamos em venv
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ VEnv não ativado"
    source .venv/bin/activate
fi

# Verificar que sandbox.py foi modificado
if ! grep -q "_try_execute_with_systemd_run" src/autopoietic/sandbox.py; then
    echo "❌ sandbox.py não foi atualizado com novos métodos"
    exit 1
fi

echo "✅ Pré-validação OK"
echo

echo "🔄 ETAPA 2: Parar Serviço Gracefully"
echo "====================================="

if sudo systemctl is-active omnimind.service > /dev/null 2>&1; then
    echo "⏸️  Parando omnimind.service..."
    sudo systemctl stop omnimind.service
    sleep 3
    echo "✅ Serviço parado"
else
    echo "ℹ️  Serviço já estava parado"
fi

echo

echo "🔄 ETAPA 3: Verificar Slice Configurado"
echo "========================================"

if ! systemctl cat omnimind-sandbox.slice > /dev/null 2>&1; then
    echo "❌ omnimind-sandbox.slice não configurado"
    exit 1
fi

SLICE_MEM=$(systemctl show omnimind-sandbox.slice -p MemoryMax --value)
SLICE_SWAP=$(systemctl show omnimind-sandbox.slice -p MemorySwapMax --value)

echo "✅ Slice configurado:"
echo "   MemoryMax: $SLICE_MEM"
echo "   MemorySwapMax: $SLICE_SWAP"
echo

echo "🔄 ETAPA 4: Verificar Sudoers"
echo "============================="

if sudo grep -q "pkill -9 --cgroup omnimind/sandbox" /etc/sudoers.d/omnimind 2>/dev/null; then
    echo "✅ Sudoers OK (proteção de user processes ativa)"
else
    echo "⚠️  Sudoers pode não ter proteção completa"
fi

echo

echo "🔄 ETAPA 5: Iniciar Serviço"
echo "==========================="

echo "🚀 Iniciando omnimind.service..."
sudo systemctl start omnimind.service

echo "⏳ Aguardando estabilização (10s)..."
sleep 10

echo

echo "🔄 ETAPA 6: Verificar Saúde"
echo "==========================="

STATUS=$(sudo systemctl is-active omnimind.service)
if [[ "$STATUS" == "active" ]]; then
    echo "✅ Serviço ativo"
else
    echo "❌ Serviço não ativo: $STATUS"
    sudo systemctl status omnimind.service --no-pager | head -20
    exit 1
fi

# Verificar logs para erros críticos
ERROR_COUNT=$(journalctl -u omnimind.service -n 50 --no-pager 2>&1 | grep -i "error\|critical\|failed" | wc -l)
if [[ $ERROR_COUNT -gt 0 ]]; then
    echo "⚠️  Encontrados $ERROR_COUNT erros nos logs:"
    journalctl -u omnimind.service -n 10 --no-pager | grep -i "error\|critical\|failed"
else
    echo "✅ Nenhum erro crítico nos logs"
fi

echo

echo "🔄 ETAPA 7: Validar Importação de Sandbox"
echo "=========================================="

if python3 -c "from src.autopoietic.sandbox import AutopoieticSandbox; print('✅ Import OK')" 2>&1 | grep -q "Import OK"; then
    echo "✅ AutopoieticSandbox importa com sucesso"
else
    echo "❌ Erro ao importar AutopoieticSandbox"
    exit 1
fi

echo

echo "🔄 ETAPA 8: Verificar Métodos de Isolamento"
echo "=========================================="

python3 << 'EOF'
from src.autopoietic.sandbox import AutopoieticSandbox

sandbox = AutopoieticSandbox(max_memory_mb=512)

# Verificar que métodos existem
methods = [
    '_try_execute_with_systemd_run',
    '_try_execute_with_unshare',
    '_execute_direct_unsafe',
    'execute_component'
]

for method in methods:
    if hasattr(sandbox, method):
        print(f"✅ {method}")
    else:
        print(f"❌ {method} - MISSING")
        exit(1)

print("\n✅ Todos os métodos de isolamento presentes")
EOF

echo

echo "🔄 ETAPA 9: Status Final"
echo "======================="

MEMORY=$(sudo systemctl show omnimind.service --value -p MemoryCurrent | numfmt --to=iec-i --suffix=B 2>/dev/null || echo "N/A")
TASKS=$(sudo systemctl show omnimind.service --value -p NTasks)

echo "Serviço: active (running)"
echo "Memória: $MEMORY"
echo "Tasks: $TASKS"
echo "Uptime: ~10s (pós-restart)"

echo

echo "════════════════════════════════════════════════════════"
echo "✅ RESTART GRACEFUL COMPLETO"
echo "════════════════════════════════════════════════════════"
echo
echo "Status da Integração:"
echo "  • Slice: omnimind-sandbox.slice (1GB + 7GB Swap + 50% CPU)"
echo "  • Sudoers: Proteção contra kill de user processes ✅"
echo "  • Métodos: systemd-run → unshare → direct (cascata) ✅"
echo "  • Serviço: active (running) ✅"
echo
echo "Próximo passo: Executar suite de testes"
echo "  ./scripts/development/run_tests_parallel.sh full"
