#!/usr/bin/env python3
"""
Script para verificar quais testes usam mocks vs servidor real.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent


def extract_excluded_files() -> List[str]:
    """Extrai lista de arquivos excluídos do pytest_server_monitor."""
    monitor_file = PROJECT_ROOT / "tests" / "plugins" / "pytest_server_monitor.py"

    with open(monitor_file, "r") as f:
        content = f.read()

    # Extrair lista excluded_files
    match = re.search(r'excluded_files = \[(.*?)\]', content, re.DOTALL)
    if not match:
        return []

    excluded_str = match.group(1)
    excluded = []
    for line in excluded_str.split('\n'):
        line = line.strip()
        if line and not line.strip().startswith('#'):
            # Extrair string entre aspas
            match_str = re.search(r'["\']([^"\']+)["\']', line)
            if match_str:
                excluded.append(match_str.group(1))

    return excluded


def find_all_test_files() -> List[str]:
    """Encontra todos os arquivos de teste."""
    test_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT / "tests"):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                rel_path = os.path.join(root, file).replace(str(PROJECT_ROOT) + '/', '')
                test_files.append(rel_path.replace('\\', '/'))
    return sorted(test_files)


def analyze_test_file(file_path: str) -> Dict[str, bool]:
    """Analisa um arquivo de teste para determinar características."""
    full_path = PROJECT_ROOT / file_path

    if not full_path.exists():
        return {"exists": False}

    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    return {
        "exists": True,
        "has_mock": bool(re.search(r'\b(mock|patch|MagicMock|Mock|@patch)\b', content, re.IGNORECASE)),
        "has_real_server": bool(re.search(r'\b(localhost:8000|localhost:3000|requests\.|http://|https://)\b', content)),
        "has_orchestrator": bool(re.search(r'\borchestrator\b', content, re.IGNORECASE)),
        "has_backend": bool(re.search(r'\bbackend\b', content, re.IGNORECASE)),
        "has_fixture_server": bool(re.search(r'\b(omnimind_server|server_fixture|@pytest\.fixture.*server)\b', content, re.IGNORECASE)),
        "has_integration_name": 'integration' in file_path.lower(),
        "has_e2e_name": 'e2e' in file_path.lower(),
        "has_dashboard_name": 'dashboard' in file_path.lower(),
    }


def main():
    """Executa análise completa."""
    print("=" * 80)
    print("🔍 ANÁLISE: TESTES MOCKS vs SERVIDOR REAL")
    print("=" * 80)
    print()

    excluded = extract_excluded_files()
    test_files = find_all_test_files()

    print(f"📊 ESTATÍSTICAS:")
    print(f"   Arquivos excluídos: {len(excluded)}")
    print(f"   Total de arquivos de teste: {len(test_files)}")
    print()

    # Categorizar testes
    excluded_with_mocks = []
    excluded_with_server = []
    not_excluded_with_mocks = []
    not_excluded_with_server = []
    suspicious = []

    for test_file in test_files:
        analysis = analyze_test_file(test_file)
        if not analysis.get("exists"):
            continue

        is_excluded = test_file in excluded

        if is_excluded:
            if analysis["has_mock"]:
                excluded_with_mocks.append((test_file, analysis))
            if analysis["has_real_server"] or analysis["has_fixture_server"]:
                excluded_with_server.append((test_file, analysis))
                if not analysis["has_mock"]:
                    suspicious.append((test_file, analysis, "Excluído mas usa servidor real"))
        else:
            if analysis["has_mock"] and analysis["has_integration_name"]:
                not_excluded_with_mocks.append((test_file, analysis))
            if analysis["has_real_server"] or analysis["has_fixture_server"]:
                not_excluded_with_server.append((test_file, analysis))

    # Relatório
    print("=" * 80)
    print("✅ ARQUIVOS EXCLUÍDOS QUE USAM MOCKS (CORRETO)")
    print("=" * 80)
    for test_file, analysis in excluded_with_mocks[:10]:
        print(f"  ✅ {test_file}")
    if len(excluded_with_mocks) > 10:
        print(f"  ... e mais {len(excluded_with_mocks) - 10} arquivos")
    print(f"\nTotal: {len(excluded_with_mocks)} arquivos")
    print()

    print("=" * 80)
    print("⚠️  ARQUIVOS EXCLUÍDOS QUE USAM SERVIDOR (SUSPEITO)")
    print("=" * 80)
    if excluded_with_server:
        for test_file, analysis in excluded_with_server:
            markers = []
            if analysis["has_real_server"]:
                markers.append("Server Real")
            if analysis["has_fixture_server"]:
                markers.append("Fixture Server")
            if analysis["has_mock"]:
                markers.append("Mock")
            print(f"  ⚠️  {test_file}")
            print(f"     {', '.join(markers)}")
        print(f"\nTotal: {len(excluded_with_server)} arquivos")
    else:
        print("  ✅ Nenhum arquivo suspeito encontrado")
    print()

    print("=" * 80)
    print("🔍 ARQUIVOS NÃO EXCLUÍDOS QUE USAM MOCKS + 'integration' NO NOME")
    print("=" * 80)
    if not_excluded_with_mocks:
        for test_file, analysis in not_excluded_with_mocks[:10]:
            print(f"  🔍 {test_file}")
            if analysis["has_mock"]:
                print(f"     Mock: ✅")
        if len(not_excluded_with_mocks) > 10:
            print(f"  ... e mais {len(not_excluded_with_mocks) - 10} arquivos")
        print(f"\nTotal: {len(not_excluded_with_mocks)} arquivos")
        print("  💡 Considerar adicionar à exclusão se são unitários")
    else:
        print("  ✅ Nenhum arquivo encontrado")
    print()

    print("=" * 80)
    print("📋 ARQUIVOS QUE PRECISAM DE SERVIDOR (NÃO EXCLUÍDOS)")
    print("=" * 80)
    for test_file, analysis in not_excluded_with_server[:10]:
        markers = []
        if analysis["has_real_server"]:
            markers.append("Server Real")
        if analysis["has_fixture_server"]:
            markers.append("Fixture Server")
        print(f"  📋 {test_file}")
        if markers:
            print(f"     {', '.join(markers)}")
    if len(not_excluded_with_server) > 10:
        print(f"  ... e mais {len(not_excluded_with_server) - 10} arquivos")
    print(f"\nTotal: {len(not_excluded_with_server)} arquivos")
    print()

    # Recomendações
    print("=" * 80)
    print("💡 RECOMENDAÇÕES")
    print("=" * 80)

    if suspicious:
        print("⚠️  Arquivos que podem precisar ser removidos da exclusão:")
        for test_file, analysis, reason in suspicious:
            print(f"  - {test_file} ({reason})")
        print()

    if not_excluded_with_mocks:
        print("💡 Arquivos que podem ser adicionados à exclusão:")
        for test_file, analysis in not_excluded_with_mocks[:5]:
            print(f"  - {test_file}")
        if len(not_excluded_with_mocks) > 5:
            print(f"  ... e mais {len(not_excluded_with_mocks) - 5} arquivos")
        print()


if __name__ == "__main__":
    main()

