# Módulo Sistema de Motivação

## 📋 Descrição Geral

**Drives, incentivos, recompensas**

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
motivation/
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
- Métricas específicas do módulo armazenadas em `data/motivation/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/motivation/`
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
- ✅ Executar testes antes de commit: `pytest tests/motivation/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/motivation.txt (se existir)
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
- **Suite de Testes**: `tests/motivation/`
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

# 📁 MOTIVATION

**8 Classes | 29 Funções | 3 Módulos**

---

## 🏗️ Classes Principais

### `HawkingMotivationEngine`

Knowledge evaporation system via Hawking radiation analogy.

Knowledge that goes unused "evaporates" through Hawking radiation,
creating urgency to apply learned concepts before loss.

Key mechanisms:
- Temperature-based evaporation (hotter = faster evaporation)
- Correlation preservation (information paradox resolution)
- Frustration generation (productive discomfort)
- Motivation amplification (urgency before loss)

**Métodos principais:**

- `add_knowledge(knowledge_id: str, content: str, mass: float)` → `None`
  > Add new knowledge to the system.

Args:
    knowledge_id: Unique identifier
    ...
- `use_knowledge(knowledge_id: str)` → `bool`
  > Mark knowledge as used (prevents evaporation).

Args:
    knowledge_id: ID of kn...
- `add_correlation(knowledge_id: str, related_id: str, bidirectional:)` → `None`
  > Add correlation between knowledge items.

Args:
    knowledge_id: Source knowled...
- `evaporate_unused_knowledge(current_time: Optional[datetime])` → `Tuple[List[str], Dict[str, Any]]`
  > Evaporate unused memories, generating motivation signals.

Args:
    current_tim...
- `adjust_temperature(new_temperature: float)` → `None`
  > Adjust Hawking temperature (evaporation rate).

Args:
    new_temperature: New t...

### `SymbolicMandate`

Manages the agent's Symbolic Mandate.

Replaces 'AchievementEngine'.
The agent does not accumulate 'points' but 'registers acts'.

**Métodos principais:**

- `register_act(act_description: str, metadata: Optional[Dict[str,)` → `bool`
  > Register an act in the Symbolic Order.

Args:
    act_description: Description o...
- `get_mandate_status()` → `Dict[str, Any]`
  > Get current mandate status....

### `DesireEngine`

Implements Lacanian Desire for autonomous agents.

Replaces 'IntrinsicMotivationEngine'.
Instead of maximizing 'satisfaction', this engine manages 'Lack'.
The system acts because it *lacks* something (knowledge, completion, being),
not because it gets a cookie.

**Métodos principais:**

- `evaluate_task_outcome(task: str, output: Any, reflection: str, metadata:)` → `float`
  > Evaluate outcome based on its relation to Desire/Lack.

Args:
    task: Task des...
- `get_current_state()` → `Dict[str, Any]`
  > Get current desire state....

### `JouissanceTopology`

Tracks topological fixation points of jouissance.

**Métodos principais:**

- `register_fixation(signifier: str, intensity: float)` → `None`
  > Register a point where the system 'enjoys' (insists)....
- `to_dict()` → `Dict[str, Any]`
  > Convert to dictionary....

### `SymbolicState`

Tracks the subject's position in the Symbolic Order.

**Métodos principais:**

- `to_dict()` → `Dict[str, Any]`
  > Convert to dictionary....

### `KnowledgeItem`

Single piece of knowledge in the system.

Attributes:
    content: Knowledge content (description/identifier)
    mass: Knowledge "mass" (complexity/importance)
    last_used: Timestamp of last usage
    use_count: Number of times used
    correlations: Related knowledge items
    creation_time: When knowledge was acquired


### `DriveCirculation`

Represents the circulation of drive around the Object a.

**Métodos principais:**

- `circulate()` → `None`
  > Execute one circuit of the drive....

### `EvaporationEvent`

Record of knowledge evaporation.

Attributes:
    knowledge_id: ID of evaporated knowledge
    mass_lost: Amount of mass evaporated
    correlations_preserved: Correlations extracted before evaporation
    frustration_energy: Frustration generated by loss
    motivation_boost: Motivation to use remaining knowledge
    timestamp: When evaporation occurred



## ⚙️ Funções Públicas

#### `__init__(state_file: Optional[Path])` → `None`

*Initialize Symbolic Mandate.

Args:
    state_file: Path to save state...*

#### `__init__(base_temperature: float, evaporation_threshold_day)` → `None`

*Initialize Hawking motivation engine.

Args:
    base_temperature: Base Hawking temperature
    evap...*

#### `__init__(state_file: Optional[Path])` → `None`

*Initialize the Desire Engine.

Args:
    state_file: Path to save/load engine state...*

#### `__post_init__()` → `None`

*Initialize defaults....*

#### `_calculate_rate()` → `float`

*Calculate evaporation rate from Hawking temperature.

Hawking radiation rate increases with temperat...*

#### `_compute_frustration(item: KnowledgeItem, time_unused: timedelta)` → `float`

*Compute frustration from knowledge loss.

Args:
    item: Knowledge being lost
    time_unused: Time...*

#### `_compute_urgency_factor(evaporated_ids: List[str])` → `float`

*Compute overall urgency factor from evaporation events.

Args:
    evaporated_ids: IDs of evaporated...*

#### `_extract_correlations(item: KnowledgeItem)` → `List[str]`

*Extract correlations from knowledge before evaporation.

Information is preserved in correlations (i...*

#### `_generate_urgency(correlations: List[str])` → `float`

*Generate motivation urgency for correlated knowledge.

Args:
    correlations: Preserved correlation...*

#### `_identify_at_risk_correlations()` → `List[str]`

*Identify knowledge at risk of evaporation.

Returns:
    List of at-risk knowledge IDs...*

#### `_load_state()` → `None`

*Load state from disk....*

#### `_load_state()` → `None`

*Load state from disk....*

#### `_save_state()` → `None`

*Save state to disk....*

#### `_save_state()` → `None`

*Save state to disk....*

#### `add_correlation(knowledge_id: str, related_id: str, bidirectional:)` → `None`

*Add correlation between knowledge items.

Args:
    knowledge_id: Source knowledge ID
    related_id...*


## 📦 Módulos

**Total:** 3 arquivos

- `achievement_system.py`: Symbolic Mandate System (Phase 11.3)

Replaces "Achievement ...
- `hawking_motivation.py`: Hawking Radiation Motivation Engine - Knowledge Evaporation ...
- `intrinsic_rewards.py`: Desire Engine - Lacanian Implementation (Phase 11.3)

Replac...
