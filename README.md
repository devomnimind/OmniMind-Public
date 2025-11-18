# OmniMind Workspace

OmniMind is a self-hosted multi-agent system with a FastAPI + React dashboard, secure monitoring agents, and automation tooling. This project follows a strict workspace layout that keeps the root clean, archives legacy artifacts, and centralizes script/log management for predictable CI/CD.

## Repository Structure

- `config/` – Environment configuration files (agent configs, credential stores).
- `docs/` – Living architecture docs and operational runbooks for the Phase 7/8 stack.
- `web/` – Dashboard frontend and backend sources (FastAPI backend + React/Vite frontend).
- `scripts/` – Utility shells and Python automation (`start_dashboard.sh`, `create_remaining_agents.sh`, `fix_completion.py`, `verify_nvidia.sh`, `scripts/benchmarks/*`).
- `tests/` – Pytest suites and fixtures; `tests/legacy/` hosts archived root-level test scripts from earlier phases.
- `src/` – Core agents, tools, integrations, memory, and security modules.
- `logs/` – Execution logs and derived outputs; `.gitignore` keeps this directory clean except for audited files (e.g., `logs/audit_chain.log`, `logs/.coverage`).
- `archive/` – Historical demos, reports, benchmarks, and CUDA experiments (`archive/examples/`, `archive/reports/`).
- `tmp/` – Scratch area for generated agents/tools artifacts (`tmp/agents/`, `tmp/tools/`). This directory is ignored by Git.

## Installation & Startup

1. Create and activate the Python virtual environment (Python 3.12+ recommended):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Ensure system tooling (Docker, Nix, or host shell) satisfies the dashboard dependencies described in `web/backend/README.md`.

3. Generate dashboard credentials on first run (auto-created at `config/dashboard_auth.json` with `chmod 600`). If you already have valid credentials, set the env vars before startup:

```bash
export OMNIMIND_DASHBOARD_USER=<user>
export OMNIMIND_DASHBOARD_PASS=<pass>
```

The backend will always prefer env vars, otherwise it loads/generates the secure file (never commit `config/dashboard_auth.json`).

4. Launch the backend + frontend via the orchestration script:

```bash
scripts/start_dashboard.sh
```

## Dashboard Workflow

- Access the FastAPI endpoints (secured via Basic Auth) for `/status`, `/snapshot`, `/metrics`, `/tasks/orchestrate`, `/mcp/execute`, `/dbus/execute`, etc.
- The React GUI (`web/frontend/`) reads credentials from the login form and stores `Basic` auth headers per session; it also surfaces the credential file path so administrators know where to rotate secrets.
- `/observability` now surfaces a `validation` payload (pulled from `logs/security_validation.jsonl`) alongside `self_healing`, `atlas`, and `security`, so teams can see the latest audit-chain verdict directly in the UI.
- MCP and D-Bus flows rely on `src/integrations` and the orchestrator agent to provide context, metrics, and manual triggers.

## Testing & Quality Gates

Run the fast pipelines after reorganizing or changing core logic:

```bash
pytest tests/test_dashboard_e2e.py -W error
pytest tests/ -k "not legacy"  # run the active suites
```

Ensure `logs/.coverage` is removed or regenerated via `pytest --cov=src` and keep work in sync with the hashed audit chain via `scripts/id` if relevant.

## Logs, Alerts, and Credentials

- Active logs live under `logs/`; coverage and audit traces now also stay here for easier rotation.
- The dashboard auth file is `config/dashboard_auth.json` (600). Rotate credentials by editing this file securely and restarting the backend; the new creds are durable until the next rotation.
- Use `scripts/start_dashboard.sh` or the Docker Compose asset to orchestrate the backend + frontend; it logs the credential location upon startup.

## Maintenance Notes

- Legacy artifacts live in `archive/reports/` and `archive/examples/`; reference `archive/README.md` for context.
- Scripts under `scripts/` are the only runtime automation files allowed at the root level; please do not scatter lone `.py` or `.sh` files outside this directory.
- Tests that once lived at the root now reside under `tests/legacy/`; keep new tests under `tests/`.
- Temporary tool outputs must stay within `tmp/`; this directory is ignored and safe to wipe.

With this organization, the root stays focused on keys (configs, requirements, Compose files), and the rest of the workspace aligns with our production readiness and CI/CD standards.

## DEVBRAIN V23 Roadmap

The `DEVBRAIN_V23/` directory now hosts the foundational work for the Masterplan (Protocolo Phoenix). Each folder mirrors a sense or infrastructure pillar:

- `core/` → futura migração do `src/`, `tests/` e `config/` atuais.
- `sensory/` → visão (Visual Cortex), audição/voz e propriocepção com `eBPF`.
- `cognition/` → Graph of Thoughts + memória A-MEM com LangGraph e ChromaDB.
- `immune/` → isolamento Firecracker, DLP e proteção P0.
- `orchestration/` → LangGraph-driven agents e modos V23.
- `infrastructure/` → Redis Streams, gateway FastAPI e ChromaDB vector store.
- `atlas/` → self-healing, auto-training e ATLAS (futuro).

O Masterplan guia cada nova implementação, começando pela visão multimodal (`sensory/visual_cortex.py`) e o Event Bus redis (`infrastructure/event_bus.py`). Consulte `DEVBRAIN_V23/README.md` e os documentos anexados (`docs/Masterplan/`) para manter o alinhamento estratégico antes de avançar nas fases seguintes.