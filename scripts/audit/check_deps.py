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

import ast
import os


def get_imports(root_dir):
    imports = set()
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split(".")[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split(".")[0])
                except Exception as e:
                    print(f"Error parsing {path}: {e}")
    return imports


def check_requirements(req_file, used_imports):
    with open(req_file, "r") as f:
        requirements = {
            line.strip().split("==")[0].split(">=")[0].lower()
            for line in f
            if line.strip() and not line.startswith("#")
        }

    used_imports = {i.lower() for i in used_imports}

    # Standard library (approximate list or ignore knowns)
    stdlib = {
        "os",
        "sys",
        "json",
        "time",
        "logging",
        "typing",
        "collections",
        "datetime",
        "math",
        "random",
        "re",
        "subprocess",
        "pathlib",
        "abc",
        "ast",
        "shutil",
        "uuid",
        "threading",
        "functools",
        "itertools",
        "io",
        "glob",
        "platform",
        "traceback",
        "inspect",
        "contextlib",
        "enum",
        "copy",
        "signal",
        "socket",
        "tempfile",
        "unittest",
        "warnings",
        "zipfile",
        "hashlib",
        "base64",
        "csv",
        "pickle",
        "struct",
        "weakref",
        "heapq",
        "bisect",
        "queue",
        "multiprocessing",
        "concurrent",
        "asyncio",
        "dataclasses",
        "textwrap",
        "urllib",
        "http",
        "email",
        "xml",
        "html",
        "pydoc",
        "doctest",
        "pdb",
        "profile",
        "cProfile",
        "timeit",
        "trace",
        "tracemalloc",
        "distutils",
        "ensurepip",
        "venv",
        "curses",
        "tkinter",
        "turtle",
        "cmd",
        "shlex",
    }

    unused = requirements - used_imports
    missing = (
        used_imports - requirements - stdlib - {"src", "tests", "scripts"}
    )  # Exclude local packages

    return unused, missing


if __name__ == "__main__":
    used = get_imports("src")
    if os.path.exists("requirements.txt"):
        unused, missing = check_requirements("requirements.txt", used)
        print("UNUSED DEPENDENCIES (in requirements.txt but not imported in src):")
        for u in sorted(unused):
            print(f"- {u}")
        print("\nPOTENTIALLY MISSING DEPENDENCIES (imported in src but not in requirements.txt):")
        for m in sorted(missing):
            print(f"- {m}")
    else:
        print("requirements.txt not found")
