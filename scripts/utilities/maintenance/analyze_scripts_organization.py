#!/usr/bin/env python3
"""
Análise completa de scripts para organização e mapeamento por fase.
Identifica scripts não usados, scripts na raiz que devem ser movidos,
e mapeia scripts por fase nas documentações.
"""

import os
from collections import defaultdict
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Scripts na raiz do projeto
ROOT_SCRIPTS = [
    "monitor_phase7.sh",
    "optimize_log.py",
    "test_decisions_fix.sh",
    "test_full_fix.sh",
    "test_tribunal_fix.sh",
    "TRIBUNAL_FIX_VISUAL.sh",
]

# Scripts canônicos (oficiais)
CANONICAL_SCRIPTS = {
    "scripts/canonical/system/start_omnimind_system.sh",
    "scripts/canonical/system/run_cluster.sh",
    "scripts/canonical/system/start_mcp_servers.sh",
    "scripts/run_tests_fast.sh",
    "scripts/run_tests_with_defense.sh",
    "scripts/quick_test.sh",
    "scripts/run_200_cycles_verbose.py",
}

# Fases conhecidas
PHASES = {
    "Phase 0": ["phase-0", "phase0", "data-collection"],
    "Phase 1": ["phase-1", "phase1", "analysis"],
    "Phase 5": ["phase-5", "phase5", "phase5_6"],
    "Phase 6": ["phase-6", "phase6", "phase5_6"],
    "Phase 7": ["phase-7", "phase7", "zimerman"],
    "Phase 22": ["phase-22", "phase22"],
    "Phase 24": ["phase-24", "phase24"],
    "Phase 26": ["phase-26", "phase26", "phase_26c"],
}


def find_script_references(script_name: str) -> List[str]:
    """Encontra todas as referências a um script."""
    references = []
    script_base = script_name.replace(".sh", "").replace(".py", "")

    for ext in ["*.md", "*.sh", "*.py", "*.tsx", "*.ts", "*.txt"]:
        for file in PROJECT_ROOT.rglob(ext):
            if file.is_file() and file.name != script_name:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if script_name in content or script_base in content:
                        references.append(str(file.relative_to(PROJECT_ROOT)))
                except:
                    pass

    return references


def map_script_to_phase(script_path: str) -> List[str]:
    """Mapeia um script para suas fases baseado no nome e conteúdo."""
    phases_found = []
    script_name = script_path.lower()

    for phase_name, keywords in PHASES.items():
        if any(kw in script_name for kw in keywords):
            phases_found.append(phase_name)

    return phases_found


def analyze_scripts():
    """Análise completa de scripts."""
    print("🔍 ANÁLISE COMPLETA DE SCRIPTS - OmniMind\n")
    print("=" * 80)

    # 1. Scripts na raiz
    print("\n📋 1. SCRIPTS NA RAIZ DO PROJETO\n")
    root_analysis = {}
    for script in ROOT_SCRIPTS:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            refs = find_script_references(script)
            phases = map_script_to_phase(script)
            root_analysis[script] = {
                "references": refs,
                "phases": phases,
                "exists": True,
            }
        else:
            root_analysis[script] = {
                "references": [],
                "phases": [],
                "exists": False,
            }

    for script, data in root_analysis.items():
        if not data["exists"]:
            continue
        print(f"📄 {script}")
        print(f"   Fases: {', '.join(data['phases']) if data['phases'] else 'N/A'}")
        print(f"   Referências: {len(data['references'])}")
        if data["references"]:
            print(f"   ✅ Usado em:")
            for ref in data["references"][:3]:
                print(f"      - {ref}")
            if len(data["references"]) > 3:
                print(f"      ... e mais {len(data['references']) - 3}")
        else:
            print(f"   ⚠️  NÃO REFERENCIADO (candidato a arquivar)")
        print()

    # 2. Scripts candidatos a arquivar
    print("\n📦 2. SCRIPTS CANDIDATOS A ARQUIVAR\n")
    candidates = []
    for script, data in root_analysis.items():
        if data["exists"] and not data["references"]:
            candidates.append(script)

    if candidates:
        print("Scripts não referenciados encontrados:")
        for script in candidates:
            print(f"   - {script}")
    else:
        print("✅ Nenhum script não referenciado encontrado")

    # 3. Mapeamento por fase
    print("\n🗺️  3. MAPEAMENTO DE SCRIPTS POR FASE\n")
    phase_scripts = defaultdict(list)

    # Buscar scripts em scripts/
    for script_file in (PROJECT_ROOT / "scripts").rglob("*.{sh,py}"):
        script_rel = str(script_file.relative_to(PROJECT_ROOT))
        phases = map_script_to_phase(script_rel)
        if phases:
            for phase in phases:
                phase_scripts[phase].append(script_rel)

    for phase, scripts in sorted(phase_scripts.items()):
        print(f"📌 {phase}:")
        for script in scripts[:5]:
            print(f"   - {script}")
        if len(scripts) > 5:
            print(f"   ... e mais {len(scripts) - 5} script(s)")
        print()

    # 4. Recomendações de organização
    print("\n💡 4. RECOMENDAÇÕES DE ORGANIZAÇÃO\n")

    print("Scripts na raiz que devem ser movidos:")
    print("   📁 scripts/testing/fixes/")
    for script in ["test_decisions_fix.sh", "test_full_fix.sh", "test_tribunal_fix.sh"]:
        if script in root_analysis and root_analysis[script]["exists"]:
            print(f"      → {script}")

    print("\n   📁 scripts/monitoring/")
    if "monitor_phase7.sh" in root_analysis and root_analysis["monitor_phase7.sh"]["exists"]:
        print(f"      → monitor_phase7.sh")

    print("\n   📁 scripts/utilities/maintenance/")
    if "optimize_log.py" in root_analysis and root_analysis["optimize_log.py"]["exists"]:
        print(f"      → optimize_log.py")

    print("\n   📁 scripts/archive/deprecated/")
    if (
        "TRIBUNAL_FIX_VISUAL.sh" in root_analysis
        and root_analysis["TRIBUNAL_FIX_VISUAL.sh"]["exists"]
    ):
        print(f"      → TRIBUNAL_FIX_VISUAL.sh (script de documentação visual)")

    # 5. Resumo
    print("\n" + "=" * 80)
    print("\n📊 RESUMO\n")
    print(f"Scripts na raiz analisados: {len([s for s in root_analysis.values() if s['exists']])}")
    print(f"Scripts não referenciados: {len(candidates)}")
    print(f"Fases mapeadas: {len(phase_scripts)}")
    print(f"Total de scripts por fase: {sum(len(s) for s in phase_scripts.values())}")


if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    analyze_scripts()
