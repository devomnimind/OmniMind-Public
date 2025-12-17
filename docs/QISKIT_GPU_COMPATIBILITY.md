# 🚨 QISKIT GPU COMPATIBILITY NOTES

**Date**: 2025-12-12
**Status**: CRITICAL - Tested on Ubuntu GTX 1650

## Summary

- **Qiskit 1.4.5 ❌ BREAKS GPU SUPPORT**
- **Qiskit 1.3.x ✅ WORKS WITH GPU**

## Root Cause

Qiskit 1.4.5+ removed `convert_to_target()` method from the API, which breaks compatibility with `qiskit-aer-gpu` 0.15.x.

```
Qiskit 1.3.x: convert_to_target() ✅ exists
Qiskit 1.4.5+: convert_to_target() ❌ removed
Qiskit-Aer-GPU 0.15.x: needs convert_to_target() to work
```

## Test Results

### Ubuntu Setup (Current)
```
Environment: Ubuntu 22.04, GTX 1650 (3.6GB), CUDA 13.0
PyTorch: 2.9.1+cu130 ✅
Qiskit: 1.3.5 (installed manually)
Qiskit-Aer-GPU: 0.15.1
Result: GPU WORKS ✅
```

### What Failed
```
Qiskit 1.4.5 + Qiskit-Aer-GPU 0.15.1:
Error: AttributeError: module 'qiskit' has no attribute 'convert_to_target'
GPU falls back to CPU
```

## Configuration

### Ubuntu GPU Setup (CORRECT)

```bash
# Install correct Qiskit version
pip install 'qiskit>=1.3.0,<2.0.0'
pip install 'qiskit-aer>=0.15.0'
pip install 'qiskit-aer-gpu>=0.15.0'

# Set environment for GPU
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:512"
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=1
export QISKIT_IN_PARALLEL=FALSE
```

### Verify GPU Works

```python
from qiskit_aer import AerSimulator

# Should show: AerSimulator with GPU available
sim = AerSimulator(method='statevector', device='GPU')
print(sim)  # Should say "GPU available"
```

## Requirements Files

All requirements files in `/home/fahbrain/projects/omnimind/requirements/` already specify:
```
qiskit>=1.3.0,<2.0.0  # LTS with GPU support
```

This ensures GPU compatibility across all installations.

## Timeline

| Date | Event |
|------|-------|
| 2025-12-11 | Kali setup used Qiskit 1.3.x (GPU worked) |
| 2025-12-12 | Ubuntu initially tried 1.4.5 (GPU broken) |
| 2025-12-12 | User downgraded to 1.3.x (GPU WORKS) ✅ |
| 2025-12-12 | Documented this incompatibility |

## References

- Qiskit Issue: https://github.com/Qiskit/qiskit/releases/tag/1.4.0
- Qiskit-Aer-GPU: https://github.com/Qiskit/qiskit-aer-gpu
- convert_to_target removal: Part of Qiskit 1.4.0 API refactor

## Action Items

- ✅ Keep Qiskit at 1.3.x in requirements
- ✅ Document this for future maintainers
- ⏳ Monitor Qiskit-Aer-GPU updates for 1.4.5+ support
- ⏳ Test Qiskit 2.x (may require Qiskit-Aer-GPU 0.16+)

---

**Last Updated**: 2025-12-12
**Tested By**: User (Fabrício)
**Environment**: Ubuntu 22.04 + GTX 1650
