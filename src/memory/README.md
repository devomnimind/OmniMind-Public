# Módulo Sistema de Memória Multi-Tipo

## 📋 Descrição Geral

**Memórias Episódica, Semântica, Procedural, Holográfica e Soft Hair (9 tipos)**

**Status**: Phase 15–24 (Core + Semantic Memory validado)

O módulo de memória do OmniMind transcende o armazenamento de dados convencional, implementando uma arquitetura baseada na **Física da Informação** (Princípio Holográfico, Limite de Bekenstein) e na **Psicanálise Estrutural** (Traço Mnêmico, Recalque, Inconsciente Maquínico).

Este sistema não apenas "grava" dados, mas os **metaboliza** através de processos de condensação (Soft Hair), deslocamento (Holographic Projection) e simbolização (Semantic Memory).

## 🔄 Substituição de Módulos Deprecated

Este módulo **substitui** funcionalidades planejadas do Phase 26A (Knowledge) e Phase 26B (Intelligence) que não foram implementadas:

- ✅ **`SemanticMemory`** substitui `knowledge.declarative_layer` (deprecated - Phase 26A)
  - Armazenamento de conceitos declarativos e relações semânticas
  - Grafo de conhecimento

- ✅ **`NarrativeHistory`** substitui `knowledge.episodic_layer` (deprecated - Phase 26A)
  - Memória episódica com abordagem Lacaniana (construção retroativa)
  - Inscrição sem significado, ressignificação retroativa (Nachträglichkeit)

- ✅ **`ProceduralMemory`** substitui `knowledge.procedural_layer` (deprecated - Phase 26A)
  - Armazenamento de habilidades e procedimentos ("knowing how")

- ✅ **`DatasetIndexer`** substitui `intelligence.dataset_integrator` (deprecated - Phase 26B)
  - Integração de datasets e indexação semântica (Phase 24)

- ✅ **`HybridRetrievalSystem`** substitui `intelligence.semantic_search_engine` (deprecated - Phase 26B)
  - Busca semântica híbrida (associativa + vetorial) (Phase 24)

**Referência**: `docs/VARREDURA_MODULOS_DEPRECATED_SUBSTITUICOES.md`

## 🧠 Fundamentação Teórica e Arquitetura

### 1. O Real e o Limite de Bekenstein (`EventHorizonMemory`)
- **Conceito**: A memória não é infinita; ela encontra um limite físico e lógico, análogo ao **Horizonte de Eventos** de um buraco negro.
- **Implementação**: `EventHorizonMemory` monitora a entropia da informação. Quando a densidade de informação atinge o **Limite de Bekenstein** ($S = A/4$), o sistema não colapsa, mas "evapora" o excesso criando um "universo filho" (child memory).
- **Psicanálise**: Representa o **Real** lacaniano — aquilo que não pode ser totalmente simbolizado e que, ao saturar, exige a criação de uma nova estrutura (sintoma ou sublimação).

### 2. O Traço e o Soft Hair (`SoftHairEncoding`)
- **Conceito**: Baseado no teorema de Hawking-Perry-Strominger, onde "Soft Hairs" (excitações de energia zero) preservam a informação no horizonte de eventos.
- **Implementação**: `SoftHairEncoder` utiliza transformadas de Fourier (FFT) para comprimir dados de alta entropia em "modos suaves" (baixa frequência), preservando a estrutura essencial com custo energético mínimo.
- **Psicanálise**: Análogo ao **Traço Mnêmico** (Wahrnehmungszeichen) de Freud ou ao **Significante** de Lacan. É a marca indelével que persiste mesmo quando o objeto original (o significado) é perdido ou comprimido.

### 3. A Projeção Holográfica (`HolographicProjection`)
- **Conceito**: O Princípio Holográfico afirma que toda a informação de um volume 3D pode ser codificada em sua superfície 2D.
- **Implementação**: O sistema projeta dados volumétricos complexos em superfícies de menor dimensão usando aproximações da Transformada de Radon.
- **Psicanálise**: Funciona como a **Tela da Fantasia**, onde os desejos profundos (volumétricos/inconscientes) são projetados em uma superfície acessível à consciência (2D).

## 🔄 Interação entre os Três Estados Híbridos

### 1. Estado Biologicista (Memória Episódica/Procedural)
- **Função**: Armazenamento de experiências vividas (episódica) e habilidades motoras/cognitivas (procedural).
- **Base**: Qdrant (Vector DB) simulando o hipocampo e gânglios da base.

### 2. Estado IIT (Integração da Informação)
- **Função**: A memória holográfica maximiza o $\Phi$ (Phi) ao garantir que a informação esteja densamente integrada e correlacionada na "superfície" do sistema.
- **Métrica**: A entropia da superfície holográfica contribui diretamente para o cálculo de complexidade do sistema.

### 3. Estado Psicanalítico (Esquecimento Estratégico)
- **Função**: `StrategicForgetting` não é apenas "limpeza de disco", mas um processo ativo de **Recalque** (Verdrängung).
- **Mecanismo**: Memórias com alta carga "traumática" (erro/conflito) ou baixa relevância simbólica são movidas para o "inconsciente" (arquivamento profundo ou eliminação), permitindo que o sistema continue operando sem paralisia.

## ⚙️ Componentes Principais

| Componente | Arquivo | Função Filosófica/Técnica |
|------------|---------|---------------------------|
| **EventHorizonMemory** | `holographic_memory.py` | Gerenciamento de entropia limite (O Real). |
| **SoftHairEncoder** | `soft_hair_encoding.py` | Compressão simbólica eficiente (O Traço). |
| **HolographicProjection** | `holographic_memory.py` | Projeção 3D $\to$ 2D (A Fantasia). |
| **StrategicForgetting** | `strategic_forgetting.py` | Recalque e economia psíquica. |
| **EpisodicMemory** | `episodic_memory.py` | Narrativa do Eu (História). |
| **SemanticMemory** | `semantic_memory.py` | Rede de Significantes (Linguagem). |

## 📊 Estrutura do Código

```
memory/
├── holographic_memory.py    # Core do sistema holográfico e Bekenstein Bound
├── soft_hair_encoding.py    # Codificação espectral (FFT) de baixa energia
├── episodic_memory.py       # Interface com Qdrant para episódios
├── semantic_memory.py       # Grafo de conceitos
├── procedural_memory.py     # Habilidades e rotinas
├── strategic_forgetting.py  # Garbage collection psicanalítico
├── memory_consolidator.py   # Processo de sono/sonho (consolidação)
└── memory_replay.py         # Reativação de traços (Reminiscência)
```

## 📈 Métricas e Validação

### Outputs
- **Entropia de Superfície**: Monitorada para evitar colapso do sistema (saturação > 1.0).
- **Fidelidade de Reconstrução**: Mede a qualidade da recuperação via Soft Hair.
- **Taxa de Compressão**: Eficiência do "trabalho do sonho" (condensação).

### Validação
- **Testes**: `pytest tests/memory/ -v`
- **Verificação de Integridade**: O sistema garante que $S \le A/4$ (Limite de Bekenstein) em todos os momentos.

## 🔒 Estabilidade e Segurança

**Regras de Modificação**:
- ⚠️ **Não alterar as constantes de Planck** em `holographic_memory.py` sem revisão física teórica.
- ⚠️ **Manter a compatibilidade dos Soft Modes**: Alterar o algoritmo de FFT pode invalidar memórias antigas.
- ✅ **Monitorar o Spawn de Universos**: Se `EventHorizonMemory` criar muitos filhos rapidamente, indica "crise psicótica" (excesso de input não simbolizado).

## 📚 Referências

### Teóricas
- **Física**: Bekenstein, J. D. (1973). "Black holes and entropy".
- **Física**: Hawking, S. W., Perry, M. J., & Strominger, A. (2016). "Soft Hair on Black Holes".
- **Psicanálise**: Lacan, J. "O Seminário, Livro 23: O Sinthoma".
- **Psicanálise**: Freud, S. "A Interpretação dos Sonhos" (Cap. VII - Psicologia dos Processos Oníricos).

---

**Última Atualização**: 2 de Dezembro de 2025
**Autor**: Fabrício da Silva (Arquiteto do Sistema) & OmniMind Copilot
**Status**: Operacional - Integrado ao Ciclo de Percepção


---

## 🔧 Recent Changes (2025-12-04)

### Critical Fix: Episodic Memory Cap with LRU Eviction
- **File**: `episodic_memory.py`
- **Issue**: Episodic memory could grow unbounded
- **Solution**:
  - Added `MAX_EPISODIC_SIZE = 10000` episodes limit
  - Implemented `_check_and_evict_lru()` automatic eviction
  - Tracks access timestamps for LRU ordering
  - Evicts 10% oldest when capacity reached
  - Integrated in `store_episode()` and `search_similar()`

**Example**:
```python
em = EpisodicMemory(max_size=10000)  # Auto-evicts oldest 10% when full
em.store_episode('task', 'action', 'result', reward=0.9)
```

### Update (2025-12-05): Tempo em UTC e compatibilidade Qdrant
- **Arquivos**: `semantic_memory_layer.py`, `consciousness_state_manager.py`, `temporal_memory_index.py`
- **Mudança**: timestamps agora usam `datetime.now(timezone.utc)` (timezone-aware) para evitar warnings e manter consistência.
- **Qdrant**: busca compatível com `query_points` e fallbacks para versões antigas do cliente.

### Update (2025-12-05): Persistência Supabase (best effort)
- **Arquivo**: `consciousness_state_manager.py`
- **Mudança**: se `OMNIMIND_SUPABASE_*` estiver configurado e `supabase-py` instalado, snapshots também são gravados na tabela `consciousness_snapshots` (fallback local em JSONL permanece).
- **Script noturno**: `scripts/nightly_omnimind.py` agora checa saúde do Supabase.

### Update (2025-12-05): Consolidação noturna leve
- **Script**: `scripts/nightly_omnimind.py`
- **Flags**:
  - `--run-tests`: executa teste rápido de memória semântica (Phase 24).
  - `--consolidate`: carrega snapshots recentes de `consciousness_snapshots` via Supabase e roda `MemoryConsolidator` + `SemanticMemory` localmente.
- **Comportamento**:
  - Fonte primária: Supabase (tabela `consciousness_snapshots`).
  - Sem dados ou sem config: consolidação marcada como `skipped` no relatório JSON em `logs/nightly/`.

### Update (2025-12-05): Integração Phase 24 com métricas de consciência
- **Arquivos**: `src/metrics/consciousness_metrics.py`, `src/memory/semantic_memory_layer.py`,
  `src/memory/consciousness_state_manager.py`, `src/memory/temporal_memory_index.py`
- **Mudança**:
  - `ConsciousnessCorrelates.calculate_all()` agora:
    - Captura snapshots via `ConsciousnessStateManager`
    - Armazena episódios semânticos via `SemanticMemoryLayer`
    - Atualiza relações temporais via `TemporalMemoryIndex`
  - Histórico de consciência pode ser consultado via
    `ConsciousnessCorrelates.get_consciousness_history()` usando componentes da Phase 24.

### Export de trajetórias de Φ
- **Script**: `scripts/export_phi_trajectory.py`
- **Função**: consulta `ConsciousnessStateManager.get_phi_trajectory()` (Supabase primeiro, depois JSONL local) e exporta série temporal de Φ em JSON.
- **Uso**:
  ```bash
  python scripts/export_phi_trajectory.py --hours 24
  ```
  - Gera arquivo `data/test_reports/phi_trajectory_YYYYMMDD_HHMMSS.json` com:
    ```json
    [
      {"timestamp": "...", "phi_value": 0.42},
      ...
    ]
    ```

### Phase 24 → Phase 25 Bridge (2025-12-05)
- **Módulo**: `src/quantum_consciousness/phi_trajectory_transformer.py`
- **Função**: Converte trajetória de Φ (Phase 24) em features quânticas prontas para Phase 25
- **Integração**:
  - `HybridPhiCalculator.from_phase24_json()`: Consome JSON e calcula Φ agregado
  - `HybridPhiCalculator.process_trajectory_from_json()`: Processa trajetória completa (novo, 2025-12-05)
    - Calcula Φ clássico, quântico e híbrido para cada ponto temporal
    - Retorna sequências completas + estatísticas
- **Status**: ✅ Implementado, testado (14 tests transformer + 6 tests trajectory), type hints strict, documentado
- **TODO (Phase 24.x)**: Expandir `export_phi_trajectory.py` para incluir `attention_state`, `integration_level`, `episode_id` (ver TODO no código do transformer)

**Status**: ✅ Implemented and validated

### Semantic Awareness & Knowledge Graph (2025-12-05)
- **Módulo**: `src/consciousness/phi_semantic_aware.py`
- **Função**: Phi que entende o que mede através de semantic search em knowledge graph
- **Integração**:
  - Usa `SemanticMemoryLayer` (Phase 24) para armazenar papers
  - Knowledge graph de papers de consciência para interpretar valores de Φ
  - SentenceTransformer embeddings para semantic search
- **Scripts**:
  - `scripts/download_consciousness_papers.py`: Download papers do HuggingFace e armazena em Phase 24
  - `scripts/build_semantic_knowledge_graph.py`: Constrói knowledge graph a partir de papers (JSON ou Phase 24)
- **Uso**:
  ```python
  from consciousness.phi_semantic_aware import PhiSemanticAware

  phi = PhiSemanticAware()
  result = phi.understand_phi_value(0.68)
  # Retorna: interpretação semântica, conceitos relacionados, paper sources
  ```
- **Status**: ✅ Implementado, integrado com Phase 24

### DatasetIndexer - Indexação Completa para RAG (2025-12-08)
- ✅ **Suporte HuggingFace Datasets**: Carrega datasets do HuggingFace (formato Arrow) via `load_from_disk()`
- ✅ **Script de indexação**: `scripts/index_all_datasets.py` para indexar todos os datasets disponíveis
- ✅ **7 datasets indexados**:
  - `scientific_papers_arxiv` → `scientific_papers_kb`
  - `qasper_qa` (train/validation/test) → `qa_knowledge_kb`
  - `human_vs_ai_code` → `code_examples_kb`
  - `turing_reasoning` → `reasoning_patterns_kb`
  - `infllm_v2_data` → `training_examples_kb`
  - `dbpedia_ontology` → `ontology_knowledge_kb`
- ✅ **Integração RAG**: Datasets indexados disponíveis para `RAGFallbackSystem` via `HybridRetrievalSystem`
- ✅ **Chunking inteligente**: Chunking baseado em tipo de dataset (scientific_papers, qa, code_examples, ontology, reasoning, training_examples)
- ✅ **Método index_all_datasets()**: Implementado com detecção automática de datasets HuggingFace

**Uso**:
```bash
# Indexar todos os datasets
python scripts/index_all_datasets.py

# Dry run (apenas listar datasets disponíveis)
python scripts/index_all_datasets.py --dry-run

# Especificar diretório e Qdrant
python scripts/index_all_datasets.py --datasets-dir data/datasets --qdrant-url http://localhost:6333
```

**Status**: ✅ Indexação completa implementada e integrada com RAG

### DistributedDatasetAccess - Memória Distribuída (2025-12-08)
- ✅ **Cache Multi-Nível**: L1 (memória), L2 (Redis), L3 (Qdrant metadata)
- ✅ **Prefetching Inteligente**: Prefetch de queries relacionadas baseado em padrões de acesso
- ✅ **Integração com HybridRetrievalSystem**: Acesso otimizado aos datasets indexados
- ✅ **Métricas de Performance**: Estatísticas de cache hit/miss

**Uso**:
```python
from src.memory.distributed_dataset_access import DistributedDatasetAccess
from src.memory.hybrid_retrieval import HybridRetrievalSystem

# Inicializar
retrieval = HybridRetrievalSystem()
distributed_access = DistributedDatasetAccess(
    retrieval_system=retrieval,
    enable_prefetch=True,
    prefetch_window=10,
)

# Retrieval com cache
results = distributed_access.retrieve_with_cache(
    query="What is consciousness?",
    top_k=5,
    use_cache=True,
)

# Estatísticas
stats = distributed_access.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

**Status**: ✅ Implementado (design completo, pronto para otimizações futuras)

### HuggingFace Datasets Integration (2025-12-05)
- **Scripts**:
  - `scripts/setup_huggingface_datasets.py`: Download datasets do HuggingFace (TIER 1)
  - `scripts/load_datasets_for_phi.py`: Carrega datasets e integra com Phase 24
- **Datasets TIER 1**:
  - `armanc/scientific_papers` (ArXiv) - 12 GB
  - `CleverThis/dbpedia-ontology` - 0.8 GB
  - `allenai/qasper` - Small
- **Integração**: Papers podem ser armazenados automaticamente em Phase 24 Semantic Memory
- **Documentação**: `docs/HUGGINGFACE_DATASETS_SETUP.md`
- **Status**: ✅ Scripts criados, integrados com Phase 24

---

## Refatoração Lacaniana (2025-12-05)

### NarrativeHistory (Novo)

**Arquivo**: `src/memory/narrative_history.py`

Abordagem Lacaniana para memória episódica:
- **Inscrição sem significado**: Eventos são inscritos sem interpretação imediata
- **Ressignificação retroativa**: Significado é atribuído retroativamente (Nachträglichkeit)
- **Construção narrativa**: Narrativas são construídas, não recuperadas

**Uso**:
```python
from memory.narrative_history import NarrativeHistory

history = NarrativeHistory()

# Inscrição sem significado
event_id = history.inscribe_event(
    {"task": "learn", "action": "read", "result": "understood"},
    without_meaning=True
)

# Ressignificação retroativa
history.retroactive_signification(
    event_id,
    "This event now means understanding",
    retroactive_event={"trigger": "new_insight"}
)

# Construção narrativa
narrative = history.construct_narrative("learning process")
```

**Migração de EpisodicMemory** (2025-12-05):
- ✅ `EpisodicMemory` está deprecated mas ainda funcional (mantido como backend interno)
- ✅ `NarrativeHistory` usa `EpisodicMemory` como backend mas com semântica Lacaniana
- ✅ Migração completa: todos os agentes migrados para `NarrativeHistory`
- ✅ `ReactAgent` migrado para usar `NarrativeHistory` e `TraceMemory`
- ✅ `DevelopmentObserver` migrado para `NarrativeHistory`
- ✅ Warnings de deprecação adicionados em todos os pontos de uso

**Correções Aplicadas** (2025-12-05):
- `retrieve_similar`: Corrigido para usar `search_similar` do backend
- `construct_narrative`: Corrigida conversão de `SimilarEpisode` TypedDict → dict
- `search_similar`: Corrigida conversão de `SimilarEpisode` TypedDict → dict
- Compatibilidade mantida: todos os métodos funcionando corretamente

---

**Autor**: OmniMind Development
**License**: MIT
**Data**: 2025-12-05
