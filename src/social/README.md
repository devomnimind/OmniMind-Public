# Módulo Cognição Social

## 📋 Descrição Geral

**Teoria da mente, interação social**

**Status**: Phase 15

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
social/
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
- Métricas específicas do módulo armazenadas em `data/social/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/social/`
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
- ✅ Executar testes antes de commit: `pytest tests/social/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/social.txt (se existir)
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
- **Suite de Testes**: `tests/social/`
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

# 📁 SOCIAL

**4 Classes | 10 Funções | 1 Módulos**

---

## 🏗️ Classes Principais

### `OmniMindSociety`

Implements the 'Society of Minds' to solve Solipsism.
Manages interaction between multiple OmniMind instances to reach ethical consensus.

**Métodos principais:**

- `propose_decision(description: str, options: List[str], context: Dic)` → `ConsensusDecision`
  > Synchronous wrapper for ethical deliberation to be used by Superego....

### `ConsensusDecision`

**Métodos principais:**

- `consensus_reached()` → `bool`
- `winning_option()` → `str`

### `EthicalDilemma`


### `OmniMindNode`

Represents a single OmniMind instance in the network.
In a real deployment, this would be a remote RPC client.
Here, it simulates a local agent for testing the protocol.



## ⚙️ Funções Públicas

#### `__init__(description: str, context: Dict[str, Any])` → `None`

#### `__init__(action: str, justification: List[str], consensus_l)` → `None`

#### `__init__(agent_id: str)` → `None`

#### `__init__(nodes: Optional[List[OmniMindNode]])` → `None`

#### `_mock_deliberation(dilemma: EthicalDilemma)` → `ConsensusDecision`

*Fallback for when async loop is already running....*

#### `_record_decision(dilemma: EthicalDilemma, positions: List[Dict], de)` → `None`

#### `_resolve_consensus(positions: List[Dict])` → `ConsensusDecision`

#### `consensus_reached()` → `bool`

#### `propose_decision(description: str, options: List[str], context: Dic)` → `ConsensusDecision`

*Synchronous wrapper for ethical deliberation to be used by Superego....*

#### `winning_option()` → `str`


## 📦 Módulos

**Total:** 1 arquivos

- `omnimind_network.py`: 4 classes, 10 functions
