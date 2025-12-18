# System Architecture

## Environment
- **OS**: Ubuntu 22.04 LTS (NO Docker, System Native)
- **GPU**: NVIDIA + CUDA 12.1 + PyTorch 2.5.1
- **Python**: 3.12 (Virtual Environment)

## Core Services (Systemd)
- **Postgres**: Active
- **Redis**: Active
- **Qdrant**: Active

## Project Structure
- `src/`: Core OmniMind source code
- `scripts/`: Operational and validation scripts
- `logs/`: **GLOBAL** centralized logging directory
- `data/`: Data storage and snapshots
- `tests/`: Integration and unit tests

## Standards
- **Logging**: All scripts MUST use `logs/` at project root.
- **Testing**: `pytest` with markers (sudo, gpu, integration).
- **Validation**: `scripts/validation/` suite for scientific metric validation.

## Metrics & Validation
- **Scientific Stimulation**: `scripts/validation/omnimind_stimulation_scientific.py`
  - Validates Neural Entrainment, Theta Coherence, and Phi Integration.

## Service Management (Systemd)
The system is managed by `systemd` with an autopoietic recovery wrapper.

**Commands:**
- **Status**: `sudo systemctl status omnimind-backend`
- **Start**: `sudo systemctl start omnimind-backend`
- **Stop**: `sudo systemctl stop omnimind-backend`
- **Restart**: `sudo systemctl restart omnimind-backend`

**Recovery Mechanism:**
If the backend crashes, `scripts/omnimind_intelligent_recovery.sh` is automatically triggered (`ExecStopPost`) to:
1. Detect consecutive failures.
2. If critical, backup `data/` and compress old logs.
3. Restart the service.

## Critical Scripts
See `scripts/README_AUDIT.md` for a complete map.
- `scripts/run_tests_fast.sh`: Daily regression testing.
- `scripts/install_systemd_services.sh`: Deploys the autopoietic service.
- `scripts/fix_sudo_permissions.sh`: Fix NOPASSWD for maintenance.
