#!/bin/bash
# Gera relatório completo da instalação

REPORT_FILE="install/logs/installation_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << 'EOF'
# 📊 Relatório de Instalação OmniMind
**Data:** $(date)
**Sistema:** $(uname -a)

## 📋 Status dos Serviços

EOF

# Adicionar status dos serviços
for service in omnimind-qdrant omnimind-backend omnimind-frontend omnimind-mcp; do
    echo "### $service" >> "$REPORT_FILE"
    sudo systemctl status "$service" --no-pager | head -10 >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << 'EOF'
## 🔌 Status da Rede

EOF

# Adicionar status das portas
echo "| Porta | Status | Processo |" >> "$REPORT_FILE"
echo "|-------|--------|----------|" >> "$REPORT_FILE"
for port in 6333 8000 3000 6379; do
    if sudo netstat -tlnp | grep -q ":$port "; then
        process=$(sudo netstat -tlnp | grep ":$port " | awk '{print $7}' | cut -d'/' -f2)
        echo "| $port | ✅ Aberta | $process |" >> "$REPORT_FILE"
    else
        echo "| $port | ❌ Fechada | - |" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << 'EOF'
## 🐳 Containers Docker

EOF

docker ps --filter "name=deploy-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << 'EOF'
## 🌐 Testes de Endpoint

EOF

# Testar endpoints
ENDPOINTS=(
    "http://localhost:6333/collections:Qdrant Collections"
    "http://localhost:8000/health:Backend Health"
    "http://localhost:3000:Frontend UI"
)

for endpoint_info in "${ENDPOINTS[@]}"; do
    IFS=':' read -r url desc <<< "$endpoint_info"
    echo "### $desc ($url)" >> "$REPORT_FILE"
    if curl -s --max-time 5 "$url" > /dev/null; then
        echo "✅ Respondendo" >> "$REPORT_FILE"
    else
        echo "❌ Não responde" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
done

echo "📄 Relatório gerado: $REPORT_FILE"