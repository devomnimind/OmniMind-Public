# 🔧 PLANO DE CORREÇÃO: Orchestrator em Produção

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Status**: Em Execução

---

## 🎯 OBJETIVO

Corrigir erros críticos do orchestrator e testar workflow completo de delegação de tarefas em modo produção.

---

## ✅ CORREÇÕES APLICADAS

### 1. Meta Cognition Failure (Corrigido)
- **Arquivo**: `src/metacognition/self_analysis.py:40-45`
- **Problema**: Hash chain sendo carregado como lista, mas código esperava dict
- **Correção**: Adicionado tratamento para ambos os formatos (dict com "entries" e list direto)
- **Status**: ✅ CORRIGIDO

### 2. TypeError em ComponentIsolation (Corrigido)
- **Arquivo**: `src/orchestrator/component_isolation.py:276`
- **Problema**: `publish()` não aceita parâmetro `priority`
- **Correção**: Removido parâmetro inválido
- **Status**: ✅ CORRIGIDO

### 3. TypeError em QuarantineSystem (Corrigido)
- **Arquivo**: `src/orchestrator/quarantine_system.py:162`
- **Problema**: `publish()` não aceita parâmetro `priority`
- **Correção**: Removido parâmetro inválido
- **Status**: ✅ CORRIGIDO

---

## 🔍 REVISÃO DO ORCHESTRATOR

### Funções de Delegação Identificadas

1. **`delegate_task()`** (linha 2626)
   - Delegação simples síncrona
   - Status: ✅ Existe

2. **`delegate_task_with_protection()`** (linha 2759)
   - Delegação com proteções (timeout, circuit breaker, retry)
   - Status: ✅ Existe, usa `DelegationManager`

3. **`_delegate_and_execute()`** (linha 2347)
   - Delegação interna para execução de subtarefas
   - Status: ✅ Existe

4. **`_execute_delegate_task()`** (linha 950)
   - Execução de tarefa delegada via tool
   - Status: ✅ Existe

### Integração com DelegationManager

- **`DelegationManager.delegate_with_protection()`**: Método principal
- **Status**: ✅ Integrado no orchestrator
- **Uso**: `delegate_task_with_protection()` chama este método

### MetaReAct Coordinator

- **`MetaReActCoordinator`**: Coordenação em nível meta
- **Status**: ✅ Integrado
- **Uso**: Ativado quando Φ < 0.3 antes de delegar

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 1. Módulos Faltando Inputs (125+ warnings)
- **Localização**: `src/consciousness/integration_loop.py:155`
- **Problema**: Módulos não recebem inputs necessários
- **Impacto**: Quebra cadeia de integração, reduz Φ
- **Prioridade**: 🔴 CRÍTICA

### 2. QdrantClient API Mudou
- **Localização**: `src/memory/hybrid_retrieval.py:227`
- **Problema**: `'QdrantClient' object has no attribute 'search'`
- **Impacto**: Busca de memória quebrada
- **Prioridade**: 🔴 CRÍTICA

### 3. Entropy Warnings (57)
- **Localização**: `src/memory/holographic_memory.py:93`
- **Problema**: Entropia excede limite de Bekenstein (2x o limite)
- **Impacto**: Memória saturada
- **Prioridade**: ⚠️ ALTA

---

## 🧪 PLANO DE TESTES

### Fase 1: Testes Isolados (Correções Funcionais)
- ✅ Testar correção de meta cognition
- ✅ Testar correção de TypeError
- ⏳ Testar delegação simples (`delegate_task`)
- ⏳ Testar delegação com proteção (`delegate_task_with_protection`)

### Fase 2: Testes em Grupos (Reprodução Real)
- ⏳ Testar workflow completo de delegação
- ⏳ Testar com múltiplas chamadas do servidor
- ⏳ Testar com uso intensivo de GPU
- ⏳ Testar cadeia de produção completa

### Fase 3: Validação em Produção
- ⏳ Executar suite completa de testes
- ⏳ Coletar novas métricas
- ⏳ Validar correções

---

## 📋 CHECKLIST DE CORREÇÕES

### Correções Críticas
- [x] Meta cognition failure (hash chain)
- [x] TypeError em ComponentIsolation
- [x] TypeError em QuarantineSystem
- [ ] Módulos faltando inputs (investigar)
- [ ] QdrantClient API (atualizar)

### Correções de Alta Prioridade
- [ ] Entropy warnings (ajustar limite)
- [ ] Falhas ao salvar snapshot Supabase
- [ ] Structural failures (Sigma muito baixo)

### Testes
- [ ] Teste isolado: delegação simples
- [ ] Teste isolado: delegação com proteção
- [ ] Teste em grupo: workflow completo
- [ ] Teste em produção: suite completa

---

## 🎯 PRÓXIMOS PASSOS

1. **Corrigir QdrantClient API** (prioridade crítica)
2. **Investigar módulos faltando inputs** (prioridade crítica)
3. **Executar testes isolados** (validação de correções)
4. **Executar testes em grupos** (reprodução real)
5. **Coletar novas métricas de produção**

---

**Última Atualização**: 2025-12-07
**Status**: 🔄 EM PROGRESSO

