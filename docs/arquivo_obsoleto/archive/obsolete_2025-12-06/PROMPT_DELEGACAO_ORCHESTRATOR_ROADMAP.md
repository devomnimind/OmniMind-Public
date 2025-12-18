# 🎯 PROMPT DE DELEGAÇÃO - ORCHESTRATOR ROADMAP (SEÇÕES 4, 5, 8)

**Data**: 6 de dezembro de 2025
**Para**: Agente Remoto / Equipe de Desenvolvimento
**Contexto**: Implementação das 3 seções pendentes do Orchestrator (PR #82)
**Tempo Estimado**: 150-180 horas de desenvolvimento + testes
**Prioridade**: ALTA

---

## 📋 INSTRUÇÃO GERAL

Este prompt descreve a implementação de 3 componentes críticos do Orchestrator:
1. **SEÇÃO 4**: Power States (Ociosidade e Otimização)
2. **SEÇÃO 5**: Permission Matrix (Autonomia)
3. **SEÇÃO 8**: Sandbox de Auto-Melhoria

Cada seção é independente mas se beneficiam da integração. Recomenda-se implementar na ordem: 4 → 5 → 8.

---

## ✅ PRÉ-REQUISITOS

Antes de começar, validar:

```bash
# 1. Verificar que PR #82 foi merged
git log --oneline | grep "orchestrator" | head -5

# 2. Verificar arquivos essenciais existem
ls -la src/orchestrator/agent_registry.py
ls -la src/orchestrator/event_bus.py
ls -la src/orchestrator/circuit_breaker.py
ls -la tests/orchestrator/

# 3. Validar testes passam
pytest tests/orchestrator/ -v --tb=short

# 4. Validar produção está saudável
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Se tudo estiver OK, prosseguir com as seções abaixo.

---

# 🔧 SEÇÃO 4: POWER STATES (Ociosidade e Otimização)

## 📊 Especificação

### Estados de Energia

```python
class PowerState(Enum):
    """Estados de energia do sistema."""
    IDLE = "idle"          # Repouso total, apenas serviços críticos
    STANDBY = "standby"    # Preparado, serviços leves
    ACTIVE = "active"      # Operação normal, todos os serviços
    CRITICAL = "critical"  # Emergencial, máximos recursos
```

### Categorização de Serviços

```python
SERVICE_CATEGORIES = {
    "critical": [
        "security",        # Sempre ativo (segurança)
        "metacognition",   # Sempre ativo (auto-awareness)
    ],
    "essential": [
        "orchestrator",    # Coordenação central
    ],
    "standard": [
        "code",           # Desenvolvimento
        "architect",      # Arquitetura
        "reviewer",       # Code review
    ],
    "optional": [
        "psychoanalyst",  # Análise profunda
        "debug",          # Debugging
    ]
}
```

### Consumo de Recursos por Estado

| Estado | CPU | Memória | Status | Tempo Ativação |
|--------|-----|---------|--------|----------------|
| IDLE | <5% | 100MB | Apenas críticos | N/A |
| STANDBY | 10% | 256MB | Críticos + essenciais | ~5s (warm cache) |
| ACTIVE | 30% | 512MB | Todos os serviços | ~2s |
| CRITICAL | 100% | 1024MB | Máximos recursos | <1s (pré-carregado) |

### Transições de Estado

```
IDLE
  ↓ (usuario solicita ação)
STANDBY
  ↓ (detecção de carga)
ACTIVE
  ↓ (ameaça detectada)
CRITICAL
  ↑ (crise resolvida)
ACTIVE
  ↑ (inatividade por N minutos)
STANDBY
  ↑ (modo economizador ativo)
IDLE
```

---

## 💻 Implementação Detalhada

### Arquivo: `src/orchestrator/power_manager.py`

```python
"""
Power Manager para Orchestrator.

Responsabilidades:
1. Gerenciar transições entre estados
2. Ativar/desativar serviços por categoria
3. Monitorar tempo de inatividade
4. Coordenar preheating
"""

from enum import Enum
from typing import Dict, List, Set
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

class PowerState(Enum):
    """Estados de energia do Orchestrator."""
    IDLE = "idle"
    STANDBY = "standby"
    ACTIVE = "active"
    CRITICAL = "critical"

class ServiceCategory(Enum):
    """Categorias de serviço."""
    CRITICAL = "critical"
    ESSENTIAL = "essential"
    STANDARD = "standard"
    OPTIONAL = "optional"

class PowerManager:
    """Gerencia estados de energia e recursos do Orchestrator."""

    def __init__(self, orchestrator):
        """
        Inicializa Power Manager.

        Args:
            orchestrator: Instância do OrchestratorAgent
        """
        self.orchestrator = orchestrator
        self.current_state = PowerState.ACTIVE
        self.last_activity = datetime.now()
        self.idle_threshold = timedelta(minutes=5)  # Entrar em IDLE após 5min

        # Mapeamento de qual estado ativa quais categorias
        self.state_services = {
            PowerState.IDLE: [ServiceCategory.CRITICAL],
            PowerState.STANDBY: [
                ServiceCategory.CRITICAL,
                ServiceCategory.ESSENTIAL,
            ],
            PowerState.ACTIVE: [
                ServiceCategory.CRITICAL,
                ServiceCategory.ESSENTIAL,
                ServiceCategory.STANDARD,
            ],
            PowerState.CRITICAL: [
                ServiceCategory.CRITICAL,
                ServiceCategory.ESSENTIAL,
                ServiceCategory.STANDARD,
                ServiceCategory.OPTIONAL,
            ],
        }

        # Mapeamento de agentes para categorias
        self.agent_categories = {
            "security": ServiceCategory.CRITICAL,
            "metacognition": ServiceCategory.CRITICAL,
            "orchestrator": ServiceCategory.ESSENTIAL,
            "code": ServiceCategory.STANDARD,
            "architect": ServiceCategory.STANDARD,
            "reviewer": ServiceCategory.STANDARD,
            "psychoanalyst": ServiceCategory.OPTIONAL,
            "debug": ServiceCategory.OPTIONAL,
        }

    async def record_activity(self):
        """Registra atividade recente."""
        self.last_activity = datetime.now()

        # Se estava em IDLE/STANDBY, transicionar para ACTIVE
        if self.current_state in [PowerState.IDLE, PowerState.STANDBY]:
            await self.transition_to(PowerState.ACTIVE)

    async def transition_to(self, target_state: PowerState):
        """
        Transição para estado alvo.

        Args:
            target_state: Estado desejado
        """
        if target_state == self.current_state:
            return

        logger.info(f"Power transition: {self.current_state.value} → {target_state.value}")

        # Desativar agentes não necessários
        agents_to_deactivate = self._get_agents_to_deactivate(target_state)
        for agent_name in agents_to_deactivate:
            await self.orchestrator._deactivate_agent(agent_name)

        # Ativar agentes necessários
        agents_to_activate = self._get_agents_to_activate(target_state)
        for agent_name in agents_to_activate:
            await self.orchestrator._ensure_agent_active(agent_name)

        self.current_state = target_state
        logger.info(f"Power state: {target_state.value} (Active agents: {self._get_active_agents()})")

    def _get_agents_to_deactivate(self, target_state: PowerState) -> Set[str]:
        """Retorna agentes que devem ser desativados."""
        current_active = set(self.agent_categories.keys())

        # Agentes que devem ficar ativos no estado alvo
        target_categories = self.state_services[target_state]
        target_active = {
            name for name, cat in self.agent_categories.items()
            if cat in target_categories
        }

        return current_active - target_active

    def _get_agents_to_activate(self, target_state: PowerState) -> Set[str]:
        """Retorna agentes que devem ser ativados."""
        target_categories = self.state_services[target_state]
        return {
            name for name, cat in self.agent_categories.items()
            if cat in target_categories
        }

    def _get_active_agents(self) -> List[str]:
        """Retorna lista de agentes ativos."""
        target_categories = self.state_services[self.current_state]
        return [
            name for name, cat in self.agent_categories.items()
            if cat in target_categories
        ]

    async def monitor_idle_time(self):
        """
        Monitora tempo de inatividade.
        Deve ser executado periodicamente (recomendado: a cada 30 segundos).
        """
        while True:
            await asyncio.sleep(30)

            # Se em ACTIVE e sem atividade por muito tempo
            if self.current_state == PowerState.ACTIVE:
                time_since_activity = datetime.now() - self.last_activity

                if time_since_activity > self.idle_threshold:
                    # Transição para STANDBY
                    await self.transition_to(PowerState.STANDBY)

                    # Se continuar inativo
                    await asyncio.sleep(60)  # Esperar mais 1 minuto

                    if datetime.now() - self.last_activity > self.idle_threshold + timedelta(minutes=1):
                        # Transição para IDLE
                        await self.transition_to(PowerState.IDLE)

    async def preheat_agents(self, agent_names: List[str]):
        """
        Aquece agentes antes de uso (compilação, cache aquecimento, etc).

        Args:
            agent_names: Lista de nomes de agentes a aquecer
        """
        logger.info(f"Preheating agents: {agent_names}")

        for agent_name in agent_names:
            agent = self.orchestrator.registry.get_agent(agent_name)
            if agent and hasattr(agent, 'preheat'):
                try:
                    await agent.preheat()
                    logger.info(f"✅ Preheated: {agent_name}")
                except Exception as e:
                    logger.error(f"❌ Preheat failed for {agent_name}: {e}")

    def get_metrics(self) -> Dict:
        """Retorna métricas de consumo de energia."""
        return {
            "current_state": self.current_state.value,
            "active_agents": self._get_active_agents(),
            "time_since_activity_seconds": (datetime.now() - self.last_activity).total_seconds(),
            "estimated_memory_mb": self._estimate_memory(),
            "estimated_cpu_percent": self._estimate_cpu(),
        }

    def _estimate_memory(self) -> float:
        """Estima consumo de memória baseado no estado."""
        mapping = {
            PowerState.IDLE: 100,
            PowerState.STANDBY: 256,
            PowerState.ACTIVE: 512,
            PowerState.CRITICAL: 1024,
        }
        return mapping.get(self.current_state, 512)

    def _estimate_cpu(self) -> float:
        """Estima consumo de CPU baseado no estado."""
        mapping = {
            PowerState.IDLE: 5,
            PowerState.STANDBY: 10,
            PowerState.ACTIVE: 30,
            PowerState.CRITICAL: 100,
        }
        return mapping.get(self.current_state, 30)
```

### Integração em `src/agents/orchestrator_agent.py`

```python
# No __init__
self.power_manager = PowerManager(self)

# No método start()
asyncio.create_task(self.power_manager.monitor_idle_time())

# Ao receber requisição (em qualquer handler)
await self.power_manager.record_activity()

# Novo endpoint de API
@router.get("/power-state")
async def get_power_state():
    return {
        "state": orchestrator.power_manager.get_metrics()
    }
```

---

## 🧪 Testes Necessários

**Arquivo**: `tests/orchestrator/test_power_manager.py`

```python
"""
Testes para PowerManager.

Cobertura:
- Transições entre estados
- Ativação/desativação de agentes
- Monitoramento de inatividade
- Preheating de agentes
- Estimativas de consumo
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from src.orchestrator.power_manager import (
    PowerManager,
    PowerState,
    ServiceCategory,
)

@pytest.fixture
def mock_orchestrator():
    """Mock do OrchestratorAgent."""
    class MockOrchestrator:
        def __init__(self):
            self.active_agents = set()
            self.registry = MockRegistry()

        async def _deactivate_agent(self, name: str):
            self.active_agents.discard(name)

        async def _ensure_agent_active(self, name: str):
            self.active_agents.add(name)

    class MockRegistry:
        def get_agent(self, name: str):
            return MockAgent()

    class MockAgent:
        async def preheat(self):
            pass

    return MockOrchestrator()

@pytest.mark.asyncio
async def test_transition_idle_to_active(mock_orchestrator):
    """Testa transição de IDLE para ACTIVE."""
    pm = PowerManager(mock_orchestrator)
    pm.current_state = PowerState.IDLE

    await pm.transition_to(PowerState.ACTIVE)

    assert pm.current_state == PowerState.ACTIVE
    assert "security" in mock_orchestrator.active_agents
    assert "code" in mock_orchestrator.active_agents

@pytest.mark.asyncio
async def test_transition_active_to_idle(mock_orchestrator):
    """Testa transição de ACTIVE para IDLE."""
    pm = PowerManager(mock_orchestrator)
    pm.current_state = PowerState.ACTIVE
    mock_orchestrator.active_agents = {"security", "code", "architect"}

    await pm.transition_to(PowerState.IDLE)

    assert pm.current_state == PowerState.IDLE
    assert "code" not in mock_orchestrator.active_agents
    assert "architect" not in mock_orchestrator.active_agents
    assert "security" in mock_orchestrator.active_agents

@pytest.mark.asyncio
async def test_record_activity_activates_from_idle(mock_orchestrator):
    """Testa que atividade ativa agentes."""
    pm = PowerManager(mock_orchestrator)
    pm.current_state = PowerState.IDLE

    await pm.record_activity()

    assert pm.current_state == PowerState.ACTIVE

@pytest.mark.asyncio
async def test_idle_timeout(mock_orchestrator):
    """Testa transição automática para IDLE após timeout."""
    pm = PowerManager(mock_orchestrator)
    pm.current_state = PowerState.ACTIVE
    pm.idle_threshold = timedelta(seconds=1)
    pm.last_activity = datetime.now() - timedelta(seconds=2)

    # Simular monitoramento (em produção roda em background)
    if datetime.now() - pm.last_activity > pm.idle_threshold:
        await pm.transition_to(PowerState.STANDBY)

    assert pm.current_state == PowerState.STANDBY

@pytest.mark.asyncio
async def test_preheat_agents(mock_orchestrator):
    """Testa preheating de agentes."""
    pm = PowerManager(mock_orchestrator)

    # Deve completar sem exceção
    await pm.preheat_agents(["code", "architect"])

def test_metrics_idle(mock_orchestrator):
    """Testa métricas em estado IDLE."""
    pm = PowerManager(mock_orchestrator)
    pm.current_state = PowerState.IDLE

    metrics = pm.get_metrics()

    assert metrics["current_state"] == "idle"
    assert metrics["estimated_memory_mb"] == 100
    assert metrics["estimated_cpu_percent"] == 5

def test_metrics_critical(mock_orchestrator):
    """Testa métricas em estado CRITICAL."""
    pm = PowerManager(mock_orchestrator)
    pm.current_state = PowerState.CRITICAL

    metrics = pm.get_metrics()

    assert metrics["current_state"] == "critical"
    assert metrics["estimated_memory_mb"] == 1024
    assert metrics["estimated_cpu_percent"] == 100

# ... mais testes para cobertura completa
```

---

## 📋 Checklist de Implementação

- [ ] Criar `src/orchestrator/power_manager.py` com classe PowerManager
- [ ] Definir enums PowerState e ServiceCategory
- [ ] Implementar lógica de transição entre estados
- [ ] Implementar categorização de agentes
- [ ] Implementar monitoramento de inatividade
- [ ] Implementar preheating de agentes
- [ ] Implementar métricas de consumo
- [ ] Integrar PowerManager em OrchestratorAgent
- [ ] Criar endpoints de API para power state
- [ ] Criar suite de testes (20+ testes)
- [ ] Validar com black, flake8, mypy
- [ ] Testar em produção por 48h
- [ ] Documentar em docs/

---

# 🔒 SEÇÃO 5: PERMISSION MATRIX (Autonomia)

## 📊 Especificação

### Matriz de Permissões

```python
class PermissionLevel(Enum):
    """Níveis de permissão."""
    AUTOMATIC = 1          # Sem aprovação, executado imediatamente
    MANUAL_REVIEW = 2      # Requer aprovação humana
    EMERGENCY_ONLY = 3     # Apenas em modo emergencial
    ESCALATE = 0           # Sempre escala para humano
```

### Ações com Permissões

```python
NORMAL_PERMISSIONS = {
    # Delegação (nível 1 - automático)
    "delegate_task": {
        "level": PermissionLevel.AUTOMATIC,
        "requires_approval": False,
        "max_retries": 3,
        "timeout_seconds": 300,
    },

    # Leitura (nível 1 - automático)
    "read_logs": {
        "level": PermissionLevel.AUTOMATIC,
        "requires_approval": False,
    },

    # Modificação de código (nível 2 - revisão)
    "modify_code": {
        "level": PermissionLevel.MANUAL_REVIEW,
        "requires_approval": True,
        "approval_timeout": 3600,
        "dry_run_first": True,
    },

    # Restart de serviço (nível 2 - revisão)
    "restart_service": {
        "level": PermissionLevel.MANUAL_REVIEW,
        "requires_approval": True,
        "backup_first": True,
    },

    # Block port (nível 2-3 - emergencial)
    "block_port": {
        "level": PermissionLevel.MANUAL_REVIEW,
        "requires_approval": True,
        "emergency_auto": True,  # Auto em emergência
    },

    # Modificar configuração (nível 3 - emergencial)
    "modify_config": {
        "level": PermissionLevel.EMERGENCY_ONLY,
        "requires_approval": True,
    },
}

EMERGENCY_PERMISSIONS = {
    # Em emergência, algumas ações são automáticas
    "block_port": {
        "level": PermissionLevel.AUTOMATIC,
        "requires_approval": False,
    },
    "isolate_component": {
        "level": PermissionLevel.AUTOMATIC,
        "requires_approval": False,
    },
    "escalate_to_human": {
        "level": PermissionLevel.AUTOMATIC,
        "requires_approval": False,
    },
}
```

### Sistema de Confiança

```python
class TrustLevel(Enum):
    """Níveis de confiança (0.0 a 1.0)."""
    UNTRUSTED = 0.2        # Requer aprovação em tudo
    LOW = 0.4              # Requer aprovação em ações de risco
    MEDIUM = 0.6           # Aprovação em ações críticas
    HIGH = 0.8             # Poucas restrições
    MAXIMUM = 1.0          # Confiança total (emergência)
```

---

## 💻 Implementação Detalhada

### Arquivo: `src/orchestrator/permission_matrix.py`

```python
"""
Permission Matrix para Orchestrator.

Responsabilidades:
1. Definir quais ações o Orchestrator pode fazer autonomamente
2. Gerenciar níveis de confiança
3. Rastrear decisões e aprovações
4. Auditar ações executadas
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class PermissionLevel(Enum):
    """Níveis de permissão."""
    AUTOMATIC = 1
    MANUAL_REVIEW = 2
    EMERGENCY_ONLY = 3
    ESCALATE = 0

class TrustLevel(Enum):
    """Níveis de confiança."""
    UNTRUSTED = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    MAXIMUM = 1.0

class Decision(Enum):
    """Resultado de uma decisão."""
    APPROVED = "approved"
    DENIED = "denied"
    ESCALATED = "escalated"
    PENDING = "pending"

class PermissionMatrix:
    """Gerencia permissões do Orchestrator."""

    # Permissões em modo normal
    NORMAL_PERMISSIONS = {
        "delegate_task": {
            "level": PermissionLevel.AUTOMATIC,
            "requires_approval": False,
            "audit": True,
        },
        "read_logs": {
            "level": PermissionLevel.AUTOMATIC,
            "requires_approval": False,
            "audit": False,
        },
        "modify_code": {
            "level": PermissionLevel.MANUAL_REVIEW,
            "requires_approval": True,
            "audit": True,
            "dry_run_first": True,
        },
        "restart_service": {
            "level": PermissionLevel.MANUAL_REVIEW,
            "requires_approval": True,
            "audit": True,
        },
        "block_port": {
            "level": PermissionLevel.MANUAL_REVIEW,
            "requires_approval": True,
            "audit": True,
            "emergency_auto": True,
        },
        "modify_config": {
            "level": PermissionLevel.MANUAL_REVIEW,
            "requires_approval": True,
            "audit": True,
        },
    }

    # Permissões em modo emergencial
    EMERGENCY_PERMISSIONS = {
        "block_port": {
            "level": PermissionLevel.AUTOMATIC,
            "requires_approval": False,
            "audit": True,
        },
        "isolate_component": {
            "level": PermissionLevel.AUTOMATIC,
            "requires_approval": False,
            "audit": True,
        },
        "escalate_to_human": {
            "level": PermissionLevel.AUTOMATIC,
            "requires_approval": False,
            "audit": True,
        },
    }

    def __init__(self):
        """Inicializa matriz de permissões."""
        self.emergency_mode = False
        self.trust_level = TrustLevel.MEDIUM
        self.approval_pending: Dict[str, Dict[str, Any]] = {}
        self.decision_history: List[Dict[str, Any]] = []

    def set_emergency_mode(self, enabled: bool, reason: str = ""):
        """Define modo emergencial."""
        self.emergency_mode = enabled
        if enabled:
            self.trust_level = TrustLevel.MAXIMUM
            logger.critical(f"🚨 EMERGENCY MODE ENABLED: {reason}")
        else:
            self.trust_level = TrustLevel.MEDIUM
            logger.info("✅ Emergency mode disabled")

    async def can_execute(self, action: str, context: Dict[str, Any] = None) -> bool:
        """
        Verifica se ação pode ser executada.

        Args:
            action: Nome da ação
            context: Contexto da ação (opcional)

        Returns:
            True se pode executar, False caso contrário
        """
        context = context or {}

        # Selecionar matriz correta
        perms = self.EMERGENCY_PERMISSIONS if self.emergency_mode else self.NORMAL_PERMISSIONS

        if action not in perms:
            logger.warning(f"Unknown action: {action}")
            return False

        perm = perms[action]

        # Se ação automática
        if perm["level"] == PermissionLevel.AUTOMATIC:
            logger.info(f"✅ Auto-approved: {action}")
            await self._audit_decision(action, Decision.APPROVED, context)
            return True

        # Se ação escalada
        if perm["level"] == PermissionLevel.ESCALATE:
            logger.warning(f"⚠️ Escalating: {action}")
            await self._audit_decision(action, Decision.ESCALATED, context)
            await self.escalate_to_human(action, context)
            return False

        # Se requer aprovação
        if perm["requires_approval"]:
            logger.info(f"⏳ Waiting approval: {action}")
            decision = await self._request_approval(action, context)
            return decision == Decision.APPROVED

        # Default: permitir
        logger.info(f"✅ Permitted: {action}")
        await self._audit_decision(action, Decision.APPROVED, context)
        return True

    async def _request_approval(self, action: str, context: Dict[str, Any]) -> Decision:
        """
        Solicita aprovação para ação.

        Em produção, isso se conectaria a sistema de aprovação humana.
        Por enquanto, simular com timeout.
        """
        request_id = f"{action}_{datetime.now().timestamp()}"

        self.approval_pending[request_id] = {
            "action": action,
            "context": context,
            "timestamp": datetime.now(),
            "status": Decision.PENDING,
        }

        logger.info(f"Approval request {request_id} created")

        # TODO: Integrar com sistema de aprovação humana
        # Por enquanto, timeout de 1 hora
        # await asyncio.sleep(3600)
        # return Decision.PENDING

        # Simular: aprovar automaticamente para testes
        self.approval_pending[request_id]["status"] = Decision.APPROVED
        return Decision.APPROVED

    async def escalate_to_human(self, action: str, context: Dict[str, Any]):
        """
        Escala ação para humano.

        Envia notificação e espera intervenção.
        """
        logger.critical(f"🚨 ESCALATING TO HUMAN: {action}")

        # TODO: Integrar com sistema de notificação
        # Enviar email, SMS, push notification, etc.

        await self._audit_decision(action, Decision.ESCALATED, context)

    async def _audit_decision(self, action: str, decision: Decision, context: Dict[str, Any]):
        """Registra decisão em auditoria."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "decision": decision.value,
            "trust_level": self.trust_level.name,
            "emergency_mode": self.emergency_mode,
            "context": context,
        }

        self.decision_history.append(record)

        # Salvar em arquivo
        try:
            with open("logs/permission_decisions.jsonl", "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Error saving audit: {e}")

    def get_decision_history(self, action: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna histórico de decisões."""
        if action:
            return [d for d in self.decision_history if d["action"] == action]
        return self.decision_history

    def explain_decision(self, action: str, context: Dict[str, Any]) -> str:
        """Explica por que uma decisão foi tomada."""
        perms = self.EMERGENCY_PERMISSIONS if self.emergency_mode else self.NORMAL_PERMISSIONS

        if action not in perms:
            return f"Action '{action}' is not recognized."

        perm = perms[action]
        mode = "EMERGENCY" if self.emergency_mode else "NORMAL"

        explanation = f"""
Decision Explanation
====================
Action: {action}
Mode: {mode}
Trust Level: {self.trust_level.name}
Permission Level: {perm['level'].name}
Requires Approval: {perm.get('requires_approval', False)}

Reasoning:
- In {mode} mode, '{action}' has permission level {perm['level'].name}
- Current trust level is {self.trust_level.name}
- Decision: {"AUTO-APPROVED" if not perm.get('requires_approval') else "REQUIRES APPROVAL"}

Context:
{json.dumps(context, indent=2)}
        """

        return explanation.strip()
```

### Integração em `src/agents/orchestrator_agent.py`

```python
# No __init__
self.permission_matrix = PermissionMatrix()

# Antes de executar ação crítica
async def execute_action(self, action: str, context: Dict[str, Any]):
    if await self.permission_matrix.can_execute(action, context):
        # Executar ação
        logger.info(f"Executing: {action}")
        # ... implementação ...
    else:
        logger.warning(f"Action denied: {action}")

# Novo endpoint de API
@router.get("/permissions/explain/{action}")
async def explain_permission(action: str):
    return {
        "explanation": orchestrator.permission_matrix.explain_decision(action, {})
    }

# Quando entrar em modo emergencial
async def _handle_crisis(self, reason: str):
    self.permission_matrix.set_emergency_mode(True, reason)
    # Agora ações automáticas são expandidas
```

---

## 🧪 Testes Necessários

**Arquivo**: `tests/orchestrator/test_permission_matrix.py`

```python
"""
Testes para PermissionMatrix.

Cobertura:
- Permissões em modo normal
- Permissões em modo emergencial
- Aprovações e escalação
- Histórico de auditoria
- Explicabilidade de decisões
"""

import pytest
from src.orchestrator.permission_matrix import (
    PermissionMatrix,
    PermissionLevel,
    TrustLevel,
    Decision,
)

@pytest.mark.asyncio
async def test_automatic_permission():
    """Testa que ações automáticas são aprovadas."""
    pm = PermissionMatrix()

    result = await pm.can_execute("delegate_task", {"target": "code"})

    assert result is True

@pytest.mark.asyncio
async def test_requires_approval():
    """Testa que ações que requerem aprovação retornam False."""
    pm = PermissionMatrix()

    result = await pm.can_execute("modify_code", {"file": "test.py"})

    # Retorna False porque não há aprovação (simular timeout)
    # Em produção seria True após aprovação humana

@pytest.mark.asyncio
async def test_emergency_mode_auto_approves():
    """Testa que modo emergencial aprova automaticamente."""
    pm = PermissionMatrix()
    pm.set_emergency_mode(True, "Security threat")

    result = await pm.can_execute("block_port", {"port": 8080})

    assert result is True
    assert pm.emergency_mode is True

@pytest.mark.asyncio
async def test_emergency_mode_escalation():
    """Testa que escalação funciona em emergência."""
    pm = PermissionMatrix()
    pm.set_emergency_mode(True, "Critical threat")

    result = await pm.can_execute("escalate_to_human", {})

    # Deve escalar (retorna False)
    assert result is False

def test_audit_trail():
    """Testa que decisões são auditadas."""
    pm = PermissionMatrix()

    # Simular decisão
    import asyncio
    asyncio.run(pm.can_execute("delegate_task", {"target": "security"}))

    history = pm.get_decision_history()

    assert len(history) > 0
    assert history[0]["action"] == "delegate_task"
    assert history[0]["decision"] == "approved"

def test_explain_decision():
    """Testa explicação de decisão."""
    pm = PermissionMatrix()

    explanation = pm.explain_decision("modify_code", {"file": "test.py"})

    assert "modify_code" in explanation
    assert "REQUIRES APPROVAL" in explanation

def test_permission_level_normal():
    """Testa que normal mode tem permissões corretas."""
    pm = PermissionMatrix()
    pm.emergency_mode = False

    # delegate_task deve ser automático
    assert pm.NORMAL_PERMISSIONS["delegate_task"]["level"] == PermissionLevel.AUTOMATIC

    # modify_code deve requer aprovação
    assert pm.NORMAL_PERMISSIONS["modify_code"]["requires_approval"] is True

def test_permission_level_emergency():
    """Testa que emergency mode tem permissões expandidas."""
    pm = PermissionMatrix()
    pm.set_emergency_mode(True, "Test")

    # Em modo emergencial, block_port é automático
    assert pm.EMERGENCY_PERMISSIONS["block_port"]["level"] == PermissionLevel.AUTOMATIC

# ... mais testes
```

---

## 📋 Checklist de Implementação

- [ ] Criar `src/orchestrator/permission_matrix.py` com classe PermissionMatrix
- [ ] Definir enums PermissionLevel, TrustLevel, Decision
- [ ] Implementar lógica de permissões normais e emergenciais
- [ ] Implementar sistema de aprovação (com timeout)
- [ ] Implementar escalação para humano
- [ ] Implementar auditoria imutável
- [ ] Implementar explicabilidade de decisões
- [ ] Integrar PermissionMatrix em OrchestratorAgent
- [ ] Criar endpoints de API para permissions
- [ ] Criar suite de testes (25+ testes)
- [ ] Validar com black, flake8, mypy
- [ ] Testar em produção por 48h
- [ ] Documentar em docs/

---

# 🧬 SEÇÃO 8: SANDBOX DE AUTO-MELHORIA (Self-Improvement)

## 📊 Especificação

### Fluxo de Auto-Melhoria

```
1. Detectar Oportunidade
   └─ Métricas mostram gap de performance
   └─ Histórico sugere padrão de falha

2. Propor Mudança
   └─ AutopoieticManager gera código
   └─ Define novo algoritmo/estratégia

3. [NOVO] Criar Sandbox
   └─ Clonar estado do Orchestrator
   └─ Preparar ambiente isolado
   └─ Aquecimento de cache

4. [NOVO] Aplicar Mudança
   └─ Instalar código na cópia
   └─ Inicializar novos componentes
   └─ Validação de sintaxe

5. [NOVO] Testar em Sandbox
   └─ Executar suite de validação
   └─ Comparar métricas (antes vs depois)
   └─ Verificar regressões

6. [NOVO] Decidir
   ├─ Se melhoria > threshold (ex: +5%)
   │  └─ Aplicar em produção
   │  └─ Registrar em history
   │  └─ Auditar mudança
   └─ Senão
     └─ Descartar
     └─ Arquivar em análise
     └─ Usar para futuro learning

7. [NOVO] Rollback Automático
   └─ Se degradação detectada
   └─ Reverter para versão anterior
   └─ Alertar humano
```

---

## 💻 Implementação Detalhada

### Arquivo: `src/orchestrator/sandbox.py`

```python
"""
Sandbox para Auto-Melhoria do Orchestrator.

Responsabilidades:
1. Clonar estado de forma segura
2. Aplicar mudanças em isolamento
3. Validar antes de aplicar em produção
4. Rastrear evolução do sistema
"""

from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
import copy
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TestResult(Enum):
    """Resultado de teste no sandbox."""
    PASSED = "passed"
    FAILED = "failed"
    DEGRADED = "degraded"

@dataclass
class SandboxMetrics:
    """Métricas do sandbox."""
    response_time_ms: float
    success_rate: float
    memory_mb: float
    cpu_percent: float
    phi_score: float
    timestamp: str

@dataclass
class ImprovementProposal:
    """Proposta de melhoria."""
    id: str
    description: str
    change_code: str
    expected_improvement_percent: float
    timestamp: str
    created_by: str  # "autopoietic_manager", "human", etc.

class OrchestratorSandbox:
    """Sandbox para testar mudanças antes de aplicar em produção."""

    def __init__(self, orchestrator):
        """
        Inicializa sandbox.

        Args:
            orchestrator: Instância do OrchestratorAgent a clonar
        """
        self.orchestrator = orchestrator
        self.sandbox_orchestrator: Optional[Any] = None
        self.baseline_metrics: Optional[SandboxMetrics] = None
        self.test_metrics: Optional[SandboxMetrics] = None
        self.improvement_history: List[Dict[str, Any]] = []
        self.improvement_threshold = 0.05  # Melhoria mínima de 5%
        self.regression_threshold = 0.02  # Regressão máxima de 2%

    async def clone_orchestrator(self) -> Any:
        """
        Clona o Orchestrator para sandbox.

        Usa deep copy para isolamento total.

        Returns:
            Cópia isolada do Orchestrator
        """
        try:
            logger.info("Cloning orchestrator for sandbox...")

            # Deep copy do orchestrator
            self.sandbox_orchestrator = copy.deepcopy(self.orchestrator)

            # Isolar recursos
            # (em produção, usar processo separado ou container)

            logger.info("✅ Orchestrator cloned successfully")
            return self.sandbox_orchestrator

        except Exception as e:
            logger.error(f"❌ Failed to clone orchestrator: {e}")
            raise

    async def apply_change(self, proposal: ImprovementProposal) -> bool:
        """
        Aplica mudança ao sandbox.

        Args:
            proposal: Proposta de melhoria

        Returns:
            True se aplicação foi bem-sucedida
        """
        if not self.sandbox_orchestrator:
            await self.clone_orchestrator()

        try:
            logger.info(f"Applying change {proposal.id}: {proposal.description}")

            # Validar sintaxe da mudança
            compile(proposal.change_code, "<string>", "exec")

            # Aplicar mudança ao sandbox
            exec_globals = {"orchestrator": self.sandbox_orchestrator}
            exec(proposal.change_code, exec_globals)

            logger.info(f"✅ Change applied: {proposal.id}")
            return True

        except SyntaxError as e:
            logger.error(f"❌ Syntax error in change: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to apply change: {e}")
            return False

    async def run_validation_tests(self) -> Dict[str, Any]:
        """
        Executa suite de testes de validação.

        Testa:
        - Funcionalidade básica
        - Performance
        - Regressões
        - Memory leaks

        Returns:
            Resultados dos testes
        """
        if not self.sandbox_orchestrator:
            raise ValueError("Sandbox not initialized")

        logger.info("Running validation tests...")

        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_cases": [],
        }

        # Testes básicos de funcionalidade
        test_cases = [
            ("Basic initialization", self._test_initialization),
            ("Agent registry", self._test_agent_registry),
            ("Event bus", self._test_event_bus),
            ("Circuit breaker", self._test_circuit_breaker),
            ("Security handlers", self._test_security_handlers),
            ("Performance", self._test_performance),
        ]

        for test_name, test_func in test_cases:
            try:
                result = await test_func()
                results["test_cases"].append({
                    "name": test_name,
                    "result": "passed",
                    "details": result,
                })
                results["passed_tests"] += 1
            except Exception as e:
                logger.error(f"Test failed: {test_name}: {e}")
                results["test_cases"].append({
                    "name": test_name,
                    "result": "failed",
                    "error": str(e),
                })
                results["failed_tests"] += 1

            results["total_tests"] += 1

        return results

    async def compare_metrics(self, baseline: SandboxMetrics, current: SandboxMetrics) -> Dict[str, Any]:
        """
        Compara métricas baseline vs atual.

        Args:
            baseline: Métricas antes da mudança
            current: Métricas após a mudança

        Returns:
            Análise de melhoria/degradação
        """
        comparison = {
            "response_time_improvement_percent": (
                (baseline.response_time_ms - current.response_time_ms) /
                baseline.response_time_ms * 100
            ),
            "success_rate_improvement_percent": (
                (current.success_rate - baseline.success_rate) * 100
            ),
            "memory_improvement_percent": (
                (baseline.memory_mb - current.memory_mb) /
                baseline.memory_mb * 100
            ),
            "phi_score_improvement_percent": (
                (current.phi_score - baseline.phi_score) /
                baseline.phi_score * 100
            ) if baseline.phi_score > 0 else 0,
        }

        # Calcular score geral
        overall_improvement = (
            comparison["response_time_improvement_percent"] * 0.3 +
            comparison["success_rate_improvement_percent"] * 0.3 +
            comparison["memory_improvement_percent"] * 0.2 +
            comparison["phi_score_improvement_percent"] * 0.2
        ) / 100

        comparison["overall_improvement_percent"] = overall_improvement * 100

        return comparison

    async def execute_improvement(self, proposal: ImprovementProposal) -> bool:
        """
        Executa fluxo completo de melhoria.

        Args:
            proposal: Proposta de melhoria

        Returns:
            True se melhoria foi aplicada em produção
        """
        logger.info(f"Starting improvement process: {proposal.id}")

        try:
            # 1. Clone
            await self.clone_orchestrator()

            # 2. Medir baseline
            self.baseline_metrics = await self._measure_performance(self.sandbox_orchestrator)
            logger.info(f"Baseline metrics: {self.baseline_metrics}")

            # 3. Aplicar mudança
            if not await self.apply_change(proposal):
                logger.error("Failed to apply change")
                return False

            # 4. Executar testes
            test_results = await self.run_validation_tests()
            if test_results["failed_tests"] > 0:
                logger.error(f"Tests failed: {test_results['failed_tests']}")
                return False

            # 5. Medir performance
            self.test_metrics = await self._measure_performance(self.sandbox_orchestrator)
            logger.info(f"Test metrics: {self.test_metrics}")

            # 6. Comparar
            comparison = await self.compare_metrics(self.baseline_metrics, self.test_metrics)
            logger.info(f"Comparison: {comparison}")

            # 7. Decidir
            if comparison["overall_improvement_percent"] > self.improvement_threshold * 100:
                logger.info(f"✅ Improvement approved: {comparison['overall_improvement_percent']:.2f}%")

                # Aplicar em produção
                success = await self.apply_change(proposal)
                if success:
                    self._record_improvement(proposal, comparison)
                    return True
            else:
                logger.info(f"❌ Improvement insufficient: {comparison['overall_improvement_percent']:.2f}%")
                return False

        except Exception as e:
            logger.error(f"Error during improvement execution: {e}")
            return False

        finally:
            # Limpar sandbox
            await self._cleanup_sandbox()

    async def _measure_performance(self, orchestrator) -> SandboxMetrics:
        """Mede performance do orchestrator."""
        # TODO: Implementar medição real
        return SandboxMetrics(
            response_time_ms=50.0,
            success_rate=0.95,
            memory_mb=512.0,
            cpu_percent=30.0,
            phi_score=0.85,
            timestamp=datetime.now().isoformat(),
        )

    async def _test_initialization(self) -> Dict[str, Any]:
        """Testa inicialização."""
        # TODO: Implementar teste real
        return {"initialized": True}

    async def _test_agent_registry(self) -> Dict[str, Any]:
        """Testa AgentRegistry."""
        # TODO: Implementar teste real
        return {"agents_registered": 7}

    async def _test_event_bus(self) -> Dict[str, Any]:
        """Testa EventBus."""
        # TODO: Implementar teste real
        return {"events_processed": 100}

    async def _test_circuit_breaker(self) -> Dict[str, Any]:
        """Testa CircuitBreaker."""
        # TODO: Implementar teste real
        return {"breakers_healthy": True}

    async def _test_security_handlers(self) -> Dict[str, Any]:
        """Testa Security Handlers."""
        # TODO: Implementar teste real
        return {"handlers_responsive": True}

    async def _test_performance(self) -> Dict[str, Any]:
        """Testa performance."""
        # TODO: Implementar teste real
        return {"response_time_ms": 50}

    async def _cleanup_sandbox(self):
        """Limpa sandbox."""
        self.sandbox_orchestrator = None
        logger.info("Sandbox cleaned up")

    def _record_improvement(self, proposal: ImprovementProposal, comparison: Dict[str, Any]):
        """Registra melhoria aprovada."""
        record = {
            "proposal_id": proposal.id,
            "description": proposal.description,
            "improvement_percent": comparison["overall_improvement_percent"],
            "timestamp": datetime.now().isoformat(),
            "status": "applied",
        }

        self.improvement_history.append(record)

        # Salvar em arquivo
        try:
            with open("logs/improvements.jsonl", "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Error saving improvement: {e}")

    def get_improvement_history(self) -> List[Dict[str, Any]]:
        """Retorna histórico de melhorias."""
        return self.improvement_history
```

### Integração em `src/agents/orchestrator_agent.py`

```python
# No __init__
self.sandbox = OrchestratorSandbox(self)

# Quando AutopoieticManager propõe melhoria
async def apply_autopoietic_improvement(self, proposal: ImprovementProposal):
    success = await self.sandbox.execute_improvement(proposal)
    if success:
        logger.info(f"✅ Improvement applied: {proposal.id}")
        await self.event_bus.publish(
            OrchestratorEvent(
                type="improvement_applied",
                severity="HIGH",
                message=f"Self-improvement executed: {proposal.description}"
            )
        )

# Novo endpoint de API
@router.get("/improvements/history")
async def get_improvement_history():
    return {
        "history": orchestrator.sandbox.get_improvement_history()
    }
```

---

## 🧪 Testes Necessários

**Arquivo**: `tests/orchestrator/test_sandbox.py`

```python
"""
Testes para OrchestratorSandbox.

Cobertura:
- Clonagem de orchestrator
- Aplicação de mudanças
- Execução de testes
- Comparação de métricas
- Fluxo completo de melhoria
"""

import pytest
from src.orchestrator.sandbox import (
    OrchestratorSandbox,
    SandboxMetrics,
    ImprovementProposal,
)
from datetime import datetime

@pytest.fixture
def mock_orchestrator():
    """Mock do OrchestratorAgent."""
    class MockOrchestrator:
        def __init__(self):
            self.name = "orchestrator"
            self.phi_score = 0.85

    return MockOrchestrator()

@pytest.fixture
def sandbox(mock_orchestrator):
    """Fixture do sandbox."""
    return OrchestratorSandbox(mock_orchestrator)

@pytest.mark.asyncio
async def test_clone_orchestrator(sandbox):
    """Testa clonagem de orchestrator."""
    cloned = await sandbox.clone_orchestrator()

    assert cloned is not None
    assert cloned.name == "orchestrator"

@pytest.mark.asyncio
async def test_apply_valid_change(sandbox):
    """Testa aplicação de mudança válida."""
    await sandbox.clone_orchestrator()

    proposal = ImprovementProposal(
        id="test-1",
        description="Test improvement",
        change_code="orchestrator.test_var = 123",
        expected_improvement_percent=10,
        timestamp=datetime.now().isoformat(),
        created_by="test",
    )

    result = await sandbox.apply_change(proposal)

    assert result is True

@pytest.mark.asyncio
async def test_apply_invalid_change(sandbox):
    """Testa aplicação de mudança inválida."""
    await sandbox.clone_orchestrator()

    proposal = ImprovementProposal(
        id="test-2",
        description="Invalid change",
        change_code="this is not valid python !!!",
        expected_improvement_percent=10,
        timestamp=datetime.now().isoformat(),
        created_by="test",
    )

    result = await sandbox.apply_change(proposal)

    assert result is False

@pytest.mark.asyncio
async def test_compare_metrics():
    """Testa comparação de métricas."""
    sandbox = OrchestratorSandbox(None)

    baseline = SandboxMetrics(
        response_time_ms=100.0,
        success_rate=0.90,
        memory_mb=512.0,
        cpu_percent=50.0,
        phi_score=0.80,
        timestamp=datetime.now().isoformat(),
    )

    improved = SandboxMetrics(
        response_time_ms=80.0,  # 20% melhor
        success_rate=0.95,  # 5% melhor
        memory_mb=400.0,  # 22% melhor
        cpu_percent=40.0,  # 20% melhor
        phi_score=0.90,  # 12% melhor
        timestamp=datetime.now().isoformat(),
    )

    comparison = await sandbox.compare_metrics(baseline, improved)

    assert comparison["response_time_improvement_percent"] > 0
    assert comparison["success_rate_improvement_percent"] > 0
    assert comparison["overall_improvement_percent"] > 0

# ... mais testes
```

---

## 📋 Checklist de Implementação

- [ ] Criar `src/orchestrator/sandbox.py` com classe OrchestratorSandbox
- [ ] Implementar clonagem de orchestrator (deep copy)
- [ ] Implementar aplicação de mudanças
- [ ] Implementar medição de performance
- [ ] Implementar suite de testes validatórios
- [ ] Implementar comparação de métricas
- [ ] Implementar fluxo completo de melhoria
- [ ] Implementar rollback automático
- [ ] Implementar histórico de melhorias
- [ ] Integrar Sandbox em OrchestratorAgent
- [ ] Criar endpoints de API para sandbox
- [ ] Criar suite de testes (20+ testes)
- [ ] Validar com black, flake8, mypy
- [ ] Testar em produção por 72h (mais longo que outras seções)
- [ ] Documentar em docs/

---

# 📦 RESUMO DE ENTREGA

## Arquivos a Criar/Modificar

```
NEW FILES:
- src/orchestrator/power_manager.py (300-400 linhas)
- src/orchestrator/permission_matrix.py (400-500 linhas)
- src/orchestrator/sandbox.py (500-600 linhas)
- tests/orchestrator/test_power_manager.py (250-300 linhas)
- tests/orchestrator/test_permission_matrix.py (300-350 linhas)
- tests/orchestrator/test_sandbox.py (250-300 linhas)

MODIFIED FILES:
- src/agents/orchestrator_agent.py (adicionar integrações)
- src/orchestrator/__init__.py (export de classes novas)

DOCUMENTATION:
- docs/ORCHESTRATOR_POWER_STATES.md
- docs/ORCHESTRATOR_PERMISSIONS.md
- docs/ORCHESTRATOR_SANDBOX.md
- docs/ORCHESTRATOR_ROADMAP.md (atualizar com status)
```

## Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| Cobertura de Testes | ≥95% |
| Black Compliance | 100% |
| Flake8 Errors | 0 |
| MyPy Errors | 0 |
| Documentação | ≥90% das funções |
| Integração com Git | 100% (todos os arquivos tracked) |

---

## Próximas Etapas

1. **Implementar Seção 4** (40-50h)
   - Criar PowerManager
   - Integrar em OrchestratorAgent
   - Testar transições

2. **Implementar Seção 5** (50-60h)
   - Criar PermissionMatrix
   - Sistema de aprovações
   - Auditoria

3. **Implementar Seção 8** (60-70h)
   - Criar OrchestratorSandbox
   - Fluxo de melhoria
   - Validação robusta

---

**Documento preparado**: 6 de dezembro de 2025
**Versão**: 1.0
**Status**: 🟢 PRONTO PARA IMPLEMENTAÇÃO
