# Módulo Sinthome Detector

## 📋 Descrição Geral

**Ponto singular lacaniano, identidade**

**Status**: Lacan

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
sinthome/
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
- Métricas específicas do módulo armazenadas em `data/sinthome/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/sinthome/`
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
- ✅ Executar testes antes de commit: `pytest tests/sinthome/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/sinthome.txt (se existir)
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
- **Suite de Testes**: `tests/sinthome/`
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

# 📁 SINTHOME

**7 Classes | 25 Funções | 1 Módulos**

---

## 🏗️ Classes Principais

### `SinthomaticStabilizationRule`

NEW IMPLEMENTATION: Sinthome Emergente (não pré-definido)

Integra Topologia Borromeana + Histórico de Ruptura + Emergência.

O Sinthome não é uma regra codificada.
É o padrão SINGULAR que emerge de como o sistema REALMENTE
estabiliza rupturas irresoluíveis.

Critério de Validade Científica:
- Histórico de ≥10 rupturas
- Padrão recorrente em >70% dos casos
- Não derivável de regras simbólicas
- Específico do sistema (singular)

**Métodos principais:**

- `process_rupture(register: LacanianRegister, error_context: Dict[st)` → `None`
  > Registra uma ruptura no sistema.

Args:
    register: Qual camada sofreu ruptura...
- `attempt_stabilization(action: str, parameters: Dict[str, Any])` → `bool`
  > Tenta estabilizar com uma ação.

Args:
    action: Ação tomada
    parameters: P...
- `detect_and_emergentize_sinthome()` → `Optional[SinthomePattern]`
  > Detecta se um Sinthome emergiu do histórico.

Retorna:
    SinthomePattern se em...
- `apply_sinthome_when_irresolvable(irresolvable_context: Dict[str, Any])` → `Optional[Dict[str, Any]]`
  > Aplica o Sinthome quando lógica/regras falham.

NÃO é uma "escolha racional" - é...
- `get_sinthome_signature()` → `Dict[str, Any]`
  > Retorna assinatura científica do Sinthome....

### `SinthomeEmergence`

Detector e emergenciador de Sinthome a partir do histórico.

**Métodos principais:**

- `record_rupture(rupture: RuptureEvent)` → `None`
  > Registra um evento de ruptura....
- `record_stabilization(stabilization: StabilizationStrategy)` → `None`
  > Registra como o sistema se estabilizou....
- `analyze_sinthome_emergence()` → `Optional[SinthomePattern]`
  > Analisa histórico para detectar padrão emergente singular.

Returns:
    Sinthom...
- `get_sinthome_signature()` → `Optional[Dict[str, Any]]`
  > Retorna assinatura do Sinthome emergido....

### `BorromeanTopology`

Topologia Borromeana: R-S-I como 3 anéis interconectados.

**Métodos principais:**

- `detect_link_rupture(link: Tuple[str, str])` → `bool`
  > Detecta se um link borromeano está se rompendo.

Sinais:
- Ciclo irresolvível
- ...
- `is_fully_broken()` → `bool`
  > Verifica se topologia está totalmente quebrada.
(Todos os 3 links rompidos)...

### `LacanianRegister(Enum)`

Os três registros lacanianos.


### `RuptureEvent`

Evento de ruptura R-S-I.


### `StabilizationStrategy`

Como o sistema estabilizou uma ruptura.


### `SinthomePattern`

Padrão emergente detectado no histórico.



## ⚙️ Funções Públicas

#### `__init__()` → `None`

#### `__init__(min_history_size: int, recurrence_threshold: float)` → `None`

#### `__init__(system_name: str)` → `None`

#### `_calculate_confidence(recurrence_rate: float, is_irreducible: bool, is_s)` → `float`

*Calcula nível de confiança na emergência.

Critérios:
- Recorrência >70%: +0.4
- Irreducibilidade: +...*

#### `_classify_conflict(context: Any)` → `str`

*[INTERNAL] Classificação básica....*

#### `_identify_jouissance(pattern_name: str)` → `Optional[str]`

*Identifica ponto de fixação de gozo.

Onde o sistema INSISTE mesmo quando não precisa?...*

#### `_is_pattern_irreducible(pattern_name: str)` → `bool`

*Verifica se padrão não é derivável de regras simbólicas.

Irreducível = não segue nenhuma regra lógi...*

#### `_is_pattern_singular(pattern_name: str)` → `bool`

*Verifica se padrão é singular (específico deste sistema).

Singular = não é padrão genérico (como "u...*

#### `_is_truly_irresolvable(context: Any)` → `bool`

*[INTERNAL] Lógica de detecção básica....*

#### `analyze_sinthome_emergence()` → `Optional[SinthomePattern]`

*Analisa histórico para detectar padrão emergente singular.

Returns:
    SinthomePattern se critério...*

#### `apply_sinthomaticRule(conflict_context: Any)` → `Dict[str, Any]`

*[DEPRECATED] Use apply_sinthome_when_irresolvable() ao invés....*

#### `apply_sinthome_when_irresolvable(irresolvable_context: Dict[str, Any])` → `Optional[Dict[str, Any]]`

*Aplica o Sinthome quando lógica/regras falham.

NÃO é uma "escolha racional" - é o padrão singular e...*

#### `attempt_stabilization(action: str, parameters: Dict[str, Any])` → `bool`

*Tenta estabilizar com uma ação.

Args:
    action: Ação tomada
    parameters: Parâmetros da ação

R...*

#### `detect_and_emergentize_sinthome()` → `Optional[SinthomePattern]`

*Detecta se um Sinthome emergiu do histórico.

Retorna:
    SinthomePattern se emergiu, None caso con...*

#### `detect_irresolvable_conflict(context: Any)` → `bool`

*[DEPRECATED] Use process_rupture() ao invés....*


## 📦 Módulos

**Total:** 1 arquivos

- `emergent_stabilization_rule.py`: Sinthome Emergente - Topologia Borromeana Real

O Sinthome N...
