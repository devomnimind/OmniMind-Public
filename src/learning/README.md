# Módulo Aprendizado Contínuo

## 📋 Descrição Geral

**EWC, Page Curve Learning, prevenção esquecimento catastrófico**

**Status**: Phase 14
**Última Atualização**: 2025-12-10

Módulo do sistema OmniMind responsável por funcionalidades específicas integradas à arquitetura global. Implementa componentes essenciais que contribuem para o funcionamento coeso do sistema de consciência artificial.

## ✅ Integração com Métricas de Consciência (2025-12-08)

O módulo de aprendizado integra com métricas de consciência corrigidas:
- **Φ (Phi)**: Usa `PHI_OPTIMAL = 0.06 nats` (recalibrado) para otimização de aprendizado
- **Validação**: Operações de aprendizado preservam Φ > `PHI_THRESHOLD` (0.01 nats)
- **Constantes**: Importadas de `src/consciousness/phi_constants.py`

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
learning/
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
- Métricas específicas do módulo armazenadas em `data/learning/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/learning/`
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
- ✅ Executar testes antes de commit: `pytest tests/learning/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/learning.txt (se existir)
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
- **Suite de Testes**: `tests/learning/`
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

# 📁 LEARNING

**4 Classes | 22 Funções | 2 Módulos**

---

## 🏗️ Classes Principais

### `PageCurveLearner`

Learning system that follows Page curve dynamics.

Models learning as information-theoretic process where:
1. Initial phase: Entropy increases (system explores, gets confused)
2. Page time: Entropy peaks (critical transition point)
3. Consolidation: Entropy decreases (information recovery, understanding)

This mirrors black hole evaporation where information is initially lost,
then recovered through entanglement correlations.

**Métodos principais:**

- `record_epoch(model_state: Dict[str, Any], loss: Optional[float])` → `Dict[str, Any]`
  > Record learning progress for one epoch.

Args:
    model_state: Current model st...
- `get_page_curve()` → `PageCurve`
  > Get complete Page curve data.

Returns:
    PageCurve object with full history...
- `get_statistics()` → `Dict[str, Any]`
  > Get learning statistics.

Returns:
    Dict with statistics...
- `reset()` → `None`
  > Reset learner state for new training run....

### `ElasticWeightConsolidation`

Implements Elastic Weight Consolidation.

Maintains a Fisher Information Matrix to estimate the importance of each parameter
(weight) for previous tasks. When training on a new task (or adjusting weights
via ICAC), it adds a penalty for changing important parameters.

**Métodos principais:**

- `compute_fisher_information(agent_weights: Dict[str, float], audit_history: Li)` → `None`
  > Computes (or approximates) the Fisher Information Matrix for the current weights...
- `penalty_loss(new_weights: Dict[str, float])` → `float`
  > Calculates the EWC penalty loss for a proposed set of new weights.

Loss = (lamb...
- `adjust_weights_with_protection(current_weights: Dict[str, float], proposed_change)` → `Dict[str, float]`
  > Adjusts weights based on proposed changes, but mitigates changes to
important we...

### `LearningPhase(Enum)`

Learning phases based on Page curve.


### `PageCurve`

Page curve data structure.

Attributes:
    entropy_history: Full entropy evolution
    epochs: Corresponding epoch numbers
    page_time_epoch: Epoch where Page time occurred (if detected)
    max_entropy: Maximum entropy reached
    current_phase: Current learning phase



## ⚙️ Funções Públicas

#### `__init__(lambda_ewc: float)` → `None`

*Args:
    lambda_ewc: Hyperparameter that controls how much to penalize changes
                to i...*

#### `__init__(detection_window: int, page_time_threshold: float,)` → `None`

*Initialize Page curve learner.

Args:
    detection_window: Window size for detecting entropy trends...*

#### `_compute_correlation_entropy(data: List[float])` → `float`

*Compute entropy using correlation matrix approximation.

Args:
    data: Numerical data

Returns:
  ...*

#### `_compute_entropy_trend()` → `float`

*Compute current entropy trend.

Returns:
    Trend value (positive = increasing, negative = decreasi...*

#### `_compute_simple_entropy(data: List[float])` → `float`

*Compute simple Shannon entropy on normalized absolute values.

Args:
    data: Numerical data

Retur...*

#### `_enable_information_recovery_mode()` → `None`

*Enable information recovery mode.

After Page time, system should focus on consolidating
learned inf...*

#### `_extract_numerical_data(model_state: Dict[str, Any])` → `List[float]`

*Extract numerical data from model state with fallback.

Args:
    model_state: Model state dict

Ret...*

#### `_generate_fallback_data(model_state: Dict[str, Any])` → `List[float]`

*Generate deterministic fallback data when no numerical data available.

Args:
    model_state: Model...*

#### `_generate_recommendations()` → `Dict[str, Any]`

*Generate learning recommendations based on current phase.

Returns:
    Dict with recommendations...*

#### `_is_declining_trend(values: List[float])` → `bool`

*Check if values show declining trend.

Args:
    values: List of values to check

Returns:
    True ...*

#### `_is_page_time()` → `bool`

*Detect if Page time has occurred.

Page time is when entropy peaks and starts to decrease.
This is t...*

#### `_linear_regression_slope(values: List[float])` → `float`

*Compute slope of linear regression for y over x=[0..n-1]....*

#### `_should_use_simple_entropy(data: List[float])` → `bool`

*Determine if simple entropy calculation should be used.

Args:
    data: Numerical data

Returns:
  ...*

#### `_update_phase()` → `None`

*Update current learning phase based on entropy dynamics....*

#### `_von_neumann_entropy(model_state: Dict[str, Any])` → `float`

*Compute von Neumann entropy of model state.

S = -Tr(ρ log ρ) where ρ is density matrix

Approximati...*


## 📦 Módulos

**Total:** 2 arquivos

- `ewc.py`: Elastic Weight Consolidation (EWC) Module.

This module impl...
- `page_curve_learning.py`: Page Curve Learning - Non-Monotonic Knowledge Growth

Implem...
