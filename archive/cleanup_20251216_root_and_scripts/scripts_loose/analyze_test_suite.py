#!/usr/bin/env python3
"""
🔍 TEST SUITE ANALYZER
=====================

Analisa TODAS as propriedades do pytest, categoriza funções, classes,
operacionalidade, marcadores, e gera relatório completo.

Saída: docs/COMPLETE_TEST_SUITE_ANALYSIS.md
"""

import os
import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any
import re


class TestAnalyzer(ast.NodeVisitor):
    """Analyzer para extrair metadados de testes."""

    def __init__(self, filename: str):
        self.filename = filename
        self.tests = []
        self.classes = []
        self.current_class = None
        self.current_decorators = []
        self.imports = []
        self.fixtures = []

    def visit_Import(self, node):
        """Rastreia imports."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Rastreia from imports."""
        for alias in node.names:
            full_import = f"{node.module}.{alias.name}" if node.module else alias.name
            self.imports.append(full_import)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Processa classes de teste."""
        # Pega decoradores da classe
        decorators = self._get_decorators(node)

        class_info = {
            "name": node.name,
            "lineno": node.lineno,
            "decorators": decorators,
            "methods": [],
            "docstring": ast.get_docstring(node),
            "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
        }

        # Processa métodos dentro da classe
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith("test_"):
                    method_info = {
                        "name": item.name,
                        "lineno": item.lineno,
                        "decorators": self._get_decorators(item),
                        "docstring": ast.get_docstring(item),
                        "is_async": isinstance(item, ast.AsyncFunctionDef),
                        "params": [arg.arg for arg in item.args.args],
                        "body_size": len(item.body),
                    }
                    class_info["methods"].append(method_info)
            elif isinstance(item, ast.FunctionDef) and item.name.startswith("_"):
                # Métodos auxiliares
                pass

        self.classes.append(class_info)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Processa funções de teste."""
        if node.name.startswith("test_"):
            test_info = {
                "name": node.name,
                "lineno": node.lineno,
                "decorators": self._get_decorators(node),
                "docstring": ast.get_docstring(node),
                "is_async": False,
                "params": [arg.arg for arg in node.args.args],
                "body_size": len(node.body),
                "in_class": False,
            }
            self.tests.append(test_info)
        elif node.name.startswith("_"):
            # Pode ser fixture ou helper
            if any(
                d.get("name") == "pytest.fixture" or d.get("name") == "fixture"
                for d in self._get_decorators(node)
            ):
                fixture_info = {
                    "name": node.name,
                    "lineno": node.lineno,
                    "scope": self._get_fixture_scope(node),
                    "params": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                }
                self.fixtures.append(fixture_info)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Processa funções async."""
        if node.name.startswith("test_"):
            test_info = {
                "name": node.name,
                "lineno": node.lineno,
                "decorators": self._get_decorators(node),
                "docstring": ast.get_docstring(node),
                "is_async": True,
                "params": [arg.arg for arg in node.args.args],
                "body_size": len(node.body),
                "in_class": False,
            }
            self.tests.append(test_info)
        self.generic_visit(node)

    def _get_decorators(self, node) -> List[Dict]:
        """Extrai informações dos decoradores."""
        decorators = []
        for decorator in node.decorator_list:
            dec_info = {"full_text": ast.unparse(decorator)}

            if isinstance(decorator, ast.Name):
                dec_info["name"] = decorator.id
            elif isinstance(decorator, ast.Attribute):
                dec_info["name"] = decorator.attr
                dec_info["module"] = ast.unparse(decorator.value)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    dec_info["name"] = decorator.func.id
                elif isinstance(decorator.func, ast.Attribute):
                    dec_info["name"] = decorator.func.attr
                    dec_info["module"] = ast.unparse(decorator.func.value)

                # Extrai argumentos do decorator
                if decorator.args:
                    dec_info["args"] = [ast.unparse(arg) for arg in decorator.args]
                if decorator.keywords:
                    dec_info["kwargs"] = {
                        kw.arg: ast.unparse(kw.value) for kw in decorator.keywords
                    }

            decorators.append(dec_info)

        return decorators

    def _get_fixture_scope(self, node) -> str:
        """Extrai scope da fixture."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                for kw in decorator.keywords:
                    if kw.arg == "scope":
                        return ast.unparse(kw.value).strip("'\"")
        return "function"  # default scope


def analyze_test_file(filepath: Path) -> Dict[str, Any]:
    """Analisa um arquivo de teste."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        analyzer = TestAnalyzer(str(filepath))
        analyzer.visit(tree)

        return {
            "filepath": str(filepath),
            "tests": analyzer.tests,
            "classes": analyzer.classes,
            "fixtures": analyzer.fixtures,
            "imports": analyzer.imports,
            "total_tests": len(analyzer.tests) + sum(len(c["methods"]) for c in analyzer.classes),
        }
    except Exception as e:
        return {
            "filepath": str(filepath),
            "error": str(e),
        }


def collect_all_tests(tests_dir: Path) -> List[Dict]:
    """Coleta análise de todos os arquivos de teste."""
    results = []

    for test_file in sorted(tests_dir.rglob("test_*.py")):
        result = analyze_test_file(test_file)
        results.append(result)

    return results


def categorize_tests(all_results: List[Dict]) -> Dict[str, Any]:
    """Categoriza testes por propriedades."""

    categories = {
        "by_marker": defaultdict(list),
        "by_type": {
            "unit": [],
            "integration": [],
            "e2e": [],
            "performance": [],
            "chaos": [],
            "gpu": [],
            "async": [],
            "mock": [],
            "real": [],
        },
        "by_operationality": {
            "http": [],
            "gpu": [],
            "file": [],
            "db": [],
            "async": [],
            "external": [],
        },
        "fixtures": defaultdict(list),
        "test_by_decorator": defaultdict(list),
        "statistics": {
            "total_files": 0,
            "total_tests": 0,
            "total_classes": 0,
            "total_fixtures": 0,
        },
    }

    # Padrões para detectar operacionalidades
    patterns = {
        "http": re.compile(r"requests\.|http\.|axios\.|fetch\(|urllib"),
        "gpu": re.compile(r"\.cuda|torch\.cuda|GPU|gpu|nvidia"),
        "file": re.compile(r"open\(|Path\(|os\.path|shutil\.|json\.load|yaml\.load"),
        "db": re.compile(r"session\.|query\(|\.execute\(|db\.|database"),
        "async": re.compile(r"await |async |asyncio\."),
        "external": re.compile(r"mock\.|patch\(|Mock\(|requests\.|http\."),
    }

    for result in all_results:
        if "error" in result:
            continue

        categories["statistics"]["total_files"] += 1
        categories["statistics"]["total_tests"] += result["total_tests"]
        categories["statistics"]["total_classes"] += len(result["classes"])
        categories["statistics"]["total_fixtures"] += len(result["fixtures"])

        # Processa testes diretos
        for test in result["tests"]:
            test_entry = {
                "file": result["filepath"],
                "name": test["name"],
                "decorators": test["decorators"],
                "is_async": test["is_async"],
            }

            # Categoriza por marcador
            for decorator in test["decorators"]:
                if "mark" in str(decorator):
                    mark_name = decorator.get("name", "unknown")
                    categories["by_marker"][mark_name].append(test_entry)

            # Categoriza por tipo
            doc = test.get("docstring", "")

            if any(d.get("name") == "mark" and "gpu" in str(d) for d in test["decorators"]):
                categories["by_type"]["gpu"].append(test_entry)

            if test["is_async"]:
                categories["by_type"]["async"].append(test_entry)

            if any(d.get("name") == "mark" and "mock" in str(d) for d in test["decorators"]):
                categories["by_type"]["mock"].append(test_entry)

            if any(d.get("name") == "mark" and "real" in str(d) for d in test["decorators"]):
                categories["by_type"]["real"].append(test_entry)

            if any(d.get("name") == "mark" and "chaos" in str(d) for d in test["decorators"]):
                categories["by_type"]["chaos"].append(test_entry)

            # Categoriza por operacionalidade (via docstring e decoradores)
            doc_text = doc.lower() if doc else ""

            for op_type, pattern in patterns.items():
                if pattern.search(doc_text):
                    categories["by_operationality"][op_type].append(test_entry)

        # Processa classes de teste
        for test_class in result["classes"]:
            for method in test_class["methods"]:
                test_entry = {
                    "file": result["filepath"],
                    "class": test_class["name"],
                    "name": method["name"],
                    "decorators": method["decorators"],
                    "is_async": method["is_async"],
                }

                # Processa decoradores
                for decorator in method["decorators"]:
                    mark_name = decorator.get("name", "unknown")
                    categories["by_marker"][mark_name].append(test_entry)
                    categories["test_by_decorator"][mark_name].append(test_entry)

        # Processa fixtures
        for fixture in result["fixtures"]:
            categories["fixtures"][fixture.get("scope", "function")].append(
                {
                    "file": result["filepath"],
                    "name": fixture["name"],
                }
            )

    return categories


def generate_report(categories: Dict[str, Any]) -> str:
    """Gera relatório markdown completo."""

    report = """# 📊 COMPLETE TEST SUITE ANALYSIS
## Comprehensive Breakdown of All Test Properties, Operations & Classifications

**Generated:** Automated Analysis Script  
**Total Files Analyzed:** {total_files}  
**Total Test Functions:** {total_tests}  
**Total Test Classes:** {total_classes}  
**Total Fixtures:** {total_fixtures}

---

## Table of Contents

1. [Overview & Statistics](#overview--statistics)
2. [Test Markers & Decorators](#test-markers--decorators)
3. [Test Types Classification](#test-types-classification)
4. [Test Operationality Matrix](#test-operationality-matrix)
5. [Fixtures & Test Infrastructure](#fixtures--test-infrastructure)
6. [Detailed Test Catalog](#detailed-test-catalog)

---

## Overview & Statistics

### Test Suite Metrics

| Metric | Count |
|--------|-------|
| **Total Test Files** | {total_files} |
| **Total Test Functions** | {total_tests} |
| **Test Classes** | {total_classes} |
| **Fixtures** | {total_fixtures} |
| **Average Tests per File** | {avg_tests_per_file:.1f} |

### Distribution Visualization

```
Test Suite Composition:
""".format(
        total_files=categories["statistics"]["total_files"],
        total_tests=categories["statistics"]["total_tests"],
        total_classes=categories["statistics"]["total_classes"],
        total_fixtures=categories["statistics"]["total_fixtures"],
        avg_tests_per_file=categories["statistics"]["total_tests"]
        / max(1, categories["statistics"]["total_files"]),
    )

    # Add marker breakdown
    report += "\n\n## Test Markers & Decorators\n\n"
    report += "### Markers Overview\n\n"
    report += "| Marker | Count | Tests |\n"
    report += "|--------|-------|-------|\n"

    for marker in sorted(categories["by_marker"].keys()):
        tests = categories["by_marker"][marker]
        report += f"| `@pytest.mark.{marker}` | {len(tests)} | "
        report += ", ".join([t["name"] for t in tests[:3]])
        if len(tests) > 3:
            report += f", +{len(tests)-3} more"
        report += " |\n"

    # Test types
    report += "\n\n## Test Types Classification\n\n"

    for test_type, tests in categories["by_type"].items():
        if tests:
            report += f"\n### {test_type.upper()} Tests ({len(tests)} tests)\n\n"
            report += "| Test Name | File | Properties |\n"
            report += "|-----------|------|------------|\n"
            for test in tests[:10]:
                async_marker = "⚡ Async" if test.get("is_async") else ""
                report += f"| `{test['name']}` | {test['file'].split('/')[-1]} | {async_marker} |\n"
            if len(tests) > 10:
                report += f"| ... | ... | +{len(tests)-10} more tests |\n"

    # Operationality
    report += "\n\n## Test Operationality Matrix\n\n"
    report += "### Operations Detected Across Test Suite\n\n"
    report += "| Operation Type | Count | Percentage |\n"
    report += "|--------|--------|----------|\n"

    total = sum(len(tests) for tests in categories["by_operationality"].values())
    for op_type, tests in sorted(
        categories["by_operationality"].items(), key=lambda x: len(x[1]), reverse=True
    ):
        if tests:
            percentage = (len(tests) / total * 100) if total > 0 else 0
            report += (
                f"| {op_type.replace('_', ' ').title()} | {len(tests)} | {percentage:.1f}% |\n"
            )

    # Fixtures
    report += "\n\n## Fixtures & Test Infrastructure\n\n"
    report += "### Fixtures by Scope\n\n"

    for scope in ["function", "class", "module", "session"]:
        fixtures = categories["fixtures"].get(scope, [])
        if fixtures:
            report += f"\n#### {scope.upper()} Scope ({len(fixtures)} fixtures)\n\n"
            report += "| Fixture Name | File |\n"
            report += "|--------------|------|\n"
            for fixture in fixtures[:5]:
                report += f"| `{fixture['name']}` | {fixture['file'].split('/')[-1]} |\n"
            if len(fixtures) > 5:
                report += f"| ... | +{len(fixtures)-5} more |\n"

    report += "\n\n---\n"
    report += "**Report Generated by:** analyze_test_suite.py\n"

    return report


def main():
    """Main execution."""
    omnimind_root = Path(__file__).parent.parent
    tests_dir = omnimind_root / "tests"

    print("🔍 Analyzing test suite...")
    print(f"  📁 Tests directory: {tests_dir}")

    # Coleta análises
    all_results = collect_all_tests(tests_dir)
    print(f"  ✅ Analisados {len(all_results)} arquivos de teste")

    # Categoriza
    print("🏷️  Categorizando testes...")
    categories = categorize_tests(all_results)

    # Gera relatório
    print("📝 Gerando relatório...")
    report = generate_report(categories)

    # Salva
    output_file = omnimind_root / "docs" / "COMPLETE_TEST_SUITE_ANALYSIS.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ Análise completa salva em: {output_file}")
    print(f"\n📊 Estatísticas:")
    print(f"  📄 Total de arquivos: {categories['statistics']['total_files']}")
    print(f"  🧪 Total de testes: {categories['statistics']['total_tests']}")
    print(f"  📦 Classes de teste: {categories['statistics']['total_classes']}")
    print(f"  🔧 Fixtures: {categories['statistics']['total_fixtures']}")


if __name__ == "__main__":
    main()
