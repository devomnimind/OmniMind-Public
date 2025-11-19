# OmniMind Dashboard API

Integra o `OrchestratorAgent` ao dashboard FastAPI com autenticação básica, métricas e controles para MCP/D-Bus.

## Requisitos

- Python 3.12+
- Ambiente virtual configurado (use `source .venv/bin/activate`)
- Dependências instaladas (`pip install -r requirements.txt`)

## Execução local

```bash
cd /home/fahbrain/projects/omnimind
source venv/bin/activate
uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Ambiente seguro

Defina as variáveis de ambiente para proteger os endpoints sensíveis:

```bash
export OMNIMIND_DASHBOARD_USER=dashboard
export OMNIMIND_DASHBOARD_PASS=omnimind
```

As credenciais também são geradas automaticamente ao inicializar o backend e persistidas em `config/dashboard_auth.json` com permissão `600`. Nunca commit esse arquivo; altere o conteúdo manualmente, aplique `chmod 600 config/dashboard_auth.json` e reinicie o serviço para rotacionar as credenciais. O backend consome automaticamente esse arquivo a cada inicialização.

## Endpoints

- `GET /health` – status básico sem autenticação
- `GET /status` – plano atual, progresso, snapshot e métricas do backend + orquestrador
- `GET /snapshot` – força atualização MCP/D-Bus
- `GET /plan` – visão detalhada do plano ativo
- `GET /metrics` – métricas periodicamente agregadas (requests, latências, erros)
- `POST /tasks/orchestrate` – inicia a orquestração de uma nova tarefa (body: `task`, `max_iterations`)
- `POST /dashboard/refresh` – atualiza manualmente o snapshot
- `POST /mcp/execute` – dispara ações MCP manuais (`action`, `path`, `recursive`)
- `POST /dbus/execute` – dispara fluxos D-Bus (`flow`, `media_action`)

Todos os endpoints acima (exceto `/health`) exigem autenticação básica com as variáveis acima.

## Observabilidade & métricas

- Middleware registra latência e taxa de erros por rota.
- Task background `/_metrics_reporter` escreve log resumido a cada 30s.
- Endpoint `/metrics` combina dados do backend e do `OrchestratorAgent`.

## Inicialização unificada

Use o script `scripts/start_dashboard.sh` para levantar backend e frontend juntos via `docker compose up --build` (requer Docker).

```bash
scripts/start_dashboard.sh
```
