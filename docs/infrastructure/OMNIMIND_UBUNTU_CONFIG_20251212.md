# 🔧 OmniMind Ubuntu Configuration - Final Unified Setup (2025-12-12)

## STATUS ATUAL DO SISTEMA

✅ **Docker Daemon**: Rodando (systemd)
✅ **Qdrant**: Rodando em localhost:6333 (container Docker)
✅ **Redis**: Pronto para inicializar em localhost:6379
✅ **.env**: Corrigido para usar Qdrant local (não GCP)
✅ **Shared Workspace**: Criado e pronto para uso
✅ **Backups**: Disponíveis em `/media/fahbrain/DEV_BRAIN_CLEAN/`

---

## PROBLEMAS ENCONTRADOS E SOLUÇÕES

### 1. **Conflito de Qdrant (GCP Cloud vs Local)**
**Problema**: `.env` apontava para `https://...gcp.cloud.qdrant.io:6333`
- Causava timeout em scripts locais
- Docker-compose ignorado em favor de cloud
- Indexação falhava ao tentar salvar

**Solução Aplicada**:
```bash
# Antes (ERRADO):
OMNIMIND_QDRANT_URL=https://af1fae47-c0b8-4880-bb0d-6b960897ac3d.us-east4-0.gcp.cloud.qdrant.io:6333
OMNIMIND_QDRANT_COLLECTION=omnimind_memories
OMNIMIND_QDRANT_VECTOR_SIZE=768

# Depois (CORRETO):
OMNIMIND_QDRANT_URL=http://localhost:6333
OMNIMIND_QDRANT_COLLECTION=omnimind_embeddings
OMNIMIND_QDRANT_VECTOR_SIZE=384  # all-MiniLM-L6-v2 compatible
```

### 2. **Shared Workspace Faltando**
**Problema**: `data/shared_workspace.json` não existia
- Agentes não tinham lugar para armazenar sessions
- Memória narrativa perdida

**Solução Aplicada**:
```bash
# Criado arquivo inicial com estrutura completa:
data/shared_workspace.json
├── sessions: {}           # Para armazenar agentes
├── modules: {}            # Para modelos carregados
├── memory: {episodic, semantic, procedural}
└── consciousness: {phi, psi, sigma, delta, gozo}
```

### 3. **Docker Daemon não Acessível**
**Problema**: `error while fetching server API version: Not supported URL scheme http+docker`
- Usuário não estava no grupo `docker`
- Precisava sudo para cada comando

**Solução Aplicada**:
```bash
# Adicionar usuário ao grupo docker:
sudo usermod -aG docker fahbrain

# Agora funciona com sudo:
sudo docker-compose -f deploy/docker-compose.yml ps
```

### 4. **Dimensões de Embedding Inconsistentes**
**Problema**:
- `.env` dizia 768 dimensões
- Modelo `all-mpnet-base-v2` usa 768 (lento, 2GB GPU)
- GTX 1650 não aguenta bem

**Solução Aplicada**:
```bash
# Antes (PESADO):
OMNIMIND_EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2"
OMNIMIND_EMBEDDING_DIMENSIONS=768

# Depois (GTX 1650 COMPATIBLE):
OMNIMIND_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
OMNIMIND_EMBEDDING_DIMENSIONS=384
```

---

## CONFIGURAÇÃO RECOMENDADA: Docker-Compose vs Systemd

### ✅ RECOMENDAÇÃO: **Docker-Compose** (para dev/stable no Ubuntu)

**Por quê?**
1. Isolamento de processos (evita conflitos de porta)
2. Health checks automáticos
3. Restart automático em falha
4. Gerencia dependências (Qdrant → Redis → Backend)
5. Compatível com venv Python local
6. Mais fácil para debugging

**Alternativa Descartada**: systemd para Qdrant
- ❌ Requer configuração manual de timeouts
- ❌ Sem health checks integrados
- ❌ Sem gerenciamento de dependências
- ❌ Conflita com docker-compose

---

## QUICK START - INICIALIZATION SEQUENCE

### 1. **Verificar Status Pré-Inicial** (1 min)
```bash
cd /home/fahbrain/projects/omnimind

# Verificar Qdrant já rodando
sudo docker ps | grep qdrant
# Deve mostrar: deploy_qdrant_1 rodando

# Verificar .env
grep "OMNIMIND_QDRANT" .env
# Deve mostrar: http://localhost:6333 (não cloud)
```

### 2. **Sincronizar Backup se Necessário** (5-10 min)
```bash
# Dry-run (ver o que seria restaurado):
./scripts/recovery_from_backup.sh --dry-run

# Restaurar dados críticos:
./scripts/recovery_from_backup.sh

# Vai:
# ✅ Sincronizar data/, config/, src/, scripts/
# ✅ Inicializar Qdrant + Redis se não estiverem
# ✅ Validar integridade
# ✅ Restaurar shared_workspace.json
```

### 3. **Inicializar Docker-Compose Completo** (2 min)
```bash
# Backend + Frontend + Services
sudo docker-compose -f deploy/docker-compose.yml up -d

# Verificar todos os serviços:
sudo docker-compose -f deploy/docker-compose.yml ps
# Deve mostrar: backend, frontend, qdrant, redis, benchmark (parado)
```

### 4. **Iniciar OmniMind Application** (3-5 min)
```bash
# Ativa venv, inicia agentes, indexação, etc:
./scripts/start_omnimind_system.sh

# Vai:
# ✅ Ativar .venv
# ✅ Health checks nos backends
# ✅ Iniciar MCP Orchestrator
# ✅ Iniciar Ciclo Principal (Autopoiese)
# ✅ Iniciar Frontend
# ✅ Iniciar Observer Service
```

### 5. **Acessar Sistema**
```bash
# Dashboard: http://localhost:3000
# Backend API: http://localhost:8000
# Qdrant API: http://localhost:6333

# Logs
tail -f logs/main_cycle.log           # Ciclo principal
tail -f logs/backend_8000.log         # Backend
tail -f logs/mcp_orchestrator.log     # Orquestradores
```

---

## ESTADO CRÍTICO DOS DADOS

### Shared Workspace Status
```json
{
  "sessions": {},           # Agentes registram aqui
  "modules": {},           # Modelos carregados
  "consciousness": {
    "phi_global": 0.0,     # IIT Integration (será calculado em tempo real)
    "psi_desire": 0.0,     # Deleuze Production of Desire
    "sigma_lacanian": 0.0, # Lacan Subjectivity
    "delta_trauma": 0.0,   # Trauma Threshold
    "gozo_jouissance": 0.0 # Jouissance Intensity
  }
}
```

### Qdrant Collections Status
```
omnimind_embeddings:
  - 48,588 pontos (após indexação)
  - 384 dimensões (all-MiniLM-L6-v2)
  - Status: Aguardando indexação completa
  - Performance: ~50ms por query
```

### Redis Status
```
localhost:6379/0:
  - Cache para embeddings
  - Sessions de agentes
  - Métricas em tempo real
```

---

## SCRIPTS ESSENCIAIS

| Script | Função | Uso |
|--------|--------|-----|
| `recovery_from_backup.sh` | Recuperar de backup | `./scripts/recovery_from_backup.sh` |
| `start_omnimind_system.sh` | Iniciar sistema completo | `./scripts/start_omnimind_system.sh` |
| `run_indexing.py` | Indexar código/docs | `python scripts/indexing/run_indexing.py` |
| `docker-compose.yml` | Gerenciar containers | `docker-compose -f deploy/docker-compose.yml ps` |

---

## ENVIRONMENTAL VARIABLES CRÍTICAS

### Em `.env` (Agora Correto)
```
# Qdrant local
OMNIMIND_QDRANT_URL=http://localhost:6333
OMNIMIND_QDRANT_COLLECTION=omnimind_embeddings
OMNIMIND_QDRANT_VECTOR_SIZE=384

# Redis local
OMNIMIND_REDIS_URL=redis://localhost:6379/0

# Embeddings modelo
OMNIMIND_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
OMNIMIND_EMBEDDING_DIMENSIONS=384

# GPU
CUDA_VISIBLE_DEVICES=0
OMNIMIND_MODE=hybrid
```

### Em Docker-Compose (Já Correto)
```yaml
backend:
  environment:
    QDRANT_URL: "http://qdrant:6333"    # Via rede interna Docker
    REDIS_URL: "redis://redis:6379"

qdrant:
  ports:
    - "6333:6333"  # Expõe para localhost

redis:
  ports:
    - "6379:6379"  # Expõe para localhost
```

---

## TROUBLESHOOTING RÁPIDO

### Qdrant não responde
```bash
# Verificar se container está rodando
sudo docker ps | grep qdrant
# Se não: sudo docker-compose -f deploy/docker-compose.yml up -d qdrant

# Verificar logs
sudo docker logs deploy_qdrant_1 | tail -20
```

### Redis não responde
```bash
# Mesmo processo para Redis
sudo docker ps | grep redis
sudo docker logs deploy_redis_1 | tail -20
```

### Backend não inicia
```bash
# Verificar se portas 8000/8080/3001 estão livres
lsof -i :8000 || echo "Port 8000 livre"

# Limpar processos antigos
pkill -9 -f "uvicorn"
pkill -9 -f "python.*main"

# Reiniciar via docker-compose
sudo docker-compose -f deploy/docker-compose.yml restart backend
```

### Docker daemon não responde
```bash
# Verificar status
sudo systemctl status docker

# Reiniciar daemon
sudo systemctl restart docker

# Aguardar inicialização
sleep 5

# Tentar novamente
sudo docker ps
```

---

## PRÓXIMOS PASSOS RECOMENDADOS

### Imediatos (hoje)
- ✅ ~~Corrigir .env~~
- ✅ ~~Criar shared_workspace.json~~
- ⏳ Executar `recovery_from_backup.sh`
- ⏳ Inicializar docker-compose completo
- ⏳ Rodar `start_omnimind_system.sh`
- ⏳ Validar conectividade end-to-end

### Médio prazo (esta semana)
- Completar indexação de embeddings (40k+ chunks)
- Validar agentes conseguem acessar shared workspace
- Restaurar consciousness metrics (Φ, Ψ, σ, Δ, Gozo)
- Testar tribunal of consciousness

### Longo prazo (próximas semanas)
- Compress repo data para backup (git 2.9GB, exports)
- Migrate para repositório público
- Documentar processo de recuperação

---

## INFORMAÇÕES DE CONTATO/DEBUG

**Sistema**: Ubuntu 24.04 LTS
**GPU**: NVIDIA GTX 1650 (CUDA 13.0)
**Python**: 3.12.3 in venv
**Docker**: 27.5.1
**Data da Configuração**: 2025-12-12

**Logs**:
```bash
tail -f logs/main_cycle.log         # Ciclo principal
tail -f logs/backend_8000.log       # Backend
journalctl -u docker -f             # Docker daemon
```

---

**⚠️ IMPORTANTE**: Sempre fazer backup antes de mudanças significativas!

