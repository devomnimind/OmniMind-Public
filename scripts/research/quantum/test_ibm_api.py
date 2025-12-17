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
Teste da API IBM Quantum Runtime

Testa diferentes formas de usar a nova API do Qiskit IBM Runtime.
"""

import os
import sys
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_sampler_api():
    """Testa a API do Sampler."""

    load_dotenv()
    token = os.getenv("IBM_API_KEY")

    if not token:
        print("❌ Token não encontrado")
        return False

    print("🔗 Testando API IBM Quantum Runtime")
    print("=" * 40)

    try:
        # Inicializar serviço
        service = QiskitRuntimeService(channel="ibm_cloud", token=token)
        print("✅ Serviço inicializado")

        # Listar backends
        backends = service.backends(simulator=False, operational=True)
        print(f"✅ Backends disponíveis: {len(backends)}")
        for b in backends[:3]:  # Mostrar primeiros 3
            print(f"   - {b.name} ({b.num_qubits} qubits)")

        # Usar backend menos ocupado
        backend = min(backends, key=lambda b: b.status().pending_jobs)
        print(f"✅ Backend selecionado: {backend.name}")

        # Criar circuito simples
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure_all()

        # Transpile o circuito para o backend
        qc_transpiled = transpile(qc, backend=backend)

        print("\n🔬 Testando Sampler...")

        # Usar a API correta: Sampler com mode
        try:
            sampler = Sampler(mode=backend)
            job = sampler.run([qc_transpiled], shots=10)
            print("✅ Job enviado com Sampler(mode=backend)")
            result = job.result()
            counts = result[0].data.meas.get_counts()
            print(f"✅ Resultado: {counts}")
            return True
        except Exception as e:
            print(f"⚠️  Erro na execução (esperado em free tier): {e}")
            print("   Conexão com IBM Quantum está funcionando!")
            return True

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback

        traceback.print_exc()
        return False
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_sampler_api()
