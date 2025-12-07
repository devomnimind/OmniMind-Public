# Módulo Microserviços

## 📋 Descrição Geral

**Backend services, componentes**

**Status**: Infraestrutura

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
services/
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
- Métricas específicas do módulo armazenadas em `data/services/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/services/`
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
- ✅ Executar testes antes de commit: `pytest tests/services/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/services.txt (se existir)
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
- **Suite de Testes**: `tests/services/`
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

# 📁 SERVICES

**3 Classes | 19 Funções | 3 Módulos**

---

## 🏗️ Classes Principais

### `ReplayService`

**Métodos principais:**

- `log_event(event_type: str, data: Any)` → `None`
  > Logs an event to the replay log....
- `seek(timestamp: float)` → `Optional[Dict]`
  > Seek to timestamp with memory limits....

### `ObserverService`

**Métodos principais:**

- `log_metric(metric_type: str, data: Dict[str, Any])` → `None`
  > Append a metric entry to the JSONL file....
- `update_heartbeat()` → `None`
  > Update the heartbeat file with current status....
- `rotate_logs()` → `None`
  > Compress logs older than ROTATION_AGE_HOURS. Gera relatórios via ModuleReporter após rotação ou diariamente (meia-noite).

**Integração com ModuleReporter** (2025-12-07):
- Relatórios gerados automaticamente após rotação de logs ou diariamente
- Relatórios salvos em `data/reports/modules/observer_service_*.json`
- Inclui métricas de longo prazo coletadas pelo serviço

### `SinthomaticCompression`

**Métodos principais:**

- `estimate_storage(runtime_days: int)` → `Dict[str, float]`
  > Calculates expected footprint....


## ⚙️ Funções Públicas

#### `__init__()` → `None`

#### `__init__()` → `None`

#### `__init__(log_path: str, compression_policy: Optional[Dict])` → `None`

#### `_apply_deltas_bounded(state: Dict, target_time: float, memory_limit: int)` → `Dict`

*Generator to avoid loading all deltas into memory....*

#### `_build_index()` → `None`

*Builds a simple index of snapshots from the log file....*

#### `_collect_system_metrics()` → `Dict[str, Any]`

*Collect real system metrics using psutil....*

#### `_collect_task_info()` → `Dict[str, Any]`

*Collect task information from Tribunal.
Reads from cache/file instead of process iteration....*

#### `_default_policy()` → `None`

#### `_load_snapshot(timestamp: float)` → `Optional[Dict]`

#### `_load_tribunal_info()` → `Dict[str, Any]`

*Load Tribunal status from report file....*

#### `_save_cache_to_disk()` → `None`

*Persist cache to disk for recovery after restart....*

#### `_stream_deltas(start_time: float, end_time: float)` → `Generator[Dict, None, None]`

*Yields delta events between start_time and end_time....*

#### `estimate_storage(runtime_days: int)` → `Dict[str, float]`

*Calculates expected footprint....*

#### `get_cached_status()` → `Dict[str, Any]`

*Get cached status (O(1) operation).
Falls back to disk if memory cache is empty....*

#### `log_event(event_type: str, data: Any)` → `None`

*Logs an event to the replay log....*


## 📦 Módulos

**Total:** 3 arquivos

- `daemon_monitor.py`: Daemon Monitor - Background worker that collects heavy metri...
- `observer_service.py`: 1 classes, 4 functions
- `replay_service.py`: 2 classes, 10 functions
