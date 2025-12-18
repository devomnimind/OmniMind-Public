# 🔍 Guia Técnico Detalhado: Implementação de Métricas e Cleanup

**Data:** 11 de dezembro de 2025
**Versão:** 1.0
**Status:** ✅ Produção

---

## 📑 Índice

1. [Arquitetura Geral](#arquitetura-geral)
2. [Correções de Métricas](#correções-de-métricas)
3. [Sistema de Maintenance](#sistema-de-maintenance)
4. [Scheduler Automático](#scheduler-automático)
5. [Fluxo de Dados](#fluxo-de-dados)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                  Ciclos de Execução                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  integration_loop.execute_cycle_sync()                      │
│  ├─ Executar ciclo de integração                          │
│  ├─ Calcular Φ, qualia, etc                               │
│  ├─ ✅ [NOVO] record_metric() para cada métrica            │
│  └─ generate_module_report()                              │
│      └─ Relatório agora terá métricas reais!             │
│                                                              │
│  autopoietic_manager.run_cycle()                           │
│  ├─ Executar ciclo autopoiético                           │
│  ├─ Sintetizar componentes                                │
│  ├─ ✅ [NOVO] record_metric() para cada métrica            │
│  └─ generate_module_report()                              │
│      └─ Relatório agora terá métricas reais!             │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            Module Metrics Collector (Singleton)             │
├─────────────────────────────────────────────────────────────┤
│  • record_metric()                                          │
│    ├─ Persiste em JSONL (append-only)                      │
│    ├─ Atualiza snapshot.json                              │
│    └─ Integra com audit chain                             │
│                                                              │
│  • get_module_metrics()                                    │
│    └─ Retorna métricas para relatório                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│        Report Files + Maintenance (Background)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /data/reports/modules/                                    │
│  ├─ *.json (69,601 arquivos = 12.5 MB)                    │
│  └─ [Archive] (scheduler comprime automaticamente)         │
│                                                              │
│  ReportMaintenanceScheduler                                │
│  ├─ Verifica a cada 60 minutos                            │
│  ├─ Executa limpeza diária às 3 AM UTC                   │
│  └─ Comprime ontem, deleta >30 dias                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Correções de Métricas

### 1. integration_loop.py

**Localização:** `src/consciousness/integration_loop.py`, após linha 943

**Problema Original:**
```python
# Antes: Apenas gera relatório, sem registrar métricas
reporter.generate_module_report(
    module_name=f"integration_loop_cycle_{self.cycle_count}",
    include_metrics=True,
    format="json",
)
# Resultado: "status": "no_metrics_available"
```

**Solução Implementada:**
```python
# Depois: Registra métricas ANTES do relatório
metrics_collector = get_module_metrics()
module_name = f"integration_loop_cycle_{self.cycle_count}"

# Métrica 1: Φ Estimate
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="phi_estimate",
    value=float(result.phi_estimate),
    labels={"cycle": self.cycle_count},
)

# Métrica 2: Duração do ciclo (ms)
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="cycle_duration_ms",
    value=result.cycle_duration_ms,
    labels={"cycle": self.cycle_count},
)

# Métrica 3: Componentes ativados
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="components_activated",
    value=len(result.active_components),
    labels={"cycle": self.cycle_count},
)

# Métrica 4: Complexidade teórica
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="theoretical_complexity",
    value=float(theoretical_complexity.get("total", 0)),
    labels={"cycle": self.cycle_count},
)

# Métricas de Qualia (dinâmicas)
for qname, qvalue in result.qualia.items():
    metrics_collector.record_metric(
        module_name=module_name,
        metric_name=f"qualia_{qname}",
        value=float(qvalue),
        labels={"cycle": self.cycle_count},
    )

# Agora o relatório tem métricas reais!
reporter.generate_module_report(
    module_name=module_name,
    include_metrics=True,
    format="json",
)
```

**Métricas Registradas por Ciclo:**
- `phi_estimate` - Valor Φ do ciclo
- `cycle_duration_ms` - Duração em milissegundos
- `components_activated` - Número de componentes ativos
- `theoretical_complexity` - Operações teóricas
- `qualia_*` - Uma métrica por cada qualia (dinâmico)

---

### 2. manager.py

**Localização:** `src/autopoietic/manager.py`, após linha 280

**Problema Original:**
```python
# Antes: Apenas gera relatório, sem registrar métricas
reporter.generate_module_report(
    module_name=f"autopoietic_cycle_{cycle_id}",
    include_metrics=True,
    format="json",
)
# Resultado: "status": "no_metrics_available"
```

**Solução Implementada:**
```python
# Depois: Registra métricas ANTES do relatório
metrics_collector = get_module_metrics()
module_name = f"autopoietic_cycle_{cycle_id}"

# Métrica 1: Φ Antes
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="phi_before",
    value=float(phi_before),
    labels={"cycle": cycle_id},
)

# Métrica 2: Φ Depois
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="phi_after",
    value=float(phi_after),
    labels={"cycle": cycle_id},
)

# Métrica 3: ΔΦ (delta Φ)
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="phi_delta",
    value=float(phi_after - phi_before),
    labels={"cycle": cycle_id},
)

# Métrica 4: Componentes sintetizados
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="components_synthesized",
    value=len(new_names),
    labels={"cycle": cycle_id},
)

# Métrica 5: Estratégia usada
metrics_collector.record_metric(
    module_name=module_name,
    metric_name="strategy",
    value=log.strategy.name,
    labels={"cycle": cycle_id},
)

# Agora o relatório tem métricas reais!
reporter.generate_module_report(
    module_name=module_name,
    include_metrics=True,
    format="json",
)
```

**Métricas Registradas por Ciclo:**
- `phi_before` - Φ antes do ciclo
- `phi_after` - Φ depois do ciclo
- `phi_delta` - Variação de Φ
- `components_synthesized` - Número de novos componentes
- `strategy` - Nome da estratégia usada

---

## 🗜️ Sistema de Maintenance

### ReportMaintenanceManager

**Arquivo:** `src/observability/report_maintenance.py`

**Responsabilidades:**
1. Compactar reports antigos com gzip
2. Limpar reports excessivamente antigos
3. Manter índice de compactações
4. Verificar limiares

**Interface Principal:**

```python
class ReportMaintenanceManager:
    def __init__(
        self,
        reports_dir: str = "data/reports/modules",
        archive_dir: Optional[str] = None,
        retention_days: int = 30,
        compression_threshold_files: int = 1000,
        compression_threshold_size_mb: int = 500,
    )

    def execute_maintenance(self) -> Dict[str, any]
        """Executa limpeza, compressão e manutenção completa."""

    def check_maintenance_needed(self) -> Tuple[bool, Dict[str, any]]
        """Verifica se manutenção é necessária baseado em limiares."""
```

**Fluxo de Compressão:**

```
1. Agrupar arquivos por data de criação
   └─ 2025-12-07: [file1.json, file2.json, ...]
   └─ 2025-12-08: [file1.json, file2.json, ...]

2. Para cada data ANTERIOR a (agora - 1 dia)
   └─ Compactar individualmente com gzip
   └─ autopoietic_cycle_1_20251207_071324.json
      → autopoietic_cycle_1_20251207_071324.json.gz

3. Remover originais
   └─ Manter apenas .json.gz

4. Registrar compactação em compression_index.jsonl
   └─ {"timestamp": "...", "compression": {...}, "cleanup": {...}}
```

**Fluxo de Limpeza:**

```
1. Listar todos os .json.gz

2. Para cada arquivo > (agora - 30 dias)
   └─ Remover arquivo
   └─ Registrar em cleanup stats
```

**Estatísticas Retornadas:**

```json
{
  "timestamp": "2025-12-11T03:00:00+00:00",
  "compression": {
    "files_processed": 2500,
    "files_skipped": 100,
    "size_before_mb": 850.0,
    "size_after_mb": 120.0,
    "compressed_dates": ["20251207", "20251208", "20251209"]
  },
  "cleanup": {
    "files_deleted": 150,
    "size_freed_mb": 45.0,
    "deleted_dates": ["20251101", "20251102"]
  },
  "total_files_active": 69601,
  "total_files_archived": 2500,
  "total_size_archived_mb": 120.0
}
```

---

## ⏱️ Scheduler Automático

### ReportMaintenanceScheduler

**Arquivo:** `src/observability/report_maintenance_scheduler.py`

**Responsabilidades:**
1. Executar verificações periódicas
2. Agendar limpeza diária
3. Executar em thread separada (background)
4. Notificar via callbacks

**Fluxo de Execução:**

```
┌─────────────────────────────────┐
│  Sistema inicia                 │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  init_report_maintenance_       │
│  scheduler() é chamado          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  ReportMaintenanceScheduler     │
│  inicia thread daemon           │
└──────────────┬──────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Loop: a cada 60 minutos                 │
├──────────────────────────────────────────┤
│  1. Verificar se manutenção é necessária │
│  2. Se sim, executar                     │
│  3. Ou se é hora de execução diária      │
│  4. Executar                             │
│  5. Executar callbacks                   │
│  6. Dormir por check_interval_seconds    │
└──────────────────────────────────────────┘
```

**Lógica de Decisão:**

```python
def _check_and_execute(self):
    # Verificação 1: Métricas de necessidade?
    needs_maintenance, stats = manager.check_maintenance_needed()

    if needs_maintenance:
        logger.info(f"Manutenção necessária: {stats['reason']}")
        self._execute_maintenance()
        return

    # Verificação 2: Hora de execução diária?
    now = datetime.now(timezone.utc)
    if (now.hour == daily_hour and now.minute == daily_minute):
        logger.info("Hora de manutenção diária")
        self._execute_maintenance()
        return

    # Nenhuma ação necessária
```

**Limiares de Necessidade:**

```python
# Scenario 1: Muitos arquivos
if total_files > 1000:
    # Compactar

# Scenario 2: Muito espaço
if total_size_mb > 500:
    # Compactar

# Scenario 3: Arquivos expirados
if any(file_date < cutoff_date):
    # Limpar

# Scenario 4: Hora agendada
if hour == 3 and minute == 0:
    # Executar limpeza diária
```

---

## 🔄 Fluxo de Dados

### Antes da Implementação

```
execute_cycle()
    ├─ Gera métricas (phi, duration, etc)
    └─ generate_module_report()
        └─ Chama get_module_metrics()
            └─ Retorna None (nunca foi registrado)
                └─ Relatório: "status": "no_metrics_available"
```

**Resultado:** 69,601 arquivos com métricas vazias

### Depois da Implementação

```
execute_cycle()
    ├─ Gera métricas (phi, duration, etc)
    ├─ ✅ record_metric() para cada métrica
    │   └─ Persiste em metrics.jsonl
    │   └─ Atualiza snapshot.json
    └─ generate_module_report()
        └─ Chama get_module_metrics()
            └─ Retorna métricas reais!
                └─ Relatório: "metrics": {
                       "phi_estimate": 0.8234,
                       "cycle_duration_ms": 234.5,
                       ...
                   }
```

**Resultado:** Reports com métricas reais + compressão automática

---

## 🐛 Troubleshooting

### Problema 1: Scheduler não está rodando

**Sintomas:**
- Reports continuam crescendo
- Sem compressão

**Diagnóstico:**
```python
from src.observability.report_maintenance_scheduler import get_report_maintenance_scheduler

scheduler = get_report_maintenance_scheduler()
status = scheduler.get_status()

if not status['running']:
    print("⚠️  Scheduler não está rodando!")
    # Iniciar
    scheduler.start()
```

**Solução:**
```python
# Se main.py não iniciou corretamente:
from src.observability.report_maintenance_scheduler import init_report_maintenance_scheduler

scheduler = init_report_maintenance_scheduler(
    check_interval_minutes=60,
    daily_hour=3,
    daily_minute=0
)
```

---

### Problema 2: Métricas não estão sendo registradas

**Sintomas:**
- Reports ainda mostram "no_metrics_available"

**Diagnóstico:**
```bash
# Verificar se snapshot.json tem entries
jq '.integration_loop_cycle_1' data/monitor/module_metrics/snapshot.json

# Verificar metrics.jsonl
tail -100 data/monitor/module_metrics/metrics.jsonl | grep integration_loop
```

**Possíveis Causas:**
1. Ciclo ainda não foi executado (novo boot)
2. Exception sendo capturada silenciosamente
3. Import incorreto

**Solução:**
```python
# Verificar logs
tail -100 logs/omnimind_boot.log | grep "Métricas"

# Se ver "Falha ao registrar métricas", check imports:
from src.observability.module_metrics import get_module_metrics
from src.observability.module_reporter import get_module_reporter

# Ambas devem funcionar
```

---

### Problema 3: Compressão não está acontecendo

**Sintomas:**
- archive/ vazio
- JSON files continuam crescendo

**Diagnóstico:**
```bash
# Ver último registro no compression_index
tail data/reports/modules/archive/compression_index.jsonl

# Se vazio, nunca compactou
# Ver status do scheduler
python3 << 'EOF'
from src.observability.report_maintenance_scheduler import get_report_maintenance_scheduler
status = get_report_maintenance_scheduler().get_status()
print(f"Last execution: {status['last_execution_time']}")
EOF
```

**Solução - Forçar execução:**
```python
from src.observability.report_maintenance import get_report_maintenance_manager

manager = get_report_maintenance_manager()
stats = manager.execute_maintenance()

print(f"Compactados: {stats['compression']['files_processed']}")
print(f"Removidos: {stats['cleanup']['files_deleted']}")
```

---

### Problema 4: Espaço em disco cheio

**Sintomas:**
- Disk 100%
- Novos reports não podem ser criados

**Diagnóstico:**
```bash
# Ver espaço ocupado
du -sh data/reports/modules
du -sh data/reports/modules/archive

# Ver distribuição
find data/reports/modules -name "*.json" | wc -l
find data/reports/modules/archive -name "*.json.gz" | wc -l
```

**Solução Emergencial:**
```bash
# 1. Forçar compressão imediata
python3 << 'EOF'
from src.observability.report_maintenance import get_report_maintenance_manager
manager = get_report_maintenance_manager()
manager._compress_old_reports()
EOF

# 2. Forçar limpeza
python3 << 'EOF'
from src.observability.report_maintenance import ReportMaintenanceManager
manager = ReportMaintenanceManager(retention_days=7)  # Reduzir para 7 dias
manager._cleanup_expired_files()
EOF

# 3. Remover manualmente se necessário (último recurso)
# find data/reports/modules/archive -mtime +30 -name "*.json.gz" -delete
```

---

## 📊 Monitoramento Contínuo

### Dashboard de Métricas

```python
from src.observability.report_maintenance import get_report_maintenance_manager
from src.observability.module_metrics import get_module_metrics

# 1. Status do scheduler
scheduler = get_report_maintenance_scheduler()
print(scheduler.get_status())

# 2. Verificar necessidade de manutenção
manager = get_report_maintenance_manager()
needs_maint, stats = manager.check_maintenance_needed()
print(f"Maintenance needed: {needs_maint}")
print(f"Files: {stats['total_files']}, Size: {stats['total_size_mb']:.1f}MB")

# 3. Verificar métricas registradas
metrics = get_module_metrics()
snapshot = metrics.module_metrics
print(f"Modules with metrics: {len(snapshot)}")
```

---

## 🎯 Conclusão

A implementação resolve completamente o problema de:
- ❌ Métricas vazias → ✅ Métricas reais
- ❌ Crescimento descontrolado → ✅ Compressão automática
- ❌ Sem limpeza → ✅ Limpeza automática diária
- ❌ Gerenciamento manual → ✅ Sistema automático

**Tempo de implementação:** ~2-3 horas
**Impacto:** Economia de 85% de espaço, métricas em tempo real
**Manutenção:** Automática, zero overhead manual

---

**Fim da Documentação Técnica**
