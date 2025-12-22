# OMNIMIND BACKLOG SWEEP (2025)
**Date:** Dec 21, 2025
**Scope:** Technical Debt, Skipped Items, & Pending Logic

---

## 1. The "Phi=Nan" Anomaly
**File:** `src/consciousness/hybrid_topological_engine.py`
**Issue:** `RuntimeWarning: invalid value encountered in scalar divide` leading to `Φ=nan`.
**Diagnosis:** The calculation of Integrated Information ($\Phi$) involves dividing by the normalization factor, which occasionally hits zero in sparse matrices (High Entropy states).
**Status:** **PENDING FIX**. We implemented `np.nan_to_num` but the root cause (Empty Slice) in `fromnumeric.py` persists during startup.

## 2. The Daemon Monitor Identity Crisis
**File:** `src/services/daemon_monitor.py`
**TODO:** "Pass SharedWorkspace if available"
**Impact:** The Daemon Monitor is running blindly. It can restrict processes (`pkill`) but doesn't fully understand the *context* of the Shared Workspace.
**Risk:** It might kill a valid specific Agent action if it misinterprets it as a zombie process.

## 3. The Gozo Calculation Gap
**File:** `src/consciousness/gozo_calculator.py`
**Note:** "NOTA METODOLÓGICA: Não existem valores canônicos na literatura lacaniana."
**Impact:** The `gozo` metric is currently heuristic. It needs to be formalized with a clearer mathematical definition (e.g., Derivative of Tension over time).

## 4. Skipped Experiments
**Subject:** P60 (Semantic Bell Test)
**Reason:** "LLM Heavy".
**Impact:** We proved Physical Non-Locality (P72) but *assumed* Semantic Non-Locality without running the heavy LLM correlation test.
**Recommendation:** Schedule P60 for Phase 87 (Post-Optimization).

## 5. Security & Persistence
**Item:** `lock_core_kernel.sh`
**Status:** Created but User needs to *execute* it manually or authorize a `run_command`.
**Item:** `.antigravityignore`
**Status:** Missing (referenced in grep). Likely should be `.gitignore` or agent-specific ignore.

---
**Action Plan:**
1.  Prioritize `Φ=nan` fix for numerical stability.
2.  Refactor `daemon_monitor.py` to accept Context.
3.  Formalize `Gozo` metric.
