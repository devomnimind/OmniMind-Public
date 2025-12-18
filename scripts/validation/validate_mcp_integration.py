#!/usr/bin/env python3
"""
MCP Integration Validation Script
Executa ciclo completo: Analyze -> Implement -> Validate (Lint/MyPy/Black) -> Test
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_command(cmd, description=""):
    """Executa comando e retorna resultado."""
    if description:
        print(f"\n📋 {description}")
    print(f"   → {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else [cmd],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT"
    except Exception as e:
        return False, "", str(e)


def validate_mcp_imports():
    """Valida se todos MCPs conseguem ser importados."""
    print("\n" + "=" * 70)
    print("🔍 FASE 1: IMPORTAÇÃO (Analyze)")
    print("=" * 70)

    mcps = [
        ("Memory", "src.integrations.mcp_memory_server:MemoryMCPServer"),
        ("Sequential Thinking", "src.integrations.mcp_thinking_server:ThinkingMCPServer"),
        ("Context", "src.integrations.mcp_context_server:ContextMCPServer"),
        ("Filesystem", "src.integrations.mcp_filesystem_wrapper:MCPFilesystemWrapper"),
        ("Git", "src.integrations.mcp_git_wrapper:GitMCPServer"),
        ("Python", "src.integrations.mcp_python_server:PythonMCPServer"),
    ]

    results = {}
    for name, path in mcps:
        module, cls = path.split(":")
        cmd = f"python -c \"from {module} import {cls}; print('OK')\""
        ok, stdout, stderr = run_command(cmd, f"Testing {name}")
        results[name] = ok
        if ok:
            print(f"   ✅ {name} imports successfully")
        else:
            print(f"   ❌ {name} import failed: {stderr[:100]}")

    return results


def validate_lint():
    """Valida lint dos MCPs críticos."""
    print("\n" + "=" * 70)
    print("🎨 FASE 2: LINTING (Analyze Syntax)")
    print("=" * 70)

    files = [
        "src/integrations/mcp_memory_server.py",
        "src/integrations/mcp_thinking_server.py",
        "src/integrations/mcp_context_server.py",
    ]

    results = {}
    for file in files:
        cmd = [
            "python",
            "-m",
            "flake8",
            file,
            "--max-line-length=88",
            "--extend-ignore=E203,W503,E501",
        ]
        ok, stdout, stderr = run_command(cmd, f"Flake8 on {file.split('/')[-1]}")
        if ok:
            print(f"   ✅ {file.split('/')[-1]} passed flake8")
        else:
            # Count violations
            violations = stdout.count("\n") if stdout else 0
            print(f"   ⚠️  {file.split('/')[-1]} has {violations} lint warnings")
        results[file] = ok

    return results


def validate_mypy():
    """Valida tipos com MyPy."""
    print("\n" + "=" * 70)
    print("🔍 FASE 3: TYPE CHECKING (MyPy)")
    print("=" * 70)

    files = [
        "src/integrations/mcp_memory_server.py",
        "src/integrations/mcp_thinking_server.py",
    ]

    results = {}
    for file in files:
        cmd = [
            "python",
            "-m",
            "mypy",
            file,
            "--ignore-missing-imports",
            "--no-implicit-optional",
        ]
        ok, stdout, stderr = run_command(cmd, f"MyPy on {file.split('/')[-1]}")
        if ok or "error:" not in stdout:
            print(f"   ✅ {file.split('/')[-1]} passes MyPy")
        else:
            errors = stdout.count("error:")
            print(f"   ⚠️  {file.split('/')[-1]} has {errors} type errors")
        results[file] = ok

    return results


def validate_black():
    """Verifica formatação Black."""
    print("\n" + "=" * 70)
    print("⚡ FASE 4: FORMATTING (Black)")
    print("=" * 70)

    files = [
        "src/integrations/mcp_memory_server.py",
        "src/integrations/mcp_thinking_server.py",
    ]

    results = {}
    for file in files:
        cmd = ["python", "-m", "black", "--check", "--diff", file]
        ok, stdout, stderr = run_command(cmd, f"Black check {file.split('/')[-1]}")
        if ok:
            print(f"   ✅ {file.split('/')[-1]} is properly formatted")
        else:
            print(f"   ⚠️  {file.split('/')[-1]} needs formatting")
        results[file] = ok

    return results


def validate_imports():
    """Valida imports (remove unused, order)."""
    print("\n" + "=" * 70)
    print("📦 FASE 5: IMPORT VALIDATION (isort)")
    print("=" * 70)

    files = [
        "src/integrations/mcp_memory_server.py",
        "src/integrations/mcp_thinking_server.py",
    ]

    results = {}
    for file in files:
        cmd = ["python", "-m", "isort", "--check-only", "--diff", file]
        ok, stdout, stderr = run_command(cmd, f"isort check {file.split('/')[-1]}")
        if ok:
            print(f"   ✅ {file.split('/')[-1]} imports are correctly ordered")
        else:
            print(f"   ⚠️  {file.split('/')[-1]} needs import reordering")
        results[file] = ok

    return results


def validate_health_check():
    """Testa health check dos MCPs."""
    print("\n" + "=" * 70)
    print("🏥 FASE 6: HEALTH CHECK (Runtime)")
    print("=" * 70)

    print("   ℹ️  Health checks require running servers (skipped in this phase)")
    print("   Use: bash scripts/production/start_mcp_internal.sh")
    return {}


def main():
    """Main validation pipeline."""
    print("\n" + "🎯 " * 25)
    print("OmniMind MCP Integration Validation")
    print("🎯 " * 25)

    results = {}

    # Phase 1: Imports
    results["imports"] = validate_mcp_imports()

    # Phase 2: Lint
    results["lint"] = validate_lint()

    # Phase 3: Types
    results["mypy"] = validate_mypy()

    # Phase 4: Format
    results["black"] = validate_black()

    # Phase 5: Imports order
    results["isort"] = validate_imports()

    # Phase 6: Health
    results["health"] = validate_health_check()

    # Summary
    print("\n" + "=" * 70)
    print("📊 RESUMO DE VALIDAÇÃO")
    print("=" * 70)

    all_ok = True
    for phase, phase_results in results.items():
        if isinstance(phase_results, dict):
            total = len(phase_results)
            passed = sum(1 for v in phase_results.values() if v)
            status = "✅" if passed == total else "⚠️"
            print(f"{status} {phase}: {passed}/{total} passed")
            if passed < total:
                all_ok = False

    print("\n" + "=" * 70)
    if all_ok:
        print("✅ TODOS OS TESTES PASSARAM - Sistema pronto para integração")
    else:
        print("⚠️  Alguns testes falharam - Revisar e corrigir")
    print("=" * 70 + "\n")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
