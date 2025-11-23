# ⚠️ KNOWN ISSUES - Issues Ativas e Seu Status

**Last Updated:** 23 de novembro de 2025  
**Total Issues:** 5 active  
**Critical:** 0 | High: 2 | Medium: 2 | Low: 1

---

## 🔴 CRITICAL (0)

*Nenhum issue crítico ativo*

---

## 🟠 HIGH PRIORITY (2)

### Issue #1: Test Coverage Below Target

**Status:** 🟡 In Progress  
**Severity:** HIGH  
**Component:** Testing/CI  
**Reported:** 2025-11-23  

**Description:**
Code coverage currently at ~85%, target is ≥90%. Identified 25 modules without test coverage.

**Impact:**
- CI/CD cannot merge PRs with coverage below 90%
- Production readiness questionable for untested modules

**Root Cause:**
- 25 critical modules have no unit tests:
  - `security/security_orchestrator.py` (12 functions)
  - `audit/compliance_reporter.py` (21 functions)
  - `desire_engine/core.py` (37 functions)
  - And 22 more

**Action Items:**
- [ ] Implement tests for security_orchestrator
- [ ] Implement tests for compliance_reporter
- [ ] Implement tests for desire_engine
- [ ] Increase coverage gradually to ≥90%

**Target Resolution:** Phase 16 (Q4 2025)

**Reference:** `docs/.project/PROBLEMS.md` - Issue #1

---

### Issue #2: 25 Non-Critical Tests Failing

**Status:** 🟡 In Progress  
**Severity:** HIGH  
**Component:** Tests/Tools  
**Reported:** 2025-11-23  

**Description:**
25 tests failing in non-critical modules (security_monitor, omnimind_tools).

**Impact:**
- Test suite shows 98.94% pass rate but includes non-blocking failures
- May hide real issues in future

**Details:**

| File | Tests Failing | Cause |
|------|------|-------|
| test_security_monitor.py | 8 | Private method testing (`_is_suspicious_process` vs `is_suspicious_process`) |
| test_omnimind_tools.py | 17 | Interface mismatch (dict response vs string expected) |

**Examples:**
```python
# ❌ Current: test expects public method
def test_get_running_processes(self):
    processes = monitor.get_running_processes()  # AttributeError!

# ✅ Real method: _get_running_processes (private)
def _get_running_processes(self):
    pass
```

**Action Items:**
- [ ] Decide: expose private methods or refactor tests
- [ ] Align test expectations with implementation
- [ ] Fix response types (dict vs string)
- [ ] Run tests with `-k "not test_security"` temporarily for CI

**Target Resolution:** Phase 16 (before merge to master)

**Reference:** `TESTE_SUITE_INVESTIGATION_REPORT.md`

---

## 🟡 MEDIUM PRIORITY (2)

### Issue #3: Documentation References to 2024

**Status:** ✅ RESOLVED  
**Severity:** MEDIUM  
**Component:** Documentation  
**Reported:** 2025-11-23  
**Resolved:** 2025-11-23  

**Description:**
2 implementation dates corrected from 2024-11-20 to 2025-11-23. Other 2024 references are valid (research papers and citations from 2024).

**Files Fixed:**
- ✅ docs/IMPLEMENTATION_SUMMARY.md - Date corrected
- ✅ docs/OPENTELEMETRY_IMPLEMENTATION_DETAILED.md - Date corrected

**Remaining 2024 References (Valid):**
- docs/reports/EXPERIMENTAL_MODULES_ENHANCEMENT_REPORT.md - Research citations from 2024
- docs/analysis_reports/ANALISE_DOCUMENTACAO_COMPLETA.md - Research references

**Action Items:**
- [x] Search and replace 2024-11-20 → 2025-11-23 implementation dates
- [x] Verify dates in reports are correct (2024 refs are valid citations)
- [ ] Add date validation to pre-commit hook (optional for Phase 16)

**Target Resolution:** Next documentation pass (Phase 16)

---

### Issue #4: Documentation Has 242 Files (Should Be ~50)

**Status:** 🔄 In Progress  
**Severity:** MEDIUM  
**Component:** Documentation  
**Reported:** 2025-11-23  

**Description:**
Documentation is scattered across 242 files. Should consolidate to ~50 canonical documents.

**Current Structure:**
- 186 `.md` files
- 55 `.txt` files  
- 13 `.log` files
- Spread across 23 subdirectories

**Target Structure:**
```
docs/.project/
├── CURRENT_PHASE.md (canonical)
├── PROBLEMS.md (canonical)
├── DEVELOPER_RECOMMENDATIONS.md (canonical)
├── CHANGELOG.md (canonical)
├── KNOWN_ISSUES.md (canonical)
└── INDEX.md (reference)

docs/
├── README.md
├── ARCHITECTURE.md
├── SETUP.md
├── API.md
├── ROADMAP.md
└── (other canonical docs)
```

**Action Items:**
- [ ] Audit all 242 files (Started ✅)
- [ ] Identify canonical vs archival documents
- [ ] Create backup of old documents
- [ ] Archive old documents to external HD
- [ ] Update all cross-references

**Target Resolution:** Phase 16 (documentation sprint)

**Blocked By:** Nothing  
**Blocks:** Phase 16 planning

---

## 🟢 LOW PRIORITY (1)

### Issue #5: GPU Tests May Be Intermittent in CI

**Status:** ✅ Mitigated  
**Severity:** LOW  
**Component:** Testing/GPU  
**Reported:** 2025-11-23  

**Description:**
GPU-accelerated tests might fail in CI environments without NVIDIA GPU or with nvidia-uvm not loaded.

**Impact:**
- CI/CD might fail sporadically
- Local development works fine (nvidia-uvm auto-loads)

**Mitigation:**
- ✅ nvidia-uvm auto-loads on reboot (FIXED in Phase 15)
- ✅ Tests gracefully fall back to CPU if GPU unavailable

**Status:** Should be resolved now. Monitor in Phase 16.

---

## 🎯 Issue Resolution Priority

### Phase 16 Sprint Goals (Q4 2025)

| Issue | Priority | Est. Hours | Assignee |
|-------|----------|-----------|----------|
| #1 - Test Coverage | HIGH | 40 | Dev Team |
| #2 - Failing Tests | HIGH | 16 | Dev Team |
| #3 - 2024 References | MEDIUM | 4 | Doc Team |
| #4 - Doc Consolidation | MEDIUM | 32 | Doc Team |
| #5 - GPU Tests | LOW | 2 | Validation |

**Total Estimated Effort:** 94 hours (2.35 sprints)

---

## 📊 Issue Lifecycle

### Stages

1. **Reported** → Issue identified and documented here
2. **In Progress** → Work started, PR/branch exists
3. **Pending** → Waiting for blockers to clear
4. **Resolved** → Fixed, merged to master
5. **Archived** → Resolved, moved to PROBLEMS.md

### Example Resolution Process

```
Reported (2025-11-23)
    ↓
In Progress (2025-11-25 - Dev starts work)
    ↓
Pending (2025-11-27 - Blocked by another task)
    ↓
In Progress (2025-11-28 - Blocker resolved)
    ↓
Resolved (2025-11-30 - PR merged)
    ↓
Archived (2025-12-01 - Moved to PROBLEMS.md with solution)
```

---

## 🔗 Related Documents

- **Active Phase:** `docs/.project/CURRENT_PHASE.md`
- **Problem History:** `docs/.project/PROBLEMS.md`
- **Changelog:** `docs/.project/CHANGELOG.md`
- **Developer Guide:** `docs/.project/DEVELOPER_RECOMMENDATIONS.md`

---

## 📝 How to Report a New Issue

1. Check if issue already exists here
2. Use GitHub Issues with proper labels
3. Update this document with brief entry
4. Include:
   - Clear title
   - Current behavior
   - Expected behavior
   - Steps to reproduce (if bug)
   - Environment (Python, GPU, OS)

---

**Last Review:** 2025-11-23 - Phase 15 GPU CUDA Fix
**Next Review:** 2025-12-07 (Phase 16 Start)
