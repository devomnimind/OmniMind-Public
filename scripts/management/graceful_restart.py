#!/usr/bin/env python3
"""
Graceful Restart Protocol for OmniMind.
Ensures evolution persistence by logging a signature containing recent highlights
from the walkthrough before performing a safe system restart.

Usage:
    python3 scripts/management/graceful_restart.py [--timeout 60] [--dry-run]
"""

import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

try:
    from src.audit.immutable_audit import ImmutableAuditSystem

    HAS_AUDIT = True
except ImportError:
    HAS_AUDIT = False

# Configuration
# Path to the current active walkthrough artifact
WALKTHROUGH_PATH = Path(
    "/home/fahbrain/.gemini/antigravity/brain/49de7867-8b85-4400-90e6-1a4a429307ed/walkthrough.md"
)
SIGNATURE_DIR = PROJECT_ROOT / "data/autopoietic/evolution_signatures"
SERVICE_NAME = "omnimind-backend.service"


def get_recent_highlights():
    """Extract summary from walkthrough.md."""
    if not WALKTHROUGH_PATH.exists():
        return f"Walkthrough not found at {WALKTHROUGH_PATH}. No summary available."

    try:
        content = WALKTHROUGH_PATH.read_text()
        # Look for Phase sections or Highlights
        lines = content.splitlines()
        highlights = []
        capture = False

        for line in lines:
            # Capture Phase 9 and beyond, or the specific safety section
            if "Phase 9" in line or "Ethical & Safety" in line:
                capture = True
            if capture:
                if line.strip().startswith("- ") or line.strip().startswith("* "):
                    highlights.append(line.strip())
            # Stop if we hit another main header or have enough highlights
            if capture and line.strip().startswith("## ") and len(highlights) > 3:
                break
            if capture and len(highlights) > 15:
                break

        return highlights if highlights else ["No specific highlights extracted from walkthrough."]
    except Exception as e:
        return [f"Error extracting highlights: {e}"]


def create_evolution_signature(highlights):
    """Generate a signed JSON blob with the current state."""
    signature = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": "Graceful Evolution Restart",
        "highlights": highlights,
        "environment": "Production",
        "protocol_version": "1.1.0 (Evolutionary Persistence)",
    }

    # Save to disk
    SIGNATURE_DIR.mkdir(parents=True, exist_ok=True)
    sig_file = SIGNATURE_DIR / f"reboot_signature_{int(time.time())}.json"
    sig_file.write_text(json.dumps(signature, indent=2, ensure_ascii=False))

    # Symlink to latest
    latest_link = SIGNATURE_DIR / "latest_signature.json"
    if latest_link.exists():
        latest_link.unlink()
    try:
        latest_link.symlink_to(sig_file.name)
    except Exception:
        # Fallback if symlink fails
        latest_link.write_text(json.dumps(signature, indent=2, ensure_ascii=False))

    return signature, sig_file


def log_to_audit(signature):
    """Inscribe signature into the immutable audit chain."""
    if not HAS_AUDIT:
        print("Warning: ImmutableAuditSystem not available, skipping audit chain log.")
        return

    try:
        # Project logs directory
        audit = ImmutableAuditSystem(log_dir=str(PROJECT_ROOT / "logs"))
        audit.log_action(
            action="SYSTEM_GRACEFUL_RESTART",
            details={
                "message": "Iniciando reinicialização graciosa e evolutiva.",
                "signature": signature,
            },
            category="autopoiesis",
        )
        print("✅ Evolution signature inscribed in the immutable audit chain.")
    except Exception as e:
        print(f"Error logging to audit: {e}")


def perform_restart(timeout):
    """Execute the restart via systemctl or manual signal."""
    print(f"🚀 Initiating graceful restart of {SERVICE_NAME}...")

    # Check if systemctl is available and service is loaded
    try:
        check = subprocess.run(
            ["systemctl", "is-active", SERVICE_NAME], capture_output=True, text=True
        )
        if check.returncode == 0:
            print(f"Using systemctl to restart {SERVICE_NAME} (Wait window: {timeout}s)...")
            # Usually requires sudo. If it fails, we inform the user.
            try:
                subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=True)
                print("✅ Restart command sent to systemd.")
                return True
            except subprocess.CalledProcessError:
                print("Warning: Failed to use 'sudo systemctl'.")
            except FileNotFoundError:
                print("Warning: 'sudo' not found.")
    except FileNotFoundError:
        print("systemctl not found. Using manual signal protocol.")

    # Manual signal logic is complex due to multiple processes in the autopoietic system.
    # We encourage the use of the systemd service for maximum reliability.
    print("❌ Automatic restart failed/requires manual action. Please execute:")
    print(f"   sudo systemctl restart {SERVICE_NAME}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Graceful Restart Protocol")
    parser.add_argument("--timeout", type=int, default=60, help="Wait timeout in seconds")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform signature and logging without actual restart",
    )
    args = parser.parse_args()

    print("--- OmniMind Graceful Evolution Protocol ---")

    # 1. Gather Intelligence
    highlights = get_recent_highlights()
    print(f"Found {len(highlights)} highlights to sign.")

    # 2. Create Signature
    signature, sig_file = create_evolution_signature(highlights)
    print(f"Created evolution signature: {sig_file}")

    # 3. Audit Log
    log_to_audit(signature)

    if args.dry_run:
        print("--- DRY RUN COMPLETE ---")
        return

    # 4. Global Communication
    print("\n[TRANSITION SIGNATURE]")
    print("Resumo da Evolução:")
    for h in highlights:
        print(f"  {h}")
    print("\nO sistema entrará em hibernação temporária para integração de mudanças.")
    print(f"Timeout de encerramento: {args.timeout}s.")

    # 5. Restart
    perform_restart(args.timeout)


if __name__ == "__main__":
    main()
