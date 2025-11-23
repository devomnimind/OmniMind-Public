#!/bin/bash
# Validação de dependências do sistema
set -euo pipefail

echo "🔍 Validando dependências do sistema..."
echo "======================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar Docker
echo -n "Docker: "
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo -e "${GREEN}✅ $docker_version${NC}"
else
    echo -e "${RED}❌ Não instalado${NC}"
    exit 1
fi

# Verificar Docker Compose
echo -n "Docker Compose: "
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version | cut -d' ' -f4)
    echo -e "${GREEN}✅ $compose_version${NC}"
else
    echo -e "${RED}❌ Não instalado${NC}"
    exit 1
fi

# Verificar systemd
echo -n "Systemd: "
if command -v systemctl &> /dev/null; then
    echo -e "${GREEN}✅ Disponível${NC}"
else
    echo -e "${RED}❌ Não disponível${NC}"
    exit 1
fi

# Verificar sudo
echo -n "Sudo: "
if sudo -n true 2>/dev/null; then
    echo -e "${GREEN}✅ Configurado${NC}"
else
    echo -e "${YELLOW}⚠️  Necessária senha ou não configurado${NC}"
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
        echo -e "${GREEN}✅ Presente${NC}"
    else
        echo -e "${RED}❌ Ausente${NC}"
        exit 1
    fi
done

# Verificar permissões
echo ""
echo "🔑 Verificando permissões..."

SCRIPTS=(
    "install/scripts/install_systemd.sh"
    "install/scripts/start_mcp_servers.sh"
    "install/validation/validate_installation.sh"
)

for script in "${SCRIPTS[@]}"; do
    echo -n "$script: "
    if [[ -x "$script" ]]; then
        echo -e "${GREEN}✅ Executável${NC}"
    else
        echo -e "${RED}❌ Não executável${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}🎉 Todas as dependências validadas com sucesso!${NC}"