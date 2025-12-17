#!/bin/bash
# Script para instalar OmniMind como serviços systemd com inicialização escalonada
# Fase 1: Serviços essenciais (Backend + Orchestrator)
# Fase 2: Serviços secundários (Daemon + Frontend + Monitor) - após 30s
# Autor: Fabrício da Silva + assistência de IA

set -euo pipefail

echo "🚀 Instalando OmniMind como serviços systemd (inicialização escalonada)..."
echo ""

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SERVICES_DIR="${PROJECT_ROOT}/scripts/production/deploy"
SYSTEMD_DIR="/etc/systemd/system"

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script deve ser executado como root (use sudo)"
   exit 1
fi

# Lista de serviços (em ordem de dependência)
SERVICES=(
    "omnimind-essential.service"
    "omnimind-secondary.service"
)

# 1. Parar processos existentes
echo "1. Parando processos existentes..."
pkill -f "uvicorn.*main:app" || true
pkill -f "python -m src.main" || true
pkill -f "vite" || true
pkill -f "bpftrace.*monitor_mcp_bpf" || true
sleep 2
echo "✅ Processos parados."

# 2. Copiar serviços
echo ""
echo "2. Copiando serviços para ${SYSTEMD_DIR}..."
for service in "${SERVICES[@]}"; do
    source_file="${SERVICES_DIR}/${service}"
    target_file="${SYSTEMD_DIR}/${service}"

    if [ -f "$source_file" ]; then
        echo "   📄 Copiando ${service}..."
        cp "$source_file" "$target_file"
        chmod 644 "$target_file"
        echo "   ✅ ${service} copiado"
    else
        echo "   ⚠️  Arquivo não encontrado: ${source_file}"
    fi
done

# 3. Recarregar daemon
echo ""
echo "3. Recarregando daemon systemd..."
systemctl daemon-reload
echo "✅ Daemon recarregado."

# 4. Verificar sintaxe
echo ""
echo "4. Verificando sintaxe dos serviços..."
for service in "${SERVICES[@]}"; do
    if systemd-analyze verify "${SYSTEMD_DIR}/${service}" 2>/dev/null; then
        echo "   ✅ ${service} OK"
    else
        echo "   ❌ Erro de sintaxe em ${service}"
        systemd-analyze verify "${SYSTEMD_DIR}/${service}" || true
    fi
done

# 5. Habilitar serviços
echo ""
echo "5. Habilitando serviços para iniciar no boot..."
for service in "${SERVICES[@]}"; do
    service_name=$(basename "$service")
    echo "   🔧 Habilitando ${service_name}..."
    systemctl enable "${service_name}" || echo "   ⚠️  Falha ao habilitar ${service_name}"
done
echo "✅ Serviços habilitados."

# 6. Status final
echo ""
echo "📊 Status dos Serviços:"
echo "======================="
for service in "${SERVICES[@]}"; do
    service_name=$(basename "$service")
    echo ""
    echo "📋 ${service_name}:"
    systemctl status "${service_name}" --no-pager -l | head -n 5 || echo "   ⚠️  Serviço não iniciado ainda"
done

echo ""
echo "✅ Instalação completa!"
echo ""
echo "🎯 Comandos úteis:"
echo "   Iniciar serviços essenciais: sudo systemctl start omnimind-essential"
echo "   Iniciar serviços secundários: sudo systemctl start omnimind-secondary"
echo "   Ver status: sudo systemctl status omnimind-essential"
echo "   Ver logs: sudo journalctl -u omnimind-essential -f"
echo ""
echo "📋 Ordem de inicialização:"
echo "   1. omnimind-essential.service (Backend + Orchestrator)"
echo "   2. omnimind-secondary.service (após 30s: Daemon + Frontend + Monitor)"
echo ""
echo "🔄 Para iniciar tudo agora:"
echo "   sudo systemctl start omnimind-essential"
echo "   sudo systemctl start omnimind-secondary"

