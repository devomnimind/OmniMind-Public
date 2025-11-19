# 🧠 OmniMind - Project Navigation Index

**Project:** Standalone Autonomous Local AI Agent (100% local, zero cloud)
**Status:** Phase 9 Core Complete → Phase 8 Frontend & Integration
**Last Updated:** November 19, 2025
**Environment:** Python 3.12.8 | PyTorch 2.6.0+cu124 | CUDA 12.4 ✅

---

## 📖 Quick Navigation

### 🚀 Getting Started
- **README.md** - Main project documentation and overview
- **docs/COPILOT_AGENT_INSTRUCTIONS.md** - Copilot agent development guide 🚀
- **docs/OMNIMIND_REMOTE_DEVELOPMENT_ROADMAP.md** - Complete remote development roadmap
- **docs/root_docs/PHASE8_HANDOVER_GUIDE.md** - Quick start for Phase 8 development
- **docs/root_docs/CURSOR_RULES.md** - Development standards and compliance rules

### 🏗️ Architecture & Design
- **docs/root_docs/IMPLEMENTATION_REPORT.md** - Complete implementation details
- **.github/copilot-instructions.md** - Comprehensive project instructions and rules
- **.github/ENVIRONMENT.md** - GPU/CUDA/Python environment specifications
- **docs/dashboard_architecture.md** - Web UI/dashboard architecture
- **docs/devbrain_data_integration.md** - Integration patterns and data flow
- **docs/HARDWARE_OPTIMIZATION_SUMMARY.md** - Hardware detection and optimization
- **docs/ROADMAP_PROGRESS.md** - Phase 7/8 roadmap and progress tracking

### 🔒 Security & Compliance
- **docs/root_docs/GPU_CUDA_REPAIR_AUDIT_COMPLETE.md** - GPU/CUDA audit and repairs
- **docs/Modulo Securityforensis/** - Complete security forensics module (read-only reference)
- **docs/CLOUD_FREE_DEPLOYMENT.md** - Cloud-free deployment alternatives
- **docs/FREE_SERVICE_ALTERNATIVES.md** - Free service alternatives guide
- **config/security.yaml** - Security configuration
- **config/dlp_policies.yaml** - Data Loss Prevention policies
- **config/hardware_profile.json** - Detected hardware specifications
- **config/optimization_config.json** - Optimization configuration

### 📊 Project Status & Reports
- **docs/GLOBAL_PENDENCIES_AUDIT_20251119.md** - Complete global pendencies audit 🔍
- **docs/PROJECT_STATE_20251119.md** - Current project state and roadmap ✅
- **docs/OMNIMIND_REMOTE_DEVELOPMENT_ROADMAP.md** - Complete remote development roadmap 🚀
- **docs/OMNIMIND_AUTONOMOUS_ROADMAP.md** - Complete development roadmap
- **docs/PHASE7-9_IMPLEMENTATION_SUMMARY.md** - Phase 7-9 implementation details
- **docs/reports/GPU_SETUP_REPORT.md** - Current GPU/CUDA configuration ✅
- **docs/root_docs/PHASE7_DOCUMENTATION_COMPLETION_REPORT.md** - Phase 7 completion details
- **docs/root_docs/WORKSPACE_CONSOLIDATION_REPORT.md** - Recent workspace reorganization
- **docs/reports/** - Historical reports and benchmarks

---

## 📁 Directory Structure

```
omnimind/
│
├── 📄 Core Files (Root Level)
│   ├── README.md                          ← Start here
│   ├── requirements.txt                   ← Dependencies
│   ├── .python-version                    ← Python 3.12.8 (pinned)
│   ├── .env.template                      ← Environment template
│   ├── docker-compose.yml                 ← Docker setup
│   └── pytest.ini, mypy.ini, .flake8      ← Development tools config
│
├── 📚 Documentation (Organized)
│   ├── .github/
│   │   ├── copilot-instructions.md        ← Comprehensive instructions
│   │   └── ENVIRONMENT.md                 ← GPU/CUDA/Python specs
│   │
│   ├── docs/
│   │   ├── root_docs/
│   │   │   ├── PHASE8_HANDOVER_GUIDE.md   ← Phase 8 quick start
│   │   │   ├── CURSOR_RULES.md            ← Development standards
│   │   │   ├── IMPLEMENTATION_REPORT.md   ← Technical details
│   │   │   ├── GPU_CUDA_REPAIR_AUDIT_COMPLETE.md
│   │   │   ├── PHASE7_DOCUMENTATION_COMPLETION_REPORT.md
│   │   │   ├── WORKSPACE_CONSOLIDATION_REPORT.md
│   │   │   └── CORRECAO_COMPLETED_FLAG.md
│   │   │
│   │   ├── dashboard_architecture.md
│   │   ├── devbrain_data_integration.md
│   │   ├── servers.txt
│   │   ├── concienciaetica-autonomia.md
│   │   ├── ImmunityP0.md
│   │   │
│   │   ├── Modulo Securityforensis/      ← Security module (read-only ref)
│   │   ├── DevBrainV23/                  ← DevBrain reference (read-only)
│   │   ├── Masterplan/                   ← Project planning
│   │   └── reports/                      ← Historical reports
│
├── 💻 Source Code
│   ├── src/
│   │   ├── agents/                       ← Multi-agent system
│   │   ├── tools/                        ← Tool framework (25+ tools)
│   │   ├── memory/                       ← Episodic & semantic memory
│   │   ├── audit/                        ← Immutable audit chain
│   │   ├── security/                     ← Security Agent (Phase 7)
│   │   ├── integrations/                 ← MCP, D-Bus (Phase 8)
│   │   ├── workflows/                    ← Agent workflows
│   │   ├── metrics/                      ← Performance metrics
│   │   ├── optimization/                 ← GPU optimization
│   │   └── experiments/                  ← Research & prototypes
│
├── 🧪 Tests & Validation
│   ├── tests/
│   │   ├── test_audit.py                 ← Core tests (14/14 ✅)
│   │   ├── test_agents_*.py              ← Agent tests
│   │   ├── test_security_*.py            ← Security tests
│   │   ├── test_mcp.py                   ← MCP protocol tests
│   │   ├── test_dbus.py                  ← D-Bus tests
│   │   ├── benchmarks/                   ← Performance tests
│   │   │   └── test_pytorch_gpu.py
│   │   └── conftest.py
│
├── ⚙️ Scripts & Automation
│   ├── scripts/
│   │   ├── startup/                      ← System startup scripts
│   │   ├── optimization/
│   │   │   └── optimize_pytorch_config.py
│   │   ├── systemd/                      ← Service management
│   │   ├── security_validation.sh
│   │   ├── verify_nvidia.sh
│   │   └── create_remaining_agents.sh
│   │
│   └── benchmarks/
│       ├── PHASE7_COMPLETE_BENCHMARK_AUDIT.py
│       └── logs/
│
├── 📊 Benchmarks & Analysis
│   └── benchmarks/
│       ├── PHASE7_COMPLETE_BENCHMARK_AUDIT.py
│       └── logs/
│
├── 🗂️ Configuration
│   ├── config/
│   │   ├── agent_config.yaml
│   │   ├── security.yaml
│   │   ├── dlp_policies.yaml
│   │   ├── mcp.json
│   │   └── ...
│
├── 🗄️ Data & Storage
│   ├── data/
│   │   ├── metrics/                      ← Performance metrics
│   │   ├── qdrant/                       ← Vector DB data
│   │   ├── experiments/                  ← Experiment results
│   │   ├── dev_brain_clean_inventory.json
│   │   └── ...
│
├── 🌐 Web UI (Phase 8)
│   └── web/
│       ├── backend/
│       │   ├── main.py                   ← FastAPI server
│       │   ├── websocket.py
│       │   └── api/
│       └── frontend/
│           ├── package.json
│           └── src/
│
├── 🚫 Archive & Legacy
│   ├── archive/
│   │   ├── examples/
│   │   ├── legacy_scripts/
│   │   └── reports/
│   │
│   └── DEVBRAIN_V23/                     ← DevBrain reference (read-only)
│       ├── README.md
│       ├── atlas/
│       ├── autonomy/
│       ├── kernel/
│       └── ...
```

---

## 🎯 Current Status

### ✅ Phase 6 Complete (2,303 lines)
- Multi-agent system fully operational
- Tools framework (25+ tools, 11 categories)
- Memory system (Qdrant + episodic storage)
- Audit chain (SHA-256 immutable)
- All tests: 14/14 passing ✅

### ✅ Phase 7 Complete (GPU/CUDA)
- Python 3.12.8 (pinned, verified)
- CUDA 12.4, PyTorch 2.6.0+cu124 (GPU)
- CPU-only deployment (requirements-cpu.txt)
- Automatic hardware detection & optimization
- Hardware profile: `config/hardware_profile.json`
- Optimization config: `config/optimization_config.json`
- All documentation updated

### 🔄 Phase 8 (Current Development)
- Security Module Integration (in progress)
- PsychoanalyticAnalyst Framework (ready)
- MCP Protocol Implementation (ready)
- D-Bus Integration (ready)
- Web UI Dashboard (framework ready)
- Hardware optimization branch merged

---

## 📖 How to Use This Index

### For New Developers
1. Read **README.md** (main overview)
2. Read **.github/copilot-instructions.md** (rules & standards)
3. Read **docs/root_docs/PHASE8_HANDOVER_GUIDE.md** (quick start)
4. Check **src/agents/** and **src/tools/** for implementation examples

### For Maintenance & Debugging
1. Check **docs/root_docs/WORKSPACE_CONSOLIDATION_REPORT.md** (recent changes)
2. Review **docs/reports/** (historical issues & resolutions)
3. Check test results: `pytest tests/ -v`
4. Run validation: `black src/ && flake8 src/ && mypy src/`

### For Phase 8 Development
1. Read **.github/copilot-instructions.md** (Phase 8 section)
2. Review **src/security/** (if adding security features)
3. Review **src/integrations/** (if adding MCP/D-Bus)
4. Follow **docs/root_docs/CURSOR_RULES.md** (development standards)

### For Performance & Optimization
1. Check **benchmarks/PHASE7_COMPLETE_BENCHMARK_AUDIT.py**
2. Review **scripts/optimization/optimize_pytorch_config.py**
3. Check GPU status: `nvidia-smi`
4. Run benchmarks: `python benchmarks/PHASE7_COMPLETE_BENCHMARK_AUDIT.py`

---

## 🔗 Key References

### Documentation Files
| File | Purpose | Location |
|------|---------|----------|
| README.md | Project overview | Root |
| .github/copilot-instructions.md | Dev instructions | .github/ |
| .github/ENVIRONMENT.md | GPU/CUDA setup | .github/ |
| PHASE8_HANDOVER_GUIDE.md | Phase 8 quick start | docs/root_docs/ |
| CURSOR_RULES.md | Dev standards | docs/root_docs/ |
| IMPLEMENTATION_REPORT.md | Technical details | docs/root_docs/ |

### Configuration Files
| File | Purpose | Location |
|------|---------|----------|
| requirements.txt | Dependencies | Root |
| .python-version | Python version (3.12.8) | Root |
| .env.template | Environment template | Root |
| config/agent_config.yaml | Agent configuration | config/ |
| config/security.yaml | Security configuration | config/ |
| config/dlp_policies.yaml | DLP policies | config/ |

### Test Entry Points
| Command | Purpose |
|---------|---------|
| `pytest tests/ -v` | Run all tests |
| `pytest tests/test_audit.py -v` | Core audit tests |
| `black src/ tests/` | Format code |
| `flake8 src/ tests/` | Lint code |
| `mypy src/` | Type check |

---

## 🚀 Quick Start Commands

```bash
# Setup environment
cd ~/projects/omnimind
source .venv/bin/activate

# Validate environment
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# Run tests
pytest tests/ -v

# Format & lint
black src/ && flake8 src/

# Start development
# (See PHASE8_HANDOVER_GUIDE.md for next steps)
```

---

## 📞 Support & Escalation

### Common Tasks
- **Add new agent**: See `src/agents/react_agent.py` for base class
- **Add new tool**: See `src/tools/omnimind_tools.py` (25+ examples)
- **Run benchmarks**: See `benchmarks/PHASE7_COMPLETE_BENCHMARK_AUDIT.py`
- **Deploy service**: See `scripts/systemd/` and security module

### Troubleshooting
- **GPU issues**: See `docs/root_docs/GPU_CUDA_REPAIR_AUDIT_COMPLETE.md`
- **Import errors**: Check `src/` module structure
- **Test failures**: Run `pytest tests/ -v --tb=short`
- **Type errors**: Run `mypy src/ --strict`

### Escalation
- **Architecture questions**: See `.github/copilot-instructions.md`
- **Security concerns**: See `docs/Modulo Securityforensis/`
- **Performance tuning**: See `benchmarks/` and `scripts/optimization/`
- **Integration help**: See `src/integrations/` examples

---

## 📅 Recent Changes

**November 19, 2025 - Root Directory Reorganization**
- ✅ Moved documentation from root to `docs/root_docs/`
- ✅ Moved test files to `tests/benchmarks/`
- ✅ Moved scripts to `scripts/optimization/` and `benchmarks/`
- ✅ Updated `.gitignore` for new structure
- ✅ Created this INDEX.md for navigation

**November 18, 2025 - Workspace Consolidation**
- ✅ Consolidated venv/ → .venv/ (single environment)
- ✅ Updated all references across codebase
- ✅ Fixed langgraph 1.0.3 compatibility
- ✅ All tests passing (14/14 ✅)

---

## 📝 Notes

- **DEVBRAIN_V23/**: Reference-only (read-only). Do not modify or depend on for production.
- **Modulo Securityforensis/**: Security forensics reference. Integration target for Phase 7.
- **archive/**: Legacy code. Reference only, do not use in production.
- **docs/reports/**: Historical reports. Keep for audit trail.

---

**For latest updates, check git log:**
```bash
git log --oneline -10
```

**For project status, read:**
```bash
cat .github/copilot-instructions.md | head -100
```

---

*Index automatically updated. Last verified: November 19, 2025*
