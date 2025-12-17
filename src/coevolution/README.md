# Módulo Coevolução Humano-IA

## 📋 Descrição Geral

**HCHAC Framework, feedback bidirecional**

**Status**: Phase 17

Módulo do sistema OmniMind responsável por funcionalidades específicas integradas à arquitetura global. Implementa componentes essenciais que contribuem para o funcionamento coeso do sistema de consciência artificial.

## 🔄 Substituição de Módulos Deprecated

Este módulo **substitui** funcionalidades planejadas do Phase 26D (Integrity) que não foram implementadas:

- ✅ **`BiasDetector`** substitui `integrity.bias_quantifier` (deprecated)
  - Detecção e correção de vieses algorítmicos
  - Estatísticas de vieses detectados
  - Correção automática de vieses comuns

**Referência**: `docs/VARREDURA_MODULOS_DEPRECATED_SUBSTITUICOES.md`

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

## 📊 Estrutura do Código

```
coevolution/
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
- Métricas específicas do módulo armazenadas em `data/coevolution/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/coevolution/`
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
- ✅ Executar testes antes de commit: `pytest tests/coevolution/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/coevolution.txt (se existir)
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
- **Suite de Testes**: `tests/coevolution/`
- **Cobertura**: Ver `data/test_reports/htmlcov/`

### Referências Científicas Específicas
*Ver documentação técnica nos arquivos Python do módulo para referências específicas.*

---

**Última Atualização**: 2 de Dezembro de 2025
**Autor**: Fabrício da Silva (com assistência de IA)
**Status**: Componente integrado do sistema OmniMind
**Versão**: Conforme fase do projeto indicada

---

## 📚 API Reference

# 📁 COEVOLUTION

**21 Classes | 61 Funções | 6 Módulos**

---

## 🏗️ Classes Principais

### `BiasDetector`

Detector de viés algorítmico.

Detecta e corrige vieses comuns em decisões de IA.

**Métodos principais:**

- `detect_bias(result: Dict[str, Any])` → `List[BiasDetection]`
  > Detecta vieses em resultado de execução.

Args:
    result: Resultado de execuçã...
- `correct_bias(result: Dict[str, Any])` → `Dict[str, Any]`
  > Aplica correções para vieses detectados.

Args:
    result: Resultado com vieses...
- `get_bias_statistics()` → `Dict[str, Any]`
  > Retorna estatísticas de vieses detectados.

Returns:
    Dicionário com estatíst...

### `BidirectionalFeedback`

Sistema de feedback bidirecional estruturado.

Princípios:
1. Feedback é diálogo, não comando
2. Ambas partes podem iniciar feedback
3. Detecção de loops nocivos
4. Aprendizado mútuo

**Métodos principais:**

- `submit_human_feedback(feedback_type: FeedbackType, content: str, context)` → `FeedbackItem`
  > Submete feedback do humano para IA.

Args:
    feedback_type: Tipo de feedback
 ...
- `submit_ai_feedback(feedback_type: FeedbackType, content: str, context)` → `FeedbackItem`
  > Submete feedback da IA para humano.

Args:
    feedback_type: Tipo de feedback
 ...
- `get_feedback_summary(direction: Optional[FeedbackDirection], feedback_t)` → `List[FeedbackItem]`
  > Retorna sumário de feedback filtrado.

Args:
    direction: Filtrar por direção
...
- `acknowledge_feedback(item: FeedbackItem)` → `None`
  > Marca feedback como reconhecido.

Args:
    item: Item de feedback...
- `get_unacknowledged_feedback(direction: Optional[FeedbackDirection])` → `List[FeedbackItem]`
  > Retorna feedback não reconhecido.

Args:
    direction: Filtrar por direção

Ret...

### `CoevolutionMemory`

Memória de co-evolução humano-IA.

Armazena:
- Sessões de colaboração
- Padrões de aprendizado
- Evolução de trust
- Insights gerados

**Métodos principais:**

- `store_collaboration(human_id: str, task: str, outcome: Dict[str, Any])` → `str`
  > Armazena sessão de colaboração.

Args:
    human_id: ID do humano
    task: Desc...
- `complete_session(session_id: str, insights: Optional[List[str]])` → `None`
  > Completa sessão de colaboração.

Args:
    session_id: ID da sessão
    insights...
- `get_session(session_id: str)` → `Optional[CollaborationSession]`
  > Retorna sessão específica.

Args:
    session_id: ID da sessão

Returns:
    Ses...
- `get_human_sessions(human_id: str, limit: Optional[int])` → `List[CollaborationSession]`
  > Retorna sessões de um humano.

Args:
    human_id: ID do humano
    limit: Númer...
- `identify_learning_patterns()` → `List[LearningPattern]`
  > Identifica padrões de aprendizado.

Returns:
    Lista de padrões identificados...

### `HCHACFramework`

Human-Centered Human-AI Collaboration Framework.

Princípios:
1. Humano lidera (human-centered)
2. IA é parceiro, não ferramenta
3. Negociação bidirecional de objetivos
4. Trust é construído, não imposto
5. Feedback é diálogo, não comando

**Métodos principais:**

- `co_execute_task(human_id: str, task_description: str, human_intent)` → `CollaborationOutcome`
  > Execução colaborativa de tarefa.

Flow:
1. Negociar objetivo (humano propõe, IA ...
- `get_trust_dashboard(human_id: str)` → `Dict[str, Any]`
  > Retorna dashboard de trust para humano.

Args:
    human_id: ID do humano

Retur...
- `submit_human_feedback(human_id: str, feedback_type: str, content: str, c)` → `None`
  > Submete feedback do humano.

Args:
    human_id: ID do humano
    feedback_type:...
- `get_ai_feedback(limit: int)` → `List[Dict[str, Any]]`
  > Retorna feedback da IA para humano.

Args:
    limit: Número máximo de itens

Re...

### `TrustMetrics`

Sistema de métricas de confiança humano-IA.

Trust é construído através de:
- Consistência (reliability)
- Transparência (explainability)
- Competência (success rate)
- Alinhamento (value alignment)

**Métodos principais:**

- `get_trust_level(human_id: str)` → `float`
  > Retorna nível de confiança atual (0-1).

Trust = weighted average of:
- 0.3 * re...
- `update_trust(human_id: str, outcome: Dict[str, Any])` → `float`
  > Atualiza trust baseado em outcome de colaboração.

Args:
    human_id: Identific...
- `get_trust_breakdown(human_id: str)` → `Dict[str, float]`
  > Retorna breakdown de trust por componente.

Args:
    human_id: Identificador do...
- `get_trust_history(human_id: str, limit: Optional[int])` → `List[TrustEvent]`
  > Retorna histórico de eventos de trust.

Args:
    human_id: Identificador do hum...
- `reset_trust(human_id: str)` → `None`
  > Reseta trust para valores iniciais.

Args:
    human_id: Identificador do humano...

### `GoalNegotiator`

Negociador dialético de objetivos humano-IA.

Princípios:
1. Humano propõe objetivo inicial
2. IA questiona premissas e sugere refinamentos
3. Iteração até convergência ou timeout
4. Resultado é síntese dialética, não imposição

**Métodos principais:**

- `negotiate(human_intent: Dict[str, Any], ai_perspective: Dict)` → `NegotiationResult`
  > Negocia objetivo entre humano e IA.

Args:
    human_intent: Intenção/objetivo d...
- `quick_accept(human_intent: Dict[str, Any], trust_level: float)` → `NegotiationResult`
  > Aceita objetivo rapidamente (sem negociação) se trust é alto.

Args:
    human_i...

### `BiasType(Enum)`

Tipos de viés detectáveis.


### `BiasDetection`

Detecção de viés.


### `FeedbackType(Enum)`

Tipo de feedback.


### `FeedbackDirection(Enum)`

Direção do feedback.



## ⚙️ Funções Públicas

#### `__init__()` → `None`

*Inicializa detector de viés....*

#### `__init__()` → `None`

*Inicializa sistema de feedback....*

#### `__init__()` → `None`

*Inicializa memória de co-evolução....*

#### `__init__()` → `None`

*Inicializa framework HCHAC....*

#### `__init__(max_rounds: int, convergence_threshold: float)` → `None`

*Inicializa negociador.

Args:
    max_rounds: Número máximo de rodadas
    convergence_threshold: Th...*

#### `__init__()` → `None`

*Inicializa sistema de trust metrics....*

#### `_aligns_with_hypothesis(result: Any, hypothesis: str)` → `bool`

*Verifica se resultado alinha com hipótese....*

#### `_allocate_roles(human_id: str, task: Dict[str, Any], ai_capabiliti)` → `Dict[str, Role]`

*Aloca papéis dinamicamente baseado em competências.

Args:
    human_id: ID do humano
    task: Obje...*

#### `_calculate_convergence(proposal1: Dict[str, Any], proposal2: Dict[str, An)` → `float`

*Calcula score de convergência entre propostas.

Args:
    proposal1: Primeira proposta
    proposal2...*

#### `_calculate_distribution(data: List[Any])` → `Dict[str, float]`

*Calcula distribuição de dados....*

#### `_calculate_divergence(dist1: Dict[str, float], dist2: Dict[str, float])` → `float`

*Calcula divergência entre distribuições....*

#### `_calculate_learning_gain(result: ExecutionResult)` → `float`

*Calcula quanto a IA aprendeu da colaboração.

Args:
    result: Resultado da execução

Returns:
    ...*

#### `_categorize_task(task_description: str)` → `str`

*Categoriza tarefa....*

#### `_correct_automation_bias(result: Dict[str, Any])` → `Dict[str, Any]`

*Corrige viés de automação....*

#### `_correct_confirmation_bias(result: Dict[str, Any])` → `Dict[str, Any]`

*Corrige viés de confirmação....*


## 📦 Módulos

**Total:** 6 arquivos

- `bias_detector.py`: Sistema de Detecção e Correção de Viés Algorítmico.

Detecta...
- `bidirectional_feedback.py`: Sistema de Feedback Bidirecional Humano-IA.

Permite feedbac...
- `coevolution_memory.py`: Sistema de Memória de Co-evolução.

Armazena histórico de co...
- `hchac_framework.py`: Framework de Colaboração Human-Centered AI (HCHAC).

Orquest...
- `negotiation.py`: Sistema de Negociação Dialética de Objetivos.

Permite que h...
- `trust_metrics.py`: Sistema de Métricas de Confiança Humano-IA.

Trust é constru...
