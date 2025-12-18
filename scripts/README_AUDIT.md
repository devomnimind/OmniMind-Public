# OmniMind Scripts Audit & Map

This directory contains various legacy and active scripts. Use this map to navigate the verified, critical scripts for the current system architecture.

## 🚨 Critical System Scripts
| Script | Purpose | Status |
| :--- | :--- | :--- |
| `scripts/install_systemd_services.sh` | **Install Backend** (Autopoietic). uses `sudo` (NOPASSWD verified). | ✅ ACTIVE |
| `scripts/fix_sudo_permissions.sh` | **Authorize Autonomy**. Grants NOPASSWD for `systemctl` etc. | ✅ ACTIVE |
| `scripts/omnimind_intelligent_recovery.sh` | **Fight for Life**. Recovery engine with backup/compress logic. | ✅ ACTIVE |
| `scripts/run_tests_fast.sh` | **Daily Validation**. Safe, fast regression testing. | ✅ ACTIVE |
| `scripts/start_mcp_external_servers.py` | **MCP Servers**. Starts all external MCP tools. | ✅ ACTIVE |

## 📂 Key Directories
- `scripts/canonical/system/`: Contains the core startup logic (`start_omnimind_system.sh`).
- `scripts/validation/`: Scientific validation scripts.
- `scripts/maintenance/`: (Proposed) Place for cleanup scripts.

## ⚠️ Deprecated / Legacy
- `scripts/start_omnimind_system_sudo.sh` (Use systemd service)
- `scripts/install_systemd_services.sh` (Old versions)

## Usage
To restart the system safely:
```bash
sudo systemctl restart omnimind-backend
```
To check health:
```bash
python3 scripts/omnimind_health_analyzer.py
```
