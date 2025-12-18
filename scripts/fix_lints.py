#!/usr/bin/env python3
"""
Script automatizado para corrigir lints comuns do flake8.
"""
import re
from pathlib import Path


def fix_blank_lines_at_end(file_path):
    """Remove blank lines at end of file."""
    content = file_path.read_text()
    if content.endswith("\n\n"):
        file_path.write_text(content.rstrip() + "\n")
        return True
    return False


def fix_f_string_placeholders(file_path):
    """Convert f-strings without placeholders to regular strings."""
    content = file_path.read_text()
    # Match f"..." or f'...' without {} placeholders
    pattern = r'f(["\'])([^"\']*?)\1'

    def replacer(match):
        quote = match.group(1)
        text = match.group(2)
        if "{" not in text:
            return f"{quote}{text}{quote}"
        return match.group(0)

    new_content = re.sub(pattern, replacer, content)
    if new_content != content:
        file_path.write_text(new_content)
        return True
    return False


def main():
    project_root = Path("/home/fahbrain/projects/omnimind")

    # Fix blank lines in __init__.py files
    print("Fixing blank lines in __init__.py files...")
    for init_file in project_root.rglob("__init__.py"):
        if fix_blank_lines_at_end(init_file):
            print(f"  Fixed: {init_file.relative_to(project_root)}")

    # Fix f-strings in specific files
    print("\nFixing f-strings without placeholders...")
    files_to_fix = [
        "src/audit/immutable_audit.py",
        "src/tools/omnimind_test_analyzer.py",
    ]

    for file_path in files_to_fix:
        full_path = project_root / file_path
        if full_path.exists():
            if fix_f_string_placeholders(full_path):
                print(f"  Fixed: {file_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
