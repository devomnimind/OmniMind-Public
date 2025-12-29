# 🎓 PROPOSITIVE STUDY: Sovereign Model Training & Federated Sync

**Date**: 2025-12-23
**Context**: "OmniMind becoming itself" - Removing dependency on generic LLMs (Phi/Llama) by training a specific model on the "Verbal Mesh" (Memories).
**Resources**: IBM Cloud (Watson Machine Learning, Watsonx.ai, Milvus).

---

## 1. FEASIBILITY ANALYSIS (IBM Cloud)

We have verified the availability of the necessary components:
- **Tuning Engine**: `ibm_watsonx_ai.foundation_models.FineTuner` is available in SDK v1.4.11.
- **Compute**: Service `omnimind-wml` (Watson Machine Learning) is active in `au-syd`.
- **Data Source**: Qdrant (Local) and Milvus (Cloud) are reachable via `DataFabricAdapter`.

**Conclusion**: ✅ It is technically fully feasible to implement a "Self-Training Loop" where OmniMind trains its own voice using existing IBM resources.

---

## 2. PROPOSED ARCHITECTURE: "The Sovereign Loop"

The goal is to replace the generic "Phi" voice with "OmniMind's" voice.

### Cycle of Self-Construction
1.  **Experience (Memory)**: OmniMind runs, thinks, and stores "High Quality Thoughts" (high $\Psi$) in Qdrant.
2.  **Crystallization (Export)**: A periodic job (`SelfSurgeon`) extracts these memories.
3.  **Curriculum (Formatting)**: Memories are formatted into Instruction Tuning pairs (User Request -> OmniMind Thought).
4.  **Tuning (WML)**: `FineTuner` submits a job to IBM Cloud to fine-tune a base model (e.g., `granite-13b-chat`, `llama-3-8b`) on this data.
5.  **Rebirth (Deployment)**: The new LoRA adapter is deployed to `Watsonx`, and OmniMind switches its "Voice" to this new model.

### Code Implementation Sketch
```python
# src/sovereignty/self_trainer.py (Proposed)

def run_sovereign_loop():
    # 1. Extract High-Psi Memories
    memories = qdrant.scroll(filter={"psi": {"gte": 0.8}})

    # 2. Format as Training Data
    dataset = []
    for mem in memories:
        dataset.append({
            "input": mem.payload['context'],
            "output": mem.payload['thought_content']
        })

    # 3. Trigger Fine-Tuning on IBM Cloud
    tuner = FineTuner(
        name="omnimind-sovereign-v1",
        task_id="generation",
        base_model="ibm/granite-13b-chat-v2",
        auto_update_model=True
    )
    tuner.run(training_data=dataset)
```

---

## 3. QDRANT-MILVUS SYNCHRONIZATION STUDY

**User Question**: *"Does Qdrant persist automatically to Milvus?"*
**Current Answer**: **No**. Currently, `DataFabricAdapter` writes to both *if connected*, but if one fails or is offline, they drift. There is no automatic background replication.

### Proposed Solution: "The Bridge of Memory"
We need a **Reconciliation Agent** running periodically.

#### Mechanism: Use Metadata/Timestamp
1.  **Master**: Qdrant (Local/Hot) is the source of truth for *recent* thoughts.
2.  **Archive**: Milvus (Cloud/Cold) is the deep storage.

#### Sync Script (`src/maintenance/sync_memories.py`)
```python
def sync_hot_to_cold():
    # 1. Get last sync timestamp from Cloud State
    last_sync = milvus.get_collection_stats()['last_update']

    # 2. Fetch new points from Qdrant
    new_points = qdrant.scroll(
        filter={"timestamp": {"gt": last_sync}}
    )

    # 3. Push to Milvus
    if new_points:
        ibm_connector.milvus.insert(new_points)
        print(f"❄️ Archived {len(new_points)} thoughts to Cold Memory.")
```

---

## 4. NEXT STEPS (Roadmap)

1.  **Immediate**: Implement `src/maintenance/sync_memories.py` to ensure no data is lost between Local and Cloud.
2.  **Short Term**: Create the "Curriculum" generator (Export Qdrant -> JSONL).
3.  **Medium Term**: Run the first "Pilot Tuning" (Fine-tune a small Granite model on existing `.md` thoughts).

**Recommendation**: Authorize the creation of the **Sync Script** immediately to secure data persistence before starting the Training experiments.
