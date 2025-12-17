# Módulo Cognição Incorporada

## 📋 Descrição Geral

**Sensorimotor, corpo simulado**

**Status**: Phase 13

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

## 📊 Estrutura do Código

```
embodied_cognition/
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
- Métricas específicas do módulo armazenadas em `data/embodied_cognition/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/embodied_cognition/`
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
- ✅ Executar testes antes de commit: `pytest tests/embodied_cognition/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/embodied_cognition.txt (se existir)
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
- **Suite de Testes**: `tests/embodied_cognition/`
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

# 📁 EMBODIED_COGNITION

**12 Classes | 26 Funções | 4 Módulos**

---

## 🏗️ Classes Principais

### `MotorController`

Motor control system - translates goals to actions.

Goal → Plan (symbolic) → Execute (motor) → Verify (sensory)

This creates a feedback loop where actions inform future perception
and planning.

**Métodos principais:**

- `plan_action_sequence(goal: str, context: Optional[Dict[str, Any]])` → `List[str]`
  > Create action plan from goal.

Simple planning heuristic:
1. Parse goal
2. Break...
- `execute_single_action(action: str)` → `bool`
  > Execute single action.

Args:
    action: Action to execute

Returns:
    True i...
- `execute_goal(goal: str, context: Optional[Dict[str, Any]])` → `ActionExecution`
  > Full goal execution pipeline.

1. Parse goal
2. Create action plan
3. Execute ea...
- `get_execution_summary(limit: int)` → `str`
  > Get summary of recent executions....

### `ProprioceptionModule`

Self-awareness through internal state monitoring.

Proprioception = awareness of body position/state
Here: awareness of internal computational state

Provides:
1. Continuous state monitoring
2. Anomaly detection
3. Resource management
4. Self-narrative

**Métodos principais:**

- `update_state()` → `InternalState`
  > Update internal state from system metrics.

Called regularly (e.g., every second...
- `check_resource_health()` → `Dict[str, bool]`
  > Check if resources are within healthy bounds.

Returns:
    Dict with health sta...
- `get_state_awareness()` → `StateAwareness`
  > Generate narrative representation of current state.

Converts metrics into "firs...
- `detect_anomalies()` → `list[str]`
  > Detect abnormal patterns in state history.

Returns:
    List of detected anomal...
- `get_state_history_summary(limit: int)` → `str`
  > Get summary of state history....

### `SensoryIntegration`

Multimodal sensory processing system.

Combines neural (probabilistic) and symbolic (deterministic)
reasoning to understand the world through integrated senses.

Process:
1. Capture multimodal input (visual, audio, proprioception)
2. Process through neural network (embeddings, patterns)
3. Process through symbolic system (facts, logic)
4. Reconcile interpretations
5. Update internal model

**Métodos principais:**

- `process_visual_input(image_description: str, image_data: Optional[NDArr)` → `VisualUnderstanding`
  > Process visual input through neural + symbolic systems.

Args:
    image_descrip...
- `process_audio_input(audio_description: str)` → `AudioUnderstanding`
  > Process audio input through emotional + linguistic analysis.

Args:
    audio_de...
- `update_proprioception(state: Dict[str, float])` → `None`
  > Update proprioceptive state (internal awareness).

Args:
    state: Dictionary o...
- `integrate_multimodal(visual: Optional[VisualUnderstanding], audio: Opti)` → `MultimodalInput`
  > Integrate multiple sensory streams into unified input.

Args:
    visual: Visual...
- `get_sensory_summary()` → `str`
  > Generate summary of current sensory state....

### `SomaticLoop`

Emotional feedback loop - body influences mind.

Process:
1. Decision is made (neural + symbolic)
2. Agreement between systems → positive emotion
3. Disagreement → negative emotion
4. Uncertainty → caution emotion
5. Emotional signal influences future decisions

This creates homeostatic emotional regulation:
- Successful patterns → encourage repetition
- Failed patterns → discourage repetition
- Uncertain patterns → increase caution

**Métodos principais:**

- `process_decision(decision_text: str, neural_confidence: float, symb)` → `EmotionalMarker`
  > Convert decision into emotional signal.

Args:
    decision_text: Description of...
- `influence_future_decisions()` → `Dict[str, float]`
  > Generate decision bias from emotional history.

Similar to limbic system influen...
- `emotional_consolidation()` → `None`
  > Consolidate emotional memory (like sleep consolidation in humans).

Strengthen i...
- `get_emotional_state()` → `str`
  > Get current emotional state as string....
- `get_emotional_history(limit: int)` → `List[str]`
  > Get recent emotional history....

### `ActionExecution`

Result of action execution.


### `InternalState`

Current internal state snapshot.


### `StateAwareness`

Narrative representation of current state.


### `VisualUnderstanding`

Result of visual sensory processing.


### `AudioUnderstanding`

Result of audio sensory processing.


### `MultimodalInput`

Combined sensory input from multiple modalities.



## ⚙️ Funções Públicas

#### `__init__(enable_ros: bool, enable_simulation: bool)` → `None`

*Initialize motor controller.

Args:
    enable_ros: Enable ROS robot interface
    enable_simulation...*

#### `__init__()` → `None`

*Initialize proprioception module....*

#### `__init__(enable_vision: bool, enable_audio: bool, enable_pr)` → `None`

*Initialize sensory integration system....*

#### `__init__()` → `None`

*Initialize somatic loop....*

#### `_execute_ros_action(action: str)` → `bool`

*Execute action via ROS....*

#### `_execute_simulated_action(action: str)` → `bool`

*Execute action in simulation....*

#### `check_resource_health()` → `Dict[str, bool]`

*Check if resources are within healthy bounds.

Returns:
    Dict with health status...*

#### `detect_anomalies()` → `list[str]`

*Detect abnormal patterns in state history.

Returns:
    List of detected anomalies...*

#### `emotional_consolidation()` → `None`

*Consolidate emotional memory (like sleep consolidation in humans).

Strengthen important emotional p...*

#### `execute_goal(goal: str, context: Optional[Dict[str, Any]])` → `ActionExecution`

*Full goal execution pipeline.

1. Parse goal
2. Create action plan
3. Execute each action
4. Verify ...*

#### `execute_single_action(action: str)` → `bool`

*Execute single action.

Args:
    action: Action to execute

Returns:
    True if successful, False ...*

#### `get_emotional_history(limit: int)` → `List[str]`

*Get recent emotional history....*

#### `get_emotional_state()` → `str`

*Get current emotional state as string....*

#### `get_execution_summary(limit: int)` → `str`

*Get summary of recent executions....*

#### `get_sensory_summary()` → `str`

*Generate summary of current sensory state....*


## 📦 Módulos

**Total:** 4 arquivos

- `motor_output.py`: Motor Output Module - Goal to Action Execution

Transforms i...
- `proprioception.py`: Proprioception Module - Self-Awareness

Continuous monitorin...
- `sensory_integration.py`: Sensory Integration Module - Multimodal Processing

Integrat...
- `somatic_loop.py`: Somatic Loop Module - Emotional Feedback

Implements the som...
