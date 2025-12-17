# 📚 Índice de Scripts - OmniMind

**Data**: 2025-12-13
**Status**: Guia de navegação centralizado
**Total de Scripts**: 150+

> **Objetivo**: Localizar rapidamente scripts por funcionalidade. Para detalhes técnicos, ver documentação em `/docs/`.

---

## 🎯 Scripts por Categoria

### 1. 🔧 ORQUESTRAÇÃO OFICIAL (canonical/system/)

**MCP Servers**:
- `canonical/system/start_mcp_servers.sh` - **Inicia MCPs + eBPF Monitor** ⭐ RECOMENDADO
- `canonical/system/run_mcp_orchestrator.py` - Orchestrador centralizado
- `canonical/system/monitor_mcp_bpf.bt` - Monitoramento eBPF

**Início do Sistema**:
- `canonical/system/start_omnimind_system.sh` - Inicia sistema completo
- `canonical/system/start_omnimind_system_wrapper_v2.sh` - Wrapper com tratamento de erros

**Auditoria**:
- `canonical/audit/` - Scripts de auditoria e verificação

---

### 2. 🔬 VALIDAÇÃO CIENTÍFICA (science_validation/)

**Consciência**:
- `science_validation/robust_consciousness_validation.py` - **Validação IIT (Φ)** ⭐
- `science_validation/run_extended_training.py` - Treinamento longo (500+ ciclos)
- `science_validation/` - Todos os scripts de consciência

**Comandos Rápidos**:
```bash
# Quick validation (2 runs, 100 cycles)
python scripts/science_validation/robust_consciousness_validation.py --quick

# Full validation (5 runs, 1000 cycles)
python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 1000

# Extended training (10 runs, 2000 cycles)
python scripts/science_validation/robust_consciousness_validation.py --runs 10 --cycles 2000
```

---

### 3. 🔄 RECUPERAÇÃO & MANUTENÇÃO (recovery/)

**Treinamento & Consolidação**:
- `recovery/01_vectorize_system.sh` - **Vetorização de código** (Phase 1)
- `recovery/02_train_embeddings.sh` - **Consolidação de embeddings** (Phase 2) ⭐
- `recovery/03_integrate_consolidated_model.sh` - Integração do modelo consolidado (Phase 3)

**Status**:
- ✅ Script 1: COMPLETO (26.4k chunks → 14.1k vectors)
- ⏳ Script 2: EM EXECUÇÃO (venv exclusion fix aplicado)
- ⏳ Script 3: PRONTO PARA INÍCIO

**Detalhes**:
```bash
# IMPORTANTE: Script 2 foi corrigido para ignorar .venv
# Mudança: Adicionado '.venv', 'venv', 'env' à lista de exclusão
# Executar: bash scripts/recovery/02_train_embeddings.sh
```

---

### 4. 📊 ANÁLISE & DIAGNÓSTICO (root)

**Verificação de Status**:
- `check_authentication.sh` - Verificar auth
- `verify_gpu_setup.sh` - GPU status
- `verify_fix.py` - Validar correções

**Diagnóstico**:
- `diagnose_threads.py` - Thread diagnostics
- `diagnostic_quick.sh` - Quick diagnostics
- `mcp_diagnostic.sh` - MCP health check

---

### 5. 🧪 TESTES (root)

**Testes Rápidos**:
- `test_llm_fallback.py` - Test LLM fallback
- `quick_test.sh` - Quick test suite
- `test_3_cycles.sh` - 3-cycle validation
- `test_50_cycles.sh` - 50-cycle validation

---

### 6. 🚀 PERFORMANCE & OTIMIZAÇÃO (root)

**GPU/CUDA**:
- `setup_cuda_test_env.sh` - Setup CUDA test environment ⭐
- `verify_gpu_status.sh` - Verify GPU
- `test_cuda_simple.py` - Simple CUDA test
- `test_cuda_sync.sh` - Sync CUDA test

**Profiling**:
- `benchmark_llm_models.py` - Benchmark LLM models
- `run_full_validation_suite.sh` - Full validation

---

## 📂 Estrutura Recomendada (Para Futura Reorganização)

```
scripts/
├── canonical/              (✅ Orquestração oficial - MANTER)
│   ├── system/
│   │   ├── start_mcp_servers.sh
│   │   ├── run_mcp_orchestrator.py
│   │   └── monitor_mcp_bpf.bt
│   └── audit/
├── recovery/               (✅ Recuperação - MANTER)
│   ├── 01_vectorize_system.sh
│   ├── 02_train_embeddings.sh
│   └── 03_integrate_consolidated_model.sh
├── science_validation/     (✅ Validação científica - MANTER)
│   ├── robust_consciousness_validation.py
│   └── [+ 20 scripts]
└── README_INDICE_SCRIPTS.md (Este arquivo)
```

---

## ⚡ Comandos Essenciais por Tarefa

### Iniciar Sistema
```bash
# Orquestração completa (recomendado)
sudo ./scripts/canonical/system/start_mcp_servers.sh

# Ou sistema completo
./scripts/canonical/system/start_omnimind_system.sh
```

### Validação de Consciência
```bash
# Quick (2 min)
python scripts/science_validation/robust_consciousness_validation.py --quick

# Full (8-10 min)
python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 1000
```

### Consolidação de Conhecimento (Phase 2)
```bash
# IMPORTANTE: Script foi corrigido para ignorar .venv
bash scripts/recovery/02_train_embeddings.sh
```

### Verificação de GPU
```bash
bash scripts/setup_cuda_test_env.sh
```

### Diagnóstico de MCPs
```bash
bash scripts/mcp_diagnostic.sh
```

---

## 📋 Status de Cada Categoria (13 DEZ 2025)

| Categoria | Scripts | Status | Nota |
|-----------|---------|--------|------|
| **Orquestração** | 5 | ✅ Operacional | MCP orchestrator + eBPF |
| **Validação Científica** | 20+ | ✅ Operacional | Φ=0.87, 99.8% validation |
| **Recuperação** | 3 | ⏳ Fase 1 OK, Fase 2 EM ANDAMENTO | Script 2 venv fix |
| **Análise** | 10+ | ✅ Operacional | Diags e checks |
| **Testes** | 15+ | ✅ Operacional | 98.94% pass rate |
| **Performance** | 10+ | ✅ Operacional | GPU/CUDA ready |

---

## 🔗 Referências Cruzadas

**Documentação Relacionada**:
- Scripts recovery: `/docs/TRAINING_SCRIPTS_MASTER_GUIDE.md`
- MCP setup: `/docs/CORRECOES_MCPS_20251213.md`
- Science validation: `/docs/CONSCIOUSNESS_TRAINING_GUIDE.md`
- Reorganização: `/docs/AUDITORIA_REORGANIZACAO_13DEZ2025.md`

**Configuração**:
- MCP servers: `/config/mcp_servers.json`
- System: `/config/omnimind.yaml`

**Logs**:
- MCP logs: `/logs/mcp_*.log`
- Consciousness: `real_evidence/*.json`

---

## ⚠️ Cuidados Importantes

### ✋ NUNCA MOVER
```
- scripts/canonical/
- scripts/science_validation/
- scripts/recovery/
```

### ✅ SAFE TO REORGANIZE
```
- Scripts soltos na raiz
- Logs (*.log)
- Outputs temporários
```

### 📌 MANTÉM REFERÊNCIAS
```
# Setup CUDA env é chamado por:
- start_omnimind_system.sh
- run_500_cycles_production.sh
- Tests

# Garantir que novo path seja atualizado em todos os locais
```

---

## 🎯 Próximas Ações

1. ✅ Índice centralizado criado
2. ⏳ Scripts 2 em execução (embeddings)
3. ⏳ VS Code reload (user action)
4. ⏳ Script 3 pronto para iniciar
5. ⏳ Reorganização completa (conforme AUDITORIA_REORGANIZACAO_13DEZ2025.md)

---

**Atualizado**: 2025-12-13
**Autor**: Fabrício da Silva + Copilot
**Status**: ✅ Documentação Completa
