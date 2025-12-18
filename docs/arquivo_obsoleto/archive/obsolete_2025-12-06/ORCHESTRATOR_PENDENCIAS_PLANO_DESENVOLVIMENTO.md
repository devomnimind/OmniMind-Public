# 🎯 PLANO DE DESENVOLVIMENTO - ORCHESTRATOR PENDÊNCIAS

**Data**: 5 de Dezembro de 2025
**Autor**: Fabrício da Silva + assistência de IA
**Base**: Auditoria completa + Implementações já realizadas

---

## 📊 STATUS ATUAL - RESUMO EXECUTIVO

### ✅ Implementações Completas (65%)

| Seção | Componente | Status | Testes | Documentação |
|-------|------------|-------|--------|--------------|
| **1** | AgentRegistry | ✅ 100% | 15/15 | ✅ |
| **2** | AutopoieticManager | ✅ 100% | Integrado | ✅ |
| **3** | EventBus | ✅ 100% | 10/10 | ✅ |
| **7** | CircuitBreaker | ✅ 100% | 12/12 | ✅ |
| **6** | Resposta Crises | 🟡 40% | Parcial | ✅ |

### ⏳ Pendências Críticas (35%)

| Seção | Componente | Prioridade | Estimativa | Dependências |
|-------|------------|------------|------------|--------------|
| **4** | Power States | 🟡 ALTA | 40-50h | Monitoramento |
| **5** | Permission Matrix | 🔴 CRÍTICA | 50-60h | Modo emergencial |
| **6** | Isolamento/Quarentena | 🔴 CRÍTICA | 30-40h | SecurityAgent |
| **8** | Sandbox Auto-Melhoria | 🟢 MÉDIA | 60-70h | AutopoieticManager |
| **9** | Explicabilidade | 🟡 ALTA | 20-30h | EventBus |

---

## 🚀 PRÓXIMAS SESSÕES DE DESENVOLVIMENTO

### SESSÃO 1: Completar Resposta a Crises (Seção 6) 🔴 CRÍTICA

**Prioridade**: 🔴 **CRÍTICA** (completar implementação parcial)
**Estimativa**: 30-40 horas
**Dependências**: SecurityAgent, EventBus (✅ já implementados)

#### Objetivos

1. **Sistema de Isolamento de Componentes**
   - Identificar componentes comprometidos
   - Bloquear comunicação com componentes isolados
   - Reduzir capacidade de componentes isolados

2. **Sistema de Quarentena**
   - Colocar componentes suspeitos em quarentena
   - Executar análise forense automática
   - Decidir quando liberar da quarentena

3. **Análise Forense Automática**
   - Coletar evidências de ameaças
   - Analisar padrões de ataque
   - Gerar relatórios forenses

4. **Notificação Estruturada**
   - Alertas para humanos em formato estruturado
   - Contexto completo da ameaça
   - Recomendações de ação

#### Arquivos a Criar/Modificar

```
src/orchestrator/
├── quarantine_system.py          # NOVO - Sistema de quarentena
├── component_isolation.py        # NOVO - Isolamento de componentes
└── forensic_analyzer.py          # NOVO - Análise forense

src/agents/
└── orchestrator_agent.py         # MODIFICAR - Integrar isolamento/quarentena

tests/orchestrator/
├── test_quarantine_system.py     # NOVO - Testes de quarentena
├── test_component_isolation.py   # NOVO - Testes de isolamento
└── test_forensic_analyzer.py     # NOVO - Testes forenses
```

#### Implementação Detalhada

**1. Sistema de Quarentena** (`src/orchestrator/quarantine_system.py`):

```python
class QuarantineSystem:
    """Sistema de quarentena para componentes comprometidos."""

    def __init__(self, orchestrator: OrchestratorAgent):
        self.orchestrator = orchestrator
        self.quarantined_components: Set[str] = set()
        self.quarantine_reasons: Dict[str, str] = {}
        self.quarantine_timestamps: Dict[str, float] = {}
        self.forensic_data: Dict[str, Dict[str, Any]] = {}

    async def quarantine(self, component_id: str, reason: str, evidence: Dict[str, Any]):
        """Coloca componente em quarentena."""
        # 1. Bloquear comunicação
        await self._block_communication(component_id)

        # 2. Reduzir capacidade
        await self._reduce_capacity(component_id)

        # 3. Coletar evidências
        await self._collect_forensic_evidence(component_id, evidence)

        # 4. Registrar
        self.quarantined_components.add(component_id)
        self.quarantine_reasons[component_id] = reason
        self.quarantine_timestamps[component_id] = time.time()

        # 5. Notificar
        await self._notify_quarantine(component_id, reason)

    async def release(self, component_id: str) -> bool:
        """Libera componente da quarentena após análise."""
        if component_id not in self.quarantined_components:
            return False

        # Verificar se análise forense indica segurança
        forensic_result = self.forensic_data.get(component_id, {})
        if forensic_result.get("safe_to_release", False):
            self.quarantined_components.remove(component_id)
            await self._restore_communication(component_id)
            await self._restore_capacity(component_id)
            return True
        return False
```

**2. Isolamento de Componentes** (`src/orchestrator/component_isolation.py`):

```python
class ComponentIsolation:
    """Isola componentes comprometidos do sistema."""

    def __init__(self, orchestrator: OrchestratorAgent):
        self.orchestrator = orchestrator
        self.isolated_components: Set[str] = set()
        self.isolation_rules: Dict[str, IsolationRule] = {}

    async def isolate(self, component_id: str, isolation_level: str = "full"):
        """Isola componente do sistema."""
        # 1. Bloquear todas as comunicações
        await self._block_all_communications(component_id)

        # 2. Reduzir permissões
        await self._reduce_permissions(component_id)

        # 3. Limitar recursos
        await self._limit_resources(component_id, isolation_level)

        # 4. Registrar
        self.isolated_components.add(component_id)

        # 5. Notificar
        await self._notify_isolation(component_id, isolation_level)
```

**3. Análise Forense** (`src/orchestrator/forensic_analyzer.py`):

```python
class ForensicAnalyzer:
    """Analisa evidências de ameaças automaticamente."""

    async def analyze_threat(self, component_id: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa ameaça e gera relatório forense."""
        # 1. Coletar evidências
        collected = await self._collect_evidence(component_id, evidence)

        # 2. Analisar padrões
        patterns = await self._analyze_patterns(collected)

        # 3. Classificar ameaça
        threat_classification = await self._classify_threat(patterns)

        # 4. Gerar relatório
        report = {
            "component_id": component_id,
            "timestamp": time.time(),
            "evidence": collected,
            "patterns": patterns,
            "classification": threat_classification,
            "recommendations": await self._generate_recommendations(threat_classification),
            "safe_to_release": threat_classification.get("severity", 10) < 5,
        }

        return report
```

#### Integração no OrchestratorAgent

```python
# Em orchestrator_agent.py

class OrchestratorAgent(ReactAgent):
    def __init__(self, config_path: str):
        # ... código existente ...
        from ..orchestrator.quarantine_system import QuarantineSystem
        from ..orchestrator.component_isolation import ComponentIsolation
        from ..orchestrator.forensic_analyzer import ForensicAnalyzer

        self.quarantine_system = QuarantineSystem(self)
        self.component_isolation = ComponentIsolation(self)
        self.forensic_analyzer = ForensicAnalyzer()

    async def _handle_crisis(self, event: Any) -> None:
        """Coordena resposta a crise (COMPLETADO)."""
        logger.critical("MODO DE CRISE ATIVADO: %s", event.event_type)

        # 1. Identificar componente comprometido
        component_id = event.details.get("source_ip") or event.details.get("component_id")

        if component_id:
            # 2. Coletar evidências
            evidence = await self._collect_crisis_evidence(event)

            # 3. Análise forense
            forensic_report = await self.forensic_analyzer.analyze_threat(component_id, evidence)

            # 4. Isolar componente
            await self.component_isolation.isolate(component_id, isolation_level="full")

            # 5. Colocar em quarentena
            await self.quarantine_system.quarantine(
                component_id,
                reason=event.event_type,
                evidence=forensic_report
            )

            # 6. Notificar humanos
            await self._notify_humans_crisis(event, forensic_report)

        # 7. Notificar SecurityAgent
        if self.security_agent:
            await self.security_agent.handle_crisis_response(event)
```

#### Testes Necessários

- [ ] Teste de quarentena de componente
- [ ] Teste de isolamento de componente
- [ ] Teste de análise forense automática
- [ ] Teste de liberação de quarentena
- [ ] Teste de notificação estruturada
- [ ] Teste de integração end-to-end

---

### SESSÃO 2: Permission Matrix (Seção 5) 🔴 CRÍTICA

**Prioridade**: 🔴 **CRÍTICA** (autonomia com segurança)
**Estimativa**: 50-60 horas
**Dependências**: EventBus, Modo Emergencial (parcial)

#### Objetivos

1. **Matriz de Permissões Dinâmica**
   - Definir permissões por ação
   - Níveis de aprovação (auto, aprovação necessária, bloqueado)
   - Modo emergencial com privilégios expandidos

2. **Sistema de Confiança Crescente**
   - Rastrear histórico de decisões
   - Aumentar confiança com decisões bem-sucedidas
   - Reduzir confiança com decisões problemáticas

3. **Explicabilidade Estruturada**
   - Contexto completo de cada decisão
   - Histórico auditado de ações autônomas
   - Rastreamento de causa-efeito

#### Arquivos a Criar

```
src/orchestrator/
├── permission_matrix.py          # NOVO - Matriz de permissões
├── trust_system.py                # NOVO - Sistema de confiança
└── decision_explainer.py          # NOVO - Explicabilidade

src/agents/
└── orchestrator_agent.py          # MODIFICAR - Integrar permissões

tests/orchestrator/
├── test_permission_matrix.py      # NOVO
├── test_trust_system.py           # NOVO
└── test_decision_explainer.py     # NOVO
```

#### Implementação Detalhada

**1. Permission Matrix** (`src/orchestrator/permission_matrix.py`):

```python
class PermissionLevel(Enum):
    AUTO = "auto"              # Execução automática
    APPROVAL_REQUIRED = "approval_required"  # Requer aprovação
    BLOCKED = "blocked"       # Bloqueado

class PermissionMatrix:
    """Matriz de permissões dinâmica."""

    PERMISSIONS = {
        "delegate_task": {
            "level": PermissionLevel.AUTO,
            "requires_approval": False,
            "emergency_override": True,
        },
        "modify_code": {
            "level": PermissionLevel.APPROVAL_REQUIRED,
            "requires_approval": True,
            "emergency_override": False,
        },
        "block_port": {
            "level": PermissionLevel.APPROVAL_REQUIRED,
            "requires_approval": True,
            "emergency_override": True,  # AUTO em emergência
        },
        "isolate_component": {
            "level": PermissionLevel.APPROVAL_REQUIRED,
            "requires_approval": True,
            "emergency_override": True,
        },
        "restart_service": {
            "level": PermissionLevel.APPROVAL_REQUIRED,
            "requires_approval": True,
            "emergency_override": False,
        },
    }

    EMERGENCY_PERMISSIONS = {
        "block_port": PermissionLevel.AUTO,
        "isolate_component": PermissionLevel.AUTO,
        "escalate_to_human": PermissionLevel.AUTO,
    }

    def can_execute(
        self,
        action: str,
        emergency: bool = False,
        trust_level: float = 0.5
    ) -> Tuple[bool, str]:
        """Verifica se ação pode ser executada.

        Returns:
            (pode_executar, motivo)
        """
        if emergency and action in self.EMERGENCY_PERMISSIONS:
            return True, "emergency_override"

        if action not in self.PERMISSIONS:
            return False, "action_not_defined"

        perm = self.PERMISSIONS[action]

        if perm["level"] == PermissionLevel.BLOCKED:
            return False, "blocked"

        if perm["level"] == PermissionLevel.AUTO:
            return True, "auto_permitted"

        if perm["level"] == PermissionLevel.APPROVAL_REQUIRED:
            if emergency and perm.get("emergency_override", False):
                return True, "emergency_override"
            if trust_level >= 0.8:  # Alta confiança
                return True, "high_trust"
            return False, "approval_required"

        return False, "unknown"
```

**2. Trust System** (`src/orchestrator/trust_system.py`):

```python
class TrustSystem:
    """Sistema de confiança crescente."""

    def __init__(self):
        self.trust_scores: Dict[str, float] = {}  # action -> trust_score
        self.decision_history: List[Dict[str, Any]] = []
        self.success_count: Dict[str, int] = {}
        self.failure_count: Dict[str, int] = {}

    def record_decision(
        self,
        action: str,
        success: bool,
        context: Dict[str, Any]
    ) -> None:
        """Registra decisão e atualiza confiança."""
        self.decision_history.append({
            "action": action,
            "success": success,
            "context": context,
            "timestamp": time.time(),
        })

        if success:
            self.success_count[action] = self.success_count.get(action, 0) + 1
        else:
            self.failure_count[action] = self.failure_count.get(action, 0) + 1

        # Calcular novo trust score
        total = self.success_count.get(action, 0) + self.failure_count.get(action, 0)
        if total > 0:
            success_rate = self.success_count.get(action, 0) / total
            self.trust_scores[action] = success_rate

    def get_trust_level(self, action: str) -> float:
        """Obtém nível de confiança para ação."""
        return self.trust_scores.get(action, 0.5)  # Default: 50%
```

**3. Decision Explainer** (`src/orchestrator/decision_explainer.py`):

```python
class DecisionExplainer:
    """Explica decisões tomadas pelo Orchestrator."""

    def explain_decision(
        self,
        action: str,
        context: Dict[str, Any],
        permission_result: Tuple[bool, str],
        trust_level: float
    ) -> Dict[str, Any]:
        """Gera explicação estruturada de decisão."""
        return {
            "action": action,
            "timestamp": time.time(),
            "context": context,
            "permission_result": {
                "can_execute": permission_result[0],
                "reason": permission_result[1],
            },
            "trust_level": trust_level,
            "alternatives_considered": self._get_alternatives(action, context),
            "expected_impact": self._estimate_impact(action, context),
            "risk_assessment": self._assess_risk(action, context),
        }
```

#### Integração no OrchestratorAgent

```python
class OrchestratorAgent(ReactAgent):
    def __init__(self, config_path: str):
        # ... código existente ...
        from ..orchestrator.permission_matrix import PermissionMatrix
        from ..orchestrator.trust_system import TrustSystem
        from ..orchestrator.decision_explainer import DecisionExplainer

        self.permission_matrix = PermissionMatrix()
        self.trust_system = TrustSystem()
        self.decision_explainer = DecisionExplainer()

    async def execute_with_permission_check(
        self,
        action: str,
        context: Dict[str, Any],
        emergency: bool = False
    ) -> Dict[str, Any]:
        """Executa ação com verificação de permissões."""
        # 1. Verificar permissões
        trust_level = self.trust_system.get_trust_level(action)
        can_execute, reason = self.permission_matrix.can_execute(
            action, emergency, trust_level
        )

        # 2. Gerar explicação
        explanation = self.decision_explainer.explain_decision(
            action, context, (can_execute, reason), trust_level
        )

        if not can_execute:
            return {
                "success": False,
                "error": f"Action {action} not permitted: {reason}",
                "explanation": explanation,
            }

        # 3. Executar ação
        try:
            result = await self._execute_action(action, context)
            success = result.get("success", False)

            # 4. Registrar decisão
            self.trust_system.record_decision(action, success, context)

            return {
                "success": success,
                "result": result,
                "explanation": explanation,
            }
        except Exception as e:
            self.trust_system.record_decision(action, False, context)
            return {
                "success": False,
                "error": str(e),
                "explanation": explanation,
            }
```

---

### SESSÃO 3: Power States (Seção 4) 🟡 ALTA

**Prioridade**: 🟡 **ALTA** (otimização de recursos)
**Estimativa**: 40-50 horas
**Dependências**: AgentRegistry (✅ já implementado)

#### Objetivos

1. **Power States Enum**
   - IDLE: Apenas serviços críticos
   - STANDBY: Preparado para ativação
   - ACTIVE: Operação normal
   - CRITICAL: Modo emergencial

2. **Categorização de Serviços**
   - Críticos: SecurityAgent, MetacognitionAgent
   - Essenciais: OrchestratorAgent
   - Opcionais: CodeAgent, ArchitectAgent, etc.

3. **Transições Suaves**
   - Preheating de agentes
   - Cool down ao desativar
   - Liberação de recursos

#### Arquivos a Criar

```
src/orchestrator/
└── power_states.py                # NOVO - Sistema de power states

src/agents/
└── orchestrator_agent.py          # MODIFICAR - Integrar power states

tests/orchestrator/
└── test_power_states.py           # NOVO
```

#### Implementação Detalhada

```python
class PowerState(Enum):
    IDLE = "idle"                 # Repouso total
    STANDBY = "standby"           # Preparado
    ACTIVE = "active"             # Operação normal
    CRITICAL = "critical"         # Modo emergencial

class PowerStateManager:
    """Gerencia estados de energia do Orchestrator."""

    def __init__(self, orchestrator: OrchestratorAgent):
        self.orchestrator = orchestrator
        self.current_state = PowerState.ACTIVE
        self.service_categories = {
            "critical": ["security", "metacognition"],
            "essential": ["orchestrator"],
            "optional": ["code", "architect", "debug", "reviewer"],
        }

    async def transition_to(self, new_state: PowerState) -> None:
        """Transição suave entre estados."""
        logger.info(f"Transição: {self.current_state.value} → {new_state.value}")

        if new_state == PowerState.IDLE:
            await self._transition_to_idle()
        elif new_state == PowerState.STANDBY:
            await self._transition_to_standby()
        elif new_state == PowerState.ACTIVE:
            await self._transition_to_active()
        elif new_state == PowerState.CRITICAL:
            await self._transition_to_critical()

        self.current_state = new_state

    async def _transition_to_idle(self):
        """Transição para IDLE - apenas críticos."""
        # Desativar opcionais
        for agent_name in self.service_categories["optional"]:
            await self._deactivate_agent(agent_name)

        # Manter apenas críticos
        for agent_name in self.service_categories["critical"]:
            await self._ensure_agent_active(agent_name)

    async def _transition_to_active(self):
        """Transição para ACTIVE - todos essenciais."""
        # Reativar essenciais
        for agent_name in self.service_categories["essential"]:
            await self._ensure_agent_active(agent_name)

        # Preheating de opcionais (mas não ativar ainda)
        for agent_name in self.service_categories["optional"]:
            await self._preheat_agent(agent_name)
```

---

### SESSÃO 4: Explicabilidade (Seção 9) 🟡 ALTA

**Prioridade**: 🟡 **ALTA** (transparência)
**Estimativa**: 20-30 horas
**Dependências**: EventBus, Permission Matrix (parcial)

#### Objetivos

1. **Histórico Contextual**
   - Rastrear todas as decisões autônomas
   - Contexto completo de cada ação
   - Causa-efeito entre decisões

2. **API de Explicabilidade**
   - Endpoint para consultar decisões
   - Filtros por ação, data, resultado
   - Exportação de relatórios

#### Integração

- Usar `DecisionExplainer` da Sessão 2
- Adicionar endpoint REST em `web/backend/main.py`
- Criar dashboard de decisões

---

### SESSÃO 5: Sandbox Auto-Melhoria (Seção 8) 🟢 MÉDIA

**Prioridade**: 🟢 **MÉDIA** (roadmap futuro)
**Estimativa**: 60-70 horas
**Dependências**: AutopoieticManager (✅ já implementado)

#### Objetivos

1. **Sandbox para Testes**
   - Clonagem segura de estado
   - Aplicação de mudanças em isolamento
   - Validação antes de aplicar

2. **Rollback Automático**
   - Detecção de degradação
   - Reversão automática
   - Histórico de mudanças

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Sessão 1: Resposta a Crises (30-40h)
- [ ] Criar `quarantine_system.py`
- [ ] Criar `component_isolation.py`
- [ ] Criar `forensic_analyzer.py`
- [ ] Integrar no `OrchestratorAgent`
- [ ] Testes unitários (15+ testes)
- [ ] Testes de integração
- [ ] Documentação

### Sessão 2: Permission Matrix (50-60h)
- [ ] Criar `permission_matrix.py`
- [ ] Criar `trust_system.py`
- [ ] Criar `decision_explainer.py`
- [ ] Integrar no `OrchestratorAgent`
- [ ] Testes unitários (20+ testes)
- [ ] Testes de integração
- [ ] Documentação

### Sessão 3: Power States (40-50h)
- [ ] Criar `power_states.py`
- [ ] Integrar no `OrchestratorAgent`
- [ ] Testes unitários (12+ testes)
- [ ] Testes de performance
- [ ] Documentação

### Sessão 4: Explicabilidade (20-30h)
- [ ] Endpoint REST
- [ ] Dashboard de decisões
- [ ] Exportação de relatórios
- [ ] Testes (8+ testes)
- [ ] Documentação

### Sessão 5: Sandbox (60-70h)
- [ ] Criar `sandbox_system.py`
- [ ] Integrar com AutopoieticManager
- [ ] Testes (25+ testes)
- [ ] Documentação

---

## 🎯 PRIORIZAÇÃO RECOMENDADA

### Fase 1 (Crítica - 2-3 semanas)
1. **Sessão 1**: Resposta a Crises (30-40h)
2. **Sessão 2**: Permission Matrix (50-60h)

### Fase 2 (Alta - 2-3 semanas)
3. **Sessão 3**: Power States (40-50h)
4. **Sessão 4**: Explicabilidade (20-30h)

### Fase 3 (Média - 3-4 semanas)
5. **Sessão 5**: Sandbox Auto-Melhoria (60-70h)

---

## 📚 REFERÊNCIAS

- `docs/AUDITORIA_ORCHESTRATOR_COMPLETA.md` - Auditoria original
- `docs/CHANGES_ORCHESTRATOR_AUDIT.md` - Implementações já feitas
- `docs/ORCHESTRATOR_SOP_VALIDATION_REPORT.md` - Validação
- `docs/ORCHESTRATOR_STATUS_UPDATE_2025-12-06.md` - Status atualizado

---

**Última Atualização**: 5 de Dezembro de 2025

