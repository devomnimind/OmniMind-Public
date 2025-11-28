#!/usr/bin/env python3
"""
Script to fix import ordering issues in Python files.
Moves all imports to the top after __future__ imports.
"""

import sys
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import ordering in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        future_imports = []
        regular_imports = []
        other_lines = []
        in_docstring = False
        docstring_delimiter = None

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Handle docstrings
            if line.startswith('"""') or line.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                    docstring_delimiter = '"""' if line.startswith('"""') else "'''"
                    other_lines.append(lines[i])
                    i += 1
                    continue
                elif in_docstring and ((docstring_delimiter == '"""' and line.endswith('"""')) or
                                     (docstring_delimiter == "'''" and line.endswith("'''"))):
                    in_docstring = False
                    docstring_delimiter = None
                    other_lines.append(lines[i])
                    i += 1
                    continue
                else:
                    other_lines.append(lines[i])
                    i += 1
                    continue
            elif in_docstring:
                other_lines.append(lines[i])
                i += 1
                continue

            # Skip empty lines and comments at the top
            if not line or line.startswith('#'):
                if not future_imports and not regular_imports:
                    other_lines.append(lines[i])
                else:
                    # After imports started, collect these
                    other_lines.append(lines[i])
                i += 1
                continue

            # Check for __future__ imports
            if line.startswith('from __future__ import'):
                future_imports.append(lines[i])
                i += 1
                continue

            # Check for regular imports
            if line.startswith('import ') or line.startswith('from ') and 'import' in line:
                regular_imports.append(lines[i])
                i += 1
                continue

            # Everything else goes to other_lines
            other_lines.append(lines[i])
            i += 1

        # Reconstruct the file
        new_lines = []

        # Add future imports first
        new_lines.extend(future_imports)

        # Add regular imports
        if future_imports and regular_imports:
            new_lines.append('')  # Empty line between future and regular imports
        new_lines.extend(regular_imports)

        # Add the rest
        if (future_imports or regular_imports) and other_lines:
            new_lines.append('')  # Empty line before other content
        new_lines.extend(other_lines)

        # Write back
        new_content = '\n'.join(new_lines)
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix imports in all Python files."""
    if len(sys.argv) != 2:
        print("Usage: python fix_imports_order.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        sys.exit(1)

    fixed_count = 0
    total_count = 0

    for py_file in directory.rglob('*.py'):
        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
            print(f"Fixed: {py_file}")

    print(f"\nFixed {fixed_count} out of {total_count} Python files")

if __name__ == '__main__':
    main()