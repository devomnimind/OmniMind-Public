# Implementação Passo-a-Passo: Observabilidade RNN (Sprint 1)
**Data**: 2025-12-10
**Duração**: 1 semana
**Objetivo**: Correlação básica funcional (TraceID propagado)

---

## 📋 Sprint 1: Foundation Tracing

### Task 1.1: Add RNNCycleContext Class
**Arquivo**: `src/consciousness/integration_loop.py`
**Tempo**: 30 min

```python
# ADICIONAR (lines ~320, antes de IntegrationLoop)
from dataclasses import dataclass
import uuid
import time
from opentelemetry import context as otel_context

@dataclass
class RNNCycleContext:
    """Contexto de observabilidade para um ciclo RNN"""
    cycle_id: int
    trace_id: str
    span_id: str
    start_time: float

    @classmethod
    def create(cls, cycle_id: int, workspace_state_hash: str = "") -> "RNNCycleContext":
        """Cria TraceID determinístico para reprodutibilidade"""
        deterministic_seed = f"cycle:{cycle_id}:{workspace_state_hash}"
        trace_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, deterministic_seed))
        span_id = str(uuid.uuid4())
        return cls(
            cycle_id=cycle_id,
            trace_id=trace_id,
            span_id=span_id,
            start_time=time.time(),
        )
```

**Checklist**:
- [ ] Adicionar import uuid, time
- [ ] Implementar classe com @dataclass
- [ ] Teste: `ctx = RNNCycleContext.create(1, "test")` → trace_id determinístico

---

### Task 1.2: Instrumentar execute_cycle_sync()
**Arquivo**: `src/consciousness/integration_loop.py`
**Tempo**: 1h 15min

**Antes** (linhas ~411):
```python
def execute_cycle_sync(self, collect_metrics: bool = True) -> LoopCycleResult:
    """Execute consciousness cycle synchronously."""
    self.cycle_count += 1
    # ... 150 linhas de código ...
    return result
```

**Depois**:
```python
def execute_cycle_sync(self, collect_metrics: bool = True) -> LoopCycleResult:
    """Execute consciousness cycle synchronously with distributed tracing."""
    from opentelemetry import trace

    self.cycle_count += 1

    # 🎯 1. Criar contexto RNN
    workspace_state_hash = str(hash(self.workspace.embedding_dim))
    cycle_context = RNNCycleContext.create(self.cycle_count, workspace_state_hash)

    # 🎯 2. Ativar tracing OTel
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        name=f"rnn_cycle:{self.cycle_count:05d}",
        attributes={
            "trace_id": cycle_context.trace_id,
            "cycle_id": self.cycle_count,
            "phase": getattr(self, 'current_phase', 0),
            "workspace_dim": self.workspace.embedding_dim,
        }
    ) as cycle_span:

        # 🎯 3. Salvar contexto para Step-level tracing
        self._current_cycle_context = cycle_context

        try:
            # ... RESTO DO CÓDIGO EXISTENTE ...
            # (execute_cycle_sync original)
            result = self._execute_cycle_body(collect_metrics)

            # 🎯 4. Registrar sucesso no span
            cycle_span.set_attribute("status", "success")
            cycle_span.set_attribute("phi", float(result.phi))
            if result.extended_data and result.extended_data.phi_causal:
                cycle_span.set_attribute("phi_causal",
                                       float(result.extended_data.phi_causal))

            # 🎯 5. Adicionar trace_id ao result
            result.trace_id = cycle_context.trace_id

            return result

        except Exception as e:
            cycle_span.set_attribute("status", "error")
            cycle_span.set_attribute("error", str(e))
            raise

        finally:
            self._current_cycle_context = None

def _execute_cycle_body(self, collect_metrics: bool) -> LoopCycleResult:
    """Original execute_cycle_sync logic (renomeado)"""
    # MOVER TODO O CÓDIGO EXISTENTE AQUI
```

**Alternativa (Menos Refactoring)**:
```python
def execute_cycle_sync(self, collect_metrics: bool = True) -> LoopCycleResult:
    """Original code + tracing wrapper"""
    from opentelemetry import trace

    self.cycle_count += 1

    # 1. Criar contexto
    cycle_context = RNNCycleContext.create(self.cycle_count)
    self._current_cycle_context = cycle_context

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        f"rnn_cycle:{self.cycle_count:05d}",
        attributes={"trace_id": cycle_context.trace_id}
    ) as span:
        try:
            # ... CÓDIGO ORIGINAL SEM MUDANÇAS ...
            # Apenas adicionar ao final:
            result.trace_id = cycle_context.trace_id  # NOVO
            return result
        except Exception as e:
            span.set_attribute("status", "error")
            raise
```

**Checklist**:
- [ ] Adicionar imports (trace, otel_context)
- [ ] Criar RNNCycleContext no início
- [ ] Ativar span com tracer
- [ ] Salvar cycle_context em self (para Step-level access)
- [ ] Adicionar trace_id ao resultado
- [ ] Teste: resultado deve ter `.trace_id` attribute

---

### Task 1.3: Instrumentar Steps Individuais (1-13)
**Arquivo**: `src/consciousness/integration_loop.py`
**Tempo**: 2h (10-15 min por step)

**Padrão para cada step** (exemplo: Step 1 Sensory):

**Antes** (linhas ~500):
```python
# Passo 1: Sensory Input Module
sensory_result = self.executors["sensory_input"].execute(
    state=initial_state,
    workspace=self.workspace,
)
```

**Depois**:
```python
# Passo 1: Sensory Input Module
if hasattr(self, '_current_cycle_context'):
    ctx = self._current_cycle_context
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("step_1_sensory") as step_span:
        step_start_time = time.time()
        sensory_result = self.executors["sensory_input"].execute(
            state=initial_state,
            workspace=self.workspace,
        )
        step_duration_ms = (time.time() - step_start_time) * 1000
        step_span.set_attribute("latency_ms", step_duration_ms)
        step_span.set_attribute("embedding_size",
                               getattr(sensory_result, 'embedding_dim', 0))
else:
    # Fallback sem tracing
    sensory_result = self.executors["sensory_input"].execute(
        state=initial_state,
        workspace=self.workspace,
    )
```

**Ou (mais simples)**: Criar decorator `@trace_step`

```python
from functools import wraps

def trace_step(step_name: str):
    """Decorator para instrumentar steps automaticamente"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            from opentelemetry import trace
            import time

            ctx = getattr(self, '_current_cycle_context', None)
            if not ctx:
                return func(self, *args, **kwargs)

            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(step_name) as span:
                start = time.time()
                result = func(self, *args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                span.set_attribute("latency_ms", duration_ms)
                return result
        return wrapper
    return decorator

# Usage:
@trace_step("step_1_sensory")
def run_step_1_sensory(self):
    return self.executors["sensory_input"].execute(...)
```

**Checklist** (x13 steps):
- [ ] Step 1: Sensory Input
- [ ] Step 2: Qualia
- [ ] Step 3: Narrative
- [ ] Step 4: Meaning Maker
- [ ] Step 5: Expectation
- [ ] Step 6: Imagination
- [ ] Step 7: Shared Workspace Update
- [ ] Step 8: Desire Engine (epsilon calc)
- [ ] Step 9: Consciousness Triad
- [ ] Step 10: Imagination Consistency
- [ ] Step 11: Δ-Φ Correlation
- [ ] Step 12: Phase Validation
- [ ] Step 13: Extended Results

---

### Task 1.4: Adicionar trace_id ao OrchestratorEventBus
**Arquivo**: `src/orchestrator/event_bus.py`
**Tempo**: 1h

**1. Modificar OrchestratorEvent** (ou adicionar fields):

```python
# Em OrchestratorEvent dataclass/class, adicionar:
trace_id: Optional[str] = None  # NOVO
span_id: Optional[str] = None   # NOVO
```

**2. Modificar publish()** (lines ~200):

**Antes**:
```python
def publish(self, event: OrchestratorEvent):
    """Publish event to all subscribers."""
    for handler in self._handlers.get(event.event_type, []):
        handler(event)

    # Log to JSONL
    self._write_event_log(event)
```

**Depois**:
```python
def publish(self, event: OrchestratorEvent):
    """Publish event with distributed tracing context."""
    from opentelemetry import context as otel_context
    import uuid

    # 🎯 1. Extrair trace_id do contexto OTel
    trace_id = otel_context.get("rnn.trace_id") or str(uuid.uuid4())

    # 🎯 2. Adicionar ao evento
    event.trace_id = trace_id
    event.span_id = str(uuid.uuid4())

    # 🎯 3. Processar handlers (existente)
    for handler in self._handlers.get(event.event_type, []):
        handler(event)

    # 🎯 4. Log com trace_id
    self._write_event_log(event)

def _write_event_log(self, event: OrchestratorEvent):
    """Write event to JSONL with tracing metadata"""
    import json
    from datetime import datetime, timezone

    event_dict = event.to_dict() if hasattr(event, 'to_dict') else asdict(event)
    event_dict.update({
        "trace_id": event.trace_id,
        "span_id": event.span_id,
        "published_at": datetime.now(timezone.utc).isoformat(),
    })

    with open("data/monitor/events_traced.jsonl", "a") as f:
        f.write(json.dumps(event_dict) + "\n")
```

**Checklist**:
- [ ] Adicionar trace_id, span_id fields em OrchestratorEvent
- [ ] Modificar publish() para extrair trace_id de OTel context
- [ ] Escrever em arquivo separado `events_traced.jsonl` com trace_id
- [ ] Teste: Publicar evento durante ciclo → deve ter trace_id

---

### Task 1.5: Adicionar ExtendedLoopCycleResult.trace_id
**Arquivo**: `src/consciousness/extended_cycle_result.py`
**Tempo**: 15 min

```python
# Em ExtendedLoopCycleResult dataclass, adicionar campo:
@dataclass
class ExtendedLoopCycleResult:
    trace_id: Optional[str] = None  # NOVO - para correlação
    # ... resto dos fields ...

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict para persistência"""
        d = {
            # ... existing fields ...
            "trace_id": self.trace_id,  # NOVO
        }
        return d
```

E em `LoopCycleResult`:
```python
@dataclass
class LoopCycleResult:
    trace_id: Optional[str] = None  # NOVO
    # ... resto ...
```

---

### Task 1.6: Atualizar Logging para Incluir TraceID
**Arquivo**: `src/consciousness/integration_loop.py`
**Tempo**: 30 min

Adicionar TraceID ao logger em pontos críticos:

```python
# Em execute_cycle_sync(), após criar cycle_context:
logger.debug(
    f"Cycle {self.cycle_count} started",
    extra={"trace_id": cycle_context.trace_id}
)

# Antes de retornar:
logger.debug(
    f"Cycle {self.cycle_count} completed",
    extra={"trace_id": cycle_context.trace_id, "phi": result.phi}
)
```

**Checklist**:
- [ ] Adicionar trace_id ao logger.debug/info/warning/error
- [ ] Usar estrutured logging (structlog preferred)
- [ ] Verificar logs: grep "trace_id" → deve aparecer

---

## ✅ Validação Pós-Sprint 1

### Teste 1: RNNCycleContext Creation
```python
from src.consciousness.integration_loop import RNNCycleContext

ctx1 = RNNCycleContext.create(1, "hash1")
ctx2 = RNNCycleContext.create(1, "hash1")
assert ctx1.trace_id == ctx2.trace_id  # Determinístico ✅

ctx3 = RNNCycleContext.create(2, "hash1")
assert ctx3.trace_id != ctx1.trace_id  # Único per cycle ✅
```

### Teste 2: Execute Cycle com TraceID
```python
from src.consciousness.integration_loop import IntegrationLoop

loop = IntegrationLoop(enable_extended_results=True)
result = loop.execute_cycle_sync(collect_metrics=True)

assert hasattr(result, 'trace_id')  ✅
assert result.trace_id is not None  ✅
print(f"Cycle {result.cycle_id} → TraceID {result.trace_id}")
```

### Teste 3: EventBus com TraceID
```python
from src.orchestrator.event_bus import OrchestratorEventBus, OrchestratorEvent

bus = OrchestratorEventBus()
event = OrchestratorEvent(
    event_type="test",
    agent="TestAgent",
    priority="normal",
)

bus.publish(event)

# Verificar JSONL
import json
with open("data/monitor/events_traced.jsonl", "r") as f:
    last_line = f.readlines()[-1]
    logged_event = json.loads(last_line)
    assert "trace_id" in logged_event  ✅
    print(f"Event logged with TraceID: {logged_event['trace_id']}")
```

### Teste 4: Correlação Manual
```
1. Executar 5 ciclos: loop.execute_cycle_sync() x 5
2. Publicar evento no ciclo 3
3. Verificar:
   - unified_metrics.jsonl → ciclo 3 tem trace_id X
   - events_traced.jsonl → evento tem trace_id X
   → São iguais? SIM ✅ → Correlação funciona!
```

---

## 📊 Métricas de Sucesso Sprint 1

- ✅ Todos os 13 steps instrumentados com OTel spans
- ✅ Cada ciclo tem `trace_id` único determinístico
- ✅ EventBus events têm `trace_id` propagado
- ✅ JSONL logs incluem `trace_id`
- ✅ Básico de correlação funcional (mesmo trace_id = mesma transação)
- ✅ Sem regressões em performance (< 5% overhead)

---

## 🚀 Próximos Steps (Sprint 2)

- Implementar UnifiedMetricsAggregator
- Migrar de 3 collectors separados para 1 unified
- Adicionar agent context (qual agente desencadeou ciclo?)
- Dashboard de trace visualization

