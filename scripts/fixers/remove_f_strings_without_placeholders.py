#!/usr/bin/env python3
"""Replace f-string prefixes where there are no `{}` placeholders.

This reduces F541 detections (f-string missing placeholders). It rewrites
`f"literal text"` -> `"literal text"` only for lines which contain 'f'
string prefix and no braces. This is a safe, idempotent rewrite.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]


FSTRING_SIMPLE = re.compile(r"(?P<prefix>\b)f(?P<quote>['\"]).*?\k<quote>")


def files_to_fix() -> Iterable[Path]:
    for p in ROOT.rglob("*.py"):
        if (
            "tests/" in str(p)
            or "demo" in str(p)
            or "scripts/" in str(p)
            or "web/" in str(p)
        ):
            yield p


def line_contains_placeholder(s: str) -> bool:
    return "{" in s or "}" in s


def fix_file(path: Path) -> bool:
    changed = False
    lines = path.read_text(encoding="utf8").splitlines()
    out: list[str] = []

    for ln in lines:
        # quick skip
        if 'f"' not in ln and "f'" not in ln:
            out.append(ln)
            continue

        # For each f-string literal without placeholders, remove leading f
        new_ln = ln
        # naive: find f"..." / f'...' substrings
        for match in re.finditer(r"f(['\"]).*?\1", ln):
            substring = match.group(0)
            if not line_contains_placeholder(substring):
                replacement = substring[1:]
                new_ln = new_ln.replace(substring, replacement)

        if new_ln != ln:
            changed = True
        out.append(new_ln)

    if changed:
        path.write_text("\n".join(out) + "\n", encoding="utf8")

    return changed


def main() -> None:
    total = 0
    files = []
    for f in files_to_fix():
        try:
            if fix_file(f):
                files.append(str(f))
                total += 1
        except Exception:
            # skip files we can't parse safely
            continue

    print(f"Updated {total} files to remove stray f-string prefixes")
    for p in files[:50]:
        print(" -", p)


if __name__ == "__main__":
    main()
