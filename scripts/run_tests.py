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
Test Runner Script for OmniMind

Este script executa todos os testes do projeto OmniMind.
Execute com: python scripts/run_tests.py
"""

import os
import sys


def main():
    """Executa suite completa de testes."""

    # Garantir que estamos na raiz do projeto
    project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
    if os.getcwd() != project_root:
        os.chdir(project_root)
        print(f"📂 Working directory set to: {os.getcwd()}")

    print("🧪 OmniMind Test Suite")
    print("=" * 50)

    # Testes E2E
    print("\n1. 🚀 End-to-End Tests")
    os.system("pytest tests/test_e2e_integration.py -v --tb=short")

    # Testes de Memória
    print("\n2. 🧠 Memory Systems")
    os.system("pytest tests/memory/ -v --tb=short")

    # Testes Quânticos
    print("\n3. ⚛️ Quantum Consciousness")
    os.system("pytest tests/quantum_consciousness/ tests/quantum_ai/ -v --tb=short")

    # Testes de Segurança
    print("\n4. 🛡️ Security & Ethics")
    os.system("pytest tests/security/ tests/ethics/ -v --tb=short")

    # Suite completa
    print("\n5. 🏃 All Tests (Background)")
    os.system("pytest tests/ -v --tb=short --maxfail=10")


if __name__ == "__main__":
    main()
