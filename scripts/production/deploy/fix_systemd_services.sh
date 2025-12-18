#!/bin/bash
# Script para corrigir serviços systemd do OmniMind
# Substitui placeholders e corrige configurações
# Autor: Fabrício da Silva + assistência de IA

set -euo pipefail

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
OMNIMIND_USER="fahbrain"
SYSTEMD_DIR="/etc/systemd/system"
SERVICES_DIR="${PROJECT_ROOT}/scripts/production/deploy"

echo "🔧 Corrigindo serviços systemd do OmniMind..."
echo ""

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script deve ser executado como root (use sudo)"
   exit 1
fi

# Lista de serviços que precisam de correção
SERVICES=(
    "omnimind-daemon.service"
    "omnimind.service"
    "omnimind-core.service"
    "omnimind-frontend.service"
    "omnimind-mcp.service"
)

echo "📋 Verificando serviços instalados..."
for service in "${SERVICES[@]}"; do
    service_file="${SYSTEMD_DIR}/${service}"
    template_file="${SERVICES_DIR}/${service}"

    if [ -f "$service_file" ]; then
        echo "   ✅ ${service} encontrado"

        # Verificar se tem placeholders
        if grep -q "__OMNIMIND_USER__\|__PROJECT_ROOT__" "$service_file" 2>/dev/null; then
            echo "   ⚠️  ${service} tem placeholders não substituídos"

            # Se existe template, substituir placeholders
            if [ -f "$template_file" ]; then
                echo "   🔄 Substituindo placeholders em ${service}..."
                sed -e "s|__OMNIMIND_USER__|${OMNIMIND_USER}|g" \
                    -e "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" \
                    "$template_file" > "${service_file}.tmp"
                mv "${service_file}.tmp" "$service_file"
                chmod 644 "$service_file"
                echo "   ✅ ${service} corrigido"
            else
                echo "   ⚠️  Template não encontrado: ${template_file}"
            fi
        else
            echo "   ✅ ${service} sem placeholders"
        fi
    else
        echo "   ⚠️  ${service} não encontrado em ${SYSTEMD_DIR}"
    fi
done

echo ""
echo "🔍 Verificando configurações de timeout..."

# Corrigir timeout do omnimind.service se necessário
OMNIMIND_SERVICE="${SYSTEMD_DIR}/omnimind.service"
if [ -f "$OMNIMIND_SERVICE" ]; then
    # Verificar se tem TimeoutStartSec configurado
    if ! grep -q "TimeoutStartSec" "$OMNIMIND_SERVICE"; then
        echo "   ⚠️  omnimind.service não tem TimeoutStartSec configurado"
        echo "   🔄 Adicionando TimeoutStartSec=300s (5 minutos)..."

        # Adicionar TimeoutStartSec após [Service]
        sed -i '/\[Service\]/a TimeoutStartSec=300s' "$OMNIMIND_SERVICE"
        echo "   ✅ TimeoutStartSec adicionado"
    else
        echo "   ✅ omnimind.service já tem TimeoutStartSec"
    fi

    # Verificar se tem TimeoutStopSec configurado
    if ! grep -q "TimeoutStopSec" "$OMNIMIND_SERVICE"; then
        echo "   🔄 Adicionando TimeoutStopSec=60s..."
        sed -i '/TimeoutStartSec/a TimeoutStopSec=60s' "$OMNIMIND_SERVICE"
        echo "   ✅ TimeoutStopSec adicionado"
    fi
fi

echo ""
echo "🔄 Recarregando daemon systemd..."
systemctl daemon-reload
echo "✅ Daemon recarregado"

echo ""
echo "🔍 Verificando sintaxe dos serviços..."
for service in "${SERVICES[@]}"; do
    service_file="${SYSTEMD_DIR}/${service}"
    if [ -f "$service_file" ]; then
        if systemd-analyze verify "$service_file" 2>/dev/null; then
            echo "   ✅ ${service} OK"
        else
            echo "   ❌ Erro de sintaxe em ${service}"
            systemd-analyze verify "$service_file" || true
        fi
    fi
done

echo ""
echo "📊 Status dos serviços após correção:"
echo "====================================="
for service in "${SERVICES[@]}"; do
    service_name=$(basename "$service")
    echo ""
    echo "📋 ${service_name}:"
    systemctl status "$service_name" --no-pager -l | head -n 5 || echo "   ⚠️  Serviço não iniciado ainda"
done

echo ""
echo "✅ Correção completa!"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Verificar logs: sudo journalctl -u omnimind.service -n 50"
echo "   2. Tentar iniciar: sudo systemctl start omnimind.service"
echo "   3. Verificar status: sudo systemctl status omnimind.service"
echo ""
echo "💡 Se ainda houver problemas:"
echo "   - Verificar logs: sudo journalctl -u omnimind.service -f"
echo "   - Verificar dependências: sudo systemctl list-dependencies omnimind.service"
echo "   - Verificar recursos: free -h && df -h"
