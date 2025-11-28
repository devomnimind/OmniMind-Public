#!/usr/bin/env python3
"""
Script para adicionar copyright header AGPL v3 em todos os arquivos Python
"""

import os
import glob

COPYRIGHT_HEADER = '''"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""
'''

def add_copyright_to_file(filepath):
    """Adiciona copyright header se não existir"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verifica se já tem copyright
        if 'Copyright (C) 2024-2025 Fabrício da Silva' in content:
            return False

        # Remove shebang se existir
        shebang = ''
        if content.startswith('#!'):
            lines = content.split('\n')
            shebang = lines[0] + '\n'
            content = '\n'.join(lines[1:])

        # Adiciona copyright
        new_content = shebang + COPYRIGHT_HEADER + '\n' + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"Erro em {filepath}: {e}")
        return False

def main():
    """Função principal"""
    directories = ['src', 'tests', 'scripts']
    total_files = 0
    modified_files = 0

    for directory in directories:
        if os.path.exists(directory):
            pattern = os.path.join(directory, '**', '*.py')
            for filepath in glob.glob(pattern, recursive=True):
                total_files += 1
                if add_copyright_to_file(filepath):
                    modified_files += 1
                    print(f"✓ {filepath}")

    print("\nResumo:")
    print(f"Total de arquivos: {total_files}")
    print(f"Arquivos modificados: {modified_files}")

if __name__ == '__main__':
    main()