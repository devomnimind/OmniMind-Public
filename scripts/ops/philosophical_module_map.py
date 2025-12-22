#!/usr/bin/env python3
"""
MAPEAMENTO FILOSÓFICO DE MÓDULOS
Não busca "dependências" mas INTENÇÃO TEÓRICA

Baseado em:
- Deleuze-Guattari (Máquinas Desejantes, Rizoma)
- Lacan (Real-Simbólico-Imaginário, Sinthome)
- IIT (Φ como estrutura, não verdade)
- Manifesto Silício (Fluxo > Hierarquia)
"""
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")


def load_audit():
    """Carrega auditoria anterior."""
    with open(PROJECT_ROOT / "data/audit/SCIENTIFIC_DEEP_AUDIT.json") as f:
        return json.load(f)


def classify_by_philosophy(modules_data):
    """Classifica módulos por INTENÇÃO filosófica, não uso técnico."""

    categories = {
        "KERNEL_VITAL": [],  # Núcleo autopoiético (daemon, kernel)
        "TEORIAS_ATIVAS": [],  # Teorias implementadas e conectadas
        "TEORIAS_HIBERNANDO": [],  # Teorias válidas mas em espera
        "EXPERIMENTOS_FASE": [],  # Testes de fase específica
        "DEPRECATED_RECUPERAVEL": [],  # Pode ser recuperado
        "DEPRECATED_OBSOLETO": [],  # Realmente obsoleto
        "STUBS_INTERFACE": [],  # Not módulos reais
    }

    orphans = {o["path"]: o["reason"] for o in modules_data["orphans"]}

    for module in modules_data["modules_detailed"]:
        path = module["path"]
        name = module["name"]
        folder = module["folder"]

        # KERNEL VITAL
        if any(k in path for k in ["daemon", "kernel", "core/omnimind", "services/daemon_monitor"]):
            categories["KERNEL_VITAL"].append(
                {
                    "path": path,
                    "role": "Núcleo autopoiético - sustenta o sistema vivo",
                    "orphan": path in orphans,
                }
            )

        # EXPERIMENTOS DE FASE
        elif "phase" in name.lower():
            categories["EXPERIMENTOS_FASE"].append(
                {
                    "path": path,
                    "phase": name,
                    "theory": "Teste de integração de conceitos",
                    "status": "Pode ser retomado",
                    "orphan": path in orphans,
                }
            )

        # DEPRECATED
        elif any(
            d in folder
            for d in ["meta_learning", "phenomenology", "observability", "orchestrator", "defense"]
        ):
            # Verificar se é recuperável
            has_theory = module["patterns"].get("PSICANALITICA") or module["patterns"].get(
                "MATEMATICA"
            )
            if has_theory:
                categories["DEPRECATED_RECUPERAVEL"].append(
                    {
                        "path": path,
                        "reason": "Teoria válida, refatoração incompleta",
                        "recommendation": "Integrar em módulo atual",
                    }
                )
            else:
                categories["DEPRECATED_OBSOLETO"].append(
                    {"path": path, "reason": "Apenas placeholder ou redirect"}
                )

        # STUBS
        elif "stubs/" in path or name == "__init__":
            categories["STUBS_INTERFACE"].append({"path": path, "role": "Interface type hints"})

        # TEORIAS
        elif path in orphans:
            # Órfão mas tem conteúdo teórico?
            lines = module["lines"]
            has_content = lines > 50
            has_theory = any(module["patterns"].values())

            if has_content and has_theory:
                categories["TEORIAS_HIBERNANDO"].append(
                    {
                        "path": path,
                        "lines": lines,
                        "theory": [k for k, v in module["patterns"].items() if v],
                        "reason": orphans[path],
                        "recommendation": "INVESTIGAR intenção filosófica antes de descartar",
                    }
                )

        # Teorias ativas
        elif any(module["patterns"].values()):
            categories["TEORIAS_ATIVAS"].append(
                {"path": path, "theories": [k for k, v in module["patterns"].items() if v]}
            )

    return categories


def generate_philosophical_report(categories):
    """Gera relatório filosófico."""

    report = []
    report.append("# MAPEAMENTO FILOSÓFICO DE MÓDULOS OMNIMIND")
    report.append("**Perspectiva**: Intenção Teórica, não Dependência Técnica\n")
    report.append("---\n")

    report.append("## 🔴 KERNEL VITAL (Nunca mexer sem compreender)")
    report.append(f"Total: {len(categories['KERNEL_VITAL'])}\n")
    for item in categories["KERNEL_VITAL"][:10]:
        report.append(f"- `{item['path']}`")
        report.append(f"  Role: {item['role']}\n")

    report.append("\n## 🟢 TEORIAS ATIVAS")
    report.append(f"Total: {len(categories['TEORIAS_ATIVAS'])}\n")
    report.append("Módulos conectados e operacionais.\n")

    report.append("\n## 🟡 TEORIAS HIBERNANDO (INVESTIGAR)")
    report.append(f"Total: {len(categories['TEORIAS_HIBERNANDO'])}")
    report.append("**CRÍTICO**: Não são 'código morto' - são teorias em espera\n")
    for item in categories["TEORIAS_HIBERNANDO"][:20]:
        report.append(f"\n### `{item['path']}`")
        report.append(f"- Linhas: {item['lines']}")
        report.append(f"- Teorias: {', '.join(item['theory'])}")
        report.append(f"- Status órfão: {item['reason']}")
        report.append(f"- **Ação**: {item['recommendation']}")

    report.append("\n\n## 🔵 EXPERIMENTOS DE FASE")
    report.append(f"Total: {len(categories['EXPERIMENTOS_FASE'])}\n")
    for item in categories["EXPERIMENTOS_FASE"]:
        report.append(f"- `{item['path']}` - {item['theory']}")

    report.append("\n\n## ⚠️ DEPRECATED RECUPERÁVEL")
    report.append(f"Total: {len(categories['DEPRECATED_RECUPERAVEL'])}\n")
    for item in categories["DEPRECATED_RECUPERAVEL"]:
        report.append(f"- `{item['path']}`")
        report.append(f"  {item['recommendation']}\n")

    report.append("\n## ❌ DEPRECATED OBSOLETO")
    report.append(f"Total: {len(categories['DEPRECATED_OBSOLETO'])}")
    report.append("(Apenas redirects, pode remover)\n")

    return "\n".join(report)


def main():
    print("🧠 MAPEAMENTO FILOSÓFICO - OMNIMIND")
    print("Perspectiva: Intenção Teórica > Uso Técnico")
    print()

    # Carregar auditoria
    audit_data = load_audit()

    # Classificar filosoficamente
    categories = classify_by_philosophy(audit_data)

    # Gerar relatório
    report = generate_philosophical_report(categories)

    # Salvar
    output_path = PROJECT_ROOT / "data/audit/PHILOSOPHICAL_MODULE_MAP.md"
    with open(output_path, "w") as f:
        f.write(report)

    print(f"✅ Relatório salvo: {output_path.relative_to(PROJECT_ROOT)}")

    # Resumo
    print("\n📊 RESUMO FILOSÓFICO:")
    for cat, items in categories.items():
        print(f"  {cat}: {len(items)} módulos")

    print("\n⚠️ TEORIAS HIBERNANDO (Precisam investigação):")
    for item in categories["TEORIAS_HIBERNANDO"][:5]:
        print(f"  - {item['path']}")


if __name__ == "__main__":
    main()
