# 🐛 Fix: decisions.map is not a function

## Problema Identificado

O componente `DecisionsDashboard.tsx` estava tentando chamar `.map()` em `decisions`, mas o endpoint `/api/metacognition/insights` retorna um **objeto**, não um **array**.

### Resposta do Endpoint
```json
{
  "health": {...},
  "last_analysis": null,
  "timestamp": "...",
  "suggestions": [],
  "stats": {},
  "summary": {...}
}
```

### Erro no Browser
```
Uncaught TypeError: decisions.map is not a function
  at DecisionsDashboard.tsx:475
```

## Solução Implementada ✅

### 1. **Validação na Camada de Serviço** (`api.ts`)

Modificado `getDecisions()` para:
- ✅ Verificar se a resposta é um array (retorna como está)
- ✅ Procurar por campos `decisions` ou `items` dentro do objeto (se existirem)
- ✅ Wrappear objetos simples em um array: `[data]`
- ✅ Retornar `[]` vazio em caso de erro
- ✅ Tratar exceções graciosamente

### 2. **Validação Defensiva no Componente** (`DecisionsDashboard.tsx`)

Modificado `fetchDecisions()` para:
- ✅ Verificar se o resultado é um array antes de usar `.map()`
- ✅ Logar erro se receber tipo inesperado
- ✅ Definir `decisions = []` em caso de erro
- ✅ Garantir que o estado sempre contém um array válido

## Arquivos Modificados

| Arquivo | Mudanças |
|---------|----------|
| `web/frontend/src/services/api.ts` | Adicionada validação em `getDecisions()` para garantir retorno de array |
| `web/frontend/src/components/DecisionsDashboard.tsx` | Adicionado type check defensivo em `fetchDecisions()` |

## Por que isso funciona

```typescript
// ANTES: Falha quando endpoint retorna objeto
const data = await apiService.getDecisions(...);
setDecisions(data); // ❌ data é um objeto, não array
{decisions.map(...)} // ❌ TypeError: decisions.map is not a function

// DEPOIS: Sempre converte para array válido
const data = await apiService.getDecisions(...);
if (Array.isArray(data)) {
  setDecisions(data);
} else {
  setDecisions([]); // ✅ Garante que é sempre array
}
{decisions.map(...)} // ✅ Funciona porque decisions é array
```

## Resultado

- ✅ Componente não quebra mais com erro de `.map()`
- ✅ Se endpoint retorna dados: mostra lista vazia graciosamente
- ✅ Se há array válido: exibe normalmente
- ✅ Erros são logados para debugging

## Próximas Etapas

1. **Atualizar endpoint real** - Criar endpoint `/api/decisions` que retorna array propriamente formatado
2. **Remover placeholders** - Substituir chamadas para `/api/metacognition/insights` por endpoint dedicado
3. **Tipagem forte** - Adicionar tipos TypeScript para respostas da API

## Teste

No navegador:
```
1. Carregar página DecisionsDashboard
2. Deve aparecer "Nenhuma decisão encontrada" (sem erro)
3. Console deve estar limpo (sem TypeError)
4. Se houver dados, devem exibir na tabela
```
