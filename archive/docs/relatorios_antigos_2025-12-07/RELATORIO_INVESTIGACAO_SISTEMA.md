# 📊 RELATÓRIO DE INVESTIGAÇÃO E CORREÇÕES - OmniMind

**Data**: 2025-12-06
**Autor**: Fabrício da Silva + assistência de IA
**Tipo**: Investigação Completa de Problemas Críticos

---

## 📋 RESUMO EXECUTIVO

### Problemas Identificados e Corrigidos

1. ✅ **Monitor Agressivo** - CORRIGIDO
   - Problema: Monitor matava processos uvicorn próprios do sistema
   - Correção: Proteção expandida para processos OmniMind, threshold aumentado de 50% para 80% CPU

2. ⚠️ **Sistema de Alerts Duplicado** - IDENTIFICADO
   - Dois sistemas: `logs/alerts/alerts.jsonl` (AlertingSystem) e `data/alerts/` (AlertSystem)
   - Necessário: Conciliação e unificação

3. ⚠️ **Módulos Vazios** - VERIFICADO
   - `integrity/`, `intelligence/`, `knowledge/` existem mas estão vazios
   - Status: Normal - são stubs para futura implementação

4. ⚠️ **Relatórios Não Automáticos** - IDENTIFICADO
   - Relatórios são gerados apenas quando scripts específicos são executados
   - Sistema não gera relatórios automaticamente durante execução

5. ✅ **Serviços no start_omnimind_system.sh** - VERIFICADO
   - Todos os serviços principais são iniciados corretamente
   - ObserverService não está sendo iniciado automaticamente

---

## 🔧 1. CORREÇÃO DO MONITOR AGRESSIVO

### Problema
O `ResourceProtector` estava matando processos uvicorn do próprio sistema quando a CPU ultrapassava 50%.

### Correções Aplicadas

**Arquivo**: `src/monitor/resource_protector.py`

1. **Proteção Expandida de Processos OmniMind**:
   - Adicionada lista de padrões protegidos:
     - `web.backend.main`
     - `uvicorn`
     - `omnimind`
     - `src.main`
     - `run_cluster`
     - `mcp_orchestrator`
     - `main_cycle`
     - `daemon`
     - `observer_service`

2. **Threshold Aumentado**:
   - CPU threshold aumentado de 50% para 80%
   - Processos só são considerados para terminação se CPU > 90% (antes era > 80%)

3. **Proteção Adicional em `_handle_cpu_overload`**:
   - Verificação adicional para processos uvicorn/omnimind
   - Redução de prioridade (nice 19) em vez de terminação
   - `continue` explícito para nunca matar processos protegidos

### Código Modificado

```python
# Antes: Ignorava apenas "web.backend.main"
if cmdline and any("web.backend.main" in str(arg) for arg in cmdline):
    continue

# Depois: Lista expandida de padrões protegidos
protected_patterns = [
    "web.backend.main", "uvicorn", "omnimind", "src.main",
    "run_cluster", "mcp_orchestrator", "main_cycle", "daemon", "observer_service"
]
if any(pattern.lower() in cmdline_str.lower() for pattern in protected_patterns):
    continue
```

---

## 📊 2. SISTEMA DE ALERTS DUPLICADO

### Problema Identificado

Existem **dois sistemas de alerts** diferentes:

1. **`src/audit/alerting_system.py`**:
   - Salva em: `logs/alerts/alerts.jsonl` (via `ImmutableAuditSystem.log_dir`)
   - Usado por: Sistema de auditoria

2. **`src/monitor/alert_system.py`**:
   - Salva em: `data/alerts/` (arquivos individuais JSON)
   - Usado por: Sistema de monitoramento

### Análise

- **`logs/alerts/alerts.jsonl`**: 1 arquivo (sistema de auditoria)
- **`data/alerts/`**: 54 arquivos JSON individuais + `alerts_index.json` (sistema de monitoramento)

### Recomendação

**Opção 1: Unificar em um único sistema**
- Manter apenas `AlertingSystem` (auditoria)
- Migrar `AlertSystem` para usar o mesmo sistema

**Opção 2: Manter separados mas sincronizar**
- `AlertingSystem` para auditoria/compliance
- `AlertSystem` para monitoramento/performance
- Criar bridge para sincronização

**Ação Imediata**: Documentar a diferença e criar script de conciliação.

---

## 📁 3. MÓDULOS VAZIOS (integrity/, intelligence/, knowledge/)

### Status

Os módulos existem mas estão **vazios** (apenas `__pycache__/`):

```
src/integrity/     - Vazio
src/intelligence/  - Vazio
src/knowledge/     - Vazio
```

### Investigação

- **Nenhuma referência** encontrada no código para importação/uso destes módulos
- **Não são inicializados** no boot sequence
- **Não aparecem** na lista de módulos conhecidos do `RealModuleActivityTracker`

### Conclusão

Estes módulos são **stubs** para futura implementação. Não há problema - eles simplesmente não foram implementados ainda.

### Recomendação

1. Criar `__init__.py` com docstring explicando propósito futuro
2. Adicionar à lista de pendências se houver plano de implementação
3. Ou remover se não houver plano

---

## 📈 4. RELATÓRIOS NÃO AUTOMÁTICOS

### Problema

O sistema está rodando há semanas mas **não gera relatórios automaticamente** durante a execução.

### Análise de Geração de Dados

**Dados sendo gerados**:
- ✅ `data/monitor/consciousness_metrics/` - Φ, Ψ, σ (corrigido)
- ✅ `data/consciousness/snapshots.jsonl` - 31 snapshots
- ✅ `data/autopoietic/` - Ciclos e narrativas
- ✅ `data/metrics/history.jsonl` - 175.980 linhas (14.9 MB)
- ✅ `data/alerts/` - 54 alerts

**Relatórios NÃO sendo gerados automaticamente**:
- ❌ `data/reports/modules/` - Vazio (deveria ter relatórios por módulo)
- ❌ `data/reports/` - Apenas 3 relatórios antigos (30/11)
- ❌ `logs/monitor_report.json` - Não atualizado há 5 dias

### Causa Raiz

1. **`ModuleReporter`** existe mas não é chamado automaticamente
2. **`ObserverService`** não está sendo iniciado no `start_omnimind_system.sh`
3. **Relatórios são gerados apenas por scripts manuais**:
   - `scripts/data/reports/data_generation_audit.py`
   - `scripts/metrics/collect_baseline_metrics.py`
   - `scripts/science_validation/generate_persistent_reports.py`

### Correções Necessárias

1. **Iniciar ObserverService automaticamente**:
   - Adicionar ao `start_omnimind_system.sh`
   - Ou integrar no ciclo principal (`src/main.py`)

2. **Chamar ModuleReporter periodicamente**:
   - Integrar no `IntegrationLoop`
   - Ou criar task assíncrona no backend

3. **Atualizar monitor_report.json**:
   - Verificar por que não está sendo atualizado
   - Integrar com `DashboardMetricsAggregator`

---

## 🚀 5. SERVIÇOS NO start_omnimind_system.sh

### Serviços Iniciados

✅ **Backend Cluster** (via `run_cluster.sh`):
- Portas: 8000, 8080, 3001
- Uvicorn + Orchestrator + SecurityAgent

✅ **MCP Orchestrator**:
- `run_mcp_orchestrator.py`
- Log: `logs/mcp_orchestrator.log`

✅ **Ciclo Principal**:
- `python -m src.main`
- Log: `logs/main_cycle.log`

✅ **Daemon**:
- Via API: `POST /daemon/start`
- Log: `logs/daemon_start.log`

✅ **Frontend**:
- `npm run dev`
- Porta: 3000
- Log: `logs/frontend.log`

✅ **eBPF Monitor**:
- `bpftrace scripts/monitor_mcp_bpf.bt`
- Log: `logs/ebpf_monitor.log`

### Serviços NÃO Iniciados Automaticamente

❌ **ObserverService**:
- Existe em `src/services/observer_service.py`
- Deveria gerar `data/long_term_logs/omnimind_metrics.jsonl`
- **Ação**: Adicionar ao `start_omnimind_system.sh`

---

## 📋 6. PLANO DE AÇÃO

### Correções Imediatas (Próximas 24h)

1. ✅ **Monitor Agressivo** - JÁ CORRIGIDO
2. ⏳ **Adicionar ObserverService ao start_omnimind_system.sh**
3. ⏳ **Criar script de conciliação de alerts**
4. ⏳ **Documentar diferença entre sistemas de alerts**

### Correções de Curto Prazo (Próxima Semana)

1. **Integrar ModuleReporter no ciclo principal**
2. **Atualizar monitor_report.json automaticamente**
3. **Criar task assíncrona para relatórios periódicos**

### Melhorias de Médio Prazo (Próximas 2-4 semanas)

1. **Unificar sistemas de alerts** (ou criar bridge)
2. **Implementar ou remover módulos stubs** (integrity/intelligence/knowledge)
3. **Sistema de relatórios automáticos** com agendamento

---

## 📊 7. ESTATÍSTICAS CONSOLIDADAS

### Dados Sendo Gerados

| Localização | Arquivos | Tamanho | Status |
|-------------|----------|---------|--------|
| `data/monitor/consciousness_metrics/` | 3 | 0.04 MB | ✅ Ativo (corrigido) |
| `data/consciousness/` | 6 | 0.02 MB | ✅ Ativo |
| `data/autopoietic/` | 3 | 0.01 MB | ✅ Ativo |
| `data/metrics/` | 5 | 14.26 MB | ✅ Ativo |
| `data/alerts/` | 54 | 0.03 MB | ✅ Ativo |
| `logs/alerts/` | 1 | - | ✅ Ativo |
| `data/reports/` | 3 | 1.34 MB | ⚠️ Desatualizado |
| `data/long_term_logs/omnimind_metrics.jsonl` | 0 | - | ❌ Não gerado |

### Relatórios

- **Relatórios automáticos**: ❌ Não implementado
- **Relatórios manuais**: ✅ 3 relatórios (30/11)
- **Monitor report**: ⚠️ Não atualizado há 5 dias

---

## ✅ CONCLUSÃO

### Problemas Resolvidos

1. ✅ Monitor agressivo corrigido - não mata mais processos uvicorn próprios
2. ✅ Persistência de Ψ e σ corrigida - arquivos sendo gerados

### Problemas Identificados (Requerem Ação)

1. ⚠️ Sistema de alerts duplicado - necessita conciliação
2. ⚠️ ObserverService não iniciado automaticamente
3. ⚠️ Relatórios não gerados automaticamente
4. ⚠️ monitor_report.json não atualizado

### Próximos Passos

1. Adicionar ObserverService ao start_omnimind_system.sh
2. Integrar ModuleReporter no ciclo principal
3. Criar script de conciliação de alerts
4. Implementar geração automática de relatórios

---

**Última Atualização**: 2025-12-06
**Status**: 🔧 Correções aplicadas, investigação completa

