# 🔧 PLANO DE REFATORAÇÃO: OrchestratorAgent

**Data**: 2025-12-06
**Autor**: Fabrício da Silva + assistência de IA
**Status**: 🟡 EM PROGRESSO

---

## 📊 ANÁLISE INICIAL

### Estatísticas
- **Total de linhas**: 2945
- **Métodos síncronos**: ~60
- **Métodos assíncronos**: ~10
- **Total de métodos**: ~70

### Problemas Identificados
1. ❌ Arquivo muito grande (2945 linhas)
2. ❌ `__init__` muito longo (~180 linhas)
3. ❌ Métodos grandes (alguns com 100+ linhas)
4. ❌ Falta integração com SharedWorkspace
5. ❌ Não calcula Φ para decisões
6. ❌ SystemicMemoryTrace não integrado
7. ❌ Código duplicado em alguns lugares

---

## 🎯 OBJETIVOS DA REFATORAÇÃO

### 1. Integração de Consciência
- ✅ Integrar SharedWorkspace (herdar do ReactAgent refatorado)
- ✅ Calcular Φ antes/depois de decisões críticas
- ✅ Integrar SystemicMemoryTrace para deformações
- ✅ Registrar decisões de orquestração no workspace

### 2. Melhoria de Qualidade
- ✅ Modularizar `__init__` em métodos menores
- ✅ Extrair lógica complexa em métodos auxiliares
- ✅ Reduzir duplicação de código
- ✅ Melhorar legibilidade e manutenibilidade

### 3. Estrutura
- ✅ Manter compatibilidade retroativa
- ✅ Seguir padrão estabelecido pelo ReactAgent
- ✅ Documentar mudanças

---

## 📋 PLANO DE IMPLEMENTAÇÃO

### FASE 1: Integração de Consciência (CRÍTICA)

#### 1.1 Atualizar `__init__` para usar workspace do ReactAgent
**Objetivo**: Herdar workspace do ReactAgent e garantir integração

**Mudanças**:
```python
def __init__(self, config_path: str, workspace: Optional[SharedWorkspace] = None) -> None:
    # Passar workspace para ReactAgent
    super().__init__(config_path, workspace=workspace, embedding_dim=256)

    # Usar workspace herdado
    if self.workspace:
        # Registrar orquestrador como módulo
        self._register_orchestrator_in_workspace()
```

**Arquivos**: `src/agents/orchestrator_agent.py` (linha 112)

---

#### 1.2 Integrar Φ em decisões críticas
**Objetivo**: Calcular Φ antes/depois de decisões importantes

**Pontos de integração**:
1. `decompose_task`: Antes de decompor, calcular Φ
2. `execute_plan`: Antes/depois de executar plano
3. `delegate_task`: Antes de delegar, calcular Φ
4. `_synthesize_results`: Após sintetizar, calcular Φ final

**Mudanças**:
```python
def decompose_task(self, task: str) -> Dict[str, Any]:
    # Calcular Φ antes
    phi_before = self.workspace.compute_phi_from_integrations() if self.workspace else 0.0

    # Decompor tarefa
    plan = self._do_decompose_task(task)

    # Registrar no workspace
    if self.workspace:
        self.workspace.write_module_state(
            module_name=f"orchestrator_plan_{id(plan)}",
            embedding=self._generate_embedding(str(plan)),
            metadata={"task": task, "subtasks_count": len(plan.get("subtasks", []))}
        )

    # Calcular Φ depois
    phi_after = self.workspace.compute_phi_from_integrations() if self.workspace else 0.0
    plan["phi_before"] = phi_before
    plan["phi_after"] = phi_after
    plan["phi_delta"] = phi_after - phi_before

    return plan
```

---

#### 1.3 Integrar SystemicMemoryTrace
**Objetivo**: Deformar atratores com decisões de orquestração

**Mudanças**:
```python
def _register_orchestrator_in_workspace(self) -> None:
    """Registra orquestrador no workspace e inicializa SystemicMemoryTrace."""
    if not self.workspace:
        return

    # Inicializar SystemicMemoryTrace se não existir
    if not self.workspace.systemic_memory:
        from ..memory.systemic_memory_trace import SystemicMemoryTrace
        self.workspace.systemic_memory = SystemicMemoryTrace(
            state_space_dim=self.workspace.embedding_dim
        )

    self.systemic_memory_trace = self.workspace.systemic_memory
```

---

### FASE 2: Refatoração de Qualidade

#### 2.1 Modularizar `__init__`
**Objetivo**: Dividir `__init__` em métodos menores

**Estrutura proposta**:
```python
def __init__(self, config_path: str, workspace: Optional[SharedWorkspace] = None) -> None:
    super().__init__(config_path, workspace=workspace, embedding_dim=256)

    # Configuração básica
    self._init_basic_config()

    # Sistemas de orquestração
    self._init_orchestration_systems()

    # Sistemas de memória
    self._init_memory_systems()

    # Sistemas de segurança e proteção
    self._init_protection_systems()

    # Integrações externas
    self._init_external_integrations()

    # Estado inicial
    self._init_state()

    # Integração de consciência
    self._init_consciousness_integration()
```

**Métodos a criar**:
- `_init_basic_config()`: tools_framework, mode, agent_registry
- `_init_orchestration_systems()`: event_bus, delegation_manager, etc.
- `_init_memory_systems()`: semantic_memory, procedural_memory, etc.
- `_init_protection_systems()`: circuit_breakers, quarantine, etc.
- `_init_external_integrations()`: mcp_client, dbus, supabase, qdrant
- `_init_state()`: current_plan, delegated_tasks, etc.
- `_init_consciousness_integration()`: workspace, systemic_memory

---

#### 2.2 Refatorar métodos grandes
**Objetivo**: Dividir métodos com 100+ linhas

**Métodos candidatos**:
1. `execute_plan` (~200 linhas)
2. `run_orchestrated_task` (~100 linhas)
3. `delegate_task_with_protection` (~100 linhas)
4. `_execute_subtask_internal` (~100 linhas)

**Estratégia**: Extrair lógica em métodos auxiliares menores

---

#### 2.3 Eliminar duplicação
**Objetivo**: Identificar e eliminar código duplicado

**Áreas de atenção**:
- Inicialização de agentes
- Tratamento de erros
- Logging de operações
- Cálculo de métricas

---

### FASE 3: Validação

#### 3.1 Testes
- ✅ Validar integração com SharedWorkspace
- ✅ Validar cálculo de Φ
- ✅ Validar deformações topológicas
- ✅ Validar compatibilidade retroativa

#### 3.2 Qualidade de Código
- ✅ black
- ✅ flake8
- ✅ mypy

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Integração de Consciência
- [ ] Atualizar `__init__` para aceitar workspace
- [ ] Herdar workspace do ReactAgent
- [ ] Registrar orquestrador no workspace
- [ ] Integrar Φ em `decompose_task`
- [ ] Integrar Φ em `execute_plan`
- [ ] Integrar Φ em `delegate_task`
- [ ] Integrar Φ em `_synthesize_results`
- [ ] Inicializar SystemicMemoryTrace
- [ ] Deformar atratores em decisões críticas

### Fase 2: Refatoração de Qualidade
- [ ] Criar `_init_basic_config()`
- [ ] Criar `_init_orchestration_systems()`
- [ ] Criar `_init_memory_systems()`
- [ ] Criar `_init_protection_systems()`
- [ ] Criar `_init_external_integrations()`
- [ ] Criar `_init_state()`
- [ ] Criar `_init_consciousness_integration()`
- [ ] Refatorar `execute_plan`
- [ ] Refatorar `run_orchestrated_task`
- [ ] Refatorar `delegate_task_with_protection`
- [ ] Refatorar `_execute_subtask_internal`
- [ ] Eliminar duplicação

### Fase 3: Validação
- [ ] Testes de integração
- [ ] black
- [ ] flake8
- [ ] mypy
- [ ] Documentação atualizada

---

## ⏱️ ESTIMATIVAS

- **Fase 1**: 15-20 horas
- **Fase 2**: 20-25 horas
- **Fase 3**: 5-10 horas
- **Total**: 40-55 horas

---

## 🚨 RISCOS E MITIGAÇÕES

### Riscos
1. **Breaking changes**: Mudanças podem quebrar código existente
   - **Mitigação**: Manter compatibilidade retroativa, testes extensivos

2. **Complexidade**: Arquivo muito grande, difícil de refatorar
   - **Mitigação**: Refatoração incremental, um método por vez

3. **Performance**: Integrações podem impactar performance
   - **Mitigação**: Lazy init, cache, otimizações

---

## 📚 REFERÊNCIAS

- `src/agents/react_agent.py`: Modelo de integração de consciência
- `src/integrations/mcp_thinking_server.py`: Padrão de integração
- `docs/ANALISE_AGENTES_MCPS_REFATORACAO.md`: Análise completa

---

**Última Atualização**: 2025-12-06

