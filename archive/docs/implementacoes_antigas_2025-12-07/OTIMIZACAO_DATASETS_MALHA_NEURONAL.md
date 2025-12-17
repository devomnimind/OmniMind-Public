# Otimização de Datasets: Malha Neuronal de Conhecimento

**Autor**: Fabrício da Silva + assistência de IA
**Data**: 2025-01-XX
**Conceito**: Quantização de embeddings + Grafo dinâmico de conhecimento

---

## 🧠 CONCEITO: Malha Neuronal de Conhecimento

**Ideia**: Criar uma "malha neuronal" que:
1. **Quantiza embeddings** (similar à quantização de modelos)
2. **Estrutura conhecimento em grafo** (nós = chunks, arestas = similaridade)
3. **Expande dinamicamente** conforme pontos similares são acessados
4. **Otimiza acesso** (cache de caminhos frequentes)

---

## 🎯 OTIMIZAÇÕES POSSÍVEIS

### 1. Quantização de Embeddings

**Problema**: Embeddings 384-dim (FP32) = 1.5KB por chunk
**Solução**: Quantizar para INT8 (384-dim INT8 = 384 bytes)

```python
# Antes: FP32 embeddings
embedding_fp32 = [0.234, -0.567, 0.891, ...]  # 384 floats = 1.5KB

# Depois: INT8 quantized
embedding_int8 = quantize_to_int8(embedding_fp32)  # 384 bytes = 75% redução
```

**Benefício**: 75% redução de memória em embeddings

---

### 2. Grafo de Conhecimento Dinâmico

**Estrutura**:
```
Nó (Chunk) → Aresta (Similaridade) → Nó (Chunk Similar)
```

**Expansão Dinâmica**:
- Quando chunk A é acessado → busca chunks similares
- Cria arestas para chunks com similaridade > threshold
- Grafo cresce conforme uso (lazy expansion)

**Otimização**:
- Cache de caminhos frequentes
- Clustering de nós similares
- Pre-computação de caminhos críticos

---

### 3. Malha Neuronal Adaptativa

**Conceito**: Rede que se reconfigura baseada em padrões de acesso

```python
class KnowledgeNeuralMesh:
    """
    Malha neuronal de conhecimento que se expande dinamicamente.
    """

    def __init__(self):
        self.nodes: Dict[str, QuantizedChunk] = {}  # Chunks quantizados
        self.edges: Dict[str, List[Edge]] = {}  # Arestas de similaridade
        self.access_patterns: Dict[str, int] = {}  # Padrões de acesso
        self.hot_paths: Set[Tuple[str, str]] = set()  # Caminhos frequentes

    def access_chunk(self, chunk_id: str) -> QuantizedChunk:
        """Acessa chunk e expande malha se necessário"""
        # 1. Acessa chunk (desquantiza se necessário)
        chunk = self._get_chunk(chunk_id)

        # 2. Registra acesso
        self.access_patterns[chunk_id] = self.access_patterns.get(chunk_id, 0) + 1

        # 3. Expande malha (lazy)
        if chunk_id not in self.edges:
            self._expand_mesh(chunk_id)

        # 4. Otimiza caminhos frequentes
        self._optimize_hot_paths()

        return chunk

    def _expand_mesh(self, chunk_id: str):
        """Expande malha encontrando chunks similares"""
        chunk = self.nodes[chunk_id]

        # Busca chunks similares (usando embedding quantizado)
        similar = self._find_similar_chunks(chunk.embedding_int8, threshold=0.85)

        # Cria arestas
        for similar_id, similarity in similar:
            self.edges[chunk_id].append(Edge(
                to=similar_id,
                weight=similarity,
                access_count=0
            ))

    def _optimize_hot_paths(self):
        """Otimiza caminhos frequentemente acessados"""
        # Identifica caminhos quentes (acessados > N vezes)
        hot_paths = [
            (a, b) for a, edges in self.edges.items()
            for edge in edges
            if edge.access_count > 10
        ]

        # Pre-computa embeddings para caminhos quentes
        for path in hot_paths:
            if path not in self.hot_paths:
                self._precompute_path_embedding(path)
                self.hot_paths.add(path)
```

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### Quantização de Embeddings

```python
class QuantizedEmbedding:
    """Embedding quantizado INT8 com desquantização on-demand"""

    def __init__(self, embedding_fp32: List[float]):
        self.embedding_int8 = self._quantize(embedding_fp32)
        self.scale = self._compute_scale(embedding_fp32)
        self.zero_point = self._compute_zero_point(embedding_fp32)

    def _quantize(self, fp32: List[float]) -> List[int]:
        """Quantiza FP32 → INT8"""
        min_val = min(fp32)
        max_val = max(fp32)
        scale = (max_val - min_val) / 255.0
        zero_point = int(-min_val / scale)

        return [int((x - min_val) / scale) for x in fp32]

    def dequantize(self) -> List[float]:
        """Desquantiza INT8 → FP32 (on-demand)"""
        return [
            (q - self.zero_point) * self.scale
            for q in self.embedding_int8
        ]

    def similarity_int8(self, other: 'QuantizedEmbedding') -> float:
        """Similaridade usando INT8 diretamente (mais rápido)"""
        # Dot product em INT8 (aproximado)
        dot = sum(a * b for a, b in zip(self.embedding_int8, other.embedding_int8))
        norm_a = sum(a * a for a in self.embedding_int8) ** 0.5
        norm_b = sum(b * b for b in other.embedding_int8) ** 0.5
        return dot / (norm_a * norm_b)
```

---

### Grafo Dinâmico com Clustering

```python
class KnowledgeGraph:
    """Grafo de conhecimento que cresce dinamicamente"""

    def __init__(self):
        self.nodes: Dict[str, QuantizedChunk] = {}
        self.edges: Dict[str, List[Edge]] = {}
        self.clusters: Dict[int, Set[str]] = {}  # Clusters de nós similares
        self.cluster_centroids: Dict[int, QuantizedEmbedding] = {}

    def add_chunk(self, chunk: QuantizedChunk):
        """Adiciona chunk e conecta a cluster similar"""
        self.nodes[chunk.id] = chunk

        # Encontra cluster mais similar
        cluster_id = self._find_closest_cluster(chunk.embedding_int8)

        if cluster_id is None:
            # Cria novo cluster
            cluster_id = len(self.clusters)
            self.clusters[cluster_id] = {chunk.id}
            self.cluster_centroids[cluster_id] = chunk.embedding_int8
        else:
            # Adiciona ao cluster existente
            self.clusters[cluster_id].add(chunk.id)
            # Atualiza centroide (média do cluster)
            self._update_cluster_centroid(cluster_id)

        # Conecta a nós do cluster
        for node_id in self.clusters[cluster_id]:
            if node_id != chunk.id:
                similarity = self._compute_similarity(chunk, self.nodes[node_id])
                if similarity > 0.8:  # Threshold
                    self._add_edge(chunk.id, node_id, similarity)

    def query_similar(self, query_embedding: QuantizedEmbedding, top_k: int = 5):
        """Busca similar usando grafo (mais eficiente que busca linear)"""
        # 1. Encontra cluster mais próximo
        cluster_id = self._find_closest_cluster(query_embedding.embedding_int8)

        # 2. Busca dentro do cluster
        candidates = []
        for node_id in self.clusters[cluster_id]:
            node = self.nodes[node_id]
            similarity = query_embedding.similarity_int8(node.embedding_int8)
            candidates.append((node_id, similarity))

        # 3. Expande para clusters adjacentes (via arestas)
        visited_clusters = {cluster_id}
        for node_id, _ in candidates[:top_k]:
            for edge in self.edges.get(node_id, []):
                target_node = self.nodes[edge.to]
                target_cluster = self._get_cluster_of_node(edge.to)
                if target_cluster not in visited_clusters:
                    visited_clusters.add(target_cluster)
                    # Adiciona nós do cluster adjacente
                    for adj_node_id in self.clusters[target_cluster]:
                        adj_node = self.nodes[adj_node_id]
                        similarity = query_embedding.similarity_int8(adj_node.embedding_int8)
                        candidates.append((adj_node_id, similarity))

        # 4. Retorna top-k
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]
```

---

## 📊 BENEFÍCIOS

### Redução de Memória
- **Embeddings FP32**: 1.5KB por chunk
- **Embeddings INT8**: 384 bytes por chunk
- **Redução**: 75% de memória

### Performance
- **Busca Linear**: O(n) - verifica todos os chunks
- **Busca em Grafo**: O(log n) - busca em clusters
- **Cache de Caminhos**: O(1) - caminhos frequentes pré-computados

### Expansão Dinâmica
- **Lazy Loading**: Chunks carregados apenas quando acessados
- **Lazy Expansion**: Arestas criadas apenas quando necessário
- **Adaptação**: Grafo se adapta a padrões de uso

---

## 🔗 INTEGRAÇÃO COM RAG

```python
class OptimizedRAGRetrieval:
    """RAG com malha neuronal otimizada"""

    def __init__(self):
        self.knowledge_mesh = KnowledgeNeuralMesh()
        self.quantized_indexer = QuantizedEmbeddingIndexer()

    def retrieve(self, query: str, top_k: int = 5):
        # 1. Quantiza query embedding
        query_embedding = self.quantized_indexer.embed(query)
        query_quantized = QuantizedEmbedding(query_embedding)

        # 2. Busca na malha neuronal (otimizada)
        similar_chunks = self.knowledge_mesh.query_similar(
            query_quantized, top_k=top_k
        )

        # 3. Desquantiza apenas os top-k (on-demand)
        results = []
        for chunk_id, similarity in similar_chunks:
            chunk = self.knowledge_mesh.nodes[chunk_id]
            # Desquantiza apenas se necessário
            if similarity > 0.9:  # Alta similaridade
                chunk.dequantize()  # Carrega conteúdo completo
            results.append(chunk)

        return results
```

---

## ✅ IMPLEMENTAÇÃO FASEADA

### Fase 1: Quantização de Embeddings
- Implementar `QuantizedEmbedding`
- Integrar com indexação de datasets
- Testar redução de memória

### Fase 2: Grafo Básico
- Implementar `KnowledgeGraph`
- Clustering básico
- Arestas de similaridade

### Fase 3: Expansão Dinâmica
- Lazy expansion
- Hot paths optimization
- Adaptação a padrões de uso

### Fase 4: Integração RAG
- Integrar com RAGFallbackSystem
- Otimizar busca
- Validar performance

---

## 🎯 RESULTADOS ESPERADOS

- **Memória**: 75% redução em embeddings
- **Latência**: 50% redução em busca (grafo vs linear)
- **Escalabilidade**: O(log n) vs O(n)
- **Adaptação**: Grafo se adapta a uso real

---

**Status**: Conceito validado - Pronto para implementação na Fase 2-3

