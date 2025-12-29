# 📋 REQUIREMENTS FILES - CLEANED & DOCUMENTED
# Status: 2025-12-14 - Auditoria e Limpeza Completa

## ✅ VALID FILES (Use these only)

### 1. requirements_core_quantum.txt
**Purpose:** Quantum + GPU Development (LOCKED VERSIONS)
**Use Case:** Local GPU development, CI/CD GPU testing
**Includes:**
- qiskit==1.2.4 (LOCKED)
- qiskit-aer-gpu==0.15.1 (LOCKED - pré-compilado)
- torch==2.5.1 (CUDA 12.4, LOCKED)
- cuquantum-cu12==25.11.0 (LOCKED)
- custatevec-cu12==1.11.0 (LOCKED)
- cutensor-cu12==2.4.1 (LOCKED)

**Install:**
```bash
pip install -r requirements/requirements_core_quantum.txt
```

**Status:** ✅ LOCKED & TESTED (final_check.py passed)

---

### 2. requirements-core.txt
**Purpose:** Core AI/ML/Web Dependencies (COMPATIBLE)
**Use Case:** General development, testing, web stack
**Includes:**
- FastAPI, Uvicorn (web)
- transformers, sentence-transformers (ML)
- qdrant-client, redis (data stores)
- pydantic, PyYAML (config)
- pytest, black, flake8, mypy (QA)
- numpy, statsmodels (data processing)
- opentelemetry, prometheus (observability)

**Note:** Torch NOT included (comes from requirements_core_quantum.txt)

**Install:**
```bash
pip install -r requirements/requirements-core.txt
```

**Status:** ✅ VALID & COMPATIBLE with locked quantum versions

---

## ⚠️ DEPRECATED FILES (DO NOT USE)

### requirements-quantum.txt
- ❌ Uses open versions (`qiskit>=1.3.0,<2.0.0`)
- ❌ Conflicts with `qiskit==1.2.4`
- ✅ Marked as DEPRECATED
- Action: Ignore completely

### requirements-core-NOVO.txt
- ❌ Old/unused file
- ✅ Marked as DEPRECATED
- Action: Ignore completely

### requirements-gpu.txt
- ⚠️ Outdated but marked DEPRECATED
- ✅ Only keeps `nvidia-ml-py` for GPU monitoring
- Action: Use requirements_core_quantum.txt instead

### requirements-cpu.txt
- ✅ Updated to be compatible
- ⚠️ Uses open torch version (torch>=2.9.0)
- Use ONLY for CPU-only deployments (no quantum/GPU)

### requirements-minimal.txt
- ✅ Updated to match backend Docker
- ⚠️ Uses open torch version (torch>=2.9.0)
- Use ONLY for backend services (no quantum)

---

## 🚀 INSTALLATION GUIDE

### For Local GPU + Quantum Development:
```bash
# Step 1: Clean venv (fresh start)
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate

# Step 2: Install quantum (torch comes here with CUDA 12.4)
pip install -r requirements/requirements_core_quantum.txt

# Step 3: Install core dependencies
pip install -r requirements/requirements-core.txt

# Step 4: Optional - Install development tools
pip install -r requirements/requirements-dev.txt

# Step 5: Verify
python final_check.py  # ✅ Should show all green
```

### For Docker Backend (FastAPI only):
```bash
# Uses requirements-minimal.txt (no quantum/GPU needed)
docker-compose up backend frontend
```

### For CPU-Only Server:
```bash
# Uses requirements-cpu.txt (no GPU)
pip install -r requirements/requirements-cpu.txt
```

---

## 📊 COMPARISON TABLE

| Use Case | Files | torch | qiskit | GPU | Status |
|----------|-------|-------|--------|-----|--------|
| **GPU Development** | core_quantum + core + dev | 2.5.1+cu124 (LOCKED) | 1.2.4 (LOCKED) | ✅ | ✅ VALID |
| **Docker Backend** | minimal | >=2.9.0 (open) | ❌ | ❌ | ✅ VALID |
| **CPU Server** | cpu | >=2.9.0 (open) | ❌ | ❌ | ✅ VALID |
| **Testing CI/CD** | core_quantum + core | 2.5.1+cu124 (LOCKED) | 1.2.4 (LOCKED) | ✅ | ✅ VALID |

---

## 🔒 VERSION LOCK PRINCIPLE

**Locked versions (NEVER CHANGE):**
- qiskit==1.2.4
- qiskit-aer-gpu==0.15.1
- torch==2.5.1 (with cu124)
- sympy==1.13.1
- symengine==0.13.0
- cuquantum-cu12==25.11.0
- custatevec-cu12==1.11.0
- cutensor-cu12==2.4.1

**Open versions (can vary):**
- fastapi>=0.122.0
- transformers>=4.57.0
- pytest>=9.0.0
- etc. (for flexibility)

---

## ✅ CLEANUP COMPLETED

1. ✅ requirements_core_quantum.txt - LOCKED & CLEAN
2. ✅ requirements-core.txt - CLEANED (no GPU duplication)
3. ✅ requirements-dev.txt - NO CHANGES (compatible)
4. ✅ requirements-gpu.txt - Marked DEPRECATED
5. ✅ requirements-quantum.txt - Marked DEPRECATED
6. ✅ requirements-cpu.txt - UPDATED with clear warnings
7. ✅ requirements-minimal.txt - UPDATED for Docker backend
8. ✅ requirements-core-NOVO.txt - Marked DEPRECATED

---

## 🎯 NEXT STEP

Install requirements with:
```bash
source .venv/bin/activate
pip install -r requirements/requirements_core_quantum.txt
pip install -r requirements/requirements-core.txt
python final_check.py
```

**Expected output:** ✅ ALL TESTS PASSED

