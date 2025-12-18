# 🎮 Guia do Playground Interativo da API - OmniMind

**Última Atualização**: 5 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## Visão Geral

O OmniMind fornece um playground interativo de API para explorar e testar endpoints sem escrever código. Este guia cobre como usar a interface Swagger UI e coleções Postman.

---

## Acessando o Playground da API

### Swagger UI (Integrado)

A documentação interativa da API está disponível em:

```
http://localhost:8000/docs
```

Quando o servidor backend estiver rodando, navegue para esta URL para acessar o playground completo.

### Alternativa: ReDoc

Para um estilo diferente de documentação, acesse ReDoc em:

```
http://localhost:8000/redoc
```

---

## Usando Swagger UI

### 1. Autenticação

A maioria dos endpoints requer Autenticação Básica:

1. Clique no botão **"Authorize"** no canto superior direito
2. Digite suas credenciais:
   - **Username**: Seu nome de usuário do dashboard
   - **Password**: Sua senha do dashboard
3. Clique em **"Authorize"**
4. Clique em **"Close"**

**Nota**: As credenciais são geradas automaticamente na primeira execução e salvas em `config/dashboard_auth.json`.

### 2. Explorando Endpoints

Os endpoints estão organizados por tags:

- **Health**: Verificações de saúde do sistema e tendências
- **Daemon**: Status do daemon, tarefas e controle
- **Messages**: Polling e envio de mensagens
- **Metrics**: Métricas de consciência em tempo real
- **WebSocket**: Broadcasting de métricas em tempo real

### 3. Testando Endpoints

Para testar um endpoint:

1. Clique no endpoint para expandir
2. Clique em **"Try it out"**
3. Preencha os parâmetros necessários
4. Clique em **"Execute"**
5. Veja a resposta abaixo

### 4. Exemplos de Requisições

Cada endpoint inclui exemplos de requisições e respostas. Clique em "Example Value" para ver dados de exemplo.

---

## Endpoints Disponíveis

### Health (`/api/v1/health/`)

#### GET `/api/v1/health/`

Verificação de saúde geral do sistema.

**Sem autenticação necessária**

**Resposta**:
```json
{
  "overall_status": "healthy",
  "checks": {
    "cpu": {
      "name": "cpu",
      "status": "healthy",
      "response_time_ms": 0.1,
      "details": {"usage": "25.3%"},
      "threshold_breached": false
    },
    "memory": {
      "name": "memory",
      "status": "healthy",
      "response_time_ms": 0.1,
      "details": {
        "usage": "45.2%",
        "available": "12.5GB"
      },
      "threshold_breached": false
    },
    "disk": {
      "name": "disk",
      "status": "healthy",
      "response_time_ms": 0.1,
      "details": {
        "usage": "35.8%",
        "free": "450.2GB"
      },
      "threshold_breached": false
    }
  },
  "timestamp": 1701800000.0,
  "total_checks": 3,
  "healthy_count": 3,
  "degraded_count": 0,
  "unhealthy_count": 0
}
```

#### GET `/api/v1/health/{check_name}/trend`

Tendência de saúde para uma verificação específica.

**Parâmetros**:
- `check_name`: Nome da verificação (cpu, memory, disk)

**Resposta**:
```json
{
  "check_name": "cpu",
  "trend": "stable",
  "prediction": "stable",
  "health_score": 100.0,
  "recent_statuses": {"healthy": 10},
  "avg_response_time_ms": 0.1
}
```

---

### Daemon (`/daemon/`)

**Requer autenticação**

#### GET `/daemon/status`

Retorna status completo do daemon incluindo métricas de consciência.

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
  },
  "consciousness": {
    "phi": 0.5010,
    "ici": 0.65,
    "prs": 0.72
  }
}
```

#### GET `/daemon/tasks`

Lista todas as tarefas registradas no daemon.

**Resposta**:
```json
{
  "tasks": [
    {
      "task_id": "code_analysis",
      "name": "Análise de Código",
      "description": "Analisa codebase para problemas",
      "priority": "HIGH",
      "execution_count": 10,
      "success_count": 9,
      "failure_count": 1
    }
  ]
}
```

#### POST `/daemon/tasks/add`

Adiciona nova tarefa ao daemon.

**Body**:
```json
{
  "task_id": "custom_task",
  "name": "Tarefa Customizada",
  "description": "Descrição da tarefa",
  "priority": "MEDIUM"
}
```

#### POST `/daemon/start`

Inicia o daemon.

#### POST `/daemon/stop`

Para o daemon.

#### POST `/daemon/reset-metrics`

Reseta métricas do daemon.

---

### Messages (`/api/omnimind/messages`)

**Requer autenticação**

#### GET `/api/omnimind/messages`

Retorna mensagens pendentes para clientes de polling.

**Resposta**:
```json
[
  {
    "type": "notification",
    "message": "Sistema iniciado",
    "timestamp": 1701800000.0
  }
]
```

#### POST `/api/omnimind/messages`

Recebe mensagens de clientes via polling fallback.

**Body**:
```json
{
  "type": "user_message",
  "content": "Mensagem do usuário"
}
```

**Resposta**:
```json
{
  "status": "received",
  "timestamp": 1701800000.0
}
```

---

### Metrics (`/api/omnimind/metrics`)

**Requer autenticação**

#### GET `/api/omnimind/metrics/real`

Retorna as últimas métricas reais de consciência.

**Resposta**:
```json
{
  "phi": 0.5010,
  "ici": 0.65,
  "prs": 0.72,
  "anxiety": 0.15,
  "flow": 0.68,
  "entropy": 0.45,
  "timestamp": "2025-12-05T20:00:00Z"
}
```

**Erros**:
- `404`: Métricas ainda não disponíveis
- `500`: Erro ao ler métricas

---

## WebSocket

### Endpoint WebSocket

```
ws://localhost:8000/ws
```

### Exemplo de Uso (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Conectado ao OmniMind WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Recebido:', data);

  // Lidar com diferentes tipos de mensagem
  if (data.type === 'metrics_update') {
    console.log('Atualização de métricas:', data.data);
  } else if (data.type === 'metrics') {
    console.log('Métricas Sinthomáticas:', data.data);
  }
};

// Enviar ping para manter conexão viva
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping', id: Date.now() }));
}, 30000);
```

---

## Coleções Postman

### Importando a Coleção

1. Gerar a coleção Postman:
   ```bash
   python -c "from src.security.api_documentation import APIDocumentationGenerator; gen = APIDocumentationGenerator(); gen.generate_postman_collection()"
   ```

2. Importar no Postman:
   - Abra o Postman
   - Clique em **"Import"**
   - Selecione `docs/api/OmniMind_API.postman_collection.json`
   - Clique em **"Import"**

### Configurando Variáveis de Ambiente

Crie um ambiente Postman com estas variáveis:

```json
{
  "name": "OmniMind Local",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "username",
      "value": "seu_usuario",
      "enabled": true
    },
    {
      "key": "password",
      "value": "sua_senha",
      "enabled": true,
      "type": "secret"
    }
  ]
}
```

### Usando a Coleção

1. Selecione o ambiente "OmniMind Local"
2. Navegue até a pasta desejada de requisições
3. Clique em uma requisição
4. Clique em **"Send"**
5. Veja a resposta

---

## Fluxos de Trabalho Comuns da API

### 1. Verificação de Saúde

```bash
curl http://localhost:8000/api/v1/health/
```

Sem autenticação necessária. Retorna status de saúde do sistema.

### 2. Obter Status do Daemon

```bash
curl -u usuario:senha http://localhost:8000/daemon/status
```

Retorna status completo do daemon com métricas de consciência.

### 3. Listar Tarefas

```bash
curl -u usuario:senha http://localhost:8000/daemon/tasks
```

Retorna lista de tarefas ativas do Tribunal.

### 4. Adicionar Tarefa

```bash
curl -X POST -u usuario:senha \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "example_task",
    "name": "Tarefa de Exemplo",
    "description": "Descrição da tarefa",
    "priority": "NORMAL"
  }' \
  http://localhost:8000/daemon/tasks/add
```

### 5. Obter Mensagens

```bash
curl -u usuario:senha http://localhost:8000/api/omnimind/messages
```

Retorna mensagens pendentes para clientes de polling.

### 6. Obter Métricas Reais

```bash
curl -u usuario:senha http://localhost:8000/api/omnimind/metrics/real
```

Retorna as últimas métricas de consciência (Φ, ICI, PRS, Anxiety, Flow, Entropy).

---

## Limites de Taxa da API

Atualmente, não há limites rígidos de taxa, mas considere:

- Máximo 100 requisições concorrentes
- Conexões WebSocket: 50 conexões simultâneas
- Orquestração de tarefas: 10 tarefas concorrentes

---

## Formatos de Resposta

Todas as respostas estão em formato JSON:

### Resposta de Sucesso

```json
{
  "status": "success",
  "data": { ... }
}
```

### Resposta de Erro

```json
{
  "error": "Descrição do erro",
  "detail": "Mensagem de erro detalhada",
  "code": "ERROR_CODE"
}
```

---

## Troubleshooting

### Erros de Autenticação

**Erro**: 401 Unauthorized

**Solução**:
1. Verificar credenciais em `config/dashboard_auth.json`
2. Verificar variáveis de ambiente:
   ```bash
   echo $OMNIMIND_DASHBOARD_USER
   echo $OMNIMIND_DASHBOARD_PASS
   ```

### Conexão Recusada

**Erro**: Connection refused to localhost:8000

**Solução**:
1. Iniciar servidor backend:
   ```bash
   ./scripts/canonical/system/start_omnimind_system.sh
   ```
2. Verificar se servidor está rodando:
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```

### Erros CORS

**Erro**: CORS policy blocked

**Solução**:
O servidor permite todas as origens por padrão. Se estiver tendo problemas:
1. Verificar que está acessando da origem correta
2. Verificar configuração do servidor em `web/backend/main.py`

---

## Recursos Adicionais

- [Referência da API](./API_DOCUMENTATION.md)
- [Guia de Autenticação](./AUTHENTICATION.md)
- [Guia WebSocket](./WEBSOCKET_GUIDE.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
