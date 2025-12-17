# 🏗️ ARQUITETURA DE MIGRAÇÃO - DOCKER → SISTEMA OS
**Data:** 16 de Dezembro de 2025
**Status:** 📋 Análise Arquitetural Completa
**Versão:** 2.0 (Baseada em scripts existentes)

---

## 📊 ANÁLISE ATUAL (Estado Antes da Migração)

### Sistema Anterior (Docker)
```
🐳 docker-compose.yml (Deploy Container-Based)
├── Services:
│   ├── backend      → uvicorn (port 8000)
│   ├── frontend     → nginx (port 3000)
│   ├── qdrant       → qdrant (port 6333)  ← VECTOR DB
│   ├── redis        → redis (port 6379)   ← CACHE
│   └── benchmark    → python scripts
│
├── Environment Variables (Via Docker Network):
│   ├── QDRANT_URL = "http://qdrant:6333"
│   ├── REDIS_URL = "redis://redis:6379"
│   └── OLLAMA_BASE_URL = "http://host.docker.internal:11434"
│
└── Volumes:
    ├── ./data/qdrant → Storage Qdrant
    └── ./data → Dados persistentes
```

### OmniMind Atual (Hybrid Approach)
```
🚀 start_omnimind_system_robust.sh (Sistema OS)
├── Backend Cluster:
│   ├── Primary      (Port 8000) - Uvicorn workers=2
│   ├── Secondary    (Port 8080) - Uvicorn workers=2
│   └── Fallback     (Port 3001) - Uvicorn workers=2
│
├── Configuração:
│   ├── Python: 3.12.8
│   ├── GPU: CUDA 12.2 com Qiskit Aer GPU
│   └── PYTHONPATH: projeto root
│
└── Scripts Críticos:
    ├── run_cluster.sh → Inicia 3 backends
    ├── start_omnimind_system_robust.sh → Orquestra tudo
    └── start_omnimind_system_sudo_auto.sh → Auto-recovery
```

### OmniMind Config (config/omnimind.yaml)
```yaml
database:
  type: "qdrant"
  url: "${OMNIMIND_QDRANT_URL}"  ← MUDA PARA: http://localhost:6333

quantum:
  backend: "simulator"
  use_real_hardware: false  ← GPU simulator com Aer GPU local

server:
  workers: ${OMNIMIND_WORKERS:-2}  ← Cluster de 3 backends
  port: 8000  ← Primary
```

---

## 🔄 MIGRAÇÃO: MUDANÇAS NECESSÁRIAS

### MUDANÇA 1: URLs de Conexão
```bash
# ANTES (Docker)
export QDRANT_URL="http://qdrant:6333"
export REDIS_URL="redis://redis:6379"

# DEPOIS (Sistema OS)
export QDRANT_URL="http://localhost:6333"
export REDIS_URL="redis://localhost:6379"
export POSTGRES_URL="postgresql://omnimind:password@localhost:5432/omnimind"
```

### MUDANÇA 2: Localização de Dados
```bash
# ANTES (Docker volumes)
./data/qdrant/
./deploy/data/

# DEPOIS (Sistema OS - partições dedicadas)
/var/lib/qdrant/         ← Qdrant data (partição /var)
/var/lib/redis/          ← Redis snapshots
/var/lib/postgresql/     ← PostgreSQL data
/home/fahbrain/data/     ← Experimentos + cache user
```

### MUDANÇA 3: Serviços Systemd (Não Docker)
```bash
# NOVO (Sistema OS)
sudo systemctl start redis-server
sudo systemctl start qdrant
sudo systemctl start postgresql
# OmniMind Backend roda via run_cluster.sh (não via systemd para flexibilidade)
```

### MUDANÇA 4: Código de Inicialização
```python
# src/config/database.py

import os

def get_database_urls():
    """URLs adaptadas para sistema OS."""
    env = os.getenv("ENVIRONMENT", "production")

    if env == "docker_experiments":
        # Para experimentos em Docker
        return {
            "qdrant_url": "http://qdrant-exp:6333",
            "redis_url": "redis://redis-exp:6379",
        }
    else:
        # Sistema OS (padrão)
        return {
            "qdrant_url": os.getenv("QDRANT_URL", "http://localhost:6333"),
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "postgres_url": os.getenv("POSTGRES_URL", "postgresql://localhost:5432"),
        }
```

---

## 📋 ARQUITETURA FINAL (Sistema OS + Docker Experimentos)

```
┌─────────────────────────────────────────────────────────────────┐
│              Ubuntu 22.04 LTS (GTX 1650 GPU + CUDA 12.2)        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  SISTEMA OS (Produção)                    │
│  │ /var/lib/       │                                            │
│  ├─ qdrant/  ───────────────────────┐                         │
│  ├─ redis/        │                  │                         │
│  └─ postgresql/   │                  ▼                         │
│                   │          ┌──────────────────┐             │
│  /home/fahbrain/  │          │  Redis Server    │             │
│  ├─ .venv/        │          │  (port 6379)     │             │
│  ├─ projects/     │          └──────────────────┘             │
│  │ └─ omnimind/   │          ┌──────────────────┐             │
│  │   ├─ src/      ◄──────────│  Qdrant Vector   │             │
│  │   ├─ config/   │          │  DB (port 6333)  │             │
│  │   ├─ web/      │          └──────────────────┘             │
│  │   ├─ data/     │          ┌──────────────────┐             │
│  │   ├─ logs/     │          │ PostgreSQL       │             │
│  │   ├─ scripts/  │          │ (port 5432)      │             │
│  │   └─ .env      │          └──────────────────┘             │
│  │   └─ .venv/    │                                            │
│  │                │          ┌────────────────────────────────┐
│  └─ data/cache/   │          │  OmniMind Backend Cluster      │
│                   │          ├────────────────────────────────┤
│                   │          │ Primary    (8000) - Workers:2  │
│                   │          │ Secondary  (8080) - Workers:2  │
│                   │          │ Fallback   (3001) - Workers:2  │
│                   │          │                                │
│                   │          │ [GPU: CUDA 12.2 + Aer GPU]    │
│                   │          │ [Python: 3.12.8 + PyTorch]    │
│                   │          └────────────────────────────────┘
│                   │
│                   │          ┌──────────────────┐
│                   │          │  Frontend React  │
│                   └──────────│  (npm dev)       │
│                              │  (port 3000)     │
│                              └──────────────────┘
│
├─────────────────────────────────────────────────────────────────┤
│  🐳 DOCKER (Experimentos + Autogeração)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  docker-compose-experiments.yml                                │
│  ├─ omnimind-code-gen    (Geração automática de código)        │
│  ├─ omnimind-experiments (Testes isolados)                     │
│  ├─ qdrant-exp           (Vector DB isolado)                   │
│  ├─ redis-exp            (Cache isolado)                       │
│  └─ ollama-exp           (LLM local para experimentos)         │
│                                                                 │
│  Volumes:                                                      │
│  ├─ /data/experiments/                                         │
│  ├─ /data/generated-code/                                      │
│  └─ /logs/experiments/                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 MUDANÇAS DE CÓDIGO (Detalhadas)

### 1️⃣ Criar: `src/config/database_os.py` (Novo)

```python
"""
Database configuration para Sistema OS.
Adaptações para conexões localhost em vez de Docker network.
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """Configuração de BD baseada em ambiente."""

    ENVIRONMENTS = {
        "production": {
            "qdrant": {
                "url": "http://localhost:6333",
                "api_key": None,
                "timeout": 30.0,
            },
            "redis": {
                "url": "redis://localhost:6379/0",
                "decode_responses": True,
            },
            "postgres": {
                "host": "localhost",
                "port": 5432,
                "database": "omnimind",
                "user": "omnimind",
                "password": os.getenv("POSTGRES_PASSWORD", "changeme"),
            },
        },
        "docker_experiments": {
            "qdrant": {
                "url": "http://qdrant-exp:6333",
                "api_key": None,
                "timeout": 30.0,
            },
            "redis": {
                "url": "redis://redis-exp:6379/0",
                "decode_responses": True,
            },
            "postgres": {
                "host": "postgres-exp",
                "port": 5432,
                "database": "omnimind_exp",
                "user": "omnimind",
                "password": "experimental",
            },
        },
    }

    @classmethod
    def get_config(cls, environment: str = None) -> Dict[str, Any]:
        """Retorna configuração para ambiente."""
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "production")

        if environment not in cls.ENVIRONMENTS:
            raise ValueError(f"Unknown environment: {environment}")

        return cls.ENVIRONMENTS[environment]

    @classmethod
    def get_qdrant_url(cls, environment: str = None) -> str:
        """Retorna URL Qdrant."""
        config = cls.get_config(environment)
        return config["qdrant"]["url"]

    @classmethod
    def get_redis_url(cls, environment: str = None) -> str:
        """Retorna URL Redis."""
        config = cls.get_config(environment)
        return config["redis"]["url"]

    @classmethod
    def get_postgres_url(cls, environment: str = None) -> str:
        """Retorna URL PostgreSQL."""
        config = cls.get_config(environment)
        cfg = config["postgres"]
        return f"postgresql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
```

### 2️⃣ Atualizar: `src/api/main.py` (Existente)

```python
# ANTES
from src.config.omnimind import get_config
qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

# DEPOIS
from src.config.database_os import DatabaseConfig
config = DatabaseConfig.get_config()
qdrant_url = config["qdrant"]["url"]
redis_url = config["redis"]["url"]
```

### 3️⃣ Atualizar: `config/omnimind.yaml` (Existente)

```yaml
# ANTES
database:
  url: "${OMNIMIND_QDRANT_URL}"

# DEPOIS
database:
  url: "http://localhost:6333"  # Sistema OS
  # Para Docker experiments:
  # url: "http://qdrant-exp:6333"
```

### 4️⃣ Criar: `.env.system` (Novo)

```bash
# ============================================================================
# OmniMind System Environment Configuration (Sistema OS)
# ============================================================================

# Environment
ENVIRONMENT=production

# Database URLs (Sistema OS)
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
POSTGRES_URL=postgresql://omnimind:omnimind2025@localhost:5432/omnimind
POSTGRES_PASSWORD=omnimind2025

# GPU Configuration
CUDA_HOME=/usr
CUDA_PATH=/usr
CUDA_VISIBLE_DEVICES=0
LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}

# Qiskit + Aer GPU
QISKIT_AER_USE_GPU=1
QISKIT_SETTINGS=~/.qiskit/settings.conf

# PyTorch CUDA
PYTORCH_CUDA_ALLOC_CONF=backend:cudaMallocAsync

# OmniMind Cluster
OMNIMIND_WORKERS=2
OMNIMIND_BACKENDS=3
OMNIMIND_WORKERS_VALIDATION=2
OMNIMIND_DEBUG=false
OMNIMIND_AUTO_RECOVERY=true

# Dashboard
OMNIMIND_DASHBOARD_USER=admin
OMNIMIND_DASHBOARD_PASS=omnimind2025
OMNIMIND_DASHBOARD_AUTH_FILE=config/dashboard_auth.json

# Security
JWT_SECRET=your-secret-key-here-change-in-production
SECURITY_API_KEY=your-api-key-here

# LLM (Experimentos)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/omnimind.log
```

### 5️⃣ Criar: `docker-compose-experiments.yml` (Novo)

```yaml
# Docker Compose para Experimentos Isolados (NÃO Produção)
# Usar: docker-compose -f docker-compose-experiments.yml up -d

version: '3.8'

services:
  # Qdrant isolado para experimentos
  qdrant-exp:
    image: qdrant/qdrant:latest
    container_name: qdrant-exp
    ports:
      - "6334:6333"  # Porta diferente de produção
    volumes:
      - ./data/experiments/qdrant:/qdrant/storage
    environment:
      - QDRANT_API_KEY=exp-key-123
    restart: unless-stopped

  # Redis isolado para experimentos
  redis-exp:
    image: redis:alpine
    container_name: redis-exp
    ports:
      - "6380:6379"  # Porta diferente
    volumes:
      - ./data/experiments/redis:/data
    restart: unless-stopped

  # PostgreSQL isolado
  postgres-exp:
    image: postgres:15-alpine
    container_name: postgres-exp
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: omnimind_exp
      POSTGRES_USER: omnimind
      POSTGRES_PASSWORD: experimental
    volumes:
      - ./data/experiments/postgres:/var/lib/postgresql/data
    restart: unless-stopped

  # Ollama para LLM (experimentos)
  ollama-exp:
    image: ollama/ollama:latest
    container_name: ollama-exp
    ports:
      - "11435:11434"  # Porta diferente
    volumes:
      - ollama-exp:/root/.ollama
    environment:
      - OLLAMA_NUM_GPU=1  # Usar GPU da máquina host
    restart: unless-stopped

  # Gerador de Código Automático
  omnimind-code-gen:
    build:
      context: .
      dockerfile: Dockerfile.codegen  # Novo arquivo
    container_name: omnimind-code-gen
    volumes:
      - ./src:/app/src
      - ./data/generated-code:/app/generated-code
      - ./logs/experiments:/app/logs
    environment:
      ENVIRONMENT: docker_experiments
      QDRANT_URL: http://qdrant-exp:6333
      REDIS_URL: redis://redis-exp:6379
      OLLAMA_BASE_URL: http://ollama-exp:11434
      PYTHONPATH: /app
    depends_on:
      - qdrant-exp
      - redis-exp
      - ollama-exp
    restart: "no"  # Manual start

  # Experimentos isolados
  omnimind-experiments:
    build:
      context: .
      dockerfile: Dockerfile.experiments  # Novo arquivo
    container_name: omnimind-experiments
    volumes:
      - ./src:/app/src
      - ./data/experiments:/app/data
      - ./logs/experiments:/app/logs
    environment:
      ENVIRONMENT: docker_experiments
      QDRANT_URL: http://qdrant-exp:6333
      REDIS_URL: redis://redis-exp:6379
      CUDA_VISIBLE_DEVICES: 0  # GPU disponível
    depends_on:
      - qdrant-exp
      - redis-exp
    restart: "no"

volumes:
  ollama-exp:
```

---

## 📦 SERVIÇOS A INSTALAR (Sistema OS)

### Instalação Sequencial

```bash
# 1. Redis
sudo apt update
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server

# 2. PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres createdb omnimind
sudo -u postgres createuser -P omnimind

# 3. Qdrant (Build local)
# Opção A: Binário pré-compilado
wget https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-v1.7.0-x86_64-unknown-linux-gnu
chmod +x qdrant-*
sudo mv qdrant-* /usr/local/bin/qdrant

# Opção B: Via Cargo (se preferir build)
cargo install qdrant

# 4. Python Environment
python3.12 -m venv /home/fahbrain/projects/omnimind/.venv
source /home/fahbrain/projects/omnimind/.venv/bin/activate

# 5. Qiskit + Aer GPU
pip install qiskit==1.0.2 qiskit-aer
pip install --upgrade qiskit-aer --no-binary qiskit-aer  # GPU compile

# 6. PyTorch GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu122

# 7. OmniMind deps
cd /home/fahbrain/projects/omnimind
pip install -r requirements.txt -r requirements-dev.txt
```

---

## 🔐 Configuração Systemd (Serviços Persistentes)

### `/etc/systemd/system/omnimind-qdrant.service`
```ini
[Unit]
Description=Qdrant Vector Database for OmniMind
After=network.target

[Service]
Type=simple
User=omnimind
WorkingDirectory=/var/lib/qdrant
ExecStart=/usr/local/bin/qdrant --storage-path /var/lib/qdrant
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/omnimind-redis.service`
```ini
[Unit]
Description=Redis Server for OmniMind
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable omnimind-qdrant omnimind-redis postgresql redis-server
sudo systemctl start omnimind-qdrant omnimind-redis postgresql redis-server

# Verificar
sudo systemctl status omnimind-qdrant omnimind-redis postgresql redis-server
```

---

## ✅ FLUXO DE MIGRAÇÃO (Fase por Fase)

### ✅ FASE 0: Análise (CONCLUÍDA)
- [x] Entender docker-compose
- [x] Analisar scripts de startup
- [x] Identificar mudanças necessárias
- [x] Planejar arquitetura

### ⏳ FASE 1: Instalação Sistema (PRÓXIMA)
1. Redis → `/var/lib/redis`
2. PostgreSQL → `/var/lib/postgresql`
3. Qdrant → `/var/lib/qdrant`
4. Restaurar dados backup

### ⏳ FASE 2: Python + GPU
1. Python 3.12.8 (já feito)
2. Qiskit + Aer GPU
3. PyTorch GPU
4. Deps OmniMind

### ⏳ FASE 3: Código
1. Criar `src/config/database_os.py`
2. Atualizar `src/api/main.py`
3. Atualizar `config/omnimind.yaml`
4. Criar `.env.system`

### ⏳ FASE 4: Docker Experimentos
1. Criar `docker-compose-experiments.yml`
2. Criar `Dockerfile.codegen`
3. Criar `Dockerfile.experiments`

### ⏳ FASE 5: Inicialização
1. Iniciar Redis + PostgreSQL + Qdrant (systemd)
2. Iniciar Backend Cluster (run_cluster.sh)
3. Iniciar Frontend (npm dev)
4. Validar sistema completo

---

## 📊 Comparativa: Docker vs Sistema OS

| Aspecto | Docker (Antes) | Sistema OS (Depois) |
|--------|-------|---------|
| **Qdrant** | `qdrant:6333` (container) | `localhost:6333` (systemd) |
| **Redis** | `redis:6379` (container) | `localhost:6379` (systemd) |
| **PostgreSQL** | - | `localhost:5432` (systemd) |
| **Backend** | `backend:8000` (container) | `localhost:8000` (uvicorn) |
| **GPU** | Limitado/Complexo | CUDA 12.2 Nativo + Aer GPU |
| **Data** | `./data/qdrant` | `/var/lib/qdrant` |
| **Experimentos** | Docker compose | docker-compose-experiments.yml |
| **Uptime** | Docker daemon | systemd (mais estável) |

---

## 🎯 Benefícios da Nova Arquitetura

✅ **GPU Funciona:** CUDA 12.2 + Aer GPU nativo (antes não funcionava)
✅ **Mais Estável:** systemd + health checks vs Docker daemon
✅ **Melhor Performance:** Sem overhead de containers para produção
✅ **Experimentos Isolados:** Docker ainda disponível para testes
✅ **Escalabilidade:** Backend cluster (3 workers) rodando local
✅ **Dados Persistentes:** /var/lib partições dedicadas
✅ **Autorecuperação:** OmniMind pode reiniciar serviços via sudo

---

## 🚀 Próximo Passo

→ Executar FASE 1: Instalar Redis, PostgreSQL, Qdrant no sistema

