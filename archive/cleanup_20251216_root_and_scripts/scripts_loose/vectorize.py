#!/usr/bin/env python3
"""
🔗 WRAPPER - Script oficial: scripts/indexing/vectorize_omnimind.py

Este arquivo é um atalho que chama o script oficial de vetorização.
O arquivo real está em scripts/indexing/ junto com outros scripts de indexação.

USE:
  python scripts/vectorize.py

Ou direto:
  python scripts/indexing/vectorize_omnimind.py
"""

import sys
from pathlib import Path

# Importar e executar o script oficial
if __name__ == "__main__":
    script_path = Path(__file__).parent / "indexing" / "vectorize_omnimind.py"

    if not script_path.exists():
        print(f"❌ Erro: Script oficial não encontrado em {script_path}")
        sys.exit(1)

    # Executar o script oficial
    with open(script_path) as f:
        code = f.read()
    exec(compile(code, str(script_path), "exec"))
