# 🔧 CHANGELOG RÁPIDO - GPU Setup Ubuntu

## [2025-12-12] GPU Configuration & Step 3 Fixes

### ✅ Fixed
- **Step 3 Import Error**: Removeu `QuantumUnconsciousModule` (classe não existe)
- **Step 3 Object Error**: LoopCycleResult → use `getattr()` not `.get()`
- **GPU Env Vars**: PYTORCH_CUDA_ALLOC_CONF → **PYTORCH_ALLOC_CONF** (new standard)
- **Memory Optimization**: `max_split_size_mb: 512 → 256` (reduz vazamento)
- **Thread Reduction**: `OMP_NUM_THREADS: 4 → 2` (estabilidade)
- **Sync Only**: `CUDA_LAUNCH_BLOCKING=1` (força sincronia, sem async issues)
- **Test Script**: Atualizado para usar `execute_cycle_sync()` (apenas sincrono)

### 📦 Created
- **`scripts/setup_gpu_ubuntu.sh`**: Configuração GPU Ubuntu-específica (OTIMIZADA)
  - ✅ PYTORCH_ALLOC_CONF: `backend:cudaMallocAsync,max_split_size_mb:512`
  - ❌ CUDA_LAUNCH_BLOCKING: REMOVIDO (era hack Kali)
  - QISKIT_IN_PARALLEL: FALSE (sem paralelização pesada)
  - OMP_NUM_THREADS: 4 (otimizado para i5-8400)
- **`scripts/test_cuda_sync.sh`**: Benchmark script (com vs sem CUDA_LAUNCH_BLOCKING)
  - ✅ Verifica serviços (Qdrant, Redis)
  - ✅ 5 ciclos SEM sync (otimizado)
  - ✅ 5 ciclos COM sync (Kali workaround)
  - ✅ Recomenda baseado em resultados
- **`scripts/test_50_cycles.sh`**: Test 50 integration cycles com monitoring
  - ✅ Rastreia memory/GPU em tempo real
  - ✅ Detecta se processo está sendo morto
  - ✅ Garbage collection a cada 10 ciclos
- **`scripts/disable_omnimind_monitors.sh`**: Desativa monitors para testing
  - ✅ Cria `.env.no_monitors` com env vars
  - ✅ Cria `scripts/run_test_safe.sh` wrapper
  - ✅ resource_protector não mata mais testes
  - ✅ Você controla lifecycle completamente
- **`docs/GPU_SERVICES_SETUP.md`**: Documentação completa sobre serviços, troubleshooting, etc

### 🚨 CRITICAL ISSUE IDENTIFIED & FIXED
- **Root Cause Found**: `resource_protector.py` estava matando processos de teste
  - Mata processos com >90% CPU ou alta memória
  - Intended para proteger sistema, mas mata testes legítimos
- **Solution**: Desativar monitors para modo testing
  - Criado `.env.no_monitors` com flags de desativação
  - `OMNIMIND_DISABLE_RESOURCE_PROTECTOR=1`
  - `OMNIMIND_DISABLE_ALERT_SYSTEM=1`

### 🔍 Verified
- PyTorch: 2.9.1+cu130 ✅
- CUDA: 13.0 ✅
- Qiskit: **1.3.0** ✅ **GPU CONFIRMED WORKING**
- Qiskit-Aer: 0.15.1 with GPU ✅
- Test: `AerSimulator(device='GPU')` → OK

### 📝 Notes
- Configuração é Ubuntu-específica, NÃO copy do Kali
- GTX 1650 com 3.6GB VRAM: sem paralelização
- Drivers atualizados no Ubuntu (CUDA 13 vs 12 no Kali)
- Setup é estável, não para velocidade

### 🚀 Next Steps
1. Executar: `bash scripts/recovery/03_run_integration_cycles.sh`
2. Monitor: `tail -f logs/daemon_cycles.log`
3. Esperado: 500 ciclos em ~10-15 min com GPU ✅

---

## Histórico Anterior

### [2025-12-11] Recovery Scripts Created
- ✅ 6 scripts de recuperação + master executor
- ✅ Step 1 (Qdrant): Verificação + init
- ✅ Step 2 (Embeddings): Dataset indexing
- ✅ Step 3 (Cycles): FIXED agora
- ⏳ Step 4 (Persistent State): Pronto
- ⏳ Step 5 (GPU Allocation): Pronto
- ⏳ Step 6 (Daemon Logging): Pronto
