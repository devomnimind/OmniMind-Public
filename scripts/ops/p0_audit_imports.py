#!/usr/bin/env python3
"""
P0 AUDIT: Import Breakage from Module Deprecation
Scans entire codebase for broken imports caused by deprecated modules.
"""
import ast
import sys
from pathlib import Path
from collections import defaultdict
import importlib.util

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT))


def check_import(module_path: str) -> tuple[bool, str]:
    """Check if a module can be imported."""
    try:
        spec = importlib.util.find_spec(module_path)
        if spec is None:
            return False, "Module not found"
        return True, "OK"
    except (ModuleNotFoundError, ValueError, ImportError) as e:
        return False, str(e)


def extract_imports(file_path: Path) -> list[dict]:
    """Extract all imports from a Python file."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({"type": "import", "module": alias.name, "line": node.lineno})
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(
                        {
                            "type": "from_import",
                            "module": node.module,
                            "names": [a.name for a in node.names],
                            "line": node.lineno,
                        }
                    )
        return imports
    except SyntaxError:
        return []


def scan_codebase():
    """Scan entire codebase for import issues."""
    src_dir = PROJECT_ROOT / "src"

    broken_imports = defaultdict(list)
    deprecated_modules = {}

    # Find deprecated modules
    for py_file in src_dir.rglob("*.py"):
        try:
            with open(py_file) as f:
                content = f.read()
                if "DEPRECATED" in content and "__init__.py" in str(py_file):
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    module_path = str(rel_path.with_suffix("")).replace("/", ".")
                    deprecated_modules[module_path] = py_file
        except:
            pass

    # Check all imports
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        imports = extract_imports(py_file)
        for imp in imports:
            module = imp["module"]

            # Convert relative imports to absolute
            if module.startswith("."):
                # Calculate absolute module path
                file_module = str(py_file.relative_to(src_dir).with_suffix("")).replace("/", ".")
                parts = file_module.split(".")
                level = len(module) - len(module.lstrip("."))
                base_parts = parts[:-1] if "__init__" not in str(py_file) else parts

                if level > len(base_parts):
                    continue

                base = ".".join(base_parts[:-level] if level else base_parts)
                module_clean = module.lstrip(".")
                absolute_module = f"{base}.{module_clean}" if module_clean else base
                full_module = f"src.{absolute_module}"
            else:
                full_module = module if module.startswith("src.") else f"src.{module}"

            # Check if import works
            can_import, error = check_import(full_module)

            if not can_import:
                broken_imports[str(py_file.relative_to(PROJECT_ROOT))].append(
                    {
                        "line": imp["line"],
                        "module": module,
                        "absolute": full_module,
                        "error": error,
                        "names": imp.get("names", []),
                    }
                )

    return broken_imports, deprecated_modules


def main():
    print("🔍 P0 AUDIT: Scanning for import breakage...")
    broken, deprecated = scan_codebase()

    print(f"\n📋 DEPRECATED MODULES FOUND: {len(deprecated)}")
    for mod, path in deprecated.items():
        print(f"  - {mod}")
        print(f"    Path: {path.relative_to(PROJECT_ROOT)}")

    print(
        f"\n❌ BROKEN IMPORTS FOUND: {sum(len(v) for v in broken.values())} in {len(broken)} files"
    )

    # Group by error type
    by_module = defaultdict(list)
    for file, imports in broken.items():
        for imp in imports:
            by_module[imp["absolute"]].append((file, imp["line"], imp.get("names", [])))

    print("\n📊 BREAKDOWN BY MODULE:")
    for module, occurrences in sorted(by_module.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n  {module} ({len(occurrences)} occurrences)")
        for file, line, names in occurrences[:5]:  # Show first 5
            names_str = f" [{', '.join(names)}]" if names else ""
            print(f"    → {file}:{line}{names_str}")
        if len(occurrences) > 5:
            print(f"    ... and {len(occurrences) - 5} more")

    # Save detailed report
    report_path = PROJECT_ROOT / "data/audit/p0_import_breakage_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    import json

    with open(report_path, "w") as f:
        json.dump(
            {
                "deprecated_modules": {
                    k: str(v.relative_to(PROJECT_ROOT)) for k, v in deprecated.items()
                },
                "broken_imports": {k: v for k, v in broken.items()},
                "summary": {
                    "total_broken_files": len(broken),
                    "total_broken_imports": sum(len(v) for v in broken.values()),
                    "unique_modules": len(by_module),
                },
            },
            f,
            indent=2,
        )

    print(f"\n💾 Full report saved to: {report_path.relative_to(PROJECT_ROOT)}")

    return len(broken) > 0


if __name__ == "__main__":
    has_errors = main()
    sys.exit(1 if has_errors else 0)
