# Módulo Meta-Aprendizado

## 📋 Descrição Geral

**Learning to learn, transferência**

**Status**: Phase 14

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
meta_learning/
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
- Métricas específicas do módulo armazenadas em `data/meta_learning/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/meta_learning/`
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
- ✅ Executar testes antes de commit: `pytest tests/meta_learning/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/meta_learning.txt (se existir)
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
- **Suite de Testes**: `tests/meta_learning/`
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

# 📁 META_LEARNING

**2 Classes | 7 Funções | 1 Módulos**

---

## 🏗️ Classes Principais

### `BlackHoleMetaLearner`

Meta-learning system triggered by knowledge density.

When knowledge density exceeds Schwarzschild radius,
system "collapses" to meta-level abstraction.

**Métodos principais:**

- `check_collapse_condition(knowledge_mass: float, knowledge_volume: float)` → `bool`
  > Check if knowledge density exceeds Schwarzschild radius.

Args:
    knowledge_ma...
- `collapse_to_meta_level(knowledge: Dict[str, Any])` → `MetaKnowledge`
  > Collapse knowledge to meta-level.

Args:
    knowledge: Knowledge to compress

R...
- `get_statistics()` → `Dict[str, Any]`
  > Get meta-learner statistics....

### `MetaKnowledge`

Meta-level knowledge extracted from collapse.



## ⚙️ Funções Públicas

#### `__init__(critical_density: float)` → `None`

*Initialize black hole meta-learner....*

#### `_define_boundary(axioms: List[str])` → `float`

*Define event horizon radius....*

#### `_extract_axioms(knowledge: Dict[str, Any])` → `List[str]`

*Extract core axioms from knowledge....*

#### `_generate_theorems(axioms: List[str])` → `List[str]`

*Generate derived theorems from axioms....*

#### `check_collapse_condition(knowledge_mass: float, knowledge_volume: float)` → `bool`

*Check if knowledge density exceeds Schwarzschild radius.

Args:
    knowledge_mass: Total knowledge ...*

#### `collapse_to_meta_level(knowledge: Dict[str, Any])` → `MetaKnowledge`

*Collapse knowledge to meta-level.

Args:
    knowledge: Knowledge to compress

Returns:
    MetaKnow...*

#### `get_statistics()` → `Dict[str, Any]`

*Get meta-learner statistics....*


## 📦 Módulos

**Total:** 1 arquivos

- `black_hole_collapse.py`: Black Hole Meta-Learning - Density-Triggered Meta-Level Tran...
