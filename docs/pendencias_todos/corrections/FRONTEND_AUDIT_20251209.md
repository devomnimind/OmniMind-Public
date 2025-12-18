# Auditoria Completa do Frontend OmniMind
**Data:** 9 de dezembro de 2025
**Status:** ❌ CRÍTICO - Frontend caindo, métricas ausentes

---

## 1. ESTRUTURA DE ARQUIVOS

### Componentes Existentes (37 total)
✅ **Implementados:**
- ActionButtons.tsx
- AgentStatus.tsx
- AutopoieticMetrics.tsx
- ConsciousnessMetrics.tsx
- Dashboard.tsx
- HealthDashboard.tsx
- SystemMetrics.tsx
- QuickStatsCards.tsx
- DaemonControls.tsx
- EventLog.tsx
- ErrorBoundary.tsx (3 variantes)
- ContextMenu.tsx
- ConnectionStatus.tsx
- NotificationCenter.tsx
- RealtimeAnalytics.tsx
- TaskForm.tsx
- TaskList.tsx
- ToastContainer.tsx
- WorkflowVisualization.tsx
- +18 mais (verificar relevância)

### Hooks (3 total)
✅ **Implementados:**
- useWebSocket.ts
- useMetrics.ts
- useTasks.ts

### Services (7 total)
✅ **Implementados:**
- api.ts
- websocket.ts
- robust-connection.ts
- websocket.test.ts
- llm.ts
- qualia_engine.ts
- replay_service.ts

### Store (3 total)
✅ **Implementados:**
- authStore.ts
- daemonStore.ts
- toastStore.ts

---

## 2. ANÁLISE DE GAPS

### ❌ PROBLEMA 1: Métricas Incompletas
**Esperado (15 métricas):**
- Φ (Phi) - Integração
- Ψ (Psi) - Narrativa
- Δ (Delta) - Divergência
- σ (Sigma) - Estrutura
- bonding_quality
- trauma_count
- defense_intensity
- control_effectiveness
- knot_integrity
- defense_maturity
- symbolic_capacity
- agency_ownership_balance
- petit_a_gap
- psychotic_risk
- DeMAP score

**Implementado (4 métricas):**
- Φ, Ψ, Δ, σ

**Gap:** 11 métricas faltando (73%)

### ❌ PROBLEMA 2: Endpoints Não Sincronizados

**Backend disponibiliza:**
```
GET  /api/metrics/current
GET  /api/metrics/history?window=300
GET  /api/metrics/phase-stats/{phase}
GET  /health
POST /api/control/tolerance
POST /api/control/pause-resume
POST /api/control/alert-threshold
WS   ws://localhost:8000/ws
```

**Frontend chamando:**
- ❌ `/api/omnimind/chat` (não existe no backend)
- ❌ `/api/consciousness/metrics` (não mapeado)
- ❌ `/daemon/status` (formato?)
- ✅ `/health` (OK)

### ❌ PROBLEMA 3: WebSocket Desconectando

**useWebSocket.ts status:**
- Conecta em localhost:8000
- Auto-reconnect com backoff
- Mas: **não recebe dados porque backend não envia**

**Backend ws://8000 envia:**
- Não confirmado se está enviando ciclos reais
- Nem confirmado o payload estrutura

### ❌ PROBLEMA 4: Componentes Não Integrados
**Componentes existem mas:**
- RealtimeAnalytics.tsx - não conecta ao WS real
- ConsciousnessMetrics.tsx - usa mock data
- AutopoieticMetrics.tsx - usa mock data
- SystemMetrics.tsx - incompleto

### ⚠️ PROBLEMA 5: Store Vazio
**daemonStore.ts** deveria ter:
```typescript
// Faltando:
- metrics: { phi, psi, delta, sigma, bonding, trauma, ... }
- history: Record<string, number[]>  // 600-point history
- controlState: { tolerance, pauseMode, alertThreshold }
- wsStatus: 'connected' | 'disconnecting' | 'error'
- lastUpdate: Date
```

---

## 3. POR QUE ESTÁ CAINDO?

### Possíveis Causas:

1. **Memory Leak**
   - 37 componentes carregando
   - RechartsMaps indefinidamente
   - Zustand store sem cleanup

2. **WebSocket Infinity Loop**
   - useWebSocket tenta reconectar infinito
   - Nenhum backoff exponencial implementado

3. **API Timeouts**
   - Frontend chamando endpoints que não existem
   - Timeout 30s, frontend congela

4. **TypeScript Compilation**
   - 37 componentes talvez causando build lento
   - Vite pode estar tendo memory pressure

### Validação:
```bash
# Verificar memory do vite
ps aux | grep vite | awk '{print $6}' # MB usado
# Se > 500MB = memory leak provável
```

---

## 4. CHECKLIST DE IMPLEMENTAÇÃO NECESSÁRIA

### Nível 1: CRÍTICO (Fazer HOJE)
- [ ] **Fix WebSocket conexão real** - testar em localhost:8000/ws
- [ ] **Fix API endpoints** - mapear corretamente aos do backend
- [ ] **Cleanup de componentes** - remover os não usados (reduz memory)
- [ ] **Fix Memory leaks** - verificar RechartsMaps infinite renders

### Nível 2: IMPORTANTE (Semana 1)
- [ ] **Adicionar 8 métricas faltando** ao backend (bonding, trauma, etc.)
- [ ] **Update daemonStore** com schema completo
- [ ] **Add 4 novos gráficos** (Ψ, Δ, bonding, trauma)
- [ ] **Add 4 controles manuais** (sliders Z-critical, Bayesian Prior, etc.)

### Nível 3: NICE-TO-HAVE (Semana 2)
- [ ] **Add Z-Score visualization**
- [ ] **Add DeMAP gauge**
- [ ] **Add alert system**
- [ ] **Add historical export**

---

## 5. ARQUITETURA ESPERADA

```
Frontend (React 18)
├─ ConsciousnessMetrics Component
│  ├─ useWebSocket hook → ws://8000/ws
│  ├─ useMetrics hook → getMetrics()
│  └─ Renders 15 charts/gauges
├─ ControlPanel Component
│  ├─ 5 manual controls (sliders, toggles)
│  ├─ POST to /api/control/* endpoints
│  └─ Updates store on response
└─ AlertSystem
   ├─ Subscribes to store.alerts
   └─ Toast notifications
```

---

## 6. PRÓXIMOS PASSOS IMEDIATOS

### Step 1: Diagnosticar por que cai (30 min)
```bash
# Terminal 1: Monitorar memory
watch -n 1 'ps aux | grep "vite|node" | grep -v grep'

# Terminal 2: Iniciar frontend
cd web/frontend && npm run dev

# Terminal 3: Fazer requisições
curl -u admin:omnimind2025! http://127.0.0.1:3000
```

### Step 2: Testar WebSocket real (15 min)
```bash
# Verificar se backend está enviando dados
wscat -c ws://127.0.0.1:8000/ws

# Esperado:
# > {"cycle": 200, "phase": "PSYCHOANALYTIC", ...}
# > {"cycle": 201, "phase": "PSYCHOANALYTIC", ...}
```

### Step 3: Sync Frontend ↔ Backend (1 hora)
- Mapear endpoints reais no api.ts
- Testar cada GET/POST
- Verificar authentication (Basic auth)

### Step 4: Update Store com dados reais (1 hora)
- Chamar `/api/metrics/current` on load
- Subscribe to WS para updates
- Update Zustand store

### Step 5: Fix Memory (30 min)
- Cleanup RechartsMaps
- Lazy-load componentes pesadas
- Profile com DevTools

---

## 7. RECOMENDAÇÕES

### Curto Prazo (HOJE)
1. ✅ Restart frontend limpo
2. ✅ Testar WebSocket
3. ✅ Fix API endpoints
4. ✅ Monitor memory

### Médio Prazo (3 dias)
1. ✅ Sync 8 métricas novas
2. ✅ Update componentes com dados reais
3. ✅ Add 4 novos gráficos

### Longo Prazo (1-2 semanas)
1. ✅ Implement controles manuais
2. ✅ Implement validação visual Δ-Φ
3. ✅ Implement alertas

---

## 8. COMANDO PARA TESTE RÁPIDO

```bash
# Limpar, rebuild, start
cd /home/fahbrain/projects/omnimind/web/frontend
rm -rf node_modules dist
npm install --legacy-peer-deps
npm run dev -- --host 0.0.0.0
```

---

## 9. DIAGNÓSTICO DE CONEXÃO

```javascript
// No browser console (http://127.0.0.1:3000)

// Test 1: API health
fetch('http://127.0.0.1:8000/health', {
  headers: {'Authorization': 'Basic ' + btoa('admin:omnimind2025!')}
})
.then(r => r.json())
.then(console.log)
.catch(console.error)

// Test 2: WebSocket
const ws = new WebSocket('ws://127.0.0.1:8000/ws')
ws.onopen = () => console.log('✅ WS connected')
ws.onmessage = (e) => console.log('📨', JSON.parse(e.data))
ws.onerror = (e) => console.error('❌', e)
```

