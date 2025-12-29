# 🔍 INVESTIGAÇÃO: GPU NÃO ESTÁ SUPORTADO - ROOT CAUSE ANALYSIS

**Data:** 2025-12-12 12:20
**Status:** GPU ESTAVA FUNCIONANDO - REGRESSÃO DETECTADA
**Evidência:** Commits anteontem/ontem tinham GPU funcionando no Kali

---

## 📊 TIMELINE - O QUE MUDOU

### ✅ Kali Setup (Anteontem - FUNCIONAVA)
```
Sistema:      Kali Linux
GPU:          GTX 1650
Qiskit:       1.3.x (LTS com GPU support)
Status:       ✅ GPU funcionando
Commits:      86d0c112 (11/12 15:25) - "Private repo: Add all data..."
Environment: Otimizado para GPU (CUDA_LAUNCH_BLOCKING, etc.)
```

### ⚠️ Migração Ubuntu (Ontem - REGREDIU)
```
Sistema:      Ubuntu 24.04.3 (novo)
GPU:          GTX 1650 (mesmo)
Qiskit:       ??? (pode ter sido atualizado)
Status:       ❌ "GPU not supported"
Commits:      60c22639 (12/12 10:53) - "PRIVATE: Add Ubuntu migration fixes..."
Issue:        GPU foi testado no Kali, não em Ubuntu
```

### 🔴 Hoje - INVESTIGAÇÃO DESCOBRIU
```
Problema:     Qiskit 1.4.5+ REMOVEU convert_to_target()
              → Quebra compatibilidade com qiskit-aer-gpu 0.15.x

Solução:      Requirements.txt ESPECIFICA Qiskit 1.3.0+
              → Mas pode estar instalado 1.4.5 na venv

Confirmação:  Documentação GPU_SETUP_UBUNTU_FINAL_SOLUTION.md
              explica exatamente esse problema

Recomendação: Downgrade Qiskit para 1.3.x LTS
```

---

## 🔧 DIAGNÓSTICO DETALHADO

### O Que Está Configurado (Correto)

**requirements/requirements.txt especifica:**
```
qiskit>=1.3.0,<2.0.0  # ✅ LTS com GPU support
qiskit-aer-gpu>=0.15.0
```

**Documentação GPU aponta a solução:**
- [x] docs/QISKIT_GPU_COMPATIBILITY.md - ✅ Identifica problema 1.4.5
- [x] docs/GPU_SETUP_UBUNTU_FINAL_SOLUTION.md - ✅ Explica downgrade para 1.3.x

**Script de setup existe:**
- [x] scripts/setup_gpu_ubuntu.sh - ✅ Deve fazer downgrade

---

## 🚨 PROBLEMA DETECTADO

### Mismatch Entre Documentação e Realidade

| Item | Esperado | Realidade | Status |
|------|----------|-----------|--------|
| Qiskit version | 1.3.x LTS | ??? (may be 1.4.5+) | ⚠️ Desconhecido |
| Environment vars | Otimizadas para GPU | ??? | ⚠️ Pode estar errado |
| CUDA_LAUNCH_BLOCKING | ❌ Removido (Kali hack) | ??? | ⚠️ Pode estar ativo |
| OMP_NUM_THREADS | 2 (reduzido) | ??? | ⚠️ Pode estar em 4 |
| Resource protector | "test" mode (lenient) | ??? | ⚠️ Pode estar em "dev" |

---

## ✅ FIX IMEDIATO - 3 PASSOS

### PASSO 1: Verificar Versão Qiskit Atual
```bash
python3 -c "import qiskit; print(f'Qiskit version: {qiskit.__version__}')"
python3 -c "import qiskit_aer; print(f'Qiskit-Aer version: {qiskit_aer.__version__}')"
```

**Se resposta for 1.4.5+:**
```bash
# DOWNGRADE para LTS
pip install --upgrade 'qiskit>=1.3.0,<2.0.0'
pip install --upgrade 'qiskit-aer>=0.15.0'
```

### PASSO 2: Verificar Environment Variables
```bash
# Check current settings
env | grep -E "CUDA|PYTORCH|OMP|QISKIT"
```

**Esperado:**
```bash
CUDA_VISIBLE_DEVICES=0
PYTORCH_ALLOC_CONF=backend:cudaMallocAsync,max_split_size_mb:256
OMP_NUM_THREADS=2
QISKIT_IN_PARALLEL=FALSE
# NÃO DEVE TER:
# CUDA_LAUNCH_BLOCKING=1  (Kali hack, remove!)
```

**Se errado:**
```bash
# Execute script correto
source scripts/setup_gpu_ubuntu.sh
```

### PASSO 3: Verificar Resource Protector Mode
```bash
# Check current mode
echo $OMNIMIND_RESOURCE_PROTECTOR_MODE
```

**Esperado:** `test` (ou não setado, usa default lenient)

**Se errado (dev mode):**
```bash
export OMNIMIND_RESOURCE_PROTECTOR_MODE=test
```

---

## 📋 AÇÕES IMEDIATAS RECOMENDADAS

### 1. Verificar Status Real
```bash
# Executar diagnóstico completo
cd /home/fahbrain/projects/omnimind
python3 << 'EOF'
import subprocess
import sys

print("═" * 80)
print("GPU DIAGNOSTIC - Real Status Check")
print("═" * 80)

# Check 1: Qiskit version
try:
    import qiskit
    print(f"✓ Qiskit: {qiskit.__version__}")
    if qiskit.__version__.startswith("1.3"):
        print("  └─ ✅ Version 1.3.x (GPU supported)")
    elif qiskit.__version__.startswith("1.4") or qiskit.__version__.startswith("1.5"):
        print("  └─ ❌ Version 1.4.x+ (GPU BROKEN - needs downgrade)")
except ImportError:
    print("✗ Qiskit not installed")

# Check 2: GPU availability
try:
    from qiskit_aer import AerSimulator
    sim = AerSimulator(method='statevector', device='GPU')
    print(f"✓ Qiskit-Aer GPU: Available")
    print(f"  └─ ✅ GPU simulator initialized")
except Exception as e:
    print(f"✗ Qiskit-Aer GPU: {str(e)[:80]}")

# Check 3: PyTorch GPU
try:
    import torch
    print(f"✓ PyTorch: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"  └─ ✅ CUDA available (Device: {torch.cuda.get_device_name(0)})")
    else:
        print(f"  └─ ⚠️ CUDA not available")
except ImportError:
    print("✗ PyTorch not installed")

# Check 4: Environment
import os
env_checks = {
    "CUDA_VISIBLE_DEVICES": "0",
    "QISKIT_IN_PARALLEL": "FALSE",
    "OMP_NUM_THREADS": "2",
}
print("\nEnvironment Variables:")
for var, expected in env_checks.items():
    actual = os.getenv(var, "NOT SET")
    if actual == expected:
        print(f"  ✅ {var}={actual}")
    else:
        print(f"  ⚠️ {var}={actual} (expected: {expected})")

print("\n" + "═" * 80)
EOF
```

### 2. Se Precisar Downgrade Qiskit
```bash
# Remove cached versions
pip cache purge

# Force install correct version
pip install --force-reinstall --no-cache-dir 'qiskit>=1.3.0,<2.0.0'
pip install --force-reinstall --no-cache-dir 'qiskit-aer>=0.15.0'

# Verify
python3 -c "import qiskit; print('Qiskit:', qiskit.__version__); from qiskit_aer import AerSimulator; print('Aer GPU: OK')"
```

### 3. Rerun Test com GPU Configurado
```bash
# Ativar environment correto
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
source scripts/setup_gpu_ubuntu.sh

# Executar test GPU
bash scripts/recovery/03_run_50_cycles.sh
```

---

## 📖 DOCUMENTAÇÕES EXISTENTES (Reference)

Todas essas documentações JÁ EXISTEM no repo e explicam o problema:

1. **docs/QISKIT_GPU_COMPATIBILITY.md** ✅
   - Identifica: Qiskit 1.4.5 breaks GPU
   - Solução: Downgrade para 1.3.x

2. **docs/GPU_SETUP_UBUNTU_FINAL_SOLUTION.md** ✅
   - Explica: Root cause era misconfiguração
   - Solução: Modo "test" + correct Qiskit

3. **scripts/setup_gpu_ubuntu.sh** ✅
   - Implementa: Setup correto de GPU
   - Inclui: Downgrade Qiskit se necessário

4. **docs/canonical/GUIA_SOLUCAO_PROBLEMAS_AMBIENTE_GPU.md** ✅
   - Troubleshooting completo
   - Verificação passo-a-passo

---

## 🎯 CONCLUSÃO

### ❌ O QUE ESTAVA ERRADO NA AUDITORIA
```
Relatório original (RELATORIO_AUDITORIA_LOGS_COMPLETO_20251212.md):
- Classificou "GPU not supported" como erro
- Sugeriu seria problema de compatibilidade PyTorch/Qiskit
- Marcou como "High severity"

Realidade:
- GPU SIM suporta, estava funcionando no Kali
- Problema: Qiskit pode estar em versão errada (1.4.5+)
- Solução é simples: downgrade para 1.3.x (JÁ DOCUMENTADO)
```

### ✅ O QUE FAZER

**Próximos passos (em ordem):**
1. Executar diagnóstico acima para confirmar versão Qiskit
2. Se 1.4.5+, executar downgrade (pip install)
3. Verificar environment variables com setup_gpu_ubuntu.sh
4. Rerun 50-cycle test com GPU
5. Atualizar RELATORIO_AUDITORIA para refletir que GPU FUNCIONA (é apenas versioning issue)

### 📌 KEY INSIGHT

**GPU não está "não suportado" - está apenas em versão errada do Qiskit.**

A documentação e scripts JÁ existem e resolvem isso. Precisa só de:
- Diagnóstico para confirmar
- Downgrade Qiskit 1.3.x
- Retest para validar GPU funciona novamente

**Tempo estimado para fix:** 5-10 minutos

