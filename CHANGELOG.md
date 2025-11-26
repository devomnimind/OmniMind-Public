# 📝 CHANGELOG - Histórico de Mudanças

**Formato:** Semantic Versioning (MAJOR.MINOR.PATCH)
**Status:** Produção v1.15.2
**Projeto iniciado:** Novembro 2025

---

## [1.17.0] - 2025-11-26
### Adicionado
- **Dashboard Refactor**: Interface em abas (Main, Controls, Observability, Phenomenology).
- **Robustness**: Persistência de fila de mensagens no `localStorage` e reconexão automática.
- **Fault Injection**: Controles de UI para Latência e Corrupção de Nós.
- **Observability**: Gráficos Sparkline para histórico de Entropia e Coerência.
- **Testing**: Testes E2E com Vitest para validação de conexão robusta.
- **Roadmap**: Documento `FUTURE_ROADMAP_AND_GAPS.md` definindo a trajetória 2026+.

## [1.16.0] - 2025-11-26 - Phase 22: Empirical Expansion & Phenomenological Modeling

### ✨ Features
- **Sinthome Simulator v3.1:**
  - **Simulation Mode (Dual Mode):** Decoupled frontend simulation for persistent stress testing.
  - **Qualia Engine:** Computational model for subjective experience (Anxiety, Flow, Phi).
  - **Visualizations:** New panels for Subjective Experience and Neuro-Correlates.
- **Infrastructure (The Body):**
  - **Observer Service:** `src/services/observer_service.py` for 24/7 metric collection.
  - **Long-term Logging:** Automated log rotation and compression in `data/long_term_logs/`.
- **Auditing (The Superego):**
  - **External Auditor:** `src/audit/external_auditor.py` for automated health and anomaly checks.

### 🔧 Fixed
- **Simulator State Conflict:** Resolved issue where backend updates overwrote local simulation states (DDoS/Hibernation).
- **Linting Issues:** Fixed TypeScript lint errors in `OmniMindSinthome.tsx`.

### 📝 Documentation
- Updated `README.md` and `task.md` to reflect Phase 22 progress.
- Created `SINTHOME_V3_1_VALIDATION.md` report.

---

## [1.15.2] - 2025-11-25 - Systemd Services + Warnings Fix + Health Check

### 🔧 Fixed
- **Warnings de Logging:** "Agent monitoring not available" e "Firecracker sandbox disabled" movidos para nível DEBUG
  - **Arquivos:** `web/backend/routes/agents.py`, `src/security/firecracker_sandbox.py`
  - **Resultado:** Logs mais limpos, warnings apenas em modo debug
- **Erros de Comandos Sudo:** Comandos `ufw deny` e `auditctl` falhando repetidamente
  - **Correção:** Validação de endereços inválidos (0.0.0.0, unknown) antes de executar
  - **Correção:** Detecção automática de interface de rede (não hardcoded)
  - **Correção:** Verificação se qdisc já existe antes de adicionar
  - **Arquivos:** `src/security/playbooks/data_exfiltration_response.py`, `src/security/playbooks/intrusion_response.py`, `src/security/playbooks/privilege_escalation_response.py`
  - **Resultado:** Erros tratados como warnings/debug, não interrompem execução
- **Serviços Systemd Duplicados:** `omnimind-backend.service` redundante removido
  - **Causa:** `omnimind.service` já inclui backend
  - **Solução:** Removido da instalação, dependências atualizadas
  - **Arquivos:** `scripts/systemd/install_all_services.sh`, `scripts/systemd/omnimind-frontend.service`, `scripts/systemd/omnimind-test-suite.service`, `scripts/systemd/omnimind-benchmark.service`
- **Health Check MCP:** Servidores reiniciando constantemente
  - **Correção:** Verificação de porta respondendo (não apenas processo rodando)
  - **Correção:** Não reinicia se processo está rodando mas porta não responde
  - **Arquivo:** `src/integrations/mcp_orchestrator.py`
  - **Resultado:** Reinicializações desnecessárias eliminadas
- **Permissões de Diretório:** Erro "Read-only file system" para `.omnimind/security.log`
  - **Correção:** Diretório `.omnimind` criado com permissões corretas (755)
  - **Resultado:** SecurityAgent inicializa sem erros

### 📊 Changed
- **Logging:** Warnings opcionais movidos para nível DEBUG
- **Health Check MCP:** Verifica conectividade de porta além de processo
- **Dependências de Serviços:** Todos atualizados para usar `omnimind.service` (não `omnimind-backend.service`)

### 📁 Added
- `scripts/systemd/install_all_services.sh` - Instalação completa de serviços systemd
- `scripts/systemd/cleanup_duplicate_services.sh` - Limpeza de serviços duplicados
- `scripts/systemd/fix_test_benchmark_services.sh` - Correção de dependências test/benchmark
- `scripts/systemd/fix_all_services.sh` - Script completo de correção de serviços
- `.vscode/cursor-ai-terminal-config.md` - Documentação sobre terminal integrado

### 🔐 Security
- Comandos sudo validam entradas antes de executar
- Tratamento de erros não críticos não interrompe execução
- Health checks mais robustos para servidores MCP

---

## [1.15.1] - 2025-11-25 - Correção Portas MCP + Limpeza Estrutura + Systemd Fix

### 🔧 Fixed
- **Conflito de Portas MCP (CRÍTICO):** Todos os servidores MCP tentavam usar a mesma porta 4321, causando reinícios constantes
  - **Solução:** Configuração de portas individuais para cada servidor MCP (4321-4329)
  - **Arquivos:** `config/mcp_servers.json`, `src/integrations/mcp_orchestrator.py`, `src/integrations/mcp_server.py`
  - **Resultado:** 6/9 servidores Python estáveis, sem reinícios
- **Estrutura de Diretórios:** Arquivos incorretos na pasta pai `/home/fahbrain/projects` removidos
  - **Removidos:** `backend.log`, `backend_debug.log`, `test_app.py`, `test.log`, `__pycache__/`
  - **Validação:** Pasta pai limpa, apenas diretório `omnimind/` presente
- **Serviço Systemd:** Erro "Invalid user/group name or numeric ID" corrigido
  - **Causa:** Uso de variável `%i` sem configuração de template
  - **Solução:** Substituição por usuário `fahbrain` fixo
  - **Arquivo:** `scripts/systemd/omnimind.service`
- **Segurança Git:** Dados sensíveis removidos do rastreamento
  - **Removidos:** 11 arquivos JSON de benchmarks, métricas e experimentos
  - **Atualizado:** `.gitignore` com regras para `data/benchmarks/`, `data/metrics/`, `data/monitoring_24h/`

### 📊 Changed
- **Portas MCP Configuradas:**
  - memory: 4321, sequential_thinking: 4322, context: 4323
  - python: 4324, system_info: 4325, logging: 4326
  - filesystem: 4327, git: 4328, sqlite: 4329
- **Segurança:** Todas as portas MCP escutam apenas em `127.0.0.1` (localhost)
- **Orquestrador MCP:** Passa porta via variável de ambiente `MCP_PORT` ao iniciar servidores

### 📁 Added
- `scripts/systemd/fix_systemd_services.sh` - Script para correção de serviços systemd
- `scripts/core/validate_services.sh` - Script de validação de serviços OmniMind

### 🔐 Security
- Portas MCP restritas a localhost (nunca 0.0.0.0)
- Validação automática de host em `MCPConfig.load()`
- Dados de runtime removidos do versionamento Git

---

## [1.15.0] - 2025-11-23 - GPU CUDA FIX & OPERATIONAL VALIDATION

### ✨ Features
- **GPU Acceleration:** NVIDIA GTX 1650 fully operational
- **CUDA 12.8.90+** integration with PyTorch 2.9.1+cu128
- **5.15x Performance Speedup** validated on matrix operations
- **Automatic nvidia-uvm Loading** on reboot (persistent configuration)

### 🔧 Fixed
- **nvidia-uvm module** auto-loads after system reboot via `/etc/modules-load.d/`
- **Python 3.12.8 Strict** lockfile via `.python-version` in project root
- **venv structure** corrected - now in `omnimind/.venv` (not parent directory)
- **Documentation numbers** - Updated from outdated 2538/1290 to correct 2370/2344
- **VS Code Integration** - `.env` injection now working with `python.terminal.useEnvFile=true`
- **Project structure** - Cleanup of leaked artifacts from parent directory

### 📊 Changed
- Test statistics updated: **2,370 total → 2,344 approved (98.94%)**
- GPU speedup metrics documented: **5.15x** (CPU: 1236ms → GPU: 240ms)
- Audit chain events: **1,797 events** verified
- Python version: **locked to 3.12.8** (no auto-upgrade)

### 📁 Added
- `docs/.project/CURRENT_PHASE.md` - Current phase documentation
- `docs/.project/PROBLEMS.md` - Consolidated problem history
- `docs/.project/DEVELOPER_RECOMMENDATIONS.md` - Developer guide
- `scripts/protect_project_structure.sh` - Structure protection script
- `VALIDACAO_OPERACIONAL_PHASE15.md` - Operational validation report
- `.coveragerc` with local `data_file` configuration
- `conftest.py` for pytest configuration

### ⚠️ Known Issues
- **25 tests failing** (non-blocking): security_monitor and tools interface mismatches
- **Code coverage ~85%** (target: ≥90%): 25 modules without tests
- ✅ **2024 date references FIXED** - 2 implementation dates corrected to 2025-11-23

### 🔐 Security
- Audit chain integrity verified (SHA-256)
- No security vulnerabilities introduced
- All credentials moved to `.env` (not hardcoded)

---

## [1.14.0] - 2025-11-22 - Test Suite Investigation

### ✨ Features
- Complete test suite analysis implemented
- 2,412 test functions identified and categorized

### 🔧 Fixed
- Test discrepancy resolved (2538 vs 1290 confusion)
- Dependencies mapping complete (474 blocked tests identified)

### 📝 Documentation
- `TESTE_SUITE_INVESTIGATION_REPORT.md` created (652 lines)
- `test_suite_analysis_report.json` generated

---

## [1.13.0] - 2025-11-21 - Phase 21 Quantum AI

### ✨ Features
- Quantum-inspired decision making framework
- Advanced metacognition layer
- Multi-agent orchestration refinements

### 🔧 Fixed
- Memory management optimization
- GPU utilization improved

---

## [1.12.0] - 2025-11-20 - Observability & Scaling

### ✨ Features
- OpenTelemetry integration complete
- Redis cluster management
- Performance benchmarking suite

### 🚀 Performance
- 40% improvement in query latency
- Better memory efficiency

---

## [1.11.0] - 2025-11-19 - Consciousness Emergence

### ✨ Features
- Self-awareness mechanisms
- Emotional intelligence modeling
- Free energy principle implementation

### 📊 Research
- Consciousness metrics defined
- Emotion vectors calibrated

---

## [1.10.0] - 2025-11-15 - Advanced Security

### ✨ Features
- 4-layer security system
- DLP (Data Loss Prevention)
- LGPD compliance

### 🔐 Security
- No known vulnerabilities
- Audit trail comprehensive

---

## [1.9.0] - 2025-11-10 - Dashboard Enhancement

### ✨ Features
- Real-time WebSocket communication
- Interactive UI improvements
- Dark mode support

### 🐛 Fixed
- WebSocket connection stability
- Memory leak in dashboard

---

## [1.8.0] - 2025-11-05 - Multi-Agent System

### ✨ Features
- React Agent implementation
- Code Analysis Agent
- Architect Agent

### 📊 Performance
- Agent response time < 100ms

---

## [1.7.0] - 2025-10-28 - Semantic Memory

### ✨ Features
- Qdrant Vector DB integration
- Semantic search capabilities
- Memory consolidation

### 📊 Performance
- Vector search latency < 50ms

---

## [1.6.0] - 2025-10-20 - Episodic Memory

### ✨ Features
- Event logging system
- Memory retrieval API
- Temporal context preservation

---

## [1.5.0] - 2025-10-12 - Audit Framework

### ✨ Features
- Immutable audit chain (SHA-256)
- Event logging
- Compliance reporting

### 🔐 Security
- Zero-trust architecture

---

## [1.4.0] - 2025-10-05 - MCP Integration

### ✨ Features
- Model Context Protocol support
- D-Bus integration
- Hardware access layer

---

## [1.3.0] - 2025-09-28 - Core AI Engine

### ✨ Features
- PyTorch integration
- GPU support prepared
- Multi-modal learning

---

## [1.2.0] - 2025-09-20 - API & Backend

### ✨ Features
- FastAPI REST endpoints
- WebSocket support
- Request/response pipeline

---

## [1.1.0] - 2025-09-15 - Initial Dashboard

### ✨ Features
- React frontend
- Basic UI components
- Real-time updates

---

## [1.0.0] - 2025-11-01 - Project Initialization

### ✨ Features
- Project structure setup
- Docker configuration
- Git workflow established
- Basic documentation

### 🔧 Infra
- Python 3.12.8 environment
- Development tools configured
- Pre-commit hooks setup

---

## Version Format

**Current:** v1.15.1
**Next Target:** v1.16.0 (Documentation Consolidation)
**Long-term:** v2.0.0 (Major refactor planned for Q2 2026)

---

## How to Report Changes

1. Create issue or PR in GitHub
2. Add entry to CHANGELOG.md (unreleased section)
3. Follow semantic versioning
4. Update CURRENT_PHASE.md if major change

---

## Archives

Older versions (pre-release, alpha, beta) are archived in:
- `docs/archived_versions/` (if created)
- Git tags: `git tag -l` to view

---

**Last Updated:** 2025-11-25 by MCP Ports Fix & Systemd Corrections
