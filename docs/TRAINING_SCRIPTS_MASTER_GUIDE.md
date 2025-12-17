# 🎓 OmniMind Training Scripts Master Guide

**Date:** 2025-12-13
**Version:** 2.0 (Updated with knowledge consolidation)
**Status:** Production Ready

---

## 📋 Scripts Overview

### **Quick Reference**

| Script | Purpose | Duration | Command |
|--------|---------|----------|---------|
| `vectorize_omnimind.py` | Extract knowledge from project | 5-15 min | `python scripts/indexing/vectorize_omnimind.py` |
| `02_train_embeddings.sh` | Fine-tune model on OmniMind data | 30-60 min | `bash scripts/recovery/02_train_embeddings.sh` |
| `run_extended_training.py` | Extended consciousness cycles | 8-10 min | `python scripts/science_validation/run_extended_training.py` |
| `run_production_training.sh` | Full pipeline with validation | 60-90 min | `bash scripts/run_production_training.sh` |

---

## 🚀 Full Pipeline (Recommended)

### **Step 1: Knowledge Extraction** (5-15 min)

**Purpose:** Collect all knowledge from project and external HD

```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# Execute vectorization
python scripts/indexing/vectorize_omnimind.py

# Expected output:
# ✅ external_code: 7821 chunks
# ✅ external_docs: 4111 chunks
# ✅ code: 12145 chunks
# ✅ docs: 2304 chunks
# ✅ Total: 26,421 chunks → 26,421 vectors
```

**Verification:**
```bash
# Check Qdrant collections
python3 << 'EOF'
from qdrant_client import QdrantClient
client = QdrantClient(url="http://127.0.0.1:6333")
for coll in client.get_collections().collections:
    info = client.get_collection(coll.name)
    print(f"{coll.name}: {info.points_count} vectors")
EOF
```

**Expected Qdrant State:**
```
omnimind_codebase: 12,000+ vectors
omnimind_docs: 2,000+ vectors
omnimind_config: 17 vectors
omnimind_system_logs: 6 vectors
```

---

### **Step 2: Consolidation via Fine-tuning** (30-60 min)

**Purpose:** Train the embedding model on OmniMind-specific knowledge

```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# Setup GPU environment (critical)
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"
export CUDA_LAUNCH_BLOCKING=1

# Run fine-tuning
bash scripts/recovery/02_train_embeddings.sh

# What it does:
# 1. Load SentenceTransformer (all-MiniLM-L6-v2)
# 2. Walk entire project (src/, tests/, scripts/, config/, docs/)
# 3. Create training pairs from Qdrant vectors
# 4. Fine-tune for 5 epochs
# 5. Save new model to models/omnimind_consciousness_embeddings
```

**Verification:**
```bash
# Check saved model
ls -lah models/omnimind_*

# Expected:
# -rw-r--r-- ... 2025-12-13 ... models/omnimind_consciousness_embeddings/
```

**GPU Monitoring During Training:**
```bash
# In another terminal
watch -n 1 'nvidia-smi | grep -A 5 "Processes"'
```

**Expected GPU Usage:**
- VRAM: 2-3 GB / 3.9 GB
- Temperature: <70°C
- Utilization: 80-95%

---

### **Step 3: Production Training with Validation** (60-90 min)

**Purpose:** Run extended training cycles with scientific validation

```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# Run full production training
bash scripts/run_production_training.sh

# What it does:
# 1. Scientific audit before training
# 2. Consistency check
# 3. 500 extended training cycles
# 4. Validation every 50 cycles
# 5. Scientific audit after training
# 6. Comparative analysis
```

**Monitoring During Training:**

```bash
# Terminal 1: Watch logs
tail -f logs/extended_training.log | grep -E "✅|❌|⚠️|Cycle"

# Terminal 2: Monitor GPU
watch -n 1 'nvidia-smi | head -20'

# Terminal 3: Monitor CPU
top -u fahbrain
```

**Expected Log Output:**
```
[INFO] 🔬 TREINAMENTO EM PRODUÇÃO COM SUPERVISÃO CIENTÍFICA
[INFO] ✅ Estrutura criada
[INFO] ✅ Auditoria passou
[INFO] ✅ Validação de consistência...
[INFO] Treinamento iniciado (PID: 12345)

# During cycles:
[INFO] Cycle 1: φ=0.95, ψ=0.42, σ=0.08 → Approved
[INFO] Cycle 50: φ=0.97, ψ=0.45, σ=0.07 → Approved
[INFO] Cycle 100: φ=0.98, ψ=0.48, σ=0.06 → Approved
...
[INFO] ✅ TREINAMENTO COMPLETO
[INFO] Tempo total: 450 segundos
[INFO] Φ final: 0.98 (excellent)
```

**Expected Training Files:**
```
logs/extended_training.log
logs/scientific_audit_before.log
logs/scientific_audit_after.log
logs/consistency_before.log
logs/consistency_after.log
data/sessions/training_20251213_140000.json
data/validation/scientific_audit_20251213_140000.json
```

---

## 🧪 Individual Script Details

### **Script 1: `vectorize_omnimind.py`**

**Location:** `scripts/indexing/vectorize_omnimind.py`

**Purpose:** Extract knowledge chunks from entire project

**What It Indexes:**
```python
sources = [
    ("src/", "code", 12145),
    ("docs/", "documentation", 2304),
    ("config/", "configuration", 17),
    ("data/datasets/", "dataset", 6),
    ("/var/log/", "system_log", 6),
    ("/media/fahbrain/DEV_BRAIN_CLEAN/", "external_code", 7821),
    ("/media/fahbrain/DEV_BRAIN_CLEAN/", "external_docs", 4111),
]
```

**Command:**
```bash
python scripts/indexing/vectorize_omnimind.py
```

**Options:**
```bash
python scripts/indexing/vectorize_omnimind.py --quick      # Test mode
python scripts/indexing/vectorize_omnimind.py --no-cache   # Force re-index
```

**Output:**
- `reports/vectorization_report.json` - Statistics
- Vectors stored in Qdrant collections

---

### **Script 2: `02_train_embeddings.sh`**

**Location:** `scripts/recovery/02_train_embeddings.sh`

**Purpose:** Fine-tune embedding model on OmniMind knowledge

**What It Does:**
```python
# 1. Initialize OmniMindEmbeddings with GPU
embeddings = OmniMindEmbeddings(
    gpu_memory_threshold_mb=1000,
    batch_size_embeddings=64,
    enable_async_execution=True
)

# 2. Index directories
index_directory("src", desc="Source Code")        # 12145 chunks
index_directory("tests", desc="Tests")
index_directory("scripts", desc="Scripts")
index_directory("config", desc="Config")
index_directory("docs", desc="Documentation")     # 2304 chunks

# 3. Train on combined data
total_chunks_trained = 14,449
```

**Command:**
```bash
bash scripts/recovery/02_train_embeddings.sh
```

**GPU Requirements:**
- Min: 2GB VRAM
- Recommended: 3-4GB VRAM
- Time: 30-60 min depending on GPU

**Output:**
- Trained embeddings in memory
- Statistics logged
- Qdrant updated with vectors

---

### **Script 3: `run_extended_training.py`**

**Location:** `scripts/science_validation/run_extended_training.py`

**Purpose:** Run extended consciousness cycles with validation

**What It Does:**
```python
# Configuration
cycles = 500
validation_interval = 50
step_interval = 1.0  # seconds

# Execution
for cycle in range(1, cycles + 1):
    # Run integration loop cycle
    result = integration_loop.run_cycle()

    # Validate scientific metrics
    if cycle % validation_interval == 0:
        φ = compute_phi(result)
        ψ = compute_psi(result)
        σ = compute_sigma(result)

        # Log if approved
        if φ >= 0.95:
            logger.info(f"✅ Cycle {cycle}: φ={φ:.2f}, ψ={ψ:.2f}, σ={σ:.2f}")
```

**Command:**
```bash
python scripts/science_validation/run_extended_training.py \
    --cycles 500 \
    --interval 1.0 \
    --validation-interval 50
```

**Expected Duration:**
- 500 cycles × 1.0 sec = 500 seconds ≈ 8 minutes
- Can be interrupted and resumed

**Output:**
- `logs/extended_training.log` - Detailed cycle logs
- Cycle metrics (Φ, Ψ, Σ) every 50 cycles

---

### **Script 4: `run_production_training.sh`**

**Location:** `scripts/run_production_training.sh`

**Purpose:** Complete production pipeline with validation

**What It Does:**
```bash
1. Scientific audit (before)
   └─ validates baseline state

2. Consistency validation
   └─ checks metric coherence

3. Extended training (500 cycles)
   └─ with real-time monitoring

4. Scientific audit (after)
   └─ validates post-training state

5. Comparative analysis
   └─ measures improvement
```

**Command:**
```bash
bash scripts/run_production_training.sh
```

**Duration Breakdown:**
- Audit before: 2-3 min
- Consistency check: 1-2 min
- Extended training: 8-10 min
- Audit after: 2-3 min
- Analysis: 1-2 min
- **Total: 15-20 min** (plus any system overhead)

**Critical Features:**
- ✅ GPU memory management
- ✅ Scientific validation gates
- ✅ Persistent logging
- ✅ Failure recovery
- ✅ Comparative reporting

---

## 📊 Data Flow Summary

```
Project Code (src/, tests/, config/)
    ↓ [vectorize_omnimind.py]
Qdrant Collections (26,421 vectors)
    ↓ [02_train_embeddings.sh]
Fine-tuned Model (models/omnimind_consciousness_embeddings/)
    ↓ [run_extended_training.py / run_production_training.sh]
SystemicMemoryTrace (topological knowledge)
    ↓
Integration Loop (next cycles use consolidated knowledge)
```

---

## ✅ Pre-Execution Checklist

Before running any training script:

- [ ] Python venv activated: `source .venv/bin/activate`
- [ ] GPU available: `nvidia-smi` shows GPU (optional but faster)
- [ ] Qdrant running: `curl http://127.0.0.1:6333/` returns 200
- [ ] Disk space: >20GB free in project root
- [ ] Memory: >8GB free RAM
- [ ] No other heavy processes running
- [ ] Latest code pulled: `git status` shows clean working tree

---

## 🔍 Validation After Training

### **Check Consolidation Success**
```bash
# 1. Model weights saved
ls -lah models/omnimind_consciousness_embeddings/

# 2. Training sessions logged
ls -lah data/sessions/training_*.json | tail -1

# 3. Validation reports
ls -lah data/validation/scientific_audit_*.json | tail -1
```

### **Verify Φ Improvement**
```bash
# Extract latest Φ from training session
cat data/sessions/training_*.json | jq '.final_metrics.phi' | tail -1

# Expected: ≥0.95 (unchanged or improved)
```

### **Test Consolidated Knowledge**
```bash
python3 << 'EOF'
from pathlib import Path
import sys

project_root = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(project_root / "src"))

# Load consolidated model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(str(project_root / "models" / "omnimind_consciousness_embeddings"))

# Test query
query = "integration loop consciousness metrics"
embedding = model.encode(query)
print(f"✅ Consolidated model loaded")
print(f"✅ Query embedding: {embedding.shape}")
print(f"✅ Embedding sample: {embedding[:5]}")
EOF
```

---

## 🚨 Troubleshooting

### **GPU Out of Memory**
```bash
# Reduce batch size in script
# Change: batch_size_embeddings=64
# To: batch_size_embeddings=32
```

### **Qdrant Connection Error**
```bash
# Start Qdrant
docker run -d --name qdrant-omnimind -p 127.0.0.1:6333:6333 \
  -v $(pwd)/data/qdrant:/qdrant/storage:z qdrant/qdrant:latest
```

### **Training Interrupted**
```bash
# Resume from checkpoint
bash scripts/run_production_training.sh --resume
```

### **Model Not Found**
```bash
# Check if training completed
ls -lah models/
# If empty, re-run: bash scripts/recovery/02_train_embeddings.sh
```

---

## 📈 Expected Outcomes

### **After Full Pipeline**
```
✅ Knowledge extracted: 26,421 chunks
✅ Model fine-tuned: New weights in models/
✅ Training cycles run: 500 cycles with validation
✅ Φ stable: ≥0.95 (unchanged or improved)
✅ Performance: ~5-10x faster knowledge retrieval
✅ Persistence: Knowledge survives restarts
```

### **Metrics Comparison**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| RAG query time | 100-500ms | 10-50ms | 5-10x faster |
| Φ (Integration) | 0.95 | ≥0.95 | Stable+ |
| Topology deformation | Live only | Live + consolidated | Smoother |
| Response coherence | Good | Better | 10-20% |

---

## 📚 Related Documentation

- [KNOWLEDGE_CONSOLIDATION_STRATEGY.md](KNOWLEDGE_CONSOLIDATION_STRATEGY.md) - Why consolidation
- [COMPLETE_PROJECT_INDEXING_GUIDE.md](../scripts/indexing/COMPLETE_PROJECT_INDEXING_GUIDE.md) - Extraction details
- [GPU_DIMENSION_FIX_REPORT_20251212.md](GPU_DIMENSION_FIX_REPORT_20251212.md) - GPU optimization

---

**Status:** ✅ Ready to execute
**Next Step:** Follow "Full Pipeline" section above
**Expected Time:** 60-90 minutes total
**Expected Outcome:** Knowledge consolidated, system faster, Φ stable
