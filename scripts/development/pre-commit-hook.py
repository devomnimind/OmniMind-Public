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

"""
Pre-commit hook to enforce security protocols.
Blocks commits if there are active DLP violations that should block development.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def check_active_violations():
    """Check if there are active DLP violations that should block development."""
    try:
        import json
        from pathlib import Path

        # Read audit log directly
        log_file = Path(__file__).parent.parent / "logs" / "audit_chain.log"
        if not log_file.exists():
            return []

        events = []
        with open(log_file, "r") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    events.append(event)
                except json.JSONDecodeError:
                    continue

        # Check for unresolved blocking violations
        violations = []
        resolutions = []

        for event in events[-100:]:  # Last 100 events
            if event.get("action") == "dlp.violation":
                details = event.get("details", {})
                if details.get("action") == "block":
                    violations.append(details)
            elif event.get("action") == "dlp.violation_resolved":
                details = event.get("details", {})
                resolutions.append(details.get("rule"))

        # Filter out resolved violations
        active_violations = []
        for violation in violations:
            rule = violation.get("rule")
            if rule not in resolutions:
                active_violations.append(violation)

        return active_violations
    except Exception as e:
        print(f"ERROR: Cannot check violations: {e}")
        return []


def main():
    """Main pre-commit hook logic."""
    print("🔒 Running OmniMind security pre-commit checks...")

    # Check for active blocking violations
    violations = check_active_violations()
    if violations:
        print("🚫 COMMIT BLOCKED: Active DLP violations detected!")
        print("The following violations must be resolved before committing:")
        for violation in violations[-3:]:  # Show last 3
            print(f"  - Rule: {violation.get('rule', 'unknown')}")
            print(f"    Severity: {violation.get('severity', 'unknown')}")
        print("\nResolve violations and re-run security validation before committing.")
        return 1

    # Check if sandbox is operational
    try:
        import os
        from pathlib import Path

        kernel_path = os.environ.get("OMNIMIND_FIRECRACKER_KERNEL", "/opt/firecracker/vmlinux.bin")
        rootfs_path = os.environ.get("OMNIMIND_FIRECRACKER_ROOTFS", "/opt/firecracker/rootfs.ext4")

        if not Path(kernel_path).exists() or not Path(rootfs_path).exists():
            print("🚫 COMMIT BLOCKED: Firecracker sandbox assets missing!")
            print("Security protocols require sandbox isolation for all operations.")
            return 1
    except Exception as e:
        print(f"🚫 COMMIT BLOCKED: Cannot verify sandbox status: {e}")
        return 1

    print("✅ Security checks passed. Proceeding with commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
