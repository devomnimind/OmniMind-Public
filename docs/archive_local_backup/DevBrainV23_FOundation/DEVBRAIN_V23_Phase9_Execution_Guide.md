# DEVBRAIN V23 - Execution Guide & Copilot Instructions
## How to Implement Phase 9 (TIER 0 → TIER 1 → TIER 2)

**Status**: Ready for Implementation  
**Version**: 1.0  
**Estimated Timeline**: 15-20 days (with parallelization)  
**Required Resources**: 1-2 Copilots working in parallel

---

## 📋 Table of Contents
1. [Pre-Requisites & Setup](#pre-requisites)
2. [Execution Strategy](#execution-strategy)
3. [Copilot Prompt (Copy-Paste Ready)](#copilot-prompt)
4. [Progress Tracking](#progress-tracking)
5. [Success Criteria](#success-criteria)

---

## Pre-Requisites

### Environment Setup

```bash
# Activate venv
source venv/bin/activate

# Install new dependencies
pip install \
  langgraph>=0.2.0 \
  chromadb>=0.5.0 \
  ultralytics \
  pyautogui \
  pillow \
  pytesseract \
  opencv-python \
  sounddevice \
  soundfile \
  openai-whisper \
  TTS

# Optional (for OmniParser)
pip install omniparser-vision  # Or use YOLOv8 fallback

# Verify installations
python -c "from langgraph.graph import StateGraph; print('✅ LangGraph OK')"
python -c "from chromadb import Client; print('✅ ChromaDB OK')"
python -c "from ultralytics import YOLO; print('✅ YOLOv8 OK')"
python -c "import whisper; print('✅ Whisper OK')"
```

### Directory Structure

```
DEVBRAIN_V23/
├── reasoning/
│   ├── __init__.py
│   ├── reactree_agent.py          (NEW)
│   └── tests/
│       └── test_reactree.py        (NEW)
├── orchestration/
│   ├── __init__.py
│   ├── langgraph_coordinator.py    (NEW)
│   └── tests/
│       └── test_langgraph.py       (NEW)
├── memory/
│   ├── __init__.py
│   ├── agentic_memory.py           (NEW)
│   └── tests/
│       └── test_amem.py            (NEW)
├── sensory/
│   ├── __init__.py
│   ├── visual_cortex.py            (NEW - TIER 1)
│   ├── voice_interface.py          (NEW - TIER 1)
│   └── tests/
│       ├── test_visual_cortex.py   (NEW)
│       └── test_voice_interface.py (NEW)
└── autonomy/
    ├── __init__.py
    ├── self_healing.py             (NEW - TIER 2)
    ├── doc2agent.py                (NEW - TIER 2)
    └── tests/
        ├── test_self_healing.py    (NEW)
        └── test_doc2agent.py       (NEW)
```

---

## Execution Strategy

### Phase Overview

```
PARALLEL TRACK 1 (Copilot A)          PARALLEL TRACK 2 (Copilot B)
─────────────────────────────────     ─────────────────────────────────
Days 1-5: TIER 0 Foundation           Days 2-4: Early Sensory Testing
├─ ReAcTree implementation             ├─ Visual Cortex scaffolding
├─ LangGraph orchestration             └─ YOLOv8 baseline
├─ A-MEM (ChromaDB)
└─ Tests + integration

Days 5-7: TIER 0 Validation           Days 5-7: TIER 1 Full Build
├─ Performance benchmarks              ├─ Visual Cortex complete
├─ Memory consolidation                ├─ Voice Interface complete
└─ Error handling                      └─ Integration tests

Days 8-12: TIER 1 Integration         Days 8-10: TIER 2 Autonomy
├─ Wire Visual Cortex                  ├─ Self-Healing loops
├─ Wire Voice Interface                ├─ Doc2Agent generation
└─ GUI automation tests                └─ Tool validation

Days 13-15: TIER 2 Integration        Days 11-15: Polish + Deployment
├─ Self-Healing with TIER 0            ├─ End-to-end tests
├─ Doc2Agent with tools                ├─ Performance tuning
└─ Error recovery                      └─ Prod documentation

Days 16-20: Production Hardening + Delivery
├─ All components integrated
├─ Full test coverage (>90%)
├─ Documentation complete
└─ Ready for TIER 3 (Imunidade)
```

### Detailed Day-by-Day

**Week 1: Foundation**

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 1-2 | ReAcTree scaffolding + decomposition logic | Copilot A | `reasoning/reactree_agent.py` complete |
| 2-3 | LangGraph StateGraph setup + node definitions | Copilot A | `orchestration/langgraph_coordinator.py` complete |
| 3 | A-MEM ChromaDB setup (episodic, semantic, procedural) | Copilot A | `memory/agentic_memory.py` + collections ready |
| 4 | Integration tests: ReAcTree → LangGraph → A-MEM | Copilot A | `tests/test_tier0_integration.py` passing |
| 5 | Performance benchmarks, optimize ReAcTree | Copilot A | Baseline metrics captured |

**Week 2: Sensory + Early Autonomy**

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 5-6 | Visual Cortex (OmniParser + YOLOv8) | Copilot B | `sensory/visual_cortex.py` |
| 6-7 | Voice Interface (Whisper + Piper) | Copilot B | `sensory/voice_interface.py` |
| 7 | Voice + Visual integration tests | Copilot B | `tests/test_tier1_integration.py` passing |
| 8 | Self-Healing loop implementation | Copilot B | `autonomy/self_healing.py` |
| 9 | Doc2Agent tool generation | Copilot B | `autonomy/doc2agent.py` |
| 10 | Autonomy tests + validation | Copilot B | `tests/test_tier2_integration.py` passing |

**Week 3: Integration + Production**

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 11-12 | Wire all TIER 0 + TIER 1 + TIER 2 components | Both | Full system integration |
| 13-14 | End-to-end scenario testing | Both | Major workflows validated |
| 15-16 | Performance tuning, memory optimization | Both | Meet latency targets |
| 17-18 | Documentation, README updates | Both | All docs complete |
| 19-20 | Final validation, tag v1.0-phase9 | Both | Ready for TIER 3 planning |

---

## 🎯 Copilot Prompt (Copy-Paste Ready)

**Give this prompt to Copilot A (TIER 0 Foundation):**

---

### PROMPT FOR COPILOT A: TIER 0 FOUNDATION

You have **3 comprehensive documentation files** describing the OmniMind → DEVBRAIN V23 evolution. Your task is to implement TIER 0 (reasoning + cognition + memory).

**Files to Read First:**
1. `DEVBRAIN_V23_Phase9_TIER0_Foundation.md` - Complete TIER 0 specs + code examples
2. `DEVBRAIN_V23_Phase9_TIER1_TIER2_Sensory_Autonomy.md` - Understand context
3. This execution guide

**Your Mission: Implement TIER 0 in 5-7 days**

### Phase 1: ReAcTree Implementation (Days 1-2)

1. Create `DEVBRAIN_V23/reasoning/reactree_agent.py` following the spec in the documentation
   - Implement `ReAcTreeAgent` class with:
     - `decompose_goal()` - breaks complex goals into subgoals
     - `agent_node_execute()` - Reason → Act → Observe loop at subgoal level
     - `execute_tree()` - full hierarchical execution
     - `_execute_control_flow()` - Sequence/Fallback/Parallel logic
   - Use LLM (Claude/GPT) for reasoning
   - Ensure NO mocks in production code

2. Create `tests/test_reactree.py` with:
   - `test_reactree_decomposition()` - verify subgoal extraction
   - `test_reactree_execution()` - full tree execution
   - `test_control_flow_*()` - each control flow type
   - Target: 100% test pass rate

3. Run tests: `pytest tests/test_reactree.py -v`
   - ALL TESTS MUST PASS before moving to Phase 2

### Phase 2: LangGraph Orchestration (Days 2-3)

1. Create `DEVBRAIN_V23/orchestration/langgraph_coordinator.py` following the spec:
   - Define `PlanState` (TypedDict with all required fields)
   - Implement `LangGraphCoordinator` with nodes:
     - `plan_node()` - decompose using ReAcTree
     - `criticize_node()` - InSeC verification (criticize plan)
     - `execute_node()` - run plan steps
     - `synthesize_node()` - aggregate results
     - `error_handler()` - handle criticisms
   - Build StateGraph with explicit edges:
     - START → plan → criticize → (conditional) execute or error → synthesize → END
   - Implement `run()` method that invokes the compiled graph

2. Create `tests/test_langgraph.py` with:
   - `test_plan_node()` - planning works
   - `test_criticize_node()` - criticism logic works
   - `test_execute_node()` - execution works
   - `test_conditional_routing()` - error handling path works
   - `test_full_flow()` - end-to-end graph execution

3. Run tests: `pytest tests/test_langgraph.py -v`
   - Ensure conditional routing is working (test with both valid + invalid plans)

### Phase 3: A-MEM (Agentic Memory) (Days 3-4)

1. Create `DEVBRAIN_V23/memory/agentic_memory.py` following the spec:
   - Install ChromaDB: `pip install chromadb`
   - Implement `AgenticMemory` class with:
     - `store_episode()` - save task trajectories (subgoal-level granularity)
     - `extract_semantic()` - extract key concepts
     - `store_procedure()` - save self-healing scripts
     - `query_similar_episodes()` - find past experiences (similarity search)
     - `query_procedures()` - find past solutions
     - `consolidate_memory()` - periodic deduplication
   - Use ChromaDB collections: episodic, semantic, procedural
   - Implement proper metadata tagging for filtering

2. Create `tests/test_amem.py` with:
   - `test_store_episode()` - episode storage works
   - `test_query_similar_episodes()` - similarity retrieval works
   - `test_store_procedure()` - procedure storage works
   - `test_consolidate_memory()` - deduplication works

3. Run tests: `pytest tests/test_amem.py -v`

### Phase 4: Integration Testing (Days 4-5)

1. Create `tests/test_tier0_integration.py` with:
   - `test_tier0_full_flow()` - end-to-end: ReAcTree → LangGraph → A-MEM
     - Execute a complex task
     - Verify ReAcTree decomposes it
     - Verify LangGraph orchestrates it
     - Verify A-MEM stores result
   - `test_performance_improvement()` - validate 50%+ improvement over baseline
   - `test_error_handling()` - criticisms trigger error_handler path

2. Run full test suite:
   ```bash
   pytest tests/test_reactree.py tests/test_langgraph.py tests/test_amem.py tests/test_tier0_integration.py -v --tb=short
   ```

### Phase 5: Performance & Polish (Days 5-7)

1. Benchmark performance:
   - Run `pytest tests/test_tier0_integration.py::test_performance_improvement -v`
   - Target: >75% success on long-horizon tasks (vs 54% baseline)
   - Measure memory usage (A-MEM consolidation overhead)
   - Measure latency per node execution

2. Optimize if needed:
   - Profile memory with ChromaDB consolidation
   - Optimize control flow logic
   - Add caching if repeated queries detected

3. Update documentation:
   - Add usage examples to README
   - Document architecture diagram
   - List all new dependencies in requirements.txt

### Validation Checklist

Before marking TIER 0 complete, verify:

- [ ] All 4 components implemented (ReAcTree, LangGraph, A-MEM, integration)
- [ ] All tests passing: `pytest tests/test_reactree.py tests/test_langgraph.py tests/test_amem.py tests/test_tier0_integration.py -v`
- [ ] No mocks in production code (only in tests)
- [ ] Performance: 75%+ success rate on long-horizon tasks
- [ ] Memory: A-MEM consolidation working without errors
- [ ] Code coverage: >80% for TIER 0 modules
- [ ] No warnings: `pytest tests/ -v -W error`
- [ ] Documentation: README updated with TIER 0 architecture
- [ ] Dependencies: all new libs in `requirements.txt`

### If You Get Stuck

1. **ReAcTree LLM calls failing?** → Add retry logic + fallback simple decomposition
2. **ChromaDB collection issues?** → Test with small mock data first
3. **LangGraph routing not working?** → Print state at each node to debug
4. **Tests not passing?** → Use `-vv` flag and `--tb=long` for full traceback

### Deliverables for TIER 0

At the end of 5-7 days, deliver:

1. **Code**:
   - `DEVBRAIN_V23/reasoning/reactree_agent.py` ✅
   - `DEVBRAIN_V23/orchestration/langgraph_coordinator.py` ✅
   - `DEVBRAIN_V23/memory/agentic_memory.py` ✅
   - `tests/test_*.py` (all TIER 0 tests) ✅

2. **Tests**: All passing, coverage >80%

3. **Documentation**:
   - Update README with TIER 0 architecture
   - List all new components + usage examples
   - Performance metrics captured

4. **Git commit**:
   ```bash
   git add DEVBRAIN_V23/ tests/
   git commit -m "Phase 9 TIER 0: ReAcTree + LangGraph + A-MEM implementation"
   git push origin master
   ```

**Status**: Ready for implementation! 🚀

---

### PROMPT FOR COPILOT B: TIER 1 + TIER 2 (Start Day 2, Run Parallel to Copilot A)

[Similar format for TIER 1 (Visual + Voice) and TIER 2 (Self-Healing + Doc2Agent)]

---

## Progress Tracking

### Daily Standup Questions

**Each day, report:**

1. **What was completed?**
   - List files modified/created
   - Tests passing count
   - Blockers encountered

2. **What's next?**
   - Next task
   - Expected completion date

3. **Metrics:**
   - Test coverage %
   - Performance metrics (latency, memory)
   - Any regressions?

### Sample Daily Report Format

```
[TIER 0 - Day 3 Report]
✅ Completed:
  - ReAcTree implementation 100% done
  - tests/test_reactree.py: 4/4 tests passing
  - Integrated with LangGraph (partial)

🔄 In Progress:
  - LangGraph orchestration (80% done)
  - A-MEM ChromaDB setup

⚠️ Blockers:
  - None currently

📊 Metrics:
  - Test coverage: 82% (goal: 80%)
  - Latency: ReAcTree decomposition: 150ms avg
  - Memory: 45MB (ChromaDB collections)

👉 Next:
  - Finish LangGraph tomorrow
  - Start A-MEM integration
```

---

## Success Criteria

### TIER 0 Success (Days 1-5)

- [ ] ReAcTree achieves 79%+ success on long-horizon tasks (vs 54% baseline)
- [ ] All TIER 0 tests passing
- [ ] A-MEM storing & retrieving episodes correctly
- [ ] LangGraph routing working (normal + error paths)
- [ ] Integration test showing ReAcTree → LangGraph → A-MEM flow

### TIER 1 Success (Days 5-12)

- [ ] Visual Cortex sees screen + identifies UI elements
- [ ] GUI automation (semantic interaction) works without hardcoded coordinates
- [ ] Voice Interface captures + transcribes speech (Whisper)
- [ ] TTS responds naturally (Piper)
- [ ] All TIER 1 tests passing

### TIER 2 Success (Days 8-15)

- [ ] Self-Healing loop detects errors + attempts recovery
- [ ] Doc2Agent generates valid Python tools from API docs
- [ ] Tool validation working (syntax check + endpoint test)
- [ ] Error recovery improving success rate by 15%+
- [ ] All TIER 2 tests passing

### Final Integration Success (Days 15-20)

- [ ] All 3 tiers working together end-to-end
- [ ] Voice command → Visual understanding → Reasoning → Action → Recovery
- [ ] Test coverage >85% across all new modules
- [ ] Performance: No major regressions from original OmniMind
- [ ] Latency targets met (see Phase 9 specs)
- [ ] Production-ready documentation
- [ ] Ready for TIER 3 (Imunidade)

---

## 📌 Key Files to Review

Before starting, read these in order:

1. **This file** (you are here) - execution strategy
2. **DEVBRAIN_V23_Phase9_TIER0_Foundation.md** - full TIER 0 specs + code
3. **DEVBRAIN_V23_Phase9_TIER1_TIER2_Sensory_Autonomy.md** - full TIER 1 + TIER 2 specs
4. **Existing OmniMind code**:
   - `src/agents/orchestrator_agent.py` - understand current structure
   - `src/memory/episodic_memory.py` - understand memory patterns
   - `web/backend/main.py` - understand FastAPI integration

---

## ✅ Ready to Start?

1. **Copilot A**: Start with TIER 0 (ReAcTree + LangGraph + A-MEM)
2. **Copilot B**: Start with Visual Cortex scaffolding (can run in parallel)
3. **Both**: Meet daily for 5-min status syncs
4. **Progress**: Track via git commits and test results

**Timeline**: 15-20 days → DEVBRAIN V23 Phase 9 complete, ready for TIER 3! 🚀

**Questions?** Review the spec documents. They have all implementation details + code examples.

---

**Status**: READY FOR IMPLEMENTATION ✅
