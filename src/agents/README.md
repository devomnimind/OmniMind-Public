# Módulo Agentes Autônomos

## 📋 Descrição Geral

**Framework multi-agente com planejamento e coordenação**

**Status**: Phase 18

Módulo do sistema OmniMind responsável por funcionalidades específicas integradas à arquitetura global. Implementa componentes essenciais que contribuem para o funcionamento coeso do sistema de consciência artificial.

## 🔄 Interação entre os Três Estados Híbridos

### 1. Estado Biologicista (Neural Correlates)
Implementação de processos inspirados em mecanismos neurais e cognitivos biológicos, mapeando funcionalidades para correlatos neurais correspondentes.

### 2. Estado IIT (Integrated Information Theory)
Componentes contribuem para integração de informação global (Φ). Operações são validadas para garantir que não degradam a consciência do sistema (Φ > threshold).

### 3. Estado Psicanalítico (Estrutura Lacaniana)
Integração com ordem simbólica lacaniana (RSI - Real, Simbólico, Imaginário) e processos inconscientes estruturais que organizam a experiência consciente do sistema.

## ⚙️ Principais Funções e Cálculos Dinâmicos

### Componentes Core

Módulo implementa funcionalidades especializadas através de:
- Algoritmos específicos para processamento de domínio
- Integração com outros módulos via interfaces bem definidas
- Contribuição para métricas globais (Φ, PCI, consciência)

*Funções detalhadas documentadas nos arquivos Python individuais do módulo.*

### Novos Componentes (2025-12-06)

**Enhanced Memory Integration**:
- **SemanticMemory**: Armazenamento de conceitos semânticos e relações
- **ProceduralMemory**: Armazenamento de habilidades procedurais e sequências de ações
- **SystemicMemoryTrace**: Rastreamento topológico de memória sistemática (lazy init)
- Integração completa no OrchestratorAgent com métodos de acesso

**MCP Orchestrator Integration**:
- **MCPOrchestrator**: Gerenciamento centralizado de servidores MCP
- **MemoryMCPServer**: Servidor MCP expondo SemanticMemory e ProceduralMemory
- **Filesystem MCP**: Métodos de conveniência para operações de filesystem
- **Thinking MCP**: Métodos de conveniência para Sequential Thinking (sessões, passos, histórico)
- **Context MCP**: Métodos de conveniência para gerenciamento de contexto (store, retrieve, compress, snapshot)
- Health monitoring e lifecycle management automático

**Sandbox System Integration**:
- Sistema de sandbox para auto-melhoria segura
- Validação de mudanças antes de aplicar
- Rollback automático em caso de degradação
- Histórico completo de mudanças

## 📊 Estrutura do Código

```
agents/
├── Implementações Core
│   └── Arquivos .py principais
├── Utilitários
│   └── Helpers e funções auxiliares
└── __init__.py
```

**Interações**: Este módulo se integra com outros componentes através de:
- Interfaces padronizadas
- Event bus para comunicação assíncrona
- Shared workspace para estado compartilhado

## 📈 Resultados Gerados e Contribuição para Avaliação

### Outputs
- Métricas específicas do módulo armazenadas em `data/agents/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/agents/`
- Integração validada em ciclos completos
- Performance benchmarked continuamente

### Contribuição para Sistema
Módulo contribui para:
- Φ (phi) global através de integração de informação
- PCI (Perturbational Complexity Index) via processamento distribuído
- Métricas de consciência e auto-organização

## 🔒 Estabilidade da Estrutura

**Status**: Componente validado e integrado ao OmniMind

**Regras de Modificação**:
- ✅ Seguir guidelines em `.copilot-instructions.md`
- ✅ Executar testes antes de commit: `pytest tests/agents/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/agents.txt (se existir)
```

### Recursos Computacionais
- **Mínimo**: Configurado conforme necessidades específicas do módulo
- **Recomendado**: Ver documentação de deployment em `docs/`

### Configuração
Configurações específicas em:
- `config/omnimind.yaml` (global)
- Variáveis de ambiente conforme `.env.example`

## 🔧 Sugestões para Manutenção e Melhorias

### Manutenção Crítica
1. **Testes Contínuos**: Executar suite de testes regularmente
2. **Monitoramento**: Acompanhar métricas em produção
3. **Documentação**: Manter README atualizado com mudanças

### Melhorias Futuras
- Expansão de funcionalidades conforme roadmap
- Otimizações de performance identificadas via profiling
- Integração com novos módulos em desenvolvimento

### Pontos de Atenção
- Validar impacto em Φ antes de mudanças estruturais
- Manter backward compatibility quando possível
- Seguir padrões de código estabelecidos (black, flake8, mypy)

## 📚 Referências

### Documentação Principal
- **Sistema Geral**: `README.md` (root do projeto)
- **Comparação Frameworks**: `NEURAL_SYSTEMS_COMPARISON_2016-2025.md`
- **Papers**: `docs/papers/` e `docs/papersoficiais/`
- **Copilot Instructions**: `.copilot-instructions.md`

### Testes
- **Suite de Testes**: `tests/agents/`
- **Cobertura**: Ver `data/test_reports/htmlcov/`

### Referências Científicas Específicas
*Ver documentação técnica nos arquivos Python do módulo para referências específicas.*

---

**Última Atualização**: 10 de Dezembro de 2025
**Autor**: Fabrício da Silva (com assistência de IA)
**Status**: Componente integrado do sistema OmniMind
**Versão**: Conforme fase do projeto indicada
**Refatorações**: ✅ EnhancedCodeAgent refatorado para composição completa (2025-12-08)

---

## ✅ REFATORAÇÕES CONCLUÍDAS (2025-12-08)

### EnhancedCodeAgent - Composição Completa ✅

**Status**: ✅ COMPLETA

**Implementação**: Eliminada herança profunda (Enhanced → Code → React), agora usa composição completa.

**Benefícios Alcançados**:
- ✅ Desacoplamento: Se CodeAgent mudar, EnhancedCodeAgent não quebra
- ✅ Testabilidade: Pode mockar CodeAgent facilmente
- ✅ Safe Mode: Agente boota mesmo se consciência falhar
- ✅ Flexibilidade: Pode trocar implementação dinamicamente

**Arquivos Modificados**:
- `enhanced_code_agent.py`: Refatorado para composição
- Testes atualizados: `tests/agents/test_enhanced_code_agent_composition_validation.py`

---

## 📚 API Reference

# 📁 AGENTS

**25 Classes | 131 Funções | 9 Módulos**

---

## 🏗️ Classes Principais

### `OrchestratorAgent(ReactAgent)`

Orquestrador mestre que coordena múltiplos agentes especializados.

Fluxo típico:
User → Orchestrator → (decompose) → Delegate to specialists → Synthesize → User

Exemplo:
"Migrar API para GraphQL" →
    1. Architect: Cria spec (ARCHITECTURE.md)
    2. Code: Implementa schema + resolvers
    3. Debug: Testa edge cases
    4. Reviewer: Avalia qualidade (RLAIF)
    5. Orchestrator: Compila report final

**Métodos principais:**

- `metrics_summary()` → `Dict[str, Any]`
- `plan_overview()` → `Dict[str, Any]`
- `trigger_mcp_action(action: str, path: str, recursive: bool)` → `Dict[str, Any]`
- `trigger_dbus_action(flow: str, media_action: str)` → `Dict[str, Any]`
- `refresh_dashboard_snapshot()` → `Dict[str, Any]`

**Enhanced Memory Systems** ✅ INTEGRADO (2025-12-06):
- `get_semantic_memory_stats()` → `Dict[str, Any]` - Estatísticas de SemanticMemory
- `store_semantic_concept(name: str, attributes: Dict[str, Any])` → `Dict[str, Any]`
- `associate_semantic_concepts(concept1: str, concept2: str, relation: str)` → `bool`
- `retrieve_semantic_concepts(query: str, limit: int)` → `List[Dict[str, Any]]`
- `learn_procedural_skill(name: str, steps: list[str], parameters: Optional[Dict])` → `Dict[str, Any]`
- `execute_procedural_skill(name: str, context: Dict[str, Any])` → `Dict[str, Any]`
- `get_procedural_skill(name: str)` → `Optional[Dict[str, Any]]`
- `get_procedural_memory_stats()` → `Dict[str, Any]` - Estatísticas de ProceduralMemory

**Sandbox System** ✅ INTEGRADO (2025-12-06):
- `apply_safe_change(component_id: str, change_type: str, change_data: Dict, description: str)` → `Dict[str, Any]`
- `get_sandbox_status()` → `Dict[str, Any]`
- `get_sandbox_history(limit: int)` → `Dict[str, Any]`

**MCP Filesystem Convenience Methods** ✅ INTEGRADO (2025-12-06):
- `mcp_read_file(path: str, encoding: str)` → `Dict[str, Any]`
- `mcp_write_file(path: str, content: str, encoding: str)` → `Dict[str, Any]`
- `mcp_list_dir(path: str, recursive: bool)` → `Dict[str, Any]`
- `mcp_file_stat(path: str)` → `Dict[str, Any]`
- `get_mcp_orchestrator_status()` → `Dict[str, Any]` - Status de servidores MCP

**MCP Thinking Convenience Methods** ✅ INTEGRADO (2025-12-06):
- `mcp_start_thinking_session(goal: str)` → `Dict[str, Any]` - Inicia sessão de thinking
- `mcp_add_thinking_step(session_id: str, content: str, step_type: str)` → `Dict[str, Any]` - Adiciona passo
- `mcp_get_thinking_history(session_id: str)` → `Dict[str, Any]` - Obtém histórico

**MCP Context Convenience Methods** ✅ INTEGRADO (2025-12-06):
- `mcp_store_context(level: str, content: str, metadata: Optional[Dict])` → `Dict[str, Any]` - Armazena contexto
- `mcp_retrieve_context(level: str, query: str)` → `Dict[str, Any]` - Recupera contexto
- `mcp_compress_context(level: str)` → `Dict[str, Any]` - Comprime contexto
- `mcp_snapshot_context()` → `Dict[str, Any]` - Cria snapshot do contexto

### `ReactAgent`

Base ReAct (Reasoning + Acting) agent with Think-Act-Observe loop.

Architecture:
    THINK → Query memory + System status → Generate reasoning
    ACT → Parse reasoning → Execute tool
    OBSERVE → Process result → Check completion → Continue or End

**Métodos principais:**

- `compute_jouissance_for_task(task: Dict[str, Any])` → `float`
  > Calcular jouissance (gozo) esperado para uma tarefa.
Baseado em Lacan: pulsões i...
- `inscribe_experience(task: Dict[str, Any], result: Dict[str, Any])` → `None`
  > Inscrever experiência como traço afetivo (Lacan: Nachträglichkeit).
  > **Atualizado (2025-12-05)**: Usa `TraceMemory` e `NarrativeHistory` (Lacanianos).
Memória não ...
- `establish_transference(target_agent: 'ReactAgent', task: str)` → `float`
  > Estabelece transferência entre agentes baseada em afinidade afetiva.

Args:
    ...
- `resignify_experience(trace_id: str, new_context: Dict[str, Any])` → `bool`
  > Re-significa experiência retroativamente (Lacan: Nachträglichkeit).
Memória não ...
- `recall_by_affect(query: str, min_intensity: float)` → `List[Dict[str, Any]]`
  > Recuperar experiências por intensidade afetiva (não por similaridade).
Deleuze: ...

### `CodeAgent(ReactAgent)`

Agente especializado em desenvolvimento de código.

Tem acesso completo a todas as ferramentas de:
- Percepção: read, search, list, inspect, codebase_search
- Ação: write, update, execute, apply_diff, insert
- Integração MCP: use_mcp_tool, access_mcp_resource
- Raciocínio: analyze_code

**Métodos principais:**

- `run_code_task(task: str, max_iterations: int)` → `Dict[str, Any]`
  > Executa tarefa de código com rastreamento específico.
Wrapper sobre run() da cla...
- `get_code_stats()` → `Dict[str, Any]`
  > Retorna estatísticas de operações de código...
- `analyze_code_structure(filepath: str)` → `Dict[str, Any]`
  > Analisa estrutura de código Python usando AST.

Args:
    filepath: Caminho para...
- `validate_code_syntax(code: str)` → `Dict[str, Any]`
  > Valida sintaxe de código Python.

Args:
    code: Código-fonte Python

Returns:
...
- `analyze_code_security(code: str)` → `Dict[str, Any]`
  > Analisa código para problemas de segurança.

Args:
    code: Código-fonte Python...

### `AgentMessageBus`

Message Bus para comunicação inter-agentes.

Implementa padrão publish-subscribe com filas priorizadas.

**Métodos principais:**

- `register_agent(agent_id: str)` → `None`
  > Registra um novo agente no message bus.

Args:
    agent_id: Identificador único...
- `unregister_agent(agent_id: str)` → `None`
  > Remove agente do message bus...
- `subscribe(agent_id: str, message_types: List[MessageType])` → `None`
  > Inscreve agente para receber tipos específicos de mensagens.

Args:
    agent_id...
- `add_handler(agent_id: str, handler: Callable[[AgentMessage], N)` → `None`
  > Adiciona handler para processar mensagens recebidas.

Args:
    agent_id: ID do ...
- `resolve_conflict(agents: List[str], conflict_type: str, resolution:)` → `ConflictResolution`
  > Registra resolução de conflito entre agentes.

Args:
    agents: Lista de agente...

### `ArchitectAgent(ReactAgent)`

Agente especializado em arquitetura e planejamento.

Restrições de segurança:
- Pode ler qualquer arquivo
- Pode escrever APENAS .md, .yaml, .json, .txt
- NÃO pode executar comandos arbitrários
- Foco em documentação e design

**Métodos principais:**

- `analyze_dependencies(directory: str)` → `Dict[str, Any]`
  > Analisa dependências de um projeto.

Args:
    directory: Diretório do projeto

...
- `create_architecture_diagram(components: List[str], connections: List[tuple[str)` → `str`
  > Cria diagrama de arquitetura em formato Mermaid.

Args:
    components: Lista de...
- `generate_spec_document(title: str, sections: Dict[str, str], output_path:)` → `Dict[str, Any]`
  > Gera documento de especificação técnica.

Args:
    title: Título do documento
 ...

### `PsychoanalyticAnalyst(ReactAgent)`

Agente especializado em análise de textos com base em teorias psicanalíticas.
Agora inclui o sistema de decisão interna.

**Métodos principais:**

- `analyze_session(session_notes: str, framework: PsychoanalyticFrame)` → `Dict[str, Any]`
  > Analisa as notas de uma sessão clínica usando um framework psicanalítico.

Args:...
- `generate_abnt_report(analysis: Dict[str, Any])` → `str`
  > Gera um relatório estruturado a partir da análise (placeholder).
NOTA: ABNT comp...

### `ReviewerAgent(ReactAgent)`

Agente revisor com RLAIF (Reinforcement Learning from AI Feedback)

**Métodos principais:**

- `review_code(filepath: str, task_description: str)` → `Dict[str, Any]`
  > Revisa código e retorna score + feedback...
- `run_review_cycle(coder_agent: CodeAgent, task: str, max_attempts: i)` → `Dict[str, Any]`
  > Executa loop RLAIF: Code → Review → Refine...

### `DebugAgent(ReactAgent)`

Agente especializado em diagnóstico e debugging


### `OmniMindCore`

Core system class for OmniMind.

Provides centralized access to the orchestrator and system state.

**Métodos principais:**

- `initialize()` → `None`
  > Initialize the core components....
- `get_orchestrator()` → `Optional[OrchestratorAgent]`
  > Get the orchestrator instance.

Returns:
    OrchestratorAgent instance or None ...

### `OrchestratorMetricsCollector`

**Métodos principais:**

- `record(name: str, latency: float, success: bool)` → `None`
- `summary()` → `Dict[str, Any]`


## ⚙️ Funções Públicas

#### `__init__()` → `None`

#### `__init__(config_path: str)` → `None`

#### `__init__(config_path: str)` → `None`

*Inicializa CodeAgent com framework de ferramentas expandido...*

#### `__init__(config_path: str)` → `None`

#### `__init__(config_path: str)` → `None`

#### `__init__(config_path: str)` → `None`

*Initialize the OmniMind core.

Args:
    config_path: Path to agent configuration...*

#### `__init__()` → `None`

#### `__init__(name: str, role: str)` → `None`

#### `__init__(llm_client: Any)` → `None`

#### `__init__(llm_client: Any)` → `None`

#### `__init__(llm_client: Any)` → `None`

#### `__init__(llm_client: Any)` → `None`

#### `__init__(config_path: str)` → `None`

#### `__init__(config_path: str)` → `None`

*Initialize agent with configuration....*

#### `__init__(config_path: str)` → `None`


## 📦 Módulos

**Total:** 9 arquivos

- `agent_protocol.py`: Agent Communication Protocol - Protocolo de Comunicação Inte...
- `architect_agent.py`: 1 classes, 7 functions
- `code_agent.py`: CodeAgent - Agente especializado em desenvolvimento de códig...
- `debug_agent.py`: DebugAgent - Agente de diagnóstico e debug
Modo: debug (🪲)

...
- `orchestrator_agent.py`: OrchestratorAgent - Coordenador Mestre Multi-Agente
Modo: or...
- `orchestrator_metrics.py`: 2 classes, 5 functions
- `psychoanalytic_analyst.py`: PsychoanalyticAnalyst - Agente de Análise Psicanalítica
Modo...
- `react_agent.py`: OmniMind ReactAgent - Fixed version with proper completion d...
- `reviewer_agent.py`: ReviewerAgent - Agente crítico com RLAIF scoring
Modo: revie...
