# Módulo Intelligence (DEPRECATED)

## ⚠️ STATUS: DEPRECATED

**Data de Deprecação**: 2025-12-07
**Phase**: 26B (não implementado)

Este módulo foi planejado como parte do Phase 26B (Intelligence) mas **nunca foi implementado**. As funcionalidades foram distribuídas em módulos especializados existentes.

---

## 📋 MÓDULOS PLANEJADOS (NÃO IMPLEMENTADOS)

### 1. `context_aware_reasoner.py`
**Substituído por**: `src.integrations.mcp_context_server.ContextServer`
- **Arquivo**: `src/integrations/mcp_context_server.py`
- **Funcionalidade**: Raciocínio baseado em contexto via MCP Context Server
- **Status**: ✅ Implementado e operacional

**Migração**:
```python
# ANTES (deprecated):
from intelligence.context_aware_reasoner import ContextAwareReasoner
reasoner = ContextAwareReasoner()
result = reasoner.reason(context, ...)

# DEPOIS (atual):
from src.integrations.mcp_context_server import ContextServer
context_server = ContextServer()
# Raciocínio baseado em contexto via MCP
```

---

### 2. `dataset_integrator.py`
**Substituído por**: `src.memory.dataset_indexer.DatasetIndexer`
- **Arquivo**: `src/memory/dataset_indexer.py`
- **Funcionalidade**: Integração de datasets e indexação semântica
- **Status**: ✅ Implementado e operacional (Phase 24)

**Migração**:
```python
# ANTES (deprecated):
from intelligence.dataset_integrator import DatasetIntegrator
integrator = DatasetIntegrator()
integrated = integrator.integrate_dataset(...)

# DEPOIS (atual):
from src.memory.dataset_indexer import DatasetIndexer
indexer = DatasetIndexer()
# Indexação e integração de datasets via Phase 24
```

---

### 3. `learning_loop.py`
**Substituído por**: `src.orchestrator.introspection_loop.IntrospectionLoop`
- **Arquivo**: `src/orchestrator/introspection_loop.py`
- **Funcionalidade**: Loop de aprendizado e introspecção contínua
- **Status**: ✅ Implementado e operacional

**Migração**:
```python
# ANTES (deprecated):
from intelligence.learning_loop import LearningLoop
loop = LearningLoop()
result = loop.learn(...)

# DEPOIS (atual):
from src.orchestrator.introspection_loop import IntrospectionLoop
introspection = IntrospectionLoop()
# Loop de aprendizado e introspecção integrado
```

---

### 4. `semantic_search_engine.py`
**Substituído por**: `src.memory.hybrid_retrieval.HybridRetrievalSystem`
- **Arquivo**: `src/memory/hybrid_retrieval.py`
- **Funcionalidade**: Busca semântica híbrida (associativa + vetorial)
- **Status**: ✅ Implementado e operacional (Phase 24)

**Migração**:
```python
# ANTES (deprecated):
from intelligence.semantic_search_engine import SemanticSearchEngine
engine = SemanticSearchEngine()
results = engine.search(query, top_k=10)

# DEPOIS (atual):
from src.memory.hybrid_retrieval import HybridRetrievalSystem
retrieval = HybridRetrievalSystem()
results = retrieval.retrieve(query, top_k=10)
# Busca semântica híbrida integrada com Phase 24
```

---

## 🔗 REFERÊNCIAS

- `docs/VARREDURA_MODULOS_DEPRECATED_SUBSTITUICOES.md` - Documentação completa de substituições
- `src/integrations/README.md` - Módulo de integrações (ContextServer)
- `src/memory/README.md` - Módulo de memória (DatasetIndexer, HybridRetrievalSystem)
- `src/orchestrator/README.md` - Módulo de orquestração (IntrospectionLoop)

---

**Autor**: Fabrício da Silva + assistência de IA
**Data**: 2025-12-07
**Versão**: 1.0

