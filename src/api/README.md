# Módulo Interface REST API

## 📋 Descrição Geral

**FastAPI, endpoints, WebSocket, autenticação**

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
api/
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
- Métricas específicas do módulo armazenadas em `data/api/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/api/`
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
- ✅ Executar testes antes de commit: `pytest tests/api/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/api.txt (se existir)
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
- **Suite de Testes**: `tests/api/`
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

# 📁 API

**3 Routers | 1 Classes | 4 Funções**

---

## 🛣️ Routers Principais

### `health`

**Endpoints:**

- `GET /api/v1/health/` → `get_health()` - Get overall system health status
- `GET /api/v1/health/{check_name}/trend` → `get_health_trend()` - Get health trend for a specific check

### `daemon`

**Endpoints:**

- `GET /daemon/status` → `get_daemon_status()` - Get current daemon status with real metrics
- `GET /daemon/tasks` → `get_daemon_tasks()` - Get list of active tasks with real data from Tribunal
- `POST /daemon/tasks/add` → `add_task()` - Add a new task
- `POST /daemon/start` → `start_daemon()` - Start daemon
- `POST /daemon/stop` → `stop_daemon()` - Stop daemon
- `POST /daemon/reset-metrics` → `reset_metrics()` - Reset all system metrics to baseline values

### `messages`

**Endpoints:**

- `GET /api/omnimind/messages` → `get_messages()` - Get pending messages for polling clients
- `POST /api/omnimind/messages` → `post_message()` - Receive messages from clients via polling fallback

---

## 🏗️ Classes Principais

### `ConnectionManager`

**Métodos principais:**

- `connect(websocket: WebSocket)` → `None` - Accept WebSocket connection
- `disconnect(websocket: WebSocket)` → `None` - Remove WebSocket connection
- `broadcast(message: str)` → `None` - Broadcast message to all connected clients

## ⚙️ Funções Públicas

#### `__init__()` → `None`

#### `count_active_agents()` → `int`

*Count active OmniMind agents (Python processes).*

#### `get_task_counts()` → `tuple`

*Get real task counts from Tribunal.*

#### `broadcast_metrics()` → `None`

*Background task to broadcast simulated metrics to all connected clients.*


## 📦 Módulos

**Total:** 1 arquivos

- `main.py`: 1 classes, 4 functions
