#!/bin/bash
set -euo pipefail

echo "🚀 Instalando todos os serviços OmniMind via systemd..."
echo ""

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
SERVICES_DIR="${PROJECT_ROOT}/scripts/systemd"
SYSTEMD_DIR="/etc/systemd/system"

# Lista de serviços a instalar (em ordem de dependência)
# NOTA: omnimind.service já inclui o backend, então não instalamos omnimind-backend.service separadamente
SERVICES=(
    "omnimind-qdrant.service"
    "omnimind-daemon.service"
    "omnimind-mcp.service"
    "omnimind.service"
)

# 1. Parar processos existentes
echo "1. Parando processos existentes..."
pkill -f "uvicorn.*main:app" || true
pkill -f "src.daemon" || true
pkill -f "run_mcp_orchestrator" || true
sleep 2
echo "✅ Processos parados."

# 2. Copiar e processar serviços
echo ""
echo "2. Copiando e processando serviços para ${SYSTEMD_DIR}..."
for service_entry in "${SERVICES[@]}"; do
    if [[ "$service_entry" == *":"* ]]; then
        # Formato: source:target
        IFS=':' read -r source target <<< "$service_entry"
    else
        source="$service_entry"
        target="$service_entry"
    fi
    
    source_file="${SERVICES_DIR}/${source}"
    target_file="${SYSTEMD_DIR}/${target}"
    
    if [ -f "$source_file" ]; then
        echo "   📄 Processando ${source} -> ${target}"
        # Substituir placeholders
        sed -e "s|__OMNIMIND_USER__|fahbrain|g" \
            -e "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" \
            "$source_file" | sudo tee "$target_file" > /dev/null
        sudo chmod 644 "$target_file"
    else
        echo "   ⚠️  Arquivo não encontrado: ${source_file}"
    fi
done
echo "✅ Serviços copiados e processados."

# 3. Recarregar daemon
echo ""
echo "3. Recarregando daemon systemd..."
sudo systemctl daemon-reload
echo "✅ Daemon recarregado."

# 4. Verificar sintaxe
echo ""
echo "4. Verificando sintaxe dos serviços..."
for service_entry in "${SERVICES[@]}"; do
    if [[ "$service_entry" == *":"* ]]; then
        IFS=':' read -r source target <<< "$service_entry"
    else
        target="$service_entry"
    fi
    
    if sudo systemd-analyze verify "${SYSTEMD_DIR}/${target}" 2>/dev/null; then
        echo "   ✅ ${target} OK"
    else
        echo "   ❌ Erro de sintaxe em ${target}"
        sudo systemd-analyze verify "${SYSTEMD_DIR}/${target}" || true
    fi
done

# 5. Habilitar serviços
echo ""
echo "5. Habilitando serviços para iniciar no boot..."
for service_entry in "${SERVICES[@]}"; do
    if [[ "$service_entry" == *":"* ]]; then
        IFS=':' read -r source target <<< "$service_entry"
    else
        target="$service_entry"
    fi
    
    service_name=$(basename "$target")
    echo "   🔧 Habilitando ${service_name}..."
    sudo systemctl enable "${service_name}" || echo "   ⚠️  Falha ao habilitar ${service_name}"
done
echo "✅ Serviços habilitados."

# 6. Iniciar serviços (em ordem)
echo ""
echo "6. Iniciando serviços..."
echo "   🔹 Iniciando omnimind-qdrant.service..."
sudo systemctl start omnimind-qdrant.service || echo "   ⚠️  Qdrant pode já estar rodando via Docker"

sleep 2

echo "   🔹 Iniciando omnimind-daemon.service..."
sudo systemctl start omnimind-daemon.service || echo "   ⚠️  Falha ao iniciar daemon"

sleep 2

echo "   🔹 Iniciando omnimind-mcp.service..."
sudo systemctl start omnimind-mcp.service || echo "   ⚠️  Falha ao iniciar MCP"

sleep 3

echo "   🔹 Iniciando omnimind.service (inclui backend)..."
sudo systemctl start omnimind.service || echo "   ⚠️  Falha ao iniciar omnimind"

# 7. Aguardar inicialização
echo ""
echo "7. Aguardando inicialização (5s)..."
sleep 5

# 8. Verificar status
echo ""
echo "📊 Status dos Serviços:"
echo "======================="
for service_entry in "${SERVICES[@]}"; do
    if [[ "$service_entry" == *":"* ]]; then
        IFS=':' read -r source target <<< "$service_entry"
    else
        target="$service_entry"
    fi
    
    service_name=$(basename "$target")
    echo ""
    echo "🔍 ${service_name}:"
    sudo systemctl status "${service_name}" --no-pager -l | head -n 10 || echo "   ⚠️  Serviço não encontrado ou com erro"
done

# 9. Verificar portas
echo ""
echo "🌐 Portas em uso:"
ss -tlnp 2>/dev/null | grep -E ":(8000|4321|4322|4323|4324|4325|4326|4327|4328|4329|6333)" || echo "   Nenhuma porta OmniMind encontrada"

# 10. Testar endpoints
echo ""
echo "🔍 Testando endpoints:"
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

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Comandos úteis:"
echo "   Ver status:     sudo systemctl status omnimind.service"
echo "   Ver logs:       sudo journalctl -u omnimind.service -f"
echo "   Reiniciar:      sudo systemctl restart omnimind.service"
echo "   Parar:          sudo systemctl stop omnimind.service"
echo "   Desabilitar:    sudo systemctl disable omnimind.service"

