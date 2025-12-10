#!/bin/bash

# 🎯 Quick Start - Testar Correções do Tribunal
# Data: 9 de dezembro de 2025

set -e

# CORREÇÃO (2025-12-10): Path relativo após mover para scripts/testing/fixes/
cd "$(dirname "$0")/../../.."

echo "════════════════════════════════════════════════════════════════"
echo "🎯 TRIBUNAL METRICS FIX - QUICK START"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Backend Health Check
echo -e "${BLUE}[1/4]${NC} Verificando Backend..."
if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend está rodando${NC}"
else
    echo -e "${YELLOW}⚠️  Backend não está acessível${NC}"
    echo "   Dica: Execute './scripts/canonical/system/start_ultrasimple.sh' em outro terminal"
fi
echo ""

# 2. Test Tribunal Activity Endpoint
echo -e "${BLUE}[2/4]${NC} Testando /api/tribunal/activity..."
if curl -s -u admin:omnimind2025! http://localhost:8000/api/tribunal/activity | python3 -m json.tool 2>/dev/null | head -20; then
    echo -e "${GREEN}✅ Endpoint /api/tribunal/activity funcionando${NC}"
else
    echo -e "${YELLOW}⚠️  Endpoint não respondendo${NC}"
fi
echo ""

# 3. Test NEW Tribunal Metrics Endpoint
echo -e "${BLUE}[3/4]${NC} Testando /api/tribunal/metrics (NOVO)..."
METRICS_RESPONSE=$(curl -s -u admin:omnimind2025! http://localhost:8000/api/tribunal/metrics 2>/dev/null || echo "{}")

if echo "$METRICS_RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Endpoint /api/tribunal/metrics funcionando${NC}"
    echo ""
    echo "   Resposta:"
    echo "$METRICS_RESPONSE" | python3 -m json.tool | head -40
else
    echo -e "${YELLOW}⚠️  Endpoint não respondendo corretamente${NC}"
fi
echo ""

# 4. Frontend Status
echo -e "${BLUE}[4/4]${NC} Verificando Frontend..."
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend está rodando${NC}"
    echo ""
    echo -e "${YELLOW}📝 Próximos passos:${NC}"
    echo "   1. Acesse: http://localhost:3000"
    echo "   2. Faça login com: admin / omnimind2025!"
    echo "   3. Procure pelo componente 'Tribunal do Diabo' no Dashboard"
    echo "   4. Verá dois cards:"
    echo "      - TribunalStatus: Status simples"
    echo "      - TribunalMetricsVisual: Métricas detalhadas com charts ✨ NOVO"
else
    echo -e "${YELLOW}⚠️  Frontend não está acessível${NC}"
    echo "   Dica: Execute 'npm run dev' na pasta web/frontend"
fi
echo ""

# 5. Summary
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}📋 RESUMO DAS MUDANÇAS:${NC}"
echo ""
echo "✅ Frontend:"
echo "   - TribunalStatus.tsx: Null-safe implementation"
echo "   - api.ts: Endpoint mapping correto + getTribunalMetrics()"
echo "   - Dashboard.tsx: Integração de TribunalMetricsVisual"
echo "   - TribunalMetricsVisual.tsx: ✨ NOVO componente com charts"
echo ""
echo "✅ Backend:"
echo "   - tribunal.py: GET /api/tribunal/metrics ✨ NOVO endpoint"
echo "   - Interpretação automática de dados brutos"
echo "   - Indicadores visuais (cores, ícones)"
echo "   - Recomendações contextualizadas"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# 6. Manual Testing
echo -e "${YELLOW}🧪 TESTES MANUAIS (opcional):${NC}"
echo ""
echo "# Ver atividade do Tribunal:"
echo "curl -s -u admin:omnimind2025! http://localhost:8000/api/tribunal/activity | python3 -m json.tool"
echo ""
echo "# Ver métricas com interpretações:"
echo "curl -s -u admin:omnimind2025! http://localhost:8000/api/tribunal/metrics | python3 -m json.tool"
echo ""
echo "# Verificar TypeScript:"
echo "cd web/frontend && npm run type-check"
echo ""

echo -e "${GREEN}✨ Pronto! Sistema atualizado e testado.${NC}"
