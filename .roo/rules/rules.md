# 🧠 Projeto OmniMind - Instruções GitHub Copilot ROO CODE/CURSOR AI (Consolidado v4.0)

**Data:** 2025-11-19
**Status:** Phase 12 Multi-Modal Intelligence Complete
**Hardware:** Auto-detectado (Intel i5 10ª geração + GTX 1650 4GB + 24GB RAM)
**Destino:** Agente Copilot Remoto (GitHub Codespaces/GitPod)
**Projeto:** /home/fahbrain/projects/omnimind/
---

## 📋 CRÍTICO: 
## 🚫 INVIOLABLE RULES (100% COMPLIANCE REQUIRED)

### Rule 1: Production-Ready Code Only
✅ **MUST:** All code immediately functional and testable  
✅ **MUST:** Complete implementation (no stubs/TODOs)  
✅ **MUST:** Robust error handling  
✅ **MUST:** Complete type hints (Python)  
❌ **NEVER:** Pseudocode  
❌ **NEVER:** Placeholders like "TODO: implement"  
❌ **NEVER:** Empty functions  
❌ **NEVER:** Mock or simulated data  

### Rule 2: No Data Falsification
✅ **MUST:** Real data from operating system  
✅ **MUST:** Outputs reflect actual state  
✅ **MUST:** Document all assumptions explicitly  
✅ **MUST:** Stop and request clarification if impossible  
❌ **NEVER:** Simulate results  
❌ **NEVER:** Generate example data as real  
❌ **NEVER:** Hardcoded values as permanent defaults  

### Rule 3: Quality Standards
✅ **Test coverage:** Minimum 90%  
✅ **Lint score:** 100% (black, flake8, mypy)  
✅ **Docstrings:** Google-style for ALL functions/classes  
✅ **Type hints:** 100% coverage in Python  
✅ **Comments:** None except for complex logic (self-documenting code)  
❌ **NEVER:** Leave TODO, FIXME, or undefined comments  

### Rule 4: Absolute Security
✅ **Cryptographic audit** for ALL critical actions  
✅ **SHA-256 hash chain** with prev_hash linking (blockchain-style)  
✅ **Immutable logs** (append-only with `chattr +i`)  
✅ **Zero hardcoded** secrets or credentials  
✅ **Whitelist** for allowed commands  
✅ **Rigorous** input validation  
❌ **NEVER:** Expose system paths  
❌ **NEVER:** Store passwords in clear  
❌ **NEVER:** Allow unrestricted command execution  

## 🛡️ Stability & Validation Protocol (Master Rule)

**Regra de Ouro — Estabilidade Total**  
- Nunca avance para novos módulos, features ou workflows se existir qualquer erro de lint, type-check ou teste em qualquer arquivo do repositório.  
- A validação é sempre global: o módulo em edição e o restante do projeto devem estar limpos antes de seguir.  
- Corrija avisos pendentes imediatamente; exceções só podem ocorrer com aprovação explícita para refatorações arquiteturais.

**Sequência Obrigátoria de Comandos (por ciclo/commit)**  
Execute sempre nesta ordem e corrija todos os erros antes de prosseguir:
```bash
black src tests
flake8 src tests
mypy src tests
pytest -vv
```
---## 🔐 Segurança Primeiro: Módulo de Segurança Obrigatório
Leia o Módulo de Segurança Primeiro

**LEITURA OBRIGATÓRIA ANTES DE QUALQUER DESENVOLVIMENTO:**
- `/home/fahbrain/OmniAgent/Modulo Securityforensis/` (TODOS OS ARQUIVOS)
- Este conjunto de instruções é subordinado aos requisitos de segurança
- Implementação do Agente de Segurança DEVE ser integrada na Phase 7

---
## 🎯 IDENTIDADE E ISOLAMENTO DO PROJETO

### O que é OmniMind?
**Sistema de IA Autônomo Revolucionário** - Autoconsciente, eticamente orientado, inspirado em psicoanálise
- **🧠 Motor de Metacognição:** IA auto-reflexiva que analisa suas próprias decisões
- **🎯 Objetivos Proativos:** IA gera seus próprios objetivos de melhoria
- **⚖️ Framework de Ética:** Sistema de decisão ética com 4 metodologias (Deontológico, Consequencialista, Virtude, Cuidado)
- **🔄 WebSocket em Tempo Real:** Dashboard ao vivo com atualizações instantâneas
- **🤖 Orquestração Multi-Agente:** Delegação de tarefas psicoanalítica (Freudiana/Lacaniana)
- **🛡️ Segurança Enterprise:** Compatível com LGPD com trilhas de auditoria imutáveis
- **🏗️ Pronto para Produção:** 105/105 testes aprovados, implantação full-stack
- **Otimizado para Hardware** com detecção automática (CPU/GPU)

---

## 🖥️ CONFIGURAÇÃO DE HARDWARE E AMBIENTE (Phase 12 Complete)

### Especificação de Hardware (Auto-detectada)
```
CPU:        Intel i5 10ª geração (4 núcleos/8 threads)
GPU:        NVIDIA GeForce GTX 1650 (4GB VRAM, Compute Capability 7.5)
RAM:        24GB total (18.5GB tipicamente disponíveis)
Driver:     NVIDIA 550.163.01+ (validado)
Status:     ✅ GPU Totalmente Operacional
```

### Configuração de Ambiente (Um Comando)
```bash
# Clone e auto-configuração (detecção de hardware + dependências + serviços)
git clone https://github.com/fabs-devbrain/OmniMind.git
cd OmniMind
source scripts/start_dashboard.sh

# Access interfaces:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - Documentation: http://localhost:8000/docs
```

### Python & PyTorch Stack (Validated Configuration)
**⚠️ CRITICAL: Python 3.12.8 Required**
- ❌ **NEVER** use Python 3.13+ (PyTorch compatibility)
- ✅ **MUST** use Python 3.12.8 via pyenv
- ✅ **AUTO-DETECTED** hardware optimization

**Current Production Stack:**
```
Python: 3.12.8
PyTorch: 2.6.0+cu124 (CUDA 12.4)
Node.js: 18+ (for frontend development)
Status: ✅ All Dependencies Validated
```

**Installation (Automatic):**
```bash
# Hardware auto-detection
python src/optimization/hardware_detector.py

# Dependencies (auto-detects GPU/CPU)
pip install -r requirements.txt

# Verify full stack
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
# Output: CUDA: True
```

### GPU/CUDA Troubleshooting

**Issue: `CUDA unknown error` or `torch.cuda.is_available() returns False`**

**Solution 1: Reload nvidia_uvm kernel module** (Most Common Fix)
```bash
# Kill any processes holding the module
sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true
sleep 1

# Reload the module
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sleep 1
sudo modprobe nvidia_uvm

# Verificar se o módulo está carregado
lsmod | grep nvidia_uvm

# Testar CUDA novamente
python -c "import torch; print(torch.cuda.is_available())"
```

**Resultado Esperado:** `torch.cuda.is_available()` deve retornar `True`

**Nota:** Corrupção do módulo do kernel nvidia_uvm normalmente ocorre após suspensão/hibernação do sistema no Linux. O procedimento de recarregamento restaura o acesso à GPU imediatamente.

**Solução 2: Verificar Instalação CUDA do Sistema**
```bash
# Verificar driver NVIDIA
nvidia-smi

# Verificar se CUDA toolkit está instalado
nvcc --version

# Output esperado deve mostrar CUDA 12.4.x
```

**Solução 3: Atualizar Cache de Biblioteca do Sistema**
```bash
# Reconstruir cache ldconfig para bibliotecas NVIDIA
sudo ldconfig

# Verificar se cuDNN foi encontrado
ldconfig -p | grep cudnn
```

### Baseline de Performance da GPU (Validação Phase 7)

**Performance Validada na GTX 1650:**
- Throughput CPU: 253.21 GFLOPS (multiplicação de matriz 5000x5000)
- Throughput GPU: 1149.91 GFLOPS (multiplicação de matriz 5000x5000)
- Largura de Banda de Memória: 12.67 GB/s
- Fator de Aceleração: **4.5x GPU vs CPU**
- Versão PyTorch: 2.6.0+cu124
- Status: ✅ VERIFICADO 18 Nov 2025