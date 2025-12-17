# Módulo Monitoramento do Sistema

## 📋 Descrição Geral

**Observabilidade, alertas, proteção de recursos**

**Status**: DevOps

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
monitor/
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
- Métricas específicas do módulo armazenadas em `data/monitor/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Nightly Metrics (`scripts/nightly_omnimind.py`)
- Relatórios detalhados por execução em `logs/nightly/nightly_report_YYYYMMDD_HHMMSS.json`:
  - Status de saúde do Qdrant (local/cloud)
  - Status de saúde do Supabase
  - Resultado do teste rápido de memória (Phase 24)
  - Resultado opcional da consolidação leve de snapshots (`--consolidate`)
- Resumo agregado em `logs/nightly/nightly_summary.json`:
  - Últimos N (default: 30) registros com status agregados por tarefa
  - Útil para inspeção rápida de estabilidade/saúde sem abrir todos os relatórios

### Inspect Helper (`scripts/nightly_summary_inspect.py`)
- CLI rápido para ler `nightly_summary.json`:
  - `--limit N`: quantidade de entradas exibidas (default: 10).
  - `--only-errors`: mostra apenas execuções com algum status não OK (Qdrant, Supabase, testes ou consolidação).
- Exemplo:
  ```bash
  python scripts/nightly_summary_inspect.py --limit 15 --only-errors
  ```

### Validação
- Testes unitários: `tests/monitor/`
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
- ✅ Executar testes antes de commit: `pytest tests/monitor/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/monitor.txt (se existir)
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
- **Suite de Testes**: `tests/monitor/`
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

# 📁 MONITOR

**11 Classes | 22 Funções | 3 Módulos**

---

## 🏗️ Classes Principais

### `ProgressiveMonitor`

Monitor com modo progressivo inteligente.

**Métodos principais:**

- `set_level(level: MonitorLevel)` → `None`
  > Ajustar nível de monitoramento.

Args:
    level: Novo nível...
- `register_alert_callback(callback: Any)` → `None`
  > Registrar callback para alertas.

Args:
    callback: Função async que recebe Al...
- `add_alert(severity: AlertSeverity, title: str, message: str,)` → `Alert`
  > Adicionar alerta.

Args:
    severity: Severidade
    title: Título
    message:...
- `acknowledge_alert(alert_index: int)` → `bool`
  > Marcar alerta como lido.

Args:
    alert_index: Índice do alerta

Returns:
    ...
- `get_current_snapshot()` → `Optional[Dict[str, Any]]`
  > Obter último snapshot.

Returns:
    Último snapshot ou None...

### `ResourceProtector`

Protetor de recursos da máquina.

**Métodos principais:**

- `register_process(pid: int)` → `None`
  > Registrar processo para proteção.

Args:
    pid: Process ID...
- `get_resource_status()` → `dict`
  > Obter status atual de recursos.

Returns:
    Dict com CPU, RAM, Disco...

### `AlertSystem`

Sistema centralizado de alertas.

**Métodos principais:**

- `register_handler(channel: AlertChannel, handler: Callable)` → `None`
  > Registrar handler para canal.

Args:
    channel: Canal
    handler: Função que ...
- `get_recent_alerts(limit: int, severity: Optional[str])` → `List[Dict[str, Any]]`
  > Obter alertas recentes.

Args:
    limit: Número máximo de alertas
    severity:...
- `get_critical_alerts()` → `List[Dict[str, Any]]`
  > Obter apenas alertas críticos.

Returns:
    Lista de alertas críticos...

### `AlertEvent`

Evento de alerta para broadcast.

**Métodos principais:**

- `to_dict()` → `Dict[str, Any]`
  > Convert to dictionary....

### `SystemSnapshot`

Captura do estado do sistema em um momento.

**Métodos principais:**

- `to_dict()` → `Dict[str, Any]`
  > Convert to dictionary....

### `Alert`

Alerta do sistema.

**Métodos principais:**

- `to_dict()` → `Dict[str, Any]`
  > Convert to dictionary....

### `AlertType(str, Enum)`

Tipos de alertas.


### `AlertChannel(str, Enum)`

Canais de distribuição de alertas.


### `MonitorLevel(str, Enum)`

Níveis progressivos de monitoramento.


### `AlertSeverity(str, Enum)`

Severidade dos alertas.



## ⚙️ Funções Públicas

#### `__init__(data_dir: str)` → `None`

*Initialize alert system.

Args:
    data_dir: Directory for storing alerts...*

#### `__init__(data_dir: str)` → `None`

*Initialize progressive monitor.

Args:
    data_dir: Directory for storing monitor data...*

#### `__init__(mode: str)` → `None`

*Initialize resource protector.

Args:
    mode: "dev", "test", ou "prod"...*

#### `__post_init__()` → `None`

*Generate ID if not provided....*

#### `_get_heavy_processes()` → `List[dict]`

*Obter processos que estão consumindo muita RAM.

Returns:
    Lista de dicts com {pid, name, memory_...*

#### `_get_heavy_python_processes()` → `List[dict]`

*Obter processos Python que estão consumindo muita CPU.

Returns:
    Lista de dicts com {pid, name, ...*

#### `_take_snapshot()` → `SystemSnapshot`

*Tirar snapshot do sistema....*

#### `acknowledge_alert(alert_index: int)` → `bool`

*Marcar alerta como lido.

Args:
    alert_index: Índice do alerta

Returns:
    True se conseguiu ma...*

#### `add_alert(severity: AlertSeverity, title: str, message: str,)` → `Alert`

*Adicionar alerta.

Args:
    severity: Severidade
    title: Título
    message: Mensagem
    contex...*

#### `get_active_alerts()` → `List[Dict[str, Any]]`

*Obter alertas não-lidos.

Returns:
    Lista de alertas...*

#### `get_critical_alerts()` → `List[Dict[str, Any]]`

*Obter apenas alertas críticos.

Returns:
    Lista de alertas críticos...*

#### `get_current_snapshot()` → `Optional[Dict[str, Any]]`

*Obter último snapshot.

Returns:
    Último snapshot ou None...*

#### `get_recent_alerts(limit: int, severity: Optional[str])` → `List[Dict[str, Any]]`

*Obter alertas recentes.

Args:
    limit: Número máximo de alertas
    severity: Filtrar por severid...*

#### `get_recent_snapshots(minutes: int)` → `List[Dict[str, Any]]`

*Obter snapshots dos últimos N minutos.

Args:
    minutes: Minutos para voltar

Returns:
    Lista d...*

#### `get_resource_status()` → `dict`

*Obter status atual de recursos.

Returns:
    Dict com CPU, RAM, Disco...*


## 📦 Módulos

**Total:** 3 arquivos

- `alert_system.py`: SISTEMA DE ALERTAS INTELIGENTE
=============================...
- `progressive_monitor.py`: MODO PROGRESSIVO DO MONITOR AGENT
==========================...
- `resource_protector.py`: PROTETOR DE RECURSOS DA MÁQUINA
============================...
