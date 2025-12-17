# Módulo Integração Neurossimbólica

## 📋 Descrição Geral

**11 níveis de integração neural-simbólico**

**Status**: Phase 16

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

## 📊 Estrutura do Código

```
neurosymbolic/
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
- Métricas específicas do módulo armazenadas em `data/neurosymbolic/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/neurosymbolic/`
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
- ✅ Executar testes antes de commit: `pytest tests/neurosymbolic/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/neurosymbolic.txt (se existir)
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
- **Suite de Testes**: `tests/neurosymbolic/`
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

# 📁 NEUROSYMBOLIC

**14 Classes | 51 Funções | 6 Módulos**

---

## 🏗️ Classes Principais

### `NeuralComponent`

Componente neural do sistema neurosymbolic.

Integra-se com LLMs (Ollama local ou Hugging Face API) para raciocínio
probabilístico e processamento de linguagem natural.

**Métodos principais:**

- `infer(query: str, context: Optional[Dict[str, Any]], cha)` → `NeuralInference`
  > Realizar inferência neural sobre query.

Args:
    query: Pergunta ou problema
 ...
- `embed(text: str)` → `List[float]`
  > Gerar embedding para texto.

Args:
    text: Texto a embeddar

Returns:
    Veto...
- `batch_infer(queries: List[str], context: Optional[Dict[str, An)` → `List[NeuralInference]`
  > Inferências em batch para múltiplas queries.

Args:
    queries: Lista de pergun...
- `process(input_data: Any)` → `Dict[str, Any]`
  > Wrapper genérico para processamento (compatibilidade de interface).

Args:
    i...

### `NeuralResponseCache`

Cache LRU com TTL para respostas neurais.

Features:
- LRU eviction (Least Recently Used)
- TTL (Time To Live) configurável
- Hash de query para lookup rápido
- Métricas de hit rate

**Métodos principais:**

- `get(query: str, context: Optional[Dict[str, Any]])` → `Optional[CachedResponse]`
  > Busca resposta em cache.

Args:
    query: Query original
    context: Contexto ...
- `put(query: str, answer: str, confidence: float, backen)` → `None`
  > Armazena resposta em cache.

Args:
    query: Query original
    answer: Respost...
- `clear()` → `None`
  > Limpa todo o cache....
- `evict_expired()` → `int`
  > Remove entradas expiradas.

Returns:
    Número de entradas removidas...
- `get_stats()` → `Dict[str, Any]`
  > Retorna estatísticas do cache.

Returns:
    Dict com métricas...

### `SymbolicComponent`

Componente simbólico do sistema neurosymbolic.

Implementa raciocínio baseado em lógica formal, grafos
de conhecimento e regras explícitas.

**Métodos principais:**

- `add_fact(subject: str, predicate: str, obj: str)` → `None`
  > Adicionar fato ao grafo de conhecimento.

Args:
    subject: Sujeito do fato
   ...
- `add_rule(antecedents: List[str], consequent: str)` → `None`
  > Adicionar regra de inferência.

Args:
    antecedents: Lista de antecedentes (co...
- `infer(query: str, max_depth: int)` → `SymbolicInference`
  > Realizar inferência simbólica.

Args:
    query: Query em lógica formal
    max_...
- `query(query_string: str)` → `List[SymbolicFact]`
  > Consultar conhecimento.

Args:
    query_string: Query simples (ex: "Sócrates is...
- `get_all_facts()` → `List[SymbolicFact]`
  > Retorna todos os fatos no grafo....

### `NeuralMetricsCollector`

Coleta e agrega métricas de todos os backends neurais.

Features:
- Latência (p50, p95, p99)
- Taxa de erro
- Throughput
- Health status

**Métodos principais:**

- `record_request(backend: str, latency_seconds: float, success: boo)` → `None`
  > Registra uma requisição.

Args:
    backend: Nome do backend (ollama, huggingfac...
- `get_backend_metrics(backend: str)` → `Optional[BackendMetrics]`
  > Retorna métricas de um backend específico....
- `get_all_metrics()` → `Dict[str, BackendMetrics]`
  > Retorna métricas de todos os backends....
- `get_summary()` → `Dict[str, Any]`
  > Retorna resumo consolidado de métricas.

Returns:
    Dict com métricas agregada...
- `reset()` → `None`
  > Reseta todas as métricas....

### `NeurosymbolicReasoner`

Motor de raciocínio híbrido neural + simbólico.

Estratégia:
  1. Ambos (neural + simbólico) raciocinam sobre o problema
  2. Compara resultados
  3. Reconcilia conforme estratégia
  4. Retorna resposta híbrida com confiança aumentada

**Métodos principais:**

- `infer(query: str, context: Optional[Dict[str, Any]], str)` → `Inference`
  > Inferência híbrida neurosymbolic.

Args:
    query: Pergunta ou problema
    con...
- `add_knowledge(knowledge: Tuple[str, str, str])` → `None`
  > Adicionar conhecimento ao grafo simbólico.

Args:
    knowledge: Tupla (sujeito,...
- `batch_infer(queries: List[str], context: Optional[Dict[str, An)` → `List[Inference]`
  > Batch de inferências.

Args:
    queries: Lista de queries
    context: Contexto...
- `explain(inference: Inference)` → `str`
  > Explicar resultado de inferência.

Args:
    inference: Resultado de inferência
...
- `reason(reconciliation_result: Any, context: Dict[str, Any)` → `Dict[str, Any]`
  > Raciocinar sobre o resultado reconciliado.

Args:
    reconciliation_result: Res...

### `BackendMetrics`

Métricas de um backend neural.

**Métodos principais:**

- `success_rate()` → `float`
  > Taxa de sucesso (0-1)....
- `average_latency()` → `float`
  > Latência média em segundos....
- `p50_latency()` → `float`
  > Mediana de latência (percentil 50)....
- `p95_latency()` → `float`
  > Percentil 95 de latência....
- `p99_latency()` → `float`
  > Percentil 99 de latência....

### `Reconciliator`

Reconcilia resultados de neural e simbólico.

Decide como combinar ou escolher entre respostas quando
neural e simbólico fornecem resultados diferentes.

**Métodos principais:**

- `reconcile(neural_answer: str, neural_confidence: float, symb)` → `ReconciliationResult`
  > Reconciliar respostas neural e simbólica.

Args:
    neural_answer: Resposta neu...

### `Inference`

Resultado de inferência híbrida neurosymbolic.


### `NeuralInference`

Resultado de inferência neural.


### `ReconciliationStrategy(Enum)`

Estratégias de reconciliação entre neural e simbólico.



## ⚙️ Funções Públicas

#### `__init__(neural_model: str, knowledge_graph_path: Optional[)` → `None`

*Inicializa raciocínio neurosymbolic.

Args:
    neural_model: Nome do modelo neural
    knowledge_gr...*

#### `__init__()` → `None`

*Inicializa o coletor de métricas....*

#### `__init__(model_name: str, temperature: float, max_tokens: i)` → `None`

*Inicializa componente neural.

Args:
    model_name: Nome do modelo. Prefixos suportados:
          ...*

#### `__init__(max_size: int, ttl_seconds: float)` → `None`

*Inicializa cache.

Args:
    max_size: Número máximo de entradas
    ttl_seconds: Tempo de vida (seg...*

#### `__init__(knowledge_graph_path: Optional[str])` → `None`

*Inicializa componente simbólico.

Args:
    knowledge_graph_path: Caminho para arquivo de conhecimen...*

#### `_hash_query(query: str, context: Optional[Dict[str, Any]])` → `str`

*Gera hash único para query + context.

Args:
    query: Query original
    context: Contexto opciona...*

#### `_infer_hf_space(query: str, context: Optional[Dict[str, Any]])` → `NeuralInference`

*Inferência via HF Space Dedicado (FastAPI)....*

#### `_infer_huggingface(query: str, context: Optional[Dict[str, Any]])` → `NeuralInference`

*Inferência via Hugging Face Inference API (Direct HTTP)....*

#### `_infer_ollama(query: str, context: Optional[Dict[str, Any]])` → `NeuralInference`

*Inferência via Ollama local....*

#### `_infer_stub(query: str, error: Optional[str])` → `NeuralInference`

*Fallback stub para testes ou falhas....*

#### `_reconcile_agreement(neural_answer: str, neural_confidence: float, symb)` → `ReconciliationResult`

*Quando ambos concordam, confiança é alta....*

#### `_reconcile_neural_dominant(neural_answer: str, neural_confidence: float, symb)` → `ReconciliationResult`

*Neural domina - para criatividade e tarefas abertas....*

#### `_reconcile_symbolic_dominant(neural_answer: str, neural_confidence: float, symb)` → `ReconciliationResult`

*Symbolic domina - para lógica e problemas formais....*

#### `_reconcile_synthesis(neural_answer: str, neural_confidence: float, symb)` → `ReconciliationResult`

*Síntese - combinar perspectivas....*

#### `add_fact(subject: str, predicate: str, obj: str)` → `None`

*Adicionar fato ao grafo de conhecimento.

Args:
    subject: Sujeito do fato
    predicate: Propried...*


## 📦 Módulos

**Total:** 6 arquivos

- `hybrid_reasoner.py`: Motor Híbrido Neurosymbolic - Orquestrador Principal

Combin...
- `metrics_collector.py`: Neural Component Metrics Collector - Phase 20.

Coleta métri...
- `neural_component.py`: Componente Neural - Interface com LLMs e Transformers

Respo...
- `reconciliation.py`: Estratégias de Reconciliação - Quando Neural e Simbólico Dis...
- `response_cache.py`: Neural Response Cache - Phase 21.

Implementa cache intelige...
- `symbolic_component.py`: Componente Simbólico - Motor de Lógica Formal

Responsável p...
