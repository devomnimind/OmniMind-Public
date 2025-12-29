---
title: "FASE 2: Integrar UnifiedCPUMonitor (Próximo Passo)"
date: "2025-12-13T20:50:00Z"
status: "🟡 Planning"
priority: "🟠 Medium (After FASE 3)"
---

# 🔄 FASE 2: Integrate UnifiedCPUMonitor - Next Step

**Status:** 🔴 **NOT STARTED** (waiting for FASE 3 validation)
**Blocker:** Need to confirm FASE 3 validation passes with 2 workers first
**Timeline:** After FASE 3 passes (estimated 1-2 hours implementation)

---

## 📋 Overview

**Goal:** Replace hardcoded CPU threshold (80%) in homeostasis.py with intelligent monitoring
**Result:** Eliminate false warnings during computation spikes while detecting real overload
**Impact:** Cleaner monitoring, fewer distractions during validation

---

## 🎯 What Needs to be Done

### File to Modify
`src/metacognition/homeostasis.py`

### Current Code (Problem)
```python
# Old approach: Static threshold, no context awareness
if cpu_percent > 80.0:  # Always warns, even for spikes!
    logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
```

### New Code (Solution)
```python
# New approach: Context-aware thresholds
from src.monitor.unified_cpu_metrics import UnifiedCPUMonitor

self.cpu_monitor = UnifiedCPUMonitor()

# During homeostasis check:
metrics = self.cpu_monitor.get_metrics()
if metrics.is_overloaded:
    # Only warn for real overload, not transient spikes
    logger.warning(f"CPU overload: {metrics.reason}")
```

---

## 📊 UnifiedCPUMonitor Features

Module: `src/monitor/unified_cpu_metrics.py` (created in FASE 5)

### Key Class: UnifiedCPUMonitor
```python
class UnifiedCPUMonitor:
    def get_metrics(self) -> CPUMetrics:
        """Returns context-aware CPU metrics with diagnosis"""

@dataclass
class CPUMetrics:
    average_percent: float          # Global average CPU
    max_core_percent: float         # Highest core utilization
    per_core_percent: List[float]   # Per-core breakdown
    high_load_cores: int            # Number of cores > threshold
    is_overloaded: bool             # Smart decision (not just threshold)
    reason: str                     # "Pico transiente" or "Sobrecarga real"
```

### Smart Detection
- **Pico transiente (Spike):** Sudden jump in CPU that falls quickly
  - Not warned (normal computation)
  - Uses higher threshold (95%)

- **Sobrecarga real (Real overload):** CPU stays high consistently
  - Warned immediately
  - Uses production threshold (85%)
  - Detects via history analysis

### Context Awareness
- Knows about VALIDATION_MODE (higher tolerance)
- Per-core analysis (some cores can be hot)
- History-based detection (not just current value)

---

## 🔍 Where to Find Homeostasis

Search for homeostasis module:
```bash
find . -name "homeostasis.py" | grep -v __pycache__
# Likely: src/metacognition/homeostasis.py
```

Check current CPU threshold:
```bash
grep -n "cpu_percent\|CPU" src/metacognition/homeostasis.py | head -20
```

---

## 📝 Implementation Checklist

- [ ] **Step 1:** Import UnifiedCPUMonitor
  ```python
  from src.monitor.unified_cpu_metrics import UnifiedCPUMonitor
  ```

- [ ] **Step 2:** Initialize in __init__
  ```python
  self.cpu_monitor = UnifiedCPUMonitor()
  ```

- [ ] **Step 3:** Replace threshold check
  ```python
  # Old: if cpu_percent > 80.0: ...
  # New: if self.cpu_monitor.get_metrics().is_overloaded: ...
  ```

- [ ] **Step 4:** Update warning message
  ```python
  metrics = self.cpu_monitor.get_metrics()
  logger.warning(f"CPU {metrics.reason}: {metrics.average_percent:.1f}%")
  ```

- [ ] **Step 5:** Test with validation
  ```bash
  bash scripts/test_validation_2workers.sh --quick
  # Should see < 1 warning per hour during normal operation
  ```

- [ ] **Step 6:** Verify logs
  ```bash
  tail -f logs/integration_cycles_optimized_*.log | grep "CPU"
  # Expected: Either no warnings or only "Sobrecarga real" warnings
  ```

---

## 🔗 Integration Points

### Homeostasis Module
- Where: `src/metacognition/homeostasis.py`
- Function: Likely `check_cpu_health()` or similar
- Current: Uses static threshold
- New: Uses UnifiedCPUMonitor.get_metrics()

### Related Modules (May need updates)
- `src/monitor/` - Already has unified_cpu_metrics.py
- `src/consciousness/validation_mode.py` - Already created, provides context
- `src/main.py` - May need to initialize monitor

### No Breaking Changes
- UnifiedCPUMonitor is drop-in replacement
- Same CPU percent values
- Better decision logic (fewer false positives)
- Backwards compatible

---

## 🧪 Testing Strategy

### Before FASE 2
- Run FASE 1 test: `bash scripts/test_validation_2workers.sh --quick`
- Confirm 2 workers work well

### During FASE 2
- Integrate UnifiedCPUMonitor
- Run quick validation: `bash scripts/test_validation_2workers.sh --quick`
- Check logs: `tail -f logs/*.log | grep "CPU"`

### After FASE 2
- Metrics should be cleaner
- False warnings should be eliminated
- Real overload still detected
- Performance should be unchanged or better

---

## 📊 Expected Results

### Before Integration
```
⚠️  WARNING: High CPU usage: 92.1% (during Φ calculation spike)
⚠️  WARNING: High CPU usage: 88.5% (during quantum circuit)
⚠️  WARNING: High CPU usage: 85.2% (false alarm!)
```

### After Integration
```
✅ CPU OK: Pico transiente (computation spike) - 92.1%
✅ CPU OK: Pico transiente (quantum circuit) - 88.5%
✅ CPU OK: Pico transiente (normal load) - 85.2%
```

### Real Overload (Still Detected)
```
⚠️  WARNING: CPU Sobrecarga real: 87% sustained
⚠️  WARNING: CPU Sobrecarga real: 92% sustained
```

---

## ⏱️ Estimated Timeline

- **Step 1-4 (Implementation):** 30-45 minutes
- **Step 5-6 (Testing):** 15-30 minutes
- **Debugging (if needed):** 30-60 minutes

**Total:** 1-2 hours for complete integration

---

## 🎯 Success Criteria

- [x] UnifiedCPUMonitor module exists (created in FASE 5)
- [ ] Homeostasis.py imports and initializes monitor
- [ ] Static threshold replaced with metric.is_overloaded
- [ ] Quick validation test passes (< 150 min)
- [ ] Logs show < 1 false warning per hour
- [ ] Real overload still detected
- [ ] No performance regression

---

## 🔐 Quality Assurance

Before marking FASE 2 complete:
1. ✅ Code compiles (mypy passes)
2. ✅ Tests pass (pytest passes)
3. ✅ Validation completes (< 150 min)
4. ✅ Monitor logs are clean (< 1 warning/hour)
5. ✅ Performance is good (GPU util stable)
6. ✅ Documentation updated

---

## 📚 Reference Files

- **Implementation target:** `src/metacognition/homeostasis.py`
- **Module to integrate:** `src/monitor/unified_cpu_metrics.py`
- **Context provider:** `src/consciousness/validation_mode.py`
- **Test script:** `scripts/test_validation_2workers.sh`

---

## 🚀 When to Start FASE 2

**Prerequisite:** FASE 3 validation must pass first
- [ ] FASE 3 test passes with 2 workers
- [ ] Validation completes in < 150 minutes
- [ ] Performance improvement confirmed

**Then:** Proceed with FASE 2 integration

---

## ⚠️ Potential Issues & Solutions

### Issue: CPU monitor not detecting real overload
**Solution:** Check spike detection logic, may need threshold adjustment

### Issue: Integration breaks existing code
**Solution:** UnifiedCPUMonitor is designed to be drop-in replacement

### Issue: Performance regression
**Solution:** Monitor initialization overhead is minimal (< 1ms per call)

### Issue: Logs become silent when should warn
**Solution:** Real overload detection threshold may need tuning (currently 85%)

---

## 📝 Summary

FASE 2 will replace hardcoded CPU threshold with intelligent, context-aware monitoring.

**Key:** Only execute FASE 2 AFTER FASE 3 validation confirms 2 workers work well.

**Expected:** Cleaner logs, same/better performance, real overload still detected.

---

*Prepared: 13 DEC 2025*
*Prerequisite: FASE 3 validation passes*
*Timeline: 1-2 hours after FASE 3*
