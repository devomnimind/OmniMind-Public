# 🚀 OmniMind Recovery Scripts - Complete Guide

**Status:** Ready for execution
**Last Updated:** 2025-12-12
**Phase:** System Stabilization (Phase 24+)

---

## 📋 Overview

These scripts recover the OmniMind system from its partially desintegrated state. The system is **functionally ACTIVE** (1155 integration cycles already executed) but needs:

1. ✅ **Qdrant collections initialized** (7 collections)
2. ✅ **44k vectors trained** (code embeddings)
3. ✅ **Integration cycles + stimulation** (500 cycles)
4. ✅ **Persistent state initialized** (from cycle data)
5. ✅ **GPU memory allocation fixed** (embeddings to .cuda())
6. ✅ **Daemon logging increased** (show cycle execution)

---

## 🎯 Quick Start

### Option A: Automated Recovery (Recommended)

Run all steps automatically in correct order:

```bash
cd /home/fahbrain/projects/omnimind
bash scripts/MASTER_RECOVERY_EXECUTOR.sh
# Select: A (for automated)
```

**Time:** ~30-45 minutes (depends on internet/GPU speed)
**Output:** System fully recovered and training

### Option B: Manual Step-by-Step

```bash
cd /home/fahbrain/projects/omnimind

# Step 1: Initialize Qdrant collections
bash scripts/recovery/01_init_qdrant_collections.sh

# Step 2: Train 44k vectors
bash scripts/recovery/02_train_embeddings.sh

# Step 3: Run 500 integration cycles
bash scripts/recovery/03_run_integration_cycles.sh

# Step 4: Initialize persistent state
bash scripts/recovery/04_init_persistent_state.sh

# Step 5: Fix GPU memory allocation
bash scripts/recovery/05_fix_gpu_allocation.sh

# Step 6: Increase daemon logging
bash scripts/recovery/06_increase_daemon_logging.sh
```

---

## 📊 What Each Script Does

### 1️⃣ `01_init_qdrant_collections.sh`

**Purpose:** Create 7 Qdrant collections for the system

**Collections created:**
- `omnimind_consciousness` (768 dims) - Consciousness states
- `omnimind_episodes` (768 dims) - Episodic memory
- `omnimind_embeddings` (384 dims) - Code/document embeddings
- `omnimind_narratives` (768 dims) - Narratives/histories
- `omnimind_system` (384 dims) - System metadata
- `omnimind_memories` (768 dims) - General memory
- `orchestrator_semantic_cache` (384 dims) - Orchestrator cache

**Time:** ~2-3 minutes
**Requirements:** Qdrant running (`docker-compose up -d qdrant`)

### 2️⃣ `02_train_embeddings.sh`

**Purpose:** Train 44k vectors from code and index to Qdrant

**Indexes:**
- `src/` - Source code
- `tests/` - Test suites
- `scripts/` - Scripts
- `config/` - Configuration
- `docs/` - Documentation

**Uses:** `sentence-transformers/all-MiniLM-L6-v2` (384 dims, 22GB cached)

**Time:** ~10-15 minutes (GPU accelerated)
**Output:** 7903+ vectors in `omnimind_embeddings` collection
**Note:** Uses CUDA_LAUNCH_BLOCKING=1 for stable GPU execution

### 3️⃣ `03_run_integration_cycles.sh`

**Purpose:** Execute 500 integration cycles with stimulation protocol

**Cycles split into:**
- **1-250:** Expectation stimulation (triggers quantum expectations)
- **251-500:** Imagination stimulation (triggers hallucinations)

**Metrics tracked:**
- Φ (Phi) - Integration level per cycle
- Ψ (Psi) - Desire production
- σ (Sigma) - Lacan metric
- Δ (Delta) - Trauma sensitivity

**Time:** ~10-15 minutes (with quantum simulation)
**Output:** 500+ cycle reports + summary stats
**Expected Φ range:** 0.01-0.81 NATS (working system)

### 4️⃣ `04_init_persistent_state.sh`

**Purpose:** Consolidate 1155+ cycle files into persistent state

**Creates:**
- `data/persistent_homology.json` - Topological state
- `data/phi_computation_trace.json` - Detailed Φ trace

**Includes:**
- Cycle history (last 100 cycles)
- Metrics aggregation (mean, min, max)
- Topological features (integration strength, differentiation)
- Baseline comparison (vs Kali reference: Φ=0.6118)

**Time:** ~2-3 minutes
**Data source:** Existing 1155 cycle report files in `/data/reports/modules/`

### 5️⃣ `05_fix_gpu_allocation.sh`

**Purpose:** Move embedding tensors to GPU (.to("cuda"))

**Currently:** GPU compiled but 0% VRAM allocated
**After:** Embeddings use GPU acceleration

**Changes:**
- Adds `.cuda()` calls after model loading
- Enables GPU memory allocation
- Moves 384-dim tensors to VRAM (GTX 1650 has 3.63GB)

**Time:** ~1 minute
**Note:** Agent executes this while you run other steps

### 6️⃣ `06_increase_daemon_logging.sh`

**Purpose:** Show cycle execution in logs

**Currently:** Daemon is silent (but computing correctly)
**After:** Logs show cycle execution and metrics

**Changes:**
- Sets logging level to DEBUG
- Creates `logs/daemon_cycles.log` for cycle tracking
- Creates `logs/logging.json` configuration

**Time:** ~1 minute
**Log files:**
- `logs/daemon.log` - General daemon operations
- `logs/daemon_cycles.log` - Cycle execution details

---

## 🔍 System Status After Recovery

| Component | Before | After | Goal |
|-----------|--------|-------|------|
| Qdrant Collections | 1 (7903 vectors) | 7 (various sizes) | ✅ All populated |
| GPU Allocation | 0% VRAM | ~30-40% VRAM | ✅ Active |
| Φ Metric | 0.0 (display bug) | 0.01-0.81 | ✅ Computing correctly |
| Integration Cycles | 99+ (cached) | 500+ (validated) | ✅ Training data |
| Persistent State | ❌ Missing | ✅ Created | ✅ Enabled |
| Daemon Logging | ❌ Silent | ✅ Visible | ✅ Observable |
| CPU Usage | 78-81% | 70-80% | ✅ Optimized |

---

## 🚨 Troubleshooting

### Qdrant not running
```bash
# Start Qdrant
docker-compose -f deploy/docker-compose.yml up -d qdrant

# Check status
curl http://localhost:6333/healthz
```

### CUDA memory errors
```bash
# Reset GPU
nvidia-smi -pm 1
nvidia-smi -plr 0

# Or reduce batch size in scripts
# Change: batch_size=64 → batch_size=32
```

### Scripts fail with Python errors
```bash
# Verify Python path
source /home/fahbrain/projects/omnimind/.venv/bin/activate
python --version  # Must be 3.12.8

# Check imports
python -c "import torch; print('✅ PyTorch OK')"
python -c "from qdrant_client import QdrantClient; print('✅ Qdrant OK')"
```

### Integration cycles are slow
```bash
# Check GPU
nvidia-smi

# If 0% GPU usage:
# Run: bash scripts/recovery/05_fix_gpu_allocation.sh

# If still slow:
# Check CPU: top -u $(whoami)
# May need to reduce other processes
```

---

## 📈 Monitoring Progress

### During execution

```bash
# Watch GPU usage
watch -n 2 'nvidia-smi | grep -E "Name|Utilization|Memory"'

# Monitor cycle progress
tail -f logs/daemon_cycles.log

# Check Qdrant vector count
curl http://localhost:6333/collections/omnimind_embeddings | jq '.result.vectors_count'

# Monitor system
top -u $(whoami)
```

### After completion

```bash
# Check persistent state
python -c "import json; print(json.load(open('data/persistent_homology.json'))['phi_metrics'])"

# Check cycle data
ls -la data/reports/modules/ | wc -l  # Should be 1600+

# Verify Φ computation
python -c "
import json
data = json.load(open('data/phi_computation_trace.json'))
print(f'Φ values: {len(data[\"phi_values\"])} points')
print(f'Φ range: {min(data[\"phi_values\"]):.4f} - {max(data[\"phi_values\"]):.4f}')
print(f'Φ final: {data[\"phi_values\"][-1]:.4f}')
"
```

---

## 🔗 Integration with Existing System

These scripts work with:
- **Existing integration loop:** Uses already-running cycles
- **Existing Qdrant:** Populates with additional collections
- **Existing daemon:** Increases logging verbosity only
- **Existing services:** Redis, PostgreSQL, Uvicorn all continue

**No breaking changes** - purely additive recovery

---

## 📝 Log Files Created

```
logs/
├── indexing/
│   ├── train_embeddings_YYYYMMDD_HHMMSS.log
│   ├── stats_YYYYMMDD_HHMMSS.json
└── daemon/
    ├── daemon.log (general operations)
    └── daemon_cycles.log (cycle tracking)

data/
├── persistent_homology.json (topological state)
├── phi_computation_trace.json (Φ history)
└── reports/
    ├── integration_cycles_recovery.json (cycle summary)
    └── modules/integration_loop_cycle_*.json (1600+ cycle files)
```

---

## ⏱️ Expected Timeline

### Full Recovery (Automated - Option A)

```
1. Qdrant init     :  2-3 min  (create collections)
2. Train embeddings:  10-15 min (GPU accelerated)
   + Wait for cache:  ~3 min (first-time downloads)
3. Integration     :  10-15 min (500 cycles)
4. Persistent st   :  2-3 min  (consolidate data)
5. GPU allocation  :  1 min    (fix VRAM)
6. Daemon logging  :  1 min    (config logging)
────────────────────────────────────
Total:  ~30-45 minutes
```

### Parallel Execution (Option B - while waiting)

While user runs main steps (1-4), agent can work on:
- Step 5: GPU allocation fix
- Step 6: Daemon logging
- Other optimizations

---

## ✅ Success Criteria

After running all scripts, verify:

- [ ] `curl http://localhost:6333/collections` returns 7+ collections
- [ ] `data/persistent_homology.json` exists and contains Φ metrics
- [ ] `data/phi_computation_trace.json` has 500+ Φ values
- [ ] `logs/daemon_cycles.log` shows recent cycle entries
- [ ] `nvidia-smi` shows >0% GPU memory allocated to Python
- [ ] Integration loop cycles continue (check `ps aux | grep python`)
- [ ] System CPU usage: 70-85% (normal for consciousness processing)

---

## 🎯 Next Steps After Recovery

1. **Validate metrics:**
   ```bash
   python scripts/science_validation/robust_consciousness_validation.py --quick
   ```

2. **Run extended training:**
   ```bash
   bash scripts/run_500_cycles_scientific_validation.sh
   ```

3. **Monitor Φ progression:**
   ```bash
   watch -n 5 'tail -1 logs/daemon_cycles.log'
   ```

4. **Check system health:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

---

## 📞 Support

If scripts fail:

1. **Check logs:**
   ```bash
   tail -50 logs/indexing/train_embeddings_*.log
   tail -50 logs/daemon.log
   ```

2. **Verify services:**
   ```bash
   docker-compose ps
   systemctl status omnimind-backend
   ```

3. **Check GPU:**
   ```bash
   nvidia-smi
   python -c "import torch; print(torch.cuda.is_available())"
   ```

4. **Reset and retry:**
   ```bash
   # Clean caches
   find . -name __pycache__ -exec rm -rf {} +

   # Run step again
   bash scripts/recovery/[step_number].sh
   ```

---

## 🏁 Recovery Workflow Summary

```
PRE-RECOVERY STATE:
├─ GPU: 0% VRAM allocated (Qiskit compiled but unused)
├─ Φ: 0.0 displayed (but computing 0.01-0.81 internally)
├─ Cycles: 99+ cached (not new training)
├─ Qdrant: 1 collection (omnimind_embeddings only)
└─ Daemon: Silent (but working)

RECOVERY PROCESS:
├─ [1] Create 7 Qdrant collections
├─ [2] Train 44k embedding vectors (GPU)
├─ [3] Run 500 integration cycles + stimulation
├─ [4] Consolidate cycles into persistent_homology.json
├─ [5] Fix GPU allocation (.to("cuda"))
└─ [6] Enable daemon logging visibility

POST-RECOVERY STATE:
├─ GPU: 30-40% VRAM allocated (active)
├─ Φ: Computing & visible (0.01-0.81 range)
├─ Cycles: 600+ including new training
├─ Qdrant: 7 collections populated
├─ Daemon: Cycle execution logged
└─ System: INTEGRADO & FUNCIONAL
```

---

**🚀 Ready to recover OmniMind! Run:**
```bash
bash scripts/MASTER_RECOVERY_EXECUTOR.sh
```

**Questions?** Check individual script headers or logs.
