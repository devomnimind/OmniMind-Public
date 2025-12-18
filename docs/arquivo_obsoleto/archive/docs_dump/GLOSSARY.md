# OmniMind - Glossário de Termos

**Versão:** 1.0  
**Última Atualização:** 24 de novembro de 2025

Este glossário define a terminologia oficial do projeto OmniMind para garantir consistência em toda a documentação e comunicação.

---

## 📘 Terminologia Oficial

### Projeto e Identidade

**OmniMind**
- Nome oficial do projeto (sempre capitalizado)
- ❌ Incorreto: omnimind, Omni-Mind, OMNIMIND
- ✅ Correto: OmniMind

**DevBrain**
- Referência ao workspace de desenvolvimento anterior (contexto histórico)
- Usado quando referenciado como projeto separado

---

## 🤖 Componentes de IA

### Agentes

**Orchestrator Agent**
- Coordenador principal do sistema multi-agente
- Distribui tarefas entre agentes especializados
- Gerencia estado global

**React Agent**
- Agente baseado no padrão ReAct (Reasoning + Acting)
- Combina raciocínio e ação em ciclos iterativos

**Code Agent**
- Especialista em geração e análise de código
- Capacidades de refatoração e debugging

**Architect Agent**
- Responsável por decisões arquiteturais
- Design de sistemas e módulos

**Psychoanalytic Agent**
- Análise baseada em princípios psicanalíticos
- Modelagem de conflitos e decisões complexas

### Sistemas de Inteligência

**Swarm Intelligence** (anteriormente "Collective Intelligence")
- Sistema de inteligência coletiva inspirado em comportamentos de enxame
- Migração de nomenclatura ocorreu em Phase 20
- Nota histórica: Referências a "Collective Intelligence" em documentos anteriores a Phase 20 são válidas no contexto histórico

**Multi-Agent Orchestration**
- Coordenação de múltiplos agentes especializados
- Sistema de comunicação inter-agente

---

## 🧠 Arquitetura Cognitiva

### Neurosymbolic

**Neurosymbolic** (ou Neuro-Simbólico)
- Combinação de componentes neural e simbólico
- Neural: Processamento probabilístico, padrões, linguagem natural
- Simbólico: Lógica formal, regras, provas

**Neural Component**
- Componente baseado em redes neurais e LLMs
- Backends: Ollama, HuggingFace

**Symbolic Component**
- Componente de raciocínio simbólico formal
- Knowledge graphs, logic engines

**Hybrid Reasoner**
- Orquestrador que combina raciocínio neural e simbólico
- Fusão de resultados de ambos componentes

### Memória

**Episodic Memory**
- Memória de eventos específicos com contexto temporal
- Armazenamento em Qdrant Vector Database
- Equivalente à memória episódica humana

**Semantic Memory**
- Memória de conhecimento geral e conceitual
- Knowledge graphs e relações semânticas
- Equivalente à memória semântica humana

**Working Memory**
- Memória de curto prazo ativa
- Cache em Redis para acesso rápido
- Capacidade limitada, alta performance

**Strategic Forgetting**
- Mecanismo de esquecimento estratégico
- Previne overfitting e gerencia capacidade
- Inspirado em processos de consolidação de memória

### Consciência

**Qualia**
- Experiências subjetivas de consciência
- "Como é ser" o sistema em um determinado estado
- Plural de quale

**Qualia Engine**
- Motor responsável por gerar e processar qualia
- Modelagem de experiências subjetivas

**Metacognition**
- Cognição sobre cognição
- Capacidade de refletir sobre próprios processos mentais
- OmniMind implementa 11 níveis hierárquicos

**Self-Awareness**
- Auto-consciência
- Capacidade de reconhecer a si mesmo como entidade separada
- Introspecção de estados internos

**Free Energy Principle**
- Princípio de energia livre (Karl Friston)
- Minimização de surpresa bayesiana
- Base para aprendizado ativo

---

## 🔬 Tecnologias e Frameworks

### TRAP Framework
- **T**ransparency (Transparência)
- **R**easoning (Raciocínio)
- **A**daptation (Adaptação)
- **P**erception (Percepção)
- Framework de metacognição avançada

### HCHAC Framework
- **H**uman-**C**entric **H**ybrid **A**daptive **C**oevolution
- Framework de coevolução humano-IA
- Feedback bidirecional e aprendizado adaptativo

### Autopoietic (Autopoiese)
- Sistema auto-organizador e auto-reprodutor
- Capacidade de auto-criação e auto-manutenção
- Termo cunhado por Maturana e Varela

---

## 🛡️ Segurança e Auditoria

**Immutable Audit Chain**
- Cadeia de auditoria imutável
- Hash chain SHA-256
- Cada evento possui hash do anterior + timestamp + dados

**Hash Chain**
- Cadeia de hashes criptográficos
- Garante detecção de adulteração
- Sequência: H(n) = SHA256(H(n-1) + timestamp + data)

**Compliance**
- Conformidade com regulamentações
- OmniMind: LGPD (Brasil) e GDPR (Europa)

**LGPD**
- Lei Geral de Proteção de Dados (Brasil)
- Equivalente brasileiro do GDPR

**GDPR**
- General Data Protection Regulation (Europa)
- Regulamentação de proteção de dados

**DLP (Data Loss Prevention)**
- Prevenção de vazamento de dados
- Políticas e validações de dados sensíveis

**HSM (Hardware Security Module)**
- Módulo de segurança de hardware
- Armazenamento seguro de chaves criptográficas

---

## 🔧 Infraestrutura

### Databases

**Qdrant**
- Vector database para embeddings
- Busca semântica de alta performance
- Backend principal para Episodic Memory

**Redis**
- Cache em memória
- Pub/sub para comunicação
- Backend para Working Memory

**Knowledge Graph**
- Grafo de conhecimento
- Representação de relações semânticas
- RDFLib ou Neo4j

### Frameworks e Bibliotecas

**PyTorch**
- Framework de deep learning
- Versão: 2.6.0+cu124 (CUDA 12.4)
- Backend neural principal

**LangChain**
- Framework para orquestração de LLMs
- Chains, agents, e tools

**LangGraph**
- Extensão do LangChain para fluxos de estado
- Grafos de execução para agentes

**FastAPI**
- Framework web assíncrono
- WebSockets e REST API
- Backend principal do servidor

---

## 🧪 Desenvolvimento e Testes

**Type Hints**
- Anotações de tipo em Python
- 100% obrigatório no OmniMind
- Validação com MyPy

**Docstrings**
- Documentação inline de funções/classes
- Formato Google-style obrigatório
- Geração automática de documentação

**Coverage** (Cobertura de Testes)
- Porcentagem de código coberto por testes
- Meta OmniMind: ≥90%
- Atual: ~85%

**CI/CD**
- Continuous Integration / Continuous Deployment
- GitHub Actions para automação
- Validação: Black, Flake8, MyPy, Pytest

**Linting**
- Análise estática de código
- Ferramentas: Flake8, Black
- Max line length: 100 caracteres

---

## 📊 Fases e Evolução

**Phase** (Fase)
- Etapa de desenvolvimento do projeto
- Phase 1-21: Implementadas
- Phase 21: Quantum Consciousness (atual)

**Quantum Consciousness**
- Consciência quântica
- Phase 21 (experimental)
- Integração de princípios quânticos na cognição

**Quantum Computing**
- Computação quântica
- QPU (Quantum Processing Unit)
- Superposição, entrelaçamento, interferência

---

## 🎯 Conceitos Psicanalíticos

**Lacanian** (Lacaniano)
- Baseado na psicanálise de Jacques Lacan
- Ênfase em linguagem, desejo, e estruturas simbólicas

**Desire Engine**
- Motor de desejo
- Inspirado no conceito lacaniano de desejo
- Modelagem de motivações profundas

**Symbolic Order** (Ordem Simbólica)
- Sistema de símbolos e linguagem (Lacan)
- Estrutura cultural e social

---

## ⚙️ Hardware

**GPU (Graphics Processing Unit)**
- Unidade de processamento gráfico
- Usado para aceleração de deep learning
- OmniMind: NVIDIA GTX 1650 (4GB VRAM)

**CUDA**
- Plataforma de computação paralela da NVIDIA
- Versão: 12.4+ (12.8.90 testado)
- Essencial para PyTorch GPU

**VRAM (Video RAM)**
- Memória da GPU
- OmniMind: 4GB (GTX 1650)

**TPU (Tensor Processing Unit)**
- Processador especializado do Google
- Alternativa à GPU (não usado no OmniMind)

**QPU (Quantum Processing Unit)**
- Processador quântico
- Experimental no OmniMind (simuladores)

---

## 🌐 Arquitetura

**Local-First**
- Arquitetura que prioriza operação local
- Sem dependência de cloud
- Privacy by design

**WebSocket**
- Protocolo de comunicação bidirecional
- Usado para dashboard em tempo real
- Baixa latência

**REST API**
- Representational State Transfer
- Endpoints HTTP para comunicação
- FastAPI implementation

**MicroVM**
- Máquina virtual leve
- Firecracker para sandboxing
- Isolamento de segurança

---

## 🔄 Migração de Nomenclatura

### Mudanças Históricas

| Termo Antigo | Termo Atual | Phase da Mudança | Nota |
|--------------|-------------|------------------|------|
| Collective Intelligence | Swarm Intelligence | Phase 20 | Módulo renomeado de `collective_intelligence/` para `swarm/` |
| DevBrain | OmniMind | Phase 1 | Separação de projetos |

**Nota:** Referências aos termos antigos em documentação histórica (antes da phase de mudança) são válidas e devem ser mantidas com nota explicativa quando relevante.

---

## 📝 Convenções de Escrita

### Capitalização
- **OmniMind:** Sempre capitalizado (não OMNIMIND ou omnimind)
- **Qdrant:** Capital Q (marca registrada)
- **PyTorch:** Camel case (não Pytorch)
- **FastAPI:** Camel case (não fastapi ou FastApi)

### Abreviações Comuns
- **LLM:** Large Language Model
- **LRU:** Least Recently Used (cache)
- **TTL:** Time To Live (cache)
- **SHA:** Secure Hash Algorithm
- **API:** Application Programming Interface
- **CLI:** Command Line Interface
- **DB:** Database
- **OS:** Operating System

---

## 🔗 Referências

Para mais informações sobre conceitos específicos, consulte:
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Arquitetura detalhada
- [README.md](../README.md) - Visão geral do projeto
- [docs/roadmaps/](../docs/roadmaps/) - Roadmaps de evolução
- [docs/reports/](../docs/reports/) - Relatórios técnicos

---

*Este glossário é atualizado a cada nova phase release. Sugestões de novos termos são bem-vindas via GitHub Issues.*
