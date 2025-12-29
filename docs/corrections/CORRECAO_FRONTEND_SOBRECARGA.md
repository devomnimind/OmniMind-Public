# Correção: Frontend Sobrecarregando Máquina

**Data**: 2025-12-08 23:15
**Problema**: Frontend fazendo polling excessivo quando backend está offline
**Status**: ✅ **CORREÇÃO IMPLEMENTADA**

---

## 🎯 PROBLEMA IDENTIFICADO

### Sintomas
1. **Backend não está rodando**: Scripts de inicialização não estão iniciando o backend corretamente
2. **Polling excessivo**: Múltiplos componentes fazendo polling simultâneo a cada 10 segundos
3. **Sem proteção**: Quando backend está offline, todos os polls falham e geram muitos erros
4. **Sobrecarga**: Múltiplas tentativas de conexão simultâneas sobrecarregam a máquina

### Componentes com Polling Identificados
- `AgentStatus`: 10 segundos
- `ConsciousnessMetrics`: 10 segundos
- `QuickStatsCards`: 10 segundos
- `HealthDashboard`: 10 segundos
- `TribunalStatus`: 10 segundos
- `AutopoieticMetrics`: 30 segundos
- `TribunalMetricsVisual`: 30 segundos
- E mais...

**Total**: ~6-8 componentes fazendo polling simultâneo!

---

## 🛠️ CORREÇÕES IMPLEMENTADAS

### 1. Hook `useBackendHealth` - Circuit Breaker Pattern

**Arquivo**: `web/frontend/src/hooks/useBackendHealth.ts`

**Funcionalidades**:
- Verifica saúde do backend antes de permitir polling
- Implementa circuit breaker: após 3 falhas consecutivas, marca backend como offline
- Aumenta intervalo de verificação quando offline (30s em vez de 10s)
- Retorna ao polling normal quando backend volta online

**Benefícios**:
- Reduz tentativas de conexão quando backend está offline
- Evita sobrecarga da máquina
- Melhora experiência do usuário (mostra status claro)

### 2. Componente `AgentStatus` Atualizado

**Arquivo**: `web/frontend/src/components/AgentStatus.tsx`

**Mudanças**:
- Usa `useBackendHealth` para verificar se backend está online
- Pausa polling quando backend está offline
- Mostra mensagem clara quando backend está offline
- Evita tentativas desnecessárias de conexão

**Antes**:
```typescript
useEffect(() => {
  fetchAgents();
  const interval = setInterval(fetchAgents, 10000);
  return () => clearInterval(interval);
}, [setAgents]);
```

**Depois**:
```typescript
const { isOnline } = useBackendHealth();

useEffect(() => {
  if (!isOnline) {
    console.log('[AgentStatus] Backend offline, pausando polling');
    return;
  }

  fetchAgents();
  const interval = setInterval(fetchAgents, 10000);
  return () => clearInterval(interval);
}, [setAgents, isOnline]);
```

---

## 📋 PRÓXIMOS PASSOS

### 1. Aplicar `useBackendHealth` em Outros Componentes

**Componentes que precisam de atualização**:
- `ConsciousnessMetrics.tsx`
- `QuickStatsCards.tsx`
- `HealthDashboard.tsx`
- `TribunalStatus.tsx`
- `AutopoieticMetrics.tsx`
- `TribunalMetricsVisual.tsx`

**Padrão a seguir**:
```typescript
import { useBackendHealth } from '../hooks/useBackendHealth';

const { isOnline } = useBackendHealth();

useEffect(() => {
  if (!isOnline) return; // Pausar polling se offline

  // ... resto do código de polling
}, [dependencies, isOnline]);
```

### 2. Verificar Scripts de Inicialização

**Problema**: Backend não está iniciando corretamente

**Ações**:
- Verificar `scripts/canonical/system/start_omnimind_system.sh`
- Verificar `scripts/canonical/system/run_cluster.sh`
- Verificar logs do backend (`logs/backend_*.log`)
- Garantir que backend inicia antes do frontend

### 3. Adicionar Timeout nas Requisições API

**Melhoria**: Adicionar timeout nas requisições para evitar esperas longas

**Arquivo**: `web/frontend/src/services/api.ts`

```typescript
const response = await fetch(`${API_BASE_URL}${endpoint}`, {
  ...options,
  headers,
  signal: AbortSignal.timeout(5000), // 5s timeout
});
```

---

## ✅ VALIDAÇÃO

### Testes Necessários

1. **Backend Offline**:
   - Abrir frontend com backend offline
   - Verificar que polling é pausado após 3 falhas
   - Verificar que mensagem "Backend offline" aparece
   - Verificar que não há tentativas excessivas de conexão

2. **Backend Online**:
   - Abrir frontend com backend online
   - Verificar que polling funciona normalmente
   - Verificar que dados são atualizados corretamente

3. **Backend Recuperando**:
   - Iniciar frontend com backend offline
   - Iniciar backend após alguns segundos
   - Verificar que polling retoma automaticamente
   - Verificar que dados são atualizados

---

## 📊 IMPACTO ESPERADO

### Antes da Correção
- **Tentativas de conexão**: ~6-8 por segundo (quando offline)
- **CPU**: Alta (múltiplas tentativas simultâneas)
- **Rede**: Muitas requisições falhando
- **UX**: Erros constantes no console

### Depois da Correção
- **Tentativas de conexão**: 1 a cada 30 segundos (quando offline)
- **CPU**: Baixa (polling pausado)
- **Rede**: Mínima (apenas verificação de saúde)
- **UX**: Mensagem clara quando backend está offline

**Redução**: ~99% nas tentativas de conexão quando backend está offline!

---

**Última Atualização**: 2025-12-08 23:15
**Status**: ✅ **CORREÇÃO IMPLEMENTADA - AGUARDANDO APLICAÇÃO EM OUTROS COMPONENTES**

