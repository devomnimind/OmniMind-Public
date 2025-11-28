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

try:
    import qiskit

    print(f"qiskit: {qiskit.__version__}")
except ImportError as e:
    print(f"qiskit import failed: {e}")

try:
    import qiskit_aer

    print(f"qiskit_aer: {qiskit_aer.__version__}")
except ImportError as e:
    print(f"qiskit_aer import failed: {e}")

try:
    from qiskit import QuantumCircuit

    print("QuantumCircuit imported")
except ImportError as e:
    print(f"QuantumCircuit import failed: {e}")

try:
    from qiskit_aer import AerSimulator

    print("AerSimulator imported")
except ImportError as e:
    print(f"AerSimulator import failed: {e}")

try:
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    print("generate_preset_pass_manager imported")
except ImportError as e:
    print(f"generate_preset_pass_manager import failed: {e}")
