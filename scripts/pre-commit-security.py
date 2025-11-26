#!/usr/bin/env python3
"""
Pre-commit hook to enforce security protocols.
Blocks commits if there are active DLP violations that should block development.
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import modules
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from src.security.dlp import DLPValidator, DLPViolationError
    from src.audit.immutable_audit import ImmutableAuditSystem
except ImportError as e:
    print(f"ERROR: Cannot import required modules: {e}")
    print("Make sure you're running this from the project root.")
    sys.exit(1)


def check_active_violations() -> bool:
    """Check if there are active DLP violations that should block development."""
    # Load DLP validator
    policy_path = os.environ.get("OMNIMIND_DLP_POLICY_FILE")
    if not policy_path:
        policy_path = str(project_root / "config" / "dlp_policies.yaml")

    validator = DLPValidator(policy_path=policy_path)

    # Check recent audit logs for violations
    audit_system = get_audit_system()
    recent_events = audit_system.get_recent_events(limit=50)

    blocking_violations = []
    for event in recent_events:
        if event.get("action") == "dlp.violation":
            details = event.get("details", {})
            if details.get("action") == "block":
                blocking_violations.append(details)

    if blocking_violations:
        print("🚫 COMMIT BLOCKED: Active DLP violations detected!")
        print("The following violations must be resolved before committing:")
        for violation in blocking_violations[-3:]:  # Show last 3
            print(f"  - Rule: {violation.get('rule', 'unknown')}")
            print(f"    Severity: {violation.get('severity', 'unknown')}")
            print(f"    Snippet: {violation.get('snippet', 'unknown')}")
        print("\nResolve violations and re-run security validation before committing.")
        return True

    return False


def main() -> int:
    """Main pre-commit hook logic."""
    print("🔒 Running OmniMind security pre-commit checks...")

    # Check for active blocking violations
    if check_active_violations():
        return 1  # Block commit

    # Check if sandbox is operational
    try:
        from security.firecracker_sandbox import FirecrackerSandbox

        sandbox = FirecrackerSandbox()
        if not sandbox.enabled:
            print("🚫 COMMIT BLOCKED: Firecracker sandbox is not operational!")
            print("Security protocols require sandbox isolation for all operations.")
            return 1
    except Exception as e:
        print(f"🚫 COMMIT BLOCKED: Cannot verify sandbox status: {e}")
        return 1

    print("✅ Security checks passed. Proceeding with commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
