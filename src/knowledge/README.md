# Módulo Knowledge (DEPRECATED)

## ⚠️ STATUS: DEPRECATED

**Data de Deprecação**: 2025-12-07
**Phase**: 26A (não implementado)

Este módulo foi planejado como parte do Phase 26A (Knowledge) mas **nunca foi implementado**. As funcionalidades foram integradas em `src/memory/` com abordagem unificada e Lacaniana.

---

## 📋 MÓDULOS PLANEJADOS (NÃO IMPLEMENTADOS)

### 1. `declarative_layer.py`
**Substituído por**: `src.memory.semantic_memory.SemanticMemory`
- **Arquivo**: `src/memory/semantic_memory.py`
- **Funcionalidade**: Armazenamento de conceitos declarativos e relações semânticas
- **Status**: ✅ Implementado e operacional

**Migração**:
```python
# ANTES (deprecated):
from knowledge.declarative_layer import Concept, DeclarativeLayer
layer = DeclarativeLayer()
concept = Concept(name="consciousness", ...)
layer.add_concept(concept)

# DEPOIS (atual):
from src.memory.semantic_memory import SemanticMemory, Concept
memory = SemanticMemory()
concept = Concept(name="consciousness", attributes={...})
memory.store_concept(concept.name, concept.attributes)
memory.relate_concepts("consciousness", "awareness", "related_to")
```

---

### 2. `episodic_layer.py`
**Substituído por**: `src.memory.narrative_history.NarrativeHistory` (Lacanian)
- **Arquivo**: `src/memory/narrative_history.py`
- **Funcionalidade**: Memória episódica com abordagem Lacaniana (construção retroativa)
- **Status**: ✅ Implementado e operacional (2025-12-05)

**Migração**:
```python
# ANTES (deprecated):
from knowledge.episodic_layer import Episode, EpisodicLayer
layer = EpisodicLayer()
episode = Episode(...)
layer.store_episode(episode)

# DEPOIS (atual - Lacanian):
from src.memory.narrative_history import NarrativeHistory
history = NarrativeHistory()
# Inscrição sem significado (Lacanian)
event_id = history.inscribe_event(
    {"task": "learn", "action": "read", "result": "understood"},
    without_meaning=True
)
# Ressignificação retroativa (Nachträglichkeit)
history.retroactive_signification(event_id, "This means understanding")
# Construção narrativa
narrative = history.construct_narrative("learning process")
```

**NOTA**: `NarrativeHistory` usa `EpisodicMemory` como backend, mas com semântica Lacaniana.

---

### 3. `procedural_layer.py`
**Substituído por**: `src.memory.procedural_memory.ProceduralMemory`
- **Arquivo**: `src/memory/procedural_memory.py`
- **Funcionalidade**: Armazenamento de habilidades e procedimentos ("knowing how")
- **Status**: ✅ Implementado e operacional

**Migração**:
```python
# ANTES (deprecated):
from knowledge.procedural_layer import ProceduralLayer, Rule
layer = ProceduralLayer()
rule = Rule(id="rule1", name="rule1", ...)
layer.store_rule(rule)

# DEPOIS (atual):
from src.memory.procedural_memory import ProceduralMemory, Skill
memory = ProceduralMemory()
skill = memory.learn_skill(
    name="problem_solving",
    steps=["analyze", "plan", "execute", "validate"],
    parameters={"timeout": 30}
)
# Execução de habilidade
result = memory.execute_skill("problem_solving", context={...})
```

---

### 4. `knowledge_integrator.py`
**Substituído por**: Integração via `src.memory.*` (módulos unificados)
- **Arquivos**: Múltiplos arquivos em `src/memory/`
- **Funcionalidade**: Integração de camadas de conhecimento
- **Status**: ✅ Implementado e operacional

**Migração**:
```python
# ANTES (deprecated):
from knowledge.knowledge_integrator import KnowledgeIntegrator
from knowledge.declarative_layer import Concept
from knowledge.episodic_layer import Episode
from knowledge.procedural_layer import Rule
integrator = KnowledgeIntegrator()
integrated = integrator.integrate(concept, episode, rule)

# DEPOIS (atual):
from src.memory.semantic_memory import SemanticMemory
from src.memory.narrative_history import NarrativeHistory
from src.memory.procedural_memory import ProceduralMemory

# Integração manual ou via IntegrationLoop
semantic = SemanticMemory()
narrative = NarrativeHistory()
procedural = ProceduralMemory()
# Uso combinado dos três sistemas de memória
```

---

## 🔄 ABORDAGEM LACANIANA

A substituição de `episodic_layer` por `NarrativeHistory` introduz uma abordagem Lacaniana fundamental:

### Diferenças Conceituais

1. **EpisodicMemory (Antigo)**: Armazena eventos como ocorrem
2. **NarrativeHistory (Novo)**: Constrói narrativas retroativamente

### Princípios Lacanianos

- **Inscrição sem significado**: Eventos são inscritos sem interpretação imediata
- **Ressignificação retroativa**: Significado é atribuído retroativamente (Nachträglichkeit)
- **Construção narrativa**: Narrativas são construídas, não recuperadas

**Migração Completa**: 2025-12-05 (todos os agentes migrados)

---

## 🔗 REFERÊNCIAS

- `docs/VARREDURA_MODULOS_DEPRECATED_SUBSTITUICOES.md` - Documentação completa de substituições
- `src/memory/README.md` - Documentação do sistema de memória unificado
- `src/memory/narrative_history.py` - Implementação Lacaniana de memória episódica
- `src/memory/semantic_memory.py` - Memória semântica (declarativa)
- `src/memory/procedural_memory.py` - Memória procedural

---

**Autor**: Fabrício da Silva + assistência de IA
**Data**: 2025-12-07
**Versão**: 1.0

