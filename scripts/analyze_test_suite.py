#!/usr/bin/env python3
"""
Script de Diagnóstico Completo da Suíte de Testes OmniMind.

Este script analisa a suíte de testes para identificar:
- Testes definidos vs testes coletados vs testes executados
- Arquivos com erros de importação
- Módulos sem testes ou com baixa cobertura
- Testes marcados para skip/skipif/xfail
- Documentação desatualizada
"""

import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional


# Cores para output
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def count_test_functions(file_path: Path) -> Tuple[int, List[str], List[str]]:
    """
    Count test functions in a file using AST parsing.

    Returns:
        Tuple of (count, function_names, async_function_names)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        sync_funcs = []
        async_funcs = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_"):
                    sync_funcs.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                if node.name.startswith("test_"):
                    async_funcs.append(node.name)

        return len(sync_funcs) + len(async_funcs), sync_funcs, async_funcs
    except SyntaxError as e:
        print(f"{Colors.WARNING}Syntax error in {file_path}: {e}{Colors.ENDC}")
        return 0, [], []
    except Exception as e:
        print(f"{Colors.WARNING}Error parsing {file_path}: {e}{Colors.ENDC}")
        return 0, [], []


def analyze_skip_markers(file_path: Path) -> Dict[str, List[str]]:
    """Analyze skip/skipif/xfail markers in test file."""
    markers = {"skip": [], "skipif": [], "xfail": [], "runtime_skip": []}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find skip decorators with reasons
        skip_pattern = r"@pytest\.mark\.skip\((.*?)\)"
        markers["skip"] = re.findall(skip_pattern, content, re.DOTALL)

        # Find skipif decorators
        skipif_pattern = r"@pytest\.mark\.skipif\((.*?)\)"
        markers["skipif"] = re.findall(skipif_pattern, content, re.DOTALL)

        # Find xfail decorators
        xfail_pattern = r"@pytest\.mark\.xfail\((.*?)\)"
        markers["xfail"] = re.findall(xfail_pattern, content, re.DOTALL)

        # Find runtime skips
        if "pytest.skip(" in content:
            markers["runtime_skip"].append("runtime skip found")

    except Exception as e:
        print(
            f"{Colors.WARNING}Error analyzing markers in {file_path}: {e}{Colors.ENDC}"
        )

    return markers


def check_import_errors(test_file: Path, project_root: Path) -> Optional[str]:
    """
    Check if a test file has import errors.

    Returns:
        Error message if import fails, None otherwise.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )

    if (
        result.returncode != 0
        or "ERROR" in result.stdout
        or "error" in result.stderr.lower()
    ):
        error_msg = result.stderr if result.stderr else result.stdout
        error_lines = error_msg.split("\n")

        # Extract the main error
        for line in reversed(error_lines):
            if "ModuleNotFoundError" in line or "ImportError" in line:
                return line.strip()

        return "Unknown import error"

    return None


def find_source_modules_without_tests(
    src_dir: Path, tests_dir: Path
) -> List[Dict[str, any]]:
    """
    Find source modules that don't have corresponding test files.

    Returns:
        List of dicts with module info
    """
    untested_modules = []

    for src_file in src_dir.rglob("*.py"):
        if src_file.name == "__init__.py":
            continue

        # Skip excluded files from .coveragerc
        if any(
            pattern in str(src_file)
            for pattern in [
                "orchestrator_agent.py",
                "react_agent.py",
                "react_agent_broken.py",
                "debug_agent.py",
                "security_agent.py",
            ]
        ):
            continue

        # Determine expected test path
        relative_path = src_file.relative_to(src_dir)
        module_name = src_file.stem

        # Check various test naming conventions
        test_candidates = [
            tests_dir / relative_path.parent / f"test_{module_name}.py",
            tests_dir / f"test_{module_name}.py",
        ]

        # Check if any test file exists
        has_test = any(candidate.exists() for candidate in test_candidates)

        if not has_test:
            # Count functions/classes in the module
            try:
                with open(src_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                functions = sum(
                    1
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
                classes = sum(
                    1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
                )

                untested_modules.append(
                    {
                        "module": str(relative_path),
                        "functions": functions,
                        "classes": classes,
                        "is_critical": is_critical_module(src_file),
                    }
                )
            except Exception:
                pass

    return untested_modules


def is_critical_module(file_path: Path) -> bool:
    """
    Determine if a module is critical based on its location/name.

    Critical modules include:
    - Core agents
    - Security components
    - Memory systems
    - Audit systems
    """
    critical_patterns = [
        "agents/",
        "security/",
        "audit/",
        "memory/",
        "integrations/",
        "core",
        "omnimind_core",
    ]

    path_str = str(file_path)
    return any(pattern in path_str for pattern in critical_patterns)


def analyze_test_coverage(project_root: Path) -> Optional[Dict]:
    """
    Run pytest with coverage and analyze results.

    Returns:
        Coverage data dict or None if coverage run fails.
    """
    coverage_file = project_root / ".coverage"
    if coverage_file.exists():
        coverage_file.unlink()

    # Try to run coverage
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=src",
            "--cov-report=json",
            "--cov-report=term",
            "-x",  # Stop on first failure
            "--tb=no",  # No traceback
            "-q",
            "tests/",
        ],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )

    coverage_json = project_root / "coverage.json"
    if coverage_json.exists():
        with open(coverage_json, "r") as f:
            return json.load(f)

    return None


def main():
    """Run comprehensive test suite analysis."""
    project_root = Path(__file__).resolve().parent.parent
    tests_dir = project_root / "tests"
    src_dir = project_root / "src"

    print_section("ANÁLISE COMPLETA DA SUÍTE DE TESTES OMNIMIND")

    # Statistics
    total_files = 0
    total_test_functions = 0
    total_async_tests = 0
    files_with_skips = 0
    total_skipped = 0
    total_skipif = 0
    total_xfail = 0
    import_errors = []

    # Detailed tracking
    file_stats = []

    print(f"{Colors.OKCYAN}Analisando arquivos de teste...{Colors.ENDC}")

    # Analyze each test file
    for test_file in sorted(tests_dir.rglob("test_*.py")):
        if "legacy" in test_file.parts:
            continue

        total_files += 1
        count, sync_funcs, async_funcs = count_test_functions(test_file)
        total_test_functions += count
        total_async_tests += len(async_funcs)

        markers = analyze_skip_markers(test_file)
        has_skip = any(markers.values())

        if has_skip:
            files_with_skips += 1
            total_skipped += len(markers["skip"])
            total_skipif += len(markers["skipif"])
            total_xfail += len(markers["xfail"])

        # Check for import errors
        import_error = check_import_errors(test_file, project_root)
        if import_error:
            import_errors.append(
                {"file": str(test_file.relative_to(tests_dir)), "error": import_error}
            )

        file_stats.append(
            {
                "file": str(test_file.relative_to(tests_dir)),
                "test_count": count,
                "async_count": len(async_funcs),
                "has_skip": has_skip,
                "skip_count": len(markers["skip"]),
                "skipif_count": len(markers["skipif"]),
                "xfail_count": len(markers["xfail"]),
                "has_import_error": import_error is not None,
            }
        )

        if total_files % 10 == 0:
            print(f"  Processados {total_files} arquivos...", end="\r")

    print(f"\n{Colors.OKGREEN}Análise de arquivos concluída!{Colors.ENDC}")

    # Find untested modules
    print(f"\n{Colors.OKCYAN}Identificando módulos sem testes...{Colors.ENDC}")
    untested = find_source_modules_without_tests(src_dir, tests_dir)
    critical_untested = [m for m in untested if m["is_critical"]]

    # Generate summary report
    print_section("RESUMO EXECUTIVO")

    print(f"{Colors.BOLD}Arquivos de Teste:{Colors.ENDC}")
    print(f"  Total de arquivos de teste: {Colors.OKGREEN}{total_files}{Colors.ENDC}")
    print(
        f"  Arquivos com erros de importação: {Colors.FAIL if import_errors else Colors.OKGREEN}{len(import_errors)}{Colors.ENDC}"
    )
    print(
        f"  Arquivos com marcadores skip: {Colors.WARNING if files_with_skips else Colors.OKGREEN}{files_with_skips}{Colors.ENDC}"
    )

    print(f"\n{Colors.BOLD}Testes Definidos:{Colors.ENDC}")
    print(
        f"  Total de funções de teste: {Colors.OKGREEN}{total_test_functions}{Colors.ENDC}"
    )
    print(f"  Testes assíncronos: {Colors.OKBLUE}{total_async_tests}{Colors.ENDC}")
    print(
        f"  Testes síncronos: {Colors.OKBLUE}{total_test_functions - total_async_tests}{Colors.ENDC}"
    )

    print(f"\n{Colors.BOLD}Marcadores de Skip:{Colors.ENDC}")
    print(f"  @pytest.mark.skip: {total_skipped}")
    print(f"  @pytest.mark.skipif: {total_skipif}")
    print(f"  @pytest.mark.xfail: {total_xfail}")
    print(
        f"  Total estimado pulados: {Colors.WARNING}{total_skipped + total_skipif + total_xfail}{Colors.ENDC}"
    )

    print(f"\n{Colors.BOLD}Previsão de Execução:{Colors.ENDC}")
    runnable_tests = total_test_functions - (total_skipped + total_skipif + total_xfail)
    blocked_by_imports = sum(
        f["test_count"] for f in file_stats if f["has_import_error"]
    )
    actually_runnable = runnable_tests - blocked_by_imports

    print(
        f"  Testes executáveis (sem erros import): {Colors.OKGREEN}{actually_runnable}{Colors.ENDC}"
    )
    print(
        f"  Testes bloqueados por import: {Colors.FAIL}{blocked_by_imports}{Colors.ENDC}"
    )
    print(
        f"  Testes marcados para skip: {Colors.WARNING}{total_skipped + total_skipif + total_xfail}{Colors.ENDC}"
    )

    # Discrepancy explanation
    print_section("EXPLICAÇÃO DA DISCREPÂNCIA")
    print(
        f"Testes definidos no código:     {Colors.BOLD}{total_test_functions:5d}{Colors.ENDC}"
    )
    print(
        f"Testes bloqueados (imports):    {Colors.FAIL}{blocked_by_imports:5d}{Colors.ENDC} ({blocked_by_imports/total_test_functions*100:.1f}%)"
    )
    print(
        f"Testes marcados skip:           {Colors.WARNING}{total_skipped + total_skipif:5d}{Colors.ENDC} ({(total_skipped + total_skipif)/total_test_functions*100:.1f}%)"
    )
    print(f"{'─'*40}")
    print(
        f"Testes esperados na execução:   {Colors.OKGREEN}{actually_runnable:5d}{Colors.ENDC} ({actually_runnable/total_test_functions*100:.1f}%)"
    )

    # Import errors breakdown
    if import_errors:
        print_section("ERROS DE IMPORTAÇÃO DETALHADOS")

        # Group by error type
        error_groups = defaultdict(list)
        for err in import_errors:
            # Extract missing module name
            if "No module named" in err["error"]:
                module = (
                    err["error"].split("'")[-2] if "'" in err["error"] else "unknown"
                )
                error_groups[module].append(err["file"])
            else:
                error_groups["other"].append(err["file"])

        for module, files in sorted(
            error_groups.items(), key=lambda x: len(x[1]), reverse=True
        ):
            print(f"\n{Colors.FAIL}Módulo faltante: {module}{Colors.ENDC}")
            print(f"  Arquivos afetados: {len(files)}")
            affected_tests = sum(
                f["test_count"] for f in file_stats if f["file"] in files
            )
            print(f"  Testes bloqueados: {affected_tests}")
            for f in files[:5]:
                test_count = next(
                    (x["test_count"] for x in file_stats if x["file"] == f), 0
                )
                print(f"    - {f} ({test_count} tests)")
            if len(files) > 5:
                print(f"    ... e mais {len(files) - 5} arquivos")

    # Untested modules
    if untested:
        print_section("MÓDULOS SEM TESTES")
        print(
            f"Total de módulos sem testes: {Colors.WARNING}{len(untested)}{Colors.ENDC}"
        )
        print(
            f"Módulos críticos sem testes: {Colors.FAIL if critical_untested else Colors.OKGREEN}{len(critical_untested)}{Colors.ENDC}"
        )

        if critical_untested:
            print(f"\n{Colors.FAIL}MÓDULOS CRÍTICOS SEM TESTES:{Colors.ENDC}")
            for module in critical_untested[:10]:
                print(f"  - {module['module']}")
                print(
                    f"    Funções: {module['functions']}, Classes: {module['classes']}"
                )
            if len(critical_untested) > 10:
                print(f"  ... e mais {len(critical_untested) - 10} módulos críticos")

    # Top files by test count
    print_section("ARQUIVOS COM MAIS TESTES")
    sorted_files = sorted(file_stats, key=lambda x: x["test_count"], reverse=True)
    for i, f in enumerate(sorted_files[:15], 1):
        status_icon = "❌" if f["has_import_error"] else "⚠️" if f["has_skip"] else "✅"
        print(f"{i:2d}. {status_icon} {f['file']:55s} - {f['test_count']:4d} tests")

    # Save detailed JSON report
    report = {
        "summary": {
            "total_test_files": total_files,
            "total_test_functions_defined": total_test_functions,
            "total_async_tests": total_async_tests,
            "files_with_import_errors": len(import_errors),
            "tests_blocked_by_imports": blocked_by_imports,
            "files_with_skip_markers": files_with_skips,
            "total_skip_decorators": total_skipped,
            "total_skipif_decorators": total_skipif,
            "total_xfail_decorators": total_xfail,
            "expected_runnable_tests": actually_runnable,
            "modules_without_tests": len(untested),
            "critical_modules_without_tests": len(critical_untested),
        },
        "file_details": file_stats,
        "import_errors": import_errors,
        "untested_modules": untested,
        "critical_untested": critical_untested,
    }

    report_path = project_root / "test_suite_analysis_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print_section("RELATÓRIO SALVO")
    print(f"Relatório detalhado salvo em: {Colors.OKGREEN}{report_path}{Colors.ENDC}")

    # Print recommendations
    print_section("RECOMENDAÇÕES")
    print(f"1. {Colors.BOLD}Instalar dependências faltantes{Colors.ENDC}")
    print(f"   - Execute: pip install -r requirements.txt")
    print(
        f"   - Isso deve resolver {len(import_errors)} arquivos com erros de importação"
    )

    print(f"\n2. {Colors.BOLD}Revisar testes marcados para skip{Colors.ENDC}")
    print(f"   - {files_with_skips} arquivos têm testes marcados para skip")
    print(f"   - Revisar se esses skips ainda são necessários")

    if critical_untested:
        print(f"\n3. {Colors.BOLD}Adicionar testes para módulos críticos{Colors.ENDC}")
        print(f"   - {len(critical_untested)} módulos críticos não têm testes")
        print(f"   - Priorizar módulos de segurança e core")

    print(f"\n4. {Colors.BOLD}Atualizar pytest.ini{Colors.ENDC}")
    print(f"   - Considerar remover --maxfail=5 para permitir coleta completa")
    print(f"   - Ou aumentar para um valor maior durante análise")

    return 0


if __name__ == "__main__":
    sys.exit(main())
