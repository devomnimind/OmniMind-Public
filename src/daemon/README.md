# Módulo Processos Daemon

## 📋 Descrição Geral

**Background services, workers persistentes, ciclo vital, autopoiesis**

**Status**: Infraestrutura

O módulo `daemon` implementa o **ciclo vital** do OmniMind - processos em background que mantêm o sistema funcionando continuamente. Este módulo trabalha em conjunto com `kernel_ai` para fornecer:

- **Ciclos de vida contínuos**: Mantém o sistema "vivo"
- **Autorreplicação de processos**: Autopoiesis (auto-produção)
- **Gerenciamento de tarefas**: Execução contínua de operações
- **Estado persistente**: Manutenção de estado entre ciclos

**Metáfora Filosófica**: É parte do "Osso Mecânico" que mantém o sistema "vivo" através de ciclos contínuos de produção e autorreplicação (autopoiesis). Trabalha em conjunto com `kernel_ai` para formar o substrato que mantém o sistema responsivo e autorreplicante.

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
daemon/
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
- Métricas específicas do módulo armazenadas em `data/daemon/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/daemon/`
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
- ✅ Executar testes antes de commit: `pytest tests/daemon/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/daemon.txt (se existir)
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
- **Suite de Testes**: `tests/daemon/`
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

# 📁 DAEMON

**5 Classes | 24 Funções | 1 Módulos**

---

## 🏗️ Classes Principais

### `OmniMindDaemon`

Main daemon class for OmniMind.

This daemon runs 24/7, monitoring the system and executing tasks proactively.
It integrates with cloud services (Supabase, Qdrant, Hugging Face) when needed
but prioritizes local execution.

**Métodos principais:**

- `register_task(task: DaemonTask)` → `None`
  > Register a new task for the daemon...
- `start()` → `None`
  > Start the daemon...
- `stop()` → `None`
  > Stop the daemon gracefully...
- `get_status()` → `Dict[str, Any]`
  > Get current daemon status...

### `SystemMetrics`

System resource metrics

**Métodos principais:**

- `is_idle()` → `bool`
  > Determine if system is idle enough for background work...
- `is_sleep_time()` → `bool`
  > Determine if it's sleep time (user likely away)...

### `DaemonState(Enum)`

Daemon operational states


### `TaskPriority(Enum)`

Task priority levels for the daemon


### `DaemonTask`

Represents a task for the daemon to execute



## ⚙️ Funções Públicas

#### `__init__(workspace_path: Path, check_interval: int, enable_)` → `None`

#### `_build_system_metrics(current_metrics: Optional[SystemMetrics])` → `Dict[str, Any]`

*Build system metrics dictionary for frontend....*

#### `_calculate_idle_seconds()` → `int`

*Calculate seconds system has been idle....*

#### `_calculate_uptime()` → `int`

*Calculate daemon uptime in seconds....*

#### `_collect_system_metrics()` → `SystemMetrics`

*Collect current system metrics...*

#### `_count_completed_tasks()` → `int`

*Count tasks that have been completed successfully....*

#### `_count_failed_tasks()` → `int`

*Count tasks that have failed....*

#### `_count_pending_tasks()` → `int`

*Count tasks that are pending execution....*

#### `_get_default_system_metrics()` → `Dict[str, Any]`

*Get default system metrics when no current metrics available....*

#### `_get_next_task(metrics: SystemMetrics)` → `Optional[DaemonTask]`

*Get the next task to execute based on system state and priorities...*

#### `_handle_shutdown(signum: int, frame: Any)` → `None`

*Handle shutdown signals...*

#### `_is_sleep_hours()` → `bool`

*Check if current time is during sleep hours (00:00-06:00)....*

#### `analyze_code()` → `Dict[str, Any]`

#### `create_default_tasks()` → `List[DaemonTask]`

*Create default tasks for the daemon...*

#### `get_status()` → `Dict[str, Any]`

*Get current daemon status...*


## 📦 Módulos

**Total:** 1 arquivos

- `omnimind_daemon.py`: OmniMind Daemon - 24/7 Autonomous Background Service

This m...
