#!/usr/bin/env python3
"""
Classifica cada teste em: [MOCK], [SEMI-REAL], ou [REAL]

Lógica:
- [MOCK]: Tem @patch ou @mock (não toca sistema real)
- [SEMI-REAL]: Toca arquivo real OU toca rede OU toca GPU mas mocka LLM
- [REAL]: Sem @patch, toca sistema real completo (GPU + LLM + rede)
"""

import json
from pathlib import Path
from typing import TypedDict


class TestInfo(TypedDict, total=False):
    """Type definition for test info."""

    file_path: str
    test_name: str
    classification: str
    reason: str
    has_patch: bool


def extract_test_functions(source_code: str) -> dict[str, bool]:
    """Extract test function names and whether they have @patch."""
    tests = {}
    lines = source_code.split("\n")

    for i, line in enumerate(lines):
        # Check for @patch decorator
        has_patch = False
        if "@patch" in line or "@mock" in line.lower():
            has_patch = True

        # Check for test function
        if line.strip().startswith("def test_") or line.strip().startswith("async def test_"):
            # Extract function name
            func_match = line.strip().replace("async ", "").replace("def ", "").split("(")[0]
            tests[func_match] = has_patch

    return tests


def classify_test_simple(source_code: str, test_name: str) -> tuple[str, str]:
    """Simple classification based on code patterns."""
    has_patch = "@patch" in source_code
    has_mock = "@mock" in source_code.lower() or "Mock" in source_code

    # Check for real system access patterns
    touches_gpu = any(p in source_code for p in [".cuda", ".to(device)", "torch.", ".device"])
    touches_filesystem = "open(" in source_code and "@patch" not in source_code
    touches_network = any(p in source_code for p in ["aiohttp", "requests.", "httpx"])
    touches_llm = any(p in source_code for p in ["OllamaClient", "qwen2", "ollama", "OpenRouter"])

    # Classify
    if has_patch or has_mock:
        return "MOCK", "Uses @patch or @mock decorators"
    elif touches_llm and touches_gpu:
        return "REAL", "Executes GPU + LLM without mocks"
    elif touches_network or touches_filesystem or touches_llm:
        return "SEMI-REAL", "Touches real system (network/filesystem/GPU)"
    else:
        return "SEMI-REAL", "Internal logic test without mocks"


def main() -> None:
    """Scan all tests and classify."""
    tests_dir = Path("/home/fahbrain/projects/omnimind/tests")
    classifications = []

    # Find all test files
    test_files = sorted(tests_dir.rglob("test_*.py"))
    print(f"📂 Found {len(test_files)} test files\n")

    for file_path in test_files:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # Extract test functions
        try:
            tests = extract_test_functions(source)
        except Exception:
            continue

        for test_name, has_patch in tests.items():
            classification, reason = classify_test_simple(source, test_name)

            info: TestInfo = {
                "file_path": str(file_path),
                "test_name": test_name,
                "classification": classification,
                "reason": reason,
                "has_patch": has_patch,
            }
            classifications.append(info)

    # Statistics
    mock_count = sum(1 for c in classifications if c["classification"] == "MOCK")
    semi_count = sum(1 for c in classifications if c["classification"] == "SEMI-REAL")
    real_count = sum(1 for c in classifications if c["classification"] == "REAL")

    print("=" * 100)
    print("📊 TEST CLASSIFICATION SUMMARY")
    print("=" * 100)
    if classifications:
        print(
            f"[MOCK]      (uses @patch)  : {mock_count:4d} ({100*mock_count//len(classifications):3d}%)"
        )
        print(
            f"[SEMI-REAL] (real GPU/LLM) : {semi_count:4d} ({100*semi_count//len(classifications):3d}%)"
        )
        print(
            f"[REAL]      (full system)  : {real_count:4d} ({100*real_count//len(classifications):3d}%)"
        )
    print(f"{'=' * 100}")
    print(f"TOTAL                       : {len(classifications):4d}\n")

    # Save JSON
    output_file = Path("/home/fahbrain/projects/omnimind/data/test_classifications.json")
    output_file.parent.mkdir(exist_ok=True, parents=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(classifications, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {output_file}")

    # Print breakdown by category
    print("\n" + "=" * 100)
    print("[MOCK] TESTS (using @patch):")
    print("=" * 100)
    mock_tests = [c for c in classifications if c["classification"] == "MOCK"]
    for c in mock_tests[:20]:
        fname = Path(c["file_path"]).name
        print(f"  {fname:40s} :: {c['test_name']:50s}")
    if len(mock_tests) > 20:
        print(f"  ... and {len(mock_tests) - 20} more mock tests")

    print("\n" + "=" * 100)
    print("[SEMI-REAL] TESTS (touches real system):")
    print("=" * 100)
    semi_tests = [c for c in classifications if c["classification"] == "SEMI-REAL"]
    for c in semi_tests[:15]:
        fname = Path(c["file_path"]).name
        print(f"  {fname:40s} :: {c['test_name']:50s}")
    if len(semi_tests) > 15:
        print(f"  ... and {len(semi_tests) - 15} more semi-real tests")

    print("\n" + "=" * 100)
    print("[REAL] TESTS (full GPU + LLM + Network):")
    print("=" * 100)
    real_tests = [c for c in classifications if c["classification"] == "REAL"]
    if real_tests:
        for c in real_tests:
            fname = Path(c["file_path"]).name
            print(f"  {fname:40s} :: {c['test_name']:50s}")
    else:
        print("  ⚠️  NO FULLY REAL TESTS FOUND")


if __name__ == "__main__":
    main()
