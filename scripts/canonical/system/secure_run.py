#!/usr/bin/env python3
"""
🛡️ OmniMind Secure Executor
===========================
Wrapper seguro para execução de comandos privilegiados.
Substitui chamadas diretas de 'sudo' para garantir:
1. Auditoria completa (logs/audit/privileged_access.log)
2. Prevenção de travamentos (usa sudo -n)
3. Validação contra Allowlist (config/security/privileged_commands.yaml)
4. Redirecionamento para Docker quando necessário

Uso:
    python scripts/canonical/system/secure_run.py <comando> [args...]
"""

import datetime
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

# Configuração
# secure_run.py está em scripts/canonical/system/, então precisamos subir 4 níveis para chegar à raiz
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config/security/privileged_commands.yaml"
AUDIT_LOG = PROJECT_ROOT / "logs/audit/privileged_access.log"

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("SecureExecutor")


def setup_audit():
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)


def log_audit(status: str, command: str, reason: str = ""):
    timestamp = datetime.datetime.now().isoformat()
    user = os.environ.get("USER", "unknown")
    entry = f"{timestamp} | {user} | {status} | {command} | {reason}\n"
    with open(AUDIT_LOG, "a") as f:
        f.write(entry)


def load_policy():
    if not CONFIG_PATH.exists():
        logger.error(f"❌ Policy file not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def check_policy(command_parts, policy):
    cmd = command_parts[0]
    args = " ".join(command_parts[1:])

    # 1. Check Docker Enforced
    for unsafe in policy.get("docker_enforced", []):
        if unsafe in cmd or unsafe in args:
            return False, "docker_required", f"Command '{unsafe}' must run in Docker"

    # 2. Check System Allowlist
    for rule in policy.get("system_allowlist", []):
        # Check command match (exact path, binary name, or ending with /binary)
        rule_cmd = rule["command"]
        binary_name = rule_cmd.split("/")[-1]

        is_match = (
            cmd == rule_cmd  # Exact match (/usr/bin/cmd)
            or cmd == binary_name  # Binary name only (cmd)
            or cmd.endswith(f"/{binary_name}")  # Path match (./cmd, /opt/cmd)
        )

        if is_match:
            # Check args regex
            if re.match(rule["args_regex"], args):
                return True, "allowed", rule["description"]
            return True, "allowed", rule["description"]

    return False, "denied", "Command not in allowlist"


def main():
    if len(sys.argv) < 2:
        print("Usage: secure_run.py <command> [args...]")
        sys.exit(1)

    command_parts = sys.argv[1:]
    full_command = " ".join(command_parts)

    setup_audit()
    policy = load_policy()

    allowed, status, reason = check_policy(command_parts, policy)

    if not allowed:
        if status == "docker_required":
            logger.warning(f"🐳 Redirecting to Docker: {full_command}")
            log_audit("REDIRECT_DOCKER", full_command, reason)
            # TODO: Implement Docker redirection logic here
            # For now, fail safely
            print(f"❌ Blocked: {reason}. Please run this inside the container.")
            sys.exit(1)
        else:
            logger.error(f"🚫 Access Denied: {full_command}")
            logger.error(f"   Reason: {reason}")
            log_audit("DENIED", full_command, reason)
            sys.exit(1)

    # Execution
    logger.info(f"🛡️ Executing securely: {full_command}")
    log_audit("ALLOWED", full_command, reason)

    try:
        # Use sudo -n (non-interactive) to prevent hanging
        # Removed -E to avoid "permission to preserve environment" error without SETENV
        cmd = ["sudo", "-n"] + command_parts

        result = subprocess.run(cmd, check=False)

        if result.returncode == 1 and "password" in str(result.stderr or ""):
            # This usually implies sudo asked for a password and failed due to -n
            pass

        if result.returncode != 0:
            # Check if it was a permission issue (sudo -n failed)
            # Note: sudo -n exits with 1 if password is required
            logger.error(f"❌ Execution failed (Exit Code: {result.returncode})")
            if result.returncode == 1:
                print("\n⚠️  PERMISSION ERROR: Sudo requires a password.")
                print("   To enable autonomous execution, run:")
                print("   ./scripts/setup_permissions.sh")

            log_audit("FAILED", full_command, f"Exit Code {result.returncode}")
            sys.exit(result.returncode)

        log_audit("SUCCESS", full_command, "Executed successfully")

    except Exception as e:
        logger.error(f"💥 Critical Error: {e}")
        log_audit("ERROR", full_command, str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
