#!/usr/bin/env bash
# Safe wrapper to run automatic style & cleanup tools used by the team.
#
# This script runs `black` then `autoflake` (remove unused imports/vars) in
# a conservative manner. It's intended to be run locally and reviewed before
# committing. It also runs the safe fixer scripts added in this change.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Running black..."
black src tests scripts web || true

echo "Running remove_f_strings_without_placeholders.py..."
python3 scripts/fixers/remove_f_strings_without_placeholders.py || true

echo "Running add_test_return_annotations.py..."
python3 scripts/fixers/add_test_return_annotations.py || true

echo "Running parametrize_bare_generics_in_tests.py..."
python3 scripts/fixers/parametrize_bare_generics_in_tests.py || true

echo "Running autoflake to remove unused imports in demos/scripts/benchmarks (dry run off)"
autoflake --remove-all-unused-imports --ignore-init-module-imports --in-place -r demo scripts benchmarks web || true

echo "Format again after autoflake"
black src tests scripts web || true

echo "Done. Review changes and run the test/typing pipeline before committing."
