#!/usr/bin/env python3
"""
Teste de Conexão IBM Quantum

Verifica se a conexão com IBM Quantum está funcionando corretamente
e testa a execução de um circuito simples no hardware real.
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

def test_ibm_connection():
    """Testa conexão básica com IBM Quantum."""

    print("🔗 Teste de Conexão IBM Quantum")
    print("=" * 40)

    # Carregar token
    load_dotenv()
    ibm_token = os.getenv('IBM_API_KEY')

    if not ibm_token:
        print("❌ ERRO: IBM_API_KEY não encontrado")
        return False

    print(f"✅ Token encontrado: {ibm_token[:10]}...")

    try:
        # Testar inicialização
        print("\n1️⃣ Inicializando QPU Interface...")
        qpu = QPUInterface(ibmq_token=ibm_token)

        backends = qpu.list_backends()
        print(f"   Backends disponíveis: {len(backends)}")
        for backend in backends:
            print(f"   - {backend.name} ({backend.backend_type.value}) - {'Disponível' if backend.available else 'Indisponível'}")

        active = qpu.get_active_backend_info()
        print(f"   Backend ativo: {active.name if active else 'Nenhum'}")

        # Testar execução simples
        print("\n2️⃣ Testando execução simples...")
        qc = QuantumCircuit(1, 1)
        qc.h(0)  # Hadamard
        qc.measure_all()

        print("   Executando no backend ativo...")
        counts = qpu.execute(qc, shots=10)  # Poucos shots para teste rápido
        print(f"   Resultados: {counts}")

        # Verificar se é hardware real ou simulador
        is_real_hardware = active and "ibm" in active.name.lower() and "simulator" not in active.name.lower()
        print(f"   Hardware real: {'Sim' if is_real_hardware else 'Não'}")

        if is_real_hardware:
            print("✅ Conexão IBM Quantum funcionando!")
            return True
        else:
            print("⚠️  Usando simulador - verificar configuração IBM")
            return False

    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ibm_connection()
    sys.exit(0 if success else 1)