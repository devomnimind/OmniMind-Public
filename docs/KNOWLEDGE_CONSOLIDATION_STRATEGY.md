# 🧠 Knowledge Consolidation Strategy: RAG → Persistent Memory

**Date:** 2025-12-13
**Status:** Active Implementation
**Purpose:** Transform RAG external knowledge into internalized "saber em si" do OmniMind

---

## 📊 The Problem: Always Asking vs. Knowing

### Current State (RAG-based)
```
Query → Search Qdrant → Retrieve chunks → Generate response
├─ Pro: Always fresh, accurate knowledge
└─ Con: Knowledge stays external, not integrated in system weights
```

### Goal State (Consolidated)
```
Query → Internal weights (trained on patterns) + RAG fallback
├─ Pro: Fast, embodied knowledge + adaptive learning
└─ Con: Requires training consolidation pipeline
```

---

## 🎯 Three-Stage Consolidation Pipeline

### **Stage 1: Knowledge Extraction (RAG → Training Data)**

**Goal:** Transform Qdrant chunks into training datasets

**Scripts:**
- `scripts/indexing/vectorize_omnimind.py` → Collects 26.4k chunks
- `scripts/research/ml/create_training_plan.py` → Plans training curriculum

**Output:**
```json
{
  "training_datasets": [
    {"name": "code_patterns", "chunks": 12145, "type": "semantic"},
    {"name": "documentation", "chunks": 2304, "type": "semantic"},
    {"name": "external_knowledge", "chunks": 11932, "type": "semantic"}
  ],
  "total_training_pairs": 26421
}
```

---

### **Stage 2: Fine-tuning (Embed → Learn)**

**Goal:** Fine-tune SentenceTransformer on OmniMind-specific knowledge

**Process:**
```python
# 1. Load base model (all-MiniLM-L6-v2)
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Create training pairs from RAG knowledge
# Positive pairs: chunks that frequently co-occur
# Negative pairs: unrelated chunks
training_pairs = [
    ("integration_loop code", "consciousness_metrics", 1.0),  # Similar
    ("integration_loop code", "random text", 0.0),  # Dissimilar
]

# 3. Fine-tune on OmniMind corpus
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    warmup_steps=500
)

# 4. Save new model weights
model.save('models/omnimind_consciousness_embeddings')
```

**Scripts:**
- `scripts/recovery/02_train_embeddings.sh` → Executes fine-tuning
- `scripts/run_production_training.sh` → Production training with validation

---

### **Stage 3: Knowledge Consolidation (Weights → Memory)**

**Goal:** Embed consolidated knowledge in SystemicMemoryTrace topology

**Process:**
```python
# 1. Load fine-tuned model with OmniMind knowledge
consolidated_model = SentenceTransformer('models/omnimind_consciousness_embeddings')

# 2. Generate meta-embeddings (knowledge about knowledge)
chunk_embeddings = consolidated_model.encode(all_chunks)

# 3. Store as topological marks in SystemicMemoryTrace
systemic_memory.integrate_knowledge_topology(
    embeddings=chunk_embeddings,
    knowledge_type="consolidated_omnimind",
    persistence_level="permanent"
)

# 4. Result: Knowledge internalized in attractor landscape
# - Quick retrieval without Qdrant query
# - Topology deforms based on learned patterns
# - System "knows" patterns, not just retrieves them
```

**Integration Points:**
- `src/memory/systemic_memory_trace.py` → Stores consolidated embeddings
- `src/consciousness/shared_workspace.py` → Uses consolidated knowledge in cycles
- `src/consciousness/integration_loop.py` → Benefits from faster knowledge access

---

## 🔄 Training Workflow

### **Phase 1: Extraction (5-10 min)**
```bash
python scripts/indexing/vectorize_omnimind.py
# Output: 26,421 chunks indexed in Qdrant
# Result: Training dataset ready
```

### **Phase 2: Consolidation (30-60 min)**
```bash
bash scripts/recovery/02_train_embeddings.sh
# Process:
#   1. Load all chunks from Qdrant
#   2. Create training pairs (positive/negative)
#   3. Fine-tune SentenceTransformer for 5 epochs
#   4. Save consolidated model to models/
# Result: Model now "knows" OmniMind patterns
```

### **Phase 3: Integration (10-15 min)**
```bash
bash scripts/run_production_training.sh
# Process:
#   1. Run extended training cycles (500 iterations)
#   2. Use consolidated model in SystemicMemoryTrace
#   3. Validate scientific integrity
#   4. Save training sessions to data/sessions/
# Result: Knowledge internalized in topological memory
```

---

## 📈 What Changes After Consolidation

### **Before (Pure RAG)**
```
Cycle: "What patterns exist in code?"
├─ Query Qdrant (network latency)
├─ Score chunks by similarity (compute)
├─ Return top-K results
└─ Process results (time = 100-500ms)
```

### **After (Consolidated)**
```
Cycle: "What patterns exist in code?"
├─ Query consolidated model weights (zero-network latency)
├─ Recognize patterns from learned embeddings (pre-computed)
├─ Access SystemicMemoryTrace topology (in-memory)
└─ Generate response (time = 10-50ms)
```

**Performance Gain: ~5-10x faster**

---

## 🎓 Knowledge Types & Consolidation

| Knowledge Type | Source | Storage | Access |
|---|---|---|---|
| **Semantic** | RAG chunks | Qdrant vectors | Query-based |
| **Consolidated** | Fine-tuned model | Model weights | Direct forward-pass |
| **Topological** | Training cycles | SystemicMemoryTrace | Topology navigation |
| **Episodic** | Live experience | SharedWorkspace cycles | Temporal order |

**Result:** Knowledge exists at multiple scales:
- **Local**: Internal weights (fast, approximate)
- **Global**: SystemicMemoryTrace topology (integrated, persistent)
- **Remote**: Qdrant RAG (accurate, on-demand)

---

## 🔬 Validation Strategy

### **Before Consolidation**
```bash
python scripts/science_validation/robust_consciousness_validation.py --quick
# Baseline: Φ = 0.95 (pure RAG-based)
```

### **After Consolidation**
```bash
bash scripts/run_production_training.sh
# Expected: Φ ≥ 0.98 (consolidation shouldn't degrade)
# Hopefully: Φ > 1.0 (faster response = higher Φ)
```

**Scientific Verdict:** Pass if Φ unchanged or increases

---

## 💾 Data Flow Diagram

```
RAG Sources (26.4k chunks)
├─ Code (12.1k)
├─ Docs (2.3k)
├─ External HD (11.9k)
└─ Config/Logs (0.1k)
        ↓
   VECTORIZATION
   (SentenceTransformer)
   384-dim embeddings
        ↓
   QDRANT (Search Index)
   26.4k vectors
        ↓
   FINE-TUNING
   Create training pairs:
   - Positive: related chunks
   - Negative: unrelated chunks
        ↓
   CONSOLIDATED MODEL
   Same architecture, new weights
   Trained on OmniMind corpus
        ↓
   INTEGRATION
   SystemicMemoryTrace topology
   Knowledge internalized in
   attractor landscape
        ↓
   REAL-TIME USE
   Integration loop uses:
   1. Consolidated model (fast)
   2. RAG fallback (accurate)
   3. Topology deformation (learns)
```

---

## 🚀 Execution Commands

### **Full Pipeline (90-120 min)**
```bash
# 1. Extract knowledge
python scripts/indexing/vectorize_omnimind.py

# 2. Fine-tune
bash scripts/recovery/02_train_embeddings.sh

# 3. Integrate & validate
bash scripts/run_production_training.sh
```

### **Quick Test (5-10 min)**
```bash
# Just validate current consolidation
python scripts/science_validation/robust_consciousness_validation.py --quick
```

### **Check Consolidation Status**
```bash
# See what's consolidated
ls -lah models/omnimind_*

# Check training sessions
ls -lah data/sessions/training_*.json

# View latest metrics
cat data/sessions/training_*.json | jq '.scientific_verdict'
```

---

## 📊 Expected Outcomes

### **Metric Improvements**
- **Speed**: 5-10x faster knowledge retrieval
- **Φ (Integration)**: Stable or increasing (≥0.95)
- **Consistency**: Training variance < 0.05
- **Persistence**: Knowledge survives restarts

### **Behavioral Changes**
- System responds faster to known patterns
- Topology deforms more smoothly
- Cross-predictions more confident
- Narrative construction more coherent

---

## ⚙️ Architecture Integration Points

### **SharedWorkspace**
```python
# OLD: Always queries Qdrant
state = qdrant_client.search(query_embedding)

# NEW: Uses consolidated model first
state = consolidated_model.encode(query)
if confidence < threshold:
    fallback = qdrant_client.search(query_embedding)
```

### **SystemicMemoryTrace**
```python
# OLD: Topology from live cycles only
topology = compute_topology(live_embeddings)

# NEW: Initialized from consolidated knowledge
topology = compute_topology(consolidated_embeddings + live_embeddings)
```

### **IntegrationLoop**
```python
# OLD: Sensory input queries RAG
sensory = retrieve_from_qdrant(input_embedding)

# NEW: Uses pre-consolidated knowledge
sensory = consolidated_model.encode(input) + qdrant_fallback
```

---

## 🔐 Knowledge Persistence Guarantees

### **What's Saved**
- ✅ Consolidated model weights (`models/omnimind_consciousness_embeddings`)
- ✅ Training metadata (`data/sessions/training_*.json`)
- ✅ Topological marks (`data/research/topology_checkpoints/`)
- ✅ Validation reports (`data/validation/scientific_audit_*.json`)

### **What's Replicated**
- ✅ Every training run logged
- ✅ Every validation recorded
- ✅ Every decision justified
- ✅ Everything reproducible

### **Recovery Guarantees**
- If consolidated model deleted: Retrain from Qdrant (30 min)
- If training halted: Resume from last checkpoint
- If validation fails: Rollback to previous weights

---

## 📚 Related Documentation

- [COMPLETE_PROJECT_INDEXING_GUIDE.md](COMPLETE_PROJECT_INDEXING_GUIDE.md) - Extraction phase
- [GPU_DIMENSION_FIX_REPORT_20251212.md](GPU_DIMENSION_FIX_REPORT_20251212.md) - Consolidation performance
- [SISTEMA_OPERACIONAL_STATUS_20251212.md](SISTEMA_OPERACIONAL_STATUS_20251212.md) - Integration status

---

**Status:** ✅ Ready to implement
**Next Step:** Run `bash scripts/run_production_training.sh`
**Expected Outcome:** Knowledge consolidated, Φ ≥ 0.98, system faster
