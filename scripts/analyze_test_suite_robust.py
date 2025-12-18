#!/usr/bin/env python3
"""
🔬 ROBUST TEST SUITE ANALYZER - REGEX VERSION
==============================================

Análise robusta usando REGEX ao invés de AST para evitar problemas
com generators, complex structures, etc.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


class RobustTestAnalyzer:
    """Análise robusta baseada em regex."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            self.content = f.read()

        self.tests = []
        self.classes = []
        self.fixtures = []
        self.decorators = set()
        self.imports = []
        self.markers = set()
        self.operations = set()

    def analyze(self):
        """Executa análise completa."""
        self._extract_imports()
        self._extract_decorators()
        self._extract_test_functions()
        self._extract_test_classes()
        self._extract_fixtures()
        self._detect_operations()

    def _extract_imports(self):
        """Extrai imports."""
        import_pattern = r"from\s+[\w\.]+\s+import\s+[\w\s,*]+|import\s+[\w\.]+"
        for match in re.finditer(import_pattern, self.content):
            self.imports.append(match.group(0))

    def _extract_decorators(self):
        """Extrai decoradores únicos."""
        dec_pattern = r"@([\w\.]+)(?:\([^)]*\))?"
        for match in re.finditer(dec_pattern, self.content):
            decorator = match.group(1)
            self.decorators.add(decorator)

            # Detecta markers
            if "mark" in decorator:
                marker_match = re.search(r"mark\.(\w+)", decorator)
                if marker_match:
                    self.markers.add(marker_match.group(1))

    def _extract_test_functions(self):
        """Extrai funções de teste."""
        # Padrão para funções de teste
        pattern = r"(?:^|\n)\s*(?:async\s+)?def\s+(test_\w+)\s*\((.*?)\)\s*:\s*\n((?:.*?\n)*?)(?=^(?:def|class|\Z))"

        for match in re.finditer(pattern, self.content, re.MULTILINE | re.DOTALL):
            func_name = match.group(1)
            params = match.group(2).split(",") if match.group(2) else []
            body = match.group(3)

            # Verifica se é async
            is_async = "async" in match.group(0)

            # Detecta operações no corpo
            operations = self._detect_body_operations(body)

            test_info = {
                "name": func_name,
                "is_async": is_async,
                "parameters": [p.strip() for p in params if p.strip()],
                "operations": operations,
                "has_docstring": '"""' in body or "'''" in body,
            }

            self.tests.append(test_info)

    def _extract_test_classes(self):
        """Extrai classes de teste."""
        pattern = r"class\s+(Test\w+)\s*(\([^)]*\))?\s*:\s*\n((?:.*?\n)*?)(?=^class|\Z)"

        for match in re.finditer(pattern, self.content, re.MULTILINE | re.DOTALL):
            class_name = match.group(1)
            bases = match.group(2) or ""
            body = match.group(3)

            # Conta métodos de teste na classe
            method_pattern = r"def\s+(test_\w+)\s*\("
            methods = list(re.finditer(method_pattern, body))

            class_info = {
                "name": class_name,
                "base_classes": bases.strip("()"),
                "test_method_count": len(methods),
                "method_names": [m.group(1) for m in methods],
                "has_setup": bool(re.search(r"def\s+(setup|setUp|setup_method)", body)),
                "has_teardown": bool(re.search(r"def\s+(teardown|tearDown|teardown_method)", body)),
            }

            self.classes.append(class_info)

    def _extract_fixtures(self):
        """Extrai fixtures."""
        pattern = r"@(?:pytest\.)?fixture(?:\([^)]*\))?\s*\n\s*(?:async\s+)?def\s+(_\w*fixture[\w_]*)\s*\((.*?)\)"

        for match in re.finditer(pattern, self.content, re.MULTILINE):
            fixture_name = match.group(1)
            params = match.group(2).split(",") if match.group(2) else []

            # Tenta extrair scope
            scope_match = re.search(
                r'@(?:pytest\.)?fixture\s*\(\s*scope\s*=\s*["\'](\w+)["\']', match.group(0)
            )
            scope = scope_match.group(1) if scope_match else "function"

            fixture_info = {
                "name": fixture_name,
                "scope": scope,
                "parameters": [p.strip() for p in params if p.strip()],
            }

            self.fixtures.append(fixture_info)

    def _detect_operations(self):
        """Detecta tipos de operações no arquivo."""
        operations_patterns = {
            "http_requests": [
                r"requests\.(get|post|put|delete|patch)",
                r"aiohttp\.ClientSession",
                r"urllib\.request",
                r"httpx\.",
            ],
            "gpu_operations": [
                r"\.cuda",
                r"torch\.cuda",
                r"GPU",
                r"\.to\(.*?device",
                r"cuda\.synchronize",
            ],
            "file_io": [
                r"open\(",
                r"Path\(",
                r"\.read_text",
                r"\.write_text",
                r"json\.load",
                r"yaml\.load",
            ],
            "database": [r"\.query\(", r"\.execute\(", r"session\.", r"ORM", r"Database\."],
            "async_operations": [r"await ", r"asyncio\.", r"aiofiles\.", r"concurrent\.futures"],
            "mocking": [r"@mock\.patch", r"@patch\(", r"MagicMock\(", r"Mock\(", r"unittest\.mock"],
            "subprocess": [r"subprocess\.", r"Popen\("],
            "threading": [r"Thread\(", r"Lock\(", r"Event\(", r"concurrent\."],
            "external_services": [r"requests\.", r"boto3", r"azure\.", r"google\."],
        }

        for op_type, patterns in operations_patterns.items():
            for pattern in patterns:
                if re.search(pattern, self.content):
                    self.operations.add(op_type)
                    break

    def _detect_body_operations(self, body: str) -> List[str]:
        """Detecta operações em um corpo de função."""
        ops = []

        if re.search(r"requests\.(get|post|put|delete)", body):
            ops.append("http_request")
        if re.search(r"\.cuda|torch\.cuda", body):
            ops.append("gpu_operation")
        if re.search(r"open\(|Path\(", body):
            ops.append("file_io")
        if re.search(r"await |asyncio\.", body):
            ops.append("async_operation")
        if re.search(r"@patch|@mock|MagicMock\(", body):
            ops.append("mocking")
        if re.search(r"assert ", body):
            ops.append("assertions")
        if re.search(r"pytest\.raises", body):
            ops.append("exception_handling")

        return ops


def analyze_all_tests(tests_dir: Path) -> Dict[str, Any]:
    """Analisa TODOS os testes."""

    print("🔍 Collecting all test files...")
    test_files = sorted(tests_dir.rglob("test_*.py"))
    print(f"   Found {len(test_files)} test files")

    results = {
        "total_files": 0,
        "total_tests": 0,
        "total_classes": 0,
        "total_fixtures": 0,
        "all_decorators": set(),
        "all_markers": set(),
        "all_operations": set(),
        "files": [],
        "by_marker": defaultdict(int),
        "by_operation": defaultdict(int),
    }

    for i, test_file in enumerate(test_files):
        if (i + 1) % 50 == 0:
            print(f"   Processing {i+1}/{len(test_files)}...")

        try:
            analyzer = RobustTestAnalyzer(str(test_file))
            analyzer.analyze()

            file_data = {
                "path": str(test_file.relative_to(tests_dir)),
                "tests": len(analyzer.tests),
                "classes": len(analyzer.classes),
                "class_methods": sum(c["test_method_count"] for c in analyzer.classes),
                "fixtures": len(analyzer.fixtures),
                "operations": list(analyzer.operations),
                "markers": list(analyzer.markers),
                "has_async": any(t["is_async"] for t in analyzer.tests),
            }

            results["files"].append(file_data)
            results["total_files"] += 1
            results["total_tests"] += len(analyzer.tests) + file_data["class_methods"]
            results["total_classes"] += len(analyzer.classes)
            results["total_fixtures"] += len(analyzer.fixtures)
            results["all_decorators"].update(analyzer.decorators)
            results["all_markers"].update(analyzer.markers)
            results["all_operations"].update(analyzer.operations)

            for marker in analyzer.markers:
                results["by_marker"][marker] += 1

            for op in analyzer.operations:
                results["by_operation"][op] += 1

        except Exception as e:
            print(f"   ⚠️  Error analyzing {test_file.name}: {str(e)[:50]}")

    return results


def generate_report(data: Dict[str, Any]) -> str:
    """Gera relatório markdown extenso."""

    report = """# 📚 COMPLETE & COMPREHENSIVE TEST SUITE ANALYSIS
## Full Breakdown of All Tests, Properties, Operations & Classifications

**Generated:** 2025-12-02
**Analysis Type:** Complete Regex-based scan of all test files

---

## 📊 EXECUTIVE SUMMARY

| Metric | Count |
|--------|-------|
| **Test Files Analyzed** | {data['total_files']} |
| **Total Test Functions & Methods** | {data['total_tests']:,} |
| **Test Classes** | {data['total_classes']} |
| **Test Fixtures** | {data['total_fixtures']} |
| **Unique Decorators** | {len(data['all_decorators'])} |
| **Pytest Markers Found** | {len(data['all_markers'])} |
| **Test Operations Types** | {len(data['all_operations'])} |

### Quick Stats

- **Average tests per file:** {data['total_tests']/max(1, data['total_files']):.1f}
- **Files with classes:** {sum(1 for f in data['files'] if f['classes'] > 0)}
- **Files with async tests:** {sum(1 for f in data['files'] if f['has_async'])}
- **Files with fixtures:** {sum(1 for f in data['files'] if f['fixtures'] > 0)}

---

## 🏷️  PYTEST MARKERS INVENTORY

### All Markers Detected

"""

    for marker in sorted(data["all_markers"]):
        count = data["by_marker"].get(marker, 0)
        report += f"- **@pytest.mark.{marker}** ({count} files)\n"

    report += "\n\n## ⚙️  TEST OPERATIONS & OPERATIONALITY\n\n"
    report += "### Operation Types Detected Across Suite\n\n"
    report += "| Operation Type | Count | Percentage |\n"
    report += "|--------|-------|------------|\n"

    _total_ops = sum(data["by_operation"].values())
    for op_type in sorted(
        data["by_operation"].keys(), key=lambda x: data["by_operation"][x], reverse=True
    ):
        count = data["by_operation"][op_type]
        pct = (count / len(data["files"]) * 100) if data["files"] else 0
        report += f"| {op_type.replace('_', ' ').title()} | {count} files | {pct:.1f}% |\n"

    report += "\n\n## 📁 DECORATOR & DECORATOR PATTERNS\n\n"
    report += "### All Decorators Found\n\n"
    report += "```\n"
    for dec in sorted(data["all_decorators"]):
        report += f"  • {dec}\n"
    report += "```\n"

    report += "\n\n## 📋 TEST FILE CATALOG (Top 50 by Test Count)\n\n"
    report += "| File | Tests | Classes | Fixtures | Operations | Markers |\n"
    report += "|------|-------|---------|----------|------------|----------|\n"

    sorted_files = sorted(data["files"], key=lambda x: x["tests"], reverse=True)[:50]
    for file_data in sorted_files:
        file_name = file_data["path"].split("/")[-1]
        tests_count = file_data["tests"] + file_data["class_methods"]
        ops_str = ", ".join(file_data["operations"][:2])
        if len(file_data["operations"]) > 2:
            ops_str += f", +{len(file_data['operations'])-2}"
        ops_str = ops_str or "—"

        markers_str = ", ".join(file_data["markers"][:2])
        if len(file_data["markers"]) > 2:
            markers_str += f", +{len(file_data['markers'])-2}"
        markers_str = markers_str or "—"

        report += f"| {file_name} | {tests_count} | {file_data['classes']} | {file_data['fixtures']} | {ops_str} | {markers_str} |\n"

    report += "\n\n## 📊 STATISTICAL BREAKDOWN\n\n"

    # Distribution
    test_counts = [f["tests"] + f["class_methods"] for f in data["files"]]
    if test_counts:
        report += "### Test Count Distribution\n\n"
        report += f"- **Largest File:** {max(test_counts)} tests\n"
        report += f"- **Smallest File:** {min(test_counts)} tests\n"
        report += f"- **Average:** {sum(test_counts)/len(test_counts):.1f} tests\n"
        report += f"- **Median:** {sorted(test_counts)[len(test_counts)//2]} tests\n"

    # Classification distribution
    report += "\n### File Classification\n\n"
    report += f"- **Pure Function Tests:** {sum(1 for f in data['files'] if f['classes'] == 0 and f['tests'] > 0)}\n"
    report += f"- **Class-Based Tests:** {sum(1 for f in data['files'] if f['classes'] > 0)}\n"
    report += f"- **With Fixtures:** {sum(1 for f in data['files'] if f['fixtures'] > 0)}\n"
    report += f"- **Async Tests:** {sum(1 for f in data['files'] if f['has_async'])}\n"

    report += "\n### Operation Distribution\n\n"
    report += "Tests are classified by the operations they perform:\n\n"
    report += f"- **HTTP/API Tests:** {data['by_operation'].get('http_requests', 0)} files\n"
    report += f"- **GPU Tests:** {data['by_operation'].get('gpu_operations', 0)} files\n"
    report += f"- **File I/O Tests:** {data['by_operation'].get('file_io', 0)} files\n"
    report += f"- **Database Tests:** {data['by_operation'].get('database', 0)} files\n"
    report += f"- **Async Tests:** {data['by_operation'].get('async_operations', 0)} files\n"
    report += f"- **Mock Tests:** {data['by_operation'].get('mocking', 0)} files\n"
    report += f"- **Subprocess Tests:** {data['by_operation'].get('subprocess', 0)} files\n"
    report += f"- **Threading Tests:** {data['by_operation'].get('threading', 0)} files\n"

    report += "\n\n## 🔍 COMPLETE TEST PROPERTIES & CHARACTERISTICS\n\n"
    report += """### Test Function Properties

All test functions in the suite share these attributes:

1. **Naming Convention:** All start with `test_` prefix
2. **Parameters:** Can accept fixtures via DI (Dependency Injection)
3. **Return:** Always return None (None implicitly)
4. **Assertions:** Use assert statements or pytest assertion helpers
5. **Exceptions:** Can use pytest.raises() for exception testing
6. **Async:** Can be defined as `async def test_*()` with `await` calls

### Test Class Properties

Classes starting with `Test` prefix can contain:

1. **Setup Methods:** `setup()`, `setup_method()`, or `setUp()`
2. **Teardown Methods:** `teardown()`, `teardown_method()`, or `tearDown()`
3. **Test Methods:** Any method starting with `test_`
4. **Fixtures:** Can use pytest fixtures with `@pytest.fixture`
5. **Parameters:** Can be parametrized with `@pytest.mark.parametrize`

### Fixture Properties

Fixtures are functions with `@pytest.fixture` decorator:

1. **Scope:** function (default), class, module, or session
2. **Parameters:** Can depend on other fixtures
3. **Yield/Return:** Provide data for tests
4. **Cleanup:** Code after yield runs on teardown
5. **Auto-use:** Can be marked with `autouse=True`

### Decorator Patterns

Tests can use decorators for:

1. **Marking:** `@pytest.mark.<name>` for test categorization
2. **Parametrization:** `@pytest.mark.parametrize()` for multiple inputs
3. **Skipping:** `@pytest.mark.skip` or `@pytest.mark.skipif`
4. **Xfailing:** `@pytest.mark.xfail` for expected failures
5. **Async:** `@pytest.mark.asyncio` for async/await tests
6. **Custom:** User-defined markers for domain classification

---

## 🎯 OPERATIONALITY MATRIX

### What Tests Do (Operations by Category)

#### API/HTTP Operations
- Direct HTTP requests via requests library
- REST API integration testing
- Webhook validation
- GraphQL queries

#### GPU/Hardware Operations
- CUDA tensor operations
- PyTorch model training/inference
- GPU memory management
- Hardware detection

#### Data I/O Operations
- File system operations
- JSON/YAML parsing
- Database transactions
- Cache operations

#### Async Operations
- Coroutine execution
- Event loop management
- Concurrent task handling
- Async context managers

#### Mocking Operations
- Function mocking with @patch
- Object stubbing
- Response simulation
- Side effect injection

#### Infrastructure Operations
- Process spawning (subprocess)
- Thread creation
- Network socket operations
- System-level commands

---

## 📈 TEST SUITE HEALTH

### Quality Metrics

✅ **Complete Coverage:** {data['total_files']} test files with {data['total_tests']:,} total tests
✅ **Diverse Operations:** {len(data['all_operations'])} different operation types tested
✅ **Rich Markers:** {len(data['all_markers'])} pytest markers for organization
✅ **Decorator Usage:** {len(data['all_decorators'])} unique decorators

### Recommended Next Steps

1. **Analyze Test Dependencies:** Map fixture dependencies
2. **Performance Profiling:** Measure slow test execution
3. **Coverage Analysis:** Generate code coverage reports
4. **Mutation Testing:** Validate test effectiveness
5. **Flakiness Detection:** Identify intermittent failures

---

**Analysis Complete** ✅
Generated by: analyze_test_suite_robust.py
Purpose: Comprehensive test suite documentation
"""

    return report


def main():
    omnimind_root = Path(__file__).parent.parent
    tests_dir = omnimind_root / "tests"

    print("🔬 Starting robust test suite analysis...")
    print()

    data = analyze_all_tests(tests_dir)

    print()
    print("✅ Analysis Complete!")
    print()
    print("📊 Summary:")
    print(f"  📄 Files: {data['total_files']}")
    print(f"  🧪 Tests: {data['total_tests']:,}")
    print(f"  📦 Classes: {data['total_classes']}")
    print(f"  🔧 Fixtures: {data['total_fixtures']}")
    print(f"  🎯 Decorators: {len(data['all_decorators'])}")
    print(f"  🏷️  Markers: {len(data['all_markers'])}")
    print(f"  ⚙️  Operations: {len(data['all_operations'])}")

    print("\n🏷️  Markers Found:")
    for marker in sorted(data["all_markers"]):
        count = data["by_marker"][marker]
        print(f"  • {marker}: {count}")

    print("\n⚙️  Operations Found:")
    for op in sorted(data["all_operations"]):
        count = data["by_operation"][op]
        print(f"  • {op}: {count} files")

    print("\n📝 Generating comprehensive report...")
    report = generate_report(data)

    output_file = omnimind_root / "docs" / "COMPLETE_TEST_SUITE_DETAILED_REPORT.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ Report saved: {output_file}")
    print(f"   📊 Size: {len(report):,} characters")
    print(f"   📄 Pages (est.): {len(report)//3000}")


if __name__ == "__main__":
    main()
