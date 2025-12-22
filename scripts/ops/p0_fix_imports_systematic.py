#!/usr/bin/env python3
"""
P0: Systematic Import Fix - Deprecated Modules
Fixes all broken imports caused by module refactoring in bulk.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")

# Mapping of deprecated -> correct paths
IMPORT_FIXES = {
    # observability -> monitor
    r"from \.\.observability\.module_logger": "from ..monitor.module_logger",
    r"from \.\.observability\.module_metrics": "from ..monitor.module_metrics",
    r"from \.\.observability\.module_reporter": "from ..monitor.module_reporter",
    r"from \.\.observability": "from ..monitor",
    # orchestrator -> orchestration
    r"from \.\.orchestrator\.": "from ..orchestration.",
    r"from \.\.orchestrator import": "from ..orchestration import",
    # defense -> security.defense
    r"from \.\.defense import": "from ..security.defense import",
    r"from \.\.defense\.": "from ..security.defense.",
    # quantum_consciousness -> quantum.consciousness
    r"from \.\.quantum_consciousness\.": "from ..quantum.consciousness.",
    r"from \.\.quantum_consciousness import": "from ..quantum.consciousness import",
    # quantum_real -> quantum.backends
    r"from \.\.quantum_real\.": "from ..quantum.backends.",
    r"from \.\.quantum_real import": "from ..quantum.backends import",
    # quantum_ai -> quantum
    r"from \.\.quantum_ai\.": "from ..quantum.",
    r"from \.\.quantum_ai import": "from ..quantum import",
    # memory deprecated patterns (if any specific ones exist)
    # Add more patterns as discovered
}


def fix_file_imports(file_path: Path) -> tuple[int, list[str]]:
    """Fix imports in a single file. Returns (fixes_count, errors)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        fixes_made = []

        for pattern, replacement in IMPORT_FIXES.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes_made.append(f"{pattern} -> {replacement}")

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return len(fixes_made), []

        return 0, []

    except PermissionError:
        return 0, [f"LOCKED: {file_path} (chattr +i)"]
    except Exception as e:
        return 0, [f"ERROR: {file_path}: {e}"]


def main():
    src_dir = PROJECT_ROOT / "src"

    stats = {
        "files_scanned": 0,
        "files_fixed": 0,
        "total_fixes": 0,
        "locked_files": [],
        "errors": [],
    }

    print("🔧 P0: Systematic Import Correction")
    print(f"Scanning: {src_dir}")
    print()

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        stats["files_scanned"] += 1
        fixes, errors = fix_file_imports(py_file)

        if fixes > 0:
            stats["files_fixed"] += 1
            stats["total_fixes"] += fixes
            rel_path = py_file.relative_to(PROJECT_ROOT)
            print(f"✅ {rel_path}: {fixes} fixes")

        if errors:
            for err in errors:
                if "LOCKED" in err:
                    stats["locked_files"].append(str(py_file.relative_to(PROJECT_ROOT)))
                else:
                    stats["errors"].append(err)

    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print(f"Files scanned: {stats['files_scanned']}")
    print(f"Files fixed: {stats['files_fixed']}")
    print(f"Total fixes applied: {stats['total_fixes']}")
    print(f"Locked files (requires sudo chattr -i): {len(stats['locked_files'])}")
    print(f"Errors: {len(stats['errors'])}")

    if stats["locked_files"]:
        print()
        print("🔒 LOCKED FILES (require kernel unlock):")
        for f in stats["locked_files"][:20]:
            print(f"  - {f}")
        if len(stats["locked_files"]) > 20:
            print(f"  ... and {len(stats['locked_files']) - 20} more")

    if stats["errors"]:
        print()
        print("❌ ERRORS:")
        for e in stats["errors"][:10]:
            print(f"  - {e}")

    # Save report
    report_path = PROJECT_ROOT / "data/audit/p0_import_fixes_applied.json"
    import json

    with open(report_path, "w") as f:
        json.dump(stats, f, indent=2)

    print()
    print(f"💾 Report saved: {report_path.relative_to(PROJECT_ROOT)}")

    return 0 if stats["total_fixes"] > 0 else 1


if __name__ == "__main__":
    exit(main())
