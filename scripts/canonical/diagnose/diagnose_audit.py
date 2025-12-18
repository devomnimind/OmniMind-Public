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

import hashlib
import json
from pathlib import Path


def hash_content(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def diagnose_chain(log_file: str):
    path = Path(log_file)
    if not path.exists():
        print(f"Log file not found: {log_file}")
        return

    print(f"Diagnosing {log_file}...")

    prev_hash = "0" * 64

    with open(path, "rb") as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        try:
            event = json.loads(line)
            action = event.get("action", "")
            stored_prev_hash = event.get("prev_hash")
            stored_current_hash = event.get("current_hash")

            # Check 1: Prev Hash Link
            if action == "audit_system_initialized":
                print(f"[INFO] Line {line_num}: System Initialized. Resetting chain.")
                prev_hash = "0" * 64  # Reset expected prev hash
                # But we still check if the event claims the correct prev_hash (which should be 0*64)

            if stored_prev_hash != prev_hash:
                print(f"[ERROR] Line {line_num}: Broken Link!")
                print(f"  Action: {action}")
                print(f"  Expected Prev Hash: {prev_hash[:16]}...")
                print(f"  Found Prev Hash:    {stored_prev_hash[:16]}...")
                # We don't stop, we continue to see if it's just one event or a total corruption
                # To continue checking, we assume the chain *should* have continued from this event's claim?
                # Or we stick to our calculated prev_hash?
                # Usually if link is broken, we can't trust the rest. But let's see if the hash ITSELF is valid.

            # Check 2: Content Hash Integrity
            event_for_hash = {
                "action": event.get("action"),
                "category": event.get("category"),
                "details": event.get("details"),
                "timestamp": event.get("timestamp"),
                "datetime_utc": event.get("datetime_utc"),
                "prev_hash": event.get("prev_hash"),
            }

            json_data = json.dumps(event_for_hash, sort_keys=True).encode("utf-8")
            calculated_hash = hash_content(json_data)

            if calculated_hash != stored_current_hash:
                print(f"[ERROR] Line {line_num}: Hash Mismatch!")
                print(f"  Action: {action}")
                print(f"  Calculated: {calculated_hash[:16]}...")
                print(f"  Stored:     {stored_current_hash[:16]}...")

            # Update prev_hash for next iteration
            # If we want to follow the file's chain even if broken:
            prev_hash = stored_current_hash

            # If we want to follow strict chain:
            # prev_hash = calculated_hash

        except json.JSONDecodeError:
            print(f"[ERROR] Line {line_num}: Invalid JSON")


if __name__ == "__main__":
    diagnose_chain("logs/audit_chain.log")
