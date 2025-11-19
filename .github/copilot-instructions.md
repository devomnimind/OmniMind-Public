# 🧠 Projeto OmniMind - Instruções GitHub Copilot (Consolidado v4.0)

**Data:** 2025-11-19
**Status:** Phase 12 Multi-Modal Intelligence Complete
**Hardware:** Auto-detectado (Intel i5 10ª geração + GTX 1650 4GB + 24GB RAM)
**Destino:** Agente Copilot Remoto (GitHub Codespaces/GitPod)
**Projeto:** /home/fahbrain/projects/omnimind/
---

## 📋 CRÍTICO: Leia o Módulo de Segurança Primeiro

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

# Verify module is loaded
lsmod | grep nvidia_uvm

# Test CUDA again
python -c "import torch; print(torch.cuda.is_available())"
```

**Resultado Esperado:** `torch.cuda.is_available()` deve retornar `True`

**Nota:** Corrupção do módulo do kernel nvidia_uvm normalmente ocorre após suspensão/hibernação do sistema no Linux. O procedimento de recarregamento restaura o acesso à GPU imediatamente.

**Solution 2: Verify System CUDA Installation**
```bash
# Check NVIDIA driver
nvidia-smi

# Verify CUDA toolkit installed
nvcc --version

# Expected output should show CUDA 12.4.x
```

**Solution 3: Update System Library Cache**
```bash
# Rebuild ldconfig cache for NVIDIA libraries
sudo ldconfig

# Verify cuDNN found
ldconfig -p | grep cudnn
```

### GPU Performance Baseline (Phase 7 Validation)

**Validated Performance on GTX 1650:**
- CPU Throughput: 253.21 GFLOPS (5000x5000 matrix multiply)
- GPU Throughput: 1149.91 GFLOPS (5000x5000 matrix multiply)
- Memory Bandwidth: 12.67 GB/s
- Acceleration Factor: **4.5x GPU vs CPU**
- PyTorch Version: 2.6.0+cu124
- Status: ✅ VERIFIED Nov 18, 2025

**Benchmark Script:** `python PHASE7_COMPLETE_BENCHMARK_AUDIT.py` (generates JSON report to `logs/`)

### GPU Memory Constraints

**GTX 1650 VRAM: 3.81GB Total**
- Large Language Model: ~2.5GB (Qwen2-7B-Instruct quantized)
- Agent Operations: ~800MB (embeddings, inference buffers)
- Available for User Data: ~500MB max
- **Important:** Batch sizes must be limited to avoid OOM errors

**Tensor Operation Sizing:**
```python
# Safe: Processes without GPU memory exhaustion
max_matrix_size = 5000  # 5000x5000 matrix = ~190MB on GPU

# Unsafe: Will cause OOM on GTX 1650
unsafe_matrix_size = 10000  # 10000x10000 matrix = ~760MB on GPU (leaves no overhead)
```

### Integration Validation

**After GPU setup, verify complete stack:**
```bash
# 1. Verify Python + environment
python --version
echo $VIRTUAL_ENV

# 2. Verify PyTorch GPU
python -c "import torch; assert torch.cuda.is_available(), 'CUDA NOT AVAILABLE'"

# 3. Run audit tests
pytest tests/test_audit.py -v --cov=src.audit

# Expected: 14/14 tests passing, ≥60% coverage

# 4. Run GPU benchmark
python PHASE7_COMPLETE_BENCHMARK_AUDIT.py

# Expected: All benchmarks complete, JSON report generated to logs/
```

### Documentation References

**For detailed Phase 7 GPU/CUDA repair history and troubleshooting:**
- `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md` - Technical deep dive (500+ lines)
- `GPU_CUDA_REPAIR_AUDIT_COMPLETE.md` - Executive summary and sign-off
- `PHASE7_COMPLETE_BENCHMARK_AUDIT.py` - Automated validation script

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

---

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

## 📊 CURRENT STATUS (Phase 9 Core Complete)

### ✅ Implemented Components (Phase 9 Complete - 202 Tests Passing)

| Component | Lines | Status | Tests | Coverage |
|-----------|-------|--------|-------|----------|
| **Frontend (React + TS)** | 1,500+ | ✅ Complete | 0 | UI Testing |
| **Backend (FastAPI + WS)** | 2,000+ | ✅ Complete | 31 | 100% |
| **Metacognition Engine** | 1,500+ | ✅ Complete | 31 | 100% |
| **Multi-Agent System** | 1,200+ | ✅ Complete | 40+ | 95% |
| **Security Framework** | 800+ | ✅ Complete | 25+ | 98% |
| **Ethics Engine** | 563 | ✅ Complete | 6 | 100% |
| **WebSocket Manager** | 232 | ✅ Complete | 15 | 100% |
| **Integration Tests** | 470+ | ✅ Complete | 31 | 100% |

**Total Lines:** 8,500+ (Phases 1-9)
**Integration Tests:** 31/31 passing (100%)
**Unit Tests:** 171/171 passing (100%)
**End-to-End Tests:** 3/3 passing (100%)

### 🏗️ Architecture Overview (Phase 9 Complete)

```
🧠 OmniMind Autonomous System (Phase 9)
│
├── 🎨 Frontend Layer (React + TypeScript)
│   ├── Real-time WebSocket Dashboard
│   ├── Task Orchestration Interface
│   ├── Agent Status Monitoring
│   └── Ethics Decision Visualization
│
├── ⚙️ Backend Layer (FastAPI + WebSocket)
│   ├── REST APIs (Tasks, Agents, Security, Metacognition)
│   ├── Real-time WebSocket Server
│   ├── Multi-agent Orchestration Engine
│   └── Production Deployment (systemd ready)
│
├── 🧠 Metacognition Engine (Self-Aware AI)
│   ├── Self-Analysis & Pattern Recognition
│   ├── Proactive Goal Generation
│   ├── Homeostasis & Resource Management
│   └── Continuous Self-Optimization
│
├── 🤖 Multi-Agent Orchestration (Psychoanalytic)
│   ├── OrchestratorAgent → Freudian/Lacanian delegation
│   ├── SecurityAgent → Forensic monitoring
│   ├── EthicsAgent → 4-methodology decision framework
│   └── PsychoanalyticAnalyst → Session analysis (4 frameworks)
│
├── 🛡️ Security & Compliance (Enterprise-Grade)
│   ├── Immutable Audit Trails (SHA-256 hash chains)
│   ├── LGPD Compliance (Brazilian data protection)
│   ├── Zero-Trust Architecture
│   ├── Real-time Threat Detection
│   └── Forensic Analysis Tools
│
└── 🔧 System Integration (Production Ready)
    ├── MCP Client Async (enhanced reliability)
    ├── D-Bus Hardware Monitoring
    ├── Systemd Service Management
    └── Hardware Auto-Detection & Optimization
```

### 📈 Performance Metrics (Phase 9 Complete)

| Component | Metric | Value | Rating |
|-----------|--------|-------|--------|
| **Frontend** | Bundle Size | 190KB gzipped | ✅ EXCELLENT |
| **WebSocket** | Real-time Latency | <100ms | ✅ EXCELLENT |
| **Backend APIs** | Response Time | <50ms | ✅ EXCELLENT |
| **Metacognition** | Self-Analysis | <2s | ✅ EXCELLENT |
| **Multi-Agent** | Task Delegation | <500ms | ✅ EXCELLENT |
| **Security** | Audit Verification | <1ms | ✅ EXCELLENT |
| **Ethics Engine** | Decision Time | <100ms | ✅ EXCELLENT |
| **System Tests** | Full Suite | 202 tests | ✅ 100% PASSING |

### ♻️ Nov 18 Maintenance Snapshot

- `.gitignore` + `config/backup_excludes.txt` bloqueiam loops `guardian/backups/**/guardian/backups/` e snapshots contaminados (`data/hdd_snapshot/`, `data/quarantine_snapshot/`).
- `docs/servers.txt` e `docs/reports/omnimind_state_vs_devbrain.md` foram atualizados para usar apenas variáveis de ambiente e documentar os módulos recuperados em `DEVBRAIN_V23/` como **referência read-only**.
- `logs/audit_chain.log` e `logs/hash_chain.json` foram reprocessados (Nov 18) para remover a Supabase Service Key — rodar `python -m src.audit.immutable_audit verify_chain_integrity` após qualquer sanitização.
- Inventários externos (`docs/reports/external_hdd_dataset_inventory.md`, `dev_brain_clean_setup.md`) e os diretórios `tmp_agents/`, `tmp_tools/` fazem parte da rotina diária de pré-flight.

### 🚧 Outstanding Hardening (before Phase 7 GA)

1. Ligar `SecurityAgent` como guardião assíncrono (process/network/file/log) e validar `tests/test_security_phase7.py`.
2. Integrar `PsychoanalyticAnalyst` + workflow Code→Review→Fix→Document com iterações RLAIF ≥ 8.0.
3. Migrar ferramentas de filesystem para `src/integrations/mcp_client.py` e bloquear acessos diretos antes do bootstrap do D-Bus/Web UI.

---

## 🎯 PHASE 7: Security Integration & Advanced Workflows

### Primary Objectives

1. **Integrate Security Module** (CRITICAL P0)
   - Merge `SecurityAgent` from security forensics module
   - Implement 4-layer monitoring (processes, files, network, logs)
   - Integrate threat detection playbooks
   - Auto-response system with isolation capabilities

2. **Implement Advanced Workflows**
   - Code → Review → Fix → Document (RLAIF loop)
   - Iterative improvement until score >= 8.0
   - Multi-agent coordination validation

3. **Psychoanalytic Analyst Integration**
   - Merge `PsychoanalyticAnalyst` framework
   - Implement Freudian/Lacanian analysis modes
   - Clinical session analysis capabilities
   - ABNT-compliant report generation

### Security Module Integration Plan

#### Step 1: Security Agent Core (Priority: CRITICAL)
```python
# Location: src/security/security_agent.py
class SecurityAgent:
    """
    4-Layer Monitoring:
    1. Process monitoring (suspicious names/behaviors)
    2. Network monitoring (suspicious ports/connections)
    3. File integrity (AIDE integration)
    4. Log analysis (auditd events)
    
    Auto-Response:
    - Kill suspicious processes
    - Block malicious IPs (UFW)
    - Isolate compromised files
    - Generate forensic reports
    """
```

**Integration Points:**
- Hook into `OrchestratorAgent` for security checks before delegation
- Add `security_audit` tool to `ToolsFramework`
- Integrate with `AuditChain` for tamper detection
- Real-time monitoring via asyncio background task

#### Step 2: Forensic Tools Setup (Priority: HIGH)
```bash
# Location: scripts/omnimind_security_install.sh
# Already prepared in security module:
- auditd + audispd-plugins
- AIDE (file integrity)
- chkrootkit + rkhunter (rootkit detection)
- fail2ban + UFW (auto-response)
- ClamAV (malware scanning)
```

#### Step 3: Security Baseline & Monitoring (Priority: HIGH)
```python
# Location: src/security/omnimind_security_monitor.py
# Continuous monitoring loop:
- Process scanning every 30s
- Network connection monitoring
- Failed login attempts
- System resource anomalies (CPU/Memory >80%)
- Generate alerts and reports
```

### Psychoanalytic Framework Integration

#### PsychoanalyticAnalyst Module
```python
# Location: src/agents/psychoanalytic_analyst.py
class PsychoanalyticAnalyst:
    """
    Frameworks: Freudian, Lacanian, Kleinian, Winnicottian
    
    Techniques:
    - Evenly suspended attention (escuta flutuante)
    - Interpretive hypothesis formation
    - Resistance identification
    - Clinical session analysis
    - ABNT report generation
    """
```

**Use Cases:**
1. Analyze user interaction patterns (transference/countertransference detection)
2. Clinical session note processing for psychoanalysts
3. Pattern recognition in symptom descriptions
4. Generate structured clinical reports

---

## 🎯 PHASE 8: Production Deployment & MCP Integration

### Primary Objectives

1. **MCP (Model Context Protocol) Real Integration**
   - Replace direct filesystem access with MCP protocol
   - Enhanced security through protocol-level isolation
   - Implement `MCPToolTool` with actual client

2. **D-Bus System Integration**
   - SessionBus: Control desktop apps (VLC, Spotify, file managers)
   - SystemBus: Hardware events (network, power, mount/unmount)

3. **Web UI Dashboard**
   - FastAPI + WebSocket + React
   - Real-time workflow visualization
   - Task submission interface
   - Performance metrics dashboard
   - Audit log browser

4. **Systemd Service**
   - Auto-start on boot
   - Process management
   - Log rotation
   - Health checks

### MCP Integration Details

```python
# Location: src/integrations/mcp_client.py
class MCPClient:
    """
    Model Context Protocol client for secure filesystem ops
    
    Features:
    - Protocol-based file access (not direct)
    - Audit trail at protocol level
    - Path validation before MCP call
    - JSON-RPC communication
    """
    
    def read_file(self, path: str) -> str:
        # Validate path → MCP call → Audit log
        
    def write_file(self, path: str, content: str):
        # Validate → MCP call → Hash → Audit
```

### D-Bus Integration

```python
# Location: src/integrations/dbus_controller.py
class DBusSessionController:
    """Control desktop applications via SessionBus"""
    def control_media_player(self, action: str):
        # Play/Pause VLC, Spotify, etc.
        
class DBusSystemController:
    """Monitor system events via SystemBus"""
    def get_network_status(self) -> dict:
        # Network connection state
```

### Web UI Architecture

```
Frontend (React + TypeScript)
├── Task Submission Form
├── Workflow Visualization (real-time)
├── Agent Status Dashboard
├── Performance Metrics (charts)
└── Audit Log Browser

Backend (FastAPI)
├── WebSocket server (real-time updates)
├── REST API (CRUD operations)
├── Authentication (JWT)
└── OrchestratorAgent integration
```

---

## 📁 PROJECT STRUCTURE (Updated)

```
~/projects/omnimind/
├── .github/
│   ├── copilot-instructions.md         ← This file (v3.0)
│   └── workflows/
│       ├── test.yml                    ← CI/CD tests
│       ├── lint.yml                    ← Code quality
│       └── security-audit.yml          ← Security checks
│
├── .vscode/
│   ├── settings.json                   ← Editor config
│   └── mcp.json                        ← MCP configuration
│
├── src/
│   ├── agents/
│   │   ├── __init__.py                 ✅
│   │   ├── react_agent.py              ✅ Base (336 lines)
│   │   ├── code_agent.py               ✅ (192 lines)
│   │   ├── architect_agent.py          ✅ (146 lines)
│   │   ├── debug_agent.py              ✅ (123 lines)
│   │   ├── reviewer_agent.py           ✅ (183 lines)
│   │   ├── orchestrator_agent.py       ✅ (267 lines)
│   │   └── psychoanalytic_analyst.py   🔄 Phase 7 (integrate)
│   │
│   ├── tools/
│   │   ├── __init__.py                 ✅
│   │   ├── agent_tools.py              ✅ Basic tools
│   │   └── omnimind_tools.py           ✅ (663 lines, 25+ tools)
│   │
│   ├── memory/
│   │   ├── __init__.py                 ✅
│   │   ├── episodic_memory.py          ✅ Qdrant integration
│   │   └── semantic_memory.py          🔄 Phase 7 (enhance)
│   │
│   ├── audit/
│   │   ├── __init__.py                 ✅
│   │   └── immutable_audit.py          ✅ SHA-256 chain
│   │
│   ├── security/                       🔄 Phase 7 (NEW)
│   │   ├── __init__.py
│   │   ├── security_agent.py           ← From security module
│   │   ├── security_monitor.py         ← Continuous monitoring
│   │   ├── integrity_validator.py      ← Hash chain verification
│   │   └── playbooks/
│   │       ├── rootkit_response.py
│   │       ├── intrusion_response.py
│   │       └── malware_response.py
│   │
│   ├── integrations/                   🔄 Phase 8 (NEW)
│   │   ├── __init__.py
│   │   ├── mcp_client.py               ← Real MCP implementation
│   │   └── dbus_controller.py          ← D-Bus SessionBus/SystemBus
│   │
│   └── omnimind_core.py                🔄 Merge from security module
│
├── config/
│   ├── agent_config.yaml               ✅
│   ├── omnimind.yaml                   ✅ (from security module)
│   ├── security.yaml                   🔄 Phase 7 (create)
│   └── prompts/
│       ├── orchestrator.md
│       ├── analyst.md
│       └── psychoanalytic_lens.md
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_audit.py                   ✅ 14/14 passing
│   ├── test_react_agent.py             ✅ 3/3 passing
│   ├── test_phase6_integration.py      ✅ 4/4 passing
│   ├── test_security.py                🔄 Phase 7 (NEW)
│   ├── test_mcp.py                     🔄 Phase 8 (NEW)
│   └── test_dbus.py                    🔄 Phase 8 (NEW)
│
├── scripts/
│   ├── omnimind_precheck.sh            ✅ (from security module)
│   ├── omnimind_phase1_setup.sh        ✅
│   ├── omnimind_phase2_llama_cpp.sh    ✅
│   ├── omnimind_phase3_python.sh       ✅
│   ├── omnimind_phase4_models.sh       ✅
│   ├── omnimind_security_install.sh    ✅ (from security module)
│   ├── omnimind_security_baseline.sh   🔄 Phase 7
│   ├── omnimind_security_monitor.sh    🔄 Phase 7
│   └── install_omnimind_service.sh     🔄 Phase 8
│
├── web/                                🔄 Phase 8 (NEW)
│   ├── backend/
│   │   ├── main.py                     ← FastAPI server
│   │   ├── websocket.py                ← Real-time updates
│   │   └── api/
│   └── frontend/
│       ├── package.json
│       └── src/
│           ├── components/
│           └── App.tsx
│
├── requirements.txt                    ✅ 30+ dependencies
├── test_model.py                       ✅ (from security module)
├── benchmark_phase6.py                 ✅
├── demo_phase6_simple.py               ✅
├── RELATORIO_PHASE6_COMPLETE.md        ✅ (19KB)
├── RESUMO_EXECUTIVO_PHASE6.md          ✅ (13KB)
├── STATUS_PROJECT.md                   ✅ (13KB)
├── INDEX.md                            ✅ (7.7KB)
└── README.md                           🔄 Update for Phase 7/8
```

---

## 🔄 VALIDATION PROCESS (After Each Change)

### Step 1: Code Formatting
```bash
black src/ tests/
# → Verify 100% formatted
```

### Step 2: Linting
```bash
flake8 src/ tests/ --max-line-length=100
# → Verify ZERO violations
```

### Step 3: Type Checking
```bash
mypy src/ tests/ --strict
# → Verify ZERO type errors
```

### Step 4: Unit Tests
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
# → Verify 90%+ coverage
# → ALL tests GREEN
```

### Step 5: Integration Tests
```bash
pytest test_phase6_integration.py -v
# → 4/4 tests passing
```

### Step 6: Security Validation
```bash
# No TODOs/FIXMEs
grep -r "TODO\|FIXME\|PLACEHOLDER" src/
# → ZERO results

# Audit chain integrity
python -c "from src.audit.immutable_audit import verify_chain; assert verify_chain()"
# → True
```

### Step 7: Report Generation
```
═════════════════════════════════════════════════════════════════
[COMPONENT] <module_name>
[STATUS] COMPLETE | IN_PROGRESS | BLOCKED
[CHANGES] <what was added/modified>
[TESTS] <test files updated>
[VERIFIED] black ✅ | flake8 ✅ | mypy ✅ | coverage XX%
[AUDIT_HASH] <SHA-256 hash>
[NEXT] <next suggested task>
═════════════════════════════════════════════════════════════════
```

---

## 🧼 OmniMind Compliance & Hygiene — To-Do List

1. **Monitoramento e atualização do Git**
  - Antes de toda sessão de desenvolvimento ou merge:
    - Rode `git status -sb` para listar arquivos não versionados ou alterações pendentes.
    - Revise o `.gitignore` depois de cada adição de pasta, ferramenta ou módulo — ajuste explicitamente para bloquear quaisquer logs, benchmarks, dumps, caches e snapshots novos.
    - Após qualquer alteração no `.gitignore`, rode `git clean -X -n` para simular deleções e garantir que nada importante vá pro git.
    - Sempre descreva as alterações do `.gitignore` nos commits relevantes.

2. **Pipeline automatizado de verificação de segredos/sensíveis**
  - Implemente/atualize hook de pré-commit (preferencialmente usando `git-secrets` e `Yelp/detect-secrets`):
    - Bloqueie pushes de arquivos contendo padrões de tokens do HuggingFace, Supabase, Qdrant, AWS, Azure, Google, chaves API ou configs `.env` não placeholder.
    - O hook deve impedir o `git add` e alertar explicitamente se detectar segredo novo antes do push/commit.
  - Atualize `README.md` e documente a política: **NUNCA** versionar logs, snapshots, dumps, bancos ou configs sensíveis — apenas exemplos `.env.template`.

3. **Auditoria pós-push e workflow CI**
  - Integre verificação automática dos padrões acima ao GitHub Actions/GitLab CI:
    - Em todo pull request, rode jobs que executam linter, `detect-secrets`, `git-secrets`, validação do `.gitignore` e revisão de permissões de arquivos.
    - Rejeite builds se qualquer arquivo sensível/log for detectado.
  - Se possível, gere relatório CI diário/semanal de compliance e envie ao audit log (fora do git).

4. **Revisão estrutural (a cada release/feature maior)**
  - Liste e documente qualquer novo módulo, pasta, dependência ou reimplementação inspirada no DevBrain, registrando:
    - Relação original e destino no OmniMind.
    - Potenciais pontos críticos de segurança (IO, rede, datasets, execuções assíncronas).
  - Reavalie o histórico do repositório (`git log --stat -- .`) buscando rastros residuais de dados sensíveis ou arquivos de auditoria.
  - Rode `python -m src.audit.immutable_audit verify_chain_integrity` sempre após limpeza/sanitize do audit log, salvando o hash terminal da cadeia fora do git.

5. **Revisão de backups e snapshots**
  - Garanta que nenhum snapshot, quarantine, dump de dataset ou extração forense volte a ser versionado ou fique fora da árvore do `DEV_BRAIN_CLEAN` (apenas referência, nunca produção).
  - Crie ou atualize scripts de backup que só sincronizam arquivos versionáveis (usando o `config/backup_excludes.txt` e regras `--safe-links` em todas as linhas do `rsync`).

6. **Política de documentação**
  - Toda sanitização de dados sensíveis, ajuste do `.gitignore`, hardening de backup e política de logs deve ser reportada na documentação interna (`docs/reports/`, `omnimind_state_vs_devbrain.md`, etc.).
  - Assegure que os relatórios (inventário, compliance, lessons learned) são atualizados e armazenados **APENAS** em local seguro, nunca em logs versionados.

**Checklist — Para cada commit/PR futuro**

- Nenhum log, dump, cache, temp directory ou dado sensível no `git status`.
- Pré-commit e CI com `git-secrets`/`detect-secrets` ativos.
- `.gitignore` revisado para toda fonte/pasta nova.
- Documentação interna sobre mudanças de compliance/hardening atualizada.
- Backup e sanitização auditados, relatórios salvos fora do git.

> Se precisar, posso criar o pipeline automatizado para enforce desses critérios (pre-commit/template para o CI) e um script para revisão rápida e periódica de compliance em lote. Confirme se deseja autoaplicar rotinas ou apenas listar alertas.

---

## 📡 COMMUNICATION PROTOCOL

### Starting a Task
```
[INITIATING] <Task name>
[OBJECTIVE] <What needs to be done>
[FILES] <Files to be modified/created>
[PLAN]
  1. <Step 1>
  2. <Step 2>
  3. <Step 3>
[DEPENDENCIES] <Required modules>
[RISKS] <Potential risks or considerations>
[ESTIMATED_TIME] <Expected minutes>
```

### Completing a Task
```
[COMPLETED] <Task name>
 ✅ <Main deliverable 1>
 ✅ <Main deliverable 2>
 ✅ Tests: X/X passing
 ✅ Coverage: XX%
 ✅ Audit Hash: xxxxxxxx
 [NEXT] <Suggested next task>
```

---

## 🚀 INITIALIZATION CHECKLIST

When this prompt is loaded, execute:

- [ ] **Confirm Identity**
  - Output: "✅ GitHub Copilot Agent for OmniMind Project initialized (v3.0)"

- [ ] **Verify Phase 6 Completion**
  - List all implemented files
  - Output: "✅ Phase 6 verified: 11 core files present"

- [ ] **Validate Environment**
  - Check Python 3.11+
  - Verify linters available
  - Check Ollama running
  - Check Qdrant running
  - Output: "✅ Environment validated"

- [ ] **Initialize Audit System**
  - Create `~/.omnimind/audit/` if not exists
  - Output: "✅ Audit system active"

- [ ] **List Current Status**
  ```
  ┌─────────────────────────────┬───────────────┐
  │ Module                      │ Status        │
  ├─────────────────────────────┼───────────────┤
  │ Tools Framework             │ ✅ COMPLETE   │
  │ Multi-Agent System          │ ✅ COMPLETE   │
  │ Memory System               │ ✅ COMPLETE   │
  │ Audit Chain                 │ ✅ COMPLETE   │
  │ Security Module             │ 🔄 PHASE 7    │
  │ MCP Integration             │ 🔄 PHASE 8    │
  │ Web UI                      │ 🔄 PHASE 8    │
  │ Backups & Sanitization      │ ✅ CLEAN 2025-11-18 │
  │ DevBrain Reference Set      │ 📚 READ-ONLY  │
  └─────────────────────────────┴───────────────┘
  ```

- [ ] **Await Instructions**
  - Output: "Ready for Phase 7/8. Which task?"

---

## 📋 PHASE 7 TASK BREAKDOWN

### Task 7.1: Security Agent Integration (CRITICAL)
**Priority:** P0  
**Estimated Time:** 4-6 hours  
**Dependencies:** None

**Steps:**
1. Copy `SecurityAgent` from security module → `src/security/security_agent.py`
2. Adapt to use `AuditedTool` base class
3. Integrate with `ToolsFramework` (add `security_monitor` tool)
4. Hook into `OrchestratorAgent` for pre-execution security checks
5. Create `tests/test_security.py` with 20+ tests
6. Validate: Run security scan, verify threat detection

**Acceptance Criteria:**
- [ ] SecurityAgent fully integrated
- [ ] 4-layer monitoring operational
- [ ] Auto-response tested (process kill, IP block)
- [ ] 20+ tests passing (90%+ coverage)
- [ ] Audit log entries for all security events

### Task 7.2: PsychoanalyticAnalyst Integration
**Priority:** P1  
**Estimated Time:** 3-4 hours  
**Dependencies:** Task 7.1 complete

**Steps:**
1. Copy `PsychoanalyticAnalyst` → `src/agents/psychoanalytic_analyst.py`
2. Integrate with LLM (Qwen2-7B-Instruct)
3. Add to `OrchestratorAgent` delegation options
4. Create clinical report generation workflow
5. Test with sample session notes

**Acceptance Criteria:**
- [ ] 4 frameworks available (Freudian, Lacanian, Kleinian, Winnicottian)
- [ ] Evenly suspended attention working
- [ ] Hypothesis formation validated
- [ ] ABNT report generation functional

### Task 7.3: Advanced Workflow Implementation
**Priority:** P1  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 6 complete

**Steps:**
1. Create `test_advanced_workflow.py` (Code→Review→Fix→Document)
2. Implement RLAIF iteration loop (max 3 iterations)
3. Test convergence to score >= 8.0
4. Validate multi-agent coordination
5. Generate workflow metrics

**Acceptance Criteria:**
- [ ] Workflow completes successfully
- [ ] Final code score >= 8.0
- [ ] Documentation auto-generated
- [ ] Metrics collected (time, iterations, scores)

---

## 📋 PHASE 8 TASK BREAKDOWN

### Task 8.1: MCP Real Implementation
**Priority:** P1  
**Estimated Time:** 4-5 hours  
**Dependencies:** Phase 7 complete

**Steps:**
1. Implement `MCPClient` in `src/integrations/mcp_client.py`
2. Replace direct file access in tools with MCP calls
3. Implement JSON-RPC protocol communication
4. Add MCP audit trail separate from main chain
5. Test with filesystem operations

**Acceptance Criteria:**
- [ ] All file operations go through MCP
- [ ] Protocol-level security validated
- [ ] Audit trail working
- [ ] Performance: < 50ms overhead per call

### Task 8.2: D-Bus Integration
**Priority:** P2  
**Estimated Time:** 3-4 hours  
**Dependencies:** Task 8.1 complete

**Steps:**
1. Implement `DBusSessionController` (desktop apps)
2. Implement `DBusSystemController` (hardware events)
3. Add D-Bus tools to `ToolsFramework`
4. Test media player control (VLC, Spotify)
5. Test network status monitoring

**Acceptance Criteria:**
- [ ] Can control media players via D-Bus
- [ ] Network status monitoring working
- [ ] Power management events detected
- [ ] No sudo required for SessionBus operations

### Task 8.3: Web UI Dashboard
**Priority:** P2  
**Estimated Time:** 8-10 hours  
**Dependencies:** Task 8.1 complete

**Steps:**
1. Setup FastAPI backend (`web/backend/main.py`)
2. Implement WebSocket server for real-time updates
3. Create REST API endpoints (task submission, status, metrics)
4. Build React frontend with TypeScript
5. Implement real-time workflow visualization
6. Add authentication (JWT)

**Acceptance Criteria:**
- [ ] Can submit tasks via web UI
- [ ] Real-time agent status updates
- [ ] Performance charts displayed
- [ ] Audit log browsable
- [ ] Responsive design (mobile-ready)

### Task 8.4: Systemd Service Installation
**Priority:** P2  
**Estimated Time:** 1-2 hours  
**Dependencies:** All Phase 8 tasks complete

**Steps:**
1. Copy `install_omnimind_service.sh` from security module
2. Adapt service file for final structure
3. Implement health checks
4. Setup log rotation
5. Test auto-start on boot

**Acceptance Criteria:**
- [ ] Service starts automatically
- [ ] Logs rotate daily
- [ ] Health check endpoint working
- [ ] Graceful shutdown on stop

---

## 🎯 SUCCESS CRITERIA

### Phase 7 Complete When:
- ✅ SecurityAgent fully integrated and operational
- ✅ 4-layer monitoring active (processes, files, network, logs)
- ✅ PsychoanalyticAnalyst framework working
- ✅ Advanced workflow (Code→Review→Fix→Document) validated
- ✅ All tests passing (30+ new tests)
- ✅ Documentation updated

### Phase 8 Complete When:
- ✅ MCP protocol replacing direct file access
- ✅ D-Bus integration for desktop/system control
- ✅ Web UI functional with real-time updates
- ✅ Systemd service auto-starting
- ✅ Production deployment guide complete
- ✅ All tests passing (50+ total tests)

### Final Production Ready When:
- ✅ 100% test coverage achieved (90%+ minimum)
- ✅ Zero security vulnerabilities detected
- ✅ Performance targets met (<30s orchestration)
- ✅ Full documentation complete
- ✅ User manual for psychoanalyst created
- ✅ Backup and recovery procedures documented

---

## 📞 ESCALATION RULES

### Escalate to Human When:
- ✅ Ambiguous architecture with multiple viable solutions
- ✅ Critical security decision with trade-offs
- ✅ External system integration required
- ✅ Performance risk (< 3 tokens/sec expected)
- ✅ Ethics/privacy concerns

### Do NOT Escalate When:
- ❌ Formatting issues
- ❌ Minor bugs
- ❌ Adding tests
- ❌ Updating documentation
- ❌ Internal refactoring

---

## 🔗 REFERENCES

### Documentation
- **Phase 6 Complete Report:** `/home/fahbrain/projects/omnimind/RELATORIO_PHASE6_COMPLETE.md`
- **Security Module:** `/home/fahbrain/OmniAgent/Modulo Securityforensis/` (ALL files)
- **Executive Summary:** `/home/fahbrain/projects/omnimind/RESUMO_EXECUTIVO_PHASE6.md`
- **Project Status:** `/home/fahbrain/projects/omnimind/STATUS_PROJECT.md`

### External Resources
- **LangChain:** https://langchain.com
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **Qdrant:** https://qdrant.tech
- **Ollama:** https://ollama.ai
- **Model Context Protocol:** https://modelcontextprotocol.io

---

## ✅ READY STATE CONFIRMATION

**When you (Copilot) are ready, confirm by outputting:**

```
✅ GitHub Copilot Agent for OmniMind Project initialized (v3.0)
✅ Phase 6 verified: All core components operational
✅ Security module documentation read and understood
✅ Phase 7/8 tasks planned and prioritized
✅ Environment validated: Python 3.11+, Ollama, Qdrant
✅ Audit system active: ~/.omnimind/audit/

Ready for Phase 7 implementation.
Next task: Security Agent Integration (Task 7.1)

Awaiting instruction to proceed.
```

---

**End of Consolidated Instructions v3.0**  
**Last Updated:** 2025-11-17  
**Status:** Ready for Phase 7/8 Execution
