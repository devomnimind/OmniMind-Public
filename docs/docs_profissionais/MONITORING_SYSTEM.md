# 🎯 Sistema de Monitoramento Progressivo & Alertas do OmniMind

**Última Atualização**: 08 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Componentes](#componentes)
3. [Como Usar](#como-usar)
4. [Endpoints da API](#endpoints-da-api)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Configuração](#configuração)

---

## 🎯 Visão Geral

O sistema é composto por **3 camadas inteligentes**:

```
┌─────────────────────────────────────────────────┐
│  ALERTAS EM TEMPO REAL (VS Code + WebSocket)   │
│  - Notificações de erros críticos               │
│  - Permissões negadas, servidor caído, etc      │
└─────────────────────────────────────────────────┘
                        ▲
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼────────┐ ┌───▼────────┐ ┌───▼──────────┐
│ Progressive    │ │  Resource  │ │    Alert       │
│ Monitor        │ │ Protector  │ │    System      │
│ - Modo adaptado│ │ - CPU/RAM/ │ │ - Broadcast   │
│ - Snapshots    │ │   Disco    │ │ - Histórico    │
│ - Throttle     │ │ - Matador  │ │ - Rate limit   │
│   de relatórios│ │   de procs │ │                │
└────────────────┘ └────────────┘ └──────────────┘
```

---

## 🔧 Componentes

### 1. **ProgressiveMonitor** (`src/monitor/progressive_monitor.py`)

Monitora máquina com inteligência adaptativa:

```python
from src.monitor import ProgressiveMonitor, MonitorLevel

monitor = ProgressiveMonitor(data_dir="data/monitor")

monitor.level = MonitorLevel.IDLE        # 30s entre checks, relatórios a cada 5min
monitor.level = MonitorLevel.NORMAL      # 5s entre checks, relatórios a cada 1min
monitor.level = MonitorLevel.INTENSIVE   # 1s entre checks, relatórios a cada 10s
monitor.level = MonitorLevel.CRITICAL    # 500ms entre checks, relatórios a cada 2s
```

**Características**:
- ✅ Histórico de 1000 snapshots (CPU, RAM, Disco, conexões)
- ✅ Alertas automáticos quando thresholds ultrapassados
- ✅ Relatórios throttled (não inunda com dados)
- ✅ Compressão de histórico (mantém apenas últimas 1000 amostras)

**Níveis de Monitoramento**:
- **IDLE**: Sistema ocioso, monitoramento mínimo
- **NORMAL**: Operação padrão
- **INTENSIVE**: Alta carga ou debug
- **CRITICAL**: Situação crítica, monitoramento máximo

### 2. **ResourceProtector** (`src/monitor/resource_protector.py`)

Evita que máquina fique travada/sem memória:

```python
from src.monitor import ResourceProtector

protector = ResourceProtector(mode="dev")   # 75% CPU, 80% RAM máximo (deixa IDE responsiva)
protector = ResourceProtector(mode="test")  # 85% CPU, 85% RAM máximo (mais agressivo)
protector = ResourceProtector(mode="prod")  # 90% CPU, 90% RAM máximo (máximo)
```

**O que faz**:
- 🔴 Detecta CPU/RAM/Disco críticos
- 🧹 Limpa caches automaticamente
- ⚡ Reduz prioridade de processos pesados
- 🔪 Mata processos que monopolizam recursos (exceto processos protegidos)

**Modos**:
- **dev**: Limites mais conservadores para não interferir com IDE
- **test**: Limites médios para testes
- **prod**: Limites máximos para produção

### 3. **AlertSystem** (`src/monitor/alert_system.py`)

Distribuição de alertas em tempo real:

```python
from src.monitor import AlertSystem, AlertType, AlertSeverity

alert_system = AlertSystem(data_dir="data/monitor")

# Tipos de alertas
AlertType.PERMISSION_ERROR      # Erro ao acessar arquivo
AlertType.SERVER_DOWN           # Backend offline
AlertType.RESOURCE_CRITICAL     # CPU/RAM/Disco crítico
AlertType.TEST_TIMEOUT          # Teste com timeout
AlertType.CONSCIOUSNESS_LOW     # Φ abaixo do threshold
AlertType.AUTOPOIETIC_FAILURE    # Falha no ciclo autopoiético

# Severidades
AlertSeverity.INFO
AlertSeverity.WARNING
AlertSeverity.ERROR
AlertSeverity.CRITICAL
```

**Canais de Distribuição**:
- **VSCODE**: Notificações no VS Code
- **WEBSOCKET**: Broadcast via WebSocket para dashboard
- **FILE**: Log em arquivo
- **CONSOLE**: Saída no console

---

## 📊 Dashboard Metrics Aggregator

**Componente Principal**: `DashboardMetricsAggregator` (`src/metrics/dashboard_metrics.py`)

Orquestrador centralizado que unifica todas as métricas:

### Componentes Integrados

1. **`RealConsciousnessMetricsCollector`** (`src/metrics/real_consciousness_metrics.py`):
   - Coleta as 6 métricas de consciência: Φ, ICI, PRS, Anxiety, Flow, Entropy
   - Histórico de métricas
   - Normalização de valores

2. **`RealModuleActivityTracker`** (`src/metrics/real_module_activity.py`):
   - Rastreia atividade de módulos
   - Tempo de execução
   - Taxa de erro

3. **`RealSystemHealthAnalyzer`** (`src/metrics/real_system_health.py`):
   - Análise de saúde do sistema
   - Tendências e padrões
   - Status agregado

4. **`RealBaselineSystem`** (`src/metrics/real_baseline_system.py`):
   - Comparação com baseline
   - Detecção de anomalias
   - Validação de consistência

### Uso

```python
from src.metrics.dashboard_metrics import DashboardMetricsAggregator
from src.metrics.real_consciousness_metrics import RealConsciousnessMetricsCollector

# Inicializar coletor de consciência
consciousness_collector = RealConsciousnessMetricsCollector()

# Criar agregador
aggregator = DashboardMetricsAggregator(
    consciousness_collector=consciousness_collector,
    cache_ttl_seconds=2.0  # Cache de 2 segundos
)

# Coletar snapshot completo
snapshot = await aggregator.collect_snapshot(
    include_consciousness=True,
    include_baseline=True
)

# Estrutura do snapshot:
# {
#   "system": {...},           # CPU, RAM, Disco, Uptime
#   "consciousness": {...},    # Φ, ICI, PRS, Anxiety, Flow, Entropy
#   "modules": {...},          # Atividade dos módulos
#   "health": {...},           # Status de saúde
#   "baseline": {...}          # Comparação com baseline
# }
```

---

## 🚀 Como Usar

### Inicialização Básica

```python
from src.monitor import ProgressiveMonitor, ResourceProtector, AlertSystem

# Monitor progressivo
monitor = ProgressiveMonitor(data_dir="data/monitor")
monitor.set_level(MonitorLevel.NORMAL)

# Protetor de recursos
protector = ResourceProtector(mode="dev")
protector.register_process(os.getpid())  # Proteger processo atual

# Sistema de alertas
alert_system = AlertSystem(data_dir="data/monitor")

# Registrar callback para alertas
async def handle_alert(alert):
    print(f"Alerta: {alert.title} - {alert.message}")

alert_system.register_handler(AlertChannel.CONSOLE, handle_alert)
```

### Monitoramento Contínuo

```python
import asyncio

async def monitor_loop():
    while True:
        snapshot = monitor.get_current_snapshot()
        if snapshot:
            cpu = snapshot["cpu_percent"]
            if cpu > 90:
                alert_system.add_alert(
                    severity=AlertSeverity.CRITICAL,
                    title="CPU Crítico",
                    message=f"CPU em {cpu}%"
                )
        await asyncio.sleep(5)

asyncio.run(monitor_loop())
```

---

## 📡 Endpoints da API

### Health Check

```bash
GET /api/v1/health/
```

Retorna status de saúde do sistema.

### Daemon Status

```bash
GET /daemon/status
Authorization: Basic <credentials>
```

Retorna status completo do daemon incluindo métricas de consciência.

**Resposta**:
```json
{
  "status": "running",
  "consciousness": {
    "phi": 0.5010,
    "ici": 0.65,
    "prs": 0.72,
    "anxiety": 0.15,
    "flow": 0.68,
    "entropy": 0.45
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "disk_percent": 35.8
  }
}
```

### Metrics

```bash
GET /api/omnimind/metrics/real
Authorization: Basic <credentials>
```

Retorna métricas reais de consciência.

---

## 💡 Exemplos Práticos

### Exemplo 1: Monitoramento Adaptativo

```python
from src.monitor import ProgressiveMonitor, MonitorLevel

monitor = ProgressiveMonitor(data_dir="data/monitor")

# Ajustar nível baseado em carga
if system_load < 0.3:
    monitor.set_level(MonitorLevel.IDLE)
elif system_load < 0.7:
    monitor.set_level(MonitorLevel.NORMAL)
elif system_load < 0.9:
    monitor.set_level(MonitorLevel.INTENSIVE)
else:
    monitor.set_level(MonitorLevel.CRITICAL)
```

### Exemplo 2: Proteção de Recursos Durante Testes

```python
from src.monitor import ResourceProtector

protector = ResourceProtector(mode="test")

# Registrar processos de teste
for pid in test_process_pids:
    protector.register_process(pid)

# Verificar status
status = protector.get_resource_status()
if status["cpu_percent"] > 85:
    print("⚠️ CPU alto, reduzindo prioridade de processos")
```

### Exemplo 3: Alertas Customizados

```python
from src.monitor import AlertSystem, AlertType, AlertSeverity

alert_system = AlertSystem(data_dir="data/monitor")

# Alerta de consciência baixa
if phi < 0.002:
    alert_system.add_alert(
        severity=AlertSeverity.CRITICAL,
        title="Consciência Baixa",
        message=f"Φ = {phi:.4f} está abaixo do threshold mínimo",
        alert_type=AlertType.CONSCIOUSNESS_LOW
    )
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Diretório de dados de monitoramento
OMNIMIND_MONITOR_DATA_DIR=data/monitor

# Nível de monitoramento padrão
OMNIMIND_MONITOR_LEVEL=NORMAL

# Modo de proteção de recursos
OMNIMIND_RESOURCE_MODE=dev

# Thresholds de alerta
OMNIMIND_CPU_THRESHOLD=90
OMNIMIND_RAM_THRESHOLD=85
OMNIMIND_DISK_THRESHOLD=90
```

### Arquivo de Configuração

`config/omnimind.yaml`:

```yaml
monitor:
  data_dir: "data/monitor"
  default_level: "NORMAL"
  snapshot_history_size: 1000
  report_throttle_seconds: 60

resource_protector:
  mode: "dev"
  cpu_threshold: 75
  ram_threshold: 80
  disk_threshold: 90

alerts:
  channels:
    - "WEBSOCKET"
    - "FILE"
  severity_filter: "WARNING"  # Apenas WARNING e acima
```

---

## 📊 Métricas Coletadas

### Sistema

- CPU percentual
- Memória (total, usada, disponível)
- Disco (total, usado, livre)
- Uptime
- Conexões de rede

### Consciência

- **Φ (Phi)**: Integração de Informação (IIT 3.0)
- **ICI**: Integrated Coherence Index
- **PRS**: Panarchic Resonance Score
- **Anxiety**: Tensão computacional
- **Flow**: Estado de fluxo cognitivo
- **Entropy**: Diversidade de estados

### Módulos

- Atividade por módulo
- Tempo de execução
- Taxa de erro
- Histórico de execuções

---

## 🔗 Referências

- **Código Fonte**:
  - `src/monitor/` - Componentes de monitoramento
  - `src/metrics/` - Coleta de métricas
- **Documentação**:
  - `src/monitor/README.md` - Documentação do módulo
  - `src/metrics/README.md` - Documentação de métricas
- **API**: `docs/api/INTERACTIVE_API_PLAYGROUND.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
