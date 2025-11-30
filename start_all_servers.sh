#!/bin/bash

echo "🚀 Iniciando OmniMind Services..."

# Funções de limpeza
cleanup() {
    echo "🛑 Encerrando servidores..."
    kill -9 $(pgrep -f "uvicorn web.backend.main:app") 2>/dev/null
    kill -9 $(pgrep -f "vite") 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

PROJECT_ROOT="$( cd "$(dirname "${BASH_SOURCE[0]}")" && pwd )"

# Configurar PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT/web:$PROJECT_ROOT"

# Carregar .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Ativar venv
source "$PROJECT_ROOT/.venv/bin/activate"

# Limpar porta 8000
echo "🔄 Limpando porta 8000..."
fuser -k 8000/tcp 2>/dev/null || true
sleep 1

# Iniciar Backend FastAPI na porta 8000
echo "📡 Iniciando Backend na porta 8000..."
cd "$PROJECT_ROOT"
/home/fahbrain/projects/omnimind/.venv/bin/uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --log-level info > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 3

# Verificar se backend está respondendo
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "✅ Backend respondendo na porta 8000"
else
    echo "❌ Backend NÃO está respondendo!"
    tail /tmp/backend.log
    exit 1
fi

# Iniciar Frontend Vite na porta 3000 (se configurado)
if [ -d "$PROJECT_ROOT/web/frontend" ]; then
    echo "📡 Iniciando Frontend na porta 3000..."
    cd "$PROJECT_ROOT/web/frontend"
    npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    sleep 3
    
    if curl -s http://127.0.0.1:3000/ > /dev/null 2>&1; then
        echo "✅ Frontend respondendo na porta 3000"
    else
        echo "⚠️  Frontend não respondendo ainda (normal, pode estar compilando)"
    fi
fi

echo ""
echo "🎉 Serviços iniciados!"
echo "Backend: http://localhost:8000 (API)"
echo "Frontend: http://localhost:3000 (Dashboard)"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "Pressione Ctrl+C para encerrar..."

# Manter script rodando
wait
