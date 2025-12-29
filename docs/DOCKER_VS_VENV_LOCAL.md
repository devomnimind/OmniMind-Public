# 🐳 Docker vs venv Local - OmniMind GPU Setup

**Date:** 2025-12-14
**Status:** ✅ Clarification - Docker é para PRODUÇÃO, venv é para DESENVOLVIMENTO

---

## 📊 Comparação: Docker vs venv Local

| Aspecto | Docker | venv Local |
|--------|--------|-----------|
| **Uso** | Production backend | Development + GPU testing |
| **Versões** | requirements-minimal.txt | requirements_core_quantum.txt |
| **GPU Support** | Opcional (not configured) | ✅ CUDA 12.4 + qiskit + torch |
| **Qiskit** | ❌ Não tem | ✅ 1.2.4 (locked) |
| **Aer-GPU** | ❌ Não tem | ✅ 0.15.1 (locked) |
| **torch** | ✅ 2.9.0+ (aberto) | ✅ 2.5.1+cu124 (locked) |
| **CUDA** | Não necessário | ✅ 12.4 (LOCKED) |

---

## 🐳 Docker (Atual - Production)

### Uso:
```bash
cd deploy/
docker-compose up backend frontend qdrant redis
```

### Dockerfile:
- `web/backend/Dockerfile` - FastAPI backend
- `web/frontend/Dockerfile` - React frontend
- `deploy/docker-compose.yml` - Services (qdrant, redis)

### Responsabilidade:
- ✅ Servir API (FastAPI)
- ✅ Servir Frontend (React/Vite)
- ✅ Database (Qdrant vector)
- ✅ Cache (Redis)
- ❌ NÃO testa Quantum/GPU

### Requisitos:
- `requirements-minimal.txt` - Core deps (FastAPI, uvicorn, transformers)
- Sem CUDA (rodaria no CPU se necessário)
- Sem qiskit/aer-gpu

---

## 💻 venv Local (Atual - Development)

### Uso:
```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
python final_check.py  # ✅ Valida GPU + Quantum
pytest tests/ -v       # ✅ Roda testes com GPU
```

### Configuração:
- Python 3.12.3
- Ativado via `.vscode/settings.json` (force venv)
- CUDA 12.4 environment variables

### Requisitos:
- `requirements/requirements_core_quantum.txt` - Qiskit + aer-gpu (LOCKED)
- `requirements/requirements-core.txt` - Core deps

### Responsabilidade:
- ✅ Testar Quantum (qiskit 1.2.4 + aer-gpu 0.15.1)
- ✅ Testar GPU (CUDA 12.4)
- ✅ Desenvolver módulos quantum
- ✅ Rodar unit tests com GPU

---

## 📦 Novo Dockerfile.development-gpu (CRIADO)

### Quando usar:
```bash
# Para criar imagem Docker com GPU + Quantum support
docker build -f deploy/Dockerfile.development-gpu -t omnimind:dev-gpu .

# Rodar container com GPU
docker run --gpus all -it omnimind:dev-gpu bash

# Dentro do container:
$ python final_check.py  # ✅ All tests pass
$ pytest tests/ -v       # ✅ Run tests with GPU
```

### O que contém:
- ✅ CUDA 12.4 (nvidia/cuda base image)
- ✅ Python 3.12
- ✅ qiskit 1.2.4 (locked)
- ✅ aer-gpu 0.15.1 (locked)
- ✅ torch 2.5.1+cu124 (locked)
- ✅ Todas as cuQuantum cu12 libs

### Casos de uso:
1. **CI/CD GPU Testing** - Testar quantum em GitHub Actions
2. **Reproducible Environment** - Garantir mesma versão em outro PC/servidor
3. **Production Quantum** - Quando quantum for production-ready
4. **Cloud Deployment** - AWS/GCP com GPU instances

---

## 🔒 Versões LOCKED (NUNCA MUDAR)

### requirements_core_quantum.txt
```
qiskit==1.2.4              # ✅ Tested working
qiskit-aer-gpu==0.15.1     # ✅ Pre-compiled GPU binary
torch==2.5.1+cu124         # ✅ CUDA 12.4 compatible
cuquantum-cu12==25.11.0    # ✅ State vector acceleration
```

### Onde são usadas:
- **venv Local**: `pip install -r requirements/requirements_core_quantum.txt`
- **Docker Dev**: `COPY requirements/requirements_core_quantum.txt` em Dockerfile.development-gpu
- **CI/CD**: GitHub Actions com GPU runner

---

## ✅ Checklist: Qual usar?

### Usar **venv Local** se:
- [ ] Desenvolvendo módulos quantum
- [ ] Testando qiskit localmente
- [ ] Precisa GPU rápida (GTX 1650)
- [ ] VS Code com debug
- [ ] Iterações rápidas (sem build Docker)

### Usar **Docker Backend** se:
- [ ] Servindo API production
- [ ] Não precisa quantum (apenas ML)
- [ ] Precisa reproducibilidade entre ambientes
- [ ] Deploy em servidor/cloud

### Usar **Docker Dev (Dockerfile.development-gpu)** se:
- [ ] Precisa quantum em CI/CD
- [ ] Testando em servidor com GPU
- [ ] Reproducibilidade de testes
- [ ] Deploy quantum em cloud (futuro)

---

## 🚀 Próximos Passos

### 1. Restaurar venv com versões LOCKED
```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
pip install --force-reinstall --no-cache-dir \
    -r requirements/requirements_core_quantum.txt \
    -r requirements/requirements-core.txt
python final_check.py  # ✅ Verify all green
```

### 2. Testar Docker Dev (Opcional)
```bash
docker build -f deploy/Dockerfile.development-gpu -t omnimind:dev-gpu .
docker run --gpus all -it omnimind:dev-gpu python final_check.py
```

### 3. Documentar no .github/workflows (CI/CD)
- Usar `Dockerfile.development-gpu` para GPU tests
- Usar `Dockerfile.tests` para CPU tests
- Rodar em paralelo (speed up CI)

---

## 📝 Status Final

✅ **Docker para Production (backend/frontend):** Configurado
✅ **venv Local para Desenvolvimento:** Configurado + LOCKED versions
✅ **Dockerfile.development-gpu novo:** Criado para CI/CD quantum testing
⏳ **CI/CD GPU Testing:** Pronto para implementar (opcional)

