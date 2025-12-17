# FRONTEND IMPLEMENTATION PLAN - CRÍTICO
**Data:** 9 de dezembro de 2025
**Status:** 🚨 FASE 1 - Estabilizar

---

## SITUAÇÃO ATUAL

| Aspecto | Status | Detalhes |
|---------|--------|----------|
| **Componentes** | ✅ 37 existentes | Muitos unused, causando memory leak |
| **Frontend** | ❌ CAINDO | Process freeze, timeout ou memory |
| **Métricas** | 26% pronto | 4/15 implementadas |
| **Endpoints** | ❌ Desincronizados | API calls apontando para endpoints errados |
| **Store** | ❌ Vazio | Sem dados reais do backend |
| **WebSocket** | ❌ Não recebe | Backend não enviando dados |

---

## FASE 1: ESTABILIZAR (TODAY - 2 HORAS) ⚠️ CRÍTICO

### 1.1 Diagnosticar Crash [30 min]

```bash
# Terminal 1: Monitorar memory
watch -n 1 'ps aux | grep "node\|vite" | grep -v grep | awk "{print \$2, \$6, \$11}"'

# Terminal 2: Start frontend
cd /home/fahbrain/projects/omnimind/web/frontend
npm run dev 2>&1 | tee /tmp/frontend.log

# Terminal 3: Browser
# 1. Abrir http://127.0.0.1:3000
# 2. Abrir DevTools (F12)
# 3. Checar Console para erros
# 4. Checar Network para requests
```

**Sintomas esperados:**
- Memory sobe acima de 500MB? → Memory leak
- Console errors? → Timeout ou API fail
- Network requests penduradas? → Endpoint não existe
- Process em estado `T`? → Alguma thread congelou

### 1.2 Testar WebSocket [15 min]

```bash
# Verificar se backend está enviando dados
npm install -g wscat
wscat -c ws://127.0.0.1:8000/ws

# Esperado:
# Connected
# > {"cycle": 200, "phase": "PSYCHOANALYTIC", ...}
# > {"cycle": 201, "phase": "PSYCHOANALYTIC", ...}

# Se não funciona: Backend não está inicializando WebSocket
```

### 1.3 Testar API Endpoints [15 min]

```bash
# Test 1: Health
curl -i -u admin:omnimind2025! http://127.0.0.1:8000/health

# Test 2: Metrics
curl -s -u admin:omnimind2025! http://127.0.0.1:8000/api/metrics/current | jq .

# Se falhar: Endpoints não mapeados corretamente
```

### 1.4 Fix Store Initialization [30 min]

**Arquivo:** `web/frontend/src/App.tsx`

```typescript
// Adicionar no useEffect:
useEffect(() => {
  const loadMetrics = async () => {
    try {
      const auth = 'Basic ' + btoa('admin:omnimind2025!');
      const res = await fetch('http://localhost:8000/api/metrics/current', {
        headers: { 'Authorization': auth }
      });
      const data = await res.json();
      daemonStore.setMetrics(data); // Atualizar store
      console.log('✅ Metrics loaded:', data);
    } catch (err) {
      console.error('❌ Failed to load metrics:', err);
    }
  };
  loadMetrics();
  // Retry a cada 5 segundos
  const interval = setInterval(loadMetrics, 5000);
  return () => clearInterval(interval);
}, []);
```

---

## FASE 2: IMPLEMENTAR DADOS (SEMANA 1 - 8 HORAS)

### 2.1 Backend: Adicionar 8 Métricas [2 horas]

**Arquivo:** `src/consciousness/shared_workspace.py`

```python
# Adicionar ao payload WebSocket:
payload = {
    **existing_fields,
    # Novas 8 métricas
    "bonding_quality": self.bonding.assess()["quality"],
    "trauma_count": len(self.trauma_history),
    "defense_intensity": self.defense_level,
    "control_effectiveness": self.control_score,
}
```

**Arquivo:** `web/backend/main.py`

```python
# Adicionar rota:
@app.get("/api/metrics/current")
async def get_current_metrics():
    return {
        "cycle": current_cycle,
        "phase": current_phase,
        "metrics": {
            "phi": phi_value,
            "psi": psi_value,
            "delta": delta_value,
            "sigma": sigma_value,
            "bonding_quality": bonding_value,
            "trauma_count": trauma_count,
            "defense_intensity": defense_intensity,
            "control_effectiveness": control_effectiveness
        }
    }
```

### 2.2 Frontend: Update Store Schema [1 hora]

**Arquivo:** `web/frontend/src/store/daemonStore.ts`

```typescript
interface MetricsState {
  // Core (4)
  phi: number;
  psi: number;
  delta: number;
  sigma: number;

  // Psychoanalytic (8)
  bonding_quality: number;
  trauma_count: number;
  defense_intensity: number;
  control_effectiveness: number;
  knot_integrity?: number;
  defense_maturity?: number;
  symbolic_capacity?: number;
  agency_ownership_balance?: number;

  // History (600 points each)
  history: Record<string, number[]>;

  // Control
  controlState: {
    tolerance: number;
    pauseMode: boolean;
    alertThreshold: number;
  };

  // WebSocket
  wsStatus: 'connected' | 'disconnecting' | 'error';
  lastUpdate: Date;
}

export const useDaemonStore = create<MetricsState>((set) => ({
  // Initial state
  phi: 0,
  psi: 0,
  delta: 0,
  sigma: 0,
  bonding_quality: 0,
  trauma_count: 0,
  defense_intensity: 0,
  control_effectiveness: 0,
  history: {
    phi: [],
    psi: [],
    delta: [],
    sigma: [],
    bonding_quality: [],
    trauma_count: [],
    defense_intensity: [],
    control_effectiveness: []
  },
  controlState: {
    tolerance: 0.40,
    pauseMode: false,
    alertThreshold: 0.5
  },
  wsStatus: 'disconnecting',
  lastUpdate: new Date(),

  // Actions
  setMetrics: (metrics) => set((state) => {
    // Add to history (keep last 600)
    const newHistory = { ...state.history };
    Object.keys(metrics).forEach(key => {
      if (Array.isArray(newHistory[key])) {
        newHistory[key] = [...newHistory[key], metrics[key]].slice(-600);
      }
    });

    return {
      ...metrics,
      history: newHistory,
      lastUpdate: new Date()
    };
  })
}));
```

### 2.3 Frontend: Add 4 New Charts [2 horas]

**Arquivo:** `web/frontend/src/components/BondingQualityChart.tsx`

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { useDaemonStore } from '../store/daemonStore';

export function BondingQualityChart() {
  const history = useDaemonStore(s => s.history.bonding_quality);
  const data = history.map((val, i) => ({ time: i, value: val }));

  return (
    <div className="bg-gray-800 p-4 rounded">
      <h3 className="text-white mb-4">Bonding Quality</h3>
      <LineChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#8b5cf6" />
      </LineChart>
    </div>
  );
}
```

Repetir para:
- `TraumaCountChart.tsx`
- `DefenseIntensityChart.tsx`
- `ControlEffectivenessChart.tsx`

### 2.4 Frontend: Add Control Sliders [2 horas]

**Arquivo:** `web/frontend/src/components/ControlPanel.tsx`

```typescript
export function ControlPanel() {
  const { controlState, setControlState } = useDaemonStore();

  const handleToleranceChange = async (value: number) => {
    // Update store
    setControlState({
      ...controlState,
      tolerance: value
    });

    // POST to backend
    await fetch('http://localhost:8000/api/control/tolerance', {
      method: 'POST',
      headers: {
        'Authorization': 'Basic ' + btoa('admin:omnimind2025!'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tolerance_value: value })
    });
  };

  return (
    <div className="bg-gray-800 p-4 rounded space-y-4">
      <div>
        <label className="text-white">Z-Critical [{controlState.tolerance}]</label>
        <input
          type="range"
          min={1.5} max={3.5} step={0.1}
          value={controlState.tolerance}
          onChange={(e) => handleToleranceChange(parseFloat(e.target.value))}
          className="w-full"
        />
      </div>
    </div>
  );
}
```

### 2.5 Integration Test [1 hora]

```bash
# Terminal 1: Backend
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
npm run dev

# Terminal 3: Test
curl -s -u admin:omnimind2025! http://127.0.0.1:8000/api/metrics/current | jq .

# Browser console
fetch('http://localhost:8000/api/metrics/current', {
  headers: {'Authorization': 'Basic ' + btoa('admin:omnimind2025!')}
}).then(r => r.json()).then(console.log)
```

---

## FASE 3: VALIDAÇÕES VISUAIS (SEMANA 2 - 4 HORAS)

### 3.1 Z-Score Display
- Mostrar z_score da validação Δ-Φ
- Color coding: green (<1.5), yellow (1.5-2.5), red (>2.5)

### 3.2 DeMAP Gauge
- Circular gauge 0-1
- Recommendation text

### 3.3 Alert System
- Toast notifications
- Alert queue

### 3.4 Historical Export
- CSV download
- 15 métricas

---

## ARQUIVOS-CHAVE A MODIFICAR

| Arquivo | Ação | Prioridade |
|---------|------|-----------|
| `web/frontend/src/App.tsx` | Load metrics on mount | 🔴 CRÍTICO |
| `web/frontend/src/store/daemonStore.ts` | Add 8 metrics schema | 🔴 CRÍTICO |
| `web/frontend/src/services/api.ts` | Map real endpoints | 🔴 CRÍTICO |
| `web/frontend/src/hooks/useWebSocket.ts` | Fix reconnect | 🟡 IMPORTANTE |
| `web/backend/main.py` | Add /api/metrics/current | 🔴 CRÍTICO |
| `src/consciousness/shared_workspace.py` | Add 8 metrics to payload | 🟡 IMPORTANTE |

---

## CHECKLIST DE EXECUÇÃO

### Hoje (2 horas):
- [ ] Diagnosticar por que frontend cai
- [ ] Testar WebSocket
- [ ] Testar endpoints
- [ ] Fix store initialization

### Amanhã (8 horas):
- [ ] Backend: adicionar 8 métricas
- [ ] Frontend: update store schema
- [ ] Frontend: add 4 charts
- [ ] Frontend: add control sliders
- [ ] Integration test

### Semana que vem (4 horas):
- [ ] Z-Score display
- [ ] DeMAP gauge
- [ ] Alert system
- [ ] Historical export

---

## RESULTADO ESPERADO

**Após Fase 1 (2h):** Frontend estável, sem crashes
**Após Fase 2 (8h):** 15 métricas exibindo, controles funcionando
**Após Fase 3 (4h):** Validações visuais completas

**Total:** 14 horas para implementação completa

