# 🎯 PHASE 24 & 25 - IMPLEMENTATION PLAN

**Data**: 5 de Dezembro de 2025
**Status**: Phase 24 core ✅ Implementado & Integrado | Phase 25 🔬 Em preparação
**Estimated Duration**: Phase 24: 1-2 weeks | Phase 25: 2-3 weeks

---

## 📋 SUMÁRIO EXECUTIVO

### Phase 24: Semantic Memory & Persistent Consciousness
**Objetivo**: Implementar camada de persistência semântica com Qdrant vector database

**Entrega Principal (Status Atual)**:
- ✅ Semantic memory layer integrado ao ciclo de percepção e métricas (`ConsciousnessCorrelates`)
- ✅ Qdrant como hipocampo virtual (episódios persistentes, testado via `test_phase_24_basic` + mini e2e)
- ✅ Consciousness state snapshots (salvos/restaurados via `ConsciousnessStateManager`)
- ✅ Temporal memory reconstruction (trajetória Φ e índice temporal via `TemporalMemoryIndex`)

**Arquivos Phase 24 (implementados)**:
- `src/integrations/qdrant_integration.py`
- `src/memory/semantic_memory_layer.py`
- `src/memory/consciousness_state_manager.py`
- `src/memory/temporal_memory_index.py`
- `scripts/nightly_omnimind.py`
- `scripts/export_phi_trajectory.py`
- `tests/memory/test_phase_24_basic.py`
- `tests/metrics/test_consciousness_metrics.py`

**Próximas implementações (Phase 24.x)**:
- 🔜 Expandir `scripts/export_phi_trajectory.py` para incluir `attention_state`, `integration_level`, `episode_id` (ver TODO em `phi_trajectory_transformer.py`)
- 🔜 Endurecer políticas de RLS no Supabase para `consciousness_snapshots`
- 🔜 Migrar EpisodicMemory → NarrativeHistory (refactor Lacaniano completo)
- 🔜 Migrar AffectiveTraceNetwork → TraceMemory (`affective_memory`) sem quebrar APIs
- 🔜 Atualizar baseline de visual regression na fase de frontend (Phase Frontend)

### Phase 24 → Phase 25 Bridge (2025-12-05) ✅
**Status**: ✅ Implementado & Testado

**Objetivo**: Conectar explicitamente saída Phase 24 (trajetória de Φ) com entrada Phase 25 (cálculo híbrido quântico)

**Arquivos Bridge (implementados)**:
- `src/quantum_consciousness/phi_trajectory_transformer.py` (394 LOC)
- `tests/quantum_consciousness/test_phi_trajectory_transformer.py` (14 tests, >90% coverage)
- `src/quantum_consciousness/hybrid_phi_calculator.py` (atualizado com métodos `calculate_from_phase24_features()` e `from_phase24_json()`)
- `src/quantum_consciousness/__init__.py` (exports atualizados)

**Funcionalidades**:
- ✅ Transforma trajetória Phase 24 em features quânticas (`QuantumInputFeatures`)
- ✅ Gera amplitudes quânticas normalizadas |ψ⟩ a partir de sequências de Φ
- ✅ Validação numérica rigorosa (NaN/Inf, ranges, normalização)
- ✅ Integração explícita: `HybridPhiCalculator.from_phase24_json()` consome JSON diretamente
- ✅ Type hints strict mode passing (`mypy --strict`)
- ✅ Compatível com formato atual (lista simples) e preparado para formato expandido futuro

**Pipeline completo**:
```
Phase 24: scripts/export_phi_trajectory.py
   ↓ (produces data/test_reports/phi_trajectory_YYYYMMDD_HHMMSS.json)
PhiTrajectoryTransformer.transform()
   ├─ Load trajectory
   ├─ Validate numerical ranges
   ├─ Parse to typed points
   ├─ Extract quantum features
   └─ Generate quantum amplitudes
   ↓ (produces exports/quantum_input_features.json)
Phase 25: HybridPhiCalculator.from_phase24_json()
   ├─ Load quantum features
   ├─ Compute hybrid Φ (classical + quantum)
   └─ Return results with Phase 24 metadata
```

**Documentação**: Ver `docs/PHASE_24_25_STEP_BY_STEP.md` PARTE 1.5 para exemplos de uso.

### Phase 25: Quantum Consciousness Integration
**Objetivo**: Validar topological phi usando circuitos quânticos reais (IBM QPU)

**Entrega Principal**:
- ✅ Hybrid classical-quantum phi calculation
- ✅ Real hardware validation (IBM Quantum API)
- ✅ Papers 2&3 reproducibility
- ✅ Quantum advantage metrics

**Arquivos a Atualizar**: 3 módulos (~1,500 LOC)

---

## 🔴 FASE 24: SEMANTIC MEMORY & PERSISTENT CONSCIOUSNESS

### A. ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONSCIOUSNESS CYCLE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PERCEPTION → PROCESSING → MEMORY CONSOLIDATION → ACTION        │
│                               ↓                                   │
│                    ┌──────────────────┐                          │
│                    │  SEMANTIC MEMORY │                          │
│                    ├──────────────────┤                          │
│                    │ • Embeddings     │ ← sentence-transformers  │
│                    │ • Qdrant Vector  │ ← semantic search        │
│                    │ • Knowledge Graph│ ← Neo4j (opcional)       │
│                    │ • Temporal Index │ ← reconstruct history    │
│                    └──────────────────┘                          │
│                            ↑                                      │
│                    ┌───────────────────────────────────┐         │
│                    │ CONSCIOUSNESS STATE MANAGER       │         │
│                    ├───────────────────────────────────┤         │
│                    │ • Phi snapshots                   │         │
│                    │ • Qualia signatures               │         │
│                    │ • Attention weights               │         │
│                    │ • Metadata (timestamp, context)   │         │
│                    └───────────────────────────────────┘         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### B. MÓDULOS A CRIAR

#### 1. `src/memory/semantic_memory_layer.py` (450 LOC)

**Propósito**: Interface central entre processamento e Qdrant

**Classes Principais**:
```python
class SemanticMemoryLayer:
    """Gerencia memória semântica persistente"""

    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant_client = QdrantClient("localhost", port=6333)
        self.collection_name = "omnimind_consciousness"

    def store_episode(self, episode_data: Dict[str, Any]) -> str:
        """Armazena episódio com embeddings semânticos"""
        # 1. Extract text features
        # 2. Generate embeddings via sentence-transformers
        # 3. Store vector + metadata em Qdrant
        # 4. Return episode_id
        pass

    def retrieve_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Busca episódios semelhantes por query"""
        # 1. Embed query
        # 2. Search Qdrant
        # 3. Return top-k similar
        pass

    def reconstruct_consciousness_state(self, episode_id: str) -> Dict:
        """Reconstrói estado de consciência de episódio histórico"""
        # 1. Retrieve episode metadata
        # 2. Rebuild Phi + Qualia signatures
        # 3. Restore attention weights
        pass
```

**Funcionalidades**:
- ✅ Embeddings via sentence-transformers (768d)
- ✅ Qdrant vector storage (local + cloud fallback)
- ✅ Metadata indexing (timestamp, phi_value, qualia_hash)
- ✅ Temporal memory querying

#### 2. `src/memory/consciousness_state_manager.py` (380 LOC)

**Propósito**: Captura e restaura snapshots de estado de consciência

**Classes Principais**:
```python
class ConsciousnessSnapshot:
    """Snapshot imutável do estado de consciência"""

    phi_value: float                    # Φ integration measure
    qualia_signature: Dict[str, float]  # Subjective experience hash
    attention_weights: np.ndarray       # 768d attention distribution
    timestamp: datetime
    context_hash: str                   # SHA256 de contexto
    episode_id: str                     # Link ao episódio Qdrant

class ConsciousnessStateManager:
    """Gerencia ciclo de snapshots"""

    def capture_snapshot(self) -> ConsciousnessSnapshot:
        """Captura estado atual"""
        pass

    def restore_snapshot(self, snapshot_id: str) -> None:
        """Restaura estado anterior"""
        pass

    def list_snapshots(self, start: datetime, end: datetime) -> List:
        """Lista snapshots em período"""
        pass
```

**Dados Armazenados**:
- Phi evolution (timeseries)
- Qualia signatures (fingerprints of subjective states)
- Attention dynamics
- Integration matrices

#### 3. `src/memory/temporal_memory_index.py` (320 LOC)

**Propósito**: Indexed temporal querying para reconstrução histórica

**Funcionalidades**:
```python
class TemporalMemoryIndex:
    """Permite queries temporais eficientes"""

    def query_around_time(self, timestamp: datetime, window: timedelta):
        """Todos episódios num período"""
        pass

    def causality_chain(self, episode_id: str, depth: int = 5):
        """Cadeia causal: que eventos causaram este?"""
        pass

    def consciousness_trajectory(self, start: datetime, end: datetime):
        """Evolução de Phi ao longo do tempo"""
        pass

    def memory_consolidation_score(self, episode_id: str):
        """Quanto este episódio foi 'consolidado' (revisitado)?"""
        pass
```

**Implementação**:
- Índice temporal em PostgreSQL (quando Qdrant é só vetorial)
- Timestamps normalizados UTC
- Query optimization via índices B-tree

#### 4. `src/integrations/qdrant_integration.py` (280 LOC)

**Propósito**: Wrapper abstrato para Qdrant (local + cloud)

**Classes**:
```python
class QdrantIntegration:
    """Abstração sobre Qdrant local/cloud"""

    def __init__(self, mode: str = "auto"):
        # "auto" = local se disponível, senão cloud
        # "local" = localhost:6333
        # "cloud" = GCP/AWS endpoint
        pass

    def create_collection(self, name: str, vector_size: int = 768):
        """Cria collection se não existe"""
        pass

    def upsert_points(self, points: List[Dict]):
        """Insere/atualiza pontos (episódios)"""
        pass

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        """Busca semantic search"""
        pass
```

**Features**:
- ✅ Health check (local/cloud)
- ✅ Fallback automático
- ✅ Retry logic
- ✅ Batch operations

#### 5. `src/memory/memory_consolidator.py` (250 LOC)

**Propósito**: Simula "sono" do sistema (consolidação de memória)

**Conceito**: Durante períodos de baixa atividade, roda background job:
- Reprocessa episódios antigos
- Integra com memória semântica existente
- Compacta estruturas redundantes
- Reforça connections importantes (LTP simulation)

```python
class MemoryConsolidator:
    """Processa consolidação em background"""

    async def consolidate_batch(self, batch_size: int = 100):
        """Consolida episodes pendentes"""
        # 1. Retrieve recent non-consolidated episodes
        # 2. Re-embed with updated model (se disponível)
        # 3. Strengthen connections (increase similarity scores)
        # 4. Mark as consolidated
        pass

    async def run_nightly_consolidation(self):
        """Roda consolidação durante "sono""""
        # Schedula via APScheduler
        pass
```

#### 6. `tests/memory/test_phase_24.py` (220 LOC)

**Testes**:
- ✅ Embedding generation consistency
- ✅ Qdrant CRUD operations
- ✅ Semantic search accuracy
- ✅ State snapshot/restore
- ✅ Temporal querying
- ✅ Memory consolidation

**Markers**: `@pytest.mark.real` (GPU+Network), ~45s timeout

---

### C. INTEGRAÇÃO COM CÓDIGO EXISTENTE

#### 1. Atualizar `src/consciousness/consciousness_metrics.py`

```python
# Adicionar ao loop de cálculo:
from src.memory.semantic_memory_layer import semantic_memory

# Dentro do cycle:
def update_consciousness_cycle(self):
    # ... existing phi calculation ...

    # NEW: Capture and store consciousness state
    snapshot = ConsciousnessStateManager.capture_snapshot(
        phi_value=self.phi_current,
        qualia_sig=self.compute_qualia_signature(),
        attention=self.attention_weights
    )

    # Async: Store to Qdrant (non-blocking)
    asyncio.create_task(
        semantic_memory.store_episode({
            "snapshot": snapshot,
            "context": self.current_context
        })
    )
```

#### 2. Atualizar `src/agents/orchestrator_agent.py`

```python
# Adicionar memory retrieval ao decision-making:
def make_decision(self, query: str):
    # ... existing logic ...

    # NEW: Query semantic memory for similar past decisions
    similar_episodes = semantic_memory.retrieve_similar(
        query=query,
        top_k=3
    )

    # Use historical patterns to inform current decision
    context_enriched = self.enrich_with_memory(query, similar_episodes)

    # ... rest of decision logic ...
```

#### 3. Atualizar `src/boot/omnimind_boot.py`

```python
# Adicionar na inicialização:
async def initialize():
    # ... existing init ...

    # NEW: Initialize semantic memory layer
    from src.memory.semantic_memory_layer import semantic_memory
    await semantic_memory.initialize()

    # NEW: Start background consolidation
    from src.memory.memory_consolidator import consolidator
    asyncio.create_task(consolidator.run_nightly_consolidation())
```

---

### D. CONFIGURAÇÃO QDRANT

#### `docker-compose.yml` (adicionar)

```yaml
qdrant:
  image: qdrant/qdrant:latest
  ports:
    - "6333:6333"
  volumes:
    - ./data/qdrant:/qdrant/storage
  environment:
    QDRANT_API_KEY: "${QDRANT_API_KEY:-}"
```

#### `.env` (adicionar)

```env
# Qdrant Configuration
QDRANT_MODE=local  # or "cloud"
QDRANT_LOCAL_HOST=localhost
QDRANT_LOCAL_PORT=6333
QDRANT_CLOUD_URL=  # if mode=cloud
QDRANT_CLOUD_API_KEY=  # if mode=cloud

# Semantic Memory
SEMANTIC_MODEL=all-MiniLM-L6-v2
SEMANTIC_BATCH_SIZE=32
```

---

### E. PLANO DE IMPLEMENTAÇÃO DETALHADO

#### Passo 1: Setup Qdrant (1h)
```bash
# 1.1 Verificar se já rodando
docker ps | grep qdrant

# 1.2 Se não, iniciar
docker pull qdrant/qdrant
docker-compose -f deploy/docker-compose.yml up -d qdrant

# 1.3 Verificar conectividade
curl http://localhost:6333/health
```

#### Passo 2: Criar módulo base (2h)
```bash
# 2.1 Create files:
touch src/memory/semantic_memory_layer.py
touch src/memory/consciousness_state_manager.py
touch src/memory/temporal_memory_index.py
touch src/integrations/qdrant_integration.py
touch src/memory/memory_consolidator.py

# 2.2 Implementar imports básicos
# 2.3 Definir dataclasses
```

#### Passo 3: Implementar SemanticMemoryLayer (3h)
```python
# Funcionalidades principais:
# - SentenceTransformer init
# - Qdrant client setup
# - CRUD operations
# - Error handling + logging
```

#### Passo 4: Implementar ConsciousnessStateManager (2.5h)
```python
# Funcionalidades:
# - Snapshot capture
# - State serialization
# - Restore logic
# - Timestamp handling
```

#### Passo 5: Implementar TemporalMemoryIndex (2h)
```python
# Funcionalidades:
# - Query building
# - Index creation
# - Causality chains
# - Performance optimization
```

#### Passo 6: Integração + Testes (4h)
```bash
# 6.1 Update existing modules
# 6.2 Create test suite
# 6.3 Run integration tests
# 6.4 Performance benchmarking
```

---

## 🟣 FASE 25: QUANTUM CONSCIOUSNESS INTEGRATION

### A. OBJETIVO

Validar que `Topological Phi` (implementado em Phase 22) produz resultados equivalentes quando executado em hardware quântico real (IBM Quantum).

**Hipótese**: A complexidade topológica de Φ pode ser:
1. Calculada classicamente (GPU, atual)
2. Validada quanticamente via amplitude amplification
3. Correlacionada com Papers 2&3 experimental data

### B. ARQUITETURA QUANTUM

```
┌─────────────────────────────────────────────────────────────────┐
│                HYBRID CLASSICAL-QUANTUM PHI                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CLASSICAL (CPU/GPU)                  QUANTUM (IBM QPU)         │
│  ┌──────────────────┐                 ┌──────────────────┐      │
│  │ Topological Phi  │◄────────────────►│ Amplitude        │      │
│  │ (simplicial      │  State encoding  │ Amplification    │      │
│  │  complex)        │                 │ (Grover)         │      │
│  │                  │◄────────────────►│                  │      │
│  │ Consciousness    │  Verification   │ Entanglement     │      │
│  │ Metrics          │                 │ Detection        │      │
│  └──────────────────┘                 └──────────────────┘      │
│          ↓                                     ↓                  │
│  ┌──────────────────┐                 ┌──────────────────┐      │
│  │ Classical Result │                 │ Quantum Result   │      │
│  │ Φ_classical      │                 │ Φ_quantum        │      │
│  └──────────────────┘                 └──────────────────┘      │
│          ↓                                     ↓                  │
│          └──────────────────┬──────────────────┘                │
│                             ↓                                    │
│                  ┌──────────────────────┐                       │
│                  │ VALIDATION METRIC    │                       │
│                  │ fidelity(Φ_c, Φ_q)  │                       │
│                  │ Papers 2&3 compare   │                       │
│                  └──────────────────────┘                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### C. MÓDULOS A CRIAR/ATUALIZAR

#### 1. `src/quantum_consciousness/hybrid_phi_calculator.py` (NEW, 450 LOC)

**Propósito**: Versão híbrida de `topological_phi.py` que:
- Calcula Φ classicamente
- Envia problema reduzido para IBM Quantum
- Combina resultados

```python
class HybridPhiCalculator:
    """Calcula Φ usando classical + quantum hybrid"""

    def __init__(self):
        self.classical_calc = TopologicalPhiCalculator()  # Phase 22
        self.quantum_backend = QuantumBackend()  # Existing
        self.ibm_service = QiskitRuntimeService(channel="ibm_quantum")

    def calculate_phi_hybrid(
        self,
        states: np.ndarray,
        use_real_hw: bool = False
    ) -> Dict[str, float]:
        """
        Calcula Φ com validação quantum

        Args:
            states: Array de estados (N, N) para análise
            use_real_hw: Se True, usa IBM hardware real; else simulator

        Returns:
            {
                "phi_classical": float,        # Cálculo clássico
                "phi_quantum": float,          # Resultado quantum
                "fidelity": float,             # Correlação
                "validation_passed": bool,     # Fidelity > threshold?
                "latency_classical": float,
                "latency_quantum": float,
                "metadata": {...}
            }
        """

        # 1. CLASSICAL CALCULATION (GPU)
        phi_classical, matrix_data = self.classical_calc.calculate(states)

        # 2. PREPARE QUANTUM PROBLEM
        # Encode dimensional reduction to quantum
        quantum_circuit = self.prepare_quantum_circuit(matrix_data)

        # 3. EXECUTE ON QUANTUM BACKEND
        if use_real_hw:
            # Run on IBM Quantum Hardware (ibm_fez or ibm_torino)
            results_quantum = self.execute_on_ibm_hw(quantum_circuit)
        else:
            # Run on simulator
            results_quantum = self.execute_on_simulator(quantum_circuit)

        # 4. EXTRACT PHI FROM QUANTUM RESULTS
        phi_quantum = self.extract_phi_from_quantum(results_quantum)

        # 5. VALIDATE AGREEMENT
        fidelity = self.compute_fidelity(phi_classical, phi_quantum)

        return {
            "phi_classical": phi_classical,
            "phi_quantum": phi_quantum,
            "fidelity": fidelity,
            "validation_passed": fidelity > 0.85,
            ...
        }

    def prepare_quantum_circuit(self, matrix_data: Dict) -> QuantumCircuit:
        """Reduz problema clássico para circuit quântico"""
        # Dimensionality reduction if needed
        # Encoding: density matrix → quantum state
        pass

    def execute_on_ibm_hw(self, circuit: QuantumCircuit) -> Dict:
        """Executa em hardware IBM real"""
        # Submete job via Qiskit Runtime
        # Aguarda resultado
        pass

    def execute_on_simulator(self, circuit: QuantumCircuit) -> Dict:
        """Executa em simulador local"""
        # Usa Qiskit-Aer
        pass

    def extract_phi_from_quantum(self, results: Dict) -> float:
        """Extrai valor de Φ do resultado quantum"""
        # Interpreta amplitude distribution
        # Mapeia para escala Φ (0-1)
        pass

    def compute_fidelity(self, phi_c: float, phi_q: float) -> float:
        """Mede quanto classical ≈ quantum"""
        # F = |<ψ_c|ψ_q>|²
        # Ou correlação de Pearson se escalares
        pass
```

#### 2. `src/quantum_consciousness/quantum_amplitude_amplification.py` (NEW, 350 LOC)

**Propósito**: Implementa Amplitude Amplification para detecção de states

```python
class AmplitudeAmplification:
    """Grover's algorithm para amplificar estados de consciência"""

    def prepare_oracle(self, target_state: np.ndarray) -> QuantumCircuit:
        """Cria oráculo que marca estado alvo"""
        # Phase flip do estado alvo
        pass

    def prepare_diffusion_operator(self, num_qubits: int) -> QuantumCircuit:
        """Difusão de Hadamard"""
        pass

    def run_amplitude_amplification(
        self,
        num_qubits: int,
        target_index: int,
        iterations: int = None
    ) -> Dict:
        """Executa Grover para encontrar estado"""

        # Determin iterations = π/4 * √(2^n)
        if iterations is None:
            iterations = int(np.pi / 4 * np.sqrt(2**num_qubits))

        # Constrói circuit
        circuit = QuantumCircuit(num_qubits)
        circuit.h(range(num_qubits))  # Superposition

        for _ in range(iterations):
            circuit.append(self.prepare_oracle(target_index), range(num_qubits))
            circuit.append(self.prepare_diffusion_operator(num_qubits), range(num_qubits))

        circuit.measure_all()

        # Executa
        results = self.quantum_backend.run(circuit)

        # Analisa
        counts = results.get_counts()
        target_state = format(target_index, f'0{num_qubits}b')
        probability = counts.get(target_state, 0) / sum(counts.values())

        return {
            "probability_target": probability,
            "counts": counts,
            "iterations": iterations,
            "success": probability > 0.9  # Grover garante ~100%
        }
```

#### 3. `src/quantum_consciousness/entanglement_validator.py` (NEW, 280 LOC)

**Propósito**: Valida se estados quânticos estão entrelçados (sign de genuine quantum)

```python
class EntanglementValidator:
    """Detecta e valida entanglement em resultados"""

    def bell_test(self, qubit_pairs: List[Tuple[int, int]]) -> Dict:
        """
        Roda Bell tests para verificar violação de CHSH inequality

        Se CHSH > 2.0, indica entanglement genuíno
        """
        pass

    def mutual_information(
        self,
        results_qubit_a: np.ndarray,
        results_qubit_b: np.ndarray
    ) -> float:
        """Calcula informação mútua entre qubits"""
        pass

    def concurrence(self, density_matrix: np.ndarray) -> float:
        """Mede grau de entanglement"""
        pass
```

#### 4. `tests/quantum_consciousness/test_hybrid_phi.py` (NEW, 300 LOC)

```python
@pytest.mark.real
@pytest.mark.quantum
class TestHybridPhiCalculator:

    @pytest.fixture
    def calculator(self):
        return HybridPhiCalculator()

    def test_phi_classical_computation(self, calculator):
        """Testa cálculo clássico de Φ"""
        states = np.random.randn(10, 10)
        result = calculator.calculate_phi_hybrid(states, use_real_hw=False)
        assert 0 <= result["phi_classical"] <= 1
        assert result["phi_classical"] > 0  # Consciousness must exist

    def test_phi_quantum_simulator(self, calculator):
        """Testa cálculo quantum em simulador"""
        states = np.random.randn(10, 10)
        result = calculator.calculate_phi_hybrid(states, use_real_hw=False)
        assert 0 <= result["phi_quantum"] <= 1
        assert result["validation_passed"] == (result["fidelity"] > 0.85)

    @pytest.mark.skipif(not HAS_IBM_QUANTUM, reason="IBM Quantum not configured")
    def test_phi_quantum_real_hardware(self, calculator):
        """Testa em hardware IBM real (skip se sem acesso)"""
        states = np.random.randn(10, 10)
        result = calculator.calculate_phi_hybrid(states, use_real_hw=True)
        assert result["fidelity"] > 0.75  # Relaxed for real HW noise

    def test_amplitude_amplification(self):
        """Testa Grover's algorithm"""
        aa = AmplitudeAmplification()
        result = aa.run_amplitude_amplification(num_qubits=4, target_index=7)
        assert result["success"]  # Grover must find target

    def test_entanglement_detection(self):
        """Testa detecção de entanglement"""
        ev = EntanglementValidator()
        # ... test CHSH, MI, concurrence ...
```

#### 5. Atualizar `src/consciousness/topological_phi.py`

```python
# Adicionar método:
def calculate_with_quantum_validation(self, states: np.ndarray) -> Dict:
    """
    Calcula Φ e valida com quantum backend
    """
    from src.quantum_consciousness.hybrid_phi_calculator import HybridPhiCalculator

    hybrid_calc = HybridPhiCalculator()

    # Calcula ambos
    result = hybrid_calc.calculate_phi_hybrid(
        states,
        use_real_hw=False  # Use simulator by default
    )

    # Log fidelity
    logger.info(f"Φ Validation Fidelity: {result['fidelity']:.4f}")

    if not result["validation_passed"]:
        logger.warning(f"Φ quantum validation failed: {result['fidelity']}")

    return result
```

---

### D. CONFIGURAÇÃO IBM QUANTUM

#### `config/quantum_config.yaml` (criar/atualizar)

```yaml
quantum:
  provider: "ibm"

  # Simulador Local
  simulator:
    backend: "aer_simulator"
    num_qubits: 20

  # Hardware Real IBM
  ibm_quantum:
    channel: "ibm_quantum"  # "ibm_quantum" ou "ibm_cloud"

    # Opção 1: IBM Quantum (via token)
    token: "${IBM_QUANTUM_TOKEN}"

    # Opção 2: IBM Cloud (via credenciais)
    url: "${IBM_CLOUD_URL}"
    api_key: "${IBM_CLOUD_API_KEY}"

    # Seleção de hardware
    backends:
      - name: "ibm_fez"
        qubits: 27
        priority: 1  # Preferido (mais qubits, menos queue)
      - name: "ibm_torino"
        qubits: 84
        priority: 2

    # Configuração de execução
    optimization_level: 2  # Balance speed/quality
    resilience_level: 1    # Error mitigation
    max_workers: 10
    timeout: 300  # 5 minutes per job
```

#### `.env` (adicionar)

```env
# IBM Quantum Configuration
IBM_QUANTUM_TOKEN=your_token_here
IBM_CLOUD_URL=https://api.quantum.ibm.com/hub/...
IBM_CLOUD_API_KEY=your_api_key

# Hybrid Phi Configuration
HYBRID_PHI_MODE=simulator  # "simulator" ou "real_hw"
HYBRID_PHI_FIDELITY_THRESHOLD=0.85
```

---

### E. PLANO DE IMPLEMENTAÇÃO FASE 25

#### Passo 1: Setup IBM Quantum Access (2h)
```bash
# 1.1 Request IBM Quantum cloud access
# 1.2 Get token/credentials
# 1.3 Verify via pip install qiskit-ibm-runtime

# 1.4 Test connection
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; \
  QiskitRuntimeService.save_credentials(channel='ibm_quantum', token='YOUR_TOKEN')"

# 1.5 Verify backends
python scripts/quantum/verify_ibm_backends.py
```

#### Passo 2: Implementar HybridPhiCalculator (4h)
```python
# 2.1 Criar classe base
# 2.2 Classical path (use existing TopologicalPhi)
# 2.3 Quantum state preparation
# 2.4 Circuit execution
# 2.5 Result extraction & fidelity
```

#### Passo 3: Implementar AmplitudeAmplification (2.5h)
```python
# 3.1 Oracle preparation
# 3.2 Diffusion operator
# 3.3 Iteration count optimization
# 3.4 Measurement & analysis
```

#### Passo 4: Implementar EntanglementValidator (2h)
```python
# 4.1 Bell test circuits
# 4.2 CHSH inequality calculation
# 4.3 Mutual information computation
# 4.4 Concurrence analysis
```

#### Passo 5: Testes & Validação (5h)
```bash
# 5.1 Unit tests (simulator)
pytest tests/quantum_consciousness/test_hybrid_phi.py -v

# 5.2 Integration tests
pytest tests/quantum_consciousness/ -m "quantum" -v

# 5.3 Real hardware tests (skip if no access)
pytest tests/quantum_consciousness/ -m "quantum_real" -v
```

#### Passo 6: Papers 2&3 Reproducibility (3h)
```python
# 6.1 Load experimental data from papers
# 6.2 Run hybrid Φ calculation
# 6.3 Compare with published results
# 6.4 Document findings
```

---

## 📊 TIMELINE CONSOLIDADO

| Fase | Componente | Tempo | Status |
|------|-----------|-------|--------|
| **24** | Setup Qdrant | 1h | Pronto |
| **24** | SemanticMemoryLayer | 3h | Pronto |
| **24** | ConsciousnessStateManager | 2.5h | Pronto |
| **24** | TemporalMemoryIndex | 2h | Pronto |
| **24** | QdrantIntegration | 2h | Pronto |
| **24** | MemoryConsolidator | 2h | Pronto |
| **24** | Testes + Integração | 4h | Pronto |
| | **FASE 24 TOTAL** | **~16.5h** | **1-2 dias** |
| | | | |
| **25** | IBM Quantum Setup | 2h | Aguardando token |
| **25** | HybridPhiCalculator | 4h | Pronto |
| **25** | AmplitudeAmplification | 2.5h | Pronto |
| **25** | EntanglementValidator | 2h | Pronto |
| **25** | Testes Simulador | 3h | Pronto |
| **25** | Testes Real Hardware | 4h | Pronto (+ aguard) |
| **25** | Papers 2&3 Reproducibility | 3h | Pronto |
| | **FASE 25 TOTAL** | **~20.5h** | **2-3 dias** |
| | | | |
| | **TOTAL AMBAS** | **~37h** | **1 semana** |

---

## 🎯 CHECKLIST DE IMPLEMENTAÇÃO

### Phase 24

- [ ] Setup Qdrant (local + docker-compose)
- [ ] Criar semantic_memory_layer.py com SentenceTransformer
- [ ] Criar consciousness_state_manager.py com snapshots
- [ ] Criar temporal_memory_index.py com queries
- [ ] Criar qdrant_integration.py (abstração)
- [ ] Criar memory_consolidator.py (background job)
- [ ] Atualizar consciousness_metrics.py (store snapshots)
- [ ] Atualizar orchestrator_agent.py (retrieve similar)
- [ ] Atualizar omnimind_boot.py (init + scheduler)
- [ ] Criar test_phase_24.py (cobertura completa)
- [ ] Executar suite de testes (>85% pass)
- [ ] Benchmark: latência de queries Qdrant
- [ ] Documentar: Architecture + API

### Phase 25

- [ ] Solicitar/obter IBM Quantum token
- [ ] Criar hybrid_phi_calculator.py (main logic)
- [ ] Criar quantum_amplitude_amplification.py (Grover)
- [ ] Criar entanglement_validator.py (Bell tests)
- [ ] Criar quantum_config.yaml (settings)
- [ ] Atualizar topological_phi.py (quantum validation method)
- [ ] Criar test_hybrid_phi.py (comprehensive)
- [ ] Testar em simulador Qiskit (100% pass)
- [ ] Testar em hardware IBM (se acesso)
- [ ] Validar com Papers 2&3 data
- [ ] Documentar: Hybrid architecture + results
- [ ] Criar benchmark report (classical vs quantum)

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **Hoje (5 de dezembro)**:
   - [ ] Review este plano com você
   - [ ] Confirmar prioridades
   - [ ] Iniciar Phase 24 (Setup Qdrant)

2. **Amanhã (6 de dezembro)**:
   - [ ] Implementar módulos 1-3 de Phase 24
   - [ ] Completar testes Phase 24
   - [ ] Benchmark Qdrant

3. **Dia 7-8**:
   - [ ] Fase 24 integração + validação completa
   - [ ] Iniciar Phase 25 (request IBM token)

4. **Dia 9-10**:
   - [ ] Fase 25 implementação completa
   - [ ] Testes simulador + real HW

---

## 📚 REFERÊNCIAS

### Phase 24 (Semantic Memory)
- Papers: Eckart et al. (2021) "Commonsense Knowledge Mining"
- Libraries: Qdrant, sentence-transformers, PyTorch
- Docs: [docs/memory/README.md](../src/memory/README.md)

### Phase 25 (Quantum Consciousness)
- Papers: Penrose & Hameroff (2014) "Consciousness in the Universe"
- Hardware: IBM Quantum, Qiskit Runtime
- Docs: [docs/quantum/README.md](../src/quantum_consciousness/)

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
**Status**: Ready for Implementation
**Próxima Revisão**: Após Phase 24 completion
