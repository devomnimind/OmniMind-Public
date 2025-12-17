#!/bin/bash

# 🧪 TESTE COMPARATIVO: 1 Worker vs 2 Workers
# Modificação Segura: Testa sem danificar configuração existente
#
# Uso: bash test_workers_comparison.sh
# Ou: OMNIMIND_WORKERS=2 bash test_workers_comparison.sh

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
WORKERS=${OMNIMIND_WORKERS:-2}  # Default 2 se não especificado

echo "════════════════════════════════════════════════════════════════"
echo "🧪 TESTE: Workers Async Config (Current vs Modified)"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Configuração:"
echo "   • Projeto: $PROJECT_ROOT"
echo "   • Workers a testar: $WORKERS"
echo "   • Backends: 3 (8000, 8080, 3001)"
echo ""

# Ativar venv
cd "$PROJECT_ROOT"
source .venv/bin/activate 2>/dev/null || true

# ════════════════════════════════════════════════════════════════
# FASE 1: Verificar configuração ATUAL
# ════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════"
echo "📋 FASE 1: Verificar Configuração Atual"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "✓ Variáveis de Ambiente:"
echo "  OMNIMIND_WORKERS = ${OMNIMIND_WORKERS:-não definida}"
echo "  OMNIMIND_ASYNC_WORKERS = ${OMNIMIND_ASYNC_WORKERS:-não definida}"
echo ""

echo "✓ Em config/optimization_config.json:"
grep -E '"(async_workers|num_workers)"' "$PROJECT_ROOT/config/optimization_config.json" || echo "  (não encontrado)"
echo ""

echo "✓ Em scripts (hardcoded):"
grep -n "\-\-workers" "$PROJECT_ROOT/scripts/canonical/system/run_cluster.sh" | head -3
echo ""

# ════════════════════════════════════════════════════════════════
# FASE 2: Criar Script de Teste Temporário
# ════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════"
echo "🔧 FASE 2: Criar Script de Teste Modificado"
echo "════════════════════════════════════════════════════════════════"
echo ""

TEMP_SCRIPT="/tmp/test_cluster_workers_${WORKERS}.sh"

cat > "$TEMP_SCRIPT" << 'EOF_SCRIPT'
#!/bin/bash

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
CLUSTER_PROJECT_ROOT="$PROJECT_ROOT"
WORKERS=${OMNIMIND_WORKERS:-2}

# Kill existing backends
pkill -f "uvicorn web.backend.main:app" 2>/dev/null || true
pkill -f "python web/backend/main.py" 2>/dev/null || true
sleep 1

export PYTHONPATH="$CLUSTER_PROJECT_ROOT:${PYTHONPATH}"
mkdir -p logs
chmod 755 logs 2>/dev/null || true

echo "🧪 Iniciando Cluster de TESTE com $WORKERS workers por backend..."
echo ""

# Start Primary (8000)
echo "▶ Iniciando Primary (Port 8000, $WORKERS workers)..."
nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --workers $WORKERS > logs/test_backend_8000.log 2>&1 &
PID_8000=$!
echo "   PID: $PID_8000"
sleep 2

# Start Secondary (8080)
echo "▶ Iniciando Secondary (Port 8080, $WORKERS workers)..."
nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8080 --workers $WORKERS > logs/test_backend_8080.log 2>&1 &
PID_8080=$!
echo "   PID: $PID_8080"
sleep 2

# Start Fallback (3001)
echo "▶ Iniciando Fallback (Port 3001, $WORKERS workers)..."
nohup python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 3001 --workers $WORKERS > logs/test_backend_3001.log 2>&1 &
PID_3001=$!
echo "   PID: $PID_3001"
sleep 2

echo ""
echo "✅ Cluster de TESTE rodando com $WORKERS workers"
echo ""
echo "📊 PIDs:"
echo "   Primary (8000):   $PID_8000"
echo "   Secondary (8080): $PID_8080"
echo "   Fallback (3001):  $PID_3001"
echo ""
echo "📋 Logs de teste:"
echo "   tail -f logs/test_backend_*.log"
echo ""
echo "🔍 Monitorar GPU:"
echo "   watch -n 2 nvidia-smi"
echo ""
echo "✋ Para parar teste:"
echo "   pkill -f 'uvicorn web.backend.main:app'"
echo ""
EOF_SCRIPT

chmod +x "$TEMP_SCRIPT"
echo "✓ Script criado: $TEMP_SCRIPT"
echo ""

# ════════════════════════════════════════════════════════════════
# FASE 3: Resumo e Instruções
# ════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════"
echo "📋 FASE 3: Como Executar Teste"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Opção A: Rodar teste COM 2 WORKERS (recomendado)"
echo "  $ OMNIMIND_WORKERS=2 bash $TEMP_SCRIPT"
echo ""

echo "Opção B: Rodar teste COM 1 WORKER (baseline atual)"
echo "  $ OMNIMIND_WORKERS=1 bash $TEMP_SCRIPT"
echo ""

echo "Opção C: Rodar teste COM 4 WORKERS (máximo)"
echo "  $ OMNIMIND_WORKERS=4 bash $TEMP_SCRIPT"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "🔬 PROTOCOLO DE TESTE (execute em 3 terminais simultâneos)"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Terminal 1 (Execute o teste):"
echo "  $ cd $PROJECT_ROOT"
echo "  $ OMNIMIND_WORKERS=$WORKERS bash $TEMP_SCRIPT"
echo ""

echo "Terminal 2 (Monitore GPU em tempo real):"
echo "  $ watch -n 2 nvidia-smi"
echo ""

echo "Terminal 3 (Teste de carga/stress):"
echo "  $ while true; do curl -s http://localhost:8000/health > /dev/null && echo 'OK' || echo 'ERRO'; sleep 1; done"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📊 MÉTRICAS A COLETAR (durante 5-10 minutos)"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "De nvidia-smi -l 2:"
echo "  • SM Utilization: ____%  (esperado: aumentar vs 1 worker)"
echo "  • Memory Usage: ____MB  (esperado: aumentar ~100-200MB)"
echo "  • Power Draw: ___W      (esperado: aumentar)"
echo "  • Temperature: __°C     (esperado: aumentar ligeiramente)"
echo ""

echo "De logs/test_backend_*.log:"
echo "  • Erros: nenhum esperado"
echo "  • Warnings: nenhum esperado"
echo "  • Latency: verificar se diminui"
echo ""

echo "Teste de conectividade:"
echo "  • http://localhost:8000/health"
echo "  • http://localhost:8080/health"
echo "  • http://localhost:3001/health"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "⏹️  COMO PARAR O TESTE"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Matar backends de teste:"
echo "  $ pkill -f 'uvicorn web.backend.main:app'"
echo ""

echo "Ou kill individual:"
echo "  $ kill <PID_8000> <PID_8080> <PID_3001>"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📝 PRÓXIMOS PASSOS"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "1. Executar teste com OMNIMIND_WORKERS=2"
echo "2. Coletar métricas GPU durante 5-10 minutos"
echo "3. Parar teste (pkill)"
echo "4. Executar novamente com OMNIMIND_WORKERS=1 (baseline)"
echo "5. Comparar métricas"
echo "6. Documentar resultados em real_evidence/"
echo ""

echo "Se tudo funcionar bem (sem erros), considerar:"
echo "  ✓ Mudar default de 1 → 2 workers em scripts oficiais"
echo "  ✓ Adicionar variável OMNIMIND_WORKERS ao .env"
echo "  ✓ Testar com 4 workers se 2 for bem"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ Teste preparado. Próxima ação: executar em Terminal 1"
echo "════════════════════════════════════════════════════════════════"
echo ""
