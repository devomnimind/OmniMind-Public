#!/usr/bin/env python3
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

print("\n" + "="*80)
print("🔧 TESTE: Qiskit-aer 0.15.1 GPU")
print("="*80 + "\n")

import subprocess
result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], 
                       capture_output=True, text=True)
print(f"GPU (nvidia-smi): {result.stdout.strip()}")

import torch
print(f"Torch CUDA: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0)}")

try:
    import cupy as cp
    print(f"CuPy: OK ({cp.cuda.memory.get_device_memory_info()[0] / 1024**3:.2f} GB)")
except:
    print(f"CuPy: Não disponível")

print("\n" + "-"*80)
print("Testando Qiskit-aer 0.15.1:\n")

from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, transpile

try:
    sim = AerSimulator(method='statevector', device='GPU')
    print(f"Backend: {sim.name}")
    print(f"Devices: {sim.available_devices()}")
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    
    result = sim.run(transpile(qc, sim), shots=100).result()
    counts = result.get_counts()
    print(f"✅ RESULTADO: {counts}")
except Exception as e:
    print(f"❌ ERRO: {e}")

print("\n" + "="*80 + "\n")
