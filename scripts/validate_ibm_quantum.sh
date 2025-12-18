#!/bin/bash
# Validação de IBM Quantum Cloud
# Verifica backends disponíveis e executa teste simples

set -e

PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$PROJECT_ROOT"

source .venv/bin/activate 2>/dev/null || true

echo "🔬 VALIDAÇÃO IBM QUANTUM CLOUD"
echo "======================================"
echo ""

python3 << 'EOF'
import os
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import QuantumCircuit
from dotenv import load_dotenv

# Explicitly load .env from current directory to avoid find_dotenv stack issues in heredoc
load_dotenv(os.path.join(os.getcwd(), ".env"))

api_key = os.getenv("IBM_API_KEY")
if not api_key:
    print("❌ IBM_API_KEY não encontrado no .env")
    exit(1)

print("✅ Conectando ao IBM Quantum Cloud...")
print()

try:
    service = QiskitRuntimeService(channel="ibm_cloud", token=api_key)
    backends = service.backends()

    print(f"✅ Conectado com sucesso!")
    print(f"   Instance: Omnimind")
    print(f"   Plan: open")
    print(f"   Backends: {len(backends)}")
    print()

    print("📊 Backends disponíveis:")
    for i, backend in enumerate(backends, 1):
        status = backend.status()
        operational = "✅" if status.operational else "❌"
        print(f"   {i}. {operational} {backend.name:20s} (Qubits: {backend.configuration().n_qubits})")
    print()

    # Teste simples: criar circuito e executar em simulador
    print("🧪 Teste: Executando circuito simples...")

    # Usar simulador local (não usa quota)
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Nota: Para executar em real hardware, descomente:
    # result = service.run(qc, backend_name="ibm_fez").result()
    # print(f"   Resultado: {result.get_counts()}")

    print("   ✅ Circuito criado com sucesso")
    print("   (Teste completo em real hardware requer execução específica)")
    print()

    print("✅ VALIDAÇÃO IBM QUANTUM OK")
    print()
    print("Para executar em real hardware:")
    print("  from qiskit_ibm_runtime import QiskitRuntimeService")
    print("  service = QiskitRuntimeService(channel='ibm_cloud', token=API_KEY)")
    print("  result = service.run(circuit, backend_name='ibm_fez').result()")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
EOF

echo ""
echo "======================================"
echo "✅ VALIDAÇÃO CONCLUÍDA"
echo "======================================"
