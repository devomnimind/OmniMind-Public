#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""
import sys
from pathlib import Path

from security.firecracker_sandbox import FirecrackerSandbox

# Add src to path so we can import modules
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from src.audit.audit_system import get_audit_system
except ImportError as e:
    print(f"ERROR: Cannot import required modules: {e}")
    print("Make sure you're running this from the project root.")
    sys.exit(1)


def check_active_violations() -> bool:
    """Check if there are active DLP violations that should block development."""
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
