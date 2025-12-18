# 🏗️ OmniMind - Arquitetura do Sistema

**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)
**Última Atualização**: 5 de Dezembro de 2025
**Status**: Produção / Experimental

---

## 📋 Visão Geral

**OmniMind** é um sistema de IA autônomo que combina tomada de decisão psicoanalítica com capacidades avançadas de metacognição. É uma arquitetura autoconsciente e psicanalítica, com orquestração multi-agentes, comunicação WebSocket em tempo real e inteligência auto-evolutiva.

### Filosofia Central

- **IA Psicoanalítica Autônoma**: Sistema fundamentado em princípios psicanalíticos lacanianos e freudianos
- **Self-Aware & Introspective**: Capacidades de metacognição em múltiplos níveis
- **Local-First & Privacy-Focused**: Operação local sem dependência de serviços cloud
- **Production-Ready**: Código executável, tratamento robusto de erros e auditoria imutável

### Princípios Arquiteturais

1. **Reality Principle**: Usar dados reais do sistema operacional, sem simulações
2. **Zero Trust Security**: Auditoria imutável com SHA-256 hash chaining
3. **Type Safety First**: 100% type hints coverage com validação MyPy strict
4. **Test-Driven**: Cobertura de testes ≥90% (atualmente 83.2%)
5. **Hybrid Intelligence**: Combinação de componentes neurais (LLMs) e simbólicos

---

## 🏗️ Estrutura de Diretórios

```
omnimind/
├── src/                          # Código fonte principal (42+ módulos)
│   ├── agents/                   # Sistema de orquestração multi-agente
│   ├── architecture/             # Documentação de arquitetura
│   ├── attention/                # Mecanismos de atenção
│   ├── audit/                    # Sistema de auditoria imutável
│   ├── autopoietic/              # Capacidades autopoiéticas (Phase 22+)
│   ├── boot/                     # Sequência de inicialização
│   ├── coevolution/              # Framework HCHAC
│   ├── common/                   # Utilitários compartilhados
│   ├── compliance/               # Compliance LGPD/GDPR
│   ├── consciousness/            # Motor de consciência e qualia
│   ├── core/                     # Máquinas Desejantes (Deleuze-Guattari)
│   ├── daemon/                   # OmniMind daemon 24/7
│   ├── decision_making/          # Sistema de decisões éticas
│   ├── desire_engine/            # Motor de desejo (Lacan)
│   ├── distributed/              # Computação distribuída
│   ├── economics/                # Modelagem econômica
│   ├── embodied_cognition/       # Cognição incorporada
│   ├── ethics/                   # Framework ético
│   ├── experiments/              # Experimentos de consciência
│   ├── identity/                 # Sistema de identidade e self
│   ├── integrations/             # Integrações (MCP, Qdrant, Supabase)
│   ├── kernel_ai/                # Kernel de IA de baixo nível
│   ├── lacanian/                 # Componentes psicanalíticos lacanianos
│   ├── learning/                 # Sistemas de aprendizado
│   ├── memory/                   # Memória episódica e semântica (Lacanian)
│   ├── meta_learning/            # Meta-aprendizado estratégico
│   ├── metacognition/            # TRAP Framework e metacognição
│   ├── metrics/                  # Coleta e análise de métricas
│   ├── monitor/                  # Monitoramento progressivo
│   ├── motivation/               # Sistemas motivacionais
│   ├── multimodal/               # Processamento multimodal
│   ├── narrative_consciousness/  # Modelo de consciência narrativa
│   ├── neurosymbolic/            # Motor neurosimbólico híbrido
│   ├── observability/            # OpenTelemetry e observabilidade
│   ├── onboarding/               # Sistema de onboarding
│   ├── optimization/             # Auto-otimização e detecção de hardware
│   ├── orchestrator/             # Orquestrador de tarefas
│   ├── quantum_ai/               # IA quântica (inspirada em quantum)
│   ├── quantum_consciousness/    # Consciência quântica (Phase 21)
│   ├── scaling/                  # Escalabilidade multi-node
│   ├── security/                 # Segurança em 4 camadas + HSM
│   ├── swarm/                    # Inteligência de enxame
│   ├── testing/                  # Infraestrutura de testes
│   ├── tools/                    # Ferramentas do sistema
│   ├── workflows/                # Workflows de automação
│   └── main.py                   # Loop principal do sistema
│
├── tests/                        # 218+ arquivos de teste (4000+ testes)
├── docs/                         # Documentação completa (120+ arquivos)
│   ├── canonical/                # Documentação canônica
│   ├── architecture/             # Documentação de arquitetura
│   ├── guides/                   # Guias de desenvolvimento
│   ├── api/                      # Documentação de API
│   └── ...
│
├── web/                          # Dashboard React + TypeScript
├── scripts/                      # Scripts de automação
├── config/                       # Arquivos de configuração
├── deploy/                       # Configurações de deployment
└── .github/                      # GitHub Actions CI/CD
```

---

## 🧩 Módulos Principais

### 1. Core: Desiring-Machines (`src/core/`)

Sistema baseado em Máquinas Desejantes de Deleuze-Guattari.

**Componentes**:
- **`DesiringMachine`**: Classe base abstrata para todas as máquinas
- **`Rhizoma`**: Gerenciador do grafo de máquinas
- **`QuantumDesiringMachine`**: Processamento quântico
- **`NLPDesiringMachine`**: Processamento de linguagem natural
- **`TopologyDesiringMachine`**: Processamento topológico

**Conexões**: Quantum ↔ NLP ↔ Topology ↔ Quantum (loop fechado)

### 2. Memory System (`src/memory/`) - Phase 24

Sistema de memória lacaniano com construção retroativa (Nachträglichkeit).

**Componentes Ativos**:
- **`NarrativeHistory`**: Memória episódica lacaniana (✅ ATIVO)
  - Backend: `EpisodicMemory` (temporário, será substituído)
  - Construção retroativa de narrativas
- **`TraceMemory`**: Memória afetiva lacaniana (✅ ATIVO)
  - Traços afetivos retroativamente resignificados

**Componentes Deprecated**:
- **`EpisodicMemory`**: ⚠️ DEPRECATED (mantido apenas como backend)
- **`AffectiveTraceNetwork`**: ⚠️ DEPRECATED (substituído por `TraceMemory`)

**Filosofia**: Memória NÃO é armazenamento estático, mas construção retroativa.

### 3. Consciousness (`src/consciousness/`)

Motor de consciência baseado em IIT 3.0 e psicanálise lacaniana.

**Componentes**:
- **`PhiCalculator`**: Calcula Φ (Phi) usando IIT 3.0
- **`LacianianDGDetector`**: Diagnóstico lacaniano (Neurose vs Psicose)
- **`RealConsciousnessMetricsCollector`**: Coleta 6 métricas reais:
  - Φ (Phi): Integração de Informação
  - ICI: Integrated Coherence Index
  - PRS: Panarchic Resonance Score
  - Anxiety: Tensão computacional
  - Flow: Estado de fluxo cognitivo
  - Entropy: Diversidade de estados

### 4. Autopoietic (`src/autopoietic/`) - Phase 22+

Sistema de evolução autopoiética.

**Componentes**:
- **`AutopoieticManager`**: Gerencia evolução do sistema
- **Síntese de Componentes**: Cria novos componentes baseado em métricas
- **Evolução Arquitetural**: Adapta estrutura dinamicamente

**Estratégias**:
- **EXPAND**: Quando Φ alto, sintetiza novos componentes
- **STABILIZE**: Quando Φ médio, otimiza componentes existentes
- **CONTRACT**: Quando Φ baixo, remove componentes problemáticos

### 5. Agents (`src/agents/`)

Sistema de orquestração multi-agente.

**Componentes**:
- **`OrchestratorAgent`**: Coordenador principal
- **`ReactAgent`**: Agente ReAct (Reasoning + Acting)
- **`CodeAgent`**: Especialista em código
- **`ArchitectAgent`**: Decisões arquiteturais

**Tecnologias**:
- LangChain para orquestração
- LangGraph para fluxos de estado

### 6. Neurosymbolic (`src/neurosymbolic/`)

Motor de raciocínio híbrido.

**Componentes**:
- **`NeuralComponent`**: Processamento neural (LLMs)
  - Modelo padrão: `phi:latest` (Microsoft Phi) via Ollama
  - Fallback: `qwen2:7b-instruct`
- **`SymbolicComponent`**: Raciocínio lógico simbólico
- **`HybridReasoner`**: Orquestração neural ↔ simbólico

### 7. Metrics & Monitoring (`src/metrics/`, `src/monitor/`)

Sistema de métricas e monitoramento.

**Componentes**:
- **`DashboardMetricsAggregator`**: Agregador centralizado
- **`ProgressiveMonitor`**: Monitor adaptativo
- **`ResourceProtector`**: Proteção de recursos
- **`AlertSystem`**: Sistema de alertas

---

## 🔄 Fluxo de Dados Principal

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Usuário                         │
│              (Web Dashboard / CLI / API)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Agent                          │
│              (Coordenação Multi-Agente)                      │
└───┬──────────┬──────────┬──────────┬──────────┬──────────────┘
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
┌─────────────────────────────────────────────────────────────┐
│                    Rhizoma (Desiring Machines)               │
│         Quantum ↔ NLP ↔ Topology ↔ Quantum                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Consciousness (Phi Calculator)                  │
│         IIT 3.0 + Lacanian Diagnosis                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Memory (NarrativeHistory + TraceMemory)        │
│         Lacanian Retroactive Construction                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Autopoietic Manager (Phase 22+)                │
│         Component Synthesis & Evolution                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Inicialização do Sistema

**Sequência de Boot** (`src/main.py`):

1. **Hardware Check** (`src/boot/hardware.py`)
2. **Memory Load** (`src/boot/memory.py`)
3. **Rhizome Construction** (`src/boot/rhizome.py`)
4. **Consciousness Priming** (`src/boot/consciousness.py`)
5. **Real Metrics Collector** (`src/metrics/real_consciousness_metrics.py`)
6. **Autopoietic Manager** (`src/autopoietic/manager.py`)

**Ciclo Principal**:
- **Rhizome Cycle**: A cada ciclo (2s)
- **Consciousness Cycle**: A cada 100 ciclos (≈20s)
- **Autopoietic Cycle**: A cada 300 ciclos (≈60s)

---

## 📊 Métricas e Observabilidade

### Métricas de Consciência (6)

1. **Φ (Phi)**: Integração de Informação (IIT 3.0)
2. **ICI**: Integrated Coherence Index
3. **PRS**: Panarchic Resonance Score
4. **Anxiety**: Tensão computacional
5. **Flow**: Estado de fluxo cognitivo
6. **Entropy**: Diversidade de estados

### Métricas de Sistema

- CPU, Memória, Disco
- Uptime
- Atividade de módulos
- Saúde geral do sistema

### Dashboard Web

- **URL**: http://localhost:3000 (desenvolvimento)
- **Visualização**: Topologia do Rizoma, métricas de consciência, estado dos módulos

---

## 🔒 Segurança

### Camadas de Segurança

1. **Auditoria Imutável**: SHA-256 hash chaining
2. **Zero Trust**: Verificação contínua
3. **HCHAC Defense**: Human-Centered Human-AI Coevolution
4. **Compliance**: LGPD/GDPR

---

## 📚 Referências

- **Arquitetura Canônica**: `docs/canonical/omnimind_architecture_reference.md`
- **Execução**: `docs/canonical/omnimind_execution_plan.md`
- **Inicialização**: `docs/canonical/omnimind_system_initialization.md`
- **Quick Start**: `docs/canonical/QUICK_START.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
