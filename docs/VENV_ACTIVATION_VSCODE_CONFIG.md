# ✅ VS Code venv Activation Configuration - CUDA 12

**Date:** 2025-12-14
**Status:** ✅ COMPLETE - New clean venv forced in VS Code
**Last Updated:** After sanitization of GPU environment
**Configuration:** Locked to prevent cu11/cu12 conflicts

---

## 📋 Overview

This document explains the VS Code configuration that **forces the new clean venv** (created 2025-12-14) with **CUDA 12.4 ONLY** (zero CUDA 11).

### Key Configuration Changes (`.vscode/settings.json`)

**1. Python Interpreter - Forced venv**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.pythonPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.terminal.activateEnvInCurrentTerminal": true,
  "python.venvPath": "${workspaceFolder}/.venv"
}
```

**Impact:** All Python execution in VS Code uses `.venv` (NOT system Python)

---

## 🔧 Terminal Environment (CRITICAL)

### New Configuration: `terminal.integrated.env.linux`

```json
"terminal.integrated.env.linux": {
  // ✅ PYTHON ENVIRONMENT - NOVO VENV LIMPO
  "VIRTUAL_ENV": "${workspaceFolder}/.venv",
  "PYTHONPATH": "${workspaceFolder}/src",
  "PATH": "${workspaceFolder}/.venv/bin:/usr/local/cuda-12/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",

  // ✅ CUDA 12.4 ONLY (ZERO CUDA 11)
  "CUDA_HOME": "/usr/local/cuda-12",
  "CUDA_VISIBLE_DEVICES": "0",
  "LD_LIBRARY_PATH": "/usr/local/cuda-12/lib64:/usr/local/cuda-12/extras/CUPTI/lib64:/usr/lib/x86_64-linux-gnu",

  // ✅ GPU OPTIMIZATION
  "TORCH_CUDA_ARCH_LIST": "7.5",
  "CUDA_MODULE_LOADING": "LAZY"
}
```

### Path Priority (Exact Order)
1. **`.venv/bin`** - New clean venv (cu12 only)
2. **`/usr/local/cuda-12/bin`** - CUDA 12 tools
3. **System paths** - Fallback

**Critical:** `.venv/bin` comes FIRST to ensure clean environment

---

## ✅ Verification Steps

### Step 1: Close and Reopen VS Code

```bash
# Close VS Code completely
pkill code

# Reopen VS Code
code /home/fahbrain/projects/omnimind
```

### Step 2: Check Terminal Environment

Open VS Code terminal (Ctrl+`) and run:

```bash
# Should show new clean venv
echo $VIRTUAL_ENV
# Expected: /home/fahbrain/projects/omnimind/.venv

# Should show CUDA 12
echo $CUDA_HOME
# Expected: /usr/local/cuda-12

# Should show Python from venv
which python
# Expected: /home/fahbrain/projects/omnimind/.venv/bin/python

# Verify no CUDA 11
python -c "import torch; print(torch.__version__)"
# Expected: 2.5.1+cu124 (cu12, NOT cu11)
```

### Step 3: Run final_check.py

```bash
python final_check.py
```

**Expected Output:**
```
✅ Python 3.12.3
✅ Qiskit 1.2.4
✅ Qiskit-Aer 0.15.1
✅ Torch 2.5.1+cu124
✅ GPU (Torch): ✅ SIM
✅ GPU (Qiskit): ✅ OK
✅ Teste Bell State: {'11': 524, '00': 500} ✅
```

### Step 4: Verify qiskit GPU Backend

```bash
python -c "from qiskit_aer import AerSimulator; sim = AerSimulator(method='statevector', device='GPU'); print(f'Backend: {sim.name}'); print(f'Devices: {sim.available_devices()}')"
```

**Expected Output:**
```
Backend: aer_simulator_statevector_gpu
Devices: ['GPU']
```

---

## 🔒 Version Lock (IMMUTABLE)

These versions are **LOCKED in `.vscode/settings.json` documentation**:

| Package | Version | Status | Reason |
|---------|---------|--------|--------|
| qiskit | 1.2.4 | 🔴 LOCKED | GPU operations require exact version |
| qiskit-aer-gpu | 0.15.1 | 🔴 LOCKED | Pré-compilado with GPU support |
| torch | 2.5.1+cu124 | 🔴 LOCKED | CUDA 12.4 compatibility |
| cuquantum-cu12 | 25.11.0 | 🔴 LOCKED | State vector acceleration |

**⚠️ CRITICAL:** Any AI attempting to change these versions will **BREAK GPU acceleration**. See `copilot-instructions.md` for immutable versions policy.

---

## 🚀 Expected Behavior After Configuration

### Terminal Activation (Automatic)

When you open a new terminal in VS Code:
1. ✅ VIRTUAL_ENV is set to `.venv`
2. ✅ `python` command uses venv binary
3. ✅ CUDA 12 paths are in LD_LIBRARY_PATH
4. ✅ GPU is accessible (CUDA_VISIBLE_DEVICES=0)

### No Manual Activation Needed

```bash
# Old (NOT needed anymore):
source .venv/bin/activate

# New (automatic from VS Code terminal):
$ python --version
Python 3.12.3

$ python -c "import torch; print(torch.cuda.is_available())"
True
```

---

## 📊 Configuration Impact

| Setting | Before | After | Impact |
|---------|--------|-------|--------|
| Python Interpreter | System Python 3.x | .venv/bin/python 3.12.3 | Clean environment |
| VIRTUAL_ENV | Not set | /path/to/.venv | Explicit venv |
| CUDA Version | Mixed cu11+cu12 | cu12 ONLY | No conflicts |
| GPU Backend | Fallback/Broken | aer_simulator_statevector_gpu | Qiskit GPU active |
| PATH Priority | System first | .venv first | Clean isolation |

---

## 🐛 Troubleshooting

### Problem: `CUDA not available` in Terminal

**Symptom:** `python final_check.py` shows GPU not available

**Solution:**
1. Close VS Code completely
2. Delete `.vscode/` settings cache: `rm -rf ~/.config/Code/Cache`
3. Reopen VS Code
4. Verify CUDA_HOME in terminal: `echo $CUDA_HOME`

### Problem: Old venv Still Used

**Symptom:** `which python` shows system path or old venv

**Solution:**
```bash
# Force new venv
rm -rf .venv
python3.12 -m venv .venv
pip install -r requirements/requirements_core_quantum.txt
# Then reload VS Code
```

### Problem: Import Errors in Terminal

**Symptom:** `ModuleNotFoundError: No module named 'qiskit'`

**Solution:**
1. Verify PYTHONPATH: `echo $PYTHONPATH`
2. Should include `${workspaceFolder}/src`
3. If not, close/reopen VS Code

---

## ✅ Final Verification Checklist

- [ ] VS Code closed and reopened
- [ ] Terminal shows `$VIRTUAL_ENV = /path/to/.venv`
- [ ] `which python` shows `.venv/bin/python`
- [ ] `echo $CUDA_HOME` shows `/usr/local/cuda-12`
- [ ] `python final_check.py` shows ✅ ALL PASSED
- [ ] Qiskit GPU backend active
- [ ] Bell State test passed on GPU
- [ ] No CUDA 11 packages in environment

---

## 📝 Notes

**Configuration Date:** 2025-12-14
**Configured By:** GitHub Copilot + Fabrício da Silva
**Status:** ✅ LOCKED - Do not modify without explicit user approval
**Last Verified:** After final_check.py execution - ✅ ALL TESTS PASSED

**Security Note:** This configuration **forces isolation** from system Python and old venv, preventing accidental mixing of CUDA versions.

