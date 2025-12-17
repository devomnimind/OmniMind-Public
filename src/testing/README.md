# Módulo Framework de Testes

## 📋 Descrição Geral

**Unitários, integração, validação**

**Status**: Quality

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
testing/
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
- Métricas específicas do módulo armazenadas em `data/testing/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/testing/`
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
- ✅ Executar testes antes de commit: `pytest tests/testing/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/testing.txt (se existir)
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
- **Suite de Testes**: `tests/testing/`
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

# 📁 TESTING

**3 Classes | 17 Funções | 1 Módulos**

---

## 🏗️ Classes Principais

### `ChaosMonkey`

Chaos Monkey for OmniMind.

Injects failures to test system resilience.

**Métodos principais:**

- `register_experiment(experiment: ChaosExperiment)` → `None`
  > Register a chaos experiment.

Args:
    experiment: Experiment configuration...
- `inject_failure(component: str, operation: str)` → `Optional[Exception]`
  > Inject failure if chaos is enabled and conditions are met.

Args:
    component:...
- `get_failure_report()` → `Dict[str, Any]`
  > Get report of all failures injected....

### `FailureType(Enum)`

Types of failures to inject.


### `ChaosExperiment`

Configuration for a chaos experiment.



## ⚙️ Funções Públicas

#### `__init__(enabled: bool)` → `None`

*Initialize Chaos Monkey.

Args:
    enabled: Whether chaos engineering is enabled...*

#### `_count_by_component()` → `Dict[str, int]`

*Count failures by component....*

#### `_count_by_type()` → `Dict[str, int]`

*Count failures by type....*

#### `_generate_failure(experiment: ChaosExperiment, operation: str)` → `Optional[Exception]`

*Generate failure based on experiment type....*

#### `chaos_aware(component: str, operation: Optional[str])` → `Callable[..., Any]`

*Decorator to make a function chaos-aware.

Args:
    component: Component name
    operation: Operat...*

#### `create_api_timeout_experiment()` → `ChaosExperiment`

*Create experiment for API timeouts....*

#### `create_database_latency_experiment()` → `ChaosExperiment`

*Create experiment for database latency....*

#### `create_llm_failure_experiment()` → `ChaosExperiment`

*Create experiment for LLM failures....*

#### `create_memory_exhaustion_experiment()` → `ChaosExperiment`

*Create experiment for memory exhaustion....*

#### `decorator(func: , Any])` → `Callable[..., Any]`

#### `enable_chaos(enabled: bool)` → `None`

*Enable or disable chaos engineering globally.

Args:
    enabled: Whether to enable chaos...*

#### `get_failure_report()` → `Dict[str, Any]`

*Get report of all failures injected....*

#### `inject_chaos(component: str, operation: str)` → `None`

*Inject chaos if enabled.

Args:
    component: Component being tested
    operation: Operation being...*

#### `inject_failure(component: str, operation: str)` → `Optional[Exception]`

*Inject failure if chaos is enabled and conditions are met.

Args:
    component: Component being tes...*

#### `register_default_experiments()` → `None`

*Register default chaos experiments....*


## 📦 Módulos

**Total:** 1 arquivos

- `chaos_engineering.py`: Chaos Engineering Framework for OmniMind

Implements failure...
