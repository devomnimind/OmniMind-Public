#!/usr/bin/env python3
"""
Análise completa de testes: mocks, produção e híbridos.

Identifica:
1. Testes que usam mock em módulos críticos (NÃO DEVERIAM)
2. Testes em produção (correto)
3. Testes híbridos (mock + real)
"""

import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Módulos críticos que NÃO devem usar mock
CRITICAL_MODULES = {
    "phi": ["phi", "consciousness", "integration", "iit"],
    "iit": ["iit", "integration", "phi"],
    "lacanian": ["lacanian", "sinthome", "desire", "symbolic"],
    "conscious": ["consciousness", "awareness", "qualia"],
    "freud": ["freud", "metapsychology", "ego", "id", "superego"],
    "quantum": ["quantum", "qiskit", "entanglement"],
    "orchestrator": ["orchestrator", "core"],
}

# Padrões de mock
MOCK_PATTERNS = [
    r"@patch\(",
    r"from unittest.mock",
    r"Mock\(",
    r"MagicMock\(",
    r"mock\.",
    r"@mock",
    r"unittest.mock",
]

# Padrões de produção
PRODUCTION_PATTERNS = [
    r"@pytest.mark.real",
    r"@pytest.mark.gpu",
    r"@pytest.mark.quantum",
]


def is_critical_module(file_path: str) -> Tuple[bool, List[str]]:
    """Verifica se o arquivo é de módulo crítico."""
    file_lower = file_path.lower()
    found_modules = []

    for module_type, keywords in CRITICAL_MODULES.items():
        for keyword in keywords:
            if keyword in file_lower:
                found_modules.append(module_type)
                break

    return len(found_modules) > 0, found_modules


def has_mock(content: str) -> bool:
    """Verifica se o conteúdo usa mock."""
    for pattern in MOCK_PATTERNS:
        if re.search(pattern, content):
            return True
    return False


def has_production_marker(content: str) -> bool:
    """Verifica se tem marcador de produção."""
    for pattern in PRODUCTION_PATTERNS:
        if re.search(pattern, content):
            return True
    return False


def extract_test_functions(content: str) -> List[Dict[str, any]]:
    """Extrai funções de teste do arquivo."""
    tests = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_code = ast.get_source_segment(content, node) or ""
                tests.append(
                    {
                        "name": node.name,
                        "has_mock": has_mock(test_code),
                        "has_production": has_production_marker(test_code),
                        "code": test_code[:200],  # Primeiros 200 chars
                    }
                )
    except Exception:
        pass
    return tests


def analyze_test_file(file_path: Path) -> Dict:
    """Analisa um arquivo de teste."""
    try:
        content = file_path.read_text()
    except Exception:
        return None

    is_critical, critical_modules = is_critical_module(str(file_path))
    file_has_mock = has_mock(content)
    file_has_production = has_production_marker(content)
    tests = extract_test_functions(content)

    # Classificar arquivo
    if file_has_mock and file_has_production:
        category = "HÍBRIDO"
    elif file_has_production:
        category = "PRODUÇÃO"
    elif file_has_mock:
        category = "MOCK"
    else:
        category = "SEM_MOCK"

    # Verificar se crítico com mock (PROBLEMA)
    problem = is_critical and file_has_mock and not file_has_production

    return {
        "file": str(file_path),
        "is_critical": is_critical,
        "critical_modules": critical_modules,
        "category": category,
        "has_mock": file_has_mock,
        "has_production": file_has_production,
        "problem": problem,
        "test_count": len(tests),
        "tests": tests,
    }


def main():
    """Análise principal."""
    tests_dir = Path("/home/fahbrain/projects/omnimind/tests")

    results = {
        "MOCK": [],
        "PRODUÇÃO": [],
        "HÍBRIDO": [],
        "SEM_MOCK": [],
        "PROBLEMAS": [],  # Críticos com mock sem produção
    }

    all_files = []

    # Encontrar todos os arquivos de teste
    for test_file in tests_dir.rglob("test_*.py"):
        analysis = analyze_test_file(test_file)
        if analysis:
            all_files.append(analysis)
            results[analysis["category"]].append(analysis)

            if analysis["problem"]:
                results["PROBLEMAS"].append(analysis)

    # Relatório
    print("=" * 80)
    print("📊 ANÁLISE COMPLETA DE TESTES: MOCKS, PRODUÇÃO E HÍBRIDOS")
    print("=" * 80)
    print()

    print(f"📁 Total de arquivos de teste analisados: {len(all_files)}")
    print()

    # Estatísticas por categoria
    print("📊 ESTATÍSTICAS POR CATEGORIA:")
    print("-" * 80)
    for category, files in results.items():
        if category != "PROBLEMAS":
            print(f"  {category}: {len(files)} arquivos")
    print()

    # PROBLEMAS CRÍTICOS
    print("🚨 PROBLEMAS CRÍTICOS (Módulos críticos usando MOCK sem produção):")
    print("-" * 80)
    if results["PROBLEMAS"]:
        for problem in results["PROBLEMAS"]:
            print(f"\n  ❌ {problem['file']}")
            print(f"     Módulos críticos: {', '.join(problem['critical_modules'])}")
            print(f"     Testes: {problem['test_count']}")
            # Mostrar testes com mock
            mock_tests = [t for t in problem["tests"] if t["has_mock"]]
            if mock_tests:
                print(f"     Testes com mock: {len(mock_tests)}")
                for test in mock_tests[:3]:  # Primeiros 3
                    print(f"       - {test['name']}")
    else:
        print("  ✅ Nenhum problema encontrado!")
    print()

    # Detalhamento por módulo crítico
    print("🔬 DETALHAMENTO POR MÓDULO CRÍTICO:")
    print("-" * 80)

    critical_by_module = defaultdict(list)
    for analysis in all_files:
        if analysis["is_critical"]:
            for module in analysis["critical_modules"]:
                critical_by_module[module].append(analysis)

    for module, files in sorted(critical_by_module.items()):
        print(f"\n  📦 {module.upper()}: {len(files)} arquivos")
        mock_count = sum(1 for f in files if f["has_mock"] and not f["has_production"])
        prod_count = sum(1 for f in files if f["has_production"])
        hybrid_count = sum(1 for f in files if f["has_mock"] and f["has_production"])

        print(f"     ❌ Com mock (sem produção): {mock_count}")
        print(f"     ✅ Em produção: {prod_count}")
        print(f"     🔄 Híbridos: {hybrid_count}")

        # Listar problemas
        problems = [f for f in files if f["problem"]]
        if problems:
            print(f"     🚨 PROBLEMAS:")
            for p in problems:
                print(f"       - {Path(p['file']).name}")

    print()
    print("=" * 80)
    print("📋 RESUMO EXECUTIVO")
    print("=" * 80)
    print()

    total_critical = sum(1 for f in all_files if f["is_critical"])
    total_problems = len(results["PROBLEMAS"])

    print(f"  Total de testes críticos: {total_critical}")
    print(f"  Testes críticos com problema: {total_problems}")
    print(
        f"  Taxa de problemas: {total_problems/total_critical*100:.1f}%"
        if total_critical > 0
        else "  Taxa de problemas: 0%"
    )
    print()

    if total_problems > 0:
        print("  ⚠️  AÇÃO NECESSÁRIA:")
        print("     - Remover mocks de testes críticos")
        print("     - Adicionar @pytest.mark.real onde necessário")
        print("     - Garantir que testes de phi, IIT, Lacanian, Freud usem sistema real")
    else:
        print("  ✅ Todos os testes críticos estão corretos!")


if __name__ == "__main__":
    main()
