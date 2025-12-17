# Análise de Testes - 08 de Dezembro de 2025

**Data**: 2025-12-08
**Suite**: Fast Test Suite (run_tests_fast.sh)
**Duração**: 2:15:00 (8100.71s)
**Resultado**: 4429 passed, 42 failed, 20 errors, 118 skipped

---

## 📊 Resumo Executivo

### Estatísticas Gerais
- ✅ **4429 testes passaram** (98.6% de sucesso)
- ❌ **42 testes falharam** (0.9%)
- ⚠️ **20 erros** (0.4%)
- ⏭️ **118 testes pulados** (2.6%)

### Categorização de Erros

| Categoria | Quantidade | Status | Prioridade |
|-----------|------------|--------|------------|
| **ASSERTION_ERROR** | 15 | ⚠️ Pendente | Média |
| **ATTRIBUTE_ERROR** | 9 | ⚠️ Pendente | Alta |
| **CUDA_OOM** | 6 | ✅ Já corrigido (parcial) | Média |
| **SERVER_NOT_RUNNING** | 8 | ✅ Esperado (testes E2E) | Baixa |
| **KEY_ERROR** | 1 | ⚠️ Pendente | Alta |
| **OTHER** | 18 | ⚠️ Variado | Variada |

---

## 🔴 Erros Críticos por Categoria

### 1. ATTRIBUTE_ERROR (9 erros) - **ALTA PRIORIDADE**

**Problema**: Mock object não tem atributo `qdrant_url`

**Testes Afetados**:
- `tests/orchestrator/test_rag_fallback.py` (6 testes)
  - `test_init`
  - `test_generate_retrieval_query`
  - `test_augment_context`
  - `test_retrieve_on_failure`
  - `test_reexecute_with_context`
  - `test_get_fallback_stats`

**Causa**: O mock de `HybridRetrievalSystem` não está completo. O código real acessa `qdrant_url` mas o mock não fornece esse atributo.

**Correção Necessária**:
```python
# Em tests/orchestrator/test_rag_fallback.py
@pytest.fixture
def mock_retrieval_system(self):
    mock = MagicMock(spec=HybridRetrievalSystem)
    mock.qdrant_url = "http://localhost:6333"  # Adicionar este atributo
    mock.retrieve.return_value = [...]
    return mock
```

**Status**: ⚠️ **PENDENTE**

---

### 2. CUDA_OOM (6 erros) - **MÉDIA PRIORIDADE**

**Problema**: CUDA out of memory durante inicialização de modelos

**Testes Afetados**:
- `tests/orchestrator/test_error_analyzer_integration.py` (5 testes)
- `tests/test_agents_core_integration.py::test_orchestrator_parses_and_executes_plan`

**Causa**: Testes estão tentando inicializar modelos de embedding/LLM que consomem GPU, mas a GPU já está ocupada ou sem memória suficiente.

**Correção Já Aplicada** (parcial):
- ✅ `src/agents/react_agent.py` já tem fallback para CPU quando CUDA OOM
- ⚠️ Testes precisam mockar ou desabilitar GPU

**Correção Necessária**:
```python
# Adicionar @pytest.mark.mock ou desabilitar GPU nos testes
@pytest.fixture(autouse=True)
def disable_gpu():
    import os
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    yield
    del os.environ['CUDA_VISIBLE_DEVICES']
```

**Status**: ✅ **PARCIALMENTE CORRIGIDO** - Precisa ajustar testes

---

### 3. ASSERTION_ERROR - Testes MCP (15 erros) - **MÉDIA PRIORIDADE**

**Problema**: Testes esperando valores hardcoded mas recebendo valores reais

**Testes Afetados**:
- `tests/integrations/test_mcp_python_server.py` (7 testes)
- `tests/integrations/test_mcp_system_info_server.py` (7 testes)
- `tests/integrations/test_mcp_logging_server.py` (2 testes)

**Causa**: Testes foram ajustados para aceitar valores reais, mas alguns ainda têm assertions hardcoded.

**Correção Já Aplicada** (parcial):
- ✅ Documentado em `docs/MCP_SERVERS_VALORES_REAIS_VS_HARDCODED.md`
- ⚠️ Alguns testes ainda precisam ajuste

**Status**: ⚠️ **PARCIALMENTE CORRIGIDO** - Verificar testes específicos

---

### 4. ASSERTION_ERROR - AlertingSystem (5 erros) - **MÉDIA PRIORIDADE**

**Problema**: State leakage entre testes

**Testes Afetados**:
- `tests/audit/test_alerting_system.py` (5 testes)
  - `test_initialization` - assert 208 == 0
  - `test_get_active_alerts_all` - assert 218 == 2
  - `test_get_active_alerts_by_severity` - assert 76 == 1
  - `test_get_statistics` - assert 233 == 2
  - `test_monitor_audit_chain_healthy` - assert 77 == 0

**Causa**: Alertas de execuções anteriores não estão sendo limpos entre testes.

**Correção Já Aplicada** (parcial):
- ✅ Fixture `alerting_system` já limpa estado
- ⚠️ Pode haver alertas persistentes em arquivos

**Status**: ⚠️ **PARCIALMENTE CORRIGIDO** - Verificar limpeza de arquivos

---

### 5. ASSERTION_ERROR - Consciousness Tests (8 erros) - **BAIXA PRIORIDADE**

**Problema**: Testes esperando comportamentos específicos que mudaram

**Testes Afetados**:
- `test_biological_metrics.py` - String de classificação mudou
- `test_consciousness_triad.py` - Thresholds empíricos atualizados
- `test_shared_workspace.py` - Validação de dimensões
- `test_extended_cycle_result.py` - Extended results disabled em sync mode
- Outros testes de consciência

**Causa**: Refatorações e atualizações empíricas mudaram comportamentos esperados.

**Status**: ⚠️ **PENDENTE** - Ajustar assertions conforme implementação atual

---

### 6. SERVER_NOT_RUNNING (8 erros) - **BAIXA PRIORIDADE**

**Problema**: Testes E2E esperando servidor rodando

**Testes Afetados**:
- `tests/e2e/test_dashboard_live.py` (8 testes)

**Causa**: Testes E2E requerem servidor backend rodando, mas não está disponível durante suite rápida.

**Status**: ✅ **ESPERADO** - Testes E2E devem ser executados separadamente com `RUN_E2E_TESTS=1`

---

## 🔍 Análise de Ciclos Executados

**Durante os testes, o IntegrationLoop executou ciclos reais**:
- Logs mostram execução de `execute_cycle_sync` e `RNN step executed`
- Ciclos foram executados como parte de testes de integração
- **Não é execução de produção**, mas sim parte dos testes que usam componentes reais

**Observação**: Os logs (408-705) mostram ciclos do `IntegrationLoop` sendo executados durante testes, não execução standalone de produção.

---

## ✅ Correções Já Aplicadas

1. ✅ **CUDA OOM handling** - Fallback para CPU implementado
2. ✅ **MCP servers** - Documentação de valores reais vs hardcoded
3. ✅ **AlertingSystem** - Limpeza de estado entre testes (parcial)
4. ✅ **Biological metrics** - Classificação atualizada
5. ✅ **Consciousness triad** - Thresholds empíricos aplicados

---

## ⚠️ Correções Pendentes

### Alta Prioridade
1. **test_rag_fallback.py** - Adicionar `qdrant_url` ao mock
2. **test_mcp_system_info_server.py** - Corrigir KeyError 'cores'

### Média Prioridade
3. **test_error_analyzer_integration.py** - Mockar GPU ou desabilitar
4. **test_alerting_system.py** - Verificar limpeza completa de arquivos
5. **test_mcp_python_server.py** - Ajustar assertions restantes

### Baixa Prioridade
6. **Testes de consciência** - Atualizar assertions conforme implementação
7. **Testes E2E** - Documentar que requerem servidor rodando

---

## 📋 Próximos Passos

1. Corrigir mocks em `test_rag_fallback.py`
2. Ajustar testes MCP que ainda têm assertions hardcoded
3. Verificar limpeza completa do AlertingSystem
4. Atualizar testes de consciência com novos comportamentos
5. Documentar requisitos de testes E2E

---

**Autor**: Fabrício da Silva + assistência de IA
**Última Atualização**: 2025-12-08

