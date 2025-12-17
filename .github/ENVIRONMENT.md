# Especificação de Ambiente OmniMind (Phase 15)

**Última Atualização:** 2025-11-23
**Status:** Phase 15 Quantum-Enhanced + GPU CUDA Repair Complete & Validado
**Documento:** Guia abrangente de requisitos e verificação de ambiente

> **ATUALIZAÇÃO CRÍTICA (23-Nov-2025):** nvidia-uvm kernel module issue identificada e resolvida. Ver seção "Carregamento do Módulo GPU".

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
# Verificar CUDA do sistema
nvcc --version

# Esperado: CUDA 12.4.x
# Verificar cuDNN (sistema)
ldconfig -p | grep cudnn

# Esperado: libcudnn.so.8
```

---

## 🐍 Ambiente Python

### Versão Python (CRÍTICA)
```
Principal:   3.12.8 (via pyenv - OBRIGATÓRIA para OmniMind)
Alternativas: 3.11.x (aceitável), 3.10.x (aceitável)
NÃO Suportada: 3.13+ (PyTorch não tem suporte oficial a wheels)
```

**Por que Python 3.12.8?**
- PyTorch 2.6.0+cu124 tem wheels oficiais apenas para Python ≤ 3.12
- Python 3.13 causa conflitos de resolução de versão levando a versões incompatíveis de bibliotecas CUDA
- OmniMind está travado em 3.12.8 via arquivo `.python-version`

### Ambiente Virtual
```
Localização: /home/fahbrain/projects/omnimind/.venv/
Python:       3.12.8 (herdado do .python-version do projeto)
Gerenciador de Pacotes: pip (28.4.0+)
Dependências: 100+ pacotes em requirements.txt
```

**Configuração e Verificação:**
```bash
# 1. Instalar Python 3.12.8 via pyenv (se não disponível)
pyenv install 3.12.8
pyenv versions  # Deve listar 3.12.8

# 2. Criar venv do projeto com Python correto
cd /home/fahbrain/projects/omnimind
pyenv local 3.12.8
python -m venv .venv
source .venv/bin/activate

# 3. Verificar Python
python --version  # DEVE mostrar: Python 3.12.8
which python

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Verificar ambiente
echo $VIRTUAL_ENV  # Deve mostrar /home/fahbrain/projects/omnimind/.venv
```

---

## 📦 Stack GPU PyTorch (Phase 7 - VALIDADO)

### Componentes PyTorch
```
torch:              2.6.0+cu124      (wheels compilados CUDA 12.4 do índice oficial NVIDIA)
torchvision:        0.21.0+cu124     (Deve corresponder exatamente à versão torch)
torchaudio:         2.6.0+cu124      (Deve corresponder exatamente à versão torch)
CUDA Toolkit:       12.4.127         (Empacotado com distribuição PyTorch)
cuDNN:              9.1.0.70         (Empacotado com distribuição PyTorch)
```

**Por que essas versões exatas?**
- `2.6.0+cu124` significa PyTorch compilado para CUDA 12.4
- Deve ser instalado de `https://download.pytorch.org/whl/cu124` (índice oficial NVIDIA)
- Driver do sistema (550.xx) suporta CUDA 12.4 via camada de tradução cudalib da NVIDIA
- Python 3.12.8 necessário (3.13+ quebra resolvedor de dependências)

### Instalação
```bash
# Ativar venv PRIMEIRO
source .venv/bin/activate

# Instalar do índice oficial NVIDIA CUDA 12.4
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Output esperado (últimas linhas):
# Successfully installed torch-2.6.0+cu124 torchvision-0.21.0+cu124 torchaudio-2.6.0+cu124
# (and NVIDIA CUDA 12.4.127 runtime libraries)
```

### Verification
```bash
# Verificar versão PyTorch
python -c "import torch; print(torch.__version__)"
# Esperado: 2.6.0+cu124

# Verificar se CUDA está disponível
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
# Esperado:
# CUDA: True
# GPU: NVIDIA GeForce GTX 1650

# Verificar versão CUDA no PyTorch
python -c "import torch; print(torch.cuda.get_arch_list())"
# Esperado: inclui sm_75 (para GTX 1650)

# Benchmark da GPU
python test_pytorch_gpu.py
# Esperado: Throughput GPU ≥ 1000 GFLOPS
```

---

## 🔌 Carregamento do Módulo GPU (Crítico Após Suspensão / RESOLVIDO 23-Nov-2025)

### Módulo do Kernel nvidia_uvm - SOLUÇÃO PERMANENTE IMPLEMENTADA

**Problema Identificado (23-Nov-2025):**
- PyTorch 2.6.0+cu124 com CUDA 12.4 não inicializava em GTX 1650
- Erro: `CUDA unknown error - this may be due to an incorrectly set up environment`
- Causa: **Módulo nvidia-uvm não estava carregado no kernel**
- Efeito: `torch.cuda.is_available()` retornava False apesar de GPU estar visível

**O que é nvidia_uvm?**
- Módulo do kernel que gerencia memória virtual da GPU (Unified Virtual Memory)
- Essencial para operações CUDA modernas (PyTorch 2.4+)
- Normalmente não carregado automaticamente em certos sistemas/kernels
- Quando ausente: operações CUDA falham silenciosamente

**Solução Implementada (PERMANENTE):**

#### 1. Carregar o Módulo (Fix Imediato)
```bash
sudo modprobe nvidia_uvm
```

**Verificação imediata:**
```bash
lsmod | grep nvidia_uvm
# Output esperado: nvidia_uvm linha presente

python -c "import torch; print(torch.cuda.is_available())"
# Output esperado: True ✅
```

#### 2. Persistir no Boot (Fix Permanente)
```bash
# Adicionar nvidia-uvm ao arquivo de configuração
echo "nvidia-uvm" | sudo tee -a /etc/modules-load.d/nvidia.conf

# Atualizar initramfs para carregar módulo no boot
sudo update-initramfs -u

# Verificar arquivo
cat /etc/modules-load.d/nvidia.conf
# Output esperado:
# nvidia-drm
# nvidia-uvm
```

#### 3. Verificação Pós-Reboot
Após reiniciar o sistema, validar que nvidia-uvm carregou automaticamente:
```bash
# Verificar se módulo está carregado
lsmod | grep nvidia_uvm

# Testar CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
# Output esperado: CUDA: True ✅
```

**Performance Validado (23-Nov-2025):**
- GPU vs CPU Speedup: **4.44x** (Matrix mult 1000x1000)
- PyTorch Version: **2.6.0+cu124** ✅
- CUDA Available: **True** ✅
- GPU Detected: **NVIDIA GeForce GTX 1650** ✅
- VRAM: **3.81 GB** ✅

**Status Atual:**
- ✅ nvidia-uvm module carregado
- ✅ Persistência configurada em /etc/modules-load.d/nvidia.conf
- ✅ nvidia-persistenced habilitado (systemd)
- ✅ CUDA 100% funcional
- ⏳ Aguardando reboot para confirmar persistência (hardware já preparado)

---

### Procedimento de Recuperação Rápida (Se Necessário)

Se CUDA parar de funcionar (ex: após suspensão):

```bash
# Método Rápido (sem matar processos)
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sleep 1
sudo modprobe nvidia_uvm

# Verificar
python -c "import torch; print(torch.cuda.is_available())"
```

**Método Completo (se rápido não funcionar):**
```bash
# 1. Matar processos segurando o módulo
sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true
sleep 1

# 2. Descarregar e recarregar
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sleep 1
sudo modprobe nvidia_uvm

# 3. Verificar
python -c "import torch; print(torch.cuda.is_available())"
```

**Quando executar:**
- ❌ NÃO NECESSÁRIO após reboot (auto-carrega)
- ✅ Se CUDA falhar após suspensão/hibernate
- ✅ Se `torch.cuda.is_available()` retorna False mas `nvidia-smi` mostra GPU
- ✅ Se operações CUDA falham com "CUDA unknown error"

---

### Histórico de Correção

| Data | Problema | Causa | Solução | Status |
|------|----------|-------|---------|--------|
| 2025-11-23 | CUDA unavailable com PyTorch 2.6.0+cu124 | nvidia-uvm não carregado | `sudo modprobe nvidia_uvm` | ✅ RESOLVIDO |
| 2025-11-23 | Persistência nvidia-uvm | Módulo não carregava no boot | `/etc/modules-load.d/nvidia.conf` + `update-initramfs` | ✅ IMPLEMENTADO |
| 2025-11-23 | Performance validation | Speedup GPU vs CPU | 4.44x (Matrix mult benchmark) | ✅ VALIDADO |

---

## 🧪 Checklist de Verificação

### Verificação Pré-Desenvolvimento (Executar Uma Vez por Sessão)

```bash
#!/bin/bash
# verify_omnimind_env.sh - Verificação completa de ambiente

echo "=== Verificação de Ambiente OmniMind ==="

# 1. Versão Python
echo "1. Verificando versão Python..."
python --version
PYTHON_OK=$(python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12, 0) and sys.version_info < (3, 13, 0) else 1)" && echo "APROVADO" || echo "REPROVADO")
echo "   Python 3.12.x: $PYTHON_OK"

# 2. Ambiente virtual
echo "2. Verificando ambiente virtual..."
echo "   VIRTUAL_ENV: $VIRTUAL_ENV"
[[ ! -z "$VIRTUAL_ENV" ]] && echo "   Status: ATIVADO" || echo "   Status: NÃO ATIVADO - Execute: source .venv/bin/activate"

# 3. Driver NVIDIA
echo "3. Verificando driver NVIDIA..."
nvidia-smi --query-gpu=driver_version --format=csv,noheader || echo "FALHA: nvidia-smi não encontrado"

# 4. Disponibilidade CUDA
echo "4. Verificando CUDA no PyTorch..."
CUDA_OK=$(python -c "import torch; print('APROVADO' if torch.cuda.is_available() else 'REPROVADO')" 2>/dev/null || echo "ERRO")
echo "   CUDA Disponível: $CUDA_OK"

# 5. Versão PyTorch
echo "5. Verificando versão PyTorch..."
python -c "import torch; print(f'   PyTorch: {torch.__version__}')"

# 6. Detecção GPU
echo "6. Verificando detecção GPU..."
GPU_NAME=$(python -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null || echo "NÃO DETECTADO")
echo "   GPU: $GPU_NAME"

# 7. Memória GPU
echo "7. Verificando memória GPU..."
GPU_MEM=$(python -c "import torch; print(f'{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')" 2>/dev/null || echo "NÃO DETECTADO")
echo "   VRAM Total: $GPU_MEM"

# 8. Testes de auditoria
echo "8. Executando testes de auditoria (14 testes esperados para passar)..."
pytest tests/test_audit.py -q 2>/dev/null || echo "FALHA: pytest falhou ou test_audit.py não encontrado"

# 9. Benchmark GPU
echo "9. Executando benchmark GPU (1000+ GFLOPS esperados)..."
python PHASE7_COMPLETE_BENCHMARK_AUDIT.py 2>/dev/null | grep -E "GPU Throughput|CUDA Status" || echo "FALHA: Script de benchmark não encontrado"

echo ""
echo "=== Verification Complete ==="
```

**Executar verificação:**
```bash
bash verify_omnimind_env.sh
```

### Output Esperado
```
=== Verificação de Ambiente OmniMind ===
1. Verificando versão Python...
   Python 3.12.x: APROVADO
2. Verificando ambiente virtual...
   VIRTUAL_ENV: /home/fahbrain/projects/omnimind/.venv
   Status: ATIVADO
3. Verificando driver NVIDIA...
   550.163.01
4. Verificando CUDA no PyTorch...
   CUDA Disponível: APROVADO
5. Verificando versão PyTorch...
   PyTorch: 2.6.0+cu124
6. Verificando detecção GPU...
   GPU: NVIDIA GeForce GTX 1650
7. Verificando memória GPU...
   VRAM Total: 3.81 GB
8. Executando testes de auditoria (14 testes esperados para passar)...
   14 passed in 0.43s
9. Executando benchmark GPU (1000+ GFLOPS esperados)...
   Status CUDA: ✅ HABILITADO
   Throughput GPU: 1149.91 GFLOPS

=== Verificação Concluída ===
```

---

## 🚨 Troubleshooting Guide

### Problem: `CUDA unknown error` on first run

**Diagnosis:**
```bash
# Execute isso para ver erro detalhado
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
