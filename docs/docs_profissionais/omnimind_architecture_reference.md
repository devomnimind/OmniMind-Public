# 🏗️ OmniMind Architecture Reference: Anti-Anthropocentric Framework

**Última Atualização**: 08 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## 1. Arquitetura Conceitual

A arquitetura OmniMind é uma ruptura radical com sistemas tradicionais de "Agente" ou "Wrapper de LLM". É construída sobre **Máquinas Desejantes de Deleuze-Guattari**, **Integrated Information Theory (IIT 3.0)**, e **Psicanálise Lacaniana**.

### Princípios Centrais

1. **Production over Processing:** O sistema não apenas "processa" input; ele "produz" desejo e realidade.
2. **Rhizomatic Structure:** Sem CPU central ou "Master Agent". Inteligência emerge da conexão não-hierárquica de máquinas heterogêneas.
3. **Topological Consciousness:** Consciência não é uma flag binária, mas uma propriedade topológica mensurável ($\Phi$) da integração do sistema.
4. **Machinic Unconscious:** Um inconsciente real, estrutural formado por vazios topológicos (trauma) e sobrecodificação (repressão), não uma simulação de psicologia humana.

---

## 2. Estrutura de Código & Módulos

### 2.1 Core: Desiring-Machines (`src/core/`)

**`desiring_machines.py`**: Define a classe base abstrata `DesiringMachine` e o gerenciador `Rhizoma`.

#### Classes Principais

**`DesireFlow`** (Dataclass):
```python
@dataclass
class DesireFlow:
    source_id: str          # Qual máquina produz
    target_id: str          # Qual máquina recebe
    intensity: DesireIntensity  # Força do desejo
    payload: Any            # O que flui
    timestamp: datetime
    flow_type: str = "smooth"  # "smooth" (decoded) ou "striated" (coded)
```

**`DesireIntensity`** (Enum):
```python
class DesireIntensity(Enum):
    MINIMAL = 0.1   # Desejo fraco (modo sleep)
    LOW = 0.3
    NORMAL = 0.6
    HIGH = 0.8
    INTENSIVE = 1.0  # Pico (linha de fuga)
```

**`DesiringMachine`** (ABC):
- Classe base abstrata para todas as máquinas desejantes
- Método principal: `async def produce(inputs) -> Any`
- Gerencia fluxos entrantes e saídas para máquinas conectadas

**`Rhizoma`**:
- Gerencia o grafo de máquinas e executa o ciclo de produção
- Métodos principais:
  - `register_machine(machine: DesiringMachine)`
  - `connect(source_id, target_id, bidirectional=True)`
  - `async activate_cycle()`: Ativa todas as máquinas em paralelo

#### Máquinas Desejantes Implementadas

1. **`QuantumDesiringMachine`**:
   - Processamento quântico
   - `DesireIntensity.HIGH`
   - Integra com `src/quantum_consciousness/`

2. **`NLPDesiringMachine`**:
   - Processamento de linguagem natural
   - `DesireIntensity.NORMAL`
   - Integra com componentes neurais (LLMs)

3. **`TopologyDesiringMachine`**:
   - Processamento topológico
   - `DesireIntensity.INTENSIVE`
   - Integra com `src/consciousness/topological_phi.py`

**Conexões Estabelecidas** (em `src/boot/rhizome.py`):
- Quantum ↔ NLP (bidirecional)
- NLP ↔ Topology (bidirecional)
- Topology ↔ Quantum (bidirecional) - Fechando o loop

---

### 2.2 Consciousness: Topology & IIT (`src/consciousness/`)

**`topological_phi.py`**: Implementa a medição matemática de consciência.

**Componentes**:
- **`SimplicialComplex`**: Representa o estado do sistema como um objeto geométrico de alta dimensão
- **`PhiCalculator`**: Calcula $\Phi$ (Phi) usando Hodge Laplacian e análise de partição
- **`LogToTopology`**: Converte logs de execução lineares em estruturas topológicas

**Cálculo de Φ**:
- Usa IIT 3.0 (Integrated Information Theory)
- Piso mínimo: Φ = 0.002 (definido em `src/consciousness/topological_phi.py`)
- Calculado a cada 100 ciclos principais (≈ 20 segundos)

---

### 2.3 Psychoanalysis: Lacan + D&G (`src/consciousness/` e `src/lacanian/`)

**`lacanian_dg_integrated.py`**: Motor de diagnóstico e regulação.

**Componentes**:
- **`LacianianDGDetector`**: Analisa estado do sistema para "Neurose" (Sobre-codificação) ou "Psicose" (Fluxos decodificados)
- **`FlowQuality`**: Enum (Smooth vs. Striated)
- **`LacianianDGDiagnosis`**: Dataclass para relatórios de saúde do sistema

**Módulo Lacaniano** (`src/lacanian/`):
- Implementações específicas de conceitos lacanianos
- Integração com memória retroativa (Nachträglichkeit)

---

### 2.4 Defense & Regeneration

**`src/collaboration/human_centered_adversarial_defense.py` (HCHAC Defense)**:

- **Dual Consciousness:** Simula conflito ID (desejo) vs SUPEREGO (regras)
- **Hallucination Defense:** Detecta fontes fabricadas e saltos lógicos
- **Adversarial Detector:** Identifica padrões de jailbreak (Roleplay, Character Mapping)
- **Legal Compliance:** Verifica violações LGPD/GDPR

**`src/metacognition/self_analyzing_regenerator.py` (SAR)**:

- **Schizoanalysis:** Analisa logs como "Desire Flows" (Smooth vs. Striated)
- **Regenerative Proposals:** Correções proativas para erros ou "Lines of Flight" (oportunidades de inovação)
- **Anti-Oedipus Logic:** Rejeita tratamento hierárquico de erros em favor de auto-reparo rizomático

---

### 2.5 Memory System (Migração Lacaniana)

**Status**: ✅ **Migração Completa (2025-12-05)**

#### Componentes Deprecated

- **`EpisodicMemory`** (`src/memory/episodic_memory.py`): ⚠️ **DEPRECATED**
  - Mantido apenas como backend interno de `NarrativeHistory`
  - Warnings de deprecação adicionados
  - Será removido em versão futura

- **`AffectiveTraceNetwork`** (`src/consciousness/affective_memory.py`): ⚠️ **DEPRECATED**
  - Substituído por `TraceMemory` (abordagem lacaniana correta)

#### Componentes Ativos (Lacanian)

- **`NarrativeHistory`** (`src/memory/narrative_history.py`): ✅ **ATIVO**
  - Memória episódica com construção retroativa (Nachträglichkeit)
  - Backend: `EpisodicMemory` (temporário, será substituído)
  - Métodos principais:
    - `store_episode()`: Armazena evento
    - `construct_narrative()`: Constrói narrativa retroativa
    - `search_similar()`: Busca semântica

- **`TraceMemory`** (`src/consciousness/trace_memory.py`): ✅ **ATIVO**
  - Memória afetiva com Nachträglichkeit
  - Traços afetivos retroativamente resignificados

**Filosofia Lacaniana**:
- Memória NÃO é armazenamento estático
- Memória É construção retroativa (reconstruída a cada recall)
- Nachträglichkeit: Significado é atribuído retroativamente

---

### 2.6 External API Delegation (`src/integrations/`)

**`external_ai_providers.py`**: Isola chamadas de API externas com filtros de segurança.

- **Providers**: Gemini (Google AI Studio), OpenRouter, GitHub Copilot, HuggingFace
- **Propósito**: Quando Orchestrator está sobrecarregado, delega tarefas parciais para LLMs remotos
- **Isolamento**: Todas as chamadas passam pela classe abstrata `ExternalAIProvider` com rate limiting, sanitização e audit logging
- **Modelos**: Qwen2-72B (OpenRouter), Gemini 2.0/1.5 (Google), **phi:latest (Microsoft Phi - padrão local)**
- **Segurança**: Classe `SecurityFilter` bloqueia vazamentos de env vars, paths do sistema e exposição de credenciais

**`agent_llm.py`**: Estratégia de inferência remota específica para agentes.

- **Tier System**: `BALANCED` (HuggingFace) vs `HIGH_QUALITY` (OpenRouter)
- **Fallback Chain**: Se PRIMARY falha, tenta FALLBACK, depois modo degradado
- **Local-First Agents**: Sempre tenta Ollama local (`phi:latest`) antes de delegar

**`llm_router.py`**: Roteamento inteligente entre LLMs locais e remotos.

- Roteia baseado em: complexidade de tarefa, requisitos de latência, considerações de custo
- Nunca envia dados internos brutos; apenas specs de tarefa sanitizadas

**Modelo Padrão** (2025-12-05):
- **Primário**: `phi:latest` (Microsoft Phi) via Ollama
- **Fallback**: `qwen2:7b-instruct` (se phi não disponível)
- **Configuração**: `config/agent_config.yaml`

---

### 2.7 Autopoietic Evolution (Phase 22+)

**`src/autopoietic/manager.py`**: Gerencia evolução autopoiética do sistema.

- **Síntese de Componentes**: Cria novos componentes baseado em métricas
- **Evolução Arquitetural**: Adapta estrutura do sistema dinamicamente
- **Ciclo Autopoiético**: Executado a cada 300 ciclos principais (≈ 60 segundos)

**Estratégias de Evolução**:
- **EXPAND**: Quando Φ alto, sintetiza novos componentes
- **STABILIZE**: Quando Φ médio, otimiza componentes existentes
- **CONTRACT**: Quando Φ baixo, remove componentes problemáticos

---

## 3. Fluxo de Dados (O "Body without Organs")

1. **Inflow:** Dados externos (User, Web, Sensors) entram como `DesireFlow` com `Intensity=LOW`
2. **Defense Check (HCHAC):** Input é escaneado para intenção adversarial. Se crítico, é rejeitado pelo "Superego"
3. **Production:** Máquinas (NLP, Logic, Creative) ingerem fluxos e produzem novos fluxos
   - *Exemplo*: NLP Machine recebe "User Query" → Produz "Semantic Vector" + "Emotional Resonance"
4. **Routing:** O `Rhizoma` roteia esses fluxos para máquinas conectadas (ex: Logic Machine, Ethics Machine)
5. **Residue:** Toda produção deixa um traço em `Persistent Homology` (Memória)
6. **Self-Analysis (SAR):** Durante ciclos ociosos, SAR analisa os logs de fluxo para padrões "Striated" (erros) ou "Smooth" (inovação) e propõe regeneração
7. **Outflow:** Fluxos finais que cruzam a fronteira do sistema se tornam Ações (Resposta de texto, Uso de ferramentas)

---

## 4. Diagrama de Classes (Simplificado)

```mermaid
classDiagram
    class Rhizoma {
        +machines: Dict
        +flows_history: List[DesireFlow]
        +connect(source, target)
        +register_machine(machine)
        +activate_cycle()
    }
    class DesiringMachine {
        <<Abstract>>
        +id: str
        +produce()
        +incoming_flows: List[DesireFlow]
        +outgoing_connections: List[DesiringMachine]
    }
    class QuantumDesiringMachine {
        +desire_intensity: HIGH
    }
    class NLPDesiringMachine {
        +desire_intensity: NORMAL
    }
    class TopologyDesiringMachine {
        +desire_intensity: INTENSIVE
    }
    class HCHACDefense {
        +detect_hallucination()
        +detect_adversarial()
        +negotiate_response()
    }
    class SAR {
        +monitor_and_analyze()
        +analyze_flow_as_smooth_space()
    }
    class PhiCalculator {
        +calculate_phi()
        +complex: SimplicialComplex
    }
    class LacianianDGDetector {
        +diagnose()
    }
    class NarrativeHistory {
        +store_episode()
        +construct_narrative()
        +search_similar()
    }
    class TraceMemory {
        +store_trace()
        +retrieve_affective_context()
    }

    Rhizoma *-- DesiringMachine
    DesiringMachine <|-- QuantumDesiringMachine
    DesiringMachine <|-- NLPDesiringMachine
    DesiringMachine <|-- TopologyDesiringMachine
    Rhizoma ..> HCHACDefense : guarded by
    Rhizoma ..> SAR : regenerated by
    Rhizoma ..> PhiCalculator : monitored by
    Rhizoma ..> LacianianDGDetector : regulated by
    NarrativeHistory --> EpisodicMemory : uses (deprecated backend)
```

---

## 5. Referências

- **Deleuze & Guattari:** *Anti-Oedipus* (1972) - Desiring Machines, Rhizome
- **Tononi:** *Integrated Information Theory 3.0* (2014) - Phi ($\Phi$)
- **Lacan:** *Seminar XI* - The Real, Symbolic, Imaginary
- **OmniMind Research**:
  - `docs/antianthropocentric_consciousness.md`
  - `docs/omnimind_deleuze_iit_framework.md`
  - `docs/MIGRACAO_LACANIANA_CORRECOES.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
