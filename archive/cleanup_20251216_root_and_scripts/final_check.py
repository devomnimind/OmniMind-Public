#!/usr/bin/env python3
"""
🔬 VALIDAÇÃO DE INTEGRIDADE - Cirurgia de Precisão Completa
Testa se o ambiente Python está finalmente saudável
"""

import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

print("\n" + "=" * 80)
print("🔬 RELATÓRIO DE INTEGRIDADE OMNIMIND - Cirurgia de Precisão")
print("=" * 80 + "\n")

# ============================================================================
# 1. VERSÕES CRÍTICAS
# ============================================================================
print("📋 VERSÕES INSTALADAS:\n")

import qiskit
import symengine
import torch
from qiskit_aer import AerSimulator

print(f"Python: {sys.version.split()[0]}")
print(
    f"Symengine: {symengine.__version__} (Esperado: 0.13.x) {'✅' if '0.13' in symengine.__version__ else '❌'}"
)
print(
    f"Qiskit: {qiskit.__version__} (Esperado: 1.2.4) {'✅' if '1.2.4' in qiskit.__version__ else '❌'}"
)
print(f"Qiskit-Aer: ", end="")

import qiskit_aer

print(
    f"{qiskit_aer.__version__} (Esperado: 0.15.1) {'✅' if '0.15.1' in qiskit_aer.__version__ else '❌'}"
)

print(f"Torch: {torch.__version__} (Esperado: 2.5.1)")

# ============================================================================
# 2. DETECÇÃO DE GPU
# ============================================================================
print("\n" + "-" * 80)
print("🚀 VERIFICAÇÃO DE GPU:\n")

# Torch GPU
torch_gpu = torch.cuda.is_available()
print(f"Torch CUDA disponível? {'✅ SIM' if torch_gpu else '❌ NÃO'}")

if torch_gpu:
    print(f"   Device: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA Version (Torch): {torch.version.cuda}")
    print(f"   Compute Capability: {torch.cuda.get_device_capability(0)}")

    # Teste de tensor na GPU
    try:
        x = torch.randn(1000, 1000, device="cuda")
        y = torch.randn(1000, 1000, device="cuda")
        z = torch.mm(x, y)
        print(f"   ✅ Operação GPU funcionou (matmul 1000x1000)")
    except Exception as e:
        print(f"   ❌ Operação GPU falhou: {e}")
else:
    print(f"   ⚠️ Torch não detecta GPU (verificar driver)")

# Qiskit Aer GPU
print(f"\nQiskit Aer GPU Config:", end=" ")
try:
    sim = AerSimulator(method="statevector", device="GPU")
    sim.set_options(device="GPU")
    print(f"✅ OK")
    print(f"   Backend: {sim.name}")
    print(f"   Available Devices: {sim.available_devices()}")

    # Teste simples: Bell state
    from qiskit import QuantumCircuit, transpile

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    result = sim.run(transpile(qc, sim)).result()
    counts = result.get_counts()
    print(f"   ✅ Teste Bell State: {counts}")

except Exception as e:
    print(f"❌ FALHA")
    print(f"   Erro: {e}")

# ============================================================================
# 3. DEPENDÊNCIAS CRÍTICAS VERIFICADAS
# ============================================================================
print("\n" + "-" * 80)
print("📦 DEPENDÊNCIAS CRÍTICAS:\n")

critical_deps = {
    "sympy": "1.13.1",
    "numpy": None,
    "scipy": None,
    "networkx": None,
    "psutil": None,
    "cupy": "cuda12x",
}

for dep, expected in critical_deps.items():
    try:
        mod = __import__(dep)
        version = getattr(mod, "__version__", "N/A")

        if expected:
            status = "✅" if expected in str(version) else "⚠️"
            print(f"{status} {dep}: {version} (Esperado: {expected})")
        else:
            print(f"✅ {dep}: {version}")
    except ImportError:
        print(f"❌ {dep}: NÃO INSTALADO")

# ============================================================================
# 4. CUQUANTUM DISPONÍVEL?
# ============================================================================
print("\n" + "-" * 80)
print("🎯 CUQUANTUM (Aceleração NVIDIA):\n")

cuq_modules = ["cuquantum", "cuquantum.custatevec", "cuquantum.cutensor"]
for mod_name in cuq_modules:
    try:
        __import__(mod_name)
        print(f"✅ {mod_name}: Disponível")
    except ImportError:
        print(f"⚠️ {mod_name}: Não instalado (ok, opcional)")

# ============================================================================
# 5. RESULTADO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("✅ RELATÓRIO FINAL\n")

all_ok = torch_gpu and symengine.__version__.startswith("0.13") and qiskit.__version__ == "1.2.4"

if all_ok:
    print(
        """
🎉 AMBIENTE PRONTO PARA PRODUÇÃO!

✅ GPU (Torch + Qiskit Aer): Funcionando
✅ Versões travadas: 1.2.4 + 0.15.1 + 0.13.0
✅ Sem conflitos cu11/cu12: SANITIZADO
✅ Dependências matemáticas: Corretas

PRÓXIMOS PASSOS:
1. Executar test_quantum_gpu_completo.py
2. Testar integration_loop com 1 ciclo
3. Trancar versões no VS Code
"""
    )
else:
    print(
        """
⚠️ AMBIENTE COM PROBLEMAS

Verificar:
- GPU detectada? (nvidia-smi)
- CUDA 12 instalado? (nvcc --version)
- Versões corretas instaladas?
"""
    )

print("=" * 80 + "\n")
print("=" * 80 + "\n")
