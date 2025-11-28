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
Add conservative type parameters to bare generics inside `tests/` files.

This script replaces bare `Dict`, `List`, `Tuple`, `Set` (without []) with
`Dict[Any, Any]`, `List[Any]`, `Tuple[Any, ...]`, `Set[Any]` respectively.
It will also insert `from typing import Any` into files that need it.

This is intentionally conservative and limited to `tests/` where quick
suppression of missing type arguments will help the typing sweep.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


TESTS_ROOT = Path(__file__).resolve().parents[2] / "tests"

BARE_REPLACEMENTS = {
    r"\bDict\b(?!\[)": "Dict[Any, Any]",
    r"\bList\b(?!\[)": "List[Any]",
    r"\bTuple\b(?!\[)": "Tuple[Any, ...]",
    r"\bSet\b(?!\[)": "Set[Any]",
}

IMPORT_CHECK = re.compile(r"from\s+typing\s+import\s+(.*)")


def find_test_files() -> Iterable[Path]:
    for p in TESTS_ROOT.rglob("*.py"):
        yield p


def add_any_import(text: str) -> str:
    # Ensure 'Any' is imported from typing
    if "Any" in text:
        # check if typing import exists
        if "from typing import" not in text:
            # add top-of-file import for Any
            return "from typing import Any\n" + text
        if "Any" in text:
            # already present or will be used; ensure Any present in import
            def_line_idx = None
            lines = text.splitlines()
            for i, ln in enumerate(lines[:10]):
                if ln.strip().startswith("from typing import"):
                    def_line_idx = i
                    break
            if def_line_idx is None:
                return "from typing import Any\n" + text
            # If Any not present in the import, add it
            if "Any" not in lines[def_line_idx]:
                lines[def_line_idx] = lines[def_line_idx].rstrip() + ", Any"
            return "\n".join(lines)
    return text


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf8")
    changed = False

    for pattern, repl in BARE_REPLACEMENTS.items():
        new_text = re.sub(pattern, repl, text)
        if new_text != text:
            text = new_text
            changed = True

    if changed and "Any" in text:
        text = add_any_import(text)

    if changed:
        path.write_text(text, encoding="utf8")

    return changed


def main() -> None:
    touched = []
    for f in find_test_files():
        try:
            if fix_file(f):
                touched.append(str(f))
        except Exception:
            continue

    print(f"Patched {len(touched)} test files to add conservative generic params")
    for p in touched[:50]:
        print(" -", p)


if __name__ == "__main__":
    main()
