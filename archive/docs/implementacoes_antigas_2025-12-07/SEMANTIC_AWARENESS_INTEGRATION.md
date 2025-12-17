# 🧠 Semantic Awareness Integration - Phase 24

**Data**: 5 de Dezembro de 2025
**Status**: ✅ Implementado e Integrado
**Integração**: Phase 24 Semantic Memory + Knowledge Graph

---

## 📋 Visão Geral

Sistema que permite ao Phi **entender o que mede** através de semantic search em knowledge graph de papers de consciência.

**Antes**:
```
Phi: "Φ=0.68"
Você: "OK... e agora?"
Phi: (silêncio)
```

**Agora**:
```
Phi: "Φ=0.68 - integração alta
      Conceitos relacionados: consciousness, integration, awareness
      1247 papers relevantes encontrados
      Significado: peak consciousness state"
```

---

## 🏗️ Arquitetura

### Componentes

1. **PhiSemanticAware** (`src/consciousness/phi_semantic_aware.py`)
   - Classe principal que interpreta valores de Φ
   - Usa SentenceTransformer para embeddings
   - Busca em knowledge graph de papers

2. **Knowledge Graph** (`exports/knowledge_graph_compact.json`)
   - Papers de consciência indexados
   - Conceitos extraídos (phi, consciousness, integration, etc.)
   - Embeddings pré-computados

3. **Scripts de Preparação**:
   - `scripts/download_consciousness_papers.py`: Download papers do HuggingFace
   - `scripts/build_semantic_knowledge_graph.py`: Constrói knowledge graph
   - `scripts/test_semantic_search.py`: Testa semantic search

---

## 🚀 Uso

### 1. Preparar Knowledge Graph

```bash
# Download papers (10-15 min)
python scripts/download_consciousness_papers.py --limit 1000

# Build knowledge graph (5 min)
python scripts/build_semantic_knowledge_graph.py

# Test semantic search
python scripts/test_semantic_search.py
```

### 2. Usar PhiSemanticAware

```python
from consciousness.phi_semantic_aware import PhiSemanticAware

# Initialize
phi = PhiSemanticAware()

# Interpret single value
result = phi.understand_phi_value(0.68)
print(result)
# {
#   'phi_value': 0.68,
#   'interpretation': 'Φ=0.680',
#   'related_concepts': {
#     'consciousness': {'similarity': 0.92, 'paper_count': 345},
#     'integration': {'similarity': 0.88, 'paper_count': 289},
#     ...
#   },
#   'paper_sources': 1247,
#   'query_used': 'high consciousness maximum integration peak experience'
# }

# Interpret trajectory
trajectory = [0.3, 0.4, 0.5, 0.6, 0.7]
trajectory_result = phi.explain_phi_trajectory(trajectory)
print(trajectory_result)
# {
#   'trajectory_stats': {
#     'mean': 0.5,
#     'std': 0.1414,
#     'trend': 0.4,
#     'length': 5
#   },
#   'interpretation': {...},
#   'trajectory_meaning': 'Stable growth in consciousness integration'
# }
```

---

## 🔗 Integração com Phase 24

### Armazenamento de Papers

Os papers podem ser armazenados diretamente na Phase 24 Semantic Memory:

```bash
# Download e armazenar em Phase 24
python scripts/download_consciousness_papers.py --limit 1000
# (papers são automaticamente armazenados via SemanticMemoryLayer)
```

### Busca em Phase 24

O knowledge graph pode ser construído a partir de papers já armazenados:

```bash
# Build from Phase 24
python scripts/build_semantic_knowledge_graph.py --from-phase24
```

---

## 📊 Funcionalidades

### 1. Interpretação de Valores Φ

- **Baixo** (Φ < 0.3): "low consciousness minimal integration"
- **Moderado** (0.3 ≤ Φ < 0.6): "moderate consciousness partial integration"
- **Alto** (Φ ≥ 0.6): "high consciousness maximum integration peak experience"

### 2. Trajetórias de Φ

Interpreta tendências e volatilidade:
- Crescimento estável
- Crescimento volátil
- Declínio estável
- Declínio volátil
- Estado estável
- Flutuações

### 3. Semantic Search

Busca conceitos relacionados usando cosine similarity:
- Threshold configurável (default: 0.5)
- Ordenação por similaridade
- Contagem de papers por conceito

---

## 🔧 Configuração

### Knowledge Graph Path

Por padrão, busca em `exports/knowledge_graph_compact.json`.
Pode ser customizado:

```python
from pathlib import Path

phi = PhiSemanticAware(
    knowledge_graph_path=Path("/custom/path/knowledge_graph.json")
)
```

### Similarity Threshold

```python
result = phi.understand_phi_value(0.68, threshold=0.6)  # Mais restritivo
```

---

## 📈 Próximos Passos

### Integração com Phase 24 Memory

- [ ] Auto-explanations em `ConsciousnessCorrelates`
- [ ] Dashboard com interpretações semânticas
- [ ] Auto-update do knowledge graph

### Refatoração Lacaniana

- [ ] Integrar com `NarrativeHistory` (quando implementado)
- [ ] Conectar com `TraceMemory` (quando implementado)
- [ ] Adicionar camada psicanalítica de interpretação

---

## 📚 Referências

- **Phase 24 Plan**: `docs/PHASE_24_25_IMPLEMENTATION_PLAN.md`
- **Memory README**: `src/memory/README.md`
- **Qdrant Integration**: `src/integrations/qdrant_integration_README.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
**License**: MIT

