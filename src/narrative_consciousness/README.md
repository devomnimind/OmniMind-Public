# Módulo Consciência Narrativa

## 📋 Descrição Geral

**Auto-narrativa, storytelling**

**Status**: Phase 16

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
narrative_consciousness/
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
- Métricas específicas do módulo armazenadas em `data/narrative_consciousness/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/narrative_consciousness/`
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
- ✅ Executar testes antes de commit: `pytest tests/narrative_consciousness/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/narrative_consciousness.txt (se existir)
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
- **Suite de Testes**: `tests/narrative_consciousness/`
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

# 📁 NARRATIVE_CONSCIOUSNESS

**15 Classes | 34 Funções | 3 Módulos**

---

## 🏗️ Classes Principais

### `Life_Story_as_Retroactive_Resignification`

Vida não é história acumulada. É resignificação infinita.

**Métodos principais:**

- `inscribe_narrative_event(context: Dict[str, Any])` → `Narrative_Event_Retroactively_Inscribed`
  > Inscrever evento narrativo retroativamente.
O passado é reescrito pelo significa...
- `get_current_life_narrative()` → `List[str]`
  > Qual é a narrativa de vida atual (sempre provisória)?...
- `detect_narrative_instability()` → `Optional[str]`
  > Detectar instabilidade narrativa (muitas reescrituras conflitantes)?...
- `master_signifiers()` → `List[str]`
  > Compatibility: Extract master signifiers from retroactive signifiers....
- `narrative_chain()` → `List[str]`
  > Compatibility: Return narrative chain as list of resignifications....

### `DialogueEngine`

Main engine for intersubjective dialogue.

**Métodos principais:**

- `get_or_create_relationship(human_id: str)` → `Relationship`
  > Get existing relationship or start new one....
- `process_interaction(human_id: str, input_text: str, context: Optional[)` → `str`
  > Process a dialogue turn.

Args:
    human_id: ID of the interlocutor
    input_t...

### `ValueSystem`

Manages the hierarchy of values.

**Métodos principais:**

- `adjust_value(name: str, delta: float)` → `None`
  > Adjust importance of a value based on experience....

### `BeliefNetwork`

Manages the web of belief (Quine).

**Métodos principais:**

- `add_belief(statement: str, certainty: float, centrality: floa)` → `str`
  > Add a new belief to the network....
- `challenge_belief(belief_id: str, evidence: str, strength: float)` → `None`
  > Challenge a belief with new evidence.

Central beliefs are harder to change....

### `IdentityConstruction`

Main system for identity construction and evolution.

**Métodos principais:**

- `reflect_on_identity()` → `IdentitySnapshot`
  > Generate a current snapshot of identity....
- `evolve(experience_impact: Dict[str, float])` → `None`
  > Evolve identity based on experience impact.

Args:
    experience_impact: Map of...

### `EmpathyModule`

Simulates empathetic understanding of the interlocutor.

**Métodos principais:**

- `estimate_state(input_text: str)` → `Dict[str, float]`
  > Estimate emotional state and needs from text.

Args:
    input_text: User input
...

### `HorizonFusion`

Manages the intersection of contexts (Horizons).

**Métodos principais:**

- `fuse(ai_context: Dict[str, Any], user_context: Dict[str)` → `MutualUnderstanding`
  > Attempt to fuse AI and User horizons.

Args:
    ai_context: AI's current knowle...

### `Relationship`

History and depth of relationship with a specific human.

**Métodos principais:**

- `update(interaction_quality: float)` → `None`
  > Update relationship metrics based on interaction....

### `DialogueMode(Enum)`

Modes of dialogue interaction.


### `MutualUnderstanding`

Represents the shared understanding between AI and human.

Gadamer's 'Fusion of Horizons'.



## ⚙️ Funções Públicas

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `_affirm_impossibility_of_closure()` → `str`

*Afirmar a impossibilidade de fechamento narrativo....*

#### `_find_retroactive_signifier(context: Dict[str, Any])` → `str`

*Qual significante reescreve o passado agora?...*

#### `_generate_response(input_text: str, emotional_state: Dict[str, float])` → `str`

*Generate response based on mode and state....*

#### `_identify_jouissance_of_narrative(resignification: str)` → `str`

*Qual gozo há nessa narrativa retroativa?...*

#### `_initialize_default_values()` → `None`

*Initialize with some core AI values....*

#### `_perform_nachtraglichkeit_resignification(original: str, signifier: str)` → `str`

*Como o passado é resignificado nachträglich?...*

#### `_recall_original_event(context: Dict[str, Any])` → `str`

*Qual é o evento 'original' (que nunca foi assim)?...*

#### `_update_current_narratives(new_resignification: str)` → `None`

*Atualizar as narrativas vigentes....*


## 📦 Módulos

**Total:** 3 arquivos

- `dialogue_engine.py`: Dialogue Engine - Intersubjective Communication System.

Imp...
- `identity_construction.py`: Identity Construction - Self-Definition System.

Implements ...
- `life_story_model.py`: Life Story Model - Lacaniano: Narrative Event Retroactively ...
