#!/bin/bash
# OmniMind Development Startup Script
# Force clean startup with proper environment injection

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

echo "🚀 [1/6] Limpando processos antigos..."
pkill -9 -f "simple_backend|uvicorn|vite.*frontend" 2>/dev/null || true
sleep 1

echo "📁 [2/6] Verificando ambiente..."
if [ ! -d ".venv" ]; then
    echo "❌ .venv não encontrado! Execute: ./activate_venv.sh"
    exit 1
fi

echo "✅ [3/6] Ativando .venv..."
source .venv/bin/activate

echo "🔧 [4/6] Configurando PYTHONPATH..."
export PYTHONPATH="$PROJECT_ROOT/src:."
export PYTHONUNBUFFERED=1

echo "🌐 [5/6] Iniciando backend (porta 9000)..."
cd "$PROJECT_ROOT"
python simple_backend.py &
BACKEND_PID=$!
echo "✅ Backend iniciado (PID: $BACKEND_PID)"
sleep 2

echo "📦 [6/6] Iniciando frontend (porta 3000)..."
cd "$PROJECT_ROOT/web/frontend"
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
sleep 3

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  🎉 OmniMind Dev Environment Ready!   ║"
echo "╠════════════════════════════════════════╣"
echo "║  Frontend:  http://localhost:3000      ║"
echo "║  Backend:   http://localhost:9000      ║"
echo "║  API URL:   http://localhost:9000      ║"
echo "║  User:      admin                       ║"
echo "║  Pass:      omnimind2025!               ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📋 Backend logs:"
tail -f /dev/null  &
wait
