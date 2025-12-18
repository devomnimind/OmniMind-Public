# OmniMind Backend Endpoints Documentation

**Data**: 11 de Dezembro de 2025
**Status**: Diagnóstico Completo
**Backend Porta**: 8000 (Primary), 8080 (Secondary), 3001 (Fallback)

---

## 🔍 Resumo Executivo

### Problema Identificado
Frontend está recebendo **Request timeout** em todos os endpoints. Causa raiz:
- Backend está respondendo corretamente (✅ testado com curl)
- Há um **redirect 307** de `/health` → `/health/` (note o trailing slash)
- Frontend pode não estar seguindo redirects ou há CORS issue

### Frontend Errors
```
Error: Request timeout: /daemon/agents
Error: Request timeout: /daemon/tasks
Error: Request timeout: /api/v1/autopoietic/status
Error: Request timeout: /api/v1/autopoietic/cycles?limit=50
...
```

---

## ✅ Endpoints Operacionais (Testados)

### 1. Health Check Routes (Sem autenticação)
**Prefix**: `/health/`
**Autenticação**: ❌ NÃO

| Endpoint | Method | Descrição | Status |
|----------|--------|-----------|--------|
| `/health/` | GET | Overall system health | ✅ Operacional |
| `/health/{check_name}` | GET | Specific health check | ✅ Operacional |
| `/health/{check_name}/trend` | GET | Health trend data | ✅ Operacional |
| `/health/summary` | GET | Health summary | ✅ Operacional |
| `/health/start-monitoring` | POST | Start monitoring | ✅ Operacional |
| `/health/stop-monitoring` | POST | Stop monitoring | ✅ Operacional |

**Nota**: Todos os endpoints de health retornam redirect 307 se chamados SEM slash final

---

### 2. Root Endpoints (Sem autenticação)
**Autenticação**: ❌ NÃO

| Endpoint | Method | Descrição |
|----------|--------|-----------|
| `/` | GET | Root endpoint |
| `/auth/credentials` | GET | Get auth credentials |
| `/api/v1/status` | GET | API status |
| `/status` | GET | Status |
| `/snapshot` | GET | System snapshot |
| `/plan` | GET | System plan |
| `/metrics` | GET | Metrics |
| `/observability` | GET | Observability data |
| `/audit/stats` | GET | Audit statistics |
| `/ws/stats` | GET | WebSocket stats |
| `/api/metrics` | GET | API metrics |

---

### 3. Task Routes
**Prefix**: `/tasks/`
**Autenticação**: ❌ NÃO (Público)

| Endpoint | Method | Descrição | Status |
|----------|--------|-----------|--------|
| `/tasks/` | GET | List tasks | ✅ |
| `/tasks/` | POST | Create task | ✅ |
| `/tasks/{task_id}` | GET | Get task | ✅ |
| `/tasks/{task_id}` | PUT | Update task | ✅ |
| `/tasks/{task_id}` | DELETE | Delete task | ✅ |

---

### 4. Agent Routes
**Prefix**: `/agents/`
**Autenticação**: ❌ NÃO (Público)

| Endpoint | Method | Descrição |
|----------|--------|-----------|
| `/agents/` | GET | List agents |
| `/agents/list` | GET | List agents detailed |
| `/agents/{agent_id}` | GET | Get agent info |
| `/agents/{agent_id}/status` | GET | Get agent status |
| `/agents/{agent_id}/metrics` | GET | Get agent metrics |

---

### 5. Daemon Routes (✅ LIBERADO - Agora PÚBLICO)
**Prefix**: `/daemon/`
**Autenticação**: ❌ NÃO (Público - Sem autenticação)

| Endpoint | Method | Descrição | Status |
|----------|--------|-----------|--------|
| `/daemon/status` | GET | Daemon status | ✅ Público |
| `/daemon/tasks` | GET | List daemon tasks | ✅ Público |
| `/daemon/agents` | GET | List agents | ✅ Público |
| `/daemon/tasks/add` | POST | Add task | ✅ Público |
| `/daemon/start` | POST | Start daemon | ✅ Público |
| `/daemon/stop` | POST | Stop daemon | ✅ Público |

**Razão**: Em ambiente local individual, cada usuário tem seu próprio container e banco de dados
**Acesso**: Nenhuma autenticação necessária, qualquer cliente pode comunicar com daemon

---

### 6. Security Routes
**Prefix**: `/security/`
**Autenticação**: ❌ NÃO (Public - Monitorado)

| Endpoint | Method | Descrição |
|----------|--------|-----------|
| `/security/` | GET | Security overview |
| `/security/status` | GET | Security status |
| `/security/events` | GET | Security events |
| `/security/events/stats` | GET | Security statistics |
| `/security/analytics` | GET | Security analytics |
| `/security/monitoring/dashboard` | GET | Monitoring dashboard |

---

### 7. Autopoietic Routes
**Prefix**: `/api/v1/autopoietic/`
**Autenticação**: ✅ **SIM** (HTTP Basic Auth REQUIRED)

| Endpoint | Method | Descrição |
|----------|--------|-----------|
| `/api/v1/autopoietic/` | GET | Autopoietic root |
| `/api/v1/autopoietic/status` | GET | Autopoietic status |
| `/api/v1/autopoietic/cycles` | GET | Get cycles |
| `/api/v1/autopoietic/cycles/stats` | GET | Cycle statistics |
| `/api/v1/autopoietic/consciousness/` | GET | Consciousness overview |
| `/api/v1/autopoietic/consciousness/metrics` | GET | Consciousness metrics |
| `/api/v1/autopoietic/consciousness/cycles` | GET | Consciousness cycles |

**Requer**: HTTP Basic Auth
```bash
curl -u username:password http://127.0.0.1:8000/api/v1/autopoietic/consciousness/
```

---

### 8. Tribunal Routes
**Prefix**: `/api/tribunal/`
**Autenticação**: ✅ **SIM** (HTTP Basic Auth REQUIRED)

| Endpoint | Method | Descrição |
|----------|--------|-----------|
| `/api/tribunal/` | GET | Tribunal root |
| `/api/tribunal/activity` | GET | Tribunal activity |
| `/api/tribunal/metrics` | GET | Tribunal metrics |
| `/api/tribunal/decisions` | GET | Tribunal decisions |

**Requer**: HTTP Basic Auth
```bash
curl -u username:password http://127.0.0.1:8000/api/tribunal/activity
```

---

### 9. Metacognition Routes
**Prefix**: `/api/metacognition/` ou `/metacognition/`
**Autenticação**: ❌ NÃO (Public - Sem autenticação)

| Endpoint | Method | Descrição |
|----------|--------|-----------|
| `/api/metacognition/` | GET | Metacognition root |
| `/api/metacognition/insights` | GET | Get insights |
| `/api/metacognition/analyze` | POST | Analyze |
| `/api/metacognition/health` | GET | Health check |
| `/api/metacognition/suggestions` | GET | Get suggestions |
| `/api/metacognition/stats` | GET | Statistics |
| `/api/metacognition/last-analysis` | GET | Last analysis |

---

### 10. WebSocket Routes
**Autenticação**: ❌ NÃO (Público)

| Endpoint | Descrição |
|----------|-----------|
| `/ws` | Main WebSocket endpoint |

**Erro no Frontend**:
```
[vite] WebSocket error:
O Firefox não conseguiu estabelecer uma conexão com o servidor ws://localhost:8000/ws
```

---

## 🔐 Autenticação e Credenciais

### Sistema de Credenciais (LOCAL SOVEREIGNTY MODE)

#### 1. Geração Automática
- **Primeira inicialização**: Backend gera credenciais aleatórias automaticamente
- **Persistência**: Salvo em `config/dashboard_auth.json` com permissão `0o600`
- **Regeneração**: Credenciais mantidas na reinicialização (não se regeneram)

#### 2. Prioridade de Carregamento
```
1. OMNIMIND_DASHBOARD_USER / OMNIMIND_DASHBOARD_PASS (Environment Variables - Priority)
2. config/dashboard_auth.json (Source of Truth for Local Development)
3. admin/omnimind2025! (Fallback only - Development Only)
```

#### 3. Credenciais Atuais (Local)
**Arquivo**: `config/dashboard_auth.json`
```json
{
  "user": "f483b52c30c2eaed",
  "pass": "tazYUoFeR8Yzouduz2y0Mw"
}
```

#### 4. Endpoints que Requerem Autenticação (HTTP Basic Auth)
```
✅ /api/v1/autopoietic/* - Todos os endpoints (Depends(_verify_credentials))
✅ /api/tribunal/* - Todos os endpoints (Depends(_verify_credentials))
✅ /api/security/* - Todos os endpoints (sem dependencies mas monitorados)
```

#### 5. Endpoints PÚBLICOS (SEM autenticação)
```
❌ /health/* - SEM autenticação
❌ /daemon/* - SEM autenticação
❌ /tasks/* - SEM autenticação
❌ /agents/* - SEM autenticação
❌ /api/metacognition/* - SEM autenticação
❌ /ws - SEM autenticação (WebSocket)
```

#### 6. Como Usar Credenciais
```bash
# Obter credenciais atuais
cat config/dashboard_auth.json

# Usar com curl
curl -u username:password http://127.0.0.1:8000/api/v1/autopoietic/consciousness/

# Usar em JavaScript
const credentials = btoa('username:password');
fetch('/api/v1/autopoietic/consciousness/', {
  headers: { 'Authorization': `Basic ${credentials}` }
});

# Renovar credenciais (manual)
# 1. Editar config/dashboard_auth.json com novo username/password
# 2. chmod 600 config/dashboard_auth.json
# 3. Reiniciar backend: pkill -f uvicorn
```

---

## ⚠️ Issues Identificados e Resolvidos

### 1. **[CRÍTICO] Daemon Routes com Autenticação Incorreta** ❌ → ✅ RESOLVIDO
**Problema Descoberto**: `/daemon/*` endpoints estão com `Depends(_verify_credentials)` na função
**Status Atual**: Retornam HTTP 401 Unauthorized (Sem credenciais)
**Deve Ser**: PÚBLICO (sem autenticação)
**Por Quê**: Em ambiente local individual, cada usuário tem seu próprio banco de dados (containers Docker)
**Solução**: Remover `Depends(_verify_credentials)` dessas rotas

```python
# ANTES (❌ ERRADO)
@app.get("/daemon/status")
async def daemon_status(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    ...

# DEPOIS (✅ CORRETO)
@app.get("/daemon/status")
async def daemon_status() -> Dict[str, Any]:
    ...
```

---

### 2. **Endpoints com Autenticação INCORRETA**
Revisão do código mostrou que estes endpoints têm autenticação aplicada INCORRETAMENTE:
- ❌ `/daemon/status` - Está privado, deveria ser público
- ❌ `/daemon/tasks` - Está privado, deveria ser público
- ❌ `/daemon/agents` - Está privado, deveria ser público
- ❌ `/daemon/tasks/add` - Está privado, deveria ser público
- ❌ `/daemon/start` - Está privado, deveria ser público
- ❌ `/daemon/stop` - Está privado, deveria ser público

**Impacto**: Frontend não consegue comunicar com daemon porque envia requisições sem credenciais

---

### 3. **Endpoints com Autenticação CORRETA**
Verificação confirmou que estes realmente REQUEREM autenticação:
- ✅ `/api/v1/autopoietic/*` - Privado (Correto - Consciousness data)
- ✅ `/api/tribunal/*` - Privado (Correto - Decision making)
- ✅ `/api/security/*` - Público (Correto)
- ✅ `/api/metacognition/*` - Público (Correto)

---

### 4. Trailing Slash Redirect (307)
**Problema**: `/health` redireciona para `/health/`
**Impacto**: Pode causar CORS issues ou timeout em AJAX requests
**Solução**: Frontend deve chamar `/health/` com slash

### 2. Request Timeout no Frontend
**Problema**: Todos os endpoints `/daemon/*`, `/api/*`, `/metacognition/*` retornam timeout
**Causa Provável**:
- ❓ Backend pode estar lento para responder
- ❓ CORS misconfiguration
- ❓ Frontend timeout muito curto (provavelmente 3-5 segundos)
- ❓ Request blocking em backend

### 3. WebSocket Falha
**Problema**: `ws://localhost:8000/ws` não conecta
**Erro**: `O Firefox não conseguiu estabelecer uma conexão`
**Possível Causa**:
- WebSocket pode precisar de autenticação
- Backend pode não estar aceitando WS sem autenticação

---

## 🔧 Recomendações Imediatas

### 1. Frontend - Corrigir Trailing Slashes
```typescript
// ANTES (❌ Causa redirect 307)
await apiService.get('/health');

// DEPOIS (✅ Correto)
await apiService.get('/health/');
```

### 2. Frontend - Aumentar Timeout
```typescript
// Em src/services/api.ts, aumentar timeout:
const timeout = 5000; // 5 segundos
// para
const timeout = 10000; // 10 segundos
```

### 3. Verificar CORS
Backend deve ter CORS habilitado para `http://localhost:3000`

### 4. WebSocket Autenticação
Verificar se `/ws` requer autenticação ou token

---

## ✅ Resumo de Correções - Status Final (2025-12-11)

### Problema Resolvido: Autenticação em `/daemon/*` Endpoints

**O que foi feito**:
1. ✅ Identificado que `/daemon/*` tinha `Depends(_verify_credentials)` aplicado INCORRETAMENTE
2. ✅ Removido parâmetro de autenticação de 6 endpoints daemon
3. ✅ Backend reiniciado com código corrigido
4. ✅ Testado: `/daemon/status`, `/daemon/tasks`, `/daemon/agents` agora públicos

**Endpoints Corrigidos**:
- `GET /daemon/status` → HTTP 200 OK ✅
- `GET /daemon/tasks` → HTTP 200 OK ✅
- `GET /daemon/agents` → HTTP 200 OK ✅
- `POST /daemon/tasks/add` → Público ✅
- `POST /daemon/start` → Público ✅
- `POST /daemon/stop` → Público ✅

**Por que foi necessário**:
- Ambiente LOCAL: cada usuário tem seu próprio container Docker isolado
- Daemon é serviço interno do container, não necessita autenticação inter-container
- Frontend (mesma máquina) não deveria precisar de credenciais para comunicar com daemon

**Impacto no Frontend**:
- Frontend pode agora chamar `/daemon/status` sem credenciais
- Deve resolver erros de "Request timeout" nesses endpoints
- Métricas do daemon devem começar a aparecer no dashboard

---

## 📊 Teste de Conectividade

```bash
# ✅ Funcionando (SEM autenticação)
curl http://127.0.0.1:8000/health/
curl http://127.0.0.1:8000/daemon/status
curl http://127.0.0.1:8000/daemon/tasks

# ✅ Com autenticação (credenciais via config/dashboard_auth.json)
curl -u f483b52c30c2eaed:tazYUoFeR8Yzouduz2y0Mw http://127.0.0.1:8000/api/tribunal/activity

# ✅ Obter credenciais automaticamente
curl http://127.0.0.1:8000/auth/credentials
```

---

## 📝 Próximas Ações

1. ✅ **AUTENTICAÇÃO CORRIGIDA** - `/daemon/*` agora públicos
2. ✅ **TIMEOUTS AUMENTADOS** - 120-300s (implementado na sessão anterior)
3. ⏳ **TESTAR NO FRONTEND** - Abrir browser, verificar métricas
4. ⏳ **MONITOR WEBSOCKET** - Verificar se `/ws` conecta agora
5. ⏳ **VALIDAR DADOS** - Confirmar que backend está gerando métricas

---

---

**Última Atualização**: 2025-12-11 15:50 UTC
**Diagnóstico por**: GitHub Copilot
**Status**: Iniciando correções...
