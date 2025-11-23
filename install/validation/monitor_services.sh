#!/bin/bash
# Monitoramento contínuo dos serviços OmniMind
set -euo pipefail

echo "📊 Monitoramento de Serviços OmniMind"
echo "====================================="
echo "Pressione Ctrl+C para sair"
echo ""

while true; do
    clear
    echo "📊 Status dos Serviços - $(date)"
    echo "=================================="

    # Status dos serviços
    sudo systemctl status omnimind-qdrant --no-pager -l | head -3 | tail -1
    sudo systemctl status omnimind-backend --no-pager -l | head -3 | tail -1
    sudo systemctl status omnimind-frontend --no-pager -l | head -3 | tail -1
    sudo systemctl status omnimind-mcp --no-pager -l | head -3 | tail -1

    echo ""
    echo "🔌 Status das Portas"
    echo "===================="

    PORTS=(6333 8000 3000)
    for port in "${PORTS[@]}"; do
        if sudo netstat -tlnp | grep -q ":$port "; then
            echo "Porta $port: ✅ Aberta"
        else
            echo "Porta $port: ❌ Fechada"
        fi
    done

    echo ""
    echo "🐳 Containers Docker"
    echo "===================="

    docker ps --filter "name=deploy-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    echo "📈 Uso de Recursos (últimos 5 minutos)"
    echo "======================================="

    for service in omnimind-qdrant omnimind-backend omnimind-frontend omnimind-mcp; do
        cpu=$(sudo systemctl show "$service" --property=CPUUsageNS | cut -d'=' -f2)
        mem=$(sudo systemctl show "$service" --property=MemoryCurrent | cut -d'=' -f2)
        if [[ -n "$cpu" && -n "$mem" ]]; then
            cpu_mb=$((cpu / 1000000))  # Convert to milliseconds
            mem_mb=$((mem / 1024 / 1024))  # Convert to MB
            echo "$service: CPU ${cpu_mb}ms, Mem ${mem_mb}MB"
        fi
    done

    sleep 5
done