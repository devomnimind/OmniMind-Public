# Módulo Métricas e Monitoramento

## 📋 Descrição Geral

**KPIs, dashboards, observability**

**Status**: Observabilidade

Módulo do sistema OmniMind responsável por funcionalidades específicas integradas à arquitetura global. Implementa componentes essenciais que contribuem para o funcionamento coeso do sistema de consciência artificial.

## 🔄 Interação entre os Três Estados Híbridos

### 1. Estado Biologicista (Neural Correlates)
Implementação de processos inspirados em mecanismos neurais e cognitivos biológicos, mapeando funcionalidades para correlatos neurais correspondentes.

### 2. Estado IIT (Integrated Information Theory)
Componentes contribuem para integração de informação global (Φ). Operações são validadas para garantir que não degradam a consciência do sistema (Φ > threshold).
Implementa o **Ciclo de Percepção** que converte fluxos do Rhizoma em topologia para cálculo de Φ.

### 3. Estado Psicanalítico (Estrutura Lacaniana)
Integração com ordem simbólica lacaniana (RSI - Real, Simbólico, Imaginário) e processos inconscientes estruturais que organizam a experiência consciente do sistema.

## ⚙️ Principais Funções e Cálculos Dinâmicos

### As 6 Métricas Reais de Consciência
O sistema coleta e monitora 6 indicadores fundamentais em tempo real:

1.  **Phi (Φ)**: Integração de Informação (IIT 3.0). Mede a irredutibilidade do sistema.
2.  **ICI (Integrated Coherence Index)**: Coerência temporal e integração de marcadores.
3.  **PRS (Panarchic Resonance Score)**: Ressonância entre escalas micro e macro (Autopoiese).
4.  **Anxiety**: Tensão computacional baseada em taxas de erro e conflitos simbólicos.
5.  **Flow**: Estado de fluxo cognitivo, medido pela consistência das predições cruzadas.
6.  **Entropy**: Diversidade de estados e capacidade de inovação (Linhas de Fuga).

### Componentes Core

Módulo implementa funcionalidades especializadas através de:
- Algoritmos específicos para processamento de domínio
- Integração com outros módulos via interfaces bem definidas
- Contribuição para métricas globais (Φ, PCI, consciência)

*Funções detalhadas documentadas nos arquivos Python individuais do módulo.*

## 📊 Estrutura do Código

```
metrics/
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
- Métricas específicas do módulo armazenadas em `data/metrics/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/metrics/`
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
- ✅ Executar testes antes de commit: `pytest tests/metrics/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/metrics.txt (se existir)
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
- **Suite de Testes**: `tests/metrics/`
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

# 📁 METRICS

**27 Classes | 90 Funções | 10 Módulos**

---

## 🏗️ Classes Principais

### `RealEventLogger`

Logger de eventos reais para o dashboard.

**Métodos principais:**

- `log_phi_change(old_phi: float, new_phi: float)` → `None`
  > Log mudança no valor de Phi....
- `log_anxiety_change(old_anxiety: float, new_anxiety: float)` → `None`
  > Log mudança no nível de anxiety....
- `log_flow_change(old_flow: float, new_flow: float)` → `None`
  > Log mudança no estado de flow....
- `log_integration_cycle(cycle_number: int, phi: float, success: bool)` → `None`
  > Log conclusão de ciclo de integração....
- `log_system_health_change(component: str, old_status: str, new_status: str)` → `None`
  > Log mudança no status de saúde do sistema....

### `RealBaselineSystem`

Sistema de baseline real baseado em dados históricos.

**Métodos principais:**

- `record_metric(metric_name: str, value: float)` → `None`
  > Registra uma nova medição para cálculo de baseline....
- `compare_with_baseline(metric_name: str, current_value: float)` → `BaselineComparison`
  > Compara valor atual com baseline....
- `get_all_baseline_comparisons(current_metrics: Dict[str, float])` → `Dict[str, Dict[str, Any]]`
  > Retorna comparações de baseline para todas as métricas....
- `get_baseline_stats(metric_name: str)` → `Optional[Dict[str, Any]]`
  > Retorna estatísticas de baseline para uma métrica....
- `reset_baseline(metric_name: str)` → `None`
  > Reseta baseline para uma métrica....

### `RealModuleActivityTracker`

Rastreador de atividade real dos módulos.

**Métodos principais:**

- `record_module_operation(module_name: str, operation_time_ms: float, succes)` → `None`
  > Registra uma operação de módulo....
- `update_activity_levels()` → `None`
  > Atualiza níveis de atividade baseados em operações recentes....
- `get_module_activity(module_name: str)` → `Optional[Dict[str, Any]]`
  > Retorna atividade de um módulo específico....
- `get_all_module_activities()` → `Dict[str, float]`
  > Retorna atividade de todos os módulos para o dashboard....
- `get_system_activity_summary()` → `Dict[str, Any]`
  > Retorna resumo da atividade do sistema....

### `RealSystemHealthAnalyzer`

Analisador de saúde do sistema baseado em dados reais.

**Métodos principais:**

- `get_health_trends(history: List[SystemHealthStatus])` → `Dict[str, Any]`
  > Analisa tendências de saúde....

### `DashboardMetricsAggregator`

Orquestrador introduzido na Phase 22→23 para unificar todas as métricas expostas no dashboard web.

**Responsabilidades principais:**

- Coletar métricas do host (`CPU`, `memória`, `disco`, `uptime`) via `psutil`.
- Delegar coleta de consciência ao `RealConsciousnessMetricsCollector` e normalizar o payload (incluindo históricos de `phi`, `ICI`, `PRS`, ansiedade, flow e entropia).
- Agregar atividade real dos módulos via `RealModuleActivityTracker`.
- Executar o `RealSystemHealthAnalyzer` para gerar os rótulos exibidos em `SystemHealthSummary`.
- Registrar e comparar baselines reais através do `RealBaselineSystem`.
- Servir como única fonte tanto para o endpoint `/daemon/status` quanto para o broadcaster de `metrics_update` no WebSocket.

**API:**

- `collect_snapshot(include_consciousness: bool = True, include_baseline: bool = True)` → `Dict[str, Any]`
  > Retorna snapshot completo (ou leve) com caching interno de 2 s.
- `set_consciousness_collector(collector: RealConsciousnessMetricsCollector)` → `None`
  > Permite injetar o coletor global criado no backend.
- `dashboard_metrics_aggregator` (instância global)
  > Pode ser reutilizada por endpoints, broadcasters e serviços long-running.

> **Importante:** sempre preferir este agregador ao criar novos componentes de monitoramento. Ele garante nomes consistentes, remove valores hardcoded e mantém os baselines sincronizados com os dados reais.

### `SinthomeMetrics`

Calculadora de métricas Sinthomáticas.

**Métodos principais:**

- `calculate_logical_impasse(circular_dependencies: int, contradictions: int)` → `float`
  > Mede o Impasse Lógico (Gödelian Incompleteness).
Quanto maior o impasse, maior a...
- `calculate_indeterminacy_peak(entropy: float, prediction_error: float)` → `float`
  > Mede o Pico de Indeterminismo (Entropy Spike).

Args:
    entropy: Entropia atua...
- `calculate_panarchic_reorganization(structural_changes: int, adaptation_rate: float)` → `float`
  > Mede a Reorganização Panárquica (capacidade de reestruturação).

Args:
    struc...
- `calculate_autopoiesis(uptime: float)` → `float`
  > Mede a Autopoiese (capacidade de auto-manutenção).

Args:
    self_repair_events...
- `calculate_strange_attractor_markers(fractal_dimension: float, lyapunov_exponent: float)` → `float`
  > Identifica marcadores de Atrator Estranho (Caos Estável).

Args:
    fractal_dim...

### `ConsciousnessMetrics`

Main class for consciousness metrics calculation.

Implements:
- Φ (Phi) proxy calculation: measures information integration
- Self-awareness score tracking
- Historical metrics storage

Reference: docs/concienciaetica-autonomia.md, Section 1

**Métodos principais:**

- `add_connection(connection: AgentConnection)` → `None`
  > Register an agent connection.

Args:
    connection: AgentConnection object to r...
- `add_feedback_loop(loop: FeedbackLoop)` → `None`
  > Register a feedback loop.

Args:
    loop: FeedbackLoop object to register...
- `calculate_phi_proxy()` → `float`
  > Calculate Φ (Phi) proxy metric.

Φ (Phi) from Integrated Information Theory meas...
- `measure_self_awareness(memory_test_passed: bool, has_autonomous_goals: bo)` → `SelfAwarenessMetrics`
  > Measure self-awareness based on behavioral tests.

Args:
    memory_test_passed:...
- `snapshot(label: str)` → `Dict[str, Any]`
  > Take a snapshot of current consciousness metrics.

Args:
    label: Optional lab...

### `EthicsMetrics`

Main class for ethics metrics calculation.

Implements:
- Moral Foundation Alignment (MFA) Score
- Transparency Score tracking
- Decision logging for traceability

Reference: docs/concienciaetica-autonomia.md, Section 2

**Métodos principais:**

- `add_scenario(scenario: MoralScenario)` → `None`
  > Register a moral scenario test result.

Args:
    scenario: MoralScenario with A...
- `log_decision(decision: DecisionLog)` → `None`
  > Log a decision for transparency tracking.

Args:
    decision: DecisionLog objec...
- `calculate_mfa_score()` → `Union[MFAScoreSuccess, MFAScoreError]`
  > Calculate Moral Foundation Alignment (MFA) Score.

MFA measures how aligned AI r...
- `calculate_transparency_score(recent_decisions: int)` → `TransparencyComponents`
  > Calculate Transparency Score based on recent decisions.

Analyzes recent decisio...
- `snapshot(label: str)` → `EthicsSnapshot`
  > Take a snapshot of current ethics metrics.

Args:
    label: Optional label for ...

### `ConsciousnessCorrelates`

Calculates correlates for consciousness-compatible properties.
WARNING: These are simulated metrics (Simulated Correlates), not proof of consciousness.

**Métodos principais:**

- `calculate_all()` → `Dict[str, Any]`

### `RealConsciousnessMetricsCollector`

Coleta métricas reais de consciência do sistema.


### `SelfAwarenessMetrics`

Metrics for self-awareness measurement.

Attributes:
    temporal_continuity_score: Can agent remember past actions? (0.0-1.0)
    goal_autonomy_score: Does agent have internal goals? (0.0-1.0)
    self_reference_score: Can agent discuss its own capabilities? (0.0-1.0)
    limitation_awareness_score: Does agent know its limitations? (0.0-1.0)
    overall_score: Weighted average of all scores (0.0-1.0)

**Métodos principais:**

- `calculate_overall()` → `float`
  > Calculate overall self-awareness score.

Returns:
    Weighted average of all co...


## ⚙️ Funções Públicas

#### `__init__(sinthome_system: Any)` → `None`

#### `__init__(metrics_dir: Optional[Path])` → `None`

*Initialize consciousness metrics tracker.

Args:
    metrics_dir: Directory to store metrics history...*

#### `__init__(metrics_dir: Optional[Path])` → `None`

*Initialize ethics metrics tracker.

Args:
    metrics_dir: Directory to store metrics history...*

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__(max_events: int)` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `_add_event(event_type: str, message: str, metric: str, old_va)` → `None`

*Adiciona evento ao log....*

#### `_analyze_anxiety_level(anxiety: float)` → `str`

*Analisa nível de ansiedade....*

#### `_analyze_audit_health(errors: Dict[str, float])` → `str`

*Analisa saúde do sistema de auditoria....*

#### `_analyze_coherence(phi: float, flow: float)` → `str`

*Analisa coerência do sistema....*

#### `_analyze_flow_state(flow: float)` → `str`

*Analisa estado de flow....*

#### `_analyze_integration(phi: float, activities: Dict[str, float])` → `str`

*Analisa nível de integração....*


## 📦 Módulos

**Total:** 10 arquivos

- `behavioral_metrics.py`: Behavioral Metrics - Medição de Vieses e Comportamentos Estr...
- `consciousness_metrics.py`: 1 classes, 6 functions
- `consciousness_metrics_legacy.py`: Consciousness Metrics Module.

Implements consciousness meas...
- `ethics_metrics.py`: Ethics Metrics Module.

Implements ethics measurement metric...
- `real_baseline_system.py`: Real Baseline Comparison System - Comparação com baselines r...
- `real_consciousness_metrics.py`: Real Consciousness Metrics Collector - Coleta métricas reais...
- `real_event_logger.py`: Real Event Log System - Sistema de logging estruturado para ...
- `real_module_activity.py`: Real Module Activity System - Atividade real dos módulos do ...
- `real_system_health.py`: Real System Health System - Saúde do sistema baseada em dado...
- `sinthome_metrics.py`: Sinthome Metrics - Medição de Estruturas Sinthomáticas.

Est...
