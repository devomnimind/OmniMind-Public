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

import json
import re
import sys
from pathlib import Path


def fix_integrity_metrics():
    """
    Fix corrupted integrity_metrics.json file by extracting valid JSON content.
    """
    log_dir = Path("logs")
    if not log_dir.exists():
        print("Logs directory not found.")
        return

    path = log_dir / "integrity_metrics.json"
    if not path.exists():
        print(f"File {path} not found.")
        return

    print(f"Analyzing {path}...")
    try:
        content = path.read_text()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Original content length: {len(content)}")
    print(f"Content preview: {content[:100]}...")

    # Try to parse as is
    try:
        data = json.loads(content)
        print("File is already valid JSON.")
        return
    except json.JSONDecodeError as e:
        print(f"File is corrupted: {e}")
        print("Attempting repair...")

    # Strategy 1: Find the last valid closing brace
    # The corruption pattern observed was `...}evel": "critical"`
    # This suggests content appended after the JSON object

    last_brace = content.rfind("}")
    if last_brace != -1:
        potential_json = content[: last_brace + 1]
        try:
            data = json.loads(potential_json)
            print("Recovered JSON data successfully using rfind strategy.")
            _save_fixed_file(path, data)
            return
        except json.JSONDecodeError:
            print("rfind strategy failed.")

    # Strategy 3: Iterative parsing
    # Try to parse content[:i+1] for every position i where content[i] == '}'

    indices = [i for i, char in enumerate(content) if char == "}"]
    for i in indices:
        potential_json = content[: i + 1]
        try:
            data = json.loads(potential_json)
            print(f"Recovered JSON data successfully at index {i}.")
            _save_fixed_file(path, data)
            return
        except json.JSONDecodeError:
            continue

    print("Could not repair file automatically.")


def _save_fixed_file(path: Path, data: dict):
    """Save the fixed data and backup the corrupted one."""
    backup_path = path.with_suffix(".json.corrupted")

    print(f"Backing up corrupted file to {backup_path}")
    try:
        path.rename(backup_path)
    except Exception as e:
        print(f"Warning: Could not rename original file: {e}")
        # If rename fails, we might still want to write the new file if possible,
        # but let's be safe and just write to a new file first

    print(f"Writing fixed content to {path}")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print("Success! File repaired.")


if __name__ == "__main__":
    fix_integrity_metrics()
