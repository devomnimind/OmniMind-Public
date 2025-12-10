#!/bin/bash
# Script para atualizar configurações de memória nos serviços systemd OmniMind
# Autor: Fabrício da Silva + assistência de IA

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SYSTEMD_DIR="/etc/systemd/system"

echo "🔧 Atualizando configurações de memória nos serviços systemd OmniMind..."
echo ""

# Função para atualizar um serviço systemd
update_service() {
    local service_name=$1
    local service_file="$SYSTEMD_DIR/$service_name"

    if [ ! -f "$service_file" ]; then
        echo "⚠️  Serviço $service_name não encontrado em $service_file"
        return 1
    fi

    echo "📝 Atualizando $service_name..."

    # Criar arquivo de override temporário
    local override_dir="$SYSTEMD_DIR/$service_name.d"
    mkdir -p "$override_dir"

    local override_file="$override_dir/memory-protection.conf"

    cat > "$override_file" << EOF
[Service]
# Proteção de memória crítica (não pode ir para swap)
MemoryLock=yes
LimitMEMLOCK=infinity

# Limites de memória (ajustar conforme necessário)
MemoryMax=4G
MemoryHigh=3G
MemorySwapMax=1G

# OOM killer (menos provável de ser morto)
OOMScoreAdjust=-500
EOF

    echo "   ✅ Override criado: $override_file"

    # Recarregar systemd
    systemctl daemon-reload

    echo "   ✅ Systemd recarregado"
}

# Serviços para atualizar
SERVICES=(
    "omnimind.service"
    "omnimind-daemon.service"
    "omnimind-core.service"
)

# Atualizar cada serviço
for service in "${SERVICES[@]}"; do
    update_service "$service" || echo "   ⚠️  Falha ao atualizar $service"
    echo ""
done

echo "✅ Configurações de memória atualizadas!"
echo ""
echo "💡 Para aplicar as mudanças:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl restart omnimind.service omnimind-daemon.service omnimind-core.service"
echo ""
echo "💡 Para verificar configurações:"
echo "   systemctl show omnimind.service | grep Memory"

