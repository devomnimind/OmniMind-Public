# Estratégia de Indexação de Datasets como Memória de Modelos

**Autor**: Fabrício da Silva + assistência de IA
**Data**: 2025-01-XX
**Status**: Estratégia definida

---

## 🎯 CONCEITO: Datasets como Memória de Modelos

Os datasets em `data/datasets/` são **parte da memória de modelos** do OmniMind - conhecimento base que deve ser:

1. **Indexado** em Qdrant para retrieval eficiente
2. **Acessível** via RAG quando agentes falham
3. **Chunked** inteligentemente baseado no tipo de conteúdo
4. **Metadata rica** para filtros e busca precisa

---

## 📊 DATASETS DISPONÍVEIS

### 1. **dbpedia_ontology/** (16 arquivos arrow)
- **Tipo**: Conhecimento ontológico estruturado
- **Tamanho**: Grande (16 arquivos)
- **Estrutura**: Entidades, relações, propriedades
- **Chunking Strategy**: Por entidade/conceito
- **Collection**: `ontology_knowledge_kb`
- **Uso RAG**: Conhecimento geral estruturado, relações semânticas

### 2. **human_vs_ai_code/** (1 arquivo arrow)
- **Tipo**: Exemplos de código humano vs IA
- **Tamanho**: Médio
- **Estrutura**: Pares de código (humano, IA)
- **Chunking Strategy**: Por exemplo de código completo
- **Collection**: `code_examples_kb`
- **Uso RAG**: Padrões de código, exemplos de implementação

### 3. **infllm_v2_data/** (1 arquivo arrow)
- **Tipo**: Dados de treinamento/validação
- **Tamanho**: Médio
- **Estrutura**: Exemplos de tarefas
- **Chunking Strategy**: Por exemplo de tarefa
- **Collection**: `training_examples_kb`
- **Uso RAG**: Exemplos de tarefas, padrões de execução

### 4. **qasper_qa/** (train/validation/test)
- **Tipo**: Perguntas e respostas científicas
- **Tamanho**: Médio (3 splits)
- **Estrutura**: Q&A pairs com contexto científico
- **Chunking Strategy**: Por Q&A pair (incluindo contexto)
- **Collection**: `qa_knowledge_kb`
- **Uso RAG**: Q&A científico, conhecimento de papers

### 5. **scientific_papers_arxiv/** (1 arquivo arrow)
- **Tipo**: Papers científicos completos
- **Tamanho**: Grande
- **Estrutura**: Papers completos (abstract, sections, references)
- **Chunking Strategy**: Por seção (abstract, introduction, methods, results, conclusion)
- **Collection**: `scientific_papers_kb`
- **Uso RAG**: Conhecimento científico profundo, referências

### 6. **turing_reasoning/** (1 arquivo arrow)
- **Tipo**: Dados de raciocínio
- **Tamanho**: Médio
- **Estrutura**: Padrões de raciocínio
- **Chunking Strategy**: Por padrão de raciocínio
- **Collection**: `reasoning_patterns_kb`
- **Uso RAG**: Padrões de raciocínio, lógica

---

## 🏗️ ARQUITETURA DE INDEXAÇÃO

### Pipeline de Indexação

```
data/datasets/
    ↓
DatasetIndexer
    ├─ Detecta tipo de dataset (auto ou manual)
    ├─ Carrega dataset (HuggingFace datasets)
    ├─ Chunking inteligente (baseado no tipo)
    ├─ Gera embeddings (all-MiniLM-L6-v2)
    ├─ Adiciona metadata rica
    └─ Indexa em Qdrant (coleção específica)
```

### Estratégias de Chunking por Tipo

#### 1. Papers Científicos (`scientific_papers_arxiv`)
```python
chunking_strategy = {
    "by_section": True,
    "sections": ["abstract", "introduction", "methods", "results", "conclusion"],
    "min_chunk_size": 200,  # tokens
    "max_chunk_size": 1000,
    "overlap": 50
}
```

#### 2. Q&A (`qasper_qa`)
```python
chunking_strategy = {
    "by_qa_pair": True,
    "include_context": True,
    "min_chunk_size": 100,
    "max_chunk_size": 500
}
```

#### 3. Código (`human_vs_ai_code`)
```python
chunking_strategy = {
    "by_example": True,
    "include_comparison": True,  # humano vs IA
    "min_chunk_size": 50,  # linhas
    "max_chunk_size": 200
}
```

#### 4. Ontologia (`dbpedia_ontology`)
```python
chunking_strategy = {
    "by_entity": True,
    "include_relations": True,
    "min_chunk_size": 100,
    "max_chunk_size": 500
}
```

---

## 🔧 IMPLEMENTAÇÃO

### DatasetIndexer

**Localização**: `src/memory/dataset_indexer.py`

**Funcionalidades**:
1. Auto-detecção de tipo de dataset
2. Chunking adaptativo baseado no tipo
3. Geração de embeddings
4. Metadata rica (source, type, timestamp, dataset_name)
5. Indexação incremental
6. Validação de qualidade

**Interface Principal**:
```python
class DatasetIndexer:
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """Inicializa indexador de datasets"""

    def index_dataset(
        self,
        dataset_path: str,
        collection_name: str,
        dataset_type: Optional[str] = None,  # auto-detecta se None
        chunk_size: Optional[int] = None,  # usa padrão do tipo se None
    ) -> Dict[str, Any]:
        """
        Indexa um dataset como memória de modelos.

        Returns:
            {
                "collection": collection_name,
                "points_indexed": int,
                "chunks_created": int,
                "metadata": {...}
            }
        """

    def index_all_datasets(
        self,
        datasets_dir: str = "data/datasets",
        collections_prefix: str = "_kb"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Indexa todos os datasets disponíveis.

        Returns:
            {
                "dataset_name": {
                    "collection": str,
                    "points_indexed": int,
                    "status": "success" | "error"
                }
            }
        """

    def get_indexed_datasets(self) -> List[Dict[str, Any]]:
        """Lista datasets já indexados com estatísticas"""
```

---

## 📋 METADATA RICA

Cada chunk indexado terá metadata completa:

```python
metadata = {
    "source": "dataset",  # ou "documentation", "code", etc.
    "dataset_name": "scientific_papers_arxiv",
    "dataset_type": "scientific_papers",
    "chunk_type": "section",  # section, qa_pair, code_example, etc.
    "chunk_index": 0,
    "total_chunks": 100,
    "original_file": "paper_12345.arrow",
    "section": "introduction",  # se aplicável
    "timestamp": "2025-01-XXT...",
    "language": "en",
    "domain": "scientific",  # scientific, code, general, etc.
}
```

---

## 🔍 INTEGRAÇÃO COM RAG RETRIEVAL

### Uso no RAG Fallback

Quando um agente falha:

1. **ErrorAnalyzer** classifica o tipo de erro
2. **RAGFallbackSystem** gera query de retrieval baseada no erro
3. **HybridRetrievalSystem** busca em múltiplas coleções:
   - `scientific_papers_kb` (se erro relacionado a conhecimento científico)
   - `code_examples_kb` (se erro relacionado a código)
   - `qa_knowledge_kb` (se erro relacionado a Q&A)
   - `ontology_knowledge_kb` (se erro relacionado a conhecimento geral)
   - etc.
4. **Reranking** com Cross-Encoder
5. **Context Augmentation** com documentos relevantes
6. **Reexecução** do agente com contexto

---

## 📊 PRIORIZAÇÃO DE INDEXAÇÃO

### Alta Prioridade (Indexar Primeiro)
1. **scientific_papers_arxiv** - Conhecimento científico profundo
2. **qasper_qa** - Q&A científico (muito útil para RAG)
3. **human_vs_ai_code** - Exemplos de código

### Média Prioridade
4. **turing_reasoning** - Padrões de raciocínio
5. **infllm_v2_data** - Exemplos de tarefas

### Baixa Prioridade (Indexar Depois)
6. **dbpedia_ontology** - Grande, pode ser indexado incrementalmente

---

## 🧪 VALIDAÇÃO DE QUALIDADE

### Métricas de Qualidade
- **Chunking Quality**: Tamanho médio, overlap, completude
- **Embedding Quality**: Similaridade entre chunks relacionados
- **Retrieval Quality**: NDCG@5, precision@k, recall@k
- **Coverage**: % do dataset indexado

### Testes
- Teste de retrieval em queries de exemplo
- Validação de chunks (não quebram contexto)
- Validação de metadata (completa e correta)

---

## 📝 EXEMPLO DE USO

```python
from src.memory.dataset_indexer import DatasetIndexer

# Inicializar indexador
indexer = DatasetIndexer(
    qdrant_url="http://localhost:6333",
    embedding_model="all-MiniLM-L6-v2"
)

# Indexar dataset específico
result = indexer.index_dataset(
    dataset_path="data/datasets/scientific_papers_arxiv",
    collection_name="scientific_papers_kb",
    dataset_type="scientific_papers"  # ou None para auto-detect
)

print(f"Indexados {result['points_indexed']} pontos em {result['collection']}")

# Indexar todos os datasets
results = indexer.index_all_datasets()
for dataset_name, result in results.items():
    print(f"{dataset_name}: {result['status']} - {result.get('points_indexed', 0)} pontos")
```

---

## ⚠️ CONSIDERAÇÕES

### Performance
- Indexação pode ser demorada para datasets grandes
- Fazer incremental (pode pausar e retomar)
- Usar batch processing para embeddings

### Memória
- Não carregar dataset inteiro em memória
- Processar em batches
- Liberar memória após indexação

### Qualidade
- Validar chunks não quebram contexto
- Garantir metadata completa
- Testar retrieval quality

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Criar `DatasetIndexer` class
- [ ] Implementar auto-detecção de tipo
- [ ] Implementar chunking strategies por tipo
- [ ] Integrar com Qdrant
- [ ] Adicionar metadata rica
- [ ] Testes unitários
- [ ] Indexar dataset piloto (scientific_papers_arxiv)
- [ ] Validar qualidade de retrieval
- [ ] Indexar todos os datasets
- [ ] Integrar com RAGFallbackSystem

---

**Status**: Estratégia definida - Pronto para implementação na Fase 1.3

