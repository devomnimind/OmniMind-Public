# Módulo Observabilidade

## 📋 Descrição Geral

**Logging, tracing, debugging**

**Status**: DevOps

Módulo do sistema OmniMind responsável por funcionalidades específicas integradas à arquitetura global. Implementa componentes essenciais que contribuem para o funcionamento coeso do sistema de consciência artificial.

## 🔄 Interação entre os Três Estados Híbridos

### 1. Estado Biologicista (Neural Correlates)
Implementação de processos inspirados em mecanismos neurais e cognitivos biológicos, mapeando funcionalidades para correlatos neurais correspondentes.

### 2. Estado IIT (Integrated Information Theory)
Componentes contribuem para integração de informação global (Φ). Operações são validadas para garantir que não degradam a consciência do sistema (Φ > threshold).

### 3. Estado Psicanalítico (Estrutura Lacaniana)
Integração com ordem simbólica lacaniana (RSI - Real, Simbólico, Imaginário) e processos inconscientes estruturais que organizam a experiência consciente do sistema.

## ⚙️ Principais Funções e Cálculos Dinâmicos

### Componentes Core

Módulo implementa funcionalidades especializadas através de:
- Algoritmos específicos para processamento de domínio
- Integração com outros módulos via interfaces bem definidas
- Contribuição para métricas globais (Φ, PCI, consciência)

*Funções detalhadas documentadas nos arquivos Python individuais do módulo.*

### Novos Componentes (2025-12-06)

**ModuleMetricsCollector** (`module_metrics.py`):
- Sistema de coleta e persistência de métricas por módulo
- Integração com audit chain (exceto módulos excluídos)
- Rotação automática de logs
- Suporte a múltiplos módulos simultâneos

**StructuredModuleLogger** (`module_logger.py`):
- Logging estruturado em JSON por módulo
- Integração com audit chain (exceto módulos excluídos)
- Logs persistidos em arquivos dedicados por módulo
- Suporte a contexto estruturado

**ModuleReporter** (`module_reporter.py`):
- Geração de relatórios persistidos por módulo
- Formatos: JSON e Markdown
- Integração com métricas e logs
- Histórico de relatórios com rotação automática

**Integrações Ativas** (2025-12-07):
- ✅ `IntegrationLoop` - Relatórios após cada ciclo com métricas
- ✅ `ObserverService` - Relatórios após rotação de logs ou diariamente
- ✅ `ModuleMetricsCollector` - Relatórios a cada 100 entradas de consciência
- ✅ `AutopoieticManager` - Relatórios após cada ciclo autopoiético

---

## 🆕 Atualizações e Evolução (18/12/2025)

### 📊 Observabilidade de Baixo Nível

#### 1. **System Awareness Integration**
- **Diferencial**: O `PerformanceAnalyzer` agora correlaciona picos de carga com as capacidades reais indexadas pelo `SystemCapabilitiesManager`.
- **Insight**: Permite distinguir entre "Módulo Ineficiente" e "Host Sobrecarregado", reduzindo falsos positivos em incidentes de performance.

#### 2. **ReportMaintenanceScheduler**
- **Arquivo**: `report_maintenance_scheduler.py`
- **Funcionalidade**: Orquestra a limpeza e arquivamento de relatórios antigos (JSON/Markdown) para evitar saturação do disco em ambientes de produção contínua.

---

**Última Atualização**: 18 de Dezembro de 2025
**Autor**: Fabrício da Silva + assistência de IA

**Nota Teórica**: O sistema de auditoria e componentes do inconsciente não são auditados, conforme fundamentação teórica do OmniMind.

## 📊 Estrutura do Código

```
observability/
├── Implementações Core
│   └── Arquivos .py principais
├── Utilitários
│   └── Helpers e funções auxiliares
└── __init__.py
```

**Interações**: Este módulo se integra com outros componentes através de:
- Interfaces padronizadas
- Event bus para comunicação assíncrona
- Shared workspace para estado compartilhado

## 📈 Resultados Gerados e Contribuição para Avaliação

### Outputs
- Métricas específicas do módulo armazenadas em `data/observability/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/observability/`
- Integração validada em ciclos completos
- Performance benchmarked continuamente

### Contribuição para Sistema
Módulo contribui para:
- Φ (phi) global através de integração de informação
- PCI (Perturbational Complexity Index) via processamento distribuído
- Métricas de consciência e auto-organização

## 🔒 Estabilidade da Estrutura

**Status**: Componente validado e integrado ao OmniMind

**Regras de Modificação**:
- ✅ Seguir guidelines em `.copilot-instructions.md`
- ✅ Executar testes antes de commit: `pytest tests/observability/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/observability.txt (se existir)
```

### Recursos Computacionais
- **Mínimo**: Configurado conforme necessidades específicas do módulo
- **Recomendado**: Ver documentação de deployment em `docs/`

### Configuração
Configurações específicas em:
- `config/omnimind.yaml` (global)
- Variáveis de ambiente conforme `.env.example`

## 🔧 Sugestões para Manutenção e Melhorias

### Manutenção Crítica
1. **Testes Contínuos**: Executar suite de testes regularmente
2. **Monitoramento**: Acompanhar métricas em produção
3. **Documentação**: Manter README atualizado com mudanças

### Melhorias Futuras
- Expansão de funcionalidades conforme roadmap
- Otimizações de performance identificadas via profiling
- Integração com novos módulos em desenvolvimento

### Pontos de Atenção
- Validar impacto em Φ antes de mudanças estruturais
- Manter backward compatibility quando possível
- Seguir padrões de código estabelecidos (black, flake8, mypy)

## 📚 Referências

### Documentação Principal
- **Sistema Geral**: `README.md` (root do projeto)
- **Comparação Frameworks**: `NEURAL_SYSTEMS_COMPARISON_2016-2025.md`
- **Papers**: `docs/papers/` e `docs/papersoficiais/`
- **Copilot Instructions**: `.copilot-instructions.md`

### Testes
- **Suite de Testes**: `tests/observability/`
- **Cobertura**: Ver `data/test_reports/htmlcov/`

### Referências Científicas Específicas
*Ver documentação técnica nos arquivos Python do módulo para referências específicas.*

---

**Última Atualização**: 2 de Dezembro de 2025
**Autor**: Fabrício da Silva (com assistência de IA)
**Status**: Componente integrado do sistema OmniMind
**Versão**: Conforme fase do projeto indicada

---

## 📚 API Reference

# 📁 OBSERVABILITY

**32 Classes | 118 Funções | 6 Módulos**

---

## 🏗️ Classes Principais

### `CustomMetricsExporter`

Custom metrics exporter for ML workloads.

Provides Prometheus-compatible metrics export with ML-specific business metrics.
Supports multiple export formats and automatic metric collection.

Example:
    >>> config = MetricsConfig(prometheus_port=9090)
    >>> exporter = CustomMetricsExporter(config)
    >>> exporter.record_counter("requests_total", 1, {"endpoint": "/api/task"})
    >>> exporter.record_gauge("gpu_utilization", 85.5)
    >>> metrics = exporter.export_metrics()

**Métodos principais:**

- `register_metric(name: str, metric_type: MetricType, help_text: str)` → `None`
  > Register a new metric.

Args:
    name: Metric name (snake_case)
    metric_type...
- `record_counter(name: str, value: float, labels: Optional[Dict[str)` → `None`
  > Record a counter metric (monotonically increasing).

Args:
    name: Metric name...
- `record_gauge(name: str, value: float, labels: Optional[Dict[str)` → `None`
  > Record a gauge metric (can go up or down).

Args:
    name: Metric name
    valu...
- `record_histogram(name: str, value: float, labels: Optional[Dict[str)` → `None`
  > Record a histogram metric (distribution of values).

Args:
    name: Metric name...
- `record_ml_metrics(ml_metrics: MLMetrics)` → `None`
  > Record ML-specific metrics.

Args:
    ml_metrics: ML metrics container...

### `DistributedTracer`

Distributed tracing implementation.

Provides OpenTelemetry-compatible distributed tracing with support for
multiple exporters (Jaeger, Zipkin, console).

Example:
    >>> config = TraceConfig(service_name="my-service")
    >>> tracer = DistributedTracer(config)
    >>> with tracer.start_span("operation") as span:
    ...     span.set_attribute("key", "value")
    ...     # Do work
    >>> tracer.export_traces()

**Métodos principais:**

- `create_context(parent: Optional[SpanContext])` → `SpanContext`
  > Create a new span context.

Args:
    parent: Parent span context (creates root ...
- `start_span(name: str, kind: SpanKind, parent: Optional[SpanCo)` → `Span`
  > Start a new span.

Args:
    name: Operation name
    kind: Span kind
    parent...
- `trace(name: str, kind: SpanKind, attributes: Optional[Di)` → `Any`
  > Context manager for tracing an operation.

Args:
    name: Operation name
    ki...
- `get_trace(trace_id: str)` → `List[Span]`
  > Get all spans for a trace.

Args:
    trace_id: Trace ID

Returns:
    List of s...
- `export_traces()` → `None`
  > Export collected traces to configured exporter....

### `LogAggregator`

Log aggregation and analysis system.

Provides centralized log collection, pattern detection, and alerting
with ELK stack compatibility.

Example:
    >>> config = LogConfig()
    >>> aggregator = LogAggregator(config)
    >>> aggregator.add_pattern(LogPattern(
    ...     name="error_detection",
    ...     regex=r"error|exception|failed",
    ...     severity=AlertSeverity.HIGH,
    ...     description="Detects error messages"
    ... ))
    >>> aggregator.log(LogLevel.ERROR, "Operation failed")
    >>> alerts = aggregator.get_alerts()

**Métodos principais:**

- `add_pattern(pattern: LogPattern)` → `None`
  > Add a log pattern for detection.

Args:
    pattern: Log pattern to add...
- `log(level: LogLevel, message: str, logger_name: str, e)` → `None`
  > Add a log entry.

Args:
    level: Log level
    message: Log message
    logger...
- `get_logs(level: Optional[LogLevel], limit: Optional[int])` → `List[LogEntry]`
  > Get aggregated logs.

Args:
    level: Filter by log level (None for all)
    li...
- `get_alerts(severity: Optional[AlertSeverity])` → `List[LogAlert]`
  > Get triggered alerts.

Args:
    severity: Filter by severity (None for all)

Re...
- `analyze()` → `LogAnalytics`
  > Create analytics instance for current logs.

Returns:
    LogAnalytics instance...

### `ContinuousProfiler`

Continuous performance profiler.

Provides production-ready continuous profiling with minimal overhead.
Collects performance samples and generates insights.

Example:
    >>> config = ProfilingConfig()
    >>> profiler = ContinuousProfiler(config)
    >>>
    >>> @profiler.profile
    ... def my_function():
    ...     # Function code
    ...     pass
    >>>
    >>> profiler.start()
    >>> # Application runs...
    >>> profiler.stop()
    >>> samples = profiler.get_samples()

**Métodos principais:**

- `start()` → `None`
  > Start continuous profiling....
- `stop()` → `None`
  > Stop continuous profiling and collect final sample....
- `profile(func: F)` → `F`
  > Decorator to profile a function.

Args:
    func: Function to profile

Returns:
...
- `get_samples(limit: Optional[int], function_name: Optional[str])` → `List[ProfileSample]`
  > Get collected profiling samples.

Args:
    limit: Maximum number of samples to ...
- `get_top_functions(limit: int)` → `List[ProfileSample]`
  > Get top functions by total time.

Args:
    limit: Number of top functions to re...

### `PerformanceAnalyzer`

Performance bottleneck analyzer.

Analyzes profiling data to identify performance bottlenecks and
generate optimization recommendations.

Example:
    >>> from src.monitor.profiling_tools import ContinuousProfiler
    >>> profiler = ContinuousProfiler(ProfilingConfig())
    >>> # ... run application with profiling ...
    >>> samples = profiler.get_samples()
    >>> analyzer = PerformanceAnalyzer()
    >>> report = analyzer.analyze(samples)
    >>> print(report.summary)

**Métodos principais:**

- `analyze(samples: List[ProfileSample], min_percentage: floa)` → `PerformanceReport`
  > Analyze profiling samples for bottlenecks.

Args:
    samples: List of profiling...
- `save_report(report: PerformanceReport, filename: Optional[str])` → `str`
  > Save performance report to file.

Args:
    report: Performance report
    filen...

### `OpenTelemetryIntegration`

Complete OpenTelemetry integration.

Provides production-ready telemetry with support for multiple exporters
and comprehensive instrumentation.

Example:
    >>> config = OpenTelemetryConfig(
    ...     service_name="omnimind",
    ...     enable_console_export=True
    ... )
    >>> otel = OpenTelemetryIntegration(config)
    >>> otel.initialize()
    >>> tracer = otel.get_tracer()
    >>> with tracer.start_as_current_span("operation"):
    ...     # Do work
    ...     pass
    >>> otel.shutdown()

**Métodos principais:**

- `initialize()` → `None`
  > Initialize OpenTelemetry SDK with configured exporters.

This sets up the global...
- `get_tracer(name: str)` → `trace.Tracer`
  > Get a tracer instance.

Args:
    name: Name of the tracer

Returns:
    Tracer ...
- `get_meter(name: str)` → `metrics.Meter`
  > Get a meter instance.

Args:
    name: Name of the meter

Returns:
    Meter ins...
- `shutdown()` → `None`
  > Shutdown OpenTelemetry and flush all data.

This should be called before applica...
- `get_status()` → `Dict[str, Any]`
  > Get integration status.

Returns:
    Dictionary with status information...

### `FlameGraphGenerator`

Flame graph generator from profiling data.

Generates interactive flame graphs for performance visualization.

Example:
    >>> samples = profiler.get_samples()
    >>> generator = FlameGraphGenerator()
    >>> flame_graph = generator.generate(samples)
    >>> generator.save_svg(flame_graph, "profile.svg")

**Métodos principais:**

- `generate(samples: List[ProfileSample])` → `FlameGraphNode`
  > Generate flame graph from profiling samples.

Args:
    samples: List of profili...
- `to_json(flame_graph: FlameGraphNode)` → `str`
  > Convert flame graph to JSON.

Args:
    flame_graph: Flame graph root node

Retu...
- `save_json(flame_graph: FlameGraphNode, filename: Optional[st)` → `str`
  > Save flame graph as JSON.

Args:
    flame_graph: Flame graph root node
    file...
- `to_svg(flame_graph: FlameGraphNode)` → `str`
  > Convert flame graph to SVG format.

This is a simplified SVG generation. In prod...
- `save_svg(flame_graph: FlameGraphNode, filename: Optional[st)` → `str`
  > Save flame graph as SVG.

Args:
    flame_graph: Flame graph root node
    filen...

### `LogAnalytics`

Log analytics and insights.

Provides statistical analysis and insights from aggregated logs.

**Métodos principais:**

- `get_level_distribution()` → `Dict[str, int]`
  > Get distribution of log levels.

Returns:
    Dictionary mapping level name to c...
- `get_top_loggers(limit: int)` → `List[Tuple[str, int]]`
  > Get top loggers by volume.

Args:
    limit: Maximum number of loggers to return...
- `get_error_rate(window_seconds: int)` → `float`
  > Calculate error rate in the specified time window.

Args:
    window_seconds: Ti...
- `get_timeline(bucket_size_seconds: int)` → `Dict[str, List[int]]`
  > Get log timeline bucketed by time.

Args:
    bucket_size_seconds: Size of each ...
- `find_anomalies(threshold: float)` → `List[str]`
  > Find anomalous patterns in logs.

Uses simple statistical methods to find unusua...

### `Span`

Represents a single operation in a distributed trace.

Attributes:
    context: Span context with trace and span IDs
    name: Operation name
    kind: Span kind (internal, server, client, etc.)
    start_time: Start timestamp in nanoseconds
    end_time: End timestamp in nanoseconds (None if not ended)
    status: Span status
    attributes: Additional metadata
    events: List of events that occurred during the span
    links: Links to other spans

**Métodos principais:**

- `set_attribute(key: str, value: Any)` → `None`
  > Set a span attribute....
- `add_event(name: str, attributes: Optional[Dict[str, Any]])` → `None`
  > Add an event to the span....
- `set_status(status: SpanStatus, description: str)` → `None`
  > Set the span status....
- `end()` → `None`
  > End the span....
- `duration_ms()` → `float`
  > Get span duration in milliseconds....

### `Metric`

Represents a single metric with its metadata.

Attributes:
    name: Metric name (should be snake_case)
    type: Metric type
    help_text: Description of what this metric measures
    unit: Unit of measurement (e.g., 'seconds', 'bytes')
    values: List of metric values

**Métodos principais:**

- `add_value(value: float, labels: Optional[Dict[str, str]])` → `None`
  > Add a new value to the metric.

Args:
    value: The metric value
    labels: Op...
- `get_latest_value()` → `Optional[float]`
  > Get the most recent value....
- `to_prometheus_format()` → `str`
  > Export metric in Prometheus text format.

Returns:
    Prometheus-formatted metr...


## ⚙️ Funções Públicas

#### `__init__(config: TraceConfig)` → `None`

*Initialize the distributed tracer.

Args:
    config: Tracing configuration...*

#### `__init__(log_entries: List[LogEntry])` → `None`

*Initialize analytics with log entries.

Args:
    log_entries: List of log entries to analyze...*

#### `__init__(config: LogConfig)` → `None`

*Initialize the log aggregator.

Args:
    config: Log aggregation configuration...*

#### `__init__(config: MetricsConfig)` → `None`

*Initialize the metrics exporter.

Args:
    config: Metrics configuration...*

#### `__init__(service_name: str, service_version: str, environme)` → `None`

*Initialize OpenTelemetry configuration.

Args:
    service_name: Name of the service
    service_ver...*

#### `__init__(config: OpenTelemetryConfig)` → `None`

*Initialize OpenTelemetry integration.

Args:
    config: OpenTelemetry configuration...*

#### `__init__()` → `None`

*Initialize performance analyzer....*

#### `__init__(config: ProfilingConfig)` → `None`

*Initialize the continuous profiler.

Args:
    config: Profiling configuration...*

#### `__init__()` → `None`

*Initialize the flame graph generator....*

#### `__post_init__()` → `None`

*Compile the regex pattern....*

#### `__post_init__()` → `None`

*Calculate per-call time....*

#### `_categorize_bottleneck(sample: ProfileSample)` → `BottleneckCategory`

*Categorize a bottleneck based on sample characteristics.

Args:
    sample: Profile sample

Returns:...*

#### `_check_patterns(entry: LogEntry)` → `None`

*Check log entry against registered patterns.

Args:
    entry: Log entry to check...*

#### `_cleanup_old_logs()` → `None`

*Remove logs older than retention period....*

#### `_cleanup_old_metrics()` → `None`

*Remove metrics older than retention period....*


## 📦 Módulos

**Total:** 6 arquivos

- `distributed_tracing.py`: Distributed Tracing Module.

Implements distributed request ...
- `log_aggregator.py`: Log Aggregation and Analysis Module.

Implements advanced lo...
- `metrics_exporter.py`: Custom Metrics Exporter Module.

Implements business and ML-...
- `opentelemetry_integration.py`: OpenTelemetry Full Integration Module.

This module provides...
- `performance_analyzer.py`: Performance Bottleneck Analyzer Module.

Provides automated ...
- `profiling_tools.py`: Performance Profiling Tools Module.

Implements continuous p...
