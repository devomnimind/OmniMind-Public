#!/usr/bin/env python3
"""
Reorganização de Documentação - OmniMind

Move arquivos .md para seus devidos lugares baseado na análise.

Autor: OmniMind Development
Data: 2025-12-05
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

from analyze_documentation import DocumentationAnalyzer


class DocumentationReorganizer:
    """Reorganiza documentação baseado em análise"""

    def __init__(self, root: Path, dry_run: bool = True):
        self.root = root
        self.dry_run = dry_run
        self.moves: List[Tuple[Path, Path]] = []
        self.archive_moves: List[Tuple[Path, Path]] = []

    def plan_reorganization(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Planeja reorganização"""
        plan = {
            "moves_to_docs": [],
            "moves_to_archive": [],
            "creates": [],
        }

        # Documentos na raiz que devem ir para docs/
        root_docs = [
            d
            for d in report["docs"]
            if d["category"] == "root_doc"
            and d["path"] != "README.md"
            and "archive" not in d["path"]
        ]

        for doc in root_docs:
            src = self.root / doc["path"]
            # Determinar destino baseado no conteúdo
            dest = self._determine_destination(src, doc)
            if dest and dest != src:
                plan["moves_to_docs"].append(
                    {
                        "from": str(src.relative_to(self.root)),
                        "to": str(dest.relative_to(self.root)),
                        "reason": "Documento na raiz deve estar em docs/",
                    }
                )

        # Candidatos a arquivar
        for candidate in report["archive_candidates"]:
            src = self.root / candidate["path"]
            if "archive" not in str(src):
                dest = self.root / "docs" / "archive" / "root_reports" / src.name
                plan["moves_to_archive"].append(
                    {
                        "from": str(src.relative_to(self.root)),
                        "to": str(dest.relative_to(self.root)),
                        "reason": "; ".join(candidate["reasons"]),
                    }
                )

        return plan

    def _determine_destination(self, src: Path, doc_info: Dict[str, Any]) -> Path | None:
        """Determina destino do documento"""
        name_lower = src.name.lower()

        # Phase reports → docs/
        if "phase" in name_lower or "PHASE" in src.name:
            if "analysis" in name_lower or "report" in name_lower:
                return self.root / "docs" / "reports" / src.name
            else:
                return self.root / "docs" / src.name

        # Status/Production reports → docs/production/
        if any(word in name_lower for word in ["status", "production", "validation"]):
            return self.root / "docs" / "production" / src.name

        # Research papers → docs/papers/
        if any(word in name_lower for word in ["research", "scientific", "paper"]):
            return self.root / "docs" / "papers" / src.name

        # Guides → docs/guides/
        if "guide" in name_lower:
            return self.root / "docs" / "guides" / src.name

        # Default: docs/
        return self.root / "docs" / src.name

    def execute_plan(self, plan: Dict[str, Any]) -> None:
        """Executa plano de reorganização"""
        print("=" * 80)
        print("📦 PLANO DE REORGANIZAÇÃO")
        print("=" * 80)

        # Criar diretórios necessários
        all_dests = set()
        for move in plan["moves_to_docs"] + plan["moves_to_archive"]:
            dest_path = self.root / move["to"]
            all_dests.add(dest_path.parent)

        for dest_dir in all_dests:
            if not self.dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Criar diretório: {dest_dir.relative_to(self.root)}")

        # Mover para docs/
        print(f"\n📄 Mover para docs/ ({len(plan['moves_to_docs'])} arquivos):")
        for move in plan["moves_to_docs"]:
            src = self.root / move["from"]
            dest = self.root / move["to"]
            print(f"  {move['from']} → {move['to']}")
            if not self.dry_run and src.exists():
                shutil.move(str(src), str(dest))

        # Mover para archive/
        print(f"\n📦 Mover para archive/ ({len(plan['moves_to_archive'])} arquivos):")
        for move in plan["moves_to_archive"]:
            src = self.root / move["from"]
            dest = self.root / move["to"]
            print(f"  {move['from']} → {move['to']}")
            if not self.dry_run and src.exists():
                shutil.move(str(src), str(dest))

        if self.dry_run:
            print("\n⚠️  DRY RUN - Nenhum arquivo foi movido")
        else:
            print("\n✅ Reorganização concluída!")


def main():
    """Função principal"""
    root = Path(__file__).parent.parent

    # Carregar análise
    report_path = root / "data" / "test_reports" / "documentation_analysis.json"
    if not report_path.exists():
        print("❌ Execute primeiro: python scripts/analyze_documentation.py")
        return

    report = json.loads(report_path.read_text())

    # Planejar reorganização
    reorganizer = DocumentationReorganizer(root, dry_run=True)
    plan = reorganizer.plan_reorganization(report)

    # Mostrar plano
    print(json.dumps(plan, indent=2, ensure_ascii=False))

    # Executar (com dry_run=True primeiro)
    reorganizer.execute_plan(plan)

    print("\n" + "=" * 80)
    print("💡 Para executar de verdade, mude dry_run=False")
    print("=" * 80)


if __name__ == "__main__":
    main()

