#!/usr/bin/env python3
"""
Teste Rápido: API IBM Quantum Corrigida

Testa se a correção da API IBM Quantum está funcionando.
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar root ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.quantum_consciousness.qpu_interface import QPUInterface, BackendType
from qiskit import QuantumCircuit

def test_ibm_api_fixed():
    """Testa a API IBM corrigida."""

    print("🔧 Teste: API IBM Quantum Corrigida")
    print("=" * 40)

    # Carregar token
    load_dotenv()
    ibm_token = os.getenv('IBM_API_KEY')

    if not ibm_token:
        print("❌ ERRO: IBM_API_KEY não encontrado")
        return False

    print(f"✅ Token: {ibm_token[:10]}...")

    try:
        # Inicializar QPU com IBM
        print("\n1️⃣ Inicializando QPU Interface...")
        qpu = QPUInterface(ibmq_token=ibm_token)

        backends = qpu.list_backends()
        print(f"   Backends disponíveis: {len(backends)}")
        for b in backends:
            print(f"   - {b.name} ({b.backend_type.value}) - {'✅' if b.available else '❌'}")

        # Tentar usar IBM
        if BackendType.IBMQ_CLOUD in [b.backend_type for b in backends]:
            print("\n2️⃣ Testando switch para IBM...")
            success = qpu.switch_backend(BackendType.IBMQ_CLOUD)
            if success:
                print("✅ Switch para IBM realizado")

                # Criar circuito simples
                qc = QuantumCircuit(1, 1)
                qc.h(0)
                qc.measure(0, 0)

                print("\n3️⃣ Executando circuito simples...")
                counts = qpu.execute(qc, shots=10)
                print(f"✅ Resultado: {counts}")

                return True
            else:
                print("❌ Falha no switch para IBM")
                return False
        else:
            print("❌ Backend IBM não disponível")
            return False

    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ibm_api_fixed()
    print(f"\nResultado: {'✅ SUCESSO' if success else '❌ FALHA'}")
    sys.exit(0 if success else 1)