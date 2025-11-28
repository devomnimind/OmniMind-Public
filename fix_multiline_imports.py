#!/usr/bin/env python3
"""
Script to fix broken multiline imports caused by the previous import ordering script.
"""

import sys
from pathlib import Path

def fix_multiline_imports(file_path):
    """Fix broken multiline imports in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Check if this is a broken multiline import
            if line.startswith('from ') and line.endswith('import (') and i + 1 < len(lines):
                # This is a broken multiline import, find the next line
                next_line = lines[i + 1].strip()
                if next_line.startswith('from ') and 'import' in next_line:
                    # Combine them
                    combined = line + ' ' + next_line
                    fixed_lines.append(combined)
                    i += 2  # Skip the next line
                    continue

            # Check for other broken patterns
            if line.startswith('from ') and line.count('(') == 1 and not line.strip().endswith(')'):
                # Find the closing parenthesis
                j = i + 1
                import_parts = [line]
                while j < len(lines):
                    next_part = lines[j].strip()
                    import_parts.append(lines[j])
                    if next_part.strip().endswith(')'):
                        # Found the end, combine all parts
                        combined_import = '\n'.join(import_parts)
                        fixed_lines.append(combined_import)
                        i = j + 1
                        break
                    j += 1
                else:
                    # No closing paren found, just add the line
                    fixed_lines.append(lines[i])
                    i += 1
            else:
                fixed_lines.append(lines[i])
                i += 1

        new_content = '\n'.join(fixed_lines)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix multiline imports in all Python files."""
    if len(sys.argv) != 2:
        print("Usage: python fix_multiline_imports.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        sys.exit(1)

    fixed_count = 0
    total_count = 0

    for py_file in directory.rglob('*.py'):
        total_count += 1
        if fix_multiline_imports(py_file):
            fixed_count += 1
            print(f"Fixed: {py_file}")

    print(f"\nFixed {fixed_count} out of {total_count} Python files")

if __name__ == '__main__':
    main()