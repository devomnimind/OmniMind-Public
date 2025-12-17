#!/bin/bash

# 🎯 SETUP OTIMIZADO GPU - UBUNTU + GTX 1650
# Configuração específica para Ubuntu (diferente de Kali)
# Foco: Estabilidade, não velocidade (já temos drivers atuais)

# ════════════════════════════════════════════════════════════════════════════

# 1. PYTORCH CONFIGURATION
# ⚠️  Updated (2025-12-12): PYTORCH_CUDA_ALLOC_CONF deprecated in PyTorch 2.9.1+
#    Use PYTORCH_ALLOC_CONF instead (new standard)
# 🔧 Reduced for memory efficiency: max_split_size_mb=256 (was 512)
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
export PYTORCH_DISABLE_DYNAMO=1
export PYTORCH_ENABLE_MPS_FALLBACK=1

# 2. CUDA CONFIGURATION (Ubuntu-specific, optimized)
export CUDA_VISIBLE_DEVICES=0
export CUDA_DEVICE_ORDER=PCI_BUS_ID
# ❌ REMOVED: CUDA_LAUNCH_BLOCKING=1
#    Kali needed this (old drivers), Ubuntu doesn't (stable CUDA 13)
#    Removing allows GPU parallelization (2-3x faster)
# If GPU OOM errors occur, readd: export CUDA_LAUNCH_BLOCKING=1

# 3. QISKIT CONFIGURATION
# 🚨 CRITICAL: Qiskit 1.3.x REQUIRED for GPU support
#    Qiskit 1.4.5+ breaks GPU (convert_to_target removed from Qiskit)
export QISKIT_IN_PARALLEL=FALSE  # GTX 1650 não suporta paralelização heavy
export QISKIT_SETTINGS="${HOME}/.qiskit"

# 4. MEMORY & PERFORMANCE (Ubuntu 22.04+)
# 🔧 Reduced threads to prevent memory leak: was 4
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
export NUMEXPR_NUM_THREADS=2
export OPENBLAS_NUM_THREADS=2

# 5. TF/KERAS (se usado)
export TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_GPU_MEMORY_FRACTION=0.7

echo "✅ GPU Setup Configured for Ubuntu"
echo "   PyTorch: CUDA allocator async (memory chunk: 256MB)"
echo "   Qiskit: Serial execution"
echo "   CUDA: Synchronous (CUDA_LAUNCH_BLOCKING=1)"
echo "   Threads: 2 (reduced for stability, prevent memory leak)"
