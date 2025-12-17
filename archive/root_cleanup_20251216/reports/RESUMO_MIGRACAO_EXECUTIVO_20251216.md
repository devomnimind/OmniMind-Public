# 📋 RESUMO EXECUTIVO - MIGRAÇÃO DOCKER → SISTEMA OS
**Data:** 16 de Dezembro de 2025
**Status:** ✅ Plano Completo + Scripts Prontos
**Tempo Estimado:** 3-4 horas

---

## 🎯 O Que Mudou?

### ❌ ANTES (Docker)
```
docker-compose.yml
├── backend      (container uvicorn)
├── qdrant       (container vector DB)
├── redis        (container cache)
├── frontend     (container nginx)
└── postgresql   (não existia)

GPU: Não funcionava bem
Produção: Docker daemon
```

### ✅ DEPOIS (Sistema OS)
```
Ubuntu 22.04 LTS (Nativo)
├── Backend Cluster (3x uvicorn rodando direto)
├── Qdrant (systemd service em /var/lib/qdrant)
├── Redis (systemd service em /var/lib/redis)
├── PostgreSQL (systemd service)
└── Frontend (npm dev)

GPU: CUDA 12.2 + Aer GPU ✨ FUNCIONANDO
Produção: systemd (mais estável)
Docker: Apenas experimentos isolados
```

---

## 🔄 MAPA DE MUDANÇAS

| Componente | Docker | Sistema OS | Mudança |
|-----------|--------|-----------|--------|
| **Qdrant** | `qdrant:6333` (container) | `localhost:6333` (systemd) | URLs mudam |
| **Redis** | `redis:6379` (container) | `localhost:6379` (systemd) | URLs mudam |
| **PostgreSQL** | NÃO existia | `localhost:5432` (novo) | Novo BD |
| **Backend** | container 8000 | uvicorn 8000 (direto) | Sem container |
| **GPU** | Complicado | CUDA 12.2 nativo | FUNCIONA! |
| **Dados** | `./data/qdrant` | `/var/lib/qdrant` | Partição dedicada |
| **Experimentos** | Junto | docker-compose-experiments.yml (isolado) | Separado |

---

## 📦 ARQUIVOS CRIADOS

### 1. 📄 Documentação
```
✅ ARQUITETURA_MIGRACAO_DOCKER_SISTEMA_OS_20251216.md (Completo)
✅ PLANO_MIGRACAO_LINUX_SISTEMA_20251216.md (Anterior)
```

### 2. 🔧 Scripts de Instalação
```
✅ scripts/migration/install_system_databases.sh (Automático)
   └─ Fases: 0 (check), 1 (install), 2 (restore),
             3 (python), 4 (config), 5 (validate)
```

### 3. 📝 Configurações (A Criar)
```
⏳ src/config/database_os.py (Novo)
⏳ .env.system (Novo)
⏳ docker-compose-experiments.yml (Novo)
```

---

## 🚀 COMO COMEÇAR (3 Passos)

### PASSO 1: Executar Script de Migração
```bash
cd /home/fahbrain/projects/omnimind

# Tornar executável
chmod +x scripts/migration/install_system_databases.sh

# Executar tudo automaticamente (ou fase por fase)
./scripts/migration/install_system_databases.sh all

# OU fase por fase (recomendado para debug):
./scripts/migration/install_system_databases.sh 0     # Check
./scripts/migration/install_system_databases.sh 1     # Install
./scripts/migration/install_system_databases.sh 2     # Restore backup
./scripts/migration/install_system_databases.sh 3     # Python + GPU
./scripts/migration/install_system_databases.sh 4     # Configure code
./scripts/migration/install_system_databases.sh 5     # Validate
```

### PASSO 2: Ativar Ambiente
```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
source .env.system
```

### PASSO 3: Iniciar Sistema
```bash
# Terminal 1: Backend Cluster (3 instâncias)
./scripts/canonical/system/run_cluster.sh

# Terminal 2: Frontend
cd web/frontend && npm run dev

# Terminal 3: Validar saúde
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 📊 O QUE CADA SCRIPT FAZ

### `install_system_databases.sh`
```
PHASE 0: Check
├─ GPU detectada?
├─ CUDA 12.2 ok?
├─ Backup acessível?
└─ Espaço em disco?

PHASE 1: Install
├─ Redis do apt
├─ PostgreSQL do apt
├─ Qdrant binário
└─ Systemd configs

PHASE 2: Restore
├─ Copiar Qdrant backup → /var/lib/qdrant
├─ Copiar Redis backup → /var/lib/redis
├─ Permissões corretas
└─ Restart serviços

PHASE 3: Python + GPU
├─ Python 3.12.8 venv
├─ Qiskit + Aer GPU (compile)
├─ PyTorch CUDA 12.2
└─ Validar GPU

PHASE 4: Configure Code
├─ Criar database_os.py
├─ Criar .env.system
├─ Update omnimind.yaml
└─ Connection strings

PHASE 5: Validate
├─ Redis: redis-cli ping
├─ PostgreSQL: psql connect
├─ Qdrant: curl health
└─ GPU: torch.cuda.is_available()
```

### `run_cluster.sh` (Existente)
```
Inicia 3 backends em paralelo:
├─ Port 8000 (Primary) - 2 workers
├─ Port 8080 (Secondary) - 2 workers
└─ Port 3001 (Fallback) - 2 workers

Com HA (High Availability) automático
```

### `start_omnimind_system_robust.sh` (Existente)
```
Orquestra tudo:
├─ Kill serviços antigos
├─ Health check com retry
├─ CPU stabilization
├─ GPU initialization
├─ Auto-recovery enable
└─ Logs detalhados
```

---

## 🔑 MUDANÇAS DE CÓDIGO NECESSÁRIAS

### 1. URLs de Conexão
```python
# ANTES (Docker)
QDRANT_URL = "http://qdrant:6333"
REDIS_URL = "redis://redis:6379"

# DEPOIS (Sistema OS)
QDRANT_URL = "http://localhost:6333"
REDIS_URL = "redis://localhost:6379"
POSTGRES_URL = "postgresql://omnimind:password@localhost:5432/omnimind"
```

### 2. Nova Classe de Configuração
```python
# src/config/database_os.py (NOVO)
class DatabaseConfig:
    ENVIRONMENTS = {
        "production": {...localhost...},      # Sistema OS
        "docker_experiments": {...docker...}, # Experimentos
    }
```

### 3. Environment Variables
```bash
# .env.system (NOVO)
ENVIRONMENT=production
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
POSTGRES_PASSWORD=omnimind2025
CUDA_VISIBLE_DEVICES=0
QISKIT_AER_USE_GPU=1
OMNIMIND_WORKERS=2
OMNIMIND_BACKENDS=3
```

---

## ⚠️ CUIDADOS CRÍTICOS

### ❌ NÃO FAZER
```bash
# ❌ Não use docker-compose.yml antigo
docker-compose up  # VAI FALHAR

# ❌ Não reinstale Docker completamente
# Os dados antigos estão no backup

# ❌ Não mude /var/lib sem avisar
# Systemd vai procurar lá

# ❌ Não use Python < 3.12
# Aer GPU requer 3.12+
```

### ✅ FAZER
```bash
# ✅ Usar docker-compose-experiments.yml para novos testes
docker-compose -f docker-compose-experiments.yml up

# ✅ Restaurar dados antes de iniciar
./scripts/migration/install_system_databases.sh 2

# ✅ Ativar ambiente correto
source .env.system

# ✅ Validar GPU antes de começar
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 📈 BENEFÍCIOS

| Benefício | Antes | Depois |
|-----------|-------|--------|
| **GPU Funciona** | ❌ Não | ✅ Sim (CUDA 12.2) |
| **Performance** | Docker overhead | Direto no OS |
| **Uptime** | Docker daemon | systemd estável |
| **Escalabilidade** | 1 container | 3 backends HA |
| **Experiências** | Misturado | Isolado em Docker |
| **Recuperação** | Manual | Auto-recovery |
| **Dados** | ./data relativo | /var partição dedicada |

---

## 🧪 TESTE RÁPIDO

```bash
# Após completar migração:

# 1. Verificar serviços
sudo systemctl status redis-server postgresql qdrant

# 2. Conectar em cada BD
redis-cli ping              # Deve retornar PONG
psql -U omnimind -d omnimind  # Deve abrir shell
curl http://localhost:6333/health  # Deve retornar JSON

# 3. Verificar GPU
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# 4. Iniciar backend
./scripts/canonical/system/run_cluster.sh &
sleep 5

# 5. Testar endpoint
curl http://localhost:8000/health
```

---

## 📞 SUPORTE

Se algo falhar:

1. **Check logs:**
   ```bash
   tail -f logs/migration_*.log
   tail -f logs/startup_detailed.log
   tail -f /var/log/syslog
   ```

2. **Rollback parcial:**
   ```bash
   # Reverter para phase anterior e debugar
   ./scripts/migration/install_system_databases.sh N
   ```

3. **Verificar systemd:**
   ```bash
   sudo journalctl -u qdrant -n 50
   sudo journalctl -u redis-server -n 50
   ```

4. **Restaurar backup:**
   ```bash
   # Dados ainda estão em HD externo
   sudo cp -r /media/fahbrain/DEV_BRAIN_CLEAN/databases/20251214_070626/qdrant/* /var/lib/qdrant/
   ```

---

## ✅ CHECKLIST FINAL

Após completar migração:

- [ ] Todos os 5 phases completaram sem erro
- [ ] `systemctl status` de todos os serviços: `active (running)`
- [ ] `redis-cli ping` → PONG
- [ ] `psql -U omnimind -d omnimind -c "SELECT 1"` → 1
- [ ] `curl http://localhost:6333/health` → JSON
- [ ] `nvidia-smi` mostra GTX 1650
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` → True
- [ ] `./scripts/canonical/system/run_cluster.sh` inicializa 3 backends
- [ ] `curl http://localhost:8000/health` → 200 OK
- [ ] Frontend inicia: `npm run dev` em web/frontend/
- [ ] GPU é usado: `nvidia-smi` mostra processo python

---

## 🎉 SUCESSO!

Se todas as verificações passarem:

```bash
✅ Sistema em produção
✅ GPU funcionando
✅ Backend cluster rodando (3x HA)
✅ Frontend servindo
✅ Dados persistentes em /var/lib
✅ Auto-recovery ativo
✅ Docker disponível para experimentos

🚀 OmniMind está operacional!
```

