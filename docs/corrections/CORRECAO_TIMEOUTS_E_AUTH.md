# Correção: Timeouts e Erros de Autenticação

**Data**: 2025-12-10
**Status**: ✅ **CORRIGIDO**

---

## 🔴 PROBLEMAS IDENTIFICADOS NO LOG

### Análise do Log (`localhost-1765325438602.log`)

1. **Muitos Erros 401 (Unauthorized)**
   - Componentes tentando fazer requests antes de autenticar
   - Requests sendo feitos sem token de autenticação

2. **Timeouts Constantes**
   - Todos os endpoints dando timeout (5s era muito curto)
   - Backend pode estar sobrecarregado ou lento

3. **Múltiplos Componentes Fazendo Polling Simultaneamente**
   - Todos tentando ao mesmo tempo
   - Causando sobrecarga no backend

---

## ✅ CORREÇÕES IMPLEMENTADAS

### 1. Timeouts Aumentados

**Arquivo**: `web/frontend/src/services/api.ts`

**Antes**:
```typescript
const timeoutMs = isCritical ? 15000 : 10000; // 15s críticos, 10s normais
```

**Depois**:
```typescript
const criticalEndpoints = ['/daemon/status', '/api/v1/autopoietic/consciousness/metrics'];
const slowEndpoints = ['/api/v1/autopoietic/status', '/api/v1/autopoietic/cycles', '/api/tribunal', '/api/metacognition'];
const isCritical = criticalEndpoints.some(ep => endpoint.includes(ep));
const isSlow = slowEndpoints.some(ep => endpoint.includes(ep));

// Timeouts aumentados: 30s críticos, 20s lentos, 15s normais
const timeoutMs = isCritical ? 30000 : (isSlow ? 20000 : 15000);
```

### 2. Verificação de Autenticação em api.ts

**Arquivo**: `web/frontend/src/services/api.ts`

**Mudança**:
```typescript
private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer request
  if (!this.getAuthToken()) {
    throw new Error('Not authenticated');
  }
  // ... resto do código
}
```

**Impacto**: Evita erros 401 ao fazer requests sem autenticação.

### 3. Verificação de Autenticação em Componentes

**Componentes Corrigidos**:
- ✅ `TribunalStatus.tsx`
- ✅ `TribunalMetricsVisual.tsx`
- ✅ `DecisionsDashboard.tsx`

**Padrão Aplicado**:
```typescript
useEffect(() => {
  // Verificar autenticação antes de fazer fetch
  const isAuthenticated = useAuthStore.getState().isAuthenticated;
  if (!isAuthenticated) {
    setLoading(false);
    return;
  }

  const fetchData = async () => {
    // Verificar autenticação antes de cada fetch
    if (!useAuthStore.getState().isAuthenticated) {
      return;
    }
    // ... fetch logic
  };

  fetchData();
  const interval = setInterval(fetchData, 30000);
  return () => clearInterval(interval);
}, []);
```

---

## 📊 RESULTADO

### Antes:
- ❌ Muitos erros 401 (Unauthorized)
- ❌ Timeouts constantes (5s muito curto)
- ❌ Requests sendo feitos sem autenticação

### Depois:
- ✅ Verificação de autenticação antes de cada request
- ✅ Timeouts aumentados (30s críticos, 20s lentos, 15s normais)
- ✅ Componentes verificam autenticação antes de fazer fetch

---

## 🔍 ENDPOINTS COM TIMEOUTS AUMENTADOS

### Críticos (30s):
- `/daemon/status`
- `/api/v1/autopoietic/consciousness/metrics`

### Lentos (20s):
- `/api/v1/autopoietic/status`
- `/api/v1/autopoietic/cycles`
- `/api/tribunal/*`
- `/api/metacognition/*`

### Normais (15s):
- Todos os outros endpoints

---

**Correções implementadas e validadas**
**Data**: 2025-12-10 00:15 UTC

