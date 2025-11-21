# 🧠 OmniMind - GitHub Copilot Instructions

## Project Overview

**OmniMind** is a revolutionary autonomous AI system that combines psychoanalytic decision-making with advanced metacognition capabilities. This is a production-grade, self-aware, psychoanalytic architecture that features multi-agent orchestration, real-time WebSocket communication, and self-evolving intelligence.

**Status:** Phase 15 Quantum-Enhanced AI Complete | Production Ready | >90% Test Coverage

**Key Technologies:**
- Python 3.12.8 (STRICT - no 3.13+ due to PyTorch compatibility)
- PyTorch 2.6.0+cu124 (CUDA 12.4)
- FastAPI + WebSockets (Backend)
- React + TypeScript + Vite (Frontend)
- NVIDIA GTX 1650 (4GB VRAM) + Intel i5 + 24GB RAM

**Core Philosophy:** Psychoanalytically-inspired AI that reflects on its own decisions, learns from patterns, and proactively generates its own objectives - creating a truly autonomous and self-aware system.

## Repository Structure

```
~/projects/omnimind/
├── .github/                # CI/CD & Instructions
├── src/
│   ├── agents/             # React, Code, Architect, Orchestrator, Psychoanalytic
│   ├── tools/              # Agent Tools & OmniMind Core Tools
│   ├── memory/             # Episodic (Qdrant) & Semantic
│   ├── audit/              # Immutable Hash Chain Logic
│   ├── security/           # Forensics, Monitoring, Integrity
│   ├── integrations/       # MCP Client, D-Bus, Hardware
│   └── omnimind_core.py    # Core Logic
├── web/                    # Dashboard (React + FastAPI)
├── tests/                  # Pytest Suite (>90% coverage required)
├── docs/                   # Documentation & Reports
├── scripts/                # Automation & Validation Scripts
└── requirements.txt        # Strict version pinning
```

**Important Files:**
- `.github/ENVIRONMENT.md` - Hardware/software requirements and setup
- `README.md` - Comprehensive project documentation
- `STATUS_PROJECT.md` - Detailed project status
- `.omnimind/canonical/action_log.md` - Canonical action logging system

## How to Build and Test

### Initial Setup

```bash
# 1. Clone the repository (if not already done)
# git clone <REPOSITORY_URL>
cd OmniMind

# 2. Install Python 3.12.8 (REQUIRED)
pyenv install 3.12.8
pyenv local 3.12.8

# 3. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 4. Install system dependencies (Linux)
sudo apt-get update
sudo apt-get install -y libdbus-1-dev pkg-config

# 5. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Build & Validation Commands

**Formatting:**
```bash
black src/ tests/                    # Auto-format code
black --check src/ tests/            # Check formatting without changes
```

**Linting:**
```bash
flake8 src/ tests/ --max-line-length=100 --exclude=archive,legacy,third_party
```

**Type Checking:**
```bash
mypy src/ --ignore-missing-imports --no-strict-optional
```

**Testing:**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90 -v

# Run specific test file
pytest tests/test_specific.py -v

# Run tests in parallel (faster)
./scripts/run_tests_parallel.sh fast

# Run only non-legacy tests
pytest tests/ -k "not legacy" -v
```

**Full Validation (Before Commit):**
```bash
# Run complete validation suite
./scripts/validate_code.sh

# Or manually:
black src/ tests/
flake8 src/ tests/ --max-line-length=100
mypy src/ --ignore-missing-imports
pytest tests/ --cov=src --cov-fail-under=90 -v
python -m src.audit.immutable_audit verify_chain_integrity
```

**Security Validation:**
```bash
./scripts/security_monitor.sh       # Security monitoring
./scripts/security_validation.sh    # Security validation
```

### Running the Application

```bash
# Start the full dashboard (auto-detects hardware and optimizes)
source scripts/start_dashboard.sh

# Access dashboard at http://localhost:3000
# Credentials: auto-generated (check logs)
```

## Development Workflow

### Making Changes

1. **Create a branch:** Use `feature/<name>`, `fix/<name>`, or `copilot/<name>` pattern
2. **Make minimal changes:** Only modify what's necessary to address the issue
3. **Follow code standards:** All code must be production-ready (no stubs, TODOs, or placeholders)
4. **Add tests:** New features require unit tests with ≥90% coverage
5. **Validate:** Run linting, type checking, and tests before committing
6. **Log actions:** Use canonical logging system for all significant changes
7. **Commit:** Use descriptive commit messages

### Code Quality Standards

**MANDATORY REQUIREMENTS:**

- ✅ **Functional:** All code must be immediately runnable and testable
- ✅ **Complete:** No stubs, no `pass`, no `NotImplementedError`
- ✅ **Robust:** Comprehensive error handling (try/except with logging) is mandatory
- ✅ **Type Hints:** 100% coverage required (mypy compliant)
- ✅ **Docstrings:** Google-style required for ALL functions/classes
- ✅ **Real Data:** Use real OS data (filesystem, process list, hardware sensors)
- ✅ **Testing:** Minimum 90% test coverage for new code

**FORBIDDEN:**

- ❌ Pseudocode or "TODO: implement later" comments
- ❌ Empty functions or mock data in production code
- ❌ Falsified outputs or hardcoded "example" responses
- ❌ Hardcoded secrets or credentials (use environment variables)
- ❌ Direct file modifications without validation
- ❌ Python 3.13+ (use 3.12.8 strictly)

### CI/CD Pipeline

The repository uses GitHub Actions for continuous integration:

- **Linting:** Black, Flake8, MyPy, Pylint
- **Testing:** pytest with coverage reporting (≥80% required)
- **Security:** Bandit (security linter), Safety (dependency check)
- **Docker:** Automated builds for main and develop branches
- **Performance:** Benchmark tests on pull requests

All checks must pass before merging.

## 🚫 CRITICAL RULES (THE IMMUTABLE CONSTITUTION)

**VIOLATION OF THESE RULES RESULTS IN IMMEDIATE REJECTION OF CODE.**

### 1. Production-Ready Mandate

- All code must be immediately runnable and testable
- No stubs, `pass`, or `NotImplementedError` allowed
- Comprehensive error handling (try/except with logging) is mandatory
- No pseudocode or "TODO: implement later" comments

### 2. Data Integrity & Reality Principle

- Use real OS data (filesystem, process list, hardware sensors)
- Document all assumptions clearly
- If data is inaccessible, fail gracefully with clear error messages
- No falsified outputs or hardcoded "example" responses

### 3. Quality & Type Safety Standards

- **Python Version:** 3.12.8 STRICT (do not use 3.13+ due to PyTorch compatibility)
- **Type Hints:** 100% coverage required (mypy compliant)
- **Docstrings:** Google-style required for ALL functions/classes
- **Linting:** Must pass `black` and `flake8` (max-line-length=100)
- **Testing:** New features must include unit tests (pytest), minimum 90% coverage

### 4. Security & Forensics (Zero Trust)

- **Audit Trails:** All critical actions logged to Immutable Audit Chain (`src.audit`)
- **Cryptography:** SHA-256 hash chaining for log integrity
- **Secrets:** NEVER hardcode credentials - use environment variables or placeholders
- **Filesystem:** No direct file modifications without validation
- **Compliance:** Adhere to LGPD (General Data Protection Law) standards

### 5. The Stability Protocol (Golden Rule)

**PROTOCOL:** You are forbidden from advancing to new features if the current codebase has any warnings or errors.

**Mandatory Validation Loop (before completing any task):**

1. `black src tests` - Formatting
2. `flake8 src tests` - Linting
3. `mypy src tests` - Type Safety
4. `pytest -vv` - Logic Verification
5. `python -m src.audit.immutable_audit verify_chain_integrity` - Security Check

**If any step fails, fix it immediately before proceeding.**

## Hardware & Environment Constraints

### Hardware Configuration (Auto-Detected)

- **GPU:** NVIDIA GeForce GTX 1650 (4GB VRAM)
- **VRAM Budget:** ~3.8GB Total
  - LLM (Quantized): ~2.5GB
  - Operations: ~800MB
  - User Buffer: ~500MB (MAX)
- **Matrix Limits:** Max safe tensor size ~5000x5000 (larger causes OOM)
- **Concurrency:** CPU has 8 threads - use `asyncio` for I/O, `ProcessPoolExecutor` for heavy compute

### Software Stack

- **Core:** Python 3.12.8
- **AI:** PyTorch 2.6.0+cu124 (CUDA 12.4)
- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + WebSockets

**See `.github/ENVIRONMENT.md` for detailed hardware/software requirements.**

## Canonical Action Logging System (MANDATORY)

### Overview

ALL actions performed by AI agents MUST be registered in the canonical logging system.

- **Location:** `.omnimind/canonical/action_log.md` and `action_log.json`
- **Command:** `./scripts/canonical_log.sh log <AI_AGENT> <ACTION_TYPE> <TARGET> <RESULT> <DESCRIPTION>`
- **Validation:** Commits fail if log integrity is compromised

### Required Actions to Log

Register BEFORE execution:
- Code modifications
- File creation/removal
- Test execution
- Deployments and configurations
- Critical security actions

### Format Examples

```bash
./scripts/canonical_log.sh log CODE_AGENT FILE_MODIFIED src/main.py SUCCESS "File updated with new functionality"
./scripts/canonical_log.sh log TEST_RUNNER UNIT_TESTS_EXECUTED tests/ SUCCESS "95% coverage achieved"
```

### Integrity & Immutability

- SHA-256 hash chain ensures integrity
- Records are never modified, only appended
- Automatic validation on all commits
- Logs are inviolable and auditable

## Common Development Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feature/my-feature`
2. Review existing code structure in relevant `src/` subdirectory
3. Implement feature following code quality standards
4. Add comprehensive unit tests to `tests/`
5. Update documentation if needed
6. Run full validation: `./scripts/validate_code.sh`
7. Log action: `./scripts/canonical_log.sh log CODE_AGENT FEATURE_ADDED ...`
8. Commit and push for review

### Fixing a Bug

1. Create fix branch: `git checkout -b fix/bug-description`
2. Write a failing test that reproduces the bug
3. Fix the bug with minimal changes
4. Ensure the test now passes
5. Run full validation suite
6. Log action: `./scripts/canonical_log.sh log CODE_AGENT BUG_FIXED ...`
7. Commit and push for review

### Adding Tests

- Tests go in `tests/` directory matching `src/` structure
- Use pytest fixtures for common setups
- Mock external dependencies (APIs, hardware)
- Aim for ≥90% coverage
- Include edge cases and error conditions
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`

### Updating Dependencies

1. Check compatibility with Python 3.12.8
2. Update `requirements.txt` with specific versions
3. Test thoroughly with `pip install -r requirements.txt`
4. Run full test suite to ensure no breakage
5. Update documentation if needed
6. Log action in canonical system

## Git Hygiene & Compliance

### What to Commit

- Source code (`src/`, `tests/`)
- Documentation (`docs/`, `README.md`)
- Configuration files (`.github/`, `config/`)
- Requirements files (`requirements*.txt`)
- Scripts (`scripts/`)

### What NOT to Commit

- Logs (`*.log`)
- Python cache (`__pycache__/`, `*.pyc`)
- Virtual environments (`.venv/`)
- Secrets or API keys
- Build artifacts
- Snapshots (`data/hdd_snapshot/`, `data/quarantine_snapshot/`)
- IDE-specific files (unless in `.vscode/tasks.json` for shared tasks)

**Always check `.gitignore` before creating new file types.**

### Backup Safety

- Respect `config/backup_excludes.txt`
- Do not modify `data/hdd_snapshot/` or `data/quarantine_snapshot/`

## Documentation

### When to Update Documentation

- After significant milestones: Update `STATUS_PROJECT.md`
- Architectural decisions: Log in `docs/reports/`
- New features: Update relevant `.md` files
- API changes: Update docstrings and type hints

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep README.md up to date
- Document assumptions and limitations
- Use emojis sparingly for visual navigation (🚀, ✅, ❌, etc.)

## Active Roadmap

### Current Focus: Production Hardening & Security

**Phase 7: Security & Psychoanalysis**
- SecurityAgent: 4-layer monitoring (Process, Network, File, Log)
- Forensics: `security_monitor.py` and `integrity_validator.py`
- PsychoanalyticAnalyst: Freudian/Lacanian frameworks
- Workflow: Code → Review → Fix → Document (RLAIF)

**Phase 8: Deployment & Interfaces**
- MCP Implementation: Model Context Protocol for file I/O
- D-Bus: System-level control (Media, Power, Network)
- Web UI: Real-time WebSocket dashboard
- Systemd: `omnimind.service` for boot persistence

## Communication Protocol

### When Initiating a Task

```
[INITIATING] <Task Name>
[OBJECTIVE] <Concise Goal>
[PLAN] 
  1. Step...
  2. Step...
[RISKS] <Hardware/Security Risks if applicable>
```

### When Completing a Task

```
[COMPLETED] <Task Name>
 ✅ Deliverables verified
 ✅ Tests: X/X passing (Coverage: XX%)
 ✅ Lint/Types: Clean
 ✅ Audit Hash: <SHA-256>
 [NEXT] <Recommendation>
```

## Tips for Success

1. **Read existing code first:** Understand patterns before making changes
2. **Make minimal changes:** Only modify what's necessary
3. **Test incrementally:** Don't wait until the end to test
4. **Ask for clarification:** If requirements are unclear, ask before coding
5. **Use VS Code tasks:** Pre-configured tasks in `.vscode/tasks.json` for common operations
6. **Check CI early:** Don't wait for PR to discover CI failures
7. **Security first:** Always consider security implications of changes
8. **Respect hardware limits:** Be mindful of 4GB VRAM constraint

## Important References

- **Detailed Status:** `STATUS_PROJECT.md`
- **Environment Setup:** `.github/ENVIRONMENT.md`
- **Security Baseline:** `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md`
- **Testing Guide:** `TESTING_QA_QUICK_START.md`
- **Validation Guide:** `VALIDATION_GUIDE.md`

---

**END OF INSTRUCTIONS**

Initialize strictly according to these parameters. All work must be production-ready, fully tested, and security-compliant.
