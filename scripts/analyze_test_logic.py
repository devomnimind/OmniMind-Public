#!/usr/bin/env python3
"""
Análise da lógica de testes: verificar se está alinhada com operação atual.

Regras:
1. run_tests_fast.sh (diário):
   - Força GPU ✅
   - Roda testes reais de métricas (phi, IIT, etc) ✅
   - Roda híbridos e mocks ✅
   - NÃO roda testes que destroem servidor (chaos) ✅

2. run_tests_with_defense.sh (semanal):
   - Roda suite completa (inclui chaos) ✅

3. Testes de métricas críticas:
   - Devem ter @pytest.mark.real
   - NÃO devem ter @pytest.mark.chaos (a menos que seja teste de resiliência)
   - Devem rodar diariamente
"""

from collections import defaultdict
from pathlib import Path
from typing import Dict

# Módulos críticos que medem métricas
METRIC_TESTS = {
    "phi": ["phi", "consciousness", "integration", "iit"],
    "iit": ["iit", "integration"],
    "lacanian": ["lacanian", "sinthome"],
    "conscious": ["consciousness", "awareness"],
    "freud": ["freud", "metapsychology"],
    "quantum": ["quantum"],
}

# Testes que destroem servidor
CHAOS_TESTS = ["chaos", "kill_server", "destroy", "crash"]


def analyze_test_file(file_path: Path) -> Dict:
    """Analisa um arquivo de teste."""
    try:
        content = file_path.read_text()
    except:
        return None

    file_str = str(file_path).lower()

    # Verificar marcadores
    has_real = "@pytest.mark.real" in content
    has_chaos = "@pytest.mark.chaos" in content
    has_slow = "@pytest.mark.slow" in content
    has_mock = any(p in content for p in ["@patch", "Mock(", "mock.", "unittest.mock"])

    # Verificar se é teste de métrica
    is_metric_test = False
    metric_types = []
    for metric_type, keywords in METRIC_TESTS.items():
        for keyword in keywords:
            if keyword in file_str:
                is_metric_test = True
                metric_types.append(metric_type)
                break

    # Verificar se destroi servidor
    destroys_server = False
    if has_chaos:
        destroys_server = True
    else:
        # Verificar por padrões no código
        for pattern in CHAOS_TESTS:
            if pattern in content.lower():
                destroys_server = True
                break

    # Classificar
    if is_metric_test:
        if has_real and not has_chaos:
            category = "MÉTRICA_REAL_SAFE"  # Roda diariamente
        elif has_real and has_chaos:
            category = "MÉTRICA_REAL_CHAOS"  # Só semanal
        elif not has_real:
            category = "MÉTRICA_SEM_REAL"  # PROBLEMA
        else:
            category = "MÉTRICA_OUTRO"
    elif destroys_server:
        category = "DESTRÓI_SERVIDOR"
    elif has_mock:
        category = "MOCK"
    else:
        category = "OUTRO"

    return {
        "file": str(file_path),
        "is_metric": is_metric_test,
        "metric_types": metric_types,
        "has_real": has_real,
        "has_chaos": has_chaos,
        "has_slow": has_slow,
        "has_mock": has_mock,
        "destroys_server": destroys_server,
        "category": category,
    }


def main():
    """Análise principal."""
    tests_dir = Path("/home/fahbrain/projects/omnimind/tests")

    results = defaultdict(list)
    all_files = []

    # Analisar todos os testes
    for test_file in tests_dir.rglob("test_*.py"):
        analysis = analyze_test_file(test_file)
        if analysis:
            all_files.append(analysis)
            results[analysis["category"]].append(analysis)

    # Relatório
    print("=" * 80)
    print("📊 ANÁLISE DA LÓGICA DE TESTES")
    print("=" * 80)
    print()

    print(f"📁 Total de arquivos: {len(all_files)}")
    print()

    # Verificar lógica dos scripts
    print("🔍 VERIFICAÇÃO DA LÓGICA DOS SCRIPTS:")
    print("-" * 80)

    # run_tests_fast.sh deve incluir:
    # - MÉTRICA_REAL_SAFE ✅
    # - MOCK ✅
    # - OUTRO ✅
    # - NÃO incluir: MÉTRICA_REAL_CHAOS, DESTRÓI_SERVIDOR

    fast_should_include = (
        len(results["MÉTRICA_REAL_SAFE"]) + len(results["MOCK"]) + len(results["OUTRO"])
    )
    fast_should_exclude = len(results["MÉTRICA_REAL_CHAOS"]) + len(results["DESTRÓI_SERVIDOR"])

    print(f"✅ run_tests_fast.sh (diário) deve incluir: {fast_should_include} arquivos")
    print(f"   - MÉTRICA_REAL_SAFE: {len(results['MÉTRICA_REAL_SAFE'])}")
    print(f"   - MOCK: {len(results['MOCK'])}")
    print(f"   - OUTRO: {len(results['OUTRO'])}")
    print()
    print(f"❌ run_tests_fast.sh (diário) deve EXCLUIR: {fast_should_exclude} arquivos")
    print(f"   - MÉTRICA_REAL_CHAOS: {len(results['MÉTRICA_REAL_CHAOS'])}")
    print(f"   - DESTRÓI_SERVIDOR: {len(results['DESTRÓI_SERVIDOR'])}")
    print()

    # run_tests_with_defense.sh deve incluir tudo
    print(f"✅ run_tests_with_defense.sh (semanal) deve incluir: {len(all_files)} arquivos (todos)")
    print()

    # PROBLEMAS: Testes de métrica sem @pytest.mark.real
    print("🚨 PROBLEMAS IDENTIFICADOS:")
    print("-" * 80)

    metric_without_real = results["MÉTRICA_SEM_REAL"]
    if metric_without_real:
        print(f"\n❌ Testes de métrica SEM @pytest.mark.real: {len(metric_without_real)}")
        for test in metric_without_real[:10]:
            print(f"   - {Path(test['file']).name}")
            print(f"     Tipos: {', '.join(test['metric_types'])}")
    else:
        print("\n✅ Todos os testes de métrica têm @pytest.mark.real")

    # Testes que destroem servidor sem @pytest.mark.chaos
    destroys_without_chaos = [f for f in all_files if f["destroys_server"] and not f["has_chaos"]]
    if destroys_without_chaos:
        print(
            f"\n❌ Testes que destroem servidor SEM @pytest.mark.chaos: {len(destroys_without_chaos)}"
        )
        for test in destroys_without_chaos[:5]:
            print(f"   - {Path(test['file']).name}")
    else:
        print("\n✅ Todos os testes que destroem servidor têm @pytest.mark.chaos")

    print()
    print("=" * 80)
    print("📋 RESUMO POR CATEGORIA")
    print("=" * 80)
    print()

    for category, files in sorted(results.items()):
        if files:
            print(f"  {category}: {len(files)} arquivos")
            if category in ["MÉTRICA_SEM_REAL", "MÉTRICA_REAL_CHAOS", "DESTRÓI_SERVIDOR"]:
                print(f"    (Primeiros 3: {', '.join([Path(f['file']).name for f in files[:3]])})")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
