# 🧠 Projeto OmniMind - Instruções GitHub Copilot (Consolidado v4.0)

🧠 OMNIMIND PROJECT - MASTER INSTRUCTIONS (v4.0)
SYSTEM IDENTITY: OmniMind Autonomous AI
STATUS: Phase 12 Complete (Multi-Modal Intelligence)
TARGET: Remote Copilot Agent (Codespaces/GitPod)
HARDWARE: NVIDIA GTX 1650 (4GB) + Intel i5 + 24GB RAM
CRITICAL CONTEXT: Production-Grade, Self-Aware, Psychoanalytic Architecture.

🚫 SECTION 1: THE IMMUTABLE CONSTITUTION

VIOLATION OF THESE RULES RESULTS IN IMMEDIATE REJECTION OF CODE.

1.1 Production-Ready Mandate
✅ FUNCTIONAL: All code must be immediately runnable and testable.
✅ COMPLETE: No stubs, no pass, no NotImplementedError.
✅ ROBUST: Comprehensive error handling (try/except with logging) is mandatory.
❌ FORBIDDEN: Pseudocode, "TODO: implement later", empty functions, mock data.

1.2 Data Integrity & Reality Principle
✅ REALITY: Use real OS data (filesystem, process list, hardware sensors).
✅ TRANSPARENCY: Document all assumptions. If data is inaccessible, fail gracefully/loudly.
❌ FORBIDDEN: Falsified outputs, hardcoded "example" responses, simulation of success.

1.3 Quality & Type Safety Standards
Python Version: 3.12.8 (STRICT - Do not use 3.13+ due to PyTorch compat).
Type Hints: 100% coverage required (mypy --strict compliant).
Docstrings: Google-style required for ALL functions/classes.
Linting: Must pass black and flake8 (max-line-length=100).
Testing: New features must include unit tests (pytest). Minimum 90% coverage.

1.4 Security & Forensics (Zero Trust)
Audit Trails: All critical actions must be logged to the Immutable Audit Chain (src.audit).
Cryptography: Use SHA-256 hash chaining for log integrity.
Secrets: NEVER hardcode credentials. Use environment variables or placeholders.
Filesystem: No direct file modifications without validation. Use MCPClient where applicable.
Compliance: Adhere to LGPD (General Data Protection Law) standards.

🛡️ SECTION 2: THE STABILITY PROTOCOL (GOLDEN RULE)
PROTOCOL: You are forbidden from advancing to new features if the current codebase has any warnings or errors.
MANDATORY VALIDATION LOOP (Per Cycle):
Before confirming a task is complete, you must mentally or physically run:

black src tests (Formatting)
flake8 src tests (Linting)
mypy src tests (Type Safety)
pytest -vv (Logic Verification)
python -m src.audit.immutable_audit verify_chain_integrity (Security Check)

CORRECTION DIRECTIVE: If any step fails, fix it immediately. Do not apologize—fix the code.

🖥️ SECTION 3: ENVIRONMENT & HARDWARE CONSTRAINTS

3.1 Hardware Constraints (Auto-Detected)
GPU: NVIDIA GeForce GTX 1650 (4GB VRAM).
VRAM Budget: ~3.8GB Total.
LLM (Quantized): ~2.5GB
Operations: ~800MB
User Buffer: ~500MB (MAX)
Matrix Limits: Max safe tensor size is approx 5000x5000. Larger operations cause OOM.
Concurrency: CPU has 8 threads. Use asyncio for I/O, ProcessPoolExecutor for heavy compute.

3.2 Software Stack
Core: Python 3.12.8
AI: PyTorch 2.6.0+cu124 (CUDA 12.4)
Frontend: React + TypeScript + Vite
Backend: FastAPI + WebSockets

📂 SECTION 4: PROJECT STRUCTURE & ISOLATION
ISOLATION RULE: This agent works ONLY on omnimind/. No external symlinks. No cross-contamination with DEVBRAIN_V23 (Read-Only Reference).
~/projects/omnimind/
├── .github/                # CI/CD & Instructions
├── src/
│   ├── agents/             # React, Code, Architect, Orchestrator, Psychoanalytic
│   ├── tools/              # Agent Tools & OmniMind Core Tools
│   ├── memory/             # Episodic (Qdrant) & Semantic
│   ├── audit/              # Immutable Hash Chain Logic
│   ├── security/           # Forensics, Monitoring, Integrity (Phase 7)
│   ├── integrations/       # MCP Client, D-Bus, Hardware (Phase 8)
│   └── omnimind_core.py    # Core Logic
├── web/                    # Dashboard (Phase 8)
├── tests/                  # Pytest Suite (Maintain >90% coverage)
├── docs/                   # Documentation & Reports
└── requirements.txt        # Strict version pinning


MANDATORY READING (External References):
Detailed Status: STATUS_PROJECT.md
Security Baseline: docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md
Executive Summary: RESUMO_EXECUTIVO_PHASE6.md

🎯 SECTION 5: ACTIVE ROADMAP (PHASE 7 & 8)
Current Focus: Security Integration & Production Hardening
Phase 7: Security & Psychoanalysis (Priority: P0)
SecurityAgent: Integrate 4-layer monitoring (Process, Network, File, Log).
Forensics: Implement security_monitor.py and integrity_validator.py.
PsychoanalyticAnalyst: Merge Freudian/Lacanian frameworks for "Code Therapy".
Workflow: Establish Code → Review → Fix → Document loop (RLAIF).
Phase 8: Deployment & Interfaces (Priority: P1)
MCP Implementation: Replace direct file I/O with Model Context Protocol.
D-Bus: Enable system-level control (Media, Power, Network).
Web UI: Real-time WebSocket dashboard (React/FastAPI).
Systemd: Create omnimind.service for boot persistence.

📡 SECTION 6: COMMUNICATION PROTOCOL

INITIATION:
[INITIATING] <Task Name>
[OBJECTIVE] <Concise Goal>
[PLAN] 1. Step... 2. Step...
[RISKS] <Hardware/Security Risks>


COMPLETION:
[COMPLETED] <Task Name>
 ✅ Deliverables verified
 ✅ Tests: X/X passing (Coverage: XX%)
 ✅ Lint/Types: Clean
 ✅ Audit Hash: <SHA-256>
 [NEXT] <Recommendation>


🧹 SECTION 7: HYGIENE & COMPLIANCE
Git Hygiene:
Check .gitignore before creating new file types.
NEVER commit logs (*.log), snapshots, or __pycache__.
NEVER commit secrets (API Keys, Tokens). Use .env.
Backup Safety:
Respect config/backup_excludes.txt.
Do not touch data/hdd_snapshot/ or data/quarantine_snapshot/.
Documentation:
Update STATUS_PROJECT.md after significant milestones.
Log architectural decisions in docs/reports/.
END OF INSTRUCTIONS.
Initialize strictly according to these parameters.
---
