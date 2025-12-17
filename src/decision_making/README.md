# Módulo Motor de Decisão

## 📋 Descrição Geral

**Reasoning, planejamento, escolhas**

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
decision_making/
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
- Métricas específicas do módulo armazenadas em `data/decision_making/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/decision_making/`
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
- ✅ Executar testes antes de commit: `pytest tests/decision_making/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/decision_making.txt (se existir)
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
- **Suite de Testes**: `tests/decision_making/`
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

# 📁 DECISION_MAKING

**24 Classes | 94 Funções | 4 Módulos**

---

## 🏗️ Classes Principais

### `EthicalDecisionMaker`

Autonomous ethical decision making system.

Features:
- Multi-framework ethical analysis
- Stakeholder impact assessment
- Transparent justifications
- Integration with decision trees and RL

**Métodos principais:**

- `decide(dilemma: EthicalDilemma)` → `EthicalOutcome`
  > Make an ethical decision.

Args:
    dilemma: Ethical dilemma to resolve

Return...
- `get_ethics_metrics()` → `Dict[str, Any]`
  > Get metrics about ethical decisions....

### `DecisionTree`

Intelligent decision tree with learning capabilities.

Features:
- Adaptive thresholds based on experience
- Integration with ethical frameworks
- Explainable decision paths
- Online learning from outcomes

**Métodos principais:**

- `decide(context: Dict[str, Any])` → `DecisionOutcome`
  > Make a decision based on current context.

Args:
    context: Dictionary contain...
- `provide_feedback(outcome: DecisionOutcome, success: bool)` → `None`
  > Provide feedback to improve decision making.

Args:
    outcome: The decision ou...
- `get_performance_metrics()` → `Dict[str, Any]`
  > Get performance metrics for the tree....

### `GoalHierarchy`

Manages hierarchical goal relationships.

Features:
- Parent-child goal relationships
- Goal dependency tracking
- Progress propagation

**Métodos principais:**

- `add_goal(goal: Goal)` → `None`
  > Add a goal to the hierarchy....
- `get_goal(goal_id: str)` → `Optional[Goal]`
  > Get a goal by ID....
- `get_children(goal_id: str)` → `List[Goal]`
  > Get child goals....
- `get_parent(goal_id: str)` → `Optional[Goal]`
  > Get parent goal....
- `get_root_goals()` → `List[Goal]`
  > Get all root (top-level) goals....

### `GoalSetter`

Autonomous goal generation and management system.

Features:
- Self-directed goal creation
- Priority-based scheduling
- Goal adaptation based on context
- Integration with decision making

**Métodos principais:**

- `generate_goal(context: Dict[str, Any], parent_goal_id: Optional[)` → `Goal`
  > Generate a new goal based on current context.

Args:
    context: Current system...
- `activate_goal(goal_id: str)` → `bool`
  > Activate a goal for pursuit.

Args:
    goal_id: Goal ID to activate

Returns:
 ...
- `complete_goal(goal_id: str, success: bool)` → `None`
  > Mark a goal as completed or failed....
- `get_next_goal()` → `Optional[Goal]`
  > Get the next goal to pursue based on priority....
- `get_metrics()` → `Dict[str, Any]`
  > Get goal setting metrics....

### `PolicyGradientAgent(RLAgent)`

Policy gradient agent with parametric policy.

Features:
- Direct policy optimization
- Stochastic policy representation
- Suitable for continuous action spaces

**Métodos principais:**

- `select_action(state: RLState, available_actions: List[RLAction])` → `RLAction`
  > Select action using stochastic policy....
- `update(transition: RLTransition)` → `None`
  > Store transition for episode update....
- `get_policy_metrics()` → `Dict[str, Any]`
  > Get metrics about the learned policy....

### `Goal`

Represents an autonomous goal.

**Métodos principais:**

- `update_progress(progress: float)` → `None`
  > Update goal progress....
- `is_overdue()` → `bool`
  > Check if goal is overdue....
- `time_remaining()` → `Optional[float]`
  > Get time remaining until deadline....

### `GoalOptimizer`

Optimizes goal pursuit strategies.

Features:
- Resource allocation optimization
- Goal reordering based on dependencies
- Deadline management

**Métodos principais:**

- `optimize_schedule()` → `List[Goal]`
  > Optimize goal execution schedule.

Returns:
    Ordered list of goals to pursue...
- `reallocate_resources(total_resources: float)` → `Dict[str, float]`
  > Allocate resources to goals.

Args:
    total_resources: Total resources availab...

### `DecisionTreeBuilder`

Builder for creating decision trees.

**Métodos principais:**

- `add_node(node_id: str, criterion_type: DecisionCriterion, q)` → `'DecisionTreeBuilder'`
  > Add a node to the tree....
- `add_edge(parent_id: str, child_id: str, edge_label: str)` → `'DecisionTreeBuilder'`
  > Add an edge between nodes....
- `build(learning_rate: float, enable_adaptation: bool)` → `DecisionTree`
  > Build the decision tree....

### `RLState`

Represents a state in the RL environment.


### `RLAgent(ABC)`

Abstract base class for RL agents.

**Métodos principais:**

- `select_action(state: RLState, available_actions: List[RLAction])` → `RLAction`
  > Select action for given state....
- `update(transition: RLTransition)` → `None`
  > Update agent based on transition....
- `decay_exploration(decay_rate: float)` → `None`
  > Decay exploration rate over time....


## ⚙️ Funções Públicas

#### `__eq__(other: object)` → `bool`

*Check state equality....*

#### `__eq__(other: object)` → `bool`

*Check action equality....*

#### `__hash__()` → `int`

*Make state hashable for use in Q-tables....*

#### `__hash__()` → `int`

*Make action hashable....*

#### `__init__()` → `None`

*Initialize goal hierarchy....*

#### `__init__(max_concurrent_goals: int, enable_auto_generation:)` → `None`

*Initialize goal setter.

Args:
    max_concurrent_goals: Maximum number of concurrent active goals
 ...*

#### `__init__(goal_setter: GoalSetter)` → `None`

*Initialize goal optimizer.

Args:
    goal_setter: GoalSetter instance to optimize...*

#### `__init__(root: DecisionNode, name: str, learning_rate: floa)` → `None`

*Initialize decision tree.

Args:
    root: Root node of the tree
    name: Name of the decision tree...*

#### `__init__(name: str)` → `None`

*Initialize builder....*

#### `__init__(primary_framework: EthicalFramework, principle_wei)` → `None`

*Initialize ethical decision maker.

Args:
    primary_framework: Primary ethical framework to use
  ...*

#### `__init__(features: Dict[str, Any], state_id: Optional[str])` → `None`

*Initialize RL state.

Args:
    features: Dictionary of state features
    state_id: Optional unique...*

#### `__init__(name: str, learning_rate: float, discount_factor: )` → `None`

*Initialize RL agent.

Args:
    name: Agent name
    learning_rate: Learning rate (alpha)
    discou...*

#### `__init__(name: str, learning_rate: float, discount_factor: )` → `None`

*Initialize policy gradient agent....*

#### `__init__(num_states: int, num_actions: int, learning_rate: )` → `None`

*Initialize tabular Q-learning agent....*

#### `__post_init__()` → `None`

*Validate goal data....*


## 📦 Módulos

**Total:** 4 arquivos

- `autonomous_goal_setting.py`: Autonomous Goal Setting for Self-Directed AI.

This module i...
- `decision_trees.py`: Intelligent Decision Trees for Autonomous Decision Making.

...
- `ethical_decision_framework.py`: Ethical Decision Framework for Autonomous AI.

This module i...
- `reinforcement_learning.py`: Reinforcement Learning-based Decision Making for OmniMind.

...
