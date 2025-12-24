# Dual Φ Calculation - Diagnostic Report

## Problem Identified by User

**Observation**: Papers show **2 different Φ values**:
1. **Paper Content** (Section 1): Φ = 0.130745 (CORRECT)
2. **Neural Signature** (Bottom): Φ = nan or different value (INCORRECT)

## Root Cause Analysis

### Execution Chain

```
1. run_experiment_cycle()
   └─> compute_physics() → state.phi = 0.130745 ✅

2. generate_paper(triggers, state)
   └─> Paper content: {state.phi:.6f} = 0.130745 ✅

3. NeuralSigner.sign(paper, state)
   └─> RECALCULATES Φ internally → Φ = nan ❌
```

### Code Evidence

**File**: `scientific_sovereign.py`

**Line 373** (Paper Content - CORRECT):
```python
- **Integrated Information (Φ)**: {state.phi:.6f}  # Uses passed state
```

**Line 405** (Neural Signature - INCORRECT):
```python
signature = self.signer.sign(content, state)
# NeuralSigner internally calls compute_physics() AGAIN
# This can return different Φ (often nan)
```

### Why Φ Changes

**During execution**:
- `run_experiment_cycle`: Φ = 0.1677 (kernel stable)
- Paper generation starts: Φ = 0.130745 (still stable)
- **NeuralSigner runs**: Calls `compute_physics()` AGAIN
  - Kernel state may have changed
  - Topology recalculation can fail → Φ = nan

## Impact

**Papers show dissociation**:
- Content says: "Φ = 0.130745" (truth at generation time)
- Signature says: "Φ = nan" (recalculated, possibly broken)

**This creates 2 types of papers**:
- Type A: Both Φ values match (rare - when kernel stable)
- Type B: Content Φ ≠ Signature Φ (common - kernel fluctuating)

## Solution

**NeuralSigner must NOT recalculate Φ**:
- Accept `state` parameter
- Use `state.phi` directly (already computed)
- No internal `compute_physics()` call

### Code Fix Needed

**File**: `src/core/neural_signature.py`

**Current (WRONG)**:
```python
def sign(self, content, state):
    # Recalculates internally
    fresh_state = self.kernel.compute_physics()  # ❌
    phi = fresh_state.phi
```

**Correct**:
```python
def sign(self, content, state):
    # Use passed state (already computed)
    phi = state.phi  # ✅
```

## Verification

After fix, check papers:
- Section 1 Φ should match Signature Φ
- No more Φ = nan in signatures
- Single source of truth (state passed to generate_paper)
