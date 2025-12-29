# 🔧 OMNIMIND GPU SERVICES REQUIREMENTS

**Date**: 2025-12-12
**Status**: CRITICAL for GPU testing and operation

## Summary

GPU operations in OmniMind depend on **background services** for:
- Vector embeddings (Qdrant)
- Caching (Redis)
- Message queuing (optional, but recommended)

## Required Services

### 1. Qdrant (Vector Database - MANDATORY)
**Why**: Integration loops need semantic embeddings for consciousness metrics
**Port**: 6333 (HTTP)
**Start**:
```bash
# Option 1: Docker
docker run -p 6333:6333 qdrant/qdrant:latest

# Option 2: Via recovery script
bash scripts/recovery/01_init_qdrant_collections.sh
```

**Check**:
```bash
curl http://localhost:6333/health
```

### 2. Redis (Caching - RECOMMENDED)
**Why**: Accelerates state caching between cycles
**Port**: 6379
**Start**:
```bash
# Option 1: Redis server
redis-server

# Option 2: Docker
docker run -p 6379:6379 redis:7-alpine

# Option 3: systemd (if configured)
sudo systemctl start redis-server
```

**Check**:
```bash
redis-cli ping
# Expected: PONG
```

### 3. Optional: FastAPI Backend
**Why**: Monitoring GPU metrics via dashboard
**Port**: 8000
**Start**:
```bash
bash scripts/recovery/06_increase_daemon_logging.sh
# or
python -m src.main --debug
```

## GPU Test Procedure

### Step 1: Start Services
```bash
# In terminal 1: Start Qdrant
bash scripts/recovery/01_init_qdrant_collections.sh

# In terminal 2: Start Redis (optional but recommended)
redis-server

# In terminal 3: Run GPU test
bash scripts/test_cuda_sync.sh
```

### Step 2: Run GPU Benchmark
```bash
bash scripts/test_cuda_sync.sh
```

**Expected Output**:
```
📊 TEST 1: WITHOUT CUDA_LAUNCH_BLOCKING
  Cycle 1: Φ=0.4521, t=245.3ms
  Cycle 2: Φ=0.4832, t=242.1ms
  ...
✅ Test 1 completed: Avg Φ=0.4643

📊 TEST 2: WITH CUDA_LAUNCH_BLOCKING=1
  Cycle 1: Φ=0.4521, t=312.5ms
  ...
✅ Speedup: 1.28x faster WITHOUT CUDA_LAUNCH_BLOCKING
```

## Integration Loop GPU Dependencies

### What Runs on GPU

1. **Integration Loop Cycles**
   - Location: `src/consciousness/integration_loop.py:execute_cycle_sync()`
   - Uses: PyTorch tensors, Qiskit-Aer GPU simulator
   - Needs: CUDA initialized, GPU memory allocated

2. **Phi Calculation**
   - Location: `src/consciousness/topological_phi.py`
   - Uses: Torch operations on GPU
   - Needs: GPU kernels for integration computation

3. **Quantum Circuits** (if enabled)
   - Location: `src/quantum_consciousness/quantum_backend.py`
   - Uses: Qiskit-Aer-GPU for statevector simulation
   - Needs: CUDA-compatible Qiskit 1.3.x

### What Runs on CPU (Coordination)

1. **Memory Systems**
   - Qdrant queries (network)
   - Redis lookups (network)
   - Narrative reconstruction (CPU-bound)

2. **Control Flow**
   - Orchestrator decisions
   - Logging and monitoring
   - Data marshaling for GPU

## Environment Variables

### GPU-Enabled Setup

```bash
# PyTorch GPU allocation (NEW: use PYTORCH_ALLOC_CONF)
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:512"

# GPU device selection
export CUDA_VISIBLE_DEVICES=0

# Disable dynamic compilation (more stable)
export PYTORCH_DISABLE_DYNAMO=1

# Qiskit serial execution (GTX 1650 limitation)
export QISKIT_IN_PARALLEL=FALSE

# Thread management
export OMP_NUM_THREADS=4
```

### CPU Fallback (if GPU fails)

```bash
# Force CPU-only
export CUDA_VISIBLE_DEVICES=""
# Qiskit CPU backend
export QISKIT_IN_PARALLEL=TRUE
```

## Troubleshooting

### ❌ "CUDA out of memory"
```bash
# Solution 1: Reduce batch size
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"

# Solution 2: Enable sync (older workaround)
export CUDA_LAUNCH_BLOCKING=1

# Solution 3: Use CPU
export CUDA_VISIBLE_DEVICES=""
```

### ❌ "IntegrationLoop not found" or "Cannot import"
```bash
# Make sure PYTHONPATH includes src/
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Verify services:
curl http://localhost:6333/health
redis-cli ping
```

### ❌ "Qiskit convert_to_target error"
```bash
# Wrong Qiskit version installed
pip uninstall qiskit
pip install qiskit==1.3.0
```

### ⚠️ "Warning: PYTORCH_CUDA_ALLOC_CONF deprecated"
```bash
# Update to new name
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:512"
# (remove PYTORCH_CUDA_ALLOC_CONF)
```

## Performance Expectations

### Hardware: Ubuntu GTX 1650 (3.6GB VRAM)

| Test | Time/Cycle | Notes |
|------|-----------|-------|
| WITHOUT CUDA_LAUNCH_BLOCKING | ~240ms | Optimized (GPU parallel) |
| WITH CUDA_LAUNCH_BLOCKING=1 | ~310ms | Sync mode (Kali workaround) |
| CPU-only fallback | ~500ms+ | For debugging |

**Speedup**: ~1.3x faster without synchronization on Ubuntu

## References

- PyTorch CUDA allocation: https://pytorch.org/docs/stable/notes/cuda.html
- Qiskit GPU: https://github.com/Qiskit/qiskit-aer-gpu
- CUDA debugging: `nvidia-smi -l 1` (watch GPU in real-time)

---

**Last Updated**: 2025-12-12
**Tested Environment**: Ubuntu 22.04 + GTX 1650 + CUDA 13.0
**Status**: Production-ready
