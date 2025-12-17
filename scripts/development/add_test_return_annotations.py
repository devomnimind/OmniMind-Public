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
Add `-> None` return annotations to test functions missing them.

This script edits files under `tests/` and adds `-> None` to definitions
starting with `def test_...` that are missing an explicit return annotation.

It performs a conservative, idempotent transformation and writes changes
back to the files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


TESTS_DIR = Path(__file__).resolve().parents[2] / "tests"


def find_test_files() -> Iterable[Path]:
    for p in TESTS_DIR.rglob("*.py"):
        yield p


RE_DEF = re.compile(r"^(\s*)def\s+(test_[A-Za-z0-9_]+)\s*\((.*?)\)\s*:\s*$")


def add_return_none_to_tests(path: Path) -> bool:
    text = path.read_text(encoding="utf8")
    changed = False
    out_lines: list[str] = []

    for line in text.splitlines(keepends=False):
        match = RE_DEF.match(line)
        if match:
            indent, name, params = match.groups()
            # skip if already annotated on the same line (-> present)
            if "->" in line:
                out_lines.append(line)
                continue

            # Add explicit -> None before the colon
            new_line = f"{indent}def {name}({params}) -> None:"
            out_lines.append(new_line)
            changed = True
        else:
            out_lines.append(line)

    if changed:
        path.write_text("\n".join(out_lines) + "\n", encoding="utf8")

    return changed


def main() -> None:
    changed_files = []
    for f in find_test_files():
        if add_return_none_to_tests(f):
            changed_files.append(str(f))

    print(f"Updated {len(changed_files)} test files:")
    for p in changed_files[:50]:
        print(" -", p)


if __name__ == "__main__":
    main()
