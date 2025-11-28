#!/usr/bin/env python3
"""
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

"""
Script para verificar e instalar dependências faltantes dos testes.

Este script:
1. Identifica quais dependências estão faltando
2. Mostra quais testes serão desbloqueados
3. Oferece instalação automática
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    """ANSI color codes."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


# Mapeamento de módulos faltantes para pacotes pip
DEPENDENCY_MAP = {
    "numpy": {
        "package": "numpy>=1.26.0",
        "test_files": 9,
        "tests_blocked": 203,
        "description": "Biblioteca fundamental para computação numérica",
    },
    "langchain_ollama": {
        "package": "langchain-ollama>=0.0.1",
        "test_files": 8,
        "tests_blocked": 44,
        "description": "Framework para agentes com Ollama",
    },
    "fastapi": {
        "package": "fastapi>=0.110.0",
        "test_files": 7,
        "tests_blocked": 80,
        "description": "Framework web para APIs",
    },
    "torch": {
        "package": "torch>=2.2.0",
        "test_files": 3,
        "tests_blocked": 37,
        "description": "PyTorch - Deep Learning Framework",
    },
    "cryptography": {
        "package": "cryptography>=41.0.0",
        "test_files": 2,
        "tests_blocked": 56,
        "description": "Biblioteca de criptografia",
    },
    "qdrant_client": {
        "package": "qdrant-client>=1.16.0",
        "test_files": 3,
        "tests_blocked": 9,
        "description": "Cliente para banco de dados vetorial Qdrant",
    },
    "opentelemetry": {
        "package": "opentelemetry-api>=1.20.0 opentelemetry-sdk>=1.20.0",
        "test_files": 1,
        "tests_blocked": 15,
        "description": "OpenTelemetry para observabilidade",
    },
    "dbus": {
        "package": "dbus-python>=1.3.0",
        "test_files": 1,
        "tests_blocked": 2,
        "description": "D-Bus para comunicação com sistema (requer libdbus-dev)",
        "system_deps": ["libdbus-1-dev"],
    },
}


def check_module_installed(module_name: str) -> bool:
    """Verifica se um módulo Python está instalado."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def check_all_dependencies() -> Tuple[List[str], List[str]]:
    """
    Verifica todas as dependências.

    Returns:
        Tuple de (missing, installed)
    """
    missing = []
    installed = []

    for module, info in DEPENDENCY_MAP.items():
        if check_module_installed(module):
            installed.append(module)
        else:
            missing.append(module)

    return missing, installed


def install_package(package: str) -> bool:
    """
    Instala um pacote usando pip.

    Returns:
        True se instalação bem-sucedida
    """
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + package.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Execute dependency check and installation."""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("VERIFICAÇÃO DE DEPENDÊNCIAS - SUITE DE TESTES OMNIMIND".center(80))
    print("=" * 80)
    print(f"{Colors.ENDC}\n")

    # Check current status
    missing, installed = check_all_dependencies()

    if not missing:
        print(f"{Colors.OKGREEN}{Colors.BOLD}")
        print("✓ Todas as dependências estão instaladas!")
        print(f"{Colors.ENDC}\n")
        return 0

    # Display status
    print(f"{Colors.BOLD}Status das Dependências:{Colors.ENDC}\n")

    print(f"{Colors.OKGREEN}Instaladas ({len(installed)}):{Colors.ENDC}")
    for module in installed:
        info = DEPENDENCY_MAP[module]
        print(f"  ✓ {module}: {info['description']}")

    print(f"\n{Colors.FAIL}Faltando ({len(missing)}):{Colors.ENDC}")
    total_blocked = 0
    total_files = 0

    for module in missing:
        info = DEPENDENCY_MAP[module]
        total_blocked += info["tests_blocked"]
        total_files += info["test_files"]

        print(f"  ✗ {module}")
        print(f"    Descrição: {info['description']}")
        print(f"    Testes bloqueados: {info['tests_blocked']} em {info['test_files']} arquivos")
        print(f"    Pacote: {info['package']}")

        if "system_deps" in info:
            print(
                f"    {Colors.WARNING}Requer deps do sistema: {', '.join(info['system_deps'])}{Colors.ENDC}"
            )

    print(f"\n{Colors.BOLD}Impacto Total:{Colors.ENDC}")
    print(f"  Arquivos afetados: {Colors.FAIL}{total_files}{Colors.ENDC}")
    print(f"  Testes bloqueados: {Colors.FAIL}{total_blocked}{Colors.ENDC}")
    print(
        f"  Percentual bloqueado: {Colors.FAIL}{total_blocked/2412*100:.1f}%{Colors.ENDC} dos 2412 testes"
    )

    # Ask for installation
    print(f"\n{Colors.BOLD}Opções:{Colors.ENDC}")
    print("  1. Instalar todas as dependências automaticamente")
    print("  2. Instalar apenas dependências específicas")
    print("  3. Instalar via requirements.txt (recomendado)")
    print("  4. Sair sem instalar")

    choice = input(f"\n{Colors.BOLD}Escolha uma opção (1-4): {Colors.ENDC}").strip()

    if choice == "1":
        print(f"\n{Colors.OKBLUE}Instalando todas as dependências...{Colors.ENDC}\n")

        for module in missing:
            info = DEPENDENCY_MAP[module]
            print(f"Instalando {module}...", end=" ")

            if install_package(info["package"]):
                print(f"{Colors.OKGREEN}✓{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ Falhou{Colors.ENDC}")

        # Re-check
        missing_after, installed_after = check_all_dependencies()

        print(f"\n{Colors.BOLD}Resultado:{Colors.ENDC}")
        print(f"  Instaladas: {len(installed_after)}/{len(DEPENDENCY_MAP)}")

        if missing_after:
            print(f"  {Colors.WARNING}Ainda faltando: {', '.join(missing_after)}{Colors.ENDC}")
        else:
            print(f"  {Colors.OKGREEN}Todas as dependências instaladas!{Colors.ENDC}")

    elif choice == "2":
        print(f"\n{Colors.BOLD}Dependências disponíveis:{Colors.ENDC}")
        for i, module in enumerate(missing, 1):
            info = DEPENDENCY_MAP[module]
            print(f"  {i}. {module} ({info['tests_blocked']} testes)")

        selections = input(
            f"\n{Colors.BOLD}Digite os números separados por vírgula: {Colors.ENDC}"
        ).strip()

        try:
            indices = [int(x.strip()) - 1 for x in selections.split(",")]

            for idx in indices:
                if 0 <= idx < len(missing):
                    module = missing[idx]
                    info = DEPENDENCY_MAP[module]
                    print(f"\nInstalando {module}...", end=" ")

                    if install_package(info["package"]):
                        print(f"{Colors.OKGREEN}✓{Colors.ENDC}")
                    else:
                        print(f"{Colors.FAIL}✗ Falhou{Colors.ENDC}")
        except (ValueError, IndexError):
            print(f"{Colors.FAIL}Seleção inválida{Colors.ENDC}")

    elif choice == "3":
        print(f"\n{Colors.OKBLUE}Execute o seguinte comando:{Colors.ENDC}")
        print(f"\n  {Colors.BOLD}pip install -r requirements.txt{Colors.ENDC}\n")
        print(
            f"{Colors.WARNING}Nota: Isso instalará TODAS as dependências do projeto.{Colors.ENDC}"
        )
        print(f"{Colors.WARNING}Pode levar alguns minutos dependendo da conexão.{Colors.ENDC}\n")

    else:
        print(f"\n{Colors.WARNING}Nenhuma instalação realizada.{Colors.ENDC}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
