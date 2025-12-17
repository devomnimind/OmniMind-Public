#!/bin/bash
set -euo pipefail

echo "🧹 Limpando serviços duplicados e consolidando configuração..."
echo ""

SYSTEMD_DIR="/etc/systemd/system"

# Lista de serviços que devem permanecer (serviços principais)
KEEP_SERVICES=(
    "omnimind.service"
    "omnimind-daemon.service"
    "omnimind-mcp.service"
    "omnimind-qdrant.service"
)

# Serviços que devem ser removidos (duplicatas/redundantes)
REMOVE_SERVICES=(
    "omnimind-backend.service"  # Redundante - omnimind.service já faz isso
    "omnimind-frontend.service" # Não está sendo usado
)

echo "1. Parando serviços redundantes..."
for service in "${REMOVE_SERVICES[@]}"; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo "   🛑 Parando ${service}..."
        sudo systemctl stop "$service" || true
    fi
    if systemctl is-enabled --quiet "$service" 2>/dev/null; then
        echo "   🔧 Desabilitando ${service}..."
        sudo systemctl disable "$service" || true
    fi
done

echo ""
echo "2. Removendo arquivos de serviço redundantes..."
for service in "${REMOVE_SERVICES[@]}"; do
    service_file="${SYSTEMD_DIR}/${service}"
    if [ -f "$service_file" ]; then
        echo "   🗑️  Removendo ${service_file}..."
        sudo rm -f "$service_file"
    fi
done

echo ""
echo "3. Verificando serviços principais..."
for service in "${KEEP_SERVICES[@]}"; do
    service_file="${SYSTEMD_DIR}/${service}"
    if [ -f "$service_file" ]; then
        echo "   ✅ ${service} - mantido"
    else
        echo "   ⚠️  ${service} - não encontrado"
    fi
done

echo ""
echo "4. Recarregando daemon systemd..."
sudo systemctl daemon-reload

echo ""
echo "5. Verificando status final..."
echo ""
echo "📋 Serviços ativos:"
systemctl list-units --type=service --state=running | grep omnimind || echo "   Nenhum serviço OmniMind rodando"

echo ""
echo "📋 Serviços habilitados:"
systemctl list-unit-files --type=service | grep omnimind | grep enabled || echo "   Nenhum serviço OmniMind habilitado"

echo ""
echo "6. Verificando portas em uso..."
ss -tlnp 2>/dev/null | grep -E ":(8000|4321|4322|4323|4324|4325|4326|4327|4328|4329|6333)" || echo "   Nenhuma porta OmniMind em uso"

echo ""
echo "7. Limpando arquivos temporários e relatórios..."
# Remover arquivos de log de instalação temporários
find /tmp -maxdepth 1 -name "*omnimind*install*" -type f -mtime +1 -delete 2>/dev/null || true
find /tmp -maxdepth 1 -name "*systemd*install*" -type f -mtime +1 -delete 2>/dev/null || true

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📋 Estrutura final de serviços:"
echo "   ✅ omnimind.service - Serviço principal (Backend API)"
echo "   ✅ omnimind-daemon.service - Daemon autônomo"
echo "   ✅ omnimind-mcp.service - Servidores MCP"
echo "   ✅ omnimind-qdrant.service - Qdrant (Docker)"
echo ""
echo "🗑️  Serviços removidos:"
for service in "${REMOVE_SERVICES[@]}"; do
    echo "   ❌ ${service}"
done
echo ""
echo "💡 Para iniciar os serviços:"
echo "   sudo systemctl start omnimind.service omnimind-daemon.service omnimind-mcp.service"

