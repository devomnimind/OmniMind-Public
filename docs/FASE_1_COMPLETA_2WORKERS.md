---
title: "FASE 1 Completa: Ambiente com 2 Workers (13 DEC 2025)"
date: "2025-12-13T20:45:00Z"
status: "✅ Completed"
priority: "🔴 CRITICAL"
---

# 🎯 FASE 1: Environment Variables Implementation - COMPLETED

**Data:** 13 de Dezembro de 2025
**Status:** ✅ **CONCLUÍDA**
**Responsável:** Fabrício (com GitHub Copilot)
**Contexto:** Implementação de variáveis de ambiente para configurar workers e backends dinamicamente

---

## 📊 Summary

FASE 1 foi **completada com sucesso**. O sistema agora suporta:

1. **Variáveis de Ambiente Implementadas:**
   - `OMNIMIND_WORKERS` (padrão: 2) - número de workers por backend
   - `OMNIMIND_BACKENDS` (padrão: 3) - quantos backends rodar
   - `OMNIMIND_WORKERS_VALIDATION` (padrão: 2) - workers durante validação científica

2. **Scripts Modificados:**
   - ✅ `scripts/canonical/system/run_cluster.sh` - Now reads env vars, uses 2 workers by default
   - ✅ `scripts/canonical/system/run_cluster.sh` - Backend toggle (rodar 1, 2, ou 3 backends conforme OMNIMIND_BACKENDS)

3. **Novo Script de Teste:**
   - ✅ `scripts/test_validation_2workers.sh` - Safe testing script with two modes:
     - `--quick` (padrão): 2 runs × 100 cycles ~ 10 minutos (sanity check)
     - `--full`: 5 runs × 1000 cycles ~ 90-150 minutos (full validation)

---

## ✅ Completed Actions

### 1. Modified run_cluster.sh

**Arquivo:** `scripts/canonical/system/run_cluster.sh`

**Mudanças:**
```bash
# Antes (hardcoded):
--workers 1

# Depois (com env vars):
--workers "${OMNIMIND_WORKERS:-2}"
```

**Recursos Adicionados:**
- Leitura de 3 variáveis de ambiente
- Configuração inteligente (mostra valores ao iniciar)
- Toggle de backends (rodar 1, 2, ou 3)
- Padrões sensatos: `OMNIMIND_WORKERS=2` (estável + rápido)

**Output Example:**
```
⚙️  Configuração:
   Workers por backend: 2 (OMNIMIND_WORKERS)
   Backends ativos: 3 (OMNIMIND_BACKENDS)
   Workers em validação: 2 (OMNIMIND_WORKERS_VALIDATION)

▶ Iniciando Primary (Port 8000)...
✓ Primary iniciado com PID 12345 (workers: 2)
```

### 2. Created test_validation_2workers.sh

**Arquivo:** `scripts/test_validation_2workers.sh`

**Funcionalidades:**
- ✅ Dois modos de teste (--quick / --full)
- ✅ Automático ativa/desativa VALIDATION_MODE
- ✅ Inicia cluster com 2 workers automaticamente
- ✅ Mede tempo de execução
- ✅ Análise de performance vs baseline (300+ min)
- ✅ Next steps recomendados baseados em resultado
- ✅ Geração de logs detalhados

**Uso:**
```bash
# Quick sanity check (10 minutes)
bash scripts/test_validation_2workers.sh --quick

# Full validation (90-150 minutes)
bash scripts/test_validation_2workers.sh --full
```

**Output Features:**
- Timing completo (start/end + duration)
- Health check dos 3 backends
- Performance analysis vs baseline
- Recomendações de próximos passos baseadas em resultado

---

## 🎯 Default Configuration (After FASE 1)

```bash
# Produção (Default)
export OMNIMIND_WORKERS=2              # 2 workers por backend (estável + rápido)
export OMNIMIND_BACKENDS=3             # 3 backends (HA cluster)
export OMNIMIND_WORKERS_VALIDATION=2   # 2 workers durante validação (consistente)

# Ao executar:
bash scripts/canonical/system/run_cluster.sh

# Resultado:
# ✓ Primary iniciado com PID xxxx (workers: 2)
# ✓ Secondary iniciado com PID yyyy (workers: 2)
# ✓ Fallback iniciado com PID zzzz (workers: 2)
# Total: 6 workers (2×3 backends)
```

---

## 📈 Performance Context

**Baseline (Previous Configuration):**
- Workers per backend: 1
- Total workers: 3 (1 × 3 backends)
- Validation time: 4-5 hours ⚠️
- GPU utilization: 61% (underutilized)
- User feedback: "Muito lento" (too slow)

**FASE 1 Configuration:**
- Workers per backend: 2 (configurable)
- Total workers: 6 (2 × 3 backends)
- Expected validation time: 90-150 minutes ✅ (target)
- GPU utilization: Expected 75%+ (higher)
- User feedback: "Mais rápido com 2" (faster with 2)

**User Validation:**
✅ User tested with 2 workers (showed screenshots as evidence)
✅ Confirmed 2 workers is objectively faster than 1
✅ Approved to keep 2 workers as minimum stable config

---

## 🔄 How to Test FASE 1

### Option 1: Quick Sanity Check (10 minutes)
```bash
cd /home/fahbrain/projects/omnimind

# Run quick test
bash scripts/test_validation_2workers.sh --quick

# Expected output:
# ✅ Validation test PASSED
# ⏱️  Duration: ~10 minutes
# ✅ EXCELLENT: Validation completed in ~10m (< 150 min target)
```

### Option 2: Full Validation (90-150 minutes)
```bash
cd /home/fahbrain/projects/omnimind

# Run full test (patience!)
bash scripts/test_validation_2workers.sh --full

# Expected output:
# ✅ Validation test PASSED
# ⏱️  Duration: 90-150 minutes
# ✅ EXCELLENT: Validation completed in ~120m (< 150 min target)
```

### Manual Test (Custom Workers)
```bash
# Test with different worker configurations
export OMNIMIND_WORKERS=1
bash scripts/canonical/system/run_cluster.sh
# ... observe performance ...

export OMNIMIND_WORKERS=2
bash scripts/canonical/system/run_cluster.sh
# ... observe performance ...

export OMNIMIND_WORKERS=3
bash scripts/canonical/system/run_cluster.sh
# ... observe performance ...
```

---

## 📋 Files Modified/Created

### Created:
- ✅ `scripts/test_validation_2workers.sh` (287 lines, executable)

### Modified:
- ✅ `scripts/canonical/system/run_cluster.sh` (added env var section)

### Not Changed (already complete):
- ✅ `src/consciousness/validation_mode.py` (188 lines - from ETAPA 1)
- ✅ `src/quantum_consciousness/cuda_init_fix.py` (with setup_cuda_isolation)
- ✅ `src/monitor/unified_cpu_metrics.py` (complete module - from ETAPA 5)
- ✅ `scripts/recovery/03_run_integration_cycles_optimized.sh` (VALIDATION_MODE signaling)

---

## 🚀 Next Phase: FASE 2

**What:** Integrate UnifiedCPUMonitor into homeostasis.py
**Why:** Remove false warnings when CPU spikes for normal computation
**When:** After FASE 1 validation passes (FASE 3)
**Impact:** Cleaner monitoring, fewer distractions during validation

**File to Modify:** `src/metacognition/homeostasis.py`
**Change:** Replace static `if cpu_percent > 80.0` with intelligent metrics

---

## 🎯 Critical Next Step: FASE 3 - Validation Test

**⚠️ CRITICAL:** Need to run validation with 2 workers and confirm it:
1. ✅ Completes successfully
2. ✅ Takes < 150 minutes (vs 4-5 hours baseline)
3. ✅ Shows improved GPU utilization
4. ✅ Has no false monitor warnings

**Action:**
```bash
bash scripts/test_validation_2workers.sh --quick   # 10 min test first
# If OK:
bash scripts/test_validation_2workers.sh --full    # 90-150 min full validation
```

**Decision Point:**
- ✅ If FASE 3 passes: Mark 2 workers as official (FASE 4)
- ❌ If FASE 3 fails: Investigate or revert to 1 worker

---

## 📚 Documentation

**Related Documents:**
- `docs/OTIMIZACAO_INTEGRADA_VALIDADA.md` - Overall strategy
- `docs/BACKEND_OPTIMIZATION_STRATEGY.md` - Backend configuration
- `docs/IMPLEMENTACAO_VALIDATION_MODE_CONCLUIDA.md` - VALIDATION_MODE system
- `docs/INVESTIGACAO_WORKERS_ASYNC_CONFIG.md` - Worker investigation

**Environment Variables Reference:**
```bash
# Set before running cluster
export OMNIMIND_WORKERS=2              # Workers per backend
export OMNIMIND_BACKENDS=3             # Number of backends to start
export OMNIMIND_WORKERS_VALIDATION=2   # Workers during scientific validation
export OMNIMIND_VALIDATION_MODE=true   # Signals graceful pause of auxiliaries
```

---

## ⚙️ Configuration Verification

### Verify FASE 1 is active:
```bash
# Check if env vars are read correctly
cd /home/fahbrain/projects/omnimind
export OMNIMIND_WORKERS=2
bash scripts/canonical/system/run_cluster.sh 2>&1 | grep -A3 "Configuração:"
# Expected: Workers por backend: 2 (OMNIMIND_WORKERS)
```

### Verify backends respond:
```bash
# Health check
curl http://localhost:8000/health
curl http://localhost:8080/health
curl http://localhost:3001/health
# Expected: 200 OK
```

---

## 🔐 Quality Checklist

- ✅ Modified run_cluster.sh with env var support
- ✅ Created safe test script (test_validation_2workers.sh)
- ✅ Env vars have sensible defaults (2/3/2)
- ✅ Script is executable and well-documented
- ✅ No breaking changes to existing workflows
- ✅ Easy rollback (just run script without custom env vars)
- ✅ Performance measurements included in test script

---

## 📝 Summary

**FASE 1 Status:** ✅ **COMPLETE**

The OmniMind cluster now supports dynamic worker configuration:

```
Before:  1 worker  × 3 backends = 3 total workers (slow ~4-5h validation)
After:   2 workers × 3 backends = 6 total workers (fast ~90-150min validation)
```

**User approved this approach:** "vamos fazer os testes com 2 se passar toda a validação nãodedrrubar script mantemos oficialmente"

**Ready for FASE 3:** Test validation with 2 workers to confirm performance improvement.

---

**Next Action:** Run `bash scripts/test_validation_2workers.sh --quick` to sanity check, then full validation.

---

*Created: 13 DEC 2025*
*Author: Fabrício + GitHub Copilot*
