#!/bin/bash
# Script para configurar inicialização automática do OmniMind no boot
# Autor: Fabrício da Silva + assistência de IA
# Data: 2025-01-XX

set -euo pipefail

echo "🔧 Configurando Inicialização Automática do OmniMind"
echo "=================================================="
echo ""

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script deve ser executado como root (use sudo)"
   echo ""
   echo "📋 Execute:"
   echo "   sudo bash scripts/canonical/system/configurar_inicializacao_automatica.sh"
   exit 1
fi

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SYSTEMD_DIR="/etc/systemd/system"

# Serviços principais que devem iniciar automaticamente
MAIN_SERVICES=(
    "omnimind.service"
    "omnimind-mcp.service"
    "omnimind-daemon.service"
    "omnimind-frontend.service"
    "omnimind-qdrant.service"
)

echo "1️⃣ Verificando serviços instalados..."
echo ""

# Verificar quais serviços existem
EXISTING_SERVICES=()
for service in "${MAIN_SERVICES[@]}"; do
    if [ -f "${SYSTEMD_DIR}/${service}" ]; then
        EXISTING_SERVICES+=("$service")
        echo "   ✅ ${service} encontrado"
    else
        echo "   ⚠️  ${service} não encontrado"
    fi
done

if [ ${#EXISTING_SERVICES[@]} -eq 0 ]; then
    echo ""
    echo "❌ Nenhum serviço encontrado. Execute primeiro:"
    echo "   sudo bash scripts/production/deploy/install_all_services.sh"
    exit 1
fi

echo ""
echo "2️⃣ Recarregando daemon systemd..."
systemctl daemon-reload
echo "   ✅ Daemon recarregado"

echo ""
echo "3️⃣ Habilitando serviços para inicialização automática no boot..."
echo ""

ENABLED_COUNT=0
for service in "${EXISTING_SERVICES[@]}"; do
    if systemctl is-enabled "$service" >/dev/null 2>&1; then
        echo "   ✅ ${service} já está habilitado"
        ((ENABLED_COUNT++))
    else
        echo "   🔧 Habilitando ${service}..."
        if systemctl enable "$service" 2>/dev/null; then
            echo "   ✅ ${service} habilitado com sucesso"
            ((ENABLED_COUNT++))
        else
            echo "   ❌ Falha ao habilitar ${service}"
        fi
    fi
done

echo ""
echo "4️⃣ Verificando status final..."
echo ""

for service in "${EXISTING_SERVICES[@]}"; do
    STATUS=$(systemctl is-enabled "$service" 2>/dev/null || echo "disabled")
    if [ "$STATUS" = "enabled" ]; then
        echo "   ✅ ${service}: HABILITADO (iniciará no boot)"
    else
        echo "   ❌ ${service}: DESABILITADO"
    fi
done

echo ""
echo "=================================================="
echo "✅ Configuração Concluída!"
echo "=================================================="
echo ""
echo "📊 Resumo:"
echo "   - Serviços encontrados: ${#EXISTING_SERVICES[@]}"
echo "   - Serviços habilitados: ${ENABLED_COUNT}"
echo ""
echo "🔄 Os seguintes serviços iniciarão automaticamente no boot:"
for service in "${EXISTING_SERVICES[@]}"; do
    if systemctl is-enabled "$service" >/dev/null 2>&1; then
        echo "   ✅ ${service}"
    fi
done
echo ""
echo "📋 Comandos úteis:"
echo "   Ver status:     sudo systemctl status omnimind.service"
echo "   Ver logs:       sudo journalctl -u omnimind.service -f"
echo "   Iniciar agora:  sudo systemctl start omnimind.service"
echo "   Reiniciar:      sudo systemctl restart omnimind.service"
echo "   Parar:          sudo systemctl stop omnimind.service"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Os serviços iniciarão automaticamente no próximo boot"
echo "   - Para iniciar agora (sem reiniciar): sudo systemctl start omnimind.service"
echo "   - Para desabilitar: sudo systemctl disable omnimind.service"

