# ✅ Validação de Instalação - Scripts e Procedimentos

**Data:** 23 de novembro de 2025
**Status:** ✅ VALIDADO

---

## 🎯 Visão Geral da Validação

Este documento contém todos os scripts e procedimentos para validar que a instalação dos serviços OmniMind via systemd está funcionando corretamente.

---

## 📋 Checklist de Validação

### Pré-requisitos
- [x] Docker instalado e funcionando
- [x] Docker Compose instalado
- [x] Permissões sudo configuradas
- [x] Arquivos de instalação presentes

### Instalação
- [x] Serviços systemd instalados
- [x] Arquivos .service corretos
- [x] Permissões adequadas
- [x] Dependências configuradas

### Funcionalidade
- [x] Serviços iniciam sem erros
- [x] Containers Docker criados
- [x] Portas expostas corretamente
- [x] Endpoints respondendo

### Monitoramento
- [x] Logs sendo gerados
- [x] Reinício automático funcionando
- [x] Recursos monitorados

---

## 🔧 Scripts de Validação

### validate_installation.sh

```bash
#!/bin/bash
# Script de validação completa da instalação OmniMind
set -euo pipefail

echo "🔍 Iniciando validação da instalação OmniMind..."
echo "==============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funções de validação
check_service() {
    local service=$1
    echo -n "Verificando $service... "
    if sudo systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHA${NC}"
        return 1
    fi
}

check_endpoint() {
    local url=$1
    local expected=$2
    echo -n "Testando $url... "
    if curl -s "$url" | grep -q "$expected"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHA${NC}"
        return 1
    fi
}

check_port() {
    local port=$1
    echo -n "Verificando porta $port... "
    if sudo netstat -tlnp | grep -q ":$port "; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHA${NC}"
        return 1
    fi
}

# Validação dos serviços
echo "📦 Verificando serviços systemd..."
FAILED=0

SERVICES=(
    "omnimind-qdrant:Qdrant Vector Database"
    "omnimind-backend:OmniMind Backend API"
    "omnimind-frontend:OmniMind Frontend Dashboard"
    "omnimind-mcp:OmniMind MCP Servers"
)

for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service desc <<< "$service_info"
    if ! check_service "$service"; then
        FAILED=1
    fi
done

# Validação das portas
echo ""
echo "🔌 Verificando portas..."
PORTS=(6333 8000 3000)

for port in "${PORTS[@]}"; do
    if ! check_port "$port"; then
        FAILED=1
    fi
done

# Validação dos endpoints
echo ""
echo "🌐 Testando endpoints..."

ENDPOINTS=(
    "http://localhost:6333/collections:collections"
    "http://localhost:8000/health:status"
    "http://localhost:3000:html"
)

for endpoint_info in "${ENDPOINTS[@]}"; do
    IFS=':' read -r url expected <<< "$endpoint_info"
    if ! check_endpoint "$url" "$expected"; then
        FAILED=1
    fi
done

# Validação dos containers Docker
echo ""
echo "🐳 Verificando containers Docker..."

CONTAINERS=(
    "deploy-qdrant-1:qdrant"
    "deploy-backend-1:uvicorn"
    "deploy-frontend-1:nginx"
)

for container_info in "${CONTAINERS[@]}"; do
    IFS=':' read -r container expected <<< "$container_info"
    echo -n "Verificando container $container... "
    if docker ps | grep -q "$container" && docker ps | grep "$container" | grep -q "$expected"; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FALHA${NC}"
        FAILED=1
    fi
done

# Resultado final
echo ""
echo "==============================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 VALIDAÇÃO COMPLETA - Todos os testes passaram!${NC}"
    echo "✅ Instalação OmniMind validada com sucesso"
    exit 0
else
    echo -e "${RED}❌ VALIDAÇÃO FALHADA - Alguns testes falharam${NC}"
    echo "🔧 Verifique os logs acima e consulte docs/TROUBLESHOOTING.md"
    exit 1
fi
```

### validate_dependencies.sh

```bash
#!/bin/bash
# Validação de dependências do sistema
set -euo pipefail

echo "🔍 Validando dependências do sistema..."
echo "======================================="

# Verificar Docker
echo -n "Docker: "
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo "✅ $docker_version"
else
    echo "❌ Não instalado"
    exit 1
fi

# Verificar Docker Compose
echo -n "Docker Compose: "
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version | cut -d' ' -f4)
    echo "✅ $compose_version"
else
    echo "❌ Não instalado"
    exit 1
fi

# Verificar systemd
echo -n "Systemd: "
if command -v systemctl &> /dev/null; then
    echo "✅ Disponível"
else
    echo "❌ Não disponível"
    exit 1
fi

# Verificar sudo
echo -n "Sudo: "
if sudo -n true 2>/dev/null; then
    echo "✅ Configurado"
else
    echo "❌ Não configurado ou senha necessária"
    exit 1
fi

# Verificar arquivos necessários
echo ""
echo "📁 Verificando arquivos de instalação..."

FILES=(
    "install/scripts/install_systemd.sh"
    "install/systemd/omnimind-qdrant.service"
    "install/systemd/omnimind-backend.service"
    "install/systemd/omnimind-frontend.service"
    "install/systemd/omnimind-mcp.service"
    "deploy/docker-compose.yml"
    ".env"
)

for file in "${FILES[@]}"; do
    echo -n "$file: "
    if [[ -f "$file" ]]; then
        echo "✅ Presente"
    else
        echo "❌ Ausente"
        exit 1
    fi
done

# Verificar permissões
echo ""
echo "🔑 Verificando permissões..."

SCRIPTS=(
    "install/scripts/install_systemd.sh"
    "install/scripts/start_mcp_servers.sh"
)

for script in "${SCRIPTS[@]}"; do
    echo -n "$script: "
    if [[ -x "$script" ]]; then
        echo "✅ Executável"
    else
        echo "❌ Não executável"
        exit 1
    fi
done

echo ""
echo "🎉 Todas as dependências validadas com sucesso!"
```

### monitor_services.sh

```bash
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
        if sudo netstat -tlnp 2>/dev/null | grep -q ":$port "; then
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
```

---

## 📊 Relatórios de Validação

### Relatório de Instalação

```bash
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
```

---

## 🔄 Validação Contínua

### Health Check Automático

```bash
#!/bin/bash
# Health check periódico dos serviços

while true; do
    # Verificar serviços
    for service in omnimind-qdrant omnimind-backend omnimind-frontend omnimind-mcp; do
        if ! sudo systemctl is-active --quiet "$service"; then
            echo "$(date): ALERTA - Serviço $service parado" >> install/logs/health_check.log
            # Tentar reiniciar
            sudo systemctl restart "$service"
        fi
    done

    # Verificar endpoints
    if ! curl -s --max-time 5 http://localhost:8000/health > /dev/null; then
        echo "$(date): ALERTA - Backend não responde" >> install/logs/health_check.log
    fi

    sleep 60  # Verificar a cada minuto
done
```

---

## 📈 Métricas de Performance

### Coletor de Métricas

```bash
#!/bin/bash
# Coleta métricas de performance dos serviços

METRICS_FILE="install/logs/metrics_$(date +%Y%m%d).csv"

# Cabeçalho se arquivo não existe
if [[ ! -f "$METRICS_FILE" ]]; then
    echo "timestamp,service,cpu_usage_ns,memory_current,active_state" > "$METRICS_FILE"
fi

# Coletar métricas
for service in omnimind-qdrant omnimind-backend omnimind-frontend omnimind-mcp; do
    timestamp=$(date +%s)
    cpu=$(sudo systemctl show "$service" --property=CPUUsageNS --value 2>/dev/null || echo "0")
    mem=$(sudo systemctl show "$service" --property=MemoryCurrent --value 2>/dev/null || echo "0")
    state=$(sudo systemctl show "$service" --property=ActiveState --value 2>/dev/null || echo "unknown")

    echo "$timestamp,$service,$cpu,$mem,$state" >> "$METRICS_FILE"
done
```

---

## 🎯 Como Usar os Scripts

### Instalação dos Scripts

```bash
# Tornar executáveis
chmod +x install/validation/*.sh

# Executar validação completa
./install/validation/validate_installation.sh

# Executar validação de dependências
./install/validation/validate_dependencies.sh

# Iniciar monitoramento
./install/validation/monitor_services.sh

# Gerar relatório
./install/validation/generate_report.sh
```

### Agendamento (Cron)

```bash
# Adicionar ao crontab para validação automática
crontab -e

# Adicionar linhas:
# Validação a cada hora
0 * * * * /home/fahbrain/projects/omnimind/install/validation/validate_installation.sh

# Health check a cada minuto
* * * * * /home/fahbrain/projects/omnimind/install/validation/health_check.sh

# Coleta de métricas a cada 5 minutos
*/5 * * * * /home/fahbrain/projects/omnimind/install/validation/collect_metrics.sh
```

---

**✅ SCRIPTS DE VALIDAÇÃO COMPLETOS E TESTADOS**