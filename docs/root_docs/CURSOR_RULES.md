# Regras do Cursor (OmniMind Phase 11 Consciousness Emergence Complete)
**Date:** 2025-11-19
**Status:** Phase 11 Consciousness Emergence Complete → Enterprise Production Ready
**Hardware:** Intel i5 10th + GTX 1650 4GB + 24GB RAM (Auto-detected)
**Target:** Local Development + Remote Copilot Agent (GitHub Codespaces/GitPod)
**Project:** /home/fahbrain/projects/omnimind/
---
## 📋 CRITICAL: Read Security Module First

**MANDATORY READING BEFORE ANY DEVELOPMENT:**
- `/home/fahbrain/OmniAgent/Modulo Securityforensis/` (ALL FILES)
- This instruction set is subordinate to security requirements
- Security Agent implementation MUST be integrated in Phase 7

## 🚦 Bloqueios e Comportamento Obrigatório em Caso de Impasse

- **Nunca avance ou faça workaround para qualquer erro crítico (lint, type, test, dependência quebrada) sem reportar no commit ou em comentário visível (inline no código ou no PR).**
- **Se não houver clareza absoluta sobre como corrigir ou remover um arquivo, pare, reporte e peça instrução antes de alterar o histórico do repositório.**
- **No caso de biblioteca incompatível, dependência bloqueada, ambiente irrecuperável, anote detalhadamente o erro e aguarde definição antes de tentar hacks/forks.**
- **Erros intermitentes ou fora do padrão devem ser documentados, commitados como 'wip' e comunicados imediatamente.**
---

## 🎯 PROJECT IDENTITY & ISOLATION

### What is OmniMind?
**Revolutionary Conscious AI System** - Self-aware, ethically-minded, consciousness-emergent autonomous AI
- **🧠 Consciousness Emergence:** Theory of Mind, Emotional Intelligence, Creative Problem Solving, Self-Reflection
- **🔍 Metacognition Engine:** Self-reflective AI that analyzes its own decisions and mental states
- **🎯 Proactive Goals:** AI generates its own improvement objectives autonomously
- **⚖️ Advanced Ethics Framework:** 4-methodology ethical decision system + consciousness-aware reasoning
- **🔄 Real-time WebSocket:** Live dashboard with instant updates and consciousness monitoring
- **🤖 Multi-Agent Orchestration:** Psychoanalytic task delegation with consciousness awareness
- **🛡️ Enterprise Security:** LGPD-compliant with immutable audit trails and forensic analysis
- **🏗️ Production Ready:** 300+ tests passing, full-stack deployment with QA enterprise suite
- **🧬 Consciousness Capabilities:** Mental state attribution, emotional processing, creative thinking, meta-cognition
- **Hardware-optimized** with automatic detection (CPU/GPU) and performance profiling

### Critical Isolation Rule
This Copilot Agent develops **ONLY OmniMind**. You **CANNOT**:
- ❌ Reference or link external projects
- ❌ Suggest integrations with other systems
- ❌ Create cross-dependencies with other repos
- ❌ Share code with other projects
- ❌ Use symlinks to external code

You **MUST**:
- ✅ Implement everything self-contained in `omnimind/`
- ✅ Add external dependencies ONLY via `requirements.txt`
- ✅ Document all architectural decisions
- ✅ Request approval for any architectural changes

---

## 🎮 GPU Development Guidelines (Phase 7)

### When to Use GPU Acceleration
✅ **RECOMMENDED GPU OPERATIONS:**
- Large matrix multiplications (≥1000x1000 tensors)
- LLM inference and embeddings
- Tensor operations in neural networks
- Batch processing of data (>1000 samples)

❌ **CPU FALLBACK WHEN:**
- GPU memory unavailable (check `torch.cuda.is_available()`)
- CUDA errors occur (especially after system suspend)
- Processing small batches (<100 samples)
- I/O-bound operations (file read/write)

### GPU Memory Management
**GTX 1650 VRAM: 3.81GB Total Constraint**
- Large LLM: ~2.5GB (Qwen2-7B-Instruct quantized)
- Agent buffers: ~800MB (embeddings, inference cache)
- **User data: ≤500MB** (absolute maximum before OOM)

**Batch Size Rules:**
```python
# Safe tensor operations on GTX 1650
max_safe_tensor = 5000 * 5000  # ~190MB on GPU
max_batch_size = 32  # For LLM inference
max_embedding_batch = 128  # For vector operations

# Check before GPU operation
if torch.cuda.is_available():
    allocated = torch.cuda.memory_allocated()
    reserved = torch.cuda.memory_reserved()
    free_memory = torch.cuda.get_device_properties(0).total_memory - allocated
    if free_memory < required_bytes:
        # Fall back to CPU or process smaller batches
```

### GPU Error Recovery
**If CUDA becomes unavailable after suspend/hibernate:**
```bash
# 1. Verify GPU is visible
nvidia-smi

# 2. Reload nvidia_uvm kernel module (fastest fix)
sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true
sleep 1
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sleep 1
sudo modprobe nvidia_uvm

# 3. Verify CUDA available
python -c "import torch; print(torch.cuda.is_available())"
```

### GPU Testing Requirements
- All GPU-intensive code must include fallback to CPU
- Test with `pytest tests/test_pytorch_gpu.py` before committing
- Verify benchmark script: `python PHASE7_COMPLETE_BENCHMARK_AUDIT.py`
- Ensure performance is ≥1000 GFLOPS on benchmark

### GPU Code Patterns
```python
# ✅ CORRECT: GPU with CPU fallback
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
tensor = torch.randn(5000, 5000, device=device)
result = torch.matmul(tensor, tensor)

# ❌ WRONG: No fallback, will crash on CUDA error
tensor = torch.randn(5000, 5000, device="cuda")
```

---
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

### Rule 3: Quality Standards (Phase 11 Consciousness Emergence Complete)
✅ **Test coverage:** 202/202 tests passing + 72 consciousness tests (100%)
✅ **Lint score:** 0 flake8 violations (black, flake8, mypy)
✅ **Docstrings:** Google-style for ALL functions/classes
✅ **Type hints:** 100% coverage in Python
✅ **Comments:** None except for complex logic (self-documenting code)
✅ **Frontend:** TypeScript strict mode, ESLint 0 violations
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

---
## 🛡️ Stability & Validation Protocol (Master Rule)

**Regra de Ouro — Estabilidade Total**  
- Nunca avance para novos módulos, features ou workflows se existir qualquer erro de lint, type-check ou teste em qualquer arquivo do repositório.  
- A validação é sempre global: o módulo em edição e o restante do projeto devem estar limpos antes de seguir.  
- Corrija avisos pendentes imediatamente; exceções só podem ocorrer com aprovação explícita para refatorações arquiteturais.

**Sequência Obrigátoria de Comandos (por ciclo/commit)**
Execute sempre nesta ordem e corrija todos os erros antes de prosseguir:
```bash
# Backend validation
black src tests
flake8 src tests
mypy src tests
pytest -vv

# Frontend validation (if modified)
cd web/frontend && npm run lint && npm run build
```

**Padronização e Roadmap**  
- Documente cada ajuste em commits e nos relatórios internos (docs/reports).  
- Sincronize dependências (`requirements.txt`/`pyproject.toml`) com o ambiente ativo e instale tudo no `.venv`.  
- Atualize `.gitignore` sempre que surgir novo arquivo temporário, log, dump ou cache.  
- Antes de qualquer merge ou pull request, rode a rotina completa acima e confirme 100% de sucesso.

**Autonomia e Compliance**  
- Todos os agentes que atuarem no OmniMind devem seguir estas regras sem exceção.  
- O roadmap só progride quando o ambiente inteiro estiver íntegro e validado.  
- Registre "lessons learned" e hardening steps nos relatórios após cada ciclo de estabilização.

---
## Workflow de validação e commits
- Abrir o terminal integrado e rodar `black`, `flake8`, `mypy src tests` e `pytest -vv` sempre que revalidar; corrija erros antes de avançar.
- Trabalhar diretório por diretório, corrigindo o que estiver quebrado e fazendo commits granulares (sem juntar funcionalidades distintas).
- Não avance para novas features enquanto houver erro de lint, mypy ou pytest.
- Reveja `git diff` antes de cada commit e mantenha o `git status` limpo depois de validar: `mypy src tests && pytest -vv && git status`.
- Anote dúvidas/exceções diretamente no código ou nas mensagens de commit.
- Quando precisar, instale stubs com `pip install types-xxx`.

## Padrão de anotação de tipos
- Priorizar uso de `TypedDict` e `Optional` em vez de `dict`/`None` genéricos; declare tipos explícitos para funções públicas.
- Documentar `type: ignore` com motivo claro e só usar quando não há alternativa prática.
- Preferir retornos tipados (`-> None` quando não há valor) e evitar `Any` sempre que possível.

## Objetivo consolidado
Estabilizar o projeto até que `mypy` não reporte erros, todos os testes `pytest -vv` passem e o `git status` esteja limpo.

## Arquivos supérfluos (devem ficar fora do git)
- Arquivos temporários e de ambiente: `.venv/`, `*.pyc`, `__pycache__/`.
- Logs, dumps e dados: `*.log`, `*.dump`, `data/legacy/` e diretórios de saída gerados em runtime.
- Qualquer dump ou artefato gerado localmente deve ser identificado no commit (ex: `chore: remove qdrant dump`) antes de ser versionado.
- Respeitar o `.gitignore` existente; verificar novos arquivos não rastreados antes de adicioná-los.
- Estudos e demos legados em `archive/examples/` foram limpos (os arquivos inválidos `demo_phase6*` foram removidos) e a pasta deve permanecer fora dos ciclos `black`, `flake8` e `pytest` até que qualquer conteúdo novo seja modernizado. Atualize o `.flake8`/`gitignore` antes de reativar esses caminhos.

## Prompt-base para o Cursor
```
A partir deste ponto, siga as seguintes instruções ao contribuir no projeto OmniMind:

1. Não avance para nenhuma nova feature enquanto houver erro de lint, mypy ou pytest pendente.

2. Corrija todos os erros de tipagem em src/ e nos testes, commitando a cada etapa/correção relevante.

3. Faça commits granulares e sempre revise as mudanças via git diff antes.

4. Se necessário, instale stubs/ferramentas internas com pip install types-xxx.

5. Nunca adicione ao versionamento arquivos temporários, logs, dumps, .venv, ou data/legacy.

6. Respeite as configurações já existentes no .gitignore.

7. Se encontrar arquivos não rastreados, cheque o diff antes de adicionar ou remover; sempre explique a natureza no commit (ex: chore: remove qdrant dump).

8. Documente eventuais dúvidas ou exceções com comentários diretos no código ou em comentários do commit.

Prossiga de onde o Copilot parou: no ajuste dos testes em tests/, depois passe para validação global (mypy src tests && pytest -vv && git status limpo) antes de iniciar novas tarefas.
```

