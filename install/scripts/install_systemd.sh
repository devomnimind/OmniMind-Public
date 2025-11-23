#!/bin/bash
set -euo pipefail

echo "🚀 Instalando OmniMind como serviços systemd..."

BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASEDIR/.."

# Instalar serviços
SERVICES=(
    "omnimind.service"
    "omnimind-backend.service" 
    "omnimind-frontend.service"
    "omnimind-mcp.service"
    "omnimind-qdrant.service"
)

for service in "${SERVICES[@]}"; do
    service_file="scripts/systemd/$service"
    if [[ -f "$service_file" ]]; then
        echo "📦 Instalando $service..."
        sudo cp "$service_file" /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable "$service"
        echo "✅ $service instalado"
    else
        echo "⚠️ Serviço $service não encontrado"
    fi
done

echo ""
echo "🎯 Para iniciar o OmniMind:"
echo "  sudo systemctl start omnimind"
echo ""
echo "📊 Para verificar status:"
echo "  sudo systemctl status omnimind"
echo ""
echo "🔄 Para reiniciar após atualizações:"
echo "  sudo systemctl restart omnimind"
