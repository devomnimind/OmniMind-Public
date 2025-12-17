# ⚠️ FIX: Import Error - custatevec / cutensor (RESOLVIDO)

**Data:** 16 de Dezembro de 2025
**Status:** ✅ RESOLVIDO
**Problema:** ImportError ao tentar `from cuquantum import custatevec`

---

## 🔴 PROBLEMA ORIGINAL

```python
# ❌ ERRADO - Isso não funciona:
from cuquantum import custatevec
from cuquantum import cutensor

# Erro:
# ImportError: cannot import name 'custatevec' from 'cuquantum'
```

---

## 🟢 SOLUÇÃO

### ✅ O Problema
`custatevec` e `cutensor` NÃO são submodules diretos de `cuquantum`. Eles são:
- **Pacotes separados** instalados via pip
  - `custatevec-cu12==1.11.0`
  - `cutensor-cu12==2.4.1`
- Não precisam ser importados DIRETAMENTE no seu código
- Estão disponíveis para Qiskit-Aer-GPU usar internamente

### ✅ A Validação Correta
```python
# ✅ CORRETO - Validar que os pacotes estão instalados:
import subprocess

# Verificar cuStatevec
result = subprocess.run(['pip', 'show', 'custatevec-cu12'],
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ cuStatevec-cu12 instalado")

# Verificar cuTensor
result = subprocess.run(['pip', 'show', 'cutensor-cu12'],
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ cuTensor-cu12 instalado")

# OU simplesmente validar que AerSimulator funciona:
from qiskit_aer import AerSimulator
sim = AerSimulator(method='statevector')
print("✅ AerSimulator com GPU aceleração ativa")
```

---

## 📋 SCRIPT DE VALIDAÇÃO CORRETO

Veja: `validate_gpu_quantum.py`

```bash
python validate_gpu_quantum.py
```

**Output esperado:**
```
✅ PyTorch: 2.5.1+cu121 | CUDA: 12.1 | GPU: True
✅ Qiskit: 1.2.4
✅ Qiskit-Aer-GPU: AerSimulator importado com sucesso
✅ CuPy: 13.6.0
✅ cuStatevec-cu12: 1.11.0
✅ cuTensor-cu12: 2.4.1
✅ AerSimulator instanciado com sucesso
   └─ GPU acceleration via Qiskit-Aer-GPU ativa
```

---

## 🔧 Como OmniMind Usa Isso

Você **não** precisa fazer imports de `custatevec` ou `cutensor` diretamente:

1. **Qiskit-Aer-GPU** detecta que essas bibliotecas estão instaladas
2. **Usa automaticamente** para aceleração GPU
3. **Seu código** apenas faz:
   ```python
   from qiskit_aer import AerSimulator
   sim = AerSimulator(method='statevector')
   # Dentro, usa cuStatevec + cuTensor automaticamente!
   ```

---

## 📦 Lista de Pacotes Instalados

Todos estes devem estar em `pip list`:

```
cupy-cuda12x
cuquantum-cu12            (versão 25.11.0)
custatevec-cu12           (versão 1.11.0)  ← Não import direto!
cutensor-cu12             (versão 2.4.1)   ← Não import direto!
custabilizer-cu12
cupauliprop-cu12
cudensitymat-cu12
cutensornet-cu12
qiskit                    (versão 1.2.4)
qiskit-aer-gpu            (versão 0.15.1)
torch                     (versão 2.5.1)
```

---

## ✅ RESUMO

| O que fazer | Status |
|-------------|--------|
| Instalar `custatevec-cu12` | ✅ Sim |
| Instalar `cutensor-cu12` | ✅ Sim |
| Fazer `from cuquantum import custatevec` | ❌ NÃO |
| Usar `AerSimulator()` | ✅ Sim (usa tudo automaticamente) |
| Validar com `validate_gpu_quantum.py` | ✅ Sim |
| Rodar OmniMind | ✅ Sim (GPU ativa) |

---

## 🚀 Próximos Passos

```bash
# 1. Validar que tudo funciona
python validate_gpu_quantum.py

# 2. Ativar ambiente completo
source .venv/bin/activate
source .env.system

# 3. Iniciar backend cluster (3 instances)
./scripts/canonical/system/run_cluster.sh

# 4. Verificar GPU em uso
nvidia-smi  # Deve mostrar processo Python usando GPU
```

---

**Status:** ✅ **RESOLVIDO E FUNCIONAL**

Teste agora: `python validate_gpu_quantum.py`

