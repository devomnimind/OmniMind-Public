# Especificação de Ambiente OmniMind (Phase 12)

**Última Atualização:** 2025-11-19
**Status:** Phase 12 Multi-Modal Intelligence Complete & Validado
**Documento:** Guia abrangente de requisitos e verificação de ambiente

---

## 🖥️ Requisitos de Hardware

### Configuração Mínima (Testada)
```
CPU:        Intel i5 10ª geração (4 núcleos/8 threads, 2.5GHz base)
GPU:        NVIDIA GeForce GTX 1650 (4GB VRAM, Compute Capability 7.5)
RAM:        24GB DDR4 (18.5GB tipicamente disponíveis para OmniMind)
Armazenamento: 256GB+ SSD (20GB para projeto + dependências, 150GB para modelos/dados)
SO:         Linux (Kali Linux 6.16.8+kali-amd64 validado)
```

### Baseline de Performance de Hardware (Phase 12 Validado - Nov 19, 2025)

| Componente | Métrica | Valor | Status |
|------------|---------|-------|--------|
| CPU | Throughput (5000x5000 matmul) | 253.21 GFLOPS | ✅ Verificado |
| GPU | Throughput (5000x5000 matmul) | 1149.91 GFLOPS | ✅ Verificado |
| GPU | Fator de Aceleração | 4.5x vs CPU | ✅ Esperado |
| Memória | Largura de Banda | 12.67 GB/s | ✅ Verificado |
| GPU | VRAM Disponível | 3.81GB total | ✅ Confirmado |

---

## 🔧 Stack de Software do Sistema

### Sistema Operacional
```
Kernel:     6.16.8+kali-amd64 (Kali Linux)
Pacotes:   Build essentials, gcc/g++, make, git
Driver NVIDIA: 550.163.01+ (necessário para suporte CUDA 12.4)
```

### Verificação
```bash
# Verificar versão do kernel
uname -r

# Verificar driver NVIDIA
nvidia-smi | head -5

# Output esperado:
# NVIDIA Driver Version: 550.163.01  CUDA Version: 12.4
```

### CUDA Toolkit & Runtime
```
System CUDA:    12.4 (system installation)
CUDA Runtime:   12.4.127 (included in PyTorch distribution)
cuDNN:          8.9.7.29 (system) + 9.1.0.70 (PyTorch bundled)
CUDA Compute Capability: 7.5 (for GTX 1650)
```

**Verification:**
```bash
# Check system CUDA
nvcc --version

# Expected: CUDA 12.4.x
# Check cuDNN (system)
ldconfig -p | grep cudnn

# Expected: libcudnn.so.8
```

---

## 🐍 Python Environment

### Python Version (CRITICAL)
```
Primary:    3.12.8 (via pyenv - MANDATORY for OmniMind)
Alternatives: 3.11.x (acceptable), 3.10.x (acceptable)
NOT Supported: 3.13+ (PyTorch has NO official wheel support)
```

**Why Python 3.12.8?**
- PyTorch 2.6.0+cu124 has official wheels only for Python ≤ 3.12
- Python 3.13 causes version resolver conflicts leading to incompatible CUDA library versions
- OmniMind is locked to 3.12.8 via `.python-version` file

### Virtual Environment
```
Location:   /home/fahbrain/projects/omnimind/.venv/
Python:     3.12.8 (inherited from project .python-version)
Package Manager: pip (28.4.0+)
Dependencies: 100+ packages in requirements.txt
```

**Setup & Verification:**
```bash
# 1. Install Python 3.12.8 via pyenv (if not available)
pyenv install 3.12.8
pyenv versions  # Should list 3.12.8

# 2. Create project venv with correct Python
cd /home/fahbrain/projects/omnimind
pyenv local 3.12.8
python -m venv .venv
source .venv/bin/activate

# 3. Verify Python
python --version  # MUST output: Python 3.12.8
which python

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify environment
echo $VIRTUAL_ENV  # Should show /home/fahbrain/projects/omnimind/.venv
```

---

## 📦 PyTorch GPU Stack (Phase 7 - VALIDATED)

### PyTorch Components
```
torch:              2.6.0+cu124      (CUDA 12.4 compiled wheels from official NVIDIA index)
torchvision:        0.21.0+cu124     (Must match torch version exactly)
torchaudio:         2.6.0+cu124      (Must match torch version exactly)
CUDA Toolkit:       12.4.127         (Bundled with PyTorch distribution)
cuDNN:              9.1.0.70         (Bundled with PyTorch distribution)
```

**Why these exact versions?**
- `2.6.0+cu124` means PyTorch compiled for CUDA 12.4
- Must be installed from `https://download.pytorch.org/whl/cu124` (official NVIDIA index)
- System driver (550.xx) supports CUDA 12.4 via NVIDIA's cudalib translation layer
- Python 3.12.8 required (3.13+ breaks dependency resolver)

### Installation
```bash
# Activate venv FIRST
source .venv/bin/activate

# Install from official NVIDIA CUDA 12.4 index
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Expected output (final lines):
# Successfully installed torch-2.6.0+cu124 torchvision-0.21.0+cu124 torchaudio-2.6.0+cu124
# (and NVIDIA CUDA 12.4.127 runtime libraries)
```

### Verification
```bash
# Check PyTorch version
python -c "import torch; print(torch.__version__)"
# Expected: 2.6.0+cu124

# Verify CUDA is available
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
# Expected:
# CUDA: True
# GPU: NVIDIA GeForce GTX 1650

# Check CUDA version in PyTorch
python -c "import torch; print(torch.cuda.get_arch_list())"
# Expected: includes sm_75 (for GTX 1650)

# Benchmark GPU
python test_pytorch_gpu.py
# Expected: GPU Throughput ≥ 1000 GFLOPS
```

---

## 🔌 GPU Module Loading (Critical for Post-Suspend)

### nvidia_uvm Kernel Module

**What is nvidia_uvm?**
- Kernel module that manages GPU virtual memory
- Typically corrupted after system suspend/hibernate on Linux
- When corrupted: `torch.cuda.is_available()` returns False even if GPU is visible in nvidia-smi

**Recovery Procedure (FASTEST FIX):**
```bash
# 1. Kill any processes holding the module
sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true
sleep 1

# 2. Unload and reload the module
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sleep 1
sudo modprobe nvidia_uvm

# 3. Verify module is loaded
lsmod | grep nvidia_uvm
# Expected output: nvidia_uvm line present

# 4. Test CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
# Expected: True (usually returns to normal after reload)
```

**When to execute this:**
- After system suspend/hibernate
- When `torch.cuda.is_available()` returns False but `nvidia-smi` shows GPU
- When CUDA operations fail with "CUDA unknown error"

**Note:** This is NOT a permanent fix and might need to be run after future suspend cycles. For permanent solution, disable automatic suspend in system power settings.

---

## 🧪 Verification Checklist

### Pre-Development Verification (Run Once Per Session)

```bash
#!/bin/bash
# verify_omnimind_env.sh - Complete environment verification

echo "=== OmniMind Environment Verification ==="

# 1. Python version
echo "1. Checking Python version..."
python --version
PYTHON_OK=$(python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12, 0) and sys.version_info < (3, 13, 0) else 1)" && echo "PASS" || echo "FAIL")
echo "   Python 3.12.x: $PYTHON_OK"

# 2. Virtual environment
echo "2. Checking virtual environment..."
echo "   VIRTUAL_ENV: $VIRTUAL_ENV"
[[ ! -z "$VIRTUAL_ENV" ]] && echo "   Status: ACTIVATED" || echo "   Status: NOT ACTIVATED - Run: source .venv/bin/activate"

# 3. NVIDIA driver
echo "3. Checking NVIDIA driver..."
nvidia-smi --query-gpu=driver_version --format=csv,noheader || echo "FAIL: nvidia-smi not found"

# 4. CUDA availability
echo "4. Checking CUDA in PyTorch..."
CUDA_OK=$(python -c "import torch; print('PASS' if torch.cuda.is_available() else 'FAIL')" 2>/dev/null || echo "ERROR")
echo "   CUDA Available: $CUDA_OK"

# 5. PyTorch version
echo "5. Checking PyTorch version..."
python -c "import torch; print(f'   PyTorch: {torch.__version__}')"

# 6. GPU detection
echo "6. Checking GPU detection..."
GPU_NAME=$(python -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null || echo "NOT DETECTED")
echo "   GPU: $GPU_NAME"

# 7. GPU memory
echo "7. Checking GPU memory..."
GPU_MEM=$(python -c "import torch; print(f'{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')" 2>/dev/null || echo "NOT DETECTED")
echo "   Total VRAM: $GPU_MEM"

# 8. Audit tests
echo "8. Running audit tests (14 tests expected to pass)..."
pytest tests/test_audit.py -q 2>/dev/null || echo "FAIL: pytest failed or test_audit.py missing"

# 9. GPU benchmark
echo "9. Running GPU benchmark (1000+ GFLOPS expected)..."
python PHASE7_COMPLETE_BENCHMARK_AUDIT.py 2>/dev/null | grep -E "GPU Throughput|CUDA Status" || echo "FAIL: Benchmark script not found"

echo ""
echo "=== Verification Complete ==="
```

**Run verification:**
```bash
bash verify_omnimind_env.sh
```

### Expected Output
```
=== OmniMind Environment Verification ===
1. Checking Python version...
   Python 3.12.x: PASS
2. Checking virtual environment...
   VIRTUAL_ENV: /home/fahbrain/projects/omnimind/.venv
   Status: ACTIVATED
3. Checking NVIDIA driver...
   550.163.01
4. Checking CUDA in PyTorch...
   CUDA Available: PASS
5. Checking PyTorch version...
   PyTorch: 2.6.0+cu124
6. Checking GPU detection...
   GPU: NVIDIA GeForce GTX 1650
7. Checking GPU memory...
   Total VRAM: 3.81 GB
8. Running audit tests (14 tests expected to pass)...
   14 passed in 0.43s
9. Running GPU benchmark (1000+ GFLOPS expected)...
   CUDA Status: ✅ ENABLED
   GPU Throughput: 1149.91 GFLOPS

=== Verification Complete ===
```

---

## 🚨 Troubleshooting Guide

### Problem: `CUDA unknown error` on first run

**Diagnosis:**
```bash
# Run this to see detailed error
python -c "import torch; print(torch.cuda.current_device())"
```

**Solutions (in order):**
1. **Reload nvidia_uvm (most common fix)**
   ```bash
   sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true
   sleep 1
   sudo modprobe -r nvidia_uvm && sleep 1 && sudo modprobe nvidia_uvm
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Verify system CUDA installation**
   ```bash
   nvcc --version  # Should show 12.4.x
   ldconfig -p | grep cudnn  # Should find libcudnn.so.8
   ```

3. **Reinstall PyTorch with correct index**
   ```bash
   pip uninstall torch torchvision torchaudio -y
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
   ```

### Problem: `torch.cuda.is_available()` returns False after suspend

**Cause:** nvidia_uvm kernel module is corrupted  
**Solution:** See "GPU Module Loading" section above - run the reload procedure

### Problem: Python version mismatch (e.g., Python 3.13 detected)

**Diagnosis:**
```bash
python --version
```

**Solution:**
```bash
# Delete old venv and create new one with correct Python
rm -rf .venv
pyenv local 3.12.8
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Problem: PyTorch "No module named torch"

**Cause:** Virtual environment not activated or dependencies not installed  
**Solution:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
python -c "import torch; print(torch.__version__)"
```

---

## 📚 Related Documentation

- **Installation & Setup:** See `README.md` (Installation & Startup section)
- **GPU Development Guidelines:** See `CURSOR_RULES.md` (GPU Development Guidelines section)
- **GPU/CUDA Setup Details:** See `.github/copilot-instructions.md` (GPU/CUDA SETUP REQUIREMENTS section)
- **Phase 7 Repair Details:** See `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md` (500+ lines technical documentation)
- **Repair Summary:** See `GPU_CUDA_REPAIR_AUDIT_COMPLETE.md` (executive summary and sign-off)

---

## ✅ Maintenance Schedule

### Before Each Development Session
- [ ] Run `verify_omnimind_env.sh` to check all components
- [ ] If CUDA error appears, run nvidia_uvm reload procedure
- [ ] Verify benchmark script passes: `python PHASE7_COMPLETE_BENCHMARK_AUDIT.py`

### After System Updates
- [ ] Verify NVIDIA driver still version 550.xx+
- [ ] Re-run verification checklist
- [ ] If PyTorch version changed, reinstall from correct index

### After System Suspend/Hibernate
- [ ] Reload nvidia_uvm module (automatic recovery in most cases after one run)
- [ ] Verify CUDA: `python -c "import torch; print(torch.cuda.is_available())"`

---

**Last Validated:** Nov 18, 2025 at 23:45 UTC  
**Validated By:** OmniMind Autonomous Agent  
**Hardware:** Intel i5-10th + GTX 1650 4GB + 24GB RAM  
**Status:** ✅ ALL SYSTEMS OPERATIONAL FOR PHASE 7
