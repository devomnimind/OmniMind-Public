#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Sistema OmniMind Completo...${NC}"

# Garantir permissão de execução no run_cluster
chmod +x scripts/run_cluster.sh

# 1. Limpeza
echo "🧹 Limpando processos antigos..."
pkill -f "python web/backend/main.py"
pkill -f "uvicorn web.backend.main:app"
pkill -f "vite"
sleep 2

# 2. Iniciar Backend Cluster
echo -e "${GREEN}🔌 Iniciando Backend Cluster...${NC}"
./scripts/run_cluster.sh

# Aguardar Backend subir
echo "⏳ Aguardando Backend inicializar (10s)..."
sleep 10

# Verificar Health Check (usando o endpoint /health/ que agora é servido pelo router)
# Nota: O endpoint raiz /health foi removido do main.py, agora é /health/ (com barra) ou /health (se o router permitir sem barra)
# O router tem prefix="/health" e @router.get("/"). Então é /health/
if curl -s http://localhost:8000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Backend (Primary) Online!${NC}"
elif curl -s http://localhost:8000/api/v1/status > /dev/null; then
    echo -e "${GREEN}✅ Backend (Primary) Online (via Status API)!${NC}"
else
    echo -e "${RED}❌ Falha ao conectar no Backend (Port 8000). Verifique logs/backend_8000.log${NC}"
    tail -n 10 logs/backend_8000.log
fi

# 3. Iniciar Frontend
echo -e "${GREEN}🎨 Iniciando Frontend...${NC}"
cd web/frontend
# Verificar se node_modules existe, se não, instalar
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do Frontend..."
    npm install
fi

nohup npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../logs/frontend.pid
echo "Frontend iniciado com PID $FRONTEND_PID"

# 4. Verificação Final
echo -e "${GREEN}🔍 Verificando status do sistema...${NC}"
sleep 5

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend rodando (PID $FRONTEND_PID)${NC}"
    echo "   Acesse: http://localhost:3000"
else
    echo -e "${RED}❌ Frontend falhou ao iniciar. Verifique logs/frontend.log${NC}"
    cat ../../logs/frontend.log
fi

echo -e "${GREEN}✨ Sistema OmniMind Reiniciado!${NC}"
echo "Backend Cluster: Ports 8000, 8080, 3001"
echo "Frontend: http://localhost:3000"
echo "Logs Directory: logs/"
