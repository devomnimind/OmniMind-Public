# 🔄 PLANO ESTRATÉGICO DE MIGRAÇÃO - UBUNTU 22.04 LTS
**Data:** 16 de Dezembro de 2025
**Máquina:** Formatada há 5 dias | Backup de 11-12 Dezembro disponível
**Estratégia:** Sistema Operacional + Docker Experimentos
**Status:** ⏳ Planejamento Concluído

---

## 📊 SITUAÇÃO ATUAL

### Hardware Detectado
```
Processador: x86_64 (Linux omnimind-dev)
GPU: NVIDIA GeForce GTX 1650 (4GB VRAM)
CUDA: 12.2 (Instalado e funcional)
NVIcc: /usr/local/cuda/bin/nvcc ✅

Disco SSD Principal: 931GB total
├── /           (372.5G) → 15G usado, 333G disponível
├── /home       (279.4G) → 60G usado, 201G disponível
├── /var        (251.5G) → 5G usado, 229G disponível
└── [SWAP]      (22.4G)

HD Externo: 465GB (/media/fahbrain/DEV_BRAIN_CLEAN)
└── Backup de 11-12 Dezembro (Qdrant 1.8GB, Redis 4KB, PostgreSQL 4KB)
```

### Python Detectado
- **Versão:** 3.10.12
- **Pip:** 22.0.2
- **Status:** ❌ Precisa atualizar para 3.12.8

### Serviços Atuais
- Docker: ❌ **NÃO INSTALADO**
- Qdrant: ❌ Apenas backup (1.8GB no HD externo)
- Redis: ❌ Apenas estrutura vazia
- PostgreSQL: ❌ Apenas estrutura vazia

---

## 🎯 PLANO DE AÇÃO (Fases)

### FASE 0: Preparação (30 min)
```bash
# 1. Criar venv com Python 3.12.8
cd /home/fahbrain/projects/omnimind
python3.12 -m venv .venv 2>/dev/null || python3.11 -m venv .venv
source .venv/bin/activate

# 2. Verificar CUDA
nvidia-smi
nvcc --version

# 3. Fix permissões do backup
sudo chown -R fahbrain:fahbrain /media/fahbrain/DEV_BRAIN_CLEAN/
sudo chmod -R 755 /media/fahbrain/DEV_BRAIN_CLEAN/
```

### FASE 1: Instalação de Sistema (Sistema OS - Não Docker)

#### 1.1 Redis (Sistema)
```bash
# Instalação
sudo apt update
sudo apt install -y redis-server

# Configuração
sudo systemctl start redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server

# Verificação
redis-cli ping  # Deve retornar PONG
```

#### 1.2 PostgreSQL (Sistema)
```bash
# Instalação
sudo apt install -y postgresql postgresql-contrib

# Iniciar
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificação
sudo -u postgres psql -c "SELECT version();"
```

#### 1.3 Qdrant (Sistema via APT/Download)
```bash
# Opção A: Build desde zero (Rust necessário)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
git clone https://github.com/qdrant/qdrant.git
cd qdrant
cargo build --release

# Opção B: Download binário pré-compilado (mais rápido)
wget https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-v1.7.0-x86_64-unknown-linux-gnu
chmod +x qdrant-*
sudo mv qdrant-* /usr/local/bin/qdrant

# Iniciar
qdrant --storage-path /var/lib/qdrant &
# ou via systemd (próximo passo)
```

#### 1.4 Restaurar Bancos de Dados (Do Backup)
```bash
# Qdrant: Copiar dados backup
sudo cp -r /media/fahbrain/DEV_BRAIN_CLEAN/databases/20251214_070626/qdrant /var/lib/qdrant

# Permissões
sudo chown -R qdrant:qdrant /var/lib/qdrant
sudo chmod -R 755 /var/lib/qdrant
```

### FASE 2: Dependências Python (Sistema)

#### 2.1 Atualizar Python
```bash
# Ubuntu 22.04 vem com 3.10, instalar 3.12.8
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Criar/atualizar venv
cd /home/fahbrain/projects/omnimind
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python --version  # Deve ser 3.12.8
```

#### 2.2 Instalar Qiskit + Aer GPU
```bash
# ⚠️ ORDEM CRÍTICA PARA GPU:
pip install --upgrade pip setuptools wheel
pip install numpy scipy scikit-learn

# Qiskit base
pip install qiskit==1.0.2 qiskit-ibmq

# Aer GPU (compilar localmente com CUDA)
git clone https://github.com/Qiskit/qiskit-aer.git
cd qiskit-aer
pip install -r requirements-dev.txt
pip install pybind11 scikit-build cmake

# Compilar com CUDA (vai levar 15-20 min)
python setup.py build_ext --inplace -j4

# Verificar
python -c "from qiskit_aer import AerSimulator; print(AerSimulator().available_methods)"
```

#### 2.3 Instalar PyTorch GPU
```bash
# Pytorch com CUDA 12.2
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu122

# Verificar
python -c "import torch; print(torch.cuda.is_available())"  # True
print(torch.cuda.get_device_name(0))  # GeForce GTX 1650
```

#### 2.4 Instalar Dependências OmniMind
```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# Requirements principais
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Validar
python -m pytest tests/ -x --tb=short 2>&1 | head -50
```

### FASE 3: Docker (Apenas Experimentos)

```bash
# Instalar Docker
sudo apt install -y docker.io docker-compose

# Usuário docker
sudo usermod -aG docker fahbrain
newgrp docker

# Verificar
docker --version
docker run hello-world
```

#### Usar Docker para:
- Experimentos isolados
- Testes de versões alternativas
- Sandboxing de features experimentais

```yaml
# docker-compose.yml exemplo
version: '3.8'
services:
  omnimind-experiment:
    build: .
    volumes:
      - ./src:/app/src
      - ./data/experiments:/app/experiments
    environment:
      - CUDA_VISIBLE_DEVICES=0
    ports:
      - "8001:8000"  # Porta diferente do sistema
```

### FASE 4: Validação GPU + Qiskit

```bash
# Script teste completo
python tests/validate_gpu_qiskit.py
```

Deveria retornar:
```
✅ GPU Detectado: GeForce GTX 1650
✅ CUDA Disponível: 12.2
✅ Qiskit Aer com GPU: Disponível
✅ PyTorch GPU: Operacional
✅ Qdrant: Conectado
✅ Redis: Conectado
✅ PostgreSQL: Conectado
```

### FASE 5: Mudanças de Código (Necessárias)

#### 5.1 Caminhos de Configuração

**ANTES:**
```python
# src/config/database.py - Docker paths
QDRANT_URL = "http://qdrant:6333"
REDIS_URL = "redis://redis:6379"
POSTGRES_URL = "postgresql://user:pass@postgres:5432"
```

**DEPOIS:**
```python
# src/config/database.py - Sistema OS paths
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://localhost:5432")
```

#### 5.2 GPU Fallback (Já implementado, validar)

```python
# src/quantum_consciousness/quantum_backend.py
def initialize_simulator():
    """Validado para GPU com fallback."""
    try:
        backend = AerSimulator(device='GPU', method='statevector')
        return backend
    except Exception:
        logger.warning("GPU not available, using CPU")
        return AerSimulator(device='CPU', method='statevector')
```

---

## 📋 CRONOGRAMA DETALHADO

| Fase | Tarefa | Tempo | Prioridade | Status |
|------|--------|-------|-----------|--------|
| 0 | Preparação venv | 30 min | 🔴 CRÍTICA | ⏳ |
| 1 | Redis Sistema | 15 min | 🔴 CRÍTICA | ⏳ |
| 1 | PostgreSQL Sistema | 15 min | 🔴 CRÍTICA | ⏳ |
| 1 | Qdrant Binário | 30-60 min | 🔴 CRÍTICA | ⏳ |
| 1 | Restaurar Bancos | 20 min | 🔴 CRÍTICA | ⏳ |
| 2 | Python 3.12.8 | 15 min | 🔴 CRÍTICA | ⏳ |
| 2 | Qiskit + Aer GPU | 20-30 min | 🔴 CRÍTICA | ⏳ |
| 2 | PyTorch GPU | 15 min | 🟡 ALTA | ⏳ |
| 2 | Deps OmniMind | 20 min | 🟡 ALTA | ⏳ |
| 3 | Docker | 15 min | 🟢 MÉDIA | ⏳ |
| 4 | Validação GPU | 10 min | 🔴 CRÍTICA | ⏳ |
| 5 | Mudanças Código | 30 min | 🟡 ALTA | ⏳ |

**Total Estimado:** 3-4 horas

---

## 🛡️ PARTIÇÕES ESPECIAIS (Ubuntu 22.04)

```
/var (251GB) - Logs, cache, dados variáveis
├── /var/lib/qdrant → QDRANT DATA (recomendado aqui)
├── /var/lib/postgresql → POSTGRESQL DATA
└── /var/lib/redis → REDIS DATA

/home (279GB) - Dados de usuário
├── /home/fahbrain/projects/omnimind → APLICAÇÃO + venv
└── /home/fahbrain/data → DATA EXPERIMENTS

Recomendação:
- Sistema + Python + OmniMind: /home/fahbrain/projects (têm espaço)
- Bancos dados: /var/lib (partição própria)
- Cache/experimentos: /tmp ou /data/cache
```

---

## 🔧 MUDANÇAS NECESSÁRIAS NO CÓDIGO

### 1. Environment Variables
```bash
# .env para sistema
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=omnimind
POSTGRES_USER=omnimind
POSTGRES_PASSWORD=<secure_password>

CUDA_VISIBLE_DEVICES=0
QISKIT_SETTINGS=~/.qiskit/settings.conf

# Para Docker experimentos
DOCKER_QDRANT_URL=http://qdrant-exp:6333
DOCKER_REDIS_URL=redis://redis-exp:6379
```

### 2. Configuração Conexões
```python
# src/config/connections.py - NOVO

import os
from typing import Dict, Any

def get_database_config() -> Dict[str, Any]:
    """Retorna config de BD baseada em ambiente."""
    env = os.getenv("ENVIRONMENT", "production")

    if env == "docker":
        return {
            "qdrant_url": os.getenv("DOCKER_QDRANT_URL", "http://qdrant-exp:6333"),
            "redis_url": os.getenv("DOCKER_REDIS_URL", "redis://redis-exp:6379"),
            # ...
        }
    else:  # production/system
        return {
            "qdrant_url": os.getenv("QDRANT_URL", "http://localhost:6333"),
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            # ...
        }
```

### 3. GPU Initialization
```python
# src/quantum_consciousness/gpu_init.py

import os
os.environ['QISKIT_AER_USE_GPU'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = os.getenv('CUDA_VISIBLE_DEVICES', '0')

from qiskit_aer import AerSimulator

def get_quantum_backend():
    """GPU backend com fallback."""
    try:
        simulator = AerSimulator(
            device='GPU',
            method='statevector',
            precision='single'  # GPU memory efficient
        )
        return simulator
    except Exception as e:
        logger.warning(f"GPU init failed: {e}, using CPU")
        return AerSimulator(device='CPU')
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Após Fase 0
- [ ] venv criado e ativado
- [ ] `python --version` retorna 3.12.8
- [ ] CUDA detectado (`nvidia-smi`)

### Após Fase 1
- [ ] `redis-cli ping` → PONG
- [ ] `psql --version` instalado
- [ ] `qdrant` executável
- [ ] Backup restaurado: `ls /var/lib/qdrant/collections`

### Após Fase 2
- [ ] `python -c "import qiskit_aer; print(qiskit_aer.__version__)"`
- [ ] `python -c "import torch; print(torch.cuda.is_available())"` → True
- [ ] `python -m pytest tests/ --co` (coleta testes)

### Após Fase 3
- [ ] `docker version`
- [ ] `docker run hello-world` funciona

### Após Fase 4
- [ ] `python tests/validate_system.py` passa

### Após Fase 5
- [ ] `pytest tests/ -x` passa
- [ ] Aplicação inicia sem erros

---

## 🚨 POSSÍVEIS PROBLEMAS + SOLUÇÕES

| Problema | Solução |
|----------|---------|
| Qiskit Aer GPU falha | Verificar CUDA_VISIBLE_DEVICES, recompilar Aer |
| PostgreSQL recusa conexão | Criar user `omnimind` e database |
| Qdrant porta 6333 em uso | `sudo lsof -i :6333 && kill <pid>` |
| Redis lento | Aumentar `maxmemory` e política de eviction |
| venv não encontra módulos | Verificar `which python` e `echo $VIRTUAL_ENV` |
| GPU out of memory | Reduzir tamanho batch, usar `precision='single'` |

---

## 📚 REFERÊNCIAS

- **Qiskit Aer GPU:** https://qiskit.org/documentation/aer/howtos/using_gpu.html
- **CUDA 12.2 Setup:** https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
- **Qdrant Production:** https://qdrant.tech/documentation/guides/production/
- **PostgreSQL Tuning:** https://wiki.postgresql.org/wiki/Performance_Optimization

---

## 📝 NOTAS IMPORTANTES

1. **Permissões:** Sempre usar `sudo` para systemd services
2. **Backups:** Dados do HD externo estão seguros em 20251214_070626/
3. **Git:** Código atual em `/home/fahbrain/projects/omnimind` é o base
4. **Python:** Mudar de 3.10.12 para 3.12.8 necessário
5. **Docker:** Usar APENAS para experimentos (não produção)
6. **GPU:** GTX 1650 4GB é limite - otimizar memoria é crítico
7. **Partições:** Usar /var para dados persistentes, não /tmp

---

**Próximo Passo:** Executar FASE 0 - Preparação
**Estimado Total:** 3-4 horas para ambiente completo
**Success Criteria:** Todos os ✅ checklist preenchidos

