#!/bin/bash
# OmniMind Status Check - 30 Nov 2025, 01:52 UTC

echo "================================"
echo "🔍 OMNIMIND SERVICES STATUS"
echo "================================"
echo ""

# Backend
echo "📡 BACKEND (Port 8000)"
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "   ✅ Respondendo"
    METRICS=$(timeout 5 curl -s -u admin:omnimind2025! http://127.0.0.1:8000/daemon/status 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Phi={d.get('consciousness_metrics',{}).get('phi',0)}, Anxiety={d.get('consciousness_metrics',{}).get('anxiety',0)}, Flow={d.get('consciousness_metrics',{}).get('flow',0)}, Entropy={d.get('consciousness_metrics',{}).get('entropy',0):.6f}\");" 2>/dev/null || echo "")
    if [ -n "$METRICS" ]; then
        echo "   📊 Real Metrics: $METRICS"
    fi
else
    echo "   ❌ Não responde"
fi
echo ""

# Frontend
echo "🎨 FRONTEND (Port 3001)"
if curl -s http://127.0.0.1:3001/ > /dev/null 2>&1; then
    echo "   ✅ Respondendo"
else
    echo "   ❌ Não responde (verifique: npm run dev)"
fi
echo ""

# Processes
echo "⚙️  PROCESSOS"
echo "   Backend (uvicorn):"
ps aux | grep "uvicorn web.backend" | grep -v grep | wc -l | xargs -I {} echo "     {} processo(s) ativo(s)"

echo "   Frontend (vite):"
ps aux | grep -E "vite|web/frontend" | grep -v grep | wc -l | xargs -I {} echo "     {} processo(s) ativo(s)"

echo ""
echo "================================"
echo "URLs DE ACESSO"
echo "================================"
echo ""
echo "Backend:"
echo "  - Raiz: http://127.0.0.1:8000/"
echo "  - Status: http://127.0.0.1:8000/health"
echo "  - Métricas: curl -u admin:omnimind2025! http://127.0.0.1:8000/daemon/status"
echo ""
echo "Frontend:"
echo "  - Dashboard: http://127.0.0.1:3001/"
echo "  - Network: http://192.168.15.2:3001/"
echo ""
echo "================================"
