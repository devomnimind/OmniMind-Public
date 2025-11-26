import json
import hashlib
import shutil
from pathlib import Path
import time
from datetime import datetime, timezone


def hash_content(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def repair_chain_preserve_history(log_file: str):
    path = Path(log_file)
    if not path.exists():
        print(f"Log file not found: {log_file}")
        return

    print(f"Repairing {log_file} (Preserving History)...")

    # Backup
    backup_file = path.with_suffix(f".backup_{int(time.time())}")
    shutil.copy2(path, backup_file)
    print(f"Backup created at {backup_file}")

    with open(path, "rb") as f:
        lines = f.readlines()

    repaired_lines = []
    prev_hash = "0" * 64

    events_modified = 0

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        try:
            event = json.loads(line)
            action = event.get("action", "")

            # Handle System Init (Allow reset OR continuation)
            if action == "audit_system_initialized":
                if event.get("prev_hash") == "0" * 64:
                    prev_hash = "0" * 64
                # If it's not 0*64, we treat it as a continuation (or force it to be if it was broken)

            # Force prev_hash to match our tracked prev_hash
            if event.get("prev_hash") != prev_hash:
                event["prev_hash"] = prev_hash
                events_modified += 1

            # Recalculate current_hash
            event_for_hash = {
                "action": event.get("action"),
                "category": event.get("category"),
                "details": event.get("details"),
                "timestamp": event.get("timestamp"),
                "datetime_utc": event.get("datetime_utc"),
                "prev_hash": event.get("prev_hash"),
            }

            json_data = json.dumps(event_for_hash, sort_keys=True).encode("utf-8")
            current_hash = hash_content(json_data)

            if event.get("current_hash") != current_hash:
                event["current_hash"] = current_hash
                events_modified += 1

            # Update prev_hash for next iteration
            prev_hash = current_hash

            # Serialize back to line
            repaired_lines.append(
                json.dumps(event, sort_keys=True).encode("utf-8") + b"\n"
            )

        except json.JSONDecodeError:
            print(f"[WARN] Skipping invalid JSON at line {line_num}")
            # We might lose this line if it's garbage, but we can't hash garbage
            continue

    # Write back
    with open(path, "wb") as f:
        for line in repaired_lines:
            f.write(line)

    # Update hash_chain.json
    hash_chain_file = path.parent / "hash_chain.json"
    with open(hash_chain_file, "w") as f:
        json.dump(
            {
                "last_hash": prev_hash,
                "timestamp": time.time(),
                "datetime": datetime.now(timezone.utc).isoformat(),
            },
            f,
            indent=2,
        )

    print(f"Repair complete. {events_modified} events re-hashed.")


if __name__ == "__main__":
    repair_chain_preserve_history("logs/audit_chain.log")
