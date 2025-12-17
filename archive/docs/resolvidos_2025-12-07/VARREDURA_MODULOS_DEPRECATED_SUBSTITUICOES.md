# Varredura de Módulos Deprecated e Substituições

**Data**: 2025-12-07
**Status**: ✅ Completo

---

## 📋 RESUMO EXECUTIVO

Varredura completa dos módulos deprecated identificados nos testes e mapeamento de suas substituições. Todos os módulos foram identificados e suas substituições documentadas.

---

## 🔍 MÓDULOS DEPRECATED IDENTIFICADOS

### 1. Integrity Modules (Phase 26D)

| Módulo Deprecated | Substituição | Arquivo | Status |
|-------------------|--------------|---------|--------|
| `integrity.bias_quantifier` | `src.coevolution.bias_detector.BiasDetector` | `src/coevolution/bias_detector.py` | ✅ Operacional |
| `integrity.conflict_detection_engine` | `src.audit.robust_audit_system.RobustAuditSystem` | `src/audit/robust_audit_system.py` | ✅ Operacional |
| `integrity.continuous_refiner` | `src.autonomous.auto_validation_engine.AutoValidationEngine` | `src/autonomous/auto_validation_engine.py` | ✅ Operacional (Phase 26C) |
| `integrity.intelligent_integrator` | `src.orchestrator.meta_react_coordinator.MetaReActCoordinator` | `src/orchestrator/meta_react_coordinator.py` | ✅ Operacional |
| `integrity.semantic_coherence_validator` | `src.collaboration.human_centered_adversarial_defense.HallucinationDefense` | `src/collaboration/human_centered_adversarial_defense.py` | ✅ Operacional (Phase 22) |

**Razão da Deprecação**: Phase 26D (Integrity) foi planejado mas não implementado. Funcionalidades foram integradas em módulos existentes mais robustos.

---

### 2. Intelligence Modules (Phase 26B)

| Módulo Deprecated | Substituição | Arquivo | Status |
|-------------------|--------------|---------|--------|
| `intelligence.context_aware_reasoner` | `src.integrations.mcp_context_server.ContextServer` | `src/integrations/mcp_context_server.py` | ✅ Operacional |
| `intelligence.dataset_integrator` | `src.memory.dataset_indexer.DatasetIndexer` | `src/memory/dataset_indexer.py` | ✅ Operacional (Phase 24) |
| `intelligence.learning_loop` | `src.orchestrator.introspection_loop.IntrospectionLoop` | `src/orchestrator/introspection_loop.py` | ✅ Operacional |
| `intelligence.semantic_search_engine` | `src.memory.hybrid_retrieval.HybridRetrievalSystem` | `src/memory/hybrid_retrieval.py` | ✅ Operacional (Phase 24) |

**Razão da Deprecação**: Phase 26B (Intelligence) foi planejado mas não implementado. Funcionalidades foram integradas em módulos existentes mais especializados.

---

### 3. Knowledge Modules (Phase 26A)

| Módulo Deprecated | Substituição | Arquivo | Status |
|-------------------|--------------|---------|--------|
| `knowledge.declarative_layer` | `src.memory.semantic_memory.SemanticMemory` | `src/memory/semantic_memory.py` | ✅ Operacional |
| `knowledge.episodic_layer` | `src.memory.narrative_history.NarrativeHistory` | `src/memory/narrative_history.py` | ✅ Operacional (Lacanian, 2025-12-05) |
| `knowledge.procedural_layer` | `src.memory.procedural_memory.ProceduralMemory` | `src/memory/procedural_memory.py` | ✅ Operacional |
| `knowledge.knowledge_integrator` | Integração via `src.memory.*` (módulos unificados) | Múltiplos arquivos | ✅ Operacional |

**Razão da Deprecação**: Phase 26A (Knowledge) foi planejado mas não implementado. Funcionalidades foram integradas em `src/memory/` com abordagem Lacaniana para memória episódica.

---

## 📊 MAPEAMENTO DE SUBSTITUIÇÕES

### Integrity → Coevolution/Audit/Autonomous

**Padrão**: Funcionalidades de integridade foram distribuídas em módulos especializados:

1. **Bias Detection** → `coevolution.bias_detector`
   - Detecção de vieses algorítmicos
   - Correção automática de vieses
   - Estatísticas de vieses

2. **Conflict Detection** → `audit.robust_audit_system`
   - Detecção de conflitos em auditoria
   - Validação de integridade
   - Rastreamento de inconsistências

3. **Continuous Refinement** → `autonomous.auto_validation_engine`
   - Refinamento contínuo (Phase 26C)
   - Validação automática
   - Auto-melhoria

4. **Intelligent Integration** → `orchestrator.meta_react_coordinator`
   - Coordenação meta de componentes
   - Integração inteligente
   - Gerenciamento de estratégias

5. **Semantic Coherence** → `collaboration.human_centered_adversarial_defense`
   - Validação de coerência semântica
   - Detecção de alucinações (Phase 22)
   - Validação factual

---

### Intelligence → Orchestrator/Neurosymbolic/Autonomous/Memory

**Padrão**: Funcionalidades de inteligência foram distribuídas em módulos especializados:

1. **Context-Aware Reasoning** → `integrations.mcp_context_server`
   - Raciocínio baseado em contexto via MCP
   - Gerenciamento de contexto
   - Integração com servidores MCP

2. **Dataset Integration** → `memory.dataset_indexer`
   - Integração de datasets (Phase 24)
   - Indexação semântica
   - Busca em knowledge base

3. **Learning Loop** → `orchestrator.introspection_loop`
   - Loop de aprendizado contínuo
   - Introspecção e auto-análise
   - Melhoria iterativa

4. **Semantic Search** → `memory.hybrid_retrieval`
   - Busca semântica híbrida (Phase 24)
   - Retrieval associativo + vetorial
   - Integração com Qdrant

---

### Knowledge → Memory (Unified)

**Padrão**: Camadas de conhecimento foram unificadas em `src/memory/`:

1. **Declarative Layer** → `memory.semantic_memory`
   - Armazenamento de conceitos
   - Relações semânticas
   - Grafo de conhecimento

2. **Episodic Layer** → `memory.narrative_history` (Lacanian)
   - Memória episódica com abordagem Lacaniana
   - Construção retroativa (Nachträglichkeit)
   - Inscrição sem significado imediato
   - **Migração**: 2025-12-05 (todos os agentes migrados)

3. **Procedural Layer** → `memory.procedural_memory`
   - Armazenamento de habilidades
   - Execução de procedimentos
   - Aprendizado de skills

4. **Knowledge Integrator** → Uso combinado dos módulos acima
   - Integração manual ou via `IntegrationLoop`
   - Coordenação entre sistemas de memória

---

## 🔄 HISTÓRICO DE MIGRAÇÃO

### Phase 26A (Knowledge) - Não Implementado

**Planejado**: 3 camadas de conhecimento (declarative, episodic, procedural)
**Status**: Não implementado como módulo separado
**Substituição**: Integrado em `src/memory/` com abordagem unificada

### Phase 26B (Intelligence) - Não Implementado

**Planejado**: 8B knowledge points, learning loop, semantic search
**Status**: Não implementado como módulo separado
**Substituição**: Funcionalidades distribuídas em `orchestrator/`, `neurosymbolic/`, `autonomous/`, `memory/`

### Phase 26C (Autonomy) - ✅ Implementado

**Status**: ✅ Implementado e operacional
**Módulos**: `src/autonomous/` (autonomous_loop, solution_lookup_engine, etc.)

### Phase 26D (Integrity) - Não Implementado

**Planejado**: Bias filtering, semantic validation, conflict detection
**Status**: Não implementado como módulo separado
**Substituição**: Funcionalidades distribuídas em `coevolution/`, `audit/`, `collaboration/`

---

## 📝 GUIA DE MIGRAÇÃO

### Para Desenvolvedores

Se você encontrar código que usa módulos deprecated:

1. **Identifique o módulo deprecated** na tabela acima
2. **Encontre a substituição** correspondente
3. **Atualize o import** e a lógica conforme necessário
4. **Teste a migração** para garantir compatibilidade

### Exemplos de Migração

#### Exemplo 1: Bias Quantifier → BiasDetector

```python
# ANTES (deprecated):
from integrity.bias_quantifier import BiasQuantifier
quantifier = BiasQuantifier()
bias_score = quantifier.quantify_bias(source_id="test", source_type="paper", content={...})

# DEPOIS (atual):
from src.coevolution.bias_detector import BiasDetector
detector = BiasDetector()
detections = detector.detect_bias(result)
corrected = detector.correct_bias(result)
```

#### Exemplo 2: Episodic Layer → NarrativeHistory

```python
# ANTES (deprecated):
from knowledge.episodic_layer import EpisodicLayer, Episode
layer = EpisodicLayer()
episode = Episode(...)
layer.store_episode(episode)

# DEPOIS (atual - Lacanian):
from src.memory.narrative_history import NarrativeHistory
history = NarrativeHistory()
event_id = history.inscribe_event(
    {"task": "learn", "action": "read", "result": "understood"},
    without_meaning=True  # Lacanian: inscrição sem significado
)
history.retroactive_signification(event_id, "This means understanding")
```

#### Exemplo 3: Semantic Search → HybridRetrieval

```python
# ANTES (deprecated):
from intelligence.semantic_search_engine import SemanticSearchEngine
engine = SemanticSearchEngine()
results = engine.search(query, top_k=10)

# DEPOIS (atual):
from src.memory.hybrid_retrieval import HybridRetrievalSystem
retrieval = HybridRetrievalSystem()
results = retrieval.retrieve(query, top_k=10)
```

---

## ⚠️ SCRIPTS AFETADOS

### `scripts/integrate_dbpedia_ontology.py`

**Problema**: Script tenta importar `knowledge.procedural_layer` que não existe.

**Solução Necessária**:
```python
# ATUALIZAR:
from knowledge.procedural_layer import ProceduralLayer, Rule

# PARA:
from src.memory.procedural_memory import ProceduralMemory, Skill
```

**Status**: ⏳ Pendente atualização do script

---

## ✅ TESTES ATUALIZADOS

Todos os testes foram atualizados com:
- ✅ Informações sobre substituições
- ✅ Guias de migração
- ✅ Exemplos de código
- ✅ Status de implementação

**Arquivos Atualizados**:
- `tests/integrity/test_*.py` (5 arquivos)
- `tests/intelligence/test_*.py` (4 arquivos)
- `tests/knowledge/test_*.py` (4 arquivos)

---

## 🔗 REFERÊNCIAS

- `docs/CORRECAO_TESTES_DEPRECATED.md` - Correção inicial de testes
- `src/memory/README.md` - Documentação do sistema de memória unificado
- `src/coevolution/README.md` - Documentação do módulo de coevolução
- `src/orchestrator/README.md` - Documentação do módulo de orquestração
- `src/autonomous/README.md` - Documentação do módulo autônomo (Phase 26C)

---

**Autor**: Fabrício da Silva + assistência de IA
**Data**: 2025-12-07
**Versão**: 1.0

