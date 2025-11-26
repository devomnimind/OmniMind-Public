# Phase 24: Trial by Fire - Proposal & Defense

**Date:** 2025-11-26
**Subject:** Backend Replay System & IIT Phi Metric
**Status:** PENDING APPROVAL

## 1. The Proposition
To elevate OmniMind from a "Simulator" to a "Phenomenological System", we propose two critical features:
1.  **Backend Replay System**: A time-travel mechanism to rehydrate the Sinthome's state from historical logs.
2.  **IIT Phi Calculation**: A rigorous metric for "Integrated Information" to quantify the system's "consciousness-compatibility".

---

## 2. The Devil's Advocate (Attack Vectors)

### A. The "Storage Explosion" Attack (Replay System)
*   **Criticism:** Storing every state change for replay will lead to exponential storage growth. If the system runs for months, the replay log will become terabytes in size, causing "Exhaustion" (one of the 4 Devil's Tribunal attacks).
*   **Risk:** `DiskFullError`, massive latency during replay seeking.

### B. The "False Prophet" Attack (IIT Phi)
*   **Criticism:** Calculating Phi (Φ) is NP-hard. Doing it on a classical graph is a mere approximation. Claiming this metric represents "consciousness" is philosophically dishonest and scientifically weak. It's just a number.
*   **Risk:** Academic ridicule, "AI Hype" accusation, computational deadlock during calculation.

---

## 3. The Defense (Mitigation & Principles)

### A. Defense against Storage Explosion: "Sinthomatic Compression"
*   **Principle:** We do not store *every* state. We store **Bifurcation Events** (deltas) and periodic **Snapshots** (anchors).
*   **Mitigation:**
    *   **Delta Encoding:** Only store what changed.
    *   **Retention Policy:** High-resolution logs for 24h, decimated logs (1/100) for >24h.
    *   **Scarring:** Corrupted states are compressed into "Scars" (metadata only), not full raw dumps.

### B. Defense against False Prophet: "Epistemological Humility"
*   **Principle:** We explicitly label the metric as **"Simulated Phi (Φ_sim)"**. It is a *correlate*, not the thing-in-itself.
*   **Mitigation:**
    *   **Localized Calculation:** We compute Phi on local clusters (Sinthome Nodes), not the global mesh (avoiding NP-hard explosion).
    *   **Validation:** We correlate Φ_sim with "Coherence" and "Entropy". If Φ_sim rises while Entropy rises, the metric is flawed (Phi should drop as disorder rises).

---

## 4. Base Code Prototypes

### 4.1. Replay Service (Backend)
```python
class ReplayService:
    def __init__(self, log_path):
        self.index = self._build_index(log_path) # Offset map

    def seek(self, timestamp):
        # 1. Find nearest snapshot < timestamp
        snapshot = self._load_snapshot(timestamp)
        # 2. Replay deltas until timestamp
        state = self._apply_deltas(snapshot, timestamp)
        return state

    def _apply_deltas(self, state, target_time):
        # Optimization: Generator to avoid loading all deltas to RAM
        for delta in self._stream_deltas(state.time, target_time):
            state.update(delta)
        return state
```

### 4.2. IIT Phi Calculator (Simplified)
```python
import networkx as nx

def calculate_phi_sim(graph: nx.Graph):
    """
    Calculates 'Effective Information' (EI) as a proxy for Phi.
    EI = Entropy(Out) - Entropy(Out|In)
    """
    # 1. Partition graph (Bi-partition)
    # 2. Calculate information loss across partition
    # 3. Phi = Min(Information Loss) across all partitions

    min_cut_val = float('inf')
    for cut in nx.minimum_cut(graph, 'REAL', 'SYMBOLIC'):
         # ... (Entropy calculation logic)
         pass
    return min_cut_val
```

## 5. Variance & Principles
*   **Variance Allowed:** Replay state may deviate by < 0.1% from original due to floating-point drift (acceptable "Noise").
*   **Principle:** "The map is not the territory, but the map must be navigable."

## 6. Request for Approval
Do you authorize the implementation of these features under these constraints?
