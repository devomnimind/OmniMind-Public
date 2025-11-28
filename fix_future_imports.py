#!/usr/bin/env python3
"""
Script para corrigir a posição do 'from __future__ import annotations'
deve estar na primeira linha não-comentada do arquivo.
"""

from pathlib import Path


def fix_future_annotations(file_path):
    """Corrige a posição do from __future__ import annotations."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Encontra a linha com from __future__ import annotations
        future_line = None
        future_index = -1

        for i, line in enumerate(lines):
            if 'from __future__ import annotations' in line:
                future_line = line
                future_index = i
                break

        if future_index <= 0:
            # Já está na posição correta ou não encontrado
            return False

        # Remove a linha da posição atual
        lines.pop(future_index)

        # Insere no início, após comentários de shebang e encoding
        insert_pos = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#!') or (stripped.startswith('#') and 'coding' in stripped):
                insert_pos = i + 1
            elif stripped and not stripped.startswith('#'):
                break

        # Insere a linha na posição correta
        lines.insert(insert_pos, future_line)

        # Escreve o arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return True

    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False


def main():
    """Processa todos os arquivos Python no projeto."""
    base_dir = Path('/home/fahbrain/projects/omnimind')
    src_dir = base_dir / 'src'
    tests_dir = base_dir / 'tests'

    fixed_count = 0

    # Processa src/
    for py_file in src_dir.rglob('*.py'):
        if fix_future_annotations(py_file):
            print(f"Corrigido: {py_file}")
            fixed_count += 1

    # Processa tests/
    for py_file in tests_dir.rglob('*.py'):
        if fix_future_annotations(py_file):
            print(f"Corrigido: {py_file}")
            fixed_count += 1

    print(f"\nTotal de arquivos corrigidos: {fixed_count}")


if __name__ == '__main__':
    main()