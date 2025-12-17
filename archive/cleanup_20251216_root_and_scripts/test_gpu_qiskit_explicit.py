#!/usr/bin/env python3
"""
🧪 Teste Explícito de GPU - Qiskit 0.17.2

Script para verificar se AerSimulator está usando GPU com device='GPU' explícito.
Útil para diagnóstico de configuração de aceleração CUDA.

Executar com:
    python test_gpu_qiskit_explicit.py

Esperado (com GPU):
    Backend Name: aer_simulator
    Available Devices: ['CPU', 'GPU']  # GPU deve aparecer aqui
    Resultado do Teste GPU: {'00': X, '11': Y}
"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

print("\n" + "=" * 70)
print("🧪 TESTE EXPLÍCITO DE GPU - QISKIT 0.17.2")
print("=" * 70 + "\n")

# 1. Defina o simulador com a configuração explícita de dispositivo
# method='statevector' é o algoritmo
# device='GPU' ativa a aceleração CUDA
print("1️⃣ Criando AerSimulator com device='GPU'...")
sim = AerSimulator(method="statevector", device="GPU")

# Verificação de Sanidade: Confirma se a GPU está sendo usada
print(f"\n📊 Informações do Backend:")
print(f"   Backend Name: {sim.name}")
print(f"   Available Devices: {sim.available_devices()}")

# Verificar se GPU está realmente disponível
if "GPU" in sim.available_devices():
    print("   ✅ GPU DISPONÍVEL PARA USO")
else:
    print("   ⚠️ GPU NÃO DISPONÍVEL - Usando CPU")

# --- Exemplo de Teste Rápido (Bell State) ---
print("\n2️⃣ Criando circuito de teste (Bell State)...")
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

print(f"   Circuito criado com {qc.num_qubits} qubits")

# Transpilação e Execução
print("\n3️⃣ Transpilando e executando...")
try:
    qc_transpiled = transpile(qc, sim)
    result = sim.run(qc_transpiled).result()
    counts = result.get_counts()

    print(f"   ✅ Execução bem-sucedida!")
    print(f"\n📈 Resultado do Teste GPU:")
    print(f"   {counts}")

except Exception as e:
    print(f"   ❌ Erro durante execução: {e}")
    print(f"\n   Tentando fallback para CPU...")
    try:
        sim_cpu = AerSimulator(method="statevector")
        qc_transpiled = transpile(qc, sim_cpu)
        result = sim_cpu.run(qc_transpiled).result()
        counts = result.get_counts()
        print(f"   ✅ CPU fallback bem-sucedido!")
        print(f"\n📈 Resultado do Teste (CPU):")
        print(f"   {counts}")
    except Exception as e2:
        print(f"   ❌ CPU também falhou: {e2}")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70 + "\n")
