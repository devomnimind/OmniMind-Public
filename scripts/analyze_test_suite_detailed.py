#!/usr/bin/env python3
"""
🔬 ADVANCED TEST SUITE ANALYZER
================================

Análise profunda de ALL test properties, decorators, classes, functions,
fixtures, operationality patterns, and complete categorization.

Gera: COMPLETE_TEST_SUITE_DETAILED_REPORT.md (Documento Extenso)
"""

import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


class DetailedTestAnalyzer(ast.NodeVisitor):
    """Análise profunda de propriedades de teste."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.rel_path = None
        self.modules_info = {
            "imports": set(),
            "from_imports": defaultdict(set),
        }
        self.tests_info = []
        self.classes_info = []
        self.fixtures_info = []
        self.all_decorators = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.modules_info["imports"].add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or "builtins"
        for alias in node.names:
            self.modules_info["from_imports"][module].add(alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        decorators = self._extract_decorators(node.decorator_list)

        class_info = {
            "name": node.name,
            "line": node.lineno,
            "decorators": decorators,
            "bases": [self._get_name(b) for b in node.bases],
            "docstring": ast.get_docstring(node),
            "methods": [],
            "properties": {
                "has_setup": False,
                "has_teardown": False,
                "has_fixtures": False,
                "is_parameterized": False,
            },
        }

        # Processa métodos
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith("test_"):
                    method = self._process_test_method(item)
                    class_info["methods"].append(method)
                elif item.name in ["setup", "setup_method", "setUp"]:
                    class_info["properties"]["has_setup"] = True
                elif item.name in ["teardown", "teardown_method", "tearDown"]:
                    class_info["properties"]["has_teardown"] = True
                elif item.name.startswith("_") and item.name.endswith("fixture"):
                    class_info["properties"]["has_fixtures"] = True

        # Verifica parametrização
        for dec in decorators:
            if "parametrize" in dec.get("full", ""):
                class_info["properties"]["is_parameterized"] = True

        self.classes_info.append(class_info)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            test_info = self._process_test_method(node)
            self.tests_info.append(test_info)
        elif any(
            d.get("name") in ["fixture", "pytest.fixture"]
            for d in self._extract_decorators(node.decorator_list)
        ):
            fixture_info = self._process_fixture(node)
            self.fixtures_info.append(fixture_info)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if node.name.startswith("test_"):
            test_info = self._process_test_method(node, is_async=True)
            self.tests_info.append(test_info)
        self.generic_visit(node)

    def _process_test_method(self, node, is_async=False):
        decorators = self._extract_decorators(node.decorator_list)

        # Detecta operações no corpo do teste
        operations = self._detect_operations(node.body)

        # Detecta parametrização
        is_parametrized = any("parametrize" in d.get("full", "") for d in decorators)

        # Extrai informações de parâmetros
        params = [arg.arg for arg in node.args.args]

        return {
            "name": node.name,
            "line": node.lineno,
            "is_async": is_async,
            "decorators": decorators,
            "docstring": ast.get_docstring(node),
            "parameters": params,
            "body_complexity": len(node.body),
            "operations": operations,
            "is_parametrized": is_parametrized,
            "markers": self._extract_markers(decorators),
            "type": self._classify_test(decorators, operations, params),
        }

    def _process_fixture(self, node):
        decorators = self._extract_decorators(node.decorator_list)

        # Extrai scope
        scope = "function"  # default
        for dec in decorators:
            if "scope" in str(dec):
                match = re.search(r"scope\s*=\s*['\"](\w+)['\"]", dec.get("full", ""))
                if match:
                    scope = match.group(1)

        params = [arg.arg for arg in node.args.args]

        return {
            "name": node.name,
            "line": node.lineno,
            "scope": scope,
            "docstring": ast.get_docstring(node),
            "parameters": params,
            "operations": self._detect_operations(node.body),
        }

    def _extract_decorators(self, decorator_list) -> List[Dict]:
        decorators = []
        for dec in decorator_list:
            dec_info = {
                "full": ast.unparse(dec),
                "name": None,
                "args": [],
                "kwargs": {},
            }

            if isinstance(dec, ast.Name):
                dec_info["name"] = dec.id
            elif isinstance(dec, ast.Attribute):
                dec_info["name"] = dec.attr
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    dec_info["name"] = dec.func.id
                elif isinstance(dec.func, ast.Attribute):
                    dec_info["name"] = dec.func.attr

                dec_info["args"] = [ast.unparse(arg) for arg in dec.args]
                dec_info["kwargs"] = {kw.arg: ast.unparse(kw.value) for kw in dec.keywords}

            decorators.append(dec_info)
            self.all_decorators.add(dec_info["name"])

        return decorators

    def _detect_operations(self, body) -> List[str]:
        """Detecta tipos de operações no corpo da função."""
        operations = []
        code = ast.unparse(node for node in body)

        patterns = {
            "http_request": r"requests\.|\.get\(|\.post\(|\.put\(|\.delete\(",
            "gpu_operation": r"\.cuda|torch\.cuda|\.to\(.*device|GPU",
            "file_io": r"open\(|Path\(|with open|\.read|\.write",
            "database": r"session\.|query\(|\.execute\(|\.add\(|ORM",
            "async_await": r"await |asyncio\.",
            "mock_patch": r"@patch|Mock\(|MagicMock\(|patch\(",
            "assert": r"assert |\.assert_",
            "exception": r"pytest\.raises|except ",
            "threading": r"Thread\(|Lock\(|Event\(",
            "subprocess": r"subprocess\.|Popen\(",
        }

        for op_type, pattern in patterns.items():
            if re.search(pattern, code):
                operations.append(op_type)

        return operations

    def _extract_markers(self, decorators) -> List[str]:
        """Extrai pytest markers."""
        markers = []
        for dec in decorators:
            if dec["name"] == "mark":
                if dec.get("args"):
                    markers.extend(dec["args"])
            # Forma alternativa: @pytest.mark.xxx
            full = dec.get("full", "")
            if "@pytest.mark." in full or "@mark." in full:
                match = re.search(r"@(?:pytest\.)?mark\.(\w+)", full)
                if match:
                    markers.append(match.group(1))
        return list(set(markers))

    def _classify_test(self, decorators, operations, params) -> str:
        """Classifica o tipo de teste."""
        markers = self._extract_markers(decorators)

        if "chaos" in markers:
            return "chaos_engineering"
        if "gpu" in markers:
            return "gpu_intensive"
        if "real" in markers:
            return "real_integration"
        if "mock" in markers:
            return "mocked_unit"
        if "parametrize" in str(decorators):
            return "parametrized"
        if "http_request" in operations or "database" in operations:
            return "integration"
        if "mock_patch" in operations:
            return "unit_with_mocks"
        if "gpu_operation" in operations:
            return "gpu_required"

        return "unit_test"

    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return ast.unparse(node)
        return "Unknown"


def analyze_all_tests(tests_dir: Path) -> Dict[str, Any]:
    """Analisa TODOS os testes."""
    all_data = {
        "total_files": 0,
        "total_tests": 0,
        "total_classes": 0,
        "total_fixtures": 0,
        "files": [],
        "all_decorators": set(),
        "all_markers": set(),
        "by_classification": defaultdict(list),
        "by_marker": defaultdict(list),
        "by_operation": defaultdict(list),
        "fixtures_by_scope": defaultdict(list),
    }

    for test_file in sorted(tests_dir.rglob("test_*.py")):
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            analyzer = DetailedTestAnalyzer(str(test_file))
            analyzer.visit(tree)

            file_data = {
                "path": str(test_file.relative_to(tests_dir)),
                "absolute_path": str(test_file),
                "tests": analyzer.tests_info,
                "classes": analyzer.classes_info,
                "fixtures": analyzer.fixtures_info,
                "imports": {
                    "direct": sorted(list(analyzer.modules_info["imports"])),
                    "from_imports": {
                        k: sorted(list(v)) for k, v in analyzer.modules_info["from_imports"].items()
                    },
                },
                "total_tests": len(analyzer.tests_info)
                + sum(len(c["methods"]) for c in analyzer.classes_info),
                "total_classes": len(analyzer.classes_info),
                "total_fixtures": len(analyzer.fixtures_info),
            }

            all_data["files"].append(file_data)
            all_data["total_files"] += 1
            all_data["total_tests"] += file_data["total_tests"]
            all_data["total_classes"] += len(analyzer.classes_info)
            all_data["total_fixtures"] += len(analyzer.fixtures_info)
            all_data["all_decorators"].update(analyzer.all_decorators)

            # Processa testes
            for test in analyzer.tests_info:
                all_data["by_classification"][test["type"]].append((str(test_file), test["name"]))
                all_data["by_marker"]["|".join(test["markers"])].append(
                    (str(test_file), test["name"])
                )
                for op in test["operations"]:
                    all_data["by_operation"][op].append((str(test_file), test["name"]))

            # Processa fixtures
            for fixture in analyzer.fixtures_info:
                all_data["fixtures_by_scope"][fixture["scope"]].append(fixture["name"])

        except Exception as e:
            print(f"❌ Erro analisando {test_file}: {e}")

    return all_data


def generate_detailed_report(data: Dict[str, Any]) -> str:
    """Gera relatório extremamente detalhado."""

    report = f"""# 📚 COMPLETE DETAILED TEST SUITE ANALYSIS
## Comprehensive & Extensible Documentation

**Analysis Date:** 2025-12-02
**Total Files:** {data['total_files']}
**Total Test Functions:** {data['total_tests']}
**Total Test Classes:** {data['total_classes']}
**Total Fixtures:** {data['total_fixtures']}

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Test Classifications](#test-classifications)
3. [Decorator & Marker Inventory](#decorator--marker-inventory)
4. [Operations Detected](#operations-detected)
5. [Test Infrastructure (Fixtures)](#test-infrastructure-fixtures)
6. [Detailed File-by-File Catalog](#detailed-file-by-file-catalog)
7. [Statistical Analysis](#statistical-analysis)

---

## Executive Summary

### Key Statistics

| Metric | Count |
|--------|-------|
| **Test Files** | {data['total_files']} |
| **Test Functions** | {data['total_tests']} |
| **Test Classes** | {data['total_classes']} |
| **Fixtures** | {data['total_fixtures']} |
| **Average Tests/File** | {data['total_tests']/max(1,data['total_files']):.1f} |
| **Unique Decorators** | {len(data['all_decorators'])} |

### Classification Distribution

"""

    # Classification distribution
    report += "| Type | Count | Percentage |\n"
    report += "|------|-------|------------|\n"
    total = sum(len(v) for v in data["by_classification"].values())

    for classification in sorted(
        data["by_classification"].keys(),
        key=lambda x: len(data["by_classification"][x]),
        reverse=True,
    ):
        count = len(data["by_classification"][classification])
        pct = (count / total * 100) if total > 0 else 0
        report += f"| {classification} | {count} | {pct:.1f}% |\n"

    report += f"\n**Total Classified Tests:** {total}\n"

    # Test Classifications Section
    report += "\n\n## Test Classifications\n\n"
    report += "### Breakdown by Test Type\n\n"

    for test_type in sorted(data["by_classification"].keys()):
        tests = data["by_classification"][test_type]
        report += f"\n### {test_type.replace('_', ' ').title()} ({len(tests)} tests)\n\n"
        report += "| Test Name | File |\n"
        report += "|-----------|------|\n"

        for filepath, test_name in sorted(tests)[:10]:
            file_short = filepath.split("/")[-1] if "/" in filepath else filepath
            report += f"| `{test_name}` | {file_short} |\n"

        if len(tests) > 10:
            report += f"| ... | ... (+{len(tests)-10} more) |\n"

    # Decorators & Markers
    report += "\n\n## Decorator & Marker Inventory\n\n"
    report += f"### All Unique Decorators Used ({len(data['all_decorators'])})\n\n"
    report += "```\n"
    for dec in sorted(data["all_decorators"]):
        report += f"  • {dec}\n"
    report += "```\n"

    report += "\n### Marker Distribution\n\n"
    report += "| Marker Combination | Count |\n"
    report += "|-------------------|-------|\n"

    for marker_combo in sorted(
        data["by_marker"].keys(), key=lambda x: len(data["by_marker"][x]), reverse=True
    )[:20]:
        count = len(data["by_marker"][marker_combo])
        display = marker_combo if marker_combo else "(no markers)"
        report += f"| {display} | {count} |\n"

    # Operations
    report += "\n\n## Operations Detected\n\n"
    report += "### Test Operationality Matrix\n\n"
    report += "| Operation Type | Test Count | Percentage |\n"
    report += "|--------|-------|------------|\n"

    total_ops = sum(len(v) for v in data["by_operation"].values())
    for op_type in sorted(
        data["by_operation"].keys(), key=lambda x: len(data["by_operation"][x]), reverse=True
    ):
        count = len(data["by_operation"][op_type])
        pct = (count / total_ops * 100) if total_ops > 0 else 0
        report += f"| {op_type} | {count} | {pct:.1f}% |\n"

    # Fixtures
    report += "\n\n## Test Infrastructure (Fixtures)\n\n"
    report += "### Fixtures by Scope\n\n"

    _total_fixtures = sum(len(v) for v in data["fixtures_by_scope"].values())
    for scope in ["function", "class", "module", "session"]:
        if scope in data["fixtures_by_scope"]:
            fixtures = data["fixtures_by_scope"][scope]
            report += f"\n#### {scope.upper()} Scope ({len(fixtures)} fixtures)\n\n"
            report += "```\n"
            for fixture in sorted(fixtures)[:10]:
                report += f"  • {fixture}\n"
            if len(fixtures) > 10:
                report += f"  ... and {len(fixtures)-10} more fixtures\n"
            report += "```\n"

    # Detailed Catalog
    report += "\n\n## Detailed File-by-File Catalog\n\n"

    for file_data in sorted(data["files"], key=lambda x: x["total_tests"], reverse=True)[:50]:
        report += f"\n### {file_data['path']}\n\n"
        report += f"**Stats:** {file_data['total_tests']} tests | "
        report += f"{file_data['total_classes']} classes | "
        report += f"{file_data['total_fixtures']} fixtures\n\n"

        # Tests diretos
        if file_data["tests"]:
            report += f"#### Test Functions ({len(file_data['tests'])})\n\n"
            for test in file_data["tests"][:5]:
                markers_str = f"[{', '.join(test['markers'])}]" if test["markers"] else ""
                async_mark = "⚡" if test["is_async"] else ""
                report += f"- **`{test['name']}`** {async_mark} {markers_str}\n"
            if len(file_data["tests"]) > 5:
                report += f"- ... and {len(file_data['tests'])-5} more\n"

        # Classes
        if file_data["classes"]:
            report += f"\n#### Test Classes ({len(file_data['classes'])})\n\n"
            for cls in file_data["classes"][:3]:
                report += f"- **`{cls['name']}`** ({len(cls['methods'])} methods)\n"
            if len(file_data["classes"]) > 3:
                report += f"- ... and {len(file_data['classes'])-3} more classes\n"

        # Imports
        if file_data["imports"]["direct"]:
            report += f"\n#### Dependencies\n\n"
            report += "**Direct Imports:** "
            report += ", ".join(file_data["imports"]["direct"][:5])
            if len(file_data["imports"]["direct"]) > 5:
                report += f", +{len(file_data['imports']['direct'])-5} more"
            report += "\n\n"

    # Statistical Analysis
    report += "\n\n## Statistical Analysis\n\n"

    test_sizes = [f["total_tests"] for f in data["files"]]
    if test_sizes:
        report += f"### Test File Size Distribution\n\n"
        report += f"- **Largest File:** {max(test_sizes)} tests\n"
        report += f"- **Smallest File:** {min(test_sizes)} tests\n"
        report += f"- **Average:** {sum(test_sizes)/len(test_sizes):.1f} tests\n"
        report += f"- **Median:** {sorted(test_sizes)[len(test_sizes)//2]} tests\n"

    report += "\n\n---\n"
    report += "**Generated by:** analyze_test_suite_detailed.py  \n"
    report += "**Purpose:** Complete documentation of test suite structure, properties, and operationality  \n"

    return report


def main():
    omnimind_root = Path(__file__).parent.parent
    tests_dir = omnimind_root / "tests"

    print("🔬 Iniciando análise profunda...")
    print(f"  📁 Diretório: {tests_dir}")

    data = analyze_all_tests(tests_dir)

    print(f"\n✅ Análise Completa:")
    print(f"  📄 {data['total_files']} arquivos de teste")
    print(f"  🧪 {data['total_tests']} funções de teste")
    print(f"  📦 {data['total_classes']} classes de teste")
    print(f"  🔧 {data['total_fixtures']} fixtures")
    print(f"  🎯 {len(data['all_decorators'])} decoradores únicos")

    print(f"\n📊 Classificações encontradas:")
    for classification in sorted(data["by_classification"].keys()):
        count = len(data["by_classification"][classification])
        print(f"  • {classification}: {count}")

    print(f"\n⚙️  Operações encontradas:")
    for op_type in sorted(data["by_operation"].keys()):
        count = len(data["by_operation"][op_type])
        print(f"  • {op_type}: {count}")

    print("\n📝 Gerando relatório detalhado...")
    report = generate_detailed_report(data)

    output_file = omnimind_root / "docs" / "COMPLETE_TEST_SUITE_DETAILED_REPORT.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ Relatório salvo: {output_file}")
    print(f"   📊 Tamanho: {len(report):,} caracteres")


if __name__ == "__main__":
    main()
