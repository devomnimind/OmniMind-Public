# QdrantIntegration - Phase 24

**Arquivo**: `src/integrations/qdrant_integration.py`  
**Status**: ✅ Core component da Phase 24 (Semantic Memory & Persistent Consciousness)  
**Última Atualização**: 5 de Dezembro de 2025

---

## 📋 Descrição

Abstração para integração com Qdrant Vector Database (local + cloud fallback).  
Usado pela Phase 24 para armazenar episódios de consciência com embeddings semânticos.

---

## 🏗️ Arquitetura

### Classes Principais

#### `QdrantPoint`
Dataclass representando um ponto no Qdrant:
- `id`: UUID do ponto
- `vector`: Embedding vector (numpy array ou list)
- `payload`: Metadados (dict)

#### `QdrantIntegration`
Classe principal de integração (singleton pattern):
- Gerencia conexão com Qdrant (local ou cloud)
- CRUD operations (create, read, update, delete)
- Vector search operations
- Health checks e error recovery

---

## 🔧 Funcionalidades

### 1. Connection Management
```python
from integrations.qdrant_integration import get_qdrant

qdrant = get_qdrant()  # Singleton instance
health = qdrant.health_check()  # True/False
```

### 2. Collection Management
```python
# Create collection (auto-checks if exists)
success = qdrant.create_collection(recreate=False)

# Check if collection exists
collections = qdrant.client.get_collections()
```

### 3. CRUD Operations
```python
# Upsert points
points = [QdrantPoint(id=uuid4(), vector=[0.1, 0.2, ...], payload={...})]
success = qdrant.upsert_points(points)

# Search
results = qdrant.search_points(
    query_vector=[0.1, 0.2, ...],
    top_k=5,
    score_threshold=0.7
)
```

### 4. Health & Error Recovery
```python
# Health check
is_healthy = qdrant.health_check()

# Automatic fallback (local → cloud or vice versa)
# Configurado via environment variables
```

---

## ⚙️ Configuração

### Environment Variables

```bash
# Qdrant Mode
QDRANT_MODE=local  # or "cloud"

# Local Configuration
QDRANT_LOCAL_HOST=localhost
QDRANT_LOCAL_PORT=6333

# Cloud Configuration (if mode=cloud)
QDRANT_CLOUD_URL=https://your-cluster.qdrant.io
QDRANT_CLOUD_API_KEY=your-api-key
```

### Collection Defaults

- **Collection Name**: `omnimind_consciousness` (Phase 24)
- **Vector Size**: 384 (all-MiniLM-L6-v2 embeddings)
- **Distance Metric**: COSINE

---

## 🔗 Integração com Phase 24

### Usado Por

1. **SemanticMemoryLayer** (`src/memory/semantic_memory_layer.py`)
   - Armazena episódios com embeddings
   - Semantic search de episódios similares

2. **ConsciousnessStateManager** (`src/memory/consciousness_state_manager.py`)
   - (Indireto via SemanticMemoryLayer)

3. **TemporalMemoryIndex** (`src/memory/temporal_memory_index.py`)
   - (Indireto via SemanticMemoryLayer)

---

## 📊 Validação

### Testes
- `tests/memory/test_phase_24_basic.py::TestQdrantIntegration`
- `scripts/validate_phase_24_complete.py` (validação completa)

### Status
- ✅ Health check: OK
- ✅ Collection management: OK
- ✅ CRUD operations: OK
- ✅ Singleton pattern: Validado
- ✅ Local + Cloud fallback: Implementado

---

## 🔧 Recent Changes (2025-12-05)

### Busca Compatível
- Usa `query_points` (cliente recente) com fallback para `search`/`search_points`
- Mantém compatibilidade com versões antigas do cliente Qdrant
- Elimina erros de atributo

### Phase 24 Integration
- Core component da Phase 24 Semantic Memory
- Validado em testes Phase 24 (22 tests passing)
- Integrado com `SemanticMemoryLayer`

---

## 📚 Referências

- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Phase 24 Plan**: `docs/PHASE_24_25_IMPLEMENTATION_PLAN.md`
- **Validation Report**: `docs/PHASE_24_VALIDATION_REPORT.md`

---

**Autor**: OmniMind Development  
**License**: MIT

