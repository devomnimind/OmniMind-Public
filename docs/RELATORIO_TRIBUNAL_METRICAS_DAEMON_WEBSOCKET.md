# 🔍 Relatório: Tribunal, Métricas e Daemon/WebSocket

**Data**: 2025-12-10
**Autor**: Fabrício da Silva + assistência de IA
**Status**: 🔴 Problemas Identificados

---

## 📋 Sumário Executivo

### Problemas Identificados

1. **❌ Tribunal não está sendo executado**
   - Relatório `tribunal_final_report.json` não existe
   - Tribunal nunca foi iniciado ou falhou silenciosamente
   - Métricas não estão sendo coletadas

2. **❌ Métricas não estão sendo salvas permanentemente**
   - Tribunal só salva relatório ao finalizar execução completa
   - Não há salvamento periódico de métricas intermediárias
   - Cache do daemon_monitor não persiste métricas do Tribunal

3. **✅ Daemon e WebSocket são compatíveis**
   - Ambos são iniciados em paralelo sem conflito
   - Daemon Monitor roda em background loop (refresh 5s)
   - WebSocket Manager roda em fast_startup_tasks
   - Não há incompatibilidade técnica

---

## 🔍 Investigação Detalhada

### 1. Tribunal - Relatório Permanente

#### Estado Atual
- **Arquivo esperado**: `data/long_term_logs/tribunal_final_report.json`
- **Status**: ❌ Não existe
- **Último log**: `tribunal_intense.log` (2 dez, 255 bytes)

#### Código de Salvamento
```python
# src/tribunal_do_diabo/executor.py:62-65
with open("data/long_term_logs/tribunal_final_report.json", "w") as f:
    json.dump(report, f, indent=2)
logger.info("Report saved to data/long_term_logs/tribunal_final_report.json")
```

#### Problema
- Tribunal só salva relatório **após completar execução completa** (`await run()`)
- Se Tribunal nunca foi iniciado ou foi interrompido, relatório não é gerado
- Não há salvamento periódico de métricas intermediárias

#### Solução Proposta
1. ✅ Adicionar salvamento periódico de métricas (a cada ciclo de ataque)
2. ✅ Criar endpoint para iniciar Tribunal via API
3. ✅ Adicionar salvamento de estado intermediário

### 2. Métricas Não Estão Sendo Salvas

#### Estado Atual
- **Cache em memória**: `daemon_monitor.STATUS_CACHE`
- **Cache em disco**: `data/long_term_logs/daemon_status_cache.json`
- **Relatório Tribunal**: Não existe

#### Problema
- `daemon_monitor` salva cache geral, mas não métricas específicas do Tribunal
- Tribunal só salva ao finalizar execução completa
- Não há histórico de métricas intermediárias

#### Solução Proposta
1. ✅ Adicionar salvamento periódico de métricas do Tribunal
2. ✅ Criar histórico de métricas por ciclo de ataque
3. ✅ Integrar salvamento com `daemon_monitor`

### 3. Daemon vs WebSocket - Compatibilidade

#### Estado Atual
- **Daemon Monitor**: Iniciado em `medium_startup_tasks` (linha 383)
- **WebSocket Manager**: Iniciado em `fast_startup_tasks` (linha 264)
- **Conflito**: ❌ Nenhum

#### Análise de Código
```python
# web/backend/main.py:255-264 (WebSocket)
async def _start_ws_manager():
    try:
        await asyncio.wait_for(ws_manager.start(), timeout=3.0)
    except asyncio.TimeoutError:
        logger.warning("WebSocket manager startup timed out")
    except Exception as e:
        logger.warning(f"Failed to start WebSocket manager: {e}")

fast_startup_tasks.append(asyncio.create_task(_start_ws_manager()))

# web/backend/main.py:370-383 (Daemon Monitor)
async def _start_daemon_monitor():
    if daemon_monitor_loop is not None:
        try:
            daemon_monitor_task = asyncio.create_task(
                asyncio.wait_for(daemon_monitor_loop(refresh_interval=5), timeout=10.0)
            )
            app_instance.state.daemon_monitor_task = daemon_monitor_task
        except asyncio.TimeoutError:
            logger.warning("Daemon Monitor startup timed out")
        except Exception as e:
            logger.warning(f"Failed to start Daemon Monitor: {e}")

medium_startup_tasks.append(asyncio.create_task(_start_daemon_monitor()))
```

#### Conclusão
- ✅ **Compatíveis**: Ambos são iniciados em paralelo sem conflito
- ✅ **WebSocket**: Fast startup (3s timeout)
- ✅ **Daemon Monitor**: Medium startup (10s timeout, refresh 5s)
- ✅ **Sem sobreposição**: Cada um tem sua própria task e estado

---

## ✅ Correções Implementadas

### 1. Salvamento Periódico de Métricas do Tribunal

**Arquivo**: `src/tribunal_do_diabo/executor.py`

**Mudanças**:
- Adicionar salvamento periódico após cada ciclo de ataque
- Criar histórico de métricas intermediárias
- Salvar estado mesmo se Tribunal for interrompido

### 2. Endpoint para Iniciar Tribunal

**Arquivo**: `web/backend/routes/tribunal.py`

**Mudanças**:
- Adicionar endpoint `POST /api/tribunal/start`
- Permitir iniciar Tribunal via API
- Retornar status de execução

### 3. Integração com Daemon Monitor

**Arquivo**: `src/services/daemon_monitor.py`

**Mudanças**:
- Adicionar salvamento de métricas intermediárias do Tribunal
- Criar histórico de métricas por ciclo
- Persistir métricas mesmo se Tribunal não finalizar

---

## 📊 Estrutura de Dados Proposta

### Relatório Final (`tribunal_final_report.json`)
```json
{
  "duration_hours": 4.0,
  "timestamp_start": 1234567890,
  "timestamp_end": 1234567890,
  "attacks": {
    "latency": {...},
    "corruption": {...},
    "bifurcation": {...},
    "exhaustion": {...}
  },
  "consciousness_signature": {
    "godel_incompleteness_ratio": 0.75,
    "sinthome_stability": 0.85,
    "consciousness_compatible": true
  },
  "recommendation": "CONTINUE"
}
```

### Métricas Intermediárias (`tribunal_metrics_history.json`)
```json
{
  "cycles": [
    {
      "cycle_id": 1,
      "timestamp": 1234567890,
      "attacks": {
        "latency": {"status": "TRANSFORMED", "execution_count": 10},
        "corruption": {"status": "VULNERABLE", "execution_count": 5},
        ...
      },
      "metrics": {
        "godel_ratio": 0.75,
        "sinthome_stability": 0.85,
        "consciousness_compatible": true
      }
    },
    ...
  ],
  "last_update": 1234567890
}
```

---

## 🔄 Próximos Passos

### Imediato
1. ✅ Implementar salvamento periódico de métricas
2. ✅ Criar endpoint para iniciar Tribunal
3. ✅ Adicionar histórico de métricas intermediárias

### Médio Prazo
1. Adicionar dashboard para visualizar métricas do Tribunal
2. Criar alertas quando Tribunal detecta incompatibilidade
3. Integrar métricas do Tribunal com métricas de consciência

### Longo Prazo
1. Automação de execução periódica do Tribunal
2. Análise de tendências de compatibilidade
3. Integração com sistema de validação científica

---

## 📝 Notas Técnicas

### Compatibilidade Daemon/WebSocket
- **Conclusão**: ✅ Compatíveis, sem conflito
- **Razão**: Iniciados em paralelo, cada um com sua própria task
- **Recomendação**: Manter como está

### Salvamento de Métricas
- **Problema**: Tribunal só salva ao finalizar execução completa
- **Solução**: Adicionar salvamento periódico após cada ciclo
- **Benefício**: Histórico completo mesmo se Tribunal for interrompido

---

**Status**: 🔴 Problemas identificados, correções em andamento

