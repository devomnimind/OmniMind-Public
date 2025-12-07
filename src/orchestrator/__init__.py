"""
Orchestrator module - Componentes centrais de orquestração do OmniMind.

Implementa recomendações da AUDITORIA_ORCHESTRATOR_COMPLETA.md:
- AgentRegistry: Registro centralizado de agentes com health checks
- EventBus: Sistema de eventos priorizado
- CircuitBreaker: Proteção contra cascata de falhas
- QuarantineSystem: Sistema de quarentena para componentes comprometidos
- ComponentIsolation: Isolamento de componentes
- ForensicAnalyzer: Análise forense automática
"""

from .agent_registry import AgentPriority, AgentRegistry
from .auto_repair import AutoRepairSystem, RepairAction, RepairStrategy
from .circuit_breaker import AgentCircuitBreaker, CircuitBreakerOpen, CircuitState
from .component_isolation import ComponentIsolation, IsolationLevel
from .decision_explainer import DecisionExplainer, DecisionExplanation
from .error_analyzer import ErrorAnalysis, ErrorAnalyzer, ErrorType, RecoveryStrategy
from .event_bus import EventPriority, OrchestratorEvent, OrchestratorEventBus
from .meta_react_coordinator import (
    AgentComposition,
    MetaReActCoordinator,
    StrategyChange,
    StrategyType,
)
from .forensic_analyzer import ForensicAnalyzer, ForensicReport, ThreatCategory, ThreatSeverity
from .introspection_loop import IntrospectionLoop, IntrospectionMetrics
from .sandbox_system import (
    SandboxChange,
    SandboxResult,
    SandboxSnapshot,
    SandboxState,
    SandboxSystem,
)
from .permission_matrix import Permission, PermissionLevel, PermissionMatrix
from .power_states import PowerState, PowerStateManager, ServiceCategory
from .quarantine_system import QuarantineRecord, QuarantineSystem
from .rollback_system import RollbackSystem, VersionSnapshot
from .trust_system import DecisionRecord, TrustSystem

__all__ = [
    "AgentRegistry",
    "AgentPriority",
    "OrchestratorEventBus",
    "EventPriority",
    "OrchestratorEvent",
    "AgentCircuitBreaker",
    "CircuitBreakerOpen",
    "CircuitState",
    "QuarantineSystem",
    "QuarantineRecord",
    "ComponentIsolation",
    "IsolationLevel",
    "ForensicAnalyzer",
    "ForensicReport",
    "ThreatCategory",
    "ThreatSeverity",
    "PermissionMatrix",
    "Permission",
    "PermissionLevel",
    "TrustSystem",
    "DecisionRecord",
    "DecisionExplainer",
    "DecisionExplanation",
    "ErrorAnalysis",
    "ErrorAnalyzer",
    "ErrorType",
    "PowerStateManager",
    "RecoveryStrategy",
    "PowerState",
    "ServiceCategory",
    "AutoRepairSystem",
    "RepairAction",
    "RepairStrategy",
    "RollbackSystem",
    "VersionSnapshot",
    "IntrospectionLoop",
    "IntrospectionMetrics",
    "SandboxSystem",
    "SandboxState",
    "SandboxSnapshot",
    "SandboxChange",
    "SandboxResult",
    "MetaReActCoordinator",
    "StrategyType",
    "StrategyChange",
    "AgentComposition",
]
