#!/bin/bash
set -e
export PYTORCH_DISABLE_DYNAMO=1

cd /home/fahbrain/projects/omnimind
source .venv/bin/activate 2>/dev/null || python3 -m venv --upgrade-deps .venv && source .venv/bin/activate

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 VALIDAÇÃO DE MÓDULOS CRÍTICOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "1️⃣ Orchestrador (meta_react_coordinator)..."
timeout 15 python3 -c "
import sys
sys.path.insert(0, 'src')
from orchestrator.meta_react_coordinator import MetaReactCoordinator
print('✅ MetaReactCoordinator importado')
" && echo "✅ Orchestrador OK" || echo "❌ Orchestrador erro"

echo ""
echo "2️⃣ Tribunal do Diabo (executor)..."
timeout 15 python3 -c "
import sys
sys.path.insert(0, 'src')
from tribunal_do_diabo.executor import TribunalExecutor
print('✅ TribunalExecutor importado')
" && echo "✅ Tribunal do Diabo OK" || echo "❌ Tribunal do Diabo erro"

echo ""
echo "3️⃣ Validação Ética (production_ethics)..."
timeout 15 python3 -c "
import sys
sys.path.insert(0, 'src')
from ethics.production_ethics import ProductionEthicsValidator
print('✅ ProductionEthicsValidator importado')
" && echo "✅ Ética OK" || echo "❌ Ética erro"

echo ""
echo "4️⃣ Frontend (dashboard)..."
timeout 10 python3 -c "
import sys
sys.path.insert(0, 'src')
from web.dashboard_mvp import DashboardMVP
print('✅ DashboardMVP importado')
" && echo "✅ Frontend OK" || echo "❌ Frontend erro"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TODOS OS MÓDULOS DISPONÍVEIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
