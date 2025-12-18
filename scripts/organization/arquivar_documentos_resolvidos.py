#!/usr/bin/env python3
"""
Script para arquivar documentos resolvidos.

Move documentos identificados como resolvidos para archive/docs/resolvidos_2025-12-07/
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
ARCHIVE_DIR = (
    PROJECT_ROOT / "archive" / "docs" / f"resolvidos_{datetime.now().strftime('%Y-%m-%d')}"
)
JSON_PATH = DOCS_DIR / "VARREDURA_COMPLETA_20251207.json"


def main():
    """Arquiva documentos resolvidos."""
    print("📦 Iniciando arquivamento de documentos resolvidos...")

    # Criar diretório de archive
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"   Diretório criado: {ARCHIVE_DIR}")

    # Carregar lista de documentos para arquivar
    if not JSON_PATH.exists():
        print(f"❌ Erro: {JSON_PATH} não encontrado. Execute varredura primeiro.")
        return

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    archive_list = data.get("archive_list", [])

    print(f"   Documentos para arquivar: {len(archive_list)}")

    # Mover documentos
    moved = []
    errors = []

    for rel_path_str in archive_list:
        src_path = PROJECT_ROOT / rel_path_str

        if not src_path.exists():
            errors.append(f"Arquivo não encontrado: {rel_path_str}")
            continue

        # Manter estrutura de diretórios no archive
        rel_path = Path(rel_path_str)
        if rel_path.parts[0] == "docs":
            # Remover "docs/" do início
            archive_rel = Path(*rel_path.parts[1:])
        else:
            archive_rel = rel_path

        dst_path = ARCHIVE_DIR / archive_rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(src_path), str(dst_path))
            moved.append(rel_path_str)
            print(f"   ✅ Movido: {rel_path_str} → {dst_path.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            errors.append(f"Erro ao mover {rel_path_str}: {e}")

    # Relatório
    print(f"\n✅ Arquivamento concluído!")
    print(f"   Movidos: {len(moved)}")
    print(f"   Erros: {len(errors)}")

    if errors:
        print("\n⚠️ Erros encontrados:")
        for error in errors:
            print(f"   - {error}")

    # Criar índice
    index_path = ARCHIVE_DIR / "INDEX.md"
    index_content = f"""# Índice de Documentos Arquivados

**Data de Arquivamento:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total de Documentos:** {len(moved)}

## Documentos Arquivados

"""
    for rel_path_str in sorted(moved):
        index_content += f"- `{rel_path_str}`\n"

    index_path.write_text(index_content, encoding="utf-8")
    print(f"\n📝 Índice criado: {index_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
