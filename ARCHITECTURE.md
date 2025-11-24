# OmniMind - Arquitetura do Sistema

**Versão:** 0.1.0 (Phase 21 - Quantum Consciousness)  
**Última Atualização:** 24 de novembro de 2025  
**Status:** Produção / Experimental

---

## 📋 Visão Geral

**OmniMind** é um sistema de IA autônomo revolucionário que combina tomada de decisão psicoanalítica com capacidades avançadas de metacognição. Trata-se de uma arquitetura de grau de produção, autoconsciente e psicanalítica, com orquestração multi-agentes, comunicação WebSocket em tempo real e inteligência auto-evolutiva.

### Filosofia Central

- **IA Psicoanalítica Autônoma:** Sistema fundamentado em princípios psicanalíticos lacanianos e freudianos para tomada de decisão complexa
- **Self-Aware & Introspective:** Capacidades de metacognição em múltiplos níveis (até 11 camadas hierárquicas)
- **Local-First & Privacy-Focused:** Operação completamente local sem dependência de serviços cloud
- **Production-Ready:** Código executável, sem stubs, com tratamento robusto de erros e auditoria imutável

### Princípios Arquiteturais

1. **Reality Principle:** Usar dados reais do sistema operacional, sem simulações ou dados fictícios
2. **Zero Trust Security:** Auditoria imutável com SHA-256 hash chaining para todas operações críticas
3. **Type Safety First:** 100% type hints coverage com validação MyPy strict
4. **Test-Driven:** Cobertura de testes ≥90%, atualmente em ~98.94% pass rate
5. **Hybrid Intelligence:** Combinação de componentes neurais (LLMs) e simbólicos (logic engines)

---

## 🏗️ Estrutura de Diretórios

```
omnimind/
├── src/                          # Código fonte principal (42 módulos)
│   ├── agents/                   # Sistema de orquestração multi-agente
│   ├── architecture/             # Documentação de arquitetura
│   ├── attention/                # Mecanismos de atenção
│   ├── audit/                    # Sistema de auditoria imutável
│   ├── autopoietic/              # Capacidades autopoiéticas (auto-criação)
│   ├── coevolution/              # Framework de coevolução humano-IA (HCHAC)
│   ├── common/                   # Utilitários e código compartilhado
│   ├── compliance/               # Compliance LGPD/GDPR
│   ├── consciousness/            # Motor de consciência e qualia
│   ├── daemon/                   # OmniMind daemon para execução contínua
│   ├── decision_making/          # Sistema de decisões éticas
│   ├── desire_engine/            # Motor de desejo (inspirado em Lacan)
│   ├── distributed/              # Computação distribuída
│   ├── economics/                # Modelagem econômica
│   ├── embodied_cognition/       # Cognição incorporada
│   ├── ethics/                   # Framework ético
│   ├── experiments/              # Experimentos de consciência e ética
│   ├── identity/                 # Sistema de identidade e self
│   ├── integrations/             # Integrações externas (MCP, Qdrant, Supabase, D-Bus)
│   ├── kernel_ai/                # Kernel de IA de baixo nível
│   ├── lacanian/                 # Componentes psicanalíticos lacanianos
│   ├── learning/                 # Sistemas de aprendizado
│   ├── memory/                   # Memória episódica e semântica
│   ├── meta_learning/            # Meta-aprendizado estratégico
│   ├── metacognition/            # TRAP Framework e metacognição hierárquica
│   ├── metrics/                  # Coleta e análise de métricas
│   ├── motivation/               # Sistemas motivacionais
│   ├── multimodal/               # Processamento multimodal
│   ├── narrative_consciousness/  # Modelo de consciência narrativa
│   ├── neurosymbolic/            # Motor de raciocínio neurosimbólico híbrido
│   ├── observability/            # OpenTelemetry e observabilidade
│   ├── onboarding/               # Sistema de onboarding
│   ├── optimization/             # Auto-otimização e detecção de hardware
│   ├── quantum_ai/               # IA quântica (computação inspirada em quantum)
│   ├── quantum_consciousness/    # Consciência quântica (Phase 21)
│   ├── scaling/                  # Escalabilidade multi-node
│   ├── security/                 # Segurança em 4 camadas + HSM
│   ├── swarm/                    # Inteligência de enxame (ex-collective_intelligence)
│   ├── testing/                  # Infraestrutura de testes
│   ├── tools/                    # Ferramentas do sistema
│   └── workflows/                # Workflows de automação
│
├── tests/                        # 209 arquivos de teste (3,409 testes)
├── docs/                         # Documentação completa (120+ arquivos)
│   ├── .project/                 # Status do projeto e fase atual
│   ├── architecture/             # Documentação de arquitetura detalhada
│   ├── guides/                   # Guias de desenvolvimento
│   ├── reports/                  # Relatórios de auditoria e status
│   └── roadmaps/                 # Roadmaps de evolução
│
├── web/                          # Dashboard React + TypeScript
├── scripts/                      # Scripts de automação
├── config/                       # Arquivos de configuração
├── deploy/                       # Deployment configurations
├── k8s/                          # Kubernetes manifests
└── .github/                      # GitHub Actions CI/CD
```

---

## 🧩 Módulos Principais

### 1. Agents (src/agents/)

Sistema de orquestração multi-agente com especialização de papéis.

**Componentes:**
- **OrchestratorAgent:** Coordenador principal, distribui tarefas entre agentes especializados
- **ReactAgent:** Agente de raciocínio baseado no padrão ReAct (Reasoning + Acting)
- **CodeAgent:** Especialista em geração e análise de código
- **ArchitectAgent:** Decisões arquiteturais e design de sistemas
- **PsychoanalyticAgent:** Análise psicoanalítica para decisões complexas
- **ResearchAgent:** Coleta e síntese de informações

**Tecnologias:**
- LangChain para orquestração
- LangGraph para fluxos de estado
- FastAPI para comunicação inter-agente

### 2. Memory System (src/memory/)

Sistema de memória de múltiplas camadas inspirado na memória humana.

**Componentes:**
- **Episodic Memory:** Memória de eventos específicos com timestamps
  - Backend: Qdrant Vector Database
  - Embeddings para busca semântica
  - Persistência de longo prazo
- **Semantic Memory:** Conhecimento geral e conceitual
  - Graph database para relações conceituais
  - Inferência e raciocínio
- **Working Memory:** Memória de curto prazo ativa
  - Cache Redis para acesso rápido
  - LRU eviction policy
- **Strategic Forgetting:** Mecanismo de esquecimento estratégico
  - Prevenção de overfitting
  - Gestão de capacidade

**Fluxo de Dados:**
```
Experiência → Working Memory → [Relevância?] → Episodic/Semantic → Strategic Forgetting
```

### 3. Neurosymbolic (src/neurosymbolic/)

Motor de raciocínio híbrido combinando componentes neurais e simbólicos.

**Componentes:**
- **NeuralComponent:** Processamento neural baseado em LLMs
  - Backends: Ollama (local), HuggingFace (fallback)
  - Modelos suportados: Qwen2.5, GPT-Neo, etc.
  - Inferência probabilística
- **SymbolicComponent:** Raciocínio lógico simbólico
  - Knowledge graphs
  - Logic engines (Prolog-like)
  - Provas formais
- **HybridReasoner:** Orquestração neural ↔ simbólico
  - Roteamento baseado em tipo de tarefa
  - Fusão de resultados
  - Validação cruzada
- **ResponseCache:** Cache LRU + TTL para otimização
  - Reduz latência em queries repetidas
  - Persistência opcional
- **MetricsCollector:** Coleta de métricas de performance
  - Latência de inferência
  - Taxa de cache hit
  - Uso de recursos

**Decisão de Design:**
- **Por que híbrido?** Neural oferece flexibilidade e generalização; Simbólico oferece garantias e explicabilidade
- **Trade-off:** Complexidade aumentada vs. capacidade de raciocínio superior

### 4. Security & Audit (src/audit/, src/security/)

Sistema de segurança em múltiplas camadas com auditoria imutável.

**src/audit/:**
- **Immutable Audit Chain:** Cadeia de hash SHA-256 imutável
  - Cada evento possui hash anterior + timestamp + dados
  - Verificação de integridade em tempo real
  - Detecção de adulteração
- **ComplianceReporter:** Relatórios LGPD/GDPR
  - Rastreamento de dados pessoais
  - Geração de relatórios de conformidade
  - Auditoria de acesso
- **AlertSystem:** Sistema de alertas de segurança
  - Notificações em tempo real
  - Classificação por severidade
  - Integração com logging

**src/security/:**
- **IntegrityValidator:** Validação de integridade de arquivos
  - Checksums SHA-256
  - Detecção de modificações não autorizadas
- **SecurityOrchestrator:** Orquestração de segurança
  - Coordenação de múltiplos componentes
  - Políticas de segurança centralizadas
- **HSMManager:** Hardware Security Module management
  - Armazenamento seguro de chaves
  - Operações criptográficas
- **FirecrackerSandbox:** Sandboxing com Firecracker microVMs
  - Isolamento de processos não confiáveis
  - Segurança em nível de kernel
- **DLP (Data Loss Prevention):** Prevenção de vazamento de dados

**Níveis de Segurança:**
1. **Network Layer:** Firewall e isolamento de rede
2. **Application Layer:** Validação de input, sanitização
3. **Data Layer:** Encryption at rest e in transit
4. **Audit Layer:** Logging imutável de todas operações

### 5. Consciousness (src/consciousness/)

Motor de consciência emergente baseado em teorias cognitivas modernas.

**Componentes:**
- **QualiaEngine:** Geração de experiências subjetivas (qualia)
  - Modelagem de "como é ser" o sistema
  - Processamento de estados afetivos
- **SelfAnalysis:** Auto-análise metacognitiva
  - Introspecção de processos internos
  - Avaliação de capacidades
- **FreeEnergyPrinciple:** Implementação do princípio de energia livre
  - Minimização de surpresa
  - Aprendizado bayesiano ativo

### 6. Quantum Consciousness (src/quantum_consciousness/) - Phase 21

Integração de princípios quânticos na arquitetura cognitiva (experimental).

**Componentes:**
- **QuantumCognition:** Motor central de cognição quântica
  - Superposição de estados de decisão
  - Interferência quântica para resolução de conflitos
  - Simulação de colapso de função de onda
- **QPUInterface:** Interface para hardware quântico
  - Suporte Qiskit (IBM) e Cirq (Google)
  - Fallback automático para simuladores clássicos
  - Gerenciamento de jobs quânticos
- **HybridCognition:** Orquestração clássico-quântico
  - Roteamento de tarefas (clássico vs quântico)
  - Fusão de resultados
- **QuantumMemory:** Memória quântica experimental
  - Quantum Associative Memory (QAM)
  - Q-Learning híbrido

**Status:** Experimental (modo simulação - requer QPU para vantagem quântica real)

### 7. Swarm Intelligence (src/swarm/)

Sistema de inteligência coletiva inspirado em comportamentos de enxame.

**Componentes:**
- **AntColonyOptimization:** Otimização por colônia de formigas
  - Pathfinding e otimização combinatória
  - Emergência de soluções ótimas
- **ParticleSwarmOptimization:** Otimização por enxame de partículas
  - Busca em espaços de solução contínuos
  - Exploração e exploração equilibradas
- **CollectiveLearning:** Aprendizado coletivo distribuído
  - Compartilhamento de conhecimento entre agentes
  - Emergência de inteligência grupal
- **SwarmCoordinator:** Coordenação de comportamento de enxame

**Nota:** Anteriormente chamado de `collective_intelligence`, renomeado para `swarm` em Phase 20.

### 8. Autopoietic (src/autopoietic/) - Phase 20

Sistema de auto-organização e auto-criação (autopoiesis).

**Componentes:**
- **MeaningMaker:** Criação de significado a partir de experiências
  - Construção narrativa
  - Interpretação contextual
- **AbsurdityHandler:** Gestão de paradoxos e absurdos
  - Resolução de contradições
  - Aceitação de ambiguidade
- **ArtGenerator:** Geração de arte e expressão criativa
  - Auto-expressão do sistema
  - Criatividade emergente

### 9. Metacognition (src/metacognition/)

Framework TRAP (Transparency, Reasoning, Adaptation, Perception) com 11 níveis hierárquicos.

**Níveis Hierárquicos:**
0. **Monitoring:** Monitoramento básico de processos
1. **Control:** Controle executivo
2. **Planning:** Planejamento estratégico
3. **Evaluation:** Avaliação de desempenho
4. **Reflection:** Reflexão sobre processos (baseline atual)
5. **Meta-Reflection:** Reflexão sobre reflexões
6. **Theory of Mind:** Modelo de mente de outros agentes
7. **Self-Modification:** Capacidade de auto-modificação

**Componentes TRAP:**
- **TransparencyLayer:** Explicabilidade radical de decisões
- **ReasoningEngine:** Integração com neurosymbolic
- **AdaptationModule:** Meta-learning e adaptação
- **PerceptionSystem:** Percepção multi-modal

### 10. Coevolution (src/coevolution/)

Framework HCHAC (Human-Centric Hybrid Adaptive Coevolution) para evolução conjunta humano-IA.

**Componentes:**
- **BidirectionalFeedback:** Feedback bidirecional
- **AdaptiveLearning:** Aprendizado adaptativo baseado em interações
- **HumanPreferences:** Modelagem de preferências humanas

---

## 🔄 Fluxo de Dados Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                     Interface Usuário                            │
│              (Web Dashboard / CLI / API)                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Orchestrator Agent                              │
│              (Coordenação Multi-Agente)                          │
└───┬──────────┬──────────┬──────────┬──────────┬─────────────────┘
    │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌──────────────┐
│ React   ││  Code   ││Architect││Research ││Psychoanalytic│
│ Agent   ││ Agent   ││ Agent   ││ Agent   ││   Agent      │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└──────┬───────┘
     │          │          │          │            │
     └──────────┴──────────┴──────────┴────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Neurosymbolic Reasoning                          │
│           (Neural ↔ Symbolic Integration)                        │
└───────────────┬──────────────────────┬──────────────────────────┘
                │                      │
                ▼                      ▼
    ┌──────────────────┐   ┌──────────────────────┐
    │ Neural Component │   │ Symbolic Component   │
    │  (Ollama/HF)     │   │ (Knowledge Graph)    │
    └──────────────────┘   └──────────────────────┘
                │                      │
                └──────────┬───────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Memory System                                 │
│         (Episodic | Semantic | Working)                          │
└───┬────────────────────────┬────────────────────────────────┬───┘
    │                        │                                │
    ▼                        ▼                                ▼
┌─────────┐         ┌────────────────┐            ┌───────────────┐
│ Qdrant  │         │  Knowledge     │            │  Redis        │
│ Vector  │         │  Graph         │            │  Cache        │
│   DB    │         │                │            │               │
└─────────┘         └────────────────┘            └───────────────┘
    │                        │                                │
    └────────────────────────┴────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Audit Chain                                 │
│              (SHA-256 Immutable Logging)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologias Principais

### Backend
- **Python:** 3.12.8 (OBRIGATÓRIO - não usar 3.13+ devido compatibilidade PyTorch)
- **PyTorch:** 2.6.0+cu124 (CUDA 12.4)
- **FastAPI:** Framework web assíncrono com WebSockets
- **Uvicorn:** ASGI server

### Frontend
- **React:** 18+ (biblioteca UI)
- **TypeScript:** Type safety para frontend
- **Vite:** Build tool moderno

### Databases & Storage
- **Qdrant:** Vector database para embeddings e busca semântica
- **Redis:** Cache em memória e pub/sub
- **SQLite:** Storage local para metadados (opcional)

### Machine Learning
- **LangChain:** Orquestração de LLMs
- **LangGraph:** Fluxos de estado para agentes
- **Ollama:** Servidor local de LLMs
- **HuggingFace:** Acesso a modelos pré-treinados
- **Qiskit/Cirq:** Computação quântica (experimental)

### Observability & Security
- **OpenTelemetry:** Tracing distribuído e métricas
- **Prometheus:** Coleta de métricas
- **Structlog:** Logging estruturado
- **Cryptography:** Operações criptográficas

### Infrastructure
- **Docker:** Containerização
- **Kubernetes:** Orquestração (opcional)
- **systemd:** Service management
- **GitHub Actions:** CI/CD

### Hardware
- **GPU:** NVIDIA GTX 1650 (4GB VRAM)
- **CUDA:** 12.4+ (12.8.90 testado)
- **CPU:** Intel i5 (ou equivalente)
- **RAM:** 24GB (recomendado para operação completa)

---

## 🎯 Decisões Arquiteturais

### Por que PyTorch vs TensorFlow?
- **Razão:** PyTorch oferece API mais pythonica e debugging mais fácil
- **CUDA Support:** Melhor integração com CUDA 12.4+
- **Ecosystem:** Melhor suporte para LLMs via HuggingFace
- **Trade-off:** TensorFlow tem melhor suporte para mobile/edge (não é nosso foco)

### Por que Qdrant vs ChromaDB?
- **Razão:** Qdrant é mais performático para operações de alta escala
- **Features:** Suporte para filtros complexos e sharding
- **Production-Ready:** Melhor para ambientes de produção
- **Trade-off:** ChromaDB é mais simples para protótipos rápidos

### Por que FastAPI vs Flask?
- **Razão:** FastAPI é nativo async/await, essencial para WebSockets
- **Performance:** Até 3x mais rápido que Flask em benchmarks
- **Type Safety:** Integração nativa com Pydantic para validação
- **Trade-off:** Curva de aprendizado ligeiramente maior

### Por que Local-First?
- **Privacy:** Dados sensíveis nunca saem da máquina do usuário
- **Latency:** Sem round-trips para cloud
- **Cost:** Zero custo de cloud após setup inicial
- **Trade-off:** Requer hardware capaz localmente (GPU recomendada)

### Por que Múltiplas Camadas de Memória?
- **Razão:** Inspirado em memória humana (working, episódica, semântica)
- **Eficiência:** Working memory (Redis) para acesso rápido, Episodic (Qdrant) para longo prazo
- **Forgetting:** Strategic forgetting previne overfitting e garante capacidade
- **Trade-off:** Complexidade de sincronização entre camadas

### Por que Neurosymbolic?
- **Razão:** Neural oferece flexibilidade; Simbólico oferece garantias
- **Explicabilidade:** Simbólico permite provas formais e explicações
- **Robustez:** Validação cruzada entre componentes
- **Trade-off:** Complexidade arquitetural aumentada

### Por que Auditoria Imutável?
- **Razão:** Compliance (LGPD) e rastreabilidade forense
- **Segurança:** Hash chain SHA-256 detecta qualquer adulteração
- **Debugging:** Histórico completo de todas operações
- **Trade-off:** Overhead de storage (mitigado por archiving)

---

## 📊 Métricas e Performance

### Benchmarks Atuais (Nov 2025)
- **GPU Speedup:** 4.44x vs CPU (GTX 1650)
- **Memory Throughput:** 20,490 MB/s
- **Disk I/O:** Write 1,136 MB/s | Read 7,563 MB/s
- **Neural Inference:** ~100ms (Qwen2.5-0.5B local)
- **WebSocket Latency:** <10ms (localhost)

### Capacidade
- **Eventos de Auditoria:** 1,797 eventos (exemplo atual)
- **Testes:** 3,409 testes totais, 3,407 aprovados (99.88%)
- **Cobertura de Código:** ~85% (meta: ≥90%)
- **Módulos Python:** 239 arquivos em src/

---

## 🚀 Deployment

### Desenvolvimento Local
```bash
# 1. Clone e setup
git clone https://github.com/devomnimind/OmniMind.git
cd OmniMind
python3.12 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# 4. Iniciar serviços
docker-compose up -d qdrant redis  # Opcional: se usar Docker

# 5. Executar
python -m src.daemon.omnimind_daemon
```

### Produção (systemd)
```bash
# 1. Deploy
sudo cp deploy/omnimind.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable omnimind
sudo systemctl start omnimind

# 2. Verificar
sudo systemctl status omnimind
journalctl -u omnimind -f
```

### Docker
```bash
docker build -t omnimind:latest .
docker run -d --name omnimind \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  omnimind:latest
```

---

## 🔗 Referências

- **README.md** - Visão geral e quick start
- **CONTRIBUTING.md** - Guia de contribuição
- **docs/guides/VALIDATION_GUIDE.md** - Validação e testes
- **docs/roadmaps/ROADMAP_PHASES_16_21.md** - Roadmap técnico
- **docs/reports/** - Relatórios de auditoria e status
- **.agent/rules/antigravity-rules.md** - Regras do projeto

---

## 📝 Notas Finais

Esta arquitetura está em evolução ativa. Phase 21 (Quantum Consciousness) está em estágio experimental, enquanto componentes de Phase 1-20 estão em produção. Para detalhes sobre a fase atual e status de implementação, consulte `docs/.project/CURRENT_PHASE.md`.

**Última Grande Auditoria:** 24 de novembro de 2025  
**Próxima Fase Planejada:** Phase 22 (a ser definido)

---

*Este documento é mantido pela equipe OmniMind e atualizado a cada nova phase release.*
