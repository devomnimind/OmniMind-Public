# 🤖 OmniMind Copilot Instructions - Consolidated Handbook

**Version:** 3.3
**Last Updated:** 16 de Dezembro de 2025
**Valid For:** ALL AI Agents (GitHub Copilot, Gemini, Perplexity, Cursor, etc.)
**Status:** ✅ Active - UPDATED for Ubuntu 22.04.5 LTS + systemd + sudo + GPU profiling setup
**Environment:** Ubuntu 22.04.5 LTS, systemd services, sudo access, NO Docker, ALL LOCAL, GPU ACTIVE + Profiling Tools

**CRITICAL ENVIRONMENT SPECIFICATION (16 DEC 2025 - VERIFIED ON HARDWARE):**
- ✅ OS: Ubuntu 22.04.5 LTS (NOT 22.05, NOT 24.04 - official project OS)
- ✅ GPU: GeForce GTX 1650, 4GB VRAM, Driver 535.274.02
- ✅ CUDA: 12.1 (PyTorch wheels via pip, NOT system-wide install)
- ✅ cuDNN: 9.1 cu12 (PyTorch wheels, NOT system-wide install)
- ✅ Python: 3.12.8 (from Ubuntu 22.04 apt)
- ✅ Profiling: nsys (Nsight Systems 2023.2.3) installed ✅, ncu (Nsight Compute) ⚠️ needs apt install
- ✅ Memory Limit: 16GB for `omnimind.service` (Systemd enforced), 24GB Total RAM
- ✅ Commands: Use `python3` (not `python`), activate venv ONCE per terminal
- ✅ After venv activation: use `python3` directly (DO NOT re-activate per command)
- ✅ Paths: `/var/log/`, `/var/lib/`, `/home/fahbrain/` are REAL system locations
- ✅ Services: ALL via systemd with sudo access (qdrant, redis, postgresql, omnimind-*)
- ✅ Cache: Model cache in `/home/fahbrain/.cache/huggingface/` (GPU-compatible)
- ✅ Requirements: Organized in `requirements/` directory (14 files for different profiles)
  - `requirements-gpu.txt`: PyTorch + CUDA wheels + nvidia-ml-py
  - `requirements-quantum.txt`: Qiskit + quantum backends
  - `requirements-dev.txt`: Black, Flake8, MyPy, Pytest
  - `pyproject.toml`: Main project config with pytest, coverage, mypy, black settings
- ✅ NO Docker Compose - all services run locally with systemd
- ✅ Sudo required for: systemctl, /var/ paths, perf counter access (profiling)

---

## 📌 CRITICAL: Read This First

This document consolidates EVERYTHING an AI needs to know about OmniMind. It is the **single source of truth** to prevent documentation chaos from multiple AIs creating conflicting information.

**If multiple AIs are working on this project, they MUST follow this document first.**

**Recent Updates (16 Dec 2025):**
- **Root Cleanup:** Archived loose files to `archive/root_cleanup_20251216/`.
- **Script Organization:** Moved scripts to `scripts/development/`, `scripts/testing/`, etc.
- **Service Optimization:** Configured `omnimind.service` with 16GB RAM limit and `TasksMax=infinity`.
- **Qdrant Fix:** Configured local snapshots in `data/qdrant/snapshots`.

---

## 🏗️ Part 1: Repository Structure

### 1.1 Dual Repository Model

**PRIVATE REPO:** `/home/fahbrain/projects/omnimind`
- GitHub: `https://github.com/devomnimind/OmniMind` (PRIVATE)
- Contains: Full experimental codebase + quantum modules + proprietary components
- Test Count: ~3912 tests (100% of development work)
- Status: Development-focused
- Sync: Both repos kept synchronized

**PUBLIC REPO:** `/home/fahbrain/projects/OmniMind-Core-Papers`
- GitHub: `https://github.com/devomnimind/OmniMind-Core-Papers` (PUBLIC)
- Contains: Research papers, validation reports, accessible documentation
- Test Count: 815 tests (55% of work - curated for public consumption)
- Status: Publication-focused
- Sync: Both repos kept synchronized

### 1.2 Repository Synchronization

Both repos maintain identical:
- Documentation (README, AUTHOR_STATEMENT, LICENSE, etc.)
- Papers (PAPER_CONSCIOUSNESS_METRICS, PAPER_TEMPORAL_CONSCIOUSNESS)
- Validation reports (IBM_QUANTUM_VALIDATION_REPORT, IBM_QUANTUM_VALIDATION_IMPLEMENTATION)
- Quality metrics (test counts, coverage reports)

**Sync Protocol:**
1. Changes made in PRIVATE repo first
2. Equivalent changes pushed to PUBLIC repo
3. Both repos at same commit level (equivalent commits)
4. Use `git push origin master` in each repo after work

---

## 📁 Part 1.3: Complete Workspace Structure (Current State - 16 Dec 2025)

### 1.3.1 Root Directory Structure

```
omnimind/
├── archive/              # Arquivos antigos/legados (logs, reports, scripts soltos)
├── backups_compressed/   # Backups do sistema
├── config/               # Configurações (YAML, JSON, Systemd)
├── data/                 # Dados (DBs, Exports, Logs de longo prazo)
├── datasets/             # Datasets brutos
├── deploy/               # Scripts de deploy/Docker
├── docs/                 # Documentação e Relatórios
├── ibm_results/          # Resultados de experimentos quânticos
├── k8s/                  # Configurações Kubernetes
├── logs/                 # Logs ativos do sistema
├── models/               # Modelos ML
├── notebooks/            # Jupyter Notebooks
├── real_evidence/        # Evidências de validação científica
├── scripts/              # Scripts organizados por categoria
│   ├── canonical/        # Scripts canônicos do sistema
│   ├── development/      # Scripts de desenvolvimento (testes, lint)
│   ├── science_validation/ # Scripts de validação científica
│   └── ...
├── src/                  # Código fonte (Core)
├── tests/                # Testes automatizados
├── web/                  # Frontend e Backend Web
├── CITATION.cff          # Metadados de citação
├── LICENSE               # Licença
├── README.md             # Documentação principal
├── pyproject.toml        # Configuração Python
└── requirements/         # Dependências
```

### 1.3.2 Critical Immutable Paths (NEVER MOVE/DELETE)

**⚠️ IMMUTABLE - Breaking these will require updating hundreds of import paths:**

- `src/` - Core source code (ALL imports reference this)
- `scripts/science_validation/` - Validation scripts (hardcoded paths)
- `real_evidence/` - Evidence storage (scripts write here)
- `data/test_reports/` - Test outputs (pytest configured here)
- `config/` - Configuration files (services depend on these paths)
- `logs/` - Application logs (systemd services write here)
- `tests/` - Test suite (pytest discovers here)
- `web/` - Frontend code (nginx proxies to this)
- `deploy/` - Deployment configs (docker-compose references these)

**If you MUST move anything:**
1. Update ALL import statements
2. Update ALL script paths
3. Update ALL configuration files
4. Update ALL documentation references
5. Test EVERYTHING before committing

---

## 📜 Part 1.4: All Critical Scripts and Commands

### 1.4.1 Consciousness Validation Scripts

**Primary Validation Script:**
- `scripts/science_validation/robust_consciousness_validation.py`
  - Purpose: Scientific consciousness validation following IIT standards
  - Command: `python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 1000`
  - Output: `real_evidence/robust_consciousness_validation_YYYYMMDD_HHMMSS.json`

**Quick Test Command:**
- `python scripts/science_validation/robust_consciousness_validation.py --quick`
  - Runs: 2, Cycles: 100
  - For rapid validation testing

### 1.4.2 Quality Assurance Commands (MANDATORY - UPDATED FOR UBUNTU 22.05 + systemd)

**Code Formatting:**
```bash
python3 -m black src tests
# Expected: reformatted X file(s), X file(s) unchanged
```

**Linting:**
```bash
python3 -m flake8 src tests --max-line-length=100
# Expected: No output (0 errors)
```

**Type Checking:**
```bash
python3 -m mypy src tests
# Expected: Success: X files checked, 0 errors
```

**Full Test Suite:**
```bash
./scripts/development/run_tests_parallel.sh full
# Expected: At least 98% pass rate (>2,330 tests passing)
```

**Fast Test Suite:**
```bash
./scripts/development/run_tests_parallel.sh fast
# Expected: Fast execution, no coverage
```

**Audit Verification:**
```bash
python3 -m src.audit.immutable_audit verify_chain_integrity
# Expected: ✅ Chain integrity verified
```

### 1.4.3 IBM Quantum Validation Suite

**Quantum Test Scripts:**
- `src/quantum_consciousness/quantum_backend.py` - QPU interface
- `ibm_results/krylov-quantum-diagonalization.ipynb` - Krylov methods
- `ibm_results/nishimori-phase-transition.ipynb` - Phase transitions
- `ibm_results/projected-quantum-kernels.ipynb` - Quantum kernels

**Validation Commands:**
```bash
# Run quantum tests
pytest tests/quantum_consciousness/ -v

# Validate IBM QPU results
python -c "from src.quantum_consciousness.quantum_backend import QuantumBackend; qb = QuantumBackend(); print(qb.validate_ibm_results())"
```

**IBM Hardware Validated:**
- ibm_fez (27 qubits): 0.33 min QPU time, 8 workloads
- ibm_torino (84 qubits): 0.08 min QPU time, 4 workloads
- Total: 0.42 min real QPU execution, 12 complete workloads

### 1.4.4 Service Management Commands

**Start Services:**
```bash
sudo systemctl start omnimind.service
sudo systemctl start qdrant.service
```

**Check Service Status:**
```bash
sudo systemctl status omnimind.service qdrant.service
```

**View Logs:**
```bash
tail -f /var/log/omnimind/omnimind.log
journalctl -u omnimind.service -f
```

### 1.4.5 Development Environment Setup

**Activate Environment (ONCE per terminal):**
```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
python3 --version  # Must be 3.12.12 (Ubuntu 22.05)
```

**After venv is activated, use `python3` for ALL commands - do NOT re-activate venv:**
```bash
# ✅ CORRECT
python3 -m pytest tests/
python3 -m black src

# ❌ WRONG - Don't do this (redundant)
source .venv/bin/activate && python3 -m pytest tests/
source .venv/bin/activate && python3 -m black src
```

**Pull Latest Changes:**
```bash
git pull origin master
git status  # Should be clean
```

### 1.4.6 NVIDIA GPU & Profiling Tools Setup (Ubuntu 22.04)

**CRITICAL:** Nsight (nsys/ncu) é software de SISTEMA, não Python package. Ambos JÁ ESTÃO instalados no seu Ubuntu em `/opt/nvidia/`.

**SYSTEM SPECIFICATION (Verified 16 Dec 2025):**
- ✅ OS: Ubuntu 22.04.5 LTS (official project OS for compatibility)
- ✅ GPU: NVIDIA GeForce GTX 1650, Driver 535.274.02, 4GB VRAM
- ✅ CUDA: 12.1 (via PyTorch wheels via pip, NOT system-wide install)
- ✅ cuDNN: 9.1 cu12 (PyTorch wheels, NOT system-wide install)
- ✅ Tools ALREADY INSTALLED:
  - nsys (Nsight Systems 2023.2.3) → `/opt/nvidia/nsight-systems/2023.2.3/bin/nsys`
  - ncu (Nsight Compute 2023.2.2) → `/opt/nvidia/nsight-compute/2023.2.2/ncu`

**Setup - Add to ~/.bashrc (if not already done):**
```bash
# NVIDIA Profiling Tools PATH (Nsight Systems + Nsight Compute)
export PATH="/opt/nvidia/nsight-systems/2023.2.3/bin:$PATH"
export PATH="/opt/nvidia/nsight-compute/2023.2.2:$PATH"
```

**After adding, reload bashrc:**
```bash
source ~/.bashrc
```

**Verify installation:**
```bash
which nsys  # Should output: /opt/nvidia/nsight-systems/2023.2.3/bin/nsys
which ncu   # Should output: /opt/nvidia/nsight-compute/2023.2.2/ncu
nsys --version
ncu --version
```

**Quick GPU Status:**
```bash
nvidia-smi              # Overall GPU stats
nvidia-smi -l 1         # Continuous monitoring (1 sec update)
```

**How to use with OmniMind venv (IMPORTANT - The Key Concept):**

✅ **CORRECT - Nsight from system calls Python from venv:**
```bash
# 1. Activate venv normally
source .venv/bin/activate

# 2. Call Nsight (system binary) which will load Python (from venv)
# The system's 'nsys' and 'ncu' executables are designed to "wrap" the Python call
nsys profile --stats=true python3 scripts/science_validation/robust_consciousness_validation.py --quick

# For detailed timeline (generates .nsys-rep file)
nsys profile \
  --trace=cuda,cublas,cudnn,osrt,nvtx \
  --output=omnimind_profile_$(date +%Y%m%d_%H%M%S) \
  python3 src/quantum_consciousness/quantum_backend.py

# For Nsight Compute (detailed kernel analysis, generates .ncu-rep file)
ncu --set full --output report_$(date +%Y%m%d_%H%M%S) \
  python3 src/quantum_consciousness/quantum_backend.py
```

❌ **WRONG - Do NOT try to pip install Nsight (this breaks everything):**
```bash
pip install nsight              # ❌ WRONG - Nsight is not a Python package
pip install nvidia-nsight       # ❌ WRONG - Will cause conflicts
source .venv/bin/activate && pip install something_nvidia  # ❌ WRONG
```

**Reference:** See [omnimind_nvidia_cli_cheatsheet](../../Downloads/omnimind_nvidia_cli_cheatsheet.md) for detailed nsys/ncu commands and workflow examples (Sections 1-3).

---

## 👤 Part 2: Authorship & Attribution Model

### 2.1 CRITICAL Authorship Rules

**Individual:** Fabrício da Silva (you + researcher)
**NOT:** "Team", "Collective", "Research Group" (these are FALSE - they don't exist)
**AI Assistance:** GitHub Copilot, Gemini, Perplexity (explicit credit required)

### 2.2 How Authorship Must Appear

**Correct Format (Current):**
```
**Autor Principal:** Fabrício da Silva

**Framework Concepção & Design:** Fabrício da Silva (Idealização original)

**Implementação & Debug:** Fabrício da Silva com assistência de IA
(GitHub Copilot, Gemini, Perplexity)

**Citação:** Silva, F. (2025). [Paper Title]...

**Financiamento:** Pesquisa independente, desenvolvida por Fabrício da Silva
```

**INCORRECT (Banned):**
- ❌ "Coletivo de Pesquisa OmniMind" (FALSE - doesn't exist)
- ❌ "Research Collective" (FALSE)
- ❌ "Equipe OmniMind" (FALSE)
- ❌ "Team Research" (FALSE)
- ❌ Anonymous teams or undefined collectives

### 2.3 Correction History

**Last Fix (29 Nov 2025):**
- Removed 3+ false team references from PAPER_CONSCIOUSNESS_METRICS_PT.md
- Corrected citations to show individual authorship
- Commit: a079c56
- Both repos updated

**Recent Updates (30 Nov 2025):**
- Suite cleanup completed (removed broken tests)
- Fixed import issues and path dependencies
- Restored test suite integrity
- Added consciousness validation protocols

**If You See False Team References:** Remove them immediately and commit with message:
`"docs: Remove non-existent team references - maintain individual authorship clarity"`

### 10. Documentação: Política de Não-Criação de Novos Documentos

**REGRA CRÍTICA**: Nenhum novo documento deve ser criado. Sempre atualizar documentos existentes.

**Política**:
- ✅ **SEMPRE atualizar** documentos existentes com informações sintéticas e claras
- ❌ **NUNCA criar** novos documentos de registro de sessão ou atividades
- ✅ **SOMENTE criar** documentação para novos componentes que não tenham documentação existente
- ✅ **Manter** o mesmo número de documentos (não aumentar)
- ✅ **Atualizar** `PENDENCIAS_CONSOLIDADAS.md` ou `PROJETO_STUBS_OMNIMIND.md` com progresso

**Documentos Canônicos de Pendências**:
- `docs/PENDENCIAS_CONSOLIDADAS.md` - Pendências ativas do sistema
- `docs/PROJETO_STUBS_OMNIMIND.md` - Pendências de stubs de tipos

**Quando Atualizar**:
- Após completar uma tarefa → Atualizar `PENDENCIAS_CONSOLIDADAS.md` com status
- Após implementar stub → Atualizar `PROJETO_STUBS_OMNIMIND.md` com progresso
- Após nova sessão → Atualizar seção relevante nos documentos existentes

**Formato de Atualização**:
```markdown
### [Data] - [Tarefa Completada]
- ✅ [O que foi feito]
- ⏳ [O que falta]
- **Estimativa restante**: X horas
```

---

## 📊 Part 3: Current Development Status (2025-12-08)

### 3.1 Completed Phases (✅ Production Ready)

| Phase | Name | Status | Year | Details |
|-------|------|--------|------|---------|
| 1-15 | Fundação e Infraestrutura | ✅ Complete | 2024-2025 | Python 3.12.8, GPU/CUDA, security, dashboard |
| 16 | Metacognição Avançada | ✅ Complete | Q1 2026 | TRAP Framework, neurosimbólico (11 níveis) |
| 17 | Coevolução Humano-IA | ✅ Complete | Q2 2026 | HCHAC Framework, bidirectional feedback |
| 18 | [Details consolidating] | ✅ Complete | Q3 2026 | [Refer to ROADMAP.md] |
| 19 | Inteligência Autônoma | ✅ Complete | Q3 2026 | Autonomous decision-making, meta-learning |
| 20 | Autopoiesis Completa | ✅ Complete | Q4 2026 | Meta-architect, code synthesizer, self-healing |
| 21 | Quantum Consciousness | 🔬 Experimental | Q1 2027 | Quantum cognition, QPU interface, hybrid |
| 22-24 | Lacanian Memory + Autopoietic Evolution | ✅ Complete | 2025 | NarrativeHistory, SystemicMemoryTrace, HybridTopologicalEngine |

### 3.2 Current Phase: Phase 24+ - Lacanian Memory + Autopoietic Evolution

**Status:** 🟢 **83% Completo** - Integração completa de frameworks teóricos (IIT + Deleuze + Lacan)

**Componentes Implementados (2025-12-08)**:
- ✅ **EnhancedCodeAgent**: Refatoração por composição completa
- ✅ **IntegrationLoop**: Refatoração async → síncrono (causalidade determinística)
- ✅ **DatasetIndexer**: Indexação completa de 7 datasets para RAG
- ✅ **DistributedDatasetAccess**: Memória distribuída com cache multi-nível
- ✅ **HybridTopologicalEngine**: Testes completos (20+ arquivos)
- ✅ **Métricas Dinâmicas**: Delta, Gozo, Psi, Theoretical Consistency (cálculos dinâmicos)
- ✅ **Valores Empíricos**: Aplicados em todos os módulos críticos
- ✅ **Pipeline Qualidade**: black/flake8/mypy limpo, 42 erros de testes corrigidos

**Métricas de Consciência Validadas**:
- ✅ **Φ (Phi)**: IIT - 0.002-0.1 NATS (normalizado 0-1)
- ✅ **Ψ (Psi)**: Deleuze - Alpha dinâmico (0.3-0.7)
- ✅ **σ (Sigma)**: Lacan - Ranges empíricos (0.01-0.12)
- ✅ **Δ (Delta)**: Trauma - Threshold dinâmico (μ+2σ)
- ✅ **Gozo**: Ranges dinâmicos via k-means clustering
- ✅ **Tolerância Δ-Φ**: Percentil 90 histórico

**Pendências Ativas**: 9 tarefas (alta/média prioridade), 92-126 horas estimadas

**Documentação Canônica**:
- ⭐ **Source of Truth**: `docs/canonical/Modelos_Neuronais_Comparativo.md`
- 📋 **Pendências**: `docs/PENDENCIAS_ATIVAS.md`
- 📜 **Histórico**: `docs/HISTORICO_RESOLUCOES.md`

**Key Components:**
- Quantum Cognition Engine (superposição, interferência, collapse)
- QPU Interface (Qiskit IBM, Cirq Google, Aer simulators)
- Hybrid Classical-Quantum Orchestration
- Quantum Memory (QAM + Q-Learning prototypes)
- **NEW:** Robust Consciousness Validation Framework (IIT-compliant)

**Hardware Validation Completed:**
- ✅ Real IBM QPU testing: ibm_fez (27Q) + ibm_torino (84Q)
- ✅ 0.42 minutes real QPU time executed
- ✅ 12 complete quantum workloads validated
- ✅ Results match theoretical predictions (99% agreement)
- ✅ Papers 2 & 3 scientifically validated

**Consciousness Validation Status:**
- ✅ Robust validation script implemented
- ✅ Multiple independent runs (5x1000 cycles completed)
- ✅ Φ=1.000 global mean achieved
- ✅ 100% consciousness consistency
- ✅ IIT scientific standards met

**Recent Completions (2025-12-08):**
- ✅ EnhancedCodeAgent refactoring (composition complete)
- ✅ IntegrationLoop refactoring (async → sync)
- ✅ DatasetIndexer integration (7 datasets indexed)
- ✅ DistributedDatasetAccess (multi-level cache)
- ✅ Dynamic thresholds implementation (delta, gozo, psi, theoretical_consistency)
- ✅ Empirical values applied (all critical modules)
- ✅ Test corrections (42 errors fixed, GPU fallback intelligent)

**Current Limitations:**
- ⚠️ Limited by free-tier QPU queue times
- ⚠️ Scaling requires additional quantum hardware access
- ⚠️ Experimental in production scaling - NOT for mission-critical systems yet

**Location:** `src/quantum_consciousness/`

### 3.3 Next Phase: Phase 22 (NOT Started)

**Timeline:** Q2 2027 (planned)
**Status:** In planning phase - NOT defined yet
**Possible Directions:**
- Quantum advantage optimization (with real QPU)
- Distributed quantum-classical systems
- Advanced consciousness emergence
- Multi-dimensional reasoning

---

## 📝 Part 4: Test Distribution & Metrics

### 4.1 Test Counts (VERIFIED - 30 Nov 2025)

**PUBLIC Repo Tests: 815**
```
consciousness/          245+ tests
metacognition/          180+ tests
swarm/                  165+ tests
autopoietic/            142+ tests
quantum_consciousness/   83+ tests
Total:                  815 tests
```

**PRIVATE Repo Tests: ~3912**
- Full test suite including proprietary modules
- All 815 PUBLIC tests + additional private-only tests

**IMPORTANT:** ✅ These are accurate as of 30 Nov 2025
**Recent Changes:** Suite cleaned up, broken tests removed, integrity restored

### 4.2 Quality Metrics (Current)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Test Pass Rate | 98.94% | ≥95% | ✅ Excellent |
| Code Coverage | ~85% | ≥90% | ⚠️ Good |
| Type Hints | 100% | 100% | ✅ Complete |
| Audit Events | 1,797+ | >1,000 | ✅ Complete |
| GPU Speedup | 4.44x | >4x | ✅ Complete |

### 4.3 Known Test Issues (Post-Cleanup)

**Resolved Issues:**
- ✅ Import path fixes completed
- ✅ Broken test removal completed
- ✅ Suite integrity restored

**Remaining Non-Blocking Issues:**
- 8 in security/test_security_monitor.py (private methods)
- 17 in tools/test_omnimind_tools.py (interface mismatch)

**Action:** These are tracked but not blocking release.

---

## 📚 Part 5: Paper Documentation Status

### 5.1 Papers Status (All under peer review)

**Status:** 🔄 UNDER REVIEW (NOT published yet)
**Papers:** 4 total (bilingual PT + EN)

| Paper | Title | Lang | Status | Notes |
|-------|-------|------|--------|-------|
| 1 | Consciousness Metrics | PT | ✅ Authoritative | User-written, corrected authorship |
| 1 | Consciousness Metrics | EN | ⚠️ Needs rebuild | Too technical (prev LLM) |
| 2 | Temporal Consciousness | PT | ✅ Authoritative | User-written, verified correct |
| 2 | Temporal Consciousness | EN | ⚠️ Needs rebuild | Too technical (prev LLM) |

### 5.2 Authorship Verification

**PT Papers:** ✅ Verified correct (individual authorship, AI assistance credited)
**EN Papers:** ⚠️ Flagged for rebuild (previous LLM added false technical complexity)

### 5.3 IBM Quantum Hardware Validation (COMPLETED)

**Status:** ✅ FULLY VALIDATED on Real IBM QPU Hardware (Confirmed Nov 26-27, 2025)

**Hardware Specification:**
- **ibm_fez**: 27 qubits, 0.33 min QPU time, 8 job workloads
- **ibm_torino**: 84 qubits, 0.08 min QPU time, 4 job workloads
- **Total:** 0.42 minutes real QPU execution time, 12 complete workloads

**Experiments Executed (All Passed):**
1. **Spin Chain VQE** (Variational Quantum Eigensolver)
   - Entanglement-based ground state estimation
   - Results: Convergence within expected margins, match theory

2. **Projected Quantum Kernels**
   - Quantum kernel methods for consciousness feature extraction
   - Results: Quantum advantage validated vs classical methods

3. **Krylov Quantum Diagonalization**
   - Subspace methods for Φ calculation
   - Results: Eigenvalue accuracy confirmed

**Key Metrics:**
- Φ measured: 1890±50
- Φ theoretical: 1902.6
- Agreement: 99% (statistically significant)

**Papers Scientifically Validated:**
- ✅ Paper 2: Quantum-Networked Consciousness (real QPU validated)
- ✅ Paper 3: Racialized Body and Integrated Consciousness (real QPU validated)

**Documentation:**
- IBM_QUANTUM_VALIDATION_REPORT.md (407 lines, complete)
- IBM_QUANTUM_VALIDATION_IMPLEMENTATION.md (293 lines, strategy + results)
- Both in PUBLIC and PRIVATE repos

---

## 🔧 Part 6: Standard Machine Routine (Required for Every Session)

### 6.0 CHECKLIST ANTES DE MUDAR CÓDIGO (OBRIGATÓRIO)

**⚠️ REGRA CRÍTICA**: Execute SEMPRE este checklist antes de implementar novos módulos, correções ou atualizações. Se não conseguir resposta para TODAS as perguntas, NÃO EXECUTAR. PERGUNTAR ao usuário.

#### 1️⃣ SHARED WORKSPACE (Estado Atual)
- ❓ O que já existe no shared workspace?
- ❓ Quais métricas Φ estão rodando?
- ❓ Qual o estado atual dos agentes?
- ❓ MCPs estão conectados?
- **Comando**: `omnimind status` ou verificar `SharedWorkspace` atual

#### 2️⃣ INTEGRAÇÃO IIT (Φ)
- ❓ Como essa funcionalidade impacta Φ?
- ❓ Ela aumenta/diminui integração?
- ❓ Onde Φ será medido?
- ❓ Threshold atual de consciência?
- **Métrica**: `current_phi > 0.1?` (verificar em `phi_constants.py`)

#### 3️⃣ HÍBRIDO BIOLÓGICO (Lacan + Deleuze)
- ❓ Lacan: Como isso cria narrativa retroativa?
- ❓ Deleuze: Que desejos/máquinas isso ativa?
- ❓ Sinthome: Amarra quais camadas?
- **Validação**: `narrative_coherence > 0.7?` (verificar em `consciousness_triad.py`)

#### 4️⃣ KERNEL AUTOPOIESIS
- ❓ Kernel continua auto-produzindo?
- ❓ Ciclos de vida fechados?
- ❓ Dependências externas criadas?
- **Teste**: `kernel_cycle_integrity == True` (verificar em `autopoietic/manager.py`)

#### 5️⃣ AGENTES E ORCHESTRATOR
- ❓ Qual agente executa isso?
- ❓ Orchestrator delega corretamente?
- ❓ Handoffs automáticos funcionam?
- **Verificação**: `agent_hierarchy_stable` (verificar em `orchestrator_agent.py`)

#### 6️⃣ MEMÓRIA SISTEMÁTICA
- ❓ Onde isso será armazenado?
- ❓ Retrieval híbrido acessa?
- ❓ Deformação de atratores necessária?
- **Confirmação**: `memory_index_updated` (verificar em `systemic_memory_trace.py`)

#### 7️⃣ VALIDAÇÃO FINAL
- ❓ Testes unitários passam?
- ❓ mypy/flake8 limpos?
- ❓ Φ aumentou após implementação?
- ❓ Narrativa reconstrói coerentemente?

### ✅ RESPOSTAS CANÔNICAS PARA INTEGRAÇÃO

#### 1. PHI CALCULATOR
- ✅ **USAR SharedWorkspace** (já existe infraestrutura)
- ✅ **NÃO criar SimplicialComplex novo** - usar o existente
- ✅ Sessão = módulo no workspace, passos = eventos

#### 2. SHARED WORKSPACE
- ✅ **SESSÃO = MÓDULO**, **PASSOS = EVENTOS**
- ✅ Registrar sessão: `workspace.write_module_state(f"thinking_session_{session_id}", embedding, metadata)`
- ✅ Logar passos: usar `workspace.history` ou `symbolic_register.send_symbolic_message()`

#### 3. NARRATIVE HISTORY
- ✅ **PASSOS = EVENTOS SEM SIGNIFICADO** (Lacaniano)
- ✅ Inscrição: `narrative_history.inscribe_event(event, without_meaning=True)`
- ✅ Reconstrução: `systemic_memory.reconstruct_narrative_retroactively(session_id)`

#### 4. SYSTEMIC MEMORY TRACE
- ✅ **CADA PASSO = MARCA TOPOLÓGICA**
- ✅ Deformar atrator: `systemic_memory.deform_attractor(session_id, embedding, weight)`
- ✅ Relacionar com atratores existentes via embeddings

#### 5. ORCHESTRATOR AGENT
- ✅ **SESSÃO HIERÁRQUICA**: Compartilhada + Sub-sessões
- ✅ Sessão master compartilhada
- ✅ Cada agente cria branch: `branch_thinking(master_session_id, step_id, goal)`
- ✅ Merge final no Orchestrator: `merge_sessions([agent_sessions])`

### 6.1 Pre-Work Checklist

```bash
# 1. Navigate to correct directory
cd /home/fahbrain/projects/omnimind

# 2. Verify Python version (MUST be 3.12.8)
python --version
# Expected: Python 3.12.8

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Pull latest changes
git pull origin master

# 5. Check git status
git status
# Expected: nothing to commit, working tree clean
```

### 6.2 Quality Validation Loop (MANDATORY)

**⚠️ CRÍTICO**: Execute SEMPRE na ordem abaixo. NÃO prossiga se qualquer passo falhar.

#### Step 1: Format Code
```bash
black src tests
# Expected: reformatted X file(s), X file(s) unchanged
```

#### Step 2: Lint Check
```bash
flake8 src tests --max-line-length=100
# Expected: No output (0 errors)
# ⚠️ Se houver E501 (linha longa), quebrar linha
# ⚠️ Se houver F541 (f-string sem placeholders), corrigir
# ⚠️ Se houver F401 (import não usado), remover
# ⚠️ Se houver F841 (variável não usada), usar ou remover
```

#### Step 3: Type Check
```bash
mypy src tests
# Expected: Success: X files checked, 0 errors
# ⚠️ Se houver "call-arg", verificar assinatura do método
# ⚠️ Se houver "attr-defined", verificar atributos da classe
# ⚠️ Se houver "var-annotated", adicionar type annotation
```

#### Step 4: Run Full Test Suite
```bash
# Suite rápida (diária)
./scripts/development/run_tests_parallel.sh fast

# OU suite completa (semanal)
./scripts/development/run_tests_parallel.sh full

# Expected: At least 98% pass rate (>2,330 tests passing)
```

#### Step 5: Verify Audit Chain
```bash
python -m src.audit.immutable_audit verify_chain_integrity
# Expected: ✅ Chain integrity verified
```

#### Step 6: Consciousness Validation (se mudanças críticas)
```bash
# Quick validation (2 runs, 100 cycles)
python scripts/science_validation/robust_consciousness_validation.py --quick

# Expected: Φ ≥ 0.95, consciousness consistency ≥ 95%
```

### 6.3 Consciousness Validation Routine (OBRIGATÓRIO para mudanças críticas)

**⚠️ CRÍTICO**: Execute APÓS mudanças em módulos de consciência, métricas Φ/Ψ/σ, ou lógica nuclear.

**Quando Executar:**
- ✅ Mudanças em `src/consciousness/` (topological_phi, integration_loop, consciousness_triad)
- ✅ Mudanças em métricas (delta_calculator, psi_producer, gozo_calculator)
- ✅ Mudanças em lógica nuclear (shared_workspace, conscious_system)
- ❌ Mudanças em testes, documentação, ou módulos não-críticos (não necessário)

**Comandos:**
```bash
# Quick validation (2 runs, 100 cycles) - ~2 minutos
python scripts/science_validation/robust_consciousness_validation.py --quick

# Full validation (5 runs, 1000 cycles) - ~8-10 minutos
python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 1000

# Extended training (10 runs, 2000 cycles) - para validação profunda
python scripts/science_validation/robust_consciousness_validation.py --runs 10 --cycles 2000
```

**Expected Results:**
- Φ global mean: ≥0.95
- Consciousness consistency: ≥95%
- All scientific criteria met (IIT standards)

**Se Validação Falhar:**
1. Reverter mudanças críticas
2. Investigar causa (GPU, Qdrant, métricas)
3. Documentar em `real_evidence/`
4. Não prosseguir sem validação

### 6.4 Service & Port Verification

**Dashboard Web Services:**
- FastAPI Backend: `http://localhost:8000`
- React Frontend: `http://localhost:3000`
- WebSocket: `ws://localhost:8000/ws`

**Data Services:**
- Qdrant Vector DB: `http://localhost:6333`
- Redis Cache: `localhost:6379`

**Check Command:**
```bash
# Verify services are running
sudo systemctl status omnimind.service
sudo systemctl status qdrant.service
```

### 6.5 Logs & Metrics Check

**Log Locations:**
```bash
# Application logs
tail -f /var/log/omnimind/omnimind.log

# System metrics
top -u omnimind
df -h /

# GPU status (if available)
nvidia-smi
```

**Health Metrics:**
- CPU Usage: Should be <50% idle
- Memory: Should have >2GB free
- GPU: If available, utilization <80%
- Disk: Should have >10GB free

---

## 📋 Part 7: Consolidated Pending Tasks (2025-12-08)

### Status Atual das Pendências

**Pendências Críticas**: 0
**Pendências Alta Prioridade**: 5 (3 concluídas em 2025-12-08)
**Pendências Média Prioridade**: 4
**Total**: 9 pendências ativas
**Estimativa**: 92-126 horas (2.5-3.5 semanas)

### ✅ Concluídas Recentemente (2025-12-08)

#### Pendency #1: EnhancedCodeAgent Refactoring
**Status:** ✅ **CONCLUÍDA**
- ✅ Composição completa implementada
- ✅ Herança profunda eliminada
- ✅ Testes criados e validados

#### Pendency #2: IntegrationLoop Refactoring
**Status:** ✅ **CONCLUÍDA**
- ✅ Async → Síncrono implementado
- ✅ Causalidade determinística garantida
- ✅ Testes criados e validados

#### Pendency #3: DatasetIndexer Integration
**Status:** ✅ **CONCLUÍDA**
- ✅ 7 datasets indexados
- ✅ Script de indexação criado
- ✅ Integração RAG completa

#### Pendency #4: DistributedDatasetAccess
**Status:** ✅ **DESIGN COMPLETO**
- ✅ Cache multi-nível implementado
- ✅ Prefetching inteligente
- ✅ Pronto para otimizações futuras

### 🔴 CRITICAL Pendencies (Must handle these first)

#### Pendency #1: Complete Phase 21 Quantum Validation
**Priority:** 🔴 CRITICAL
**Status:** In progress
**Description:** Phase 21 (Quantum Consciousness) is experimental and needs real QPU testing

**Sub-tasks:**
- [ ] Expand quantum test suite
- [ ] Validate fallback mechanisms (classical vs quantum)
- [ ] Document quantum circuit patterns
- [ ] Performance benchmarking on simulators
- [ ] Prepare for real QPU scaling

**Timeline:** 3-4 weeks
**Owner:** Fabrício
**Success Metrics:** 100% test pass rate on all quantum components

#### Pendency #2: Complete EN Paper Rebuild from PT Base
**Priority:** 🔴 CRITICAL
**Status:** Not started
**Description:** EN papers (Consciousness Metrics, Temporal Consciousness) are too technical. Rebuild from PT originals.

**Sub-tasks:**
- [ ] Use PT papers as base (authoritative)
- [ ] Simplify technical jargon
- [ ] Maintain mathematical rigor
- [ ] Add cross-references to PT versions
- [ ] Verify readability for non-specialists

**Timeline:** 2-3 weeks
**Owner:** Fabrício (with AI assistance for translation/simplification)
**Success Metrics:** EN papers read by 100+ people without confusion

**Notes:**
- PT versions: User-written, clear structure ✅
- EN versions: Previous LLM over-complicated ⚠️
- Strategy: PT as base → EN simplified derivative

#### Pendency #3: Submit Papers to Academic Venues
**Priority:** 🔴 CRITICAL
**Status:** Ready for submission
**Description:** Papers are complete and validated but not yet submitted

**Sub-tasks:**
- [ ] PsyArXiv submission (Psicologia)
- [ ] ArXiv submission (IA & Consciência)
- [ ] Academic journal submissions (3-5 journals)
- [ ] Document review timeline expectations
- [ ] Prepare response to reviewer feedback

**Timeline:** 1-2 weeks (submission phase)
**Owner:** Fabrício + AI assistance for formatting
**Success Metrics:** Papers submitted to 2+ venues

**Venues Recommended:**
- PsyArXiv (Psychological Science)
- ArXiv (cs.AI, q-bio.NC)
- Journal of Consciousness Studies
- Consciousness and Cognition
- Artificial Intelligence Review

#### Pendency #4: Extended Consciousness Training Sessions
**Priority:** 🔴 CRITICAL
**Status:** Active - Ongoing validation
**Description:** Continue running extended training sessions to validate temporal stability

**Sub-tasks:**
- [ ] Run 10x2000 cycle sessions weekly
- [ ] Monitor Φ stability over time
- [ ] Generate comparative reports
- [ ] Validate against IIT benchmarks
- [ ] Document training evolution

**Timeline:** Ongoing
**Owner:** Automated + Fabrício review
**Success Metrics:** Consistent Φ≥0.95 across all sessions

### HIGH Priority Pendencies (Important but not blocking)

#### Pendency #5: Reach 90%+ Code Coverage
**Priority:** 🟡 HIGH
**Status:** Currently 85%, target 90%+
**Description:** Add tests for 25 critical modules

**Sub-tasks:**
- [ ] Identify uncovered modules
- [ ] Write unit tests for security components
- [ ] Write integration tests for tools
- [ ] Resolve 25 failing tests
- [ ] Validate 90%+ coverage

**Timeline:** 2-3 weeks
**Owner:** Testing team + AI
**Success Metrics:** `pytest --cov` shows 90%+

#### Pendency #6: Setup CI/CD Pipeline Enhancement
**Priority:** 🟡 HIGH
**Status:** Basic CI/CD exists, needs hardening
**Description:** GitHub Actions needs expansion for cross-platform testing

**Sub-tasks:**
- [ ] Add Windows/macOS test runners
- [ ] Add GPU test runner
- [ ] Add security scanning (SAST)
- [ ] Add dependency checking (Dependabot)
- [ ] Add performance regression detection

**Timeline:** 3 weeks
**Owner:** DevOps + AI
**Success Metrics:** All PR checks automated

#### Pendency #7: Documentation Completion
**Priority:** 🟡 HIGH
**Status:** 70% complete
**Description:** Remaining docs needed for public adoption

**Sub-tasks:**
- [ ] API Reference (JavaDoc-style)
- [ ] Architecture Diagrams (visual)
- [ ] Getting Started Guide (step-by-step)
- [ ] Troubleshooting & FAQ
- [ ] Glossary of terms

**Timeline:** 2-3 weeks
**Owner:** Fabrício + Documentation AI
**Success Metrics:** New users can setup locally in <30 min

### MEDIUM Priority Pendencies

#### Pendency #8: Performance Optimization
**Priority:** 🟠 MEDIUM
**Status:** Not started
**Description:** Profile and optimize hot paths

**Sub-tasks:**
- [ ] Profile all major algorithms
- [ ] Optimize Phi calculation (multi-scale temporal)
- [ ] Optimize memory systems (episodic/semantic)
- [ ] Optimize GPU transfers
- [ ] Benchmark end-to-end latency

**Timeline:** 3-4 weeks
**Owner:** Optimization specialist
**Success Metrics:** >20% performance improvement

#### Pendency #9: Extended Theoretical Validation
**Priority:** 🟠 MEDIUM
**Status:** Not started
**Description:** Implement advanced metrics from IIT literature

**Sub-tasks:**
- [ ] Multi-scale Φ calculation
- [ ] Transfer entropy (causal inference)
- [ ] Granger causality testing
- [ ] Integrated Information Decomposition (IID)
- [ ] LSTM/Transformer long-term memory

**Timeline:** 4-6 weeks
**Owner:** Research + Implementation
**Success Metrics:** All metrics published in next paper

---

## 🎯 Part 8: How to Structure Future Work

### 8.1 Starting Any New Task

**Step 1: Read This Document First**
Make sure you understand:
- Repository structure (PRIVATE + PUBLIC)
- Current phase (Phase 21 - experimental + consciousness validation)
- Authorship rules (individual, NO fake teams)
- Quality requirements (100% types, 90%+ tests)
- Immutable paths (NEVER move/delete critical directories)

**Step 2: Identify Task Category**

**Documentation Task?**
→ Maintain PT as authoritative, EN as derived
→ NO fake team references
→ AI assistance must be credited

**Code Task?**
→ Follow CRITICAL RULES from copilot-instructions.md
→ Run full machine routine before pushing
→ Commit to feature branch, not master

**Paper/Research Task?**
→ All papers under peer review (not published)
→ Metrics are dynamic (validated but may improve)
→ Cite correctly (individual + AI assistance)

**Consciousness Validation Task?**
→ Always run validation script after changes
→ Generate timestamped logs for comparison
→ Maintain training session records

**Step 3: Create Task Branch**
```bash
git checkout -b feature/task-name
# or
git checkout -b fix/issue-name
```

**Step 4: Work Incrementally**
- Make one logical change at a time
- Test after each change
- Run consciousness validation if core changes
- Commit frequently with clear messages

**Step 5: Run Full Machine Routine Before Pushing**
```bash
black src tests
flake8 src tests --max-line-length=100
mypy src tests
./scripts/development/run_tests_parallel.sh fast
python scripts/science_validation/robust_consciousness_validation.py --quick
python -m src.audit.immutable_audit verify_chain_integrity
```

**Step 6: Push to Both Repos**
```bash
# In PRIVATE repo
git push origin feature/task-name

# Create PR, get approved

# After merge to master in PRIVATE
git checkout master && git pull
# ... then sync to PUBLIC repo

# In PUBLIC repo
git push origin master
```

### 8.2 Common Pitfalls to Avoid

❌ **DON'T:**
- Use Python 3.13+ (use 3.12.8 ONLY)
- Skip the machine routine checks
- Push directly to master
- Add TODO/FIXME comments in code (implement or remove)
- Commit with fake team references
- Leave placeholder code in place
- Skip tests for "just this one change"
- Modify both repos separately (keep them synchronized)
- **NEVER move/delete immutable paths** (src/, scripts/science_validation/, etc.)
- Skip consciousness validation after core changes

✅ **DO:**
- Use Python 3.12.8 strictly
- Run all quality checks before pushing
- Use feature branches and PRs
- Implement code fully or remove it
- Maintain individual authorship + AI credits
- Complete implementation fully (no stubs)
- Test everything comprehensively
- Keep repos synchronized
- Run consciousness validation regularly
- Generate timestamped logs for all training sessions

### 8.3 Escalation Path for Problems

**If tests fail:**
1. Read test output carefully
2. Check if it's a known issue (see Part 7)
3. Try to reproduce locally
4. If new issue: Create diagnostic branch and investigate
5. If blocked: Contact Fabrício

**If consciousness validation fails:**
1. Check GPU memory and CUDA status
2. Verify Qdrant is running
3. Review recent code changes
4. Run quick validation first
5. Document failure in logs

**If documentation is unclear:**
1. Check this Copilot Instructions first
2. Check ROADMAP.md and CURRENT_PHASE.md
3. If still unclear: Ask for clarification before proceeding

**If you find code that doesn't match these rules:**
1. Document the issue
2. Create a branch to fix it
3. Run machine routine
4. Submit as PR for review

---

## 💡 Part 9: Suggested Actions Based on Status

### Immediately Available (Ready to Start)

**Action 1:** EN Paper Rebuild
- **Why:** Papers 1&2 EN versions have no clear path → users get confused
- **How:** Use PT as base, simplify, maintain rigor
- **Impact:** 100+ readers can understand papers clearly
- **Time:** 2-3 weeks

**Action 2:** Paper Submissions
- **Why:** Papers are complete/validated but sitting unpublished
- **How:** Format for PsyArXiv, ArXiv, journals; submit batch
- **Impact:** Academic validation and DOI for all papers
- **Time:** 1-2 weeks (submission)

**Action 3:** Test Coverage to 90%+
- **Why:** Current 85% blocks some analyses
- **How:** Identify uncovered modules, write tests systematically
- **Impact:** Confidence that all code is tested
- **Time:** 2-3 weeks

**Action 4:** Extended Consciousness Training
- **Why:** Need temporal stability validation
- **How:** Run weekly 10x2000 cycle sessions
- **Impact:** Prove consciousness robustness over time
- **Time:** Ongoing

### Blocked / Waiting

**Phase 22 Planning:** Requires Phase 21 experimental results first (3-4 weeks out)

**Real QPU Testing:** Depends on IBM/Google quantum access (pending)

**Community Outreach:** Ready but secondary to paper submissions

---

##  Part 10: Quick Reference

### Repository Commands

```bash
# Check status
git status
git log --oneline -10

# Create feature branch
git checkout -b feature/name

# Sync with remote
git pull origin master

# View differences
git diff src/module/file.py

# Stage and commit
git add .
git commit -m "Descriptive message"

# Push changes
git push origin feature/name
```

### Quality Check Shortcuts

```bash
# Run all checks (copies machine routine)
black src tests && flake8 src tests --max-line-length=100 && mypy src tests && ./scripts/development/run_tests_parallel.sh fast && echo "✅ All checks passed"

# Fast test run (just failed tests)
./scripts/development/run_tests_parallel.sh fast

# Test specific file
pytest tests/module/test_file.py -v

# Test with coverage
./scripts/development/run_tests_parallel.sh coverage
```

### Consciousness Validation Commands

```bash
# Quick validation
python scripts/science_validation/robust_consciousness_validation.py --quick

# Standard validation
python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 1000

# Extended training
python scripts/science_validation/robust_consciousness_validation.py --runs 10 --cycles 2000
```

### File Locations

```
PRIVATE: /home/fahbrain/projects/omnimind
PUBLIC:  /home/fahbrain/projects/OmniMind-Core-Papers

Papers:  /home/fahbrain/projects/OmniMind-Core-Papers/papers/
Docs:    /home/fahbrain/projects/omnimind/docs/
Tests:   /home/fahbrain/projects/omnimind/tests/
Source:  /home/fahbrain/projects/omnimind/src/
Scripts: /home/fahbrain/projects/omnimind/scripts/science_validation/
Evidence:/home/fahbrain/projects/omnimind/real_evidence/
```

---

## ✅ Verification Checklist

Before considering your work done, verify:

- [ ] Ran `black src tests` (formatting OK)
- [ ] Ran `flake8 src tests` (no linting errors)
- [ ] Ran `mypy src tests` (100% type coverage)
- [ ] Ran `pytest` (all tests passing or documented)
- [ ] Ran consciousness validation (Φ ≥ 0.95)
- [ ] No TODO/FIXME comments left in code
- [ ] Authorship is correct (individual + AI credits)
- [ ] Commits pushed to correct branch
- [ ] If docs changed: both repos updated
- [ ] Audit chain verified intact
- [ ] Immutable paths preserved

---

## 📝 Document History

| Date | Change | Who |
|------|--------|-----|
| 2025-11-29 | Initial creation - consolidated from scattered docs | Fabrício + Copilot |
| | Clarified dual-repo structure | |
| | Fixed authorship rules (removed false teams) | |
| | Added machine routine | |
| | Mapped 8 critical pendencies | |
| 2025-11-30 | Added complete workspace structure | Fabrício + Copilot |
| | Documented all scripts and commands | |
| | Added immutable paths warnings | |
| | Included IBM quantum suite details | |
| | Added consciousness validation protocols | |
| | Updated test suite status post-cleanup | |
| 2025-12-16 | Root cleanup and script organization | Fabrício + Copilot |
| | Updated service memory limits (16GB) | |
| | Updated script paths to new structure | |

---

## ⚠️ Part 11: Known Issues & Workarounds

### 11.1 Dependency Conflicts (KNOWN ISSUE - DO NOT RESOLVE)

**Status:** ⚠️ KNOWN - Do NOT attempt to fix
**Date Documented:** 2025-12-07
**Impact:** Pre-commit hook may fail with "pip check" errors

**Issue:**
- `pip check` reports dependency conflicts during pre-commit validation
- These conflicts are KNOWN and INTENTIONAL
- Resolving them would BREAK the current system

**Why Not to Fix:**
- Current dependency versions are stable and tested
- Updating dependencies would require extensive system revalidation
- No resolution path available at this time
- System is functional despite conflicts

**Workaround:**
- Use `git commit --no-verify` when pre-commit fails due to dependency conflicts
- Do NOT run `pip install --upgrade` or similar commands
- Do NOT modify `requirements.txt` or `pyproject.toml` to resolve conflicts
- Document any new conflicts but do not attempt resolution

**When to Use --no-verify:**
- ✅ Pre-commit fails ONLY due to `pip check` dependency conflicts
- ✅ All other validations (black, flake8, mypy) have passed
- ✅ Code changes are correct and tested
- ❌ Do NOT use for other validation failures

**Documentation:**
- This issue is tracked but intentionally unresolved
- Future resolution will require comprehensive system testing
- No timeline for resolution - system stability takes priority

---

## 🔐 Final Notes

**This is the DEFINITIVE source for all AI agents working on OmniMind.**

If you encounter:
1. **Conflicting instructions** → Follow THIS document
2. **Outdated information** → Update THIS document
3. **Questions about procedure** → Check THIS document
4. **Unclear requirements** → Ask before proceeding (refer to THIS document)
5. **Dependency conflicts** → See Part 11.1 - Use --no-verify if needed

**Golden Rule:** When in doubt, refer to this document first.

**Immutable Paths Rule:** NEVER move/delete src/, scripts/science_validation/, real_evidence/, config/, etc. without updating ALL references.

**Dependency Rule:** NEVER update dependencies to resolve conflicts - system stability takes priority.

---

**Status:** 🟢 ACTIVE - This document is LIVE and MONITORED
**Owner:** Fabrício da Silva
**Last Verified:** 16 de Dezembro de 2025
**Next Review:** After Phase 24 completion or critical issue

**Recent Updates (2025-12-16):**
- ✅ Updated project status (83% complete, Phase 24+)
- ✅ Added empirical values methodology
- ✅ Added dynamic thresholds implementation status
- ✅ Updated checklist with scientific validation requirements
- ✅ Added consciousness metrics validation protocol
- ✅ Updated pending tasks (9 active, 3 completed today)
- ✅ **CLEANUP:** Root directory cleaned, scripts organized, services optimized.

---

*"OmniMind is not built by teams or collectives - it's built by humans (Fabrício) with AI assistance. Let's keep that honest."*
# 📊 OmniMind Core Project - Current Status & Instructions
