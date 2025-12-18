#!/bin/bash

# ============================================================================
# 🔍 DIAGNOSTIC: Test Server Startup
# ============================================================================
# Testa se o servidor consegue subir sem pytest
# ============================================================================

set -e

echo "🔍 OMNIMIND SERVER STARTUP DIAGNOSTIC"
echo "===================================="
echo ""

cd /home/fahbrain/projects/omnimind

# 1. Limpar processos antigos
echo "🧹 Limpando processos antigos..."
pkill -f "uvicorn web.backend.main:app" || true
pkill -f "bpftrace.*monitor_mcp_bpf" || true
sleep 2

# 2. Iniciar servidor
echo ""
echo "🚀 Iniciando servidor com sudo..."
timeout 30 sudo -n bash scripts/start_omnimind_system_sudo.sh &
PID=$!

# Aguardar um pouco
echo "⏳ Aguardando 15s..."
sleep 15

# 3. Testar conexão
echo ""
echo "🧪 Testando conexão..."

if curl -s -m 2 http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "✅ SERVER IS ONLINE at http://localhost:8000"

    echo ""
    echo "📊 Status:"
    curl -s http://localhost:8000/health/ | head -50

    echo ""
    echo "✅ SUCCESS - Server is responding!"
else
    echo "❌ SERVER OFFLINE - Connection refused"

    echo ""
    echo "🔍 Debugging:"
    ps aux | grep uvicorn | grep -v grep || echo "   No uvicorn processes found"

    echo ""
    echo "📋 Backend logs:"
    tail -20 logs/backend_*.log 2>/dev/null || echo "   No logs found"

    exit 1
fi
