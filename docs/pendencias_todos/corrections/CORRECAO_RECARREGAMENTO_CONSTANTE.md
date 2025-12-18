# Correção: Recarregamento Constante do Navegador

**Data**: 2025-12-09
**Status**: ✅ **CORRIGIDO**

---

## 🔴 PROBLEMA IDENTIFICADO

### Sintoma
- WebSocket fica verde (funcionando)
- Métricas aparecem
- **MAS**: Navegador recarrega constantemente

### Causa Raiz
**Loop infinito causado por dependências instáveis no `useEffect`**

1. **Dashboard.tsx** - Linha 114:
   ```typescript
   useEffect(() => {
     // ...
   }, [fetchData]); // ❌ fetchData é recriado a cada render → loop infinito
   ```

2. **Dashboard.tsx** - Linha 96:
   ```typescript
   useEffect(() => {
     // ...
   }, [lastMessage, setStatus]); // ❌ lastMessage muda constantemente → loop
   ```

3. **useWebSocket.ts** - Linha 30:
   ```typescript
   useEffect(() => {
     const unsubscribe = connectionService.subscribe((message) => {
       setLastMessage(message); // ❌ Cada mensagem causa re-subscription
     });
   }, []);
   ```

---

## ✅ CORREÇÕES IMPLEMENTADAS

### 1. Dashboard useEffect - Array Vazio

**Arquivo**: `web/frontend/src/components/Dashboard.tsx`

**Antes**:
```typescript
useEffect(() => {
  fetchData();
  const interval = setInterval(() => {
    fetchData();
  }, 15000);
  return () => clearInterval(interval);
}, [fetchData]); // ❌ Loop infinito
```

**Depois**:
```typescript
useEffect(() => {
  // Função estável dentro do useEffect
  const fetchDataStable = async () => {
    // ... lógica de fetch
  };

  fetchDataStable();
  const interval = setInterval(() => {
    fetchDataStable();
  }, 15000);
  return () => clearInterval(interval);
}, []); // ✅ Array vazio - executa apenas uma vez
```

### 2. WebSocket Handler - Dependências Estáveis

**Arquivo**: `web/frontend/src/components/Dashboard.tsx`

**Antes**:
```typescript
useEffect(() => {
  switch (lastMessage.type) {
    // ...
  }
}, [lastMessage, setStatus]); // ❌ lastMessage muda constantemente
```

**Depois**:
```typescript
useEffect(() => {
  if (!lastMessage) return;

  const currentLastMessage = lastMessage; // Capturar valor atual

  switch (currentLastMessage.type) {
    // ...
  }
}, [lastMessage?.type, lastMessage?.id, setStatus]); // ✅ Campos estáveis
```

### 3. useWebSocket Hook - Flag isMounted

**Arquivo**: `web/frontend/src/hooks/useWebSocket.ts`

**Antes**:
```typescript
useEffect(() => {
  const unsubscribe = connectionService.subscribe((message) => {
    setLastMessage(message); // ❌ Sempre atualiza, mesmo após unmount
  });
  return unsubscribe;
}, []);
```

**Depois**:
```typescript
useEffect(() => {
  let isMounted = true;

  const unsubscribe = connectionService.subscribe((message) => {
    if (isMounted) { // ✅ Só atualiza se montado
      setLastMessage(message);
    }
  });

  return () => {
    isMounted = false;
    unsubscribe();
  };
}, []);
```

---

## 📊 RESULTADO

### Antes:
- ❌ Navegador recarregando constantemente
- ❌ Loop infinito de re-renders
- ❌ WebSocket causando atualizações excessivas

### Depois:
- ✅ Navegador estável (sem recarregamentos)
- ✅ Sem loops infinitos
- ✅ WebSocket funcionando corretamente (verde)
- ✅ Métricas aparecendo normalmente

---

## 🔍 PRINCÍPIOS APLICADOS

1. **Dependências Estáveis**: Usar apenas valores primitivos ou campos estáveis nas dependências
2. **Funções Estáveis**: Definir funções dentro do `useEffect` quando possível
3. **Flags de Montagem**: Usar `isMounted` para evitar updates após unmount
4. **Array Vazio**: Quando possível, usar `[]` para execução única

---

**Correções implementadas e validadas**
**Data**: 2025-12-09 23:55 UTC

