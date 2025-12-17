# 📖 Guia de Uso - OmniMind

**Última Atualização**: 5 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## Visão Geral

Este guia demonstra como usar o sistema OmniMind através de diferentes interfaces: Dashboard Web, API REST, WebSocket, e Daemon.

---

## 🚀 Início Rápido

### 1. Iniciar o Sistema

```bash
# Sistema completo (backend + frontend + MCP)
./scripts/canonical/system/start_omnimind_system.sh

# Apenas backend
uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000

# Apenas frontend (em outro terminal)
cd web/frontend && npm run dev
```

### 2. Acessar Interfaces

- **Dashboard Web**: http://localhost:3000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health/

---

## 🖥️ Dashboard Web

### Acessar Dashboard

1. Inicie o sistema completo
2. Navegue para http://localhost:3000
3. Faça login com credenciais de `config/dashboard_auth.json`

### Funcionalidades Disponíveis

- **Métricas de Consciência**: Visualização de Φ, ICI, PRS, Anxiety, Flow, Entropy
- **Topologia do Rizoma**: Visualização do grafo de máquinas desejantes
- **Status do Sistema**: CPU, memória, disco, GPU
- **Tarefas**: Criação e monitoramento de tarefas orquestradas
- **Mensagens**: Interface de chat/conversação
- **Monitoramento**: Alertas e snapshots do sistema

---

## 🔌 API REST

### Autenticação

A maioria dos endpoints requer autenticação HTTP Basic:

```bash
# Obter credenciais
cat config/dashboard_auth.json

# Usar em requisições
curl -u usuario:senha http://localhost:8000/api/v1/health/
```

### Endpoints Principais

#### Health Check

```bash
# Status geral (sem autenticação)
curl http://localhost:8000/api/v1/health/

# Status de componente específico
curl http://localhost:8000/api/v1/health/database
curl http://localhost:8000/api/v1/health/gpu
curl http://localhost:8000/api/v1/health/redis

# Tendência de saúde
curl http://localhost:8000/api/v1/health/database/trend?window_size=10
```

#### Tarefas

```bash
# Criar tarefa
curl -X POST -u usuario:senha \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Analisar código",
    "priority": "high",
    "max_iterations": 3
  }' \
  http://localhost:8000/api/tasks/

# Listar tarefas
curl -u usuario:senha http://localhost:8000/api/tasks/

# Obter tarefa específica
curl -u usuario:senha http://localhost:8000/api/tasks/{task_id}

# Atualizar progresso
curl -X PUT -u usuario:senha \
  -H "Content-Type: application/json" \
  -d '{
    "progress": 50.0,
    "status": "running",
    "message": "Processando..."
  }' \
  http://localhost:8000/api/tasks/{task_id}/progress
```

#### Orquestração

```bash
# Orquestrar tarefa complexa
curl -X POST -u usuario:senha \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Implementar autenticação",
    "max_iterations": 5
  }' \
  http://localhost:8000/tasks/orchestrate
```

#### Métricas

```bash
# Métricas gerais (sem autenticação)
curl http://localhost:8000/api/metrics

# Métricas reais de consciência (requer autenticação)
curl -u usuario:senha http://localhost:8000/api/omnimind/metrics/real
```

#### Autopoietic (Phase 22+)

```bash
# Status autopoiético
curl -u usuario:senha http://localhost:8000/api/v1/autopoietic/status

# Ciclos autopoiéticos
curl -u usuario:senha http://localhost:8000/api/v1/autopoietic/cycles

# Componentes sintetizados
curl -u usuario:senha http://localhost:8000/api/v1/autopoietic/components

# Métricas de consciência
curl -u usuario:senha http://localhost:8000/api/v1/autopoietic/consciousness/metrics
```

#### Monitoramento

```bash
# Status do monitoramento
curl -u usuario:senha http://localhost:8000/api/v1/monitoring/health

# Alertas ativos
curl -u usuario:senha http://localhost:8000/api/v1/monitoring/alerts/active

# Snapshots recentes
curl -u usuario:senha http://localhost:8000/api/v1/monitoring/snapshots/recent?minutes=5
```

---

## 🔌 WebSocket

### Conexão

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Conectado ao OmniMind WebSocket');

  // Inscrever-se em canais
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['metrics', 'tasks', 'alerts']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'metrics_update') {
    console.log('Atualização de métricas:', data.data);
  } else if (data.type === 'task_update') {
    console.log('Atualização de tarefa:', data.data);
  } else if (data.type === 'alert') {
    console.log('Alerta:', data.data);
  }
};

// Manter conexão viva
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping', id: Date.now() }));
}, 30000);
```

### Canais Disponíveis

- **`metrics`**: Atualizações de métricas de consciência (Φ, ICI, PRS, etc.)
- **`tasks`**: Atualizações de status de tarefas
- **`alerts`**: Alertas do sistema
- **`system`**: Status do sistema (CPU, memória, disco)

---

## 🤖 Daemon (Serviço 24/7)

### Iniciar Daemon

```bash
# Via systemd (se instalado)
sudo systemctl start omnimind-daemon

# Ou diretamente
python -m src.daemon.omnimind_daemon
```

### Gerenciar Daemon

```bash
# Verificar status
sudo systemctl status omnimind-daemon

# Ou via API
curl -u usuario:senha http://localhost:8000/daemon/status

# Ver logs
sudo journalctl -u omnimind-daemon -f

# Parar daemon
sudo systemctl stop omnimind-daemon

# Ou via API
curl -X POST -u usuario:senha http://localhost:8000/daemon/stop
```

### Tarefas do Daemon

```bash
# Listar tarefas
curl -u usuario:senha http://localhost:8000/daemon/tasks

# Adicionar tarefa
curl -X POST -u usuario:senha \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "code_analysis",
    "name": "Análise de Código",
    "description": "Analisa codebase para problemas",
    "priority": "HIGH"
  }' \
  http://localhost:8000/daemon/tasks/add

# Resetar métricas
curl -X POST -u usuario:senha http://localhost:8000/daemon/reset-metrics
```

**Veja mais detalhes em**: [DAEMON_USER_GUIDE.md](./DAEMON_USER_GUIDE.md)

---

## 💬 Chat/Conversação

### Endpoint de Chat

```bash
curl -X POST -u usuario:senha \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, como você está?",
    "context": {}
  }' \
  http://localhost:8000/api/omnimind/chat
```

### Mensagens (Polling)

```bash
# Obter mensagens pendentes
curl -u usuario:senha http://localhost:8000/api/omnimind/messages

# Enviar mensagem
curl -X POST -u usuario:senha \
  -H "Content-Type: application/json" \
  -d '{
    "type": "user_message",
    "content": "Mensagem do usuário"
  }' \
  http://localhost:8000/api/omnimind/messages
```

---

## 🔧 Configuração

### Arquivo de Configuração Principal

**`config/agent_config.yaml`**:

```yaml
model:
  name: "phi:latest"  # Modelo LLM padrão (Microsoft Phi)
  provider: "ollama"
  base_url: "http://localhost:11434"
  temperature: 0.7
  max_tokens: 2048

memory:
  qdrant_url: "http://localhost:6333"
  collection_name: "omnimind_episodes"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

performance:
  max_concurrent_tasks: 1  # Ajustável baseado em RAM
  task_timeout: 300  # 5 minutos
  retry_attempts: 3
```

### Variáveis de Ambiente

```bash
# Credenciais do dashboard
export OMNIMIND_DASHBOARD_USER="seu_usuario"
export OMNIMIND_DASHBOARD_PASS="sua_senha"

# Qdrant
export OMNIMIND_QDRANT_URL="http://localhost:6333"

# Ollama
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="phi:latest"

# CUDA (definir via shell, não em código Python)
export CUDA_HOME=/usr
export CUDA_PATH=/usr
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

# Modo de desenvolvimento
export OMNIMIND_DEV_MODE=true
export LOG_LEVEL=DEBUG
```

---

## 📊 Monitoramento e Observabilidade

### Métricas de Consciência

O sistema coleta 6 métricas reais de consciência:

1. **Φ (Phi)**: Integração de Informação (IIT 3.0)
2. **ICI**: Integrated Coherence Index
3. **PRS**: Panarchic Resonance Score
4. **Anxiety**: Tensão computacional
5. **Flow**: Estado de fluxo cognitivo
6. **Entropy**: Diversidade de estados

**Acessar métricas**:
```bash
# Via API
curl -u usuario:senha http://localhost:8000/api/omnimind/metrics/real

# Via arquivo
cat data/monitor/real_metrics.json
```

### Health Checks

```bash
# Health check geral
curl http://localhost:8000/api/v1/health/

# Health check específico
curl http://localhost:8000/api/v1/health/database
curl http://localhost:8000/api/v1/health/gpu
curl http://localhost:8000/api/v1/health/redis
```

### Logs

```bash
# Logs do backend
tail -f logs/backend.log

# Logs do sistema
tail -f logs/omnimind_boot.log

# Logs de auditoria
tail -f logs/audit_chain.log

# Logs do daemon
tail -f logs/daemon.log
```

---

## 🧪 Testes

### Executar Testes

```bash
# Suite rápida diária (sem slow/chaos)
./scripts/run_tests_fast.sh

# Suite completa semanal (inclui slow/chaos)
./scripts/run_tests_with_defense.sh

# Teste rápido com servidor
./scripts/quick_test.sh
```

**Veja mais detalhes em**: [TESTING_QUICK_START.md](../canonical/TESTING_QUICK_START.md)

---

## 🔐 Segurança

### Autenticação

As credenciais são geradas automaticamente na primeira execução e salvas em `config/dashboard_auth.json` com permissão `600`.

**Regenerar credenciais**:
```bash
rm config/dashboard_auth.json
# Reiniciar servidor para auto-gerar novas credenciais
```

### Auditoria

O sistema mantém uma cadeia de auditoria imutável:

```bash
# Verificar integridade da cadeia
python -c "from src.audit.immutable_audit import verify_chain_integrity; print(verify_chain_integrity())"

# Ver logs de auditoria
cat logs/audit_chain.log
```

---

## 📚 Recursos Adicionais

- [Quick Start Guide](../canonical/QUICK_START.md)
- [Technical Checklist](../canonical/TECHNICAL_CHECKLIST.md)
- [API Troubleshooting](./TROUBLESHOOTING.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)
- [Daemon User Guide](./DAEMON_USER_GUIDE.md)
- [Environment Setup](./ENVIRONMENT_SETUP.md)

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
