# Phase 8 Handover & Quick Start Guide

**Prepared:** November 19, 2025  
**Status:** ✅ Phase 7 Complete - Phase 8 Ready to Begin  
**System:** OmniMind with GPU/CUDA fully operational

---

## 🚀 Quick Start (5 Minutes)

### 1. Activate Environment
```bash
cd /home/fahbrain/projects/omnimind
pyenv local 3.12.8  # Ensures Python 3.12.8
source .venv/bin/activate
```

### 2. Verify GPU Status
```bash
# Quick check
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Comprehensive check
python PHASE7_COMPLETE_BENCHMARK_AUDIT.py | grep "CUDA Status"

# If CUDA unavailable (post-suspend):
sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true
sleep 1
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sleep 1
sudo modprobe nvidia_uvm
```

### 3. Run Tests
```bash
# Audit tests (14/14 should pass)
pytest tests/test_audit.py -v

# All quality gates
black --check src tests && flake8 src tests && pytest -v
```

---

## 📋 Phase 8 Planning Overview

### Phase 8.1: Security Module Integration (Priority: P0)

**Files to integrate from `/home/fahbrain/OmniAgent/Modulo Securityforensis/`:**
- SecurityAgent class
- 4-layer monitoring (process, network, file, log)
- Auto-response playbooks
- Forensic tools integration (auditd, AIDE, chkrootkit, rkhunter)

**Destination:** `src/security/security_agent.py`  
**Tests:** `tests/test_security_phase8.py` (20+ tests)

### Phase 8.2: PsychoanalyticAnalyst Framework Integration

**Implementation:**
- Copy PsychoanalyticAnalyst framework from security module
- Integrate with LLM (Qwen2-7B-Instruct)
- Add to OrchestratorAgent delegation
- Create clinical report generation workflow

**Destination:** `src/agents/psychoanalytic_analyst.py`

### Phase 8.3: MCP Protocol Implementation

**Tasks:**
1. Implement real MCP client (not mock) in `src/integrations/mcp_client.py`
2. Replace direct filesystem access with MCP calls
3. Implement audit trail at protocol level

### Phase 8.4: D-Bus Integration

**Tasks:**
1. Implement DBusSessionController for desktop apps
2. Implement DBusSystemController for hardware events
3. Add D-Bus tools to ToolsFramework

### Phase 8.5: Web UI Dashboard

**Structure:**
```
web/backend/     → FastAPI + WebSocket + Real-time updates
web/frontend/    → React + TypeScript + Responsive design
```

**Features:**
- Task submission form
- Real-time workflow visualization
- Agent status dashboard
- Performance metrics charts
- Audit log browser

---

## 🔧 Development Workflow (Phase 8+)

### Before Starting Work
```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Verify GPU (if needed post-suspend)
python -c "import torch; assert torch.cuda.is_available()"

# 3. Pull latest changes
git pull origin master

# 4. Check status
git status
```

### During Development
```bash
# Format and lint after each feature
black src tests
flake8 src tests

# Run relevant tests
pytest tests/test_<module>.py -v

# Before committing
black src tests && flake8 src tests && mypy src tests && pytest -v
```

### When Committing
```bash
# Descriptive commit message
git add <files>
git commit -m "Feature: <clear description> (Phase 8)"
git push origin master
```

### If CUDA Errors Occur
```bash
# Most common fix
sudo modprobe -r nvidia_uvm && sleep 1 && sudo modprobe nvidia_uvm

# Verify
python -c "import torch; print(torch.cuda.is_available())"

# If still broken, reference ENVIRONMENT.md troubleshooting section
```

---

## 📚 Key Documentation Files

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Comprehensive agent rules + GPU/CUDA setup |
| `CURSOR_RULES.md` | Development rules + GPU guidelines |
| `README.md` | Quick start + GPU verification |
| `.github/ENVIRONMENT.md` | Complete environment specification |
| `GPU_CUDA_REPAIR_AUDIT_COMPLETE.md` | GPU repair summary |
| `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md` | Detailed GPU troubleshooting |

---

## 🎯 GPU Memory Constraints (Remember!)

**GTX 1650 VRAM: 3.81 GB Total**

```
Safe allocation breakdown:
├─ LLM inference:     ~2.5 GB
├─ Agent buffers:     ~800 MB
├─ Embeddings:        ~200 MB
└─ User operations:   ~500 MB (absolute max)

Batch size rules:
- LLM inference:      batch_size ≤ 32
- Embedding ops:      batch_size ≤ 128
- Tensor operations:  matrix_size ≤ 5000
```

**Always include CPU fallback in GPU code:**
```python
device = "cuda" if torch.cuda.is_available() else "cpu"
tensor = torch.randn(size, device=device)
```

---

## 🔍 Verification Checklist (Weekly)

- [ ] Run `python PHASE7_COMPLETE_BENCHMARK_AUDIT.py` (GPU ≥1000 GFLOPS?)
- [ ] Run `pytest tests/test_audit.py -v` (14/14 passing?)
- [ ] Run `black --check src tests` (all formatted?)
- [ ] Run `flake8 src tests` (zero violations?)
- [ ] Check `git status` (clean?)
- [ ] Test GPU after suspend: `python -c "import torch; print(torch.cuda.is_available())"`

---

## 📊 Current Status Snapshot

```
System:        Linux 6.16.8+kali-amd64
CPU:           Intel i5-10th gen (4c/8t)
GPU:           NVIDIA GTX 1650 (3.81GB VRAM) ✅ OPERATIONAL
Python:        3.12.8 (pyenv pinned)
PyTorch:       2.6.0+cu124 (GPU-enabled)
Performance:   8.1x GPU acceleration (1124.44 GFLOPS)
Tests:         14/14 passing (100%)
Code Quality:  Perfect (black/flake8)
Git Status:    Clean & synchronized
```

---

## 🚨 Emergency Procedures

### GPU Not Available
```bash
# Step 1: Reload nvidia_uvm (most common fix)
sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true
sleep 1
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sleep 1
sudo modprobe nvidia_uvm

# Step 2: Verify
python -c "import torch; print(torch.cuda.is_available())"

# Step 3: If still fails, check ENVIRONMENT.md troubleshooting
```

### PyTorch Version Issue
```bash
# Delete venv and recreate with correct Python
rm -rf .venv
python3.12 -m venv .venv  # Use Python 3.12 explicitly
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Verify
python --version  # MUST show Python 3.12.8
python -c "import torch; print(torch.__version__)"  # MUST show 2.6.0+cu124
```

### Test Failures
```bash
# Run with verbose output
pytest tests/test_audit.py -vv --tb=short

# Check if dependencies changed
pip install -r requirements.txt

# Run specific test
pytest tests/test_audit.py::TestImmutableAuditSystem::test_initialization -vv
```

---

## 💡 Pro Tips for Phase 8

1. **Always verify after suspend:** Linux often corrupts nvidia_uvm after sleep
2. **Use GPU for large ops only:** CPU is sufficient for small batches
3. **Monitor GPU memory:** `nvidia-smi -l 1` (updates every second)
4. **Keep requirements.txt updated:** Any new package must be added
5. **Document decisions:** Update ADRs in `docs/` when making architectural choices
6. **Commit frequently:** Small commits are easier to review and revert if needed
7. **Test before pushing:** Always run full pipeline (black/flake8/pytest) before git push
8. **Use benchmarks:** PHASE7_COMPLETE_BENCHMARK_AUDIT.py validates system health

---

## 📞 Support References

- **GPU Issues:** See `.github/ENVIRONMENT.md` → Troubleshooting Guide
- **Development Rules:** See `CURSOR_RULES.md` → GPU Development Guidelines
- **Setup Issues:** See `README.md` → GPU Verification section
- **Detailed Repair Log:** See `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md`
- **Agent Instructions:** See `.github/copilot-instructions.md` → Full reference

---

## ✨ Next Session Quick Links

1. **Activate:** `cd omnimind && source .venv/bin/activate`
2. **Verify:** `python PHASE7_COMPLETE_BENCHMARK_AUDIT.py`
3. **Start coding:** Reference `.github/copilot-instructions.md` for Phase 8 tasks
4. **Commit:** Follow workflow above
5. **Push:** `git push origin master`

---

**Prepared by:** OmniMind Autonomous Agent  
**Date:** November 19, 2025  
**Status:** ✅ Phase 7 Complete - Ready for Phase 8

Welcome to Phase 8! GPU is operational. All systems ready. 🚀
