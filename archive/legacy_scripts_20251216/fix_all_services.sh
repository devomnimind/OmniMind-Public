#!/bin/bash
set -euo pipefail

echo "🔧 Corrigindo todos os problemas identificados no service_validation_report..."
echo ""

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SYSTEMD_DIR="/etc/systemd/system"

# 1. Corrigir diretório .omnimind
echo "1. Corrigindo diretório .omnimind..."
mkdir -p "${PROJECT_ROOT}/.omnimind"
chmod 755 "${PROJECT_ROOT}/.omnimind"
echo "✅ Diretório .omnimind corrigido."

# 2. Atualizar serviços systemd
echo ""
echo "2. Atualizando serviços systemd..."
sudo cp "${PROJECT_ROOT}/scripts/systemd/omnimind.service" "${SYSTEMD_DIR}/"
sudo cp "${PROJECT_ROOT}/scripts/systemd/omnimind-test-suite.service" "${SYSTEMD_DIR}/"
sudo cp "${PROJECT_ROOT}/scripts/systemd/omnimind-benchmark.service" "${SYSTEMD_DIR}/"
sudo cp "${PROJECT_ROOT}/scripts/systemd/omnimind-frontend.service" "${SYSTEMD_DIR}/"
sudo systemctl daemon-reload
echo "✅ Serviços atualizados."

# 3. Verificar e corrigir porta 8000
echo ""
echo "3. Verificando porta 8000..."
PORT_8000_PID=$(sudo lsof -t -i :8000 2>/dev/null || true)
if [ -n "$PORT_8000_PID" ]; then
    echo "   Processo usando porta 8000: PID $PORT_8000_PID"
    # Verificar se é o serviço systemd
    if systemctl status omnimind.service --no-pager | grep -q "PID.*$PORT_8000_PID"; then
        echo "   ✅ Porta 8000 está sendo usada pelo serviço systemd (correto)"
    else
        echo "   ⚠️  Porta 8000 está sendo usada por processo não-systemd"
        echo "   Parando processo..."
        sudo kill -9 "$PORT_8000_PID" 2>/dev/null || true
        sleep 2
    fi
else
    echo "   ✅ Porta 8000 está livre"
fi

# 4. Reiniciar serviços principais
echo ""
echo "4. Reiniciando serviços principais..."
sudo systemctl restart omnimind.service
sleep 3
sudo systemctl restart omnimind-mcp.service
sleep 5
echo "✅ Serviços reiniciados."

# 5. Verificar status
echo ""
echo "5. Verificando status dos serviços..."
echo ""
echo "📋 omnimind.service:"
systemctl is-active omnimind.service && echo "   ✅ ATIVO" || echo "   ❌ INATIVO"

echo ""
echo "📋 omnimind-mcp.service:"
systemctl is-active omnimind-mcp.service && echo "   ✅ ATIVO" || echo "   ❌ INATIVO"

echo ""
echo "📋 omnimind-daemon.service:"
systemctl is-active omnimind-daemon.service && echo "   ✅ ATIVO" || echo "   ❌ INATIVO"

echo ""
echo "📋 omnimind-qdrant.service:"
systemctl is-active omnimind-qdrant.service && echo "   ✅ ATIVO" || echo "   ❌ INATIVO"

# 6. Testar endpoints
echo ""
echo "6. Testando endpoints..."
echo -n "   Backend (8000): "
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null | grep -q "200"; then
    echo "✅ OK"
else
    echo "❌ Não responde"
fi

echo -n "   Qdrant (6333): "
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:6333/healthz 2>/dev/null | grep -q "200"; then
    echo "✅ OK"
else
    echo "❌ Não responde"
fi

# 7. Verificar servidores MCP
echo ""
echo "7. Verificando servidores MCP..."
MCP_PROCESSES=$(ps aux | grep -E "mcp.*server|mcp.*wrapper" | grep -v grep | wc -l)
echo "   Processos MCP: $MCP_PROCESSES"

MCP_PORTS=$(ss -tlnp 2>/dev/null | grep -E ":(4321|4322|4323|4324|4325|4326|4327|4328|4329)" | wc -l)
echo "   Portas MCP em uso: $MCP_PORTS/9"

if [ "$MCP_PORTS" -eq 9 ]; then
    echo "   ✅ Todos os servidores MCP estão ativos"
else
    echo "   ⚠️  Alguns servidores MCP podem não estar rodando"
fi

# 8. Verificar logs de erros recentes
echo ""
echo "8. Verificando erros recentes nos logs..."
echo "   Erros omnimind.service (últimas 10 linhas):"
journalctl -u omnimind.service --no-pager -n 10 | grep -i "error\|fail\|exception" | tail -5 || echo "   Nenhum erro encontrado"

echo ""
echo "✅ Correções aplicadas!"
echo ""
echo "📊 Status Final:"
echo "   - omnimind.service: $(systemctl is-active omnimind.service)"
echo "   - Backend API: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health 2>/dev/null || echo 'N/A')"
echo "   - Servidores MCP: $MCP_PORTS/9 portas ativas"
echo ""
echo "💡 Para ver logs detalhados:"
echo "   sudo journalctl -u omnimind.service -f"
echo "   sudo journalctl -u omnimind-mcp.service -f"

