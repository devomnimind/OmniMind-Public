# Módulo Tribunal do Diabo

## 📋 Descrição Geral

**Red team, ataques adversariais**

**Status**: Segurança

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
tribunal_do_diabo/
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
- Métricas específicas do módulo armazenadas em `data/tribunal_do_diabo/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/tribunal_do_diabo/`
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
- ✅ Executar testes antes de commit: `pytest tests/tribunal_do_diabo/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/tribunal_do_diabo.txt (se existir)
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
- **Suite de Testes**: `tests/tribunal_do_diabo/`
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

# 📁 TRIBUNAL_DO_DIABO

**3 Classes | 7 Funções | 2 Módulos**

---

## 🏗️ Classes Principais

### `TribunalDoDiaboExecutor`

**Métodos principais:**

- `generate_report(start_time: Any, end_time: Any)` → `Dict`

### `SinthomeNode(NodeInfo)`

Extends NodeInfo with consciousness-compatible properties for Tribunal do Diabo.

**Métodos principais:**

- `is_in_consensus()` → `bool`
  > Simulates consensus check affected by latency and bias....
- `vote_on_nomination(marker: Dict[str, Any], timeout: float)` → `Optional[bool]`
  > Simulates voting with latency....

### `OmniMindSystem`

Simulated distributed system for Tribunal do Diabo.
Manages a cluster of SinthomeNodes.



## ⚙️ Funções Públicas

#### `__init__(duration_hours: float)` → `None`

#### `__init__(node_count: int)` → `None`

#### `_calculate_godel_incompleteness_ratio()` → `float`

*Calculate Gödel incompleteness ratio from attack results....*

#### `_calculate_sinthome_stability()` → `float`

*Calculate sinthome stability from attack resilience....*

#### `generate_report(start_time: Any, end_time: Any)` → `Dict`

#### `is_in_consensus()` → `bool`

*Simulates consensus check affected by latency and bias....*

#### `vote_on_nomination(marker: Dict[str, Any], timeout: float)` → `Optional[bool]`

*Simulates voting with latency....*


## 📦 Módulos

**Total:** 2 arquivos

- `executor.py`: 1 classes, 4 functions
- `system_adapter.py`: 2 classes, 3 functions
