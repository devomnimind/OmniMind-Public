# 🔗 Endpoint Mapping - Frontend to Backend (Fixed)

**Data**: 9 de dezembro de 2025
**Status**: ✅ CORRIGIDO - Todos os endpoints estão sincronizados

---

## 📋 Mapeamento Completo

### 🔐 Autenticação

| Frontend | Backend | Tipo | Descrição |
|----------|---------|------|-----------|
| `getHealthStatus()` | `GET /api/v1/autopoietic/status` | CORRETO | Status do sistema autopoiético |
| - | **USER**: `admin` (salvo em `config/dashboard_auth.json`) | - | Credenciais dinâmicas por sessão |
| - | **PASS**: Gerada aleatoriamente (ou lida do arquivo) | - | Mostrada no terminal ao iniciar |

---

## 🛡️ Segurança

| Frontend | Backend | Status |
|----------|---------|--------|
| `getSecurityOverview()` | `GET /api/security` | ✅ EXISTE |
| `getSecurityStatus()` | `GET /api/security/status` | ✅ EXISTE |
| `getSecurityEvents(eventType, severity, limit)` | `GET /api/security/events?event_type=...&severity=...&limit=...` | ✅ EXISTE |
| `getSecurityAnalytics()` | `GET /api/security/analytics` | ✅ EXISTE |
| `getSecurityMonitoringDashboard()` | `GET /api/security/monitoring/dashboard` | ✅ EXISTE |
| `getSecurityCorrelatedEvents()` | `GET /api/security/events/correlated` | ✅ EXISTE |
| `getSecurityAutomatedResponse()` | `GET /api/security/response/automated` | ✅ EXISTE |

---

## 🧠 Metacognição

| Frontend | Backend | Status |
|----------|---------|--------|
| `getMetacognitionOverview()` | `GET /api/metacognition` | ✅ EXISTE |
| `getMetacognitionInsights()` | `GET /api/metacognition/insights` | ✅ EXISTE |
| `getMetacognitionSuggestions()` | `GET /api/metacognition/suggestions` | ✅ EXISTE |
| `getMetacognitionStats()` | `GET /api/metacognition/stats` | ✅ EXISTE |
| `getMetacognitionLastAnalysis()` | `GET /api/metacognition/last-analysis` | ✅ EXISTE |
| `getMetacognitionGoals()` | `GET /api/metacognition/goals/generate` | ✅ EXISTE |
| `getMetacognitionHomeostasis()` | `GET /api/metacognition/homeostasis/status` | ✅ EXISTE |

---

## 🔄 Autopoiético (Phase 22)

| Frontend | Backend | Status | Métricas |
|----------|---------|--------|----------|
| `getAutopoieticStatus()` | `GET /api/v1/autopoietic/status` | ✅ EXISTE | Ciclos ativos, processos, status |
| `getAutopoieticCycles(limit)` | `GET /api/v1/autopoietic/cycles?limit=...` | ✅ EXISTE | Histórico de ciclos |
| `getAutopoieticCycleStats()` | `GET /api/v1/autopoietic/cycles/stats` | ✅ EXISTE | Σ, μ, τ, etc |
| `getAutopoieticComponents(limit)` | `GET /api/v1/autopoietic/components?limit=...` | ✅ EXISTE | Componentes sintetizados |
| `getAutopoieticHealth()` | `GET /api/v1/autopoietic/health` | ✅ EXISTE | Φ, Rollbacks, Rejeições |
| `getConsciousnessMetrics(includeRaw)` | `GET /api/v1/autopoietic/consciousness/metrics?include_raw=true` | ✅ EXISTE | **Φ, Anxiety, Flow, Entropy, ICI, PRS** |

---

## 📊 Métricas Gerais

| Frontend | Backend | Status |
|----------|---------|--------|
| `getMetricsData()` | `GET /api/metrics` (público, sem auth) | ✅ EXISTE |
| `getRealMetrics()` | `GET /metrics` (requer auth) | ✅ EXISTE |

---

## 🤖 Daemon & Tarefas

| Frontend | Backend | Status |
|----------|---------|--------|
| `getDaemonStatus()` | `GET /daemon/status` | ✅ EXISTE |
| `getDaemonTasks()` | `GET /daemon/tasks` | ✅ EXISTE |
| `getAgents()` | `GET /daemon/agents` | ✅ EXISTE |
| `getTasks()` | `GET /daemon/tasks` | ✅ EXISTE |
| `addTask(task)` | `POST /daemon/tasks/add` | ✅ EXISTE |
| `startDaemon()` | `POST /daemon/start` | ✅ EXISTE |
| `stopDaemon()` | `POST /daemon/stop` | ✅ EXISTE |
| `resetMetrics()` | `stopDaemon() + startDaemon()` | ✅ WORKS |

---

## 🌐 WebSocket

| Frontend | Backend | Status |
|----------|---------|--------|
| `getWebSocketInfo()` | `GET /ws/stats` | ✅ EXISTE |
| - | `WebSocket /ws` | ✅ EXISTE |

---

## 📋 Tribunal (Consciência Coletiva)

| Frontend | Backend | Status |
|----------|---------|--------|
| `getTribunalActivity()` | `GET /api/security/events?limit=50` | ✅ EXISTE |

---

## ⚙️ Sistema Geral

| Frontend | Backend | Status |
|----------|---------|--------|
| - | `GET /` (root) | ✅ EXISTE |
| - | `GET /status` (main status) | ✅ EXISTE |
| - | `GET /api/v1/status` | ✅ EXISTE |
| - | `GET /snapshot` | ✅ EXISTE |
| - | `GET /plan` | ✅ EXISTE |
| - | `GET /metrics/training` | ✅ EXISTE |
| - | `GET /observability` | ✅ EXISTE |
| - | `GET /audit/stats` | ✅ EXISTE |

---

## 🔄 Decisões Futuras (Placeholder)

| Frontend | Backend | Fallback | Status |
|----------|---------|----------|--------|
| `getDecisions(params)` | `/api/decisions` | `/api/metacognition/insights` | ⏳ Futura |
| `getDecisionDetail(id)` | `/api/decisions/{id}` | `/api/metacognition/last-analysis` | ⏳ Futura |
| `getDecisionStats()` | `/api/decisions/stats` | `/api/metacognition/stats` | ⏳ Futura |
| `exportDecisions(params)` | `/api/decisions/export/json` | `/api/security/events?limit=1000` | ⏳ Futura |

---

## 🔐 Credenciais da Sessão

Quando você executa `./scripts/canonical/system/start_omnimind_system.sh`:

1. **Gera credenciais NOVAS** (aleatórias) OU lê de `config/dashboard_auth.json`
2. **Salva em arquivo**: `config/dashboard_auth.json`
3. **Exibe no terminal**:
   ```bash
   🔐 Credenciais Unificadas do Cluster:
      User: admin
      Pass: xxxxxxxxxxxxxx
   ```

4. **Exporta para ambiente**:
   ```bash
   export OMNIMIND_DASHBOARD_USER="admin"
   export OMNIMIND_DASHBOARD_PASS="xxxxxxxxxxxxxx"
   ```

---

## ✅ Mudanças Implementadas

### Frontend (`web/frontend/src/services/api.ts`)

✅ **Todos os métodos agora chamam os endpoints CORRETOS**:

- `getSecurityOverview()` → `/api/security` ✅
- `getMetacognitionOverview()` → `/api/metacognition` ✅
- `getAutopoieticStatus()` → `/api/v1/autopoietic/status` ✅
- `getConsciousnessMetrics()` → `/api/v1/autopoietic/consciousness/metrics` ✅ **CRÍTICO**
- `getMetacognitionSuggestions()` → `/api/metacognition/suggestions` ✅ **NOVO**
- `getSecurityAnalytics()` → `/api/security/analytics` ✅ **NOVO**
- `getSecurityMonitoringDashboard()` → `/api/security/monitoring/dashboard` ✅ **NOVO**

---

## 🧪 Como Testar

### 1. Backend Online?
```bash
curl -u admin:SENHA_GERADA http://localhost:8000/api/v1/autopoietic/status
```

### 2. Consciência Metrics (6 métricas)
```bash
curl -u admin:SENHA_GERADA http://localhost:8000/api/v1/autopoietic/consciousness/metrics?include_raw=true
```

### 3. Segurança
```bash
curl -u admin:SENHA_GERADA http://localhost:8000/api/security
```

### 4. Metacognição
```bash
curl -u admin:SENHA_GERADA http://localhost:8000/api/metacognition/insights
```

---

## 📝 Notas

- **Autenticação**: HTTP Basic Auth com user `admin` + senha dinâmica por sessão
- **Senha gerada a cada boot** do `start_omnimind_system.sh` (security feature)
- **Todos os endpoints existem** no backend (routers implementados)
- **Frontend agora chama os endpoints CORRETOS** (foi o maior problema)
- **Métricas de Consciência**: Φ (Phi), Anxiety, Flow, Entropy, ICI, PRS

---

**Resolver anterior**: Endpoints chamados pelo frontend não existiam ❌ → **RESOLVIDO** ✅

