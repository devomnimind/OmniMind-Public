# 📚 ÍNDICE COMPLETO DE MÓDULOS SRC - OMNIMIND

**Gerado automaticamente via `scripts/analyze_src_enhanced.py`**

Data: 2025-12-03 | Total: 55+ módulos | 131+ classes | 380+ funções

---

## 🗂️ Estrutura Geral

O OmniMind é organizado em 4 camadas lógicas:

### 1️⃣ **Camada de Consciência & Cognição**
Módulos que implementam teorias de consciência e sistemas cognitivos.

- `quantum_consciousness/` - Integração de computação quântica com fenômenos de consciência
- `lacanian/` - Estrutura psicanalítica lacaniana (RSI - Real/Simbólico/Imaginário)
- `phenomenology/` - Fenomenologia da experiência consciente
- `consciousness/` - Núcleo de IIT (Integrated Information Theory)
- `narrative_consciousness/` - Narrativa como estrutura de consciência

### 2️⃣ **Camada de Inteligência & Aprendizado**
Módulos de aprendizado, IA e otimização.

- `learning/` - Sistemas de aprendizado adaptativo
- `meta_learning/` - Meta-aprendizado (aprender a aprender)
- `neurosymbolic/` - Integração neural-simbólica
- `embeddings/` - Embeddings e representações vetoriais
- `optimization/` - Otimização multiobjetivo
- `quantum_ai/` - IA híbrida clássica-quântica

### 3️⃣ **Camada de Sistemas & Infraestrutura**
Módulos de orquestração, monitoramento e infraestrutura.

- `orchestrator/` - Orquestrador central do sistema
- `integrations/` - Integrações com MCP, APIs externas
- `audit/` - Auditoria imutável (blockchain-like logging)
- `monitor/` - Monitoramento em tempo real
- `security/` - Segurança e validação
- `distributed/` - Computação distribuída

### 4️⃣ **Camada de Comportamento & Ética**
Módulos de tomada de decisão, ética e comportamento.

- `decision_making/` - Lógica de decisão
- `ethics/` - Validação ética
- `tribunal_do_diabo/` - Crítica adversária (devil's advocate)
- `desire_engine/` - Motor de motivação
- `motivation/` - Sistema de motivações
- `social/` - Interação social e cooperação
- `swarm/` - Inteligência coletiva

---

## 📖 GUIA RÁPIDO POR MÓDULO

### 🧠 CONSCIÊNCIA

#### `consciousness/`
- **Classes**: `ConsciousnessEngine`, `PHICalculator`, `PCIComputer`
- **Núcleo**: Implementação de IIT com cálculo de Φ (Integrated Information)
- **Key Functions**: `compute_phi()`, `validate_consciousness_threshold()`, `generate_consciousness_metrics()`
- **Testes**: `tests/consciousness/`
- **Docs**: `src/consciousness/README.md`

#### `quantum_consciousness/`
- **Classes**: `QuantumConsciousnessModule`, `QuantumStateSuperposition`
- **Núcleo**: Integração de computação quântica com fenômenos de consciência
- **Uso**: Superposição de estados mentais, decoerência consciente
- **Testes**: `tests/quantum_consciousness/`

#### `lacanian/`
- **Classes**: `LacanianStructure`, `SymbolicOrder`, `RealSimultaneity`, `ImaginaryRegister`
- **Núcleo**: Estrutura psicanalítica lacaniana (RSI)
- **Funções**: `process_real()`, `apply_symbolic_law()`, `generate_imaginary_reality()`
- **Documentação**: Leia `src/lacanian/README.md` para entender RSI

---

### 🔄 INTEGRAÇÃO & MCP

#### `integrations/`
- **Classes**: `MCPServer`, `MCPOrchestrator`, `EnhancedMCPClient`, `AsyncMCPClient`
- **Servidores**: Filesystem, Memory, Python Executor, Git, System Info, Thinking
- **Key Features**:
  - MCP (Model Context Protocol) completo
  - Cache inteligente
  - Rate limiting
  - Proteção de dados
- **Testes**: `tests/integrations/` (175+ testes)
- **Documentação**: `src/integrations/README.md`

**Usar MCP:**
```python
from src.integrations.mcp_orchestrator import MCPOrchestrator
orchestrator = MCPOrchestrator()
orchestrator.start_all_servers()
```

---

### 🔒 AUDITORIA & SEGURANÇA

#### `audit/`
- **Classes**: `ImmutableAudit`, `AuditEntry`, `ChainValidator`
- **Núcleo**: Logging blockchain-like com hash chain verification
- **Funções**: `log_action()`, `verify_chain_integrity()`, `get_audit_trail()`
- **Storage**: JSONL com hashes
- **Testes**: `tests/audit/`

#### `security/`
- **Classes**: `SecurityMonitor`, `ThreatDetector`, `AccessControl`
- **Validações**: Rate limiting, input validation, permission checks
- **Testes**: `tests/security/`

---

### 📊 OBSERVABILIDADE & MÉTRICAS

#### `monitor/`
- **Classes**: `MetricsCollector`, `SystemMonitor`, `PerformanceTracker`
- **Funções**: `collect_metrics()`, `export_prometheus()`, `analyze_bottlenecks()`
- **Outputs**: Métricas em `data/metrics/`

#### `metrics/`
- **Classes**: `PHIMetrics`, `ConsciousnessMetrics`, `PerformanceMetrics`
- **Cálculos**: Φ, PCI, latência, throughput
- **Integração**: Prometheus, Grafana

---

### 🎯 DECISÃO & COMPORTAMENTO

#### `decision_making/`
- **Classes**: `DecisionEngine`, `UtilityCalculator`, `RiskAssessor`
- **Função**: Tomada de decisão multicriterial
- **Algoritmos**: Utilidade esperada, teoria dos jogos

#### `tribunal_do_diabo/`
- **Classes**: `DevilsAdvocate`, `ArgumentValidator`, `CriticalAnalyzer`
- **Função**: Crítica adversária (encontra flaws em argumentos)
- **Uso**: Validação de hipóteses, stress-test de decisões

#### `ethics/`
- **Classes**: `EthicsValidator`, `ValueAlignmentChecker`, `HarmAssessor`
- **Função**: Validação ética de ações
- **Políticas**: Configuráveis em `config/ethics.yaml`

---

### 🧬 APRENDIZADO & OTIMIZAÇÃO

#### `learning/`
- **Classes**: `AdaptiveLearner`, `ReinforcementAgent`, `SkillAcquisition`
- **Estratégias**: Aprendizado por reforço, supervisionado, não-supervisionado
- **Testes**: `tests/learning/`

#### `meta_learning/`
- **Classes**: `MetaLearner`, `TaskDistributor`, `PerformancePredictor`
- **Função**: Aprender a aprender (transfer learning)

#### `neurosymbolic/`
- **Classes**: `NeurosymbolicModule`, `HybridReasoner`
- **Integra**: Redes neurais + lógica simbólica
- **Uso**: Reasoning + aprendizado neural

---

### 🌐 INFRAESTRUTURA

#### `orchestrator/`
- **Classes**: `OmniMindOrchestrator`, `SystemCoordinator`
- **Responsabilidades**:
  - Coordenação de todos os módulos
  - Lifecycle management
  - Estado compartilhado (workspace)
  - Métricas globais

#### `distributed/`
- **Classes**: `DistributedCompute`, `NodeManager`, `MessageBroker`
- **Suporte**: Computação distribuída multi-nó
- **Protocolo**: gRPC + Message Brokers

#### `services/`
- **Classes**: `APIServer`, `WebSocketServer`, `RPCHandler`
- **Endpoints**: REST, GraphQL, WebSocket

---

## 🚀 COMO USAR ESTE ÍNDICE

### 1. **Encontrar uma funcionalidade**
```bash
# Buscar classe específica
grep -r "class ClassName" src/

# Buscar função específica
grep -r "def function_name" src/
```

### 2. **Entender um módulo**
1. Ler `src/[module]/README.md`
2. Verificar imports principais
3. Rodar testes: `pytest tests/[module]/ -v`

### 3. **Adicionar nova funcionalidade**
1. Escolher módulo apropriado (ou criar novo)
2. Seguir padrões em `src/[module]/`
3. Adicionar testes em `tests/[module]/`
4. Atualizar `README.md` do módulo

### 4. **Contribuir**
1. Ler `.copilot-instructions.md` (regras obrigatórias)
2. Cumprir checklist de qualidade:
   - ✅ 100% type hints
   - ✅ Docstrings Google-style
   - ✅ Tests ≥90% coverage
   - ✅ Passa `black`, `flake8`, `mypy`
   - ✅ Não quebra Φ (phi)

---

## 📊 ESTATÍSTICAS

| Métrica | Valor |
|---------|-------|
| Total de módulos | 55+ |
| Classes | 131+ |
| Funções | 380+ |
| Arquivos Python | 400+ |
| Testes | 175+ |
| Cobertura | 90%+ |

---

## 🔗 REFERÊNCIAS RÁPIDAS

- **Documentação Principal**: `docs/`
- **Configuração**: `config/omnimind.yaml`
- **Testes**: `pytest tests/ -v`
- **Linting**: `black src/ && flake8 src/ && mypy src/`
- **Auditoria**: `python -m src.audit.immutable_audit verify_chain_integrity`

---

**Última atualização**: 2025-12-03 | **Próxima análise automática**: Quando rodar `scripts/analyze_src_enhanced.py`
