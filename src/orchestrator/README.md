# Módulo Orquestração

## 📋 Descrição Geral

**Coordenação de módulos, workflows**

**Status**: Core

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

**MetaReActCoordinator** (`meta_react_coordinator.py`):
- Coordenação em nível meta para orquestração
- Gerenciamento de mudanças de estratégia (SEQUENTIAL, PIPELINE, ADAPTIVE)
- Recuperação de falhas em nível meta
- Composição de agentes baseada em requisitos
- Integração com ErrorAnalyzer para análise estrutural
- ✅ **Substitui** `integrity.intelligent_integrator` (deprecated - Phase 26D)

**IntrospectionLoop** (`introspection_loop.py`):
- Loop de aprendizado e introspecção contínua
- Auto-análise e melhoria iterativa
- ✅ **Substitui** `intelligence.learning_loop` (deprecated - Phase 26B)

**ErrorAnalyzer** (`error_analyzer.py`):
- Análise estrutural de erros
- Classificação de tipos de erro (SYNTAX, DEPENDENCY, HALLUCINATION, etc.)
- Sugestão de estratégias de recuperação
- Aprendizado de padrões de erro
- Integração com ModuleMetricsCollector e StructuredModuleLogger

**RAGFallbackSystem** (`rag_fallback.py`):
- Sistema de fallback inteligente quando agentes falham
- Geração de queries de recuperação baseada em análise de erro
- Integração com HybridRetrievalSystem e DatasetIndexer
- Aumento de contexto para re-execução
- Integração com ModuleMetricsCollector e StructuredModuleLogger
- ✅ **Indexação de Datasets** (2025-12-08): Integração completa com DatasetIndexer para indexar todos os datasets disponíveis
- ✅ **7 datasets indexados**: scientific_papers_arxiv, qasper_qa, human_vs_ai_code, turing_reasoning, infllm_v2_data, dbpedia_ontology

**SandboxSystem** (`sandbox_system.py`) - ✅ COMPLETO (2025-12-06):
- Sistema de sandbox para auto-melhoria segura
- Criação de snapshots de estado antes de mudanças
- Validação de mudanças antes de aplicar (RollbackSystem + validação de código Python)
- Aplicação de mudanças em isolamento
- Detecção automática de degradação
- Rollback automático em caso de falha
- Histórico completo de mudanças
- Integração completa com OrchestratorAgent (métodos: `apply_safe_change`, `get_sandbox_status`, `get_sandbox_history`)
- Testes: 11/11 passando

**MCPOrchestrator Integration** - ✅ COMPLETO (2025-12-06):
- Integração do MCPOrchestrator no OrchestratorAgent
- Gerenciamento centralizado de servidores MCP
- Health monitoring e lifecycle management
- Métodos de conveniência para Filesystem MCP (`mcp_read_file`, `mcp_write_file`, `mcp_list_dir`, `mcp_file_stat`)
- Status de servidores MCP (`get_mcp_orchestrator_status`)

## 📊 Estrutura do Código

```
orchestrator/
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
- Métricas específicas do módulo armazenadas em `data/orchestrator/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/orchestrator/`
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
- ✅ Executar testes antes de commit: `pytest tests/orchestrator/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/orchestrator.txt (se existir)
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
- **Suite de Testes**: `tests/orchestrator/`
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

# 📁 ORCHESTRATOR

**1 Classes | 1 Funções | 1 Módulos**

---

## 🏗️ Classes Principais

### `TaskExecutor`

Robust Task Executor for OmniMind.
Handles Quantum, Symbolic, and Workflow execution with error recovery.



## ⚙️ Funções Públicas

#### `__init__()` → `None`


## 📦 Módulos

**Total:** 1 arquivos

- `task_executor.py`: 1 classes, 1 functions
