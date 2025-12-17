# OmniMind Daemon - Guia do Usuário

**Última Atualização**: 5 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## O que é o OmniMind Daemon?

O OmniMind Daemon **NÃO é um chatbot**. É um serviço autônomo em background que funciona 24/7, trabalhando proativamente mesmo enquanto você dorme. Ele monitora seu sistema, executa tarefas automaticamente e ajuda a maximizar sua produtividade sem exigir interação constante.

### Características Principais

- **Sempre Rodando**: Funciona 24/7 em background
- **Proativo**: Inicia tarefas baseado no estado do sistema, não em prompts do usuário
- **Agendamento Inteligente**: Sabe quando trabalhar (tempo ocioso, horários de sono)
- **Local-First**: Todo processamento acontece na sua máquina
- **Cloud-Ready**: Pode integrar com Supabase e Qdrant quando necessário

---

## Instalação

### Pré-requisitos

- **Python 3.12.8** (obrigatório)
- Sistema Linux com systemd
- Ambiente virtual configurado
- Dependências instaladas

### Passos de Instalação

1. **Instalar Dependências**:
   ```bash
   cd ~/projects/omnimind
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Instalar Serviço Daemon** (se disponível):
   ```bash
   ./scripts/install_daemon.sh
   ```

3. **Iniciar o Daemon**:
   ```bash
   # Via systemd (se instalado)
   sudo systemctl start omnimind-daemon

   # Ou diretamente via Python
   python -m src.daemon.omnimind_daemon
   ```

4. **Habilitar Inicialização Automática**:
   ```bash
   sudo systemctl enable omnimind-daemon
   ```

---

## Gerenciamento do Daemon

### Verificar Status

```bash
# Via systemd
sudo systemctl status omnimind-daemon

# Ou via API (se servidor rodando)
curl http://localhost:8000/daemon/status
```

### Ver Logs em Tempo Real

```bash
# Via journalctl (systemd)
sudo journalctl -u omnimind-daemon -f

# Ou via arquivo de log
tail -f logs/daemon.log
```

### Parar Daemon

```bash
# Via systemd
sudo systemctl stop omnimind-daemon

# Ou via API
curl -X POST http://localhost:8000/daemon/stop
```

### Reiniciar Daemon

```bash
# Via systemd
sudo systemctl restart omnimind-daemon

# Ou via API
curl -X POST http://localhost:8000/daemon/start
```

---

## Estados do Daemon

O daemon opera em diferentes estados:

```python
class DaemonState(Enum):
    INITIALIZING = "initializing"  # Inicializando
    IDLE = "idle"                  # Ocioso, aguardando tarefas
    WORKING = "working"            # Executando tarefa
    SLEEPING = "sleeping"          # Modo sono (00:00-06:00)
    SHUTTING_DOWN = "shutting_down"  # Encerrando
    ERROR = "error"                # Estado de erro
```

### Transições de Estado

```
INITIALIZING → IDLE
    ↓
IDLE → WORKING (quando tarefa disponível)
    ↓
WORKING → IDLE (após conclusão)
    ↓
IDLE → SLEEPING (se 00:00-06:00)
    ↓
SLEEPING → IDLE (após 06:00)
```

---

## Tarefas Padrão em Background

O daemon vem com 4 tarefas pré-configuradas que rodam automaticamente:

### 1. Análise de Código (Prioridade: HIGH)

- **Quando**: Durante tempo ocioso (CPU < 20%, usuário inativo)
- **Frequência**: A cada 2 horas
- **O que faz**:
  - Analisa codebase para problemas
  - Verifica vulnerabilidades de segurança
  - Sugere melhorias
  - Atualiza documentação

### 2. Otimização de Testes (Prioridade: LOW)

- **Quando**: Durante horários de sono (00:00-06:00)
- **Frequência**: Uma vez por dia
- **O que faz**:
  - Executa suite de testes
  - Identifica testes lentos
  - Sugere melhorias de performance
  - Gera relatórios de otimização

### 3. Leitura de Papers de Pesquisa (Prioridade: LOW)

- **Quando**: Durante horários de sono
- **Frequência**: Uma vez por dia
- **O que faz**:
  - Busca papers recentes do ArXiv
  - Resume descobertas principais
  - Armazena insights na base de conhecimento
  - Sugere papers relevantes para seu trabalho

### 4. Otimização de Banco de Dados (Prioridade: MEDIUM)

- **Quando**: Durante tempo ocioso
- **Frequência**: A cada 6 horas
- **O que faz**:
  - Otimiza índices do Qdrant
  - Limpa dados antigos
  - Compacta coleções
  - Verifica integridade

---

## Criando Tarefas Customizadas

### Exemplo: Tarefa Simples

```python
from src.daemon.omnimind_daemon import OmniMindDaemon, DaemonTask, TaskPriority
from datetime import timedelta

# Criar daemon
daemon = OmniMindDaemon(
    workspace_path=Path("/home/fahbrain/projects/omnimind"),
    check_interval=30,  # Verificar a cada 30 segundos
    enable_cloud=True
)

# Definir função de tarefa
def minha_tarefa():
    print("Executando tarefa customizada...")
    # Seu código aqui
    return {"status": "success"}

# Criar tarefa
task = DaemonTask(
    task_id="minha_tarefa_001",
    name="Minha Tarefa Customizada",
    description="Executa uma tarefa específica",
    priority=TaskPriority.MEDIUM,
    execute_fn=minha_tarefa,
    repeat_interval=timedelta(hours=1),  # Repetir a cada hora
    max_duration=timedelta(minutes=15)   # Timeout de 15 minutos
)

# Registrar tarefa
daemon.register_task(task)

# Iniciar daemon
daemon.start()
```

### Exemplo: Tarefa com Prioridade Alta

```python
def tarefa_critica():
    """Tarefa que deve executar imediatamente quando sistema estiver ocioso"""
    # Verificar algo crítico
    # Enviar alerta se necessário
    pass

task = DaemonTask(
    task_id="critical_check",
    name="Verificação Crítica",
    description="Verifica condições críticas do sistema",
    priority=TaskPriority.CRITICAL,  # Executa imediatamente
    execute_fn=tarefa_critica,
    repeat_interval=timedelta(minutes=5)  # A cada 5 minutos
)
```

---

## Métricas do Sistema

O daemon coleta métricas do sistema automaticamente:

```python
@dataclass
class SystemMetrics:
    cpu_percent: float           # Uso de CPU
    memory_percent: float        # Uso de memória
    disk_usage_percent: float    # Uso de disco
    network_active: bool         # Atividade de rede
    user_active: bool            # Usuário ativo
    timestamp: datetime          # Timestamp da coleta
```

### Métodos Úteis

```python
metrics = daemon._collect_system_metrics()

# Verificar se sistema está ocioso
if metrics.is_idle():
    print("Sistema ocioso, pode executar tarefas")

# Verificar se é horário de sono
if metrics.is_sleep_time():
    print("Horário de sono (00:00-06:00)")
```

---

## Integração com Cloud

O daemon pode integrar com serviços cloud quando necessário:

### Supabase

```python
# O daemon inicializa cliente Supabase sob demanda
# Configurar via variável de ambiente:
# OMNIMIND_SUPABASE_URL=...
# OMNIMIND_SUPABASE_ANON_KEY=...
```

### Qdrant

```python
# O daemon inicializa cliente Qdrant sob demanda
# Configurar via variável de ambiente:
# OMNIMIND_QDRANT_URL=...
# OMNIMIND_QDRANT_API_KEY=...
```

### Hugging Face

```python
# Token para acesso a modelos
# Configurar via variável de ambiente:
# HUGGINGFACE_TOKEN=...
```

---

## API Endpoints

O daemon expõe endpoints via API (se servidor backend estiver rodando):

### GET /daemon/status

Retorna status completo do daemon:

```bash
curl http://localhost:8000/daemon/status
```

**Resposta**:
```json
{
  "state": "idle",
  "tasks_count": 4,
  "running_tasks": 0,
  "metrics": {
    "cpu_percent": 25.3,
    "memory_percent": 45.2,
    "disk_usage_percent": 35.8
  }
}
```

### GET /daemon/tasks

Lista todas as tarefas registradas:

```bash
curl http://localhost:8000/daemon/tasks
```

### POST /daemon/tasks/add

Adiciona nova tarefa:

```bash
curl -X POST http://localhost:8000/daemon/tasks/add \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "custom_task",
    "name": "Tarefa Customizada",
    "description": "Descrição da tarefa",
    "priority": "MEDIUM"
  }'
```

### POST /daemon/start

Inicia o daemon:

```bash
curl -X POST http://localhost:8000/daemon/start
```

### POST /daemon/stop

Para o daemon:

```bash
curl -X POST http://localhost:8000/daemon/stop
```

---

## Configuração

### Variáveis de Ambiente

```bash
# Workspace do projeto
OMNIMIND_WORKSPACE=/home/fahbrain/projects/omnimind

# Habilitar integração cloud
OMNIMIND_CLOUD_ENABLED=true

# Intervalo de verificação (segundos)
OMNIMIND_DAEMON_CHECK_INTERVAL=30

# Supabase
OMNIMIND_SUPABASE_URL=...
OMNIMIND_SUPABASE_ANON_KEY=...

# Qdrant
OMNIMIND_QDRANT_URL=...
OMNIMIND_QDRANT_API_KEY=...

# Hugging Face
HUGGINGFACE_TOKEN=...
```

### Arquivo de Configuração

`config/omnimind.yaml`:

```yaml
daemon:
  workspace_path: "/home/fahbrain/projects/omnimind"
  check_interval: 30
  enable_cloud: true
  max_concurrent_tasks: 1
  default_task_timeout: 1800  # 30 minutos
```

---

## Troubleshooting

### Daemon não inicia

**Problema**: Daemon não inicia ou para imediatamente

**Solução**:
1. Verificar logs: `journalctl -u omnimind-daemon -n 50`
2. Verificar Python: `python --version` (deve ser 3.12.8)
3. Verificar dependências: `pip list | grep psutil`
4. Verificar permissões: `ls -la ~/projects/omnimind`

### Tarefas não executam

**Problema**: Tarefas registradas não são executadas

**Solução**:
1. Verificar se sistema está ocioso: `top` ou `htop`
2. Verificar prioridade da tarefa (CRITICAL executa imediatamente)
3. Verificar logs do daemon
4. Verificar se `repeat_interval` não é muito longo

### Alto uso de recursos

**Problema**: Daemon consome muitos recursos

**Solução**:
1. Aumentar `check_interval` (verificar menos frequentemente)
2. Reduzir número de tarefas simultâneas
3. Ajustar `max_duration` das tarefas
4. Verificar se tarefas não estão em loop infinito

---

## Referências

- **Código Fonte**: `src/daemon/omnimind_daemon.py`
- **Documentação do Módulo**: `src/daemon/README.md`
- **API Reference**: `docs/api/INTERACTIVE_API_PLAYGROUND.md`
- **Quick Start**: `docs/canonical/QUICK_START.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
