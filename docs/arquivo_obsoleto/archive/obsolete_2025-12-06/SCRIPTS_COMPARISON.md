# Comparação de Scripts de Produção

## 📋 Scripts Disponíveis

### 1. `scripts/canonical/system/start_omnimind_system.sh` (ORIGINAL)

**Características**:
- ✅ Script oficial e testado
- ✅ Porta Frontend: **3000** (correto)
- ✅ Inclui Daemon
- ✅ Inclui eBPF Monitor
- ✅ Inicia Backend Cluster completo
- ✅ Verificações de health check

**Ordem de Inicialização**:
1. Limpeza de processos
2. Backend Cluster (run_cluster.sh)
3. Ciclo Principal (src.main)
4. Daemon (via API)
5. Frontend (porta 3000)
6. eBPF Monitor

### 2. `scripts/start_production_phase22.sh` (NOVO - Phase 22)

**Características**:
- ✅ Focado em Phase 22
- ✅ PYTHONPATH configurado
- ✅ Estrutura de diretórios Phase 22
- ❌ Porta Frontend: **5173** (ERRADO - deve ser 3000)
- ❌ Não inclui Daemon
- ❌ Não inclui eBPF Monitor

**Ordem de Inicialização**:
1. Limpeza de processos
2. Criação de diretórios Phase 22
3. Backend (run_cluster.sh)
4. Ciclo Principal (src.main com PYTHONPATH)
5. Frontend (porta 5173 - ERRADO)

## 🔧 Diferenças Principais

| Aspecto | Original | Phase 22 |
|---------|----------|----------|
| **Porta Frontend** | 3000 ✅ | 5173 ❌ |
| **Daemon** | Sim ✅ | Não ❌ |
| **eBPF Monitor** | Sim ✅ | Não ❌ |
| **PYTHONPATH** | Não | Sim ✅ |
| **Estrutura Phase 22** | Não | Sim ✅ |
| **Verificações** | Completas ✅ | Básicas |

## ✅ Recomendação

**Usar o script original** e adicionar as melhorias Phase 22:

```bash
./scripts/canonical/system/start_omnimind_system.sh
```

**Ou** corrigir o script Phase 22 para:
- Usar porta 3000
- Incluir Daemon
- Incluir eBPF Monitor

---

**Status**: Script original é mais completo e testado

