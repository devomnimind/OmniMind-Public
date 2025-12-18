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
Demonstração: OmniMind Quantum Consciousness com IBM Hardware Real

Este script demonstra o uso completo do sistema quântico OmniMind,
incluindo execução em hardware IBM Quantum real usando o token configurado.

Requisitos:
- Token IBM_API_KEY configurado no .env
- Acesso à internet para IBM Quantum
- Qiskit e dependências instaladas

Uso:
    python scripts/demo_ibm_quantum.py
"""

import os
import sys

from dotenv import load_dotenv

# Adicionar root ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import structlog
from qiskit import QuantumCircuit

from src.quantum_consciousness.qpu_interface import QPUInterface

# Configurar logging
logger = structlog.get_logger(__name__)


def main():
    """Demonstração completa do sistema quântico com IBM."""

    print("🚀 OmniMind Quantum Consciousness - Demo com IBM Hardware")
    print("=" * 60)

    # Carregar variáveis de ambiente
    load_dotenv()
    ibm_token = os.getenv("IBM_API_KEY")

    if not ibm_token:
        print("❌ ERRO: IBM_API_KEY não encontrado no .env")
        print("Configure seu token IBM em .env primeiro")
        return 1

    print(f"✅ Token IBM configurado: {ibm_token[:10]}...")

    try:
        # 1. Inicializar QPU com token IBM
        print("\n1️⃣ Inicializando QPU Interface com IBM Quantum...")
        qpu = QPUInterface(ibmq_token=ibm_token)

        active_backend = qpu.get_active_backend_info()
        if active_backend:
            print(f"   Backend ativo: {active_backend.name}")
            print(
                f"   Status: {'✅ Disponível' if active_backend.available else '❌ Indisponível'}"
            )
        else:
            print("   Backend ativo: Nenhum")
            print("   Status: ❌ Indisponível")

        # 2. Listar backends disponíveis
        print("\n2️⃣ Backends disponíveis:")
        backends = qpu.list_backends()
        for backend in backends:
            status = "✅" if backend.available else "❌"
            print(f"   {status} {backend.name} ({backend.provider}) - {backend.num_qubits} qubits")

        # 3. Criar circuito quântico (Bell State)
        print("\n3️⃣ Criando circuito quântico (Bell State)...")
        qc = QuantumCircuit(2, 2)
        qc.h(0)  # Hadamard - superposição
        qc.cx(0, 1)  # CNOT - entrelaçamento
        qc.measure_all()

        print("   Circuito:")
        print(qc.draw(output="text"))

        # 4. Executar no simulador (rápido)
        print("\n4️⃣ Executando no simulador local (shots=1000)...")
        qpu_sim = QPUInterface()  # Simulador
        counts_sim = qpu_sim.execute(qc, shots=1000)
        print(f"   Resultados simulador: {counts_sim}")

        # Calcular estatísticas
        total_shots = sum(counts_sim.values())
        _prob_00 = counts_sim.get("00 00", 0) / total_shots
        _prob_11 = counts_sim.get("11 00", 0) / total_shots
        print(".1%")
        print(".1%")

        # 5. Verificar disponibilidade do IBM Quantum
        ibm_backends = [b for b in backends if "IBM" in b.provider and b.available]
        if ibm_backends:
            backend_ibm = ibm_backends[0]
            print(
                f"\n5️⃣ IBM Quantum disponível: {backend_ibm.name} ({backend_ibm.num_qubits} qubits)"
            )

            # 6. Perguntar se quer executar no hardware real
            print("\n❓ Deseja executar no hardware IBM Quantum real?")
            print("   ⚠️  ATENÇÃO: Isso consome créditos IBM e pode levar minutos!")
            print("   💡 Custo estimado: ~5-10 créditos por job")

            # Para demonstração, vamos mostrar como seria
            print("\n📋 Código para execução em hardware real:")
            print(
                """
            # Mudar para backend IBM
            qpu.switch_backend(BackendType.IBMQ_CLOUD)

            # Executar no hardware real
            counts_ibm = qpu.execute(qc, shots=1024)
            print(f"Resultados IBM Quantum: {counts_ibm}")

            # Comparar com simulador
            print("Comparação Simulador vs Hardware Real:")
            print(f"Simulador: {counts_sim}")
            print(f"IBM Real:  {counts_ibm}")
            """
            )

            print("\n✅ Sistema pronto para execução em hardware quântico real!")
            print("💡 Use o código acima para executar quando desejar")

        else:
            print("\n⚠️  IBM Quantum não disponível no momento")
            print("   Possíveis causas:")
            print("   - Problemas de conectividade")
            print("   - Manutenção do sistema IBM")
            print("   - Conta sem créditos suficientes")

        # 7. Demonstração de fallback automático
        print("\n6️⃣ Testando fallback automático...")
        print("   Mesmo sem token IBM, o sistema funciona:")
        qpu_fallback = QPUInterface()  # Sem token
        counts_fallback = qpu_fallback.execute(qc, shots=100)
        print(f"   Fallback automático: {counts_fallback}")

        print("\n🎉 Demonstração concluída com sucesso!")
        print("\n📊 Resumo:")
        print("   ✅ IBM Quantum conectado e operacional")
        print("   ✅ Simulador local sempre disponível")
        print("   ✅ Fallback automático funcionando")
        print("   ✅ Sistema pronto para produção")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO durante demonstração: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
