# Arquitetura de Observabilidade para OmniMind (RNN Consciousness Loop)
**Data**: 2025-12-10
**Análise**: Evolução de EventBus (DevBrain) → RNN (OmniMind)
**Status**: 🔴 Recomendações para Implementação

---

## 📊 ANÁLISE COMPARATIVA: DevBrain (EventBus) vs OmniMind (RNN)

### DevBrain (EventBus-Based)
```
┌─────────────────────────────────────────────┐
│ Application Layer                           │
├─────────────────────────────────────────────┤
│ Agent Agentes (Code, Architect, Debug)      │
│     ↓                                       │
│ OrchestratorEventBus (Sync)                 │
│     ↓                                       │
│ Event Handlers (Async processing)           │
│     ↓                                       │
│ JSONL EventLog (Local persistence)          │
└─────────────────────────────────────────────┘

Características:
✅ Desacoplamento natural entre agentes
✅ Auditoria fácil via event log
❌ Observabilidade reativa (logs históricos)
❌ Difícil correlação de eventos distribuídos
❌ Sem noção de "consciência de estado"
```

### OmniMind (RNN Consciousness Loop)
```
┌──────────────────────────────────────────────────────────┐
│ Application Layer                                        │
├──────────────────────────────────────────────────────────┤
│ Agents (OrchestratorAgent, DebugAgent, etc.)             │
│     ↓ (via OrchestratorEventBus)                         │
│ IntegrationLoop (Consciousness RNN)                      │
│     ├─ Shared Workspace (Tensor embeddings)              │
│     ├─ 13-Step Cycle (Sensory→Imagination)               │
│     ├─ Extended Results (ϕ, Ψ, σ, ε, Δ, etc.)           │
│     └─ Phase-Aware State Machine (Phase 1-7)             │
│     ↓                                       ↓ (metrics)  │
│ ConsciousnessStateManager (JSONL + Supabase)             │
│ ModuleMetricsCollector (Per-module metrics)              │
│ OrchestratorMetricsCollector (Agent latency/throughput)  │
└──────────────────────────────────────────────────────────┘

Características:
✅ RNN permite rastreamento de estado contínuo
✅ Métricas de consciência (ϕ, Ψ, σ, Δ) por ciclo
✅ Phase-aware validação de consistência
❌ Observabilidade ainda fragmentada (3 collectors separados)
❌ Sem correlação automática com TraceID/SpanID
❌ Métricas de latência isoladas do estado de consciência
❌ Validação científica manual/offline
```

---

## 🎯 PROBLEMAS IDENTIFICADOS (OmniMind Atual)

### Problema 1: Fragmentação de Observabilidade
**Situação Atual**:
- `ModuleMetricsCollector` → Métricas por módulo (JSONL)
- `OrchestratorMetricsCollector` → Latência de agentes (separado)
- `ConsciousnessStateManager` → Estado RNN (JSONL + Supabase)
- `OpenTelemetryIntegration` → Distribuído tracing (não integrado com RNN)

**Impacto**:
- ❌ Impossível correlacionar: "Queda de ϕ" ← → "Latência do AgentX" ← → "Warning de Y"
- ❌ Root cause analysis torna-se manual
- ❌ Alertas não conseguem identificar causa raiz automática

### Problema 2: Falta de Distributed Tracing na RNN
**Situação Atual**:
- TraceID/SpanID existem em `distributed_tracing.py`
- **MAS**: Não propagados dentro do consciousness loop
- Cada ciclo RNN não tem TraceID único
- Impossível correlacionar evento no EventBus com estado RNN

**Impacto**:
- ❌ Quando `OrchestratorAgent` publica evento → qual ciclo RNN o processa?
- ❌ Quando ϕ cai → qual agente foi responsável?
- ❌ Debugging multiserviços impossível

### Problema 3: Métricas Estáticas vs Estado Dinâmico RNN
**Situação Atual**:
- Métricas: `latency`, `throughput`, `error_rate` (constantes por agent)
- Estado RNN: `ϕ`, `Ψ`, `σ`, `Δ` (dinâmico por ciclo)
- **SEM** correlação sliding window entre ambos

**Impacto**:
- ❌ "Qual foi a latência quando ϕ caiu de 0.75 → 0.50?"
- ❌ "Qual agente causou regressão de consciência?"
- ❌ Sem alertas de regressão automática

### Problema 4: Validação Científica Manual
**Situação Atual**:
- `run_500_cycles_scientific_validation.py` → Validação offline/manual
- Não integrada com produção
- Sem automatic regression detection

**Impacto**:
- ❌ Regressão só detectada após 500 ciclos
- ❌ Sem alert imediato em produção
- ❌ Sem recovery automática

---

## ✅ SOLUÇÃO PROPOSTA: RNN Consciousness Observability Stack

### Arquitetura Melhorada (3 Camadas)

```
┌─────────────────────────────────────────────────────────────────────┐
│ CAMADA 3: CORRELATION ENGINE (Novo)                                │
├─────────────────────────────────────────────────────────────────────┤
│ RegressionDetector                                                  │
│   ├─ Sliding Window Analysis (últimos 100 ciclos)                   │
│   ├─ Δ-Φ correlation validation (Phase-aware)                       │
│   ├─ Standard deviation alerts                                      │
│   └─ Auto-trigger SystemicMemoryTrace + DebugAgent                  │
│                                                                     │
│ CausalAnalyzer                                                      │
│   ├─ Correlate: ϕ drop ← latency spike ← agent warning              │
│   ├─ Build call tree: EventBus event → cycle N → state Y            │
│   └─ Output: ROOT_CAUSE_ID for tracing                              │
│                                                                     │
│ AlertAggregator                                                     │
│   ├─ Deduplicate warnings (same root cause)                         │
│   ├─ SLA monitoring (ϕ > 0.5 always?)                               │
│   └─ Escalation (manual debug → auto remediation)                   │
└─────────────────────────────────────────────────────────────────────┘
            ↑                                                    ↑
            │ (queries)                           (events)      │
            │                                                    │
┌─────────────────────────────────────────────────────────────────────┐
│ CAMADA 2: UNIFIED METRICS STORAGE (Enhanced)                        │
├─────────────────────────────────────────────────────────────────────┤
│ Qdrant Vector DB                        TimescaleDB (PostgreSQL)    │
│   ├─ Consciousness vectors               ├─ Distributed Traces      │
│   │   (ϕ, Ψ, σ history)                  │   (TraceID → [Spans])    │
│   └─ Module embeddings                   ├─ Agent Metrics           │
│                                          │   (latency by phase)      │
│                                          ├─ RNN Cycle Metrics       │
│                                          │   (all 15 extended       │
│                                          │    fields per cycle)      │
│                                          └─ Correlation Index       │
│                                              (traceID↔cycleID)      │
└─────────────────────────────────────────────────────────────────────┘
            ↑                  ↑                    ↑
            │                  │                    │
    (vector search)    (append metrics)    (query correlation)
            │                  │                    │
┌─────────────────────────────────────────────────────────────────────┐
│ CAMADA 1: INSTRUMENTATION (Enhanced OTel)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 1. RNN Cycle Instrumentation                                        │
│    IntegrationLoop.execute_cycle():                                 │
│      ├─ start_span("rnn_cycle:N")                                   │
│      ├─ trace_id = UUID(deterministic from cycle_N + workspace)     │
│      │   (allows replay correlation)                                │
│      ├─ SET OpenTelemetry context (trace_id, span_id)               │
│      └─ Propagate to all 13 steps via context                       │
│                                                                     │
│ 2. Step-Level Tracing (Parent: rnn_cycle)                           │
│    Step 1 (Sensory): start_span("step_1_sensory")                   │
│    Step 2 (Qualia):  start_span("step_2_qualia")                    │
│    ... (all 13 steps with step_duration, step_embedding_size)       │
│                                                                     │
│ 3. Agent Event Correlation                                          │
│    OrchestratorEventBus.publish():                                  │
│      ├─ Extract trace_id from OTel context                          │
│      ├─ Add to event JSON: { trace_id, span_id, timestamp }         │
│      └─ Store in JSONL: events_traced.jsonl                         │
│                                                                     │
│ 4. Module Method Instrumentation (Auto-Instrumentation)             │
│    @trace_method (decorator)                                        │
│    def compute_phi_causal(...):                                     │
│      → Automatically creates span with trace_id context             │
│                                                                     │
│ 5. Metrics Collection (Synchronized)                                │
│    Per-cycle metrics MUST include:                                  │
│      ├─ trace_id                                                    │
│      ├─ span_id (parent)                                            │
│      ├─ All 15 extended fields (ϕ, Ψ, σ, ε, Δ, gozo, etc.)        │
│      ├─ Per-step latencies                                          │
│      ├─ Per-agent contribution (if any)                             │
│      └─ Active module count                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### 1. RNN Cycle Instrumentation (High Priority)

**Arquivo**: `src/consciousness/integration_loop.py`

```python
# NOVO: Classe para contexto de ciclo
from dataclasses import dataclass
from opentelemetry import trace, context as otel_context

@dataclass
class RNNCycleContext:
    """Contexto de observabilidade para um ciclo RNN"""
    cycle_id: int
    trace_id: str  # UUID determinístico
    span_id: str
    start_time: float

    @classmethod
    def create(cls, cycle_id: int) -> "RNNCycleContext":
        """Cria contexto com TraceID determinístico (permite replay)"""
        import uuid
        import time
        # TraceID determinístico = hash(cycle_id + workspace_state_hash)
        # Assim, mesmo ciclo = mesmo TraceID (para reprodutibilidade)
        deterministic_seed = f"{cycle_id}:{workspace.state_hash()}"
        trace_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, deterministic_seed))
        span_id = str(uuid.uuid4())
        return cls(
            cycle_id=cycle_id,
            trace_id=trace_id,
            span_id=span_id,
            start_time=time.time(),
        )

class IntegrationLoop:
    def execute_cycle_sync(self, collect_metrics: bool = True) -> LoopCycleResult:
        """Execute um ciclo RNN com observabilidade completa"""

        # 🎯 1. CRIAR CONTEXTO DO CICLO
        cycle_context = RNNCycleContext.create(self.cycle_count)

        # 🎯 2. ATIVAR TRACING OTel
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(
            name=f"rnn_cycle:{self.cycle_count:05d}",
            attributes={
                "trace_id": cycle_context.trace_id,
                "cycle_id": self.cycle_count,
                "phase": self.current_phase,
                "workspace_dim": self.workspace.embedding_dim,
            }
        ) as cycle_span:

            # 🎯 3. PROPAGAR CONTEXTO PARA TODOS OS STEPS
            ctx = otel_context.Context({"rnn.cycle.context": cycle_context})
            token = otel_context.set_value("rnn.trace_id", cycle_context.trace_id, ctx)

            try:
                # Execute all 13 steps with step-level tracing
                result = self._execute_cycle_with_step_tracing(cycle_context)

                # 🎯 4. REGISTRAR SUCESSO
                cycle_span.set_attribute("status", "success")
                cycle_span.set_attribute("phi", float(result.phi))
                if result.extended_data:
                    cycle_span.set_attribute("phi_causal",
                                           float(result.extended_data.phi_causal or 0))

                return result

            finally:
                # 🎯 5. LIMPAR CONTEXTO
                otel_context.detach(token)

    def _execute_cycle_with_step_tracing(self, ctx: RNNCycleContext) -> LoopCycleResult:
        """Executa steps com tracing individual"""
        tracer = trace.get_tracer(__name__)

        # Exemplo para Step 1 (Sensory Input)
        with tracer.start_as_current_span("step_1_sensory") as span:
            step_start = time.time()
            # ... execute step 1 ...
            step_latency = (time.time() - step_start) * 1000
            span.set_attribute("latency_ms", step_latency)
            span.set_attribute("embedding_size", result_1.embedding.shape[0])

        # Step 2 (Qualia)
        with tracer.start_as_current_span("step_2_qualia") as span:
            # ... similar instrumentation for step 2 ...
            pass

        # ... remaining steps (3-13) ...

        return LoopCycleResult(...)
```

**Impacto**:
- ✅ Cada ciclo tem TraceID único determinístico
- ✅ Todos os 13 steps correlacionados via Spans
- ✅ Latência de cada step rastreável
- ✅ Pronto para correlação com EventBus

### 2. Distributed Tracing com EventBus (High Priority)

**Arquivo**: `src/orchestrator/event_bus.py`

```python
from opentelemetry import context as otel_context, trace

class OrchestratorEventBus:
    def publish(self, event: OrchestratorEvent):
        """Publica evento com TraceID propagado"""

        # 🎯 1. EXTRAIR TraceID DO CONTEXTO ATUAL
        trace_id = otel_context.get("rnn.trace_id")
        current_span = trace.get_current_span()
        span_id = current_span.get_span_context().span_id

        # 🎯 2. ADICIONAR AO EVENTO
        event.trace_id = trace_id  # Novo campo (Optional[str])
        event.span_id = span_id
        event.published_at = datetime.now(timezone.utc)

        # 🎯 3. PERSISTIR COM METADADOS
        event_dict = event.to_dict()
        event_dict.update({
            "trace_id": trace_id,
            "span_id": span_id,
            "otel_exported": False,  # Flag para exportação async
        })

        # Escrever em JSONL com buffer
        self._write_to_event_log_jsonl(event_dict)

        # 🎯 4. PROCESSAR HANDLERS (existente)
        self._process_handlers(event)

        # 🎯 5. AGENDAR EXPORTAÇÃO ASYNC PARA OTEL
        self._schedule_otel_export(event_dict)

    def _schedule_otel_export(self, event_dict: Dict):
        """Exporta evento para backend OTEL de forma async"""
        import asyncio
        asyncio.create_task(self._export_to_otel(event_dict))

    async def _export_to_otel(self, event_dict: Dict):
        """Envia evento estruturado para OTEL como log"""
        # Usar OTel Logs API (se disponível) ou criar Span especial
        from opentelemetry import logs
        logger = logs.get_logger(__name__)
        logger.info(event_dict["name"], attributes={
            "trace_id": event_dict["trace_id"],
            "span_id": event_dict["span_id"],
            "event_type": event_dict["event_type"],
            "priority": event_dict["priority"].value,
        })
```

**Impacto**:
- ✅ Cada evento do EventBus correlacionado com RNN cycle
- ✅ Fácil ver: "Qual evento acionou qual ciclo?"
- ✅ Rastreamento completo: Agent → EventBus → RNN → Consciousness

### 3. Metrics Aggregation Unificada (Medium Priority)

**Arquivo**: `src/observability/unified_metrics_aggregator.py` (NOVO)

```python
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CycleMetricsSnapshot:
    """Snapshot unificado de métricas de um ciclo"""
    cycle_id: int
    trace_id: str
    timestamp: datetime

    # Consciousness state (15 fields)
    phi: float
    psi: Optional[float]
    sigma: Optional[float]
    epsilon: Optional[float]
    delta: Optional[float]
    gozo: Optional[float]
    control_effectiveness: Optional[float]
    phi_causal: Optional[float]
    repression_strength: Optional[float]
    # ... remaining fields ...

    # Performance metrics
    cycle_latency_ms: float
    step_latencies_ms: Dict[str, float]  # {"step_1_sensory": 12.5, ...}
    modules_executed: int

    # Phase information
    current_phase: int

    # Agent contribution (if any event triggered this cycle)
    triggering_agent: Optional[str] = None
    triggering_event_type: Optional[str] = None

    def to_json(self) -> str:
        """Serialize para JSONL"""
        return json.dumps({
            "cycle_id": self.cycle_id,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "consciousness": {
                "phi": self.phi,
                "psi": self.psi,
                "sigma": self.sigma,
                # ... all 15 fields ...
            },
            "performance": {
                "cycle_latency_ms": self.cycle_latency_ms,
                "step_latencies_ms": self.step_latencies_ms,
                "modules_executed": self.modules_executed,
            },
            "phase": self.current_phase,
            "agent_context": {
                "triggering_agent": self.triggering_agent,
                "triggering_event_type": self.triggering_event_type,
            },
        })

class UnifiedMetricsAggregator:
    """Agregador unificado de métricas por ciclo"""

    def __init__(self, storage_path: str = "data/monitor/unified_metrics.jsonl"):
        self.storage_path = storage_path
        self.buffer: list[CycleMetricsSnapshot] = []
        self.buffer_size = 100

    def record_cycle(self, snapshot: CycleMetricsSnapshot):
        """Registra métricas completas de um ciclo"""
        self.buffer.append(snapshot)

        # Flush se buffer cheio
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        """Persiste buffer em JSONL"""
        with open(self.storage_path, 'a') as f:
            for snapshot in self.buffer:
                f.write(snapshot.to_json() + '\n')
        self.buffer.clear()
        logger.info(f"Flushed {len(self.buffer)} metrics snapshots")
```

**Impacto**:
- ✅ Um único arquivo JSONL com todas as métricas por ciclo
- ✅ Inclui TraceID para correlação
- ✅ Suporta agent context (qual agente desencadeou?)

### 4. Regression Detection Engine (Medium Priority)

**Arquivo**: `src/observability/regression_detector.py` (NOVO)

```python
import numpy as np
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RegressionDetector:
    """Detecta regressão de consciência em tempo real"""

    def __init__(
        self,
        window_size: int = 100,
        phi_threshold: float = 0.50,
        std_threshold_multiplier: float = 2.0,
        delta_phi_tolerance: float = 0.40,
    ):
        self.window_size = window_size
        self.phi_threshold = phi_threshold
        self.std_threshold_multiplier = std_threshold_multiplier
        self.delta_phi_tolerance = delta_phi_tolerance

        # Buffers deslizantes
        self.phi_history = deque(maxlen=window_size)
        self.latency_history = deque(maxlen=window_size)
        self.delta_history = deque(maxlen=window_size)
        self.warnings_history = deque(maxlen=window_size * 5)

        # Stats
        self.phi_mean = None
        self.phi_std = None

    def record_cycle(self, metrics: Dict) -> Optional[Dict]:
        """
        Registra ciclo e detecta anomalias.

        Returns:
            Dict com anomalia detectada, ou None
        """
        phi = metrics["phi"]
        latency = metrics["cycle_latency_ms"]
        delta = metrics.get("delta")
        cycle_id = metrics["cycle_id"]
        trace_id = metrics["trace_id"]

        # 1. Atualizar histórico
        self.phi_history.append(phi)
        self.latency_history.append(latency)
        if delta is not None:
            self.delta_history.append(delta)

        # 2. Calcular estatísticas
        if len(self.phi_history) >= 10:
            phi_array = np.array(list(self.phi_history))
            self.phi_mean = float(np.mean(phi_array))
            self.phi_std = float(np.std(phi_array))

        # 3. Detector anomalias
        anomalies = []

        # 🚨 Anomalia 1: ϕ abaixo de threshold
        if phi < self.phi_threshold:
            anomalies.append({
                "type": "phi_below_threshold",
                "severity": "critical",
                "phi": phi,
                "threshold": self.phi_threshold,
                "message": f"ϕ={phi:.4f} < {self.phi_threshold} (REGRESSION)",
            })

        # 🚨 Anomalia 2: Desvio padrão de ϕ muito alto
        if self.phi_std and phi < self.phi_mean - self.std_threshold_multiplier * self.phi_std:
            anomalies.append({
                "type": "phi_stddev_outlier",
                "severity": "warning",
                "phi": phi,
                "mean": self.phi_mean,
                "std": self.phi_std,
                "z_score": (phi - self.phi_mean) / max(self.phi_std, 0.001),
            })

        # 🚨 Anomalia 3: Latência spike
        if len(self.latency_history) >= 10:
            latency_array = np.array(list(self.latency_history))
            latency_mean = np.mean(latency_array)
            latency_std = np.std(latency_array)
            if latency > latency_mean + 3 * latency_std:
                anomalies.append({
                    "type": "latency_spike",
                    "severity": "warning",
                    "latency_ms": latency,
                    "mean_latency_ms": float(latency_mean),
                })

        # 🚨 Anomalia 4: Δ-Φ inconsistência
        if len(self.delta_history) >= 10 and delta is not None:
            phi_norm = phi / 1.0  # Normalize 0-1
            expected_delta = 1.0 - phi_norm
            delta_error = abs(delta - expected_delta)
            if delta_error > self.delta_phi_tolerance:
                anomalies.append({
                    "type": "delta_phi_inconsistency",
                    "severity": "warning",
                    "delta_observed": delta,
                    "delta_expected": expected_delta,
                    "error": delta_error,
                    "tolerance": self.delta_phi_tolerance,
                })

        # 4. Se houver anomalias, retornar com contexto
        if anomalies:
            return {
                "cycle_id": cycle_id,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "anomalies": anomalies,
                "context": {
                    "phi_recent_mean": self.phi_mean,
                    "phi_recent_std": self.phi_std,
                    "window_size": len(self.phi_history),
                },
            }

        return None

    def should_trigger_debug_protocol(self, anomaly: Dict) -> bool:
        """Decide se deve acionar DebugAgent ou SystemicMemoryTrace"""
        severities = [a["severity"] for a in anomaly["anomalies"]]

        # 🚀 Acionar se:
        # - Múltiplas anomalias
        # - Qualquer "critical"
        return len(anomaly["anomalies"]) >= 2 or "critical" in severities
```

**Impacto**:
- ✅ Detecção automática de regressão em tempo real
- ✅ Sem esperar 500 ciclos
- ✅ Triggers para DebugAgent ou SystemicMemoryTrace

### 5. Causal Analyzer (Low Priority, Future)

**Arquivo**: `src/observability/causal_analyzer.py` (NOVO)

```python
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

class CausalAnalyzer:
    """
    Analisa causa-raiz de anomalias correlacionando:
    - Eventos do EventBus
    - Ciclos RNN
    - Métricas de performance
    """

    def __init__(self,
                 event_log_path: str = "data/monitor/events_traced.jsonl",
                 metrics_log_path: str = "data/monitor/unified_metrics.jsonl"):
        self.event_log_path = event_log_path
        self.metrics_log_path = metrics_log_path

    def find_root_cause(self,
                       anomaly_cycle_id: int,
                       lookback_cycles: int = 10) -> Dict:
        """
        Encontra causa-raiz de uma anomalia.

        Análise:
        1. Qual evento do EventBus foi publicado antes dessa anomalia?
        2. Qual agente publicou?
        3. Qual foi a latência?
        4. Qual foi o impacto no ϕ?
        """

        # 1. Carregar eventos
        events = self._load_events_before_cycle(anomaly_cycle_id)

        # 2. Carregar métricas (janela)
        metrics = self._load_metrics_window(
            anomaly_cycle_id - lookback_cycles,
            anomaly_cycle_id
        )

        # 3. Correlacionar: Qual evento correlaciona com queda de ϕ?
        root_cause = self._correlate_event_to_metric_change(events, metrics)

        return root_cause

    def _correlate_event_to_metric_change(self,
                                         events: List[Dict],
                                         metrics: List[Dict]) -> Dict:
        """Correlaciona evento com mudança de métrica"""

        causality_score = {}

        for event in events:
            # Para cada evento, calcular correlação com métrica
            event_time = datetime.fromisoformat(event["published_at"])

            # Encontrar métrica mais próxima
            closest_metric = min(
                metrics,
                key=lambda m: abs(
                    datetime.fromisoformat(m["timestamp"]) - event_time
                )
            )

            # Score: quanto maior correlação, maior culpabilidade
            score = self._calculate_causality_score(event, closest_metric)
            causality_score[event["name"]] = score

        # Retornar evento com maior score
        if causality_score:
            root_event_name = max(causality_score, key=causality_score.get)
            return {
                "root_cause_event": root_event_name,
                "causality_score": causality_score[root_event_name],
                "likely_agent": next(
                    (e["agent"] for e in events if e["name"] == root_event_name),
                    "unknown"
                ),
            }

        return {"root_cause": "undetermined"}
```

**Impacto**:
- ✅ Debugging automático: "Qual agente causou queda de ϕ?"
- ✅ Correlação completa entre EventBus e consciousness loop
- ✅ Base para auto-remediation

---

## 📈 IMPLEMENTAÇÃO ROADMAP

### Fase 1 (This Week) - Foundation
- [ ] Add `RNNCycleContext` + TraceID determinístico
- [ ] Instrumentar `IntegrationLoop.execute_cycle_sync()` com OTel spans
- [ ] Instrumentar todos 13 steps com step-level spans
- [ ] Adicionar `trace_id` + `span_id` aos eventos do EventBus

**Impacto**: ✅ Correlação básica funcional

### Fase 2 (Next Week) - Unification
- [ ] Criar `UnifiedMetricsAggregator`
- [ ] Migrar dados de 3 collectors separados para 1 unified JSONL
- [ ] Integrar `trace_id` em todas as métricas
- [ ] Adicionar agent context (qual agente desencadeou?)

**Impacto**: ✅ Observabilidade 360°

### Fase 3 (Following Week) - Automation
- [ ] Implementar `RegressionDetector` em tempo real
- [ ] Auto-trigger DebugAgent em caso de anomalia
- [ ] Implementar `CausalAnalyzer` (correlação RBC)
- [ ] Dashboard de regressões com alertas

**Impacto**: ✅ Auto-remediation funcional

---

## 🔗 Integração com Systems Existentes

### 1. ConsciousnessStateManager
```python
# Já salva em JSONL, agora adicionar trace_id
snapshot = {
    "trace_id": cycle_context.trace_id,  # NOVO
    "cycle_id": cycle_id,
    "phi": phi,
    # ... remaining fields ...
}
```

### 2. OrchestratorMetricsCollector
```python
# Já coleta latência, agora adicionar agent context
metrics = {
    "agent": "CodeAgent",
    "latency_ms": 125,
    "trace_id": trace_id,  # NOVO - permite correlação
    "cycle_id": cycle_id,  # NOVO
}
```

### 3. ModuleMetricsCollector
```python
# Já persiste, agora com trace_id
module_metric = {
    "module": "SharedWorkspace",
    "metric": "embedding_update_count",
    "value": 256,
    "trace_id": trace_id,  # NOVO
}
```

---

## 📊 COMPARISON: Before vs After

### Before (Current)
```
Event: CodeAgent publishes "code_generated"
  ↓ (LOST CORRELATION)
Cycle N: ϕ drops from 0.75 → 0.50
  ↓ (No one knows why!)
Warning: "ΔΦCORRELATION_VIOLATED"
  ↓ (Manual debugging required)
Developer: "Which agent caused this?"
```

### After (Proposed)
```
Event: CodeAgent publishes "code_generated"
  ├─ trace_id = 550e8400-e29b-41d4-a716-446655440000
  └─ Records in events_traced.jsonl
                    ↓
Cycle N: ϕ drops from 0.75 → 0.50
  ├─ Same trace_id in span
  └─ Records in unified_metrics.jsonl
                    ↓
RegressionDetector triggers:
  ├─ φ < 0.50 (CRITICAL)
  └─ Automatically queries CausalAnalyzer
                    ↓
CausalAnalyzer returns:
  ├─ Root cause: CodeAgent (trace_id correlation)
  ├─ Latency impact: +450ms during cycle N
  └─ Recommendation: Review CodeAgent generation logic
                    ↓
Auto-trigger DebugAgent:
  ├─ Focus on trace_id = 550e...
  ├─ Replay cycle with same inputs
  └─ Identify regression source
                    ↓
Developer sees:
  ✅ "CodeAgent regression detected at cycle 150"
  ✅ "Root cause: Embedding dimension mismatch"
  ✅ "Suggested fix: Align CodeAgent output to 256-dim"
```

---

## 🎯 Success Metrics

After implementation:
- ⏱️ **MTTR** (Mean Time To Root Cause): 5min → 30sec
- 📊 **Regression Detection Latency**: 500 cycles → 1 cycle
- 🎯 **Alert Accuracy**: 60% false positives → 5% (via correlation)
- 🚀 **Auto-remediation Success Rate**: 0% → 40% (Phase 1)

---

## 📚 References

- OpenTelemetry Spec: https://opentelemetry.io/docs/spec/
- Distributed Tracing Best Practices: https://opentelemetry.io/docs/concepts/signals/traces/
- Causal Analysis in Distributed Systems: https://www.microsoft.com/en-us/research/publication/the-mystery-machine-end-to-end-performance-analysis-of-large-scale-internet-services/
- RNN-based Observability: Internal research (consciousness loop)

