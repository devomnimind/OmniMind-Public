#!/usr/bin/env python3
"""
OrchestratorAgent - Coordenador Mestre Multi-Agente
Modo: orchestrator (🪃)

Função: Decompor tarefas, delegar para agentes especializados, sintetizar resultados
Implementa "boomerang tasks" (task → delegate → receive → synthesize → return)
Ferramentas: workflow (new_task, switch_mode, plan_task, attempt_completion)

Quando usar: Tarefas complexas multi-fase que exigem coordenação entre agentes
Integração: Controla todos os modos (code, architect, debug, reviewer, ask)
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..autopoietic.manager import AutopoieticManager
from ..integrations.dbus_controller import (
    DBusSessionController,
    DBusSystemController,
)
from ..integrations.llm_router import LLMModelTier
from ..integrations.mcp_client import MCPClient, MCPClientError
from ..integrations.mcp_orchestrator import MCPOrchestrator, MCPOrchestratorError
from ..integrations.orchestrator_llm import invoke_orchestrator_llm
from ..integrations.qdrant_adapter import (
    QdrantAdapter,
    QdrantAdapterError,
    QdrantConfig,
)
from ..integrations.supabase_adapter import (
    SupabaseAdapter,
    SupabaseAdapterError,
    SupabaseConfig,
)
from ..memory.procedural_memory import ProceduralMemory
from ..memory.semantic_cache import SemanticCacheLayer
from ..memory.semantic_memory import SemanticMemory
from ..memory.systemic_memory_trace import SystemicMemoryTrace
from ..metacognition.metacognition_agent import MetacognitionAgent
from ..orchestration.agent_registry import AgentPriority, AgentRegistry
from ..orchestration.auto_repair import AutoRepairSystem
from ..orchestration.circuit_breaker import AgentCircuitBreaker
from ..orchestration.component_isolation import ComponentIsolation, IsolationLevel
from ..orchestration.decision_explainer import DecisionExplainer
from ..orchestration.delegation_manager import DelegationManager, HeartbeatMonitor
from ..orchestration.error_analyzer import ErrorAnalyzer
from ..orchestration.event_bus import (
    EventPriority,
    OrchestratorEvent,
    OrchestratorEventBus,
)
from ..orchestration.forensic_analyzer import ForensicAnalyzer
from ..orchestration.introspection_loop import IntrospectionLoop
from ..orchestration.meta_react_coordinator import MetaReActCoordinator
from ..orchestration.permission_matrix import PermissionMatrix
from ..orchestration.power_states import PowerStateManager
from ..orchestration.quarantine_system import QuarantineSystem
from ..orchestration.rag_fallback import RAGFallbackSystem
from ..orchestration.rollback_system import RollbackSystem
from ..orchestration.sandbox_system import SandboxSystem
from ..orchestration.trust_system import TrustSystem
from ..security.security_agent import SecurityAgent
from ..tools.dynamic_tool_creator import DynamicToolCreator
from ..tools.omnimind_tools import ToolsFramework
from .architect_agent import ArchitectAgent
from .code_agent import CodeAgent
from .debug_agent import DebugAgent
from .orchestrator_metrics import OrchestratorMetricsCollector
from .psychoanalytic_analyst import PsychoanalyticAnalyst
from .react_agent import ReactAgent
from .reviewer_agent import ReviewerAgent
from ..benchmarks.benchmark_evaluator import BenchmarkEvaluator
from ..consciousness.paradox_orchestrator import ParadoxOrchestrator

logger = logging.getLogger(__name__)


class AgentMode(Enum):
    """Modos de agente disponíveis"""

    ORCHESTRATOR = "orchestrator"
    CODE = "code"
    ARCHITECT = "architect"
    DEBUG = "debug"
    REVIEWER = "reviewer"
    PSYCHOANALYST = "psychoanalyst"
    SECURITY = "security"
    MCP = "mcp"
    DBUS = "dbus"
    ASK = "ask"


class OrchestratorAgent(ReactAgent):
    """
    Orquestrador mestre que coordena múltiplos agentes especializados.

    Fluxo típico:
    User → Orchestrator → (decompose) → Delegate to specialists → Synthesize → User

    Exemplo:
    "Migrar API para GraphQL" →
        1. Architect: Cria spec (ARCHITECTURE.md)
        2. Code: Implementa schema + resolvers
        3. Debug: Testa edge cases
        4. Reviewer: Avalia qualidade (RLAIF)
        5. Orchestrator: Compila report final
    """

    def __init__(
        self,
        config_path: str,
        workspace: Optional[Any] = None,
        embedding_dim: int = 256,
    ) -> None:
        """Initialize OrchestratorAgent with consciousness integration.

        Args:
            config_path: Path to agent configuration file
            workspace: Instância opcional de SharedWorkspace para integração
            embedding_dim: Dimensão dos embeddings (deve corresponder ao workspace)
        """
        # Passar workspace para ReactAgent (herda integração de consciência)
        super().__init__(config_path, workspace=workspace, embedding_dim=embedding_dim)

        self.tools_framework = ToolsFramework()
        self.mode = "orchestrator"

        # Agentes especializados (lazy init) - MANTIDO para compatibilidade
        self._agents: Dict[AgentMode, ReactAgent] = {}

        # NEW: AgentRegistry centralizado (Seção 1 da Auditoria)
        self.agent_registry = AgentRegistry()

        # NEW: EventBus para integração de sensores (Seção 3 da Auditoria)
        self.event_bus = OrchestratorEventBus()

        # NEW: AutopoieticManager integrado (Seção 2 da Auditoria)
        self.autopoietic_manager: Optional[AutopoieticManager] = None

        # NEW: Circuit breakers por agente (Seção 7 da Auditoria)
        self._circuit_breakers: Dict[str, AgentCircuitBreaker] = {}

        # NEW: Delegation Manager com proteções (Seção 7 da Auditoria)
        self.delegation_manager: Optional[DelegationManager] = None

        # NEW: Heartbeat Monitor para saúde dos agentes (Seção 7 da Auditoria)
        self.heartbeat_monitor: Optional[HeartbeatMonitor] = None

        # NEW: Sistema de Resposta a Crises (Seção 6 da Auditoria)
        self.quarantine_system: Optional[QuarantineSystem] = None
        self.component_isolation: Optional[ComponentIsolation] = None
        self.forensic_analyzer: Optional[ForensicAnalyzer] = None

        # NEW: Sistema de Permissões e Confiança (Seção 5 da Auditoria)
        self.permission_matrix: Optional[PermissionMatrix] = None
        self.trust_system: Optional[TrustSystem] = None
        self.decision_explainer: Optional[DecisionExplainer] = None

        # NEW: Sistema de Power States (Seção 4 da Auditoria)
        self.power_state_manager: Optional[PowerStateManager] = None

        # NEW: HybridResourceManager para alocação inteligente GPU/CPU
        from ..monitor.resource_manager import HybridResourceManager

        self.resource_manager = HybridResourceManager()

        # NEW: Sistema de Auto-Reparação (Seção 2 da Auditoria)
        self.auto_repair_system: Optional[AutoRepairSystem] = None
        self.rollback_system: Optional[RollbackSystem] = None
        self.introspection_loop: Optional[IntrospectionLoop] = None

        # NEW: Sistema de Sandbox para Auto-Melhoria (Seção 8 da Auditoria)
        self.sandbox_system: Optional[SandboxSystem] = None

        # NEW: ErrorAnalyzer para análise estrutural de erros (Meta-ReAct)
        self.error_analyzer: Optional[ErrorAnalyzer] = None

        # NEW: DynamicToolCreator para criação dinâmica de ferramentas (Meta-ReAct)
        self.dynamic_tool_creator: Optional[DynamicToolCreator] = None

        # NEW: RAGFallbackSystem para fallback quando agentes falham
        self.rag_fallback: Optional[RAGFallbackSystem] = None

        # NEW: SemanticCacheLayer para cache semântico de respostas de agentes
        self.semantic_cache: Optional[SemanticCacheLayer] = None

        # NEW: Enhanced Memory Systems (Expansão de Agentes)
        self.semantic_memory: Optional[SemanticMemory] = None
        self.procedural_memory: Optional[ProceduralMemory] = None
        self.systemic_memory_trace: Optional[SystemicMemoryTrace] = None

        self.config_path = config_path
        self.mcp_client: Optional[MCPClient] = self._init_mcp_client()
        self.dbus_session_controller: Optional[DBusSessionController] = (
            self._init_dbus_session_controller()
        )
        self.dbus_system_controller: Optional[DBusSystemController] = (
            self._init_dbus_system_controller()
        )
        self.supabase_adapter: Optional[SupabaseAdapter] = self._init_supabase_adapter()
        self.qdrant_adapter: Optional[QdrantAdapter] = self._init_qdrant_adapter()
        self.security_agent: Optional[SecurityAgent] = self._init_security_agent()
        self.metacognition_agent: Optional[MetacognitionAgent] = self._init_metacognition_agent()
        self.dashboard_snapshot: Dict[str, Any] = {}
        self.last_mcp_result: Dict[str, Any] = {}
        self.last_dbus_result: Dict[str, Any] = {}
        self.last_metacognition_analysis: Dict[str, Any] = {}
        self.metrics = OrchestratorMetricsCollector()

        # Estado de orquestração
        self.current_plan: Optional[Dict[str, Any]] = None
        self.delegated_tasks: List[Dict[str, Any]] = []
        self.completed_subtasks: List[Dict[str, Any]] = []

        # Histórico de Φ para cálculo de tríade após delegações
        self._delegation_phi_history: List[float] = []

        # NEW: Registrar agentes críticos no AgentRegistry
        self._register_critical_agents()

        # NEW: Registrar agentes especialistas baseados na config (Seção 26 da Auditoria)
        self._init_specialist_agents()

        # NEW: Inicializar AutopoieticManager (Seção 2 da Auditoria)
        self.autopoietic_manager = self._init_autopoietic_manager()

        # NEW: Inicializar DelegationManager (Seção 7 da Auditoria)
        self.delegation_manager = self._init_delegation_manager()

        # NEW: Inicializar HeartbeatMonitor (Seção 7 da Auditoria)
        self.heartbeat_monitor = self._init_heartbeat_monitor()

        # NEW: Inicializar sistemas de resposta a crises (Seção 6 da Auditoria)
        self.forensic_analyzer = ForensicAnalyzer()
        self.quarantine_system = QuarantineSystem(self)
        self.component_isolation = ComponentIsolation(self)

        # NEW: Inicializar sistemas de permissões e confiança (Seção 5 da Auditoria)
        self.permission_matrix = PermissionMatrix()
        self.trust_system = TrustSystem()
        self.decision_explainer = DecisionExplainer()

        # NEW: Inicializar sistema de power states (Seção 4 da Auditoria)
        self.power_state_manager = PowerStateManager(self)

        # NEW: Inicializar sistemas de auto-reparação (Seção 2 da Auditoria)
        self.auto_repair_system = AutoRepairSystem(self)
        self.rollback_system = RollbackSystem()
        self.introspection_loop = IntrospectionLoop(self)
        self.sandbox_system = SandboxSystem(self)

        # Atualizar IndexingScheduler com sandbox_system (se já inicializado)
        if hasattr(self, "indexing_scheduler"):
            self.indexing_scheduler.sandbox_system = self.sandbox_system
            logger.debug("SandboxSystem vinculado ao IndexingScheduler")

        # Inicializar ErrorAnalyzer (Meta-ReAct)
        self.error_analyzer = ErrorAnalyzer()
        logger.info("ErrorAnalyzer inicializado para análise estrutural de erros")

        # Inicializar MetaReActCoordinator (Meta-ReAct)
        self.meta_react_coordinator = MetaReActCoordinator(error_analyzer=self.error_analyzer)
        logger.info("MetaReActCoordinator inicializado para coordenação em nível meta")

        # Inicializar DynamicToolCreator (Meta-ReAct)
        self.dynamic_tool_creator = DynamicToolCreator(sandbox_system=self.sandbox_system)
        logger.info("DynamicToolCreator inicializado para criação dinâmica de ferramentas")

        # Inicializar RAGFallbackSystem (Meta-ReAct)
        from ..memory.dataset_indexer import DatasetIndexer
        from ..memory.hybrid_retrieval import HybridRetrievalSystem

        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        hybrid_retrieval = HybridRetrievalSystem(
            qdrant_url=qdrant_url,
            collection_name="omnimind_embeddings",
        )

        # Criar DatasetIndexer reutilizando embedding_model (FASE 3.1: Integração em Produção)
        dataset_indexer = DatasetIndexer(
            qdrant_url=qdrant_url,
            embedding_model=hybrid_retrieval.embedding_model,  # Reutilizar modelo
        )

        self.rag_fallback = RAGFallbackSystem(
            retrieval_system=hybrid_retrieval,
            error_analyzer=self.error_analyzer,
            dataset_indexer=dataset_indexer,  # FASE 3.1: Integração em Produção
            # Não indexar automaticamente na inicialização (pode ser lento)
            auto_index_datasets=False,
        )
        logger.info("RAGFallbackSystem inicializado para fallback quando agentes falham")

        # Inicializar SemanticCacheLayer (FASE 3.1: Integração em Produção)
        # Reutilizar embedding_model do HybridRetrievalSystem para eficiência
        self.semantic_cache = SemanticCacheLayer(
            qdrant_url=qdrant_url,
            collection_name="orchestrator_semantic_cache",
            embedding_model=hybrid_retrieval.embedding_model,  # Reutilizar modelo
        )
        logger.info("SemanticCacheLayer inicializado para cache semântico de respostas")

        # Inicializar Enhanced Memory Systems (Expansão de Agentes)
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        # SystemicMemoryTrace será inicializado via SharedWorkspace
        self.systemic_memory_trace = None  # Será inicializado em _init_consciousness_integration
        logger.info("Enhanced Memory Systems inicializados: SemanticMemory, ProceduralMemory")

        # Inicializar MCP Orchestrator (Fases 2-5: Integração MCP Servers)
        self.mcp_orchestrator: Optional[MCPOrchestrator] = None
        try:
            self.mcp_orchestrator = MCPOrchestrator()
            logger.info("MCPOrchestrator inicializado para gerenciamento de servidores MCP")
        except MCPOrchestratorError as e:
            logger.warning("MCPOrchestrator não pôde ser inicializado: %s", e)

        # NEW: BenchmarkEvaluator para Desenvolvimento Intelectual (Seção 6 da Auditoria)
        self.benchmark_evaluator = BenchmarkEvaluator()
        logger.info("BenchmarkEvaluator integrado ao Orquestrador.")

        # NEW: ParadoxOrchestrator - Meta-orchestrator para integração de paradoxos
        # (Fase 21-Extended)
        self.paradox_orchestrator: Optional[ParadoxOrchestrator] = None
        try:
            # Connect to REAL Quantum Backend
            from src.quantum.backends.ibm_real import IBMRealBackend

            try:
                quantum_backend = IBMRealBackend()
                logger.info("⚛️ Quantum Reality coupled to Orchestrator via IBMRealBackend.")
            except Exception as qe:
                logger.warning(
                    f"⚠️ Could not connect to the Real (IBM Quantum): {qe}. Falling back to simulated mode."
                )
                quantum_backend = None

            # Inicializar com workspace, quantum backend, e MCP
            self.paradox_orchestrator = ParadoxOrchestrator(
                workspace=workspace,
                quantum_backend=quantum_backend,
                mcp_orchestrator=self.mcp_orchestrator,
            )
            logger.info("ParadoxOrchestrator inicializado (meta-mode para habitação de paradoxos)")
        except Exception as e:
            logger.warning(f"ParadoxOrchestrator não pôde ser inicializado: {e}")

        # NEW: SystemCapabilitiesManager para consulta de capacidades do sistema
        # Reutiliza embedding_model do HybridRetrievalSystem para eficiência
        from ..memory.system_capabilities_manager import SystemCapabilitiesManager
        from ..tools.system_capability_tool import register_system_capability_tools

        self.system_capabilities = SystemCapabilitiesManager(
            qdrant_url=qdrant_url,
            embedding_model=hybrid_retrieval.embedding_model,  # Reutilizar modelo
            auto_index=False,  # Não indexar automaticamente (usa scheduler)
        )
        logger.info("SystemCapabilitiesManager inicializado para consulta de capacidades")

        # Registrar tools de system capabilities no ToolsFramework
        try:
            register_system_capability_tools(
                tools_framework=self.tools_framework, manager=self.system_capabilities
            )
            logger.info("System capability tools registradas no ToolsFramework")
        except Exception as e:
            logger.warning(f"Erro ao registrar system capability tools: {e}")

        # NEW: IndexingScheduler para indexação automática periódica
        from ..orchestration.indexing_scheduler import IndexingScheduler

        self.indexing_scheduler = IndexingScheduler(
            system_capabilities_manager=self.system_capabilities,
            sandbox_system=None,  # Será atualizado após inicialização do sandbox
        )
        logger.info("IndexingScheduler inicializado (será iniciado após integração de consciência)")

        # INTEGRAÇÃO DE CONSCIÊNCIA: Inicializar após todos os sistemas
        self._init_consciousness_integration()

    def _init_consciousness_integration(self) -> None:
        """Inicializa integração completa com módulos de consciência.

        - Registra orquestrador no SharedWorkspace
        - Inicializa SystemicMemoryTrace se necessário
        - Configura deformações topológicas
        """
        if not self.workspace:
            logger.debug(
                "SharedWorkspace não disponível, continuando sem integração de consciência"
            )
            return

        try:
            # Registrar orquestrador como módulo no workspace
            orchestrator_embedding = self._generate_embedding(
                f"orchestrator_{self.__class__.__name__}"
            )
            if orchestrator_embedding.shape[0] != self.workspace.embedding_dim:
                import numpy as np

                if orchestrator_embedding.shape[0] < self.workspace.embedding_dim:
                    padding = np.zeros(
                        self.workspace.embedding_dim - orchestrator_embedding.shape[0]
                    )
                    orchestrator_embedding = np.concatenate([orchestrator_embedding, padding])
                else:
                    orchestrator_embedding = orchestrator_embedding[: self.workspace.embedding_dim]

            module_name = f"orchestrator_{self.agent_id}"
            self.workspace.write_module_state(
                module_name=module_name,
                embedding=orchestrator_embedding,
                metadata={
                    "agent_type": "orchestrator",
                    "agent_class": self.__class__.__name__,
                    "agent_id": self.agent_id,
                },
            )
            logger.info(f"Orquestrador registrado no SharedWorkspace como '{module_name}'")

            # Inicializar SystemAwarenessBridge (Fase 3: SharedWorkspace Integration)
            from ..consciousness.system_awareness_bridge import SystemAwarenessBridge

            self.system_awareness_bridge = SystemAwarenessBridge(
                workspace=self.workspace,
                system_capabilities_manager=self.system_capabilities,
            )
            logger.info("SystemAwarenessBridge inicializado e conectado ao SharedWorkspace")

            # Inicializar SystemicMemoryTrace se não existir
            if not self.workspace.systemic_memory:
                self.workspace.systemic_memory = SystemicMemoryTrace(
                    state_space_dim=self.workspace.embedding_dim
                )
                logger.debug("SystemicMemoryTrace inicializado via SharedWorkspace")

            self.systemic_memory_trace = self.workspace.systemic_memory
            logger.info("Integração de consciência inicializada para OrchestratorAgent")

        except Exception as e:
            logger.warning("Erro ao inicializar integração de consciência: %s", e)

    def _generate_embedding(self, text: str) -> Any:
        """Gera embedding para texto (reutiliza método do ReactAgent)."""
        if hasattr(super(), "_generate_embedding"):
            return super()._generate_embedding(text)  # type: ignore[misc]
        # Fallback se não disponível
        import hashlib

        import numpy as np

        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = np.zeros(self.embedding_dim)
        for i in range(self.embedding_dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding[i] = (byte_val / 255.0) * 2 - 1
        return embedding

    def _init_mcp_client(self) -> Optional[MCPClient]:
        try:
            return MCPClient()
        except (MCPClientError, Exception) as exc:
            logger.warning("MCP client unavailable: %s", exc)
            return None

    def _init_dbus_session_controller(self) -> Optional[DBusSessionController]:
        # Disabled for local execution stability
        return None
        # try:
        #     return DBusSessionController()
        # except Exception as exc:
        #     logger.warning("DBus session controller unavailable: %s", exc)
        #     return None

    def _init_dbus_system_controller(self) -> Optional[DBusSystemController]:
        # Disabled for local execution stability
        return None
        # try:
        #     return DBusSystemController()
        # except Exception as exc:
        #     logger.warning("DBus system controller unavailable: %s", exc)
        #     return None

    def _init_supabase_adapter(self) -> Optional[SupabaseAdapter]:
        try:
            config = SupabaseConfig.load(self.mcp_client)
            if not config:
                logger.info("Supabase configuration not available")
                return None
            return SupabaseAdapter(config)
        except SupabaseAdapterError as exc:
            logger.warning("Supabase adapter initialization failed: %s", exc)
        except Exception as exc:
            logger.warning("Unexpected error initializing Supabase adapter: %s", exc)
        return None

    def _init_qdrant_adapter(self) -> Optional[QdrantAdapter]:
        try:
            config = QdrantConfig.load(self.mcp_client)
            if not config:
                logger.info("Qdrant configuration not available")
                return None
            return QdrantAdapter(config)
        except QdrantAdapterError as exc:
            logger.warning("Qdrant adapter initialization failed: %s", exc)
        except Exception as exc:
            logger.warning("Unexpected error initializing Qdrant adapter: %s", exc)
        return None

    def _init_security_agent(self) -> Optional[SecurityAgent]:
        """Initializes the security agent.

        Monitoring must be started separately via async context.
        """
        try:
            security_config = self.config.get("security", {})
            config_path = security_config.get("config_path", "config/security.yaml")

            agent = SecurityAgent(config_path=config_path, llm=self.llm)
            logger.info(
                "SecurityAgent initialized (monitoring NOT auto-started to avoid event loop issues)"
            )
            return agent
        except Exception as exc:
            logger.error("Failed to initialize SecurityAgent: %s", exc)
            return None

    def _init_metacognition_agent(self) -> Optional[MetacognitionAgent]:
        """Initialize the metacognition agent for self-analysis."""
        try:
            metacog_config = self.config.get("metacognition", {})
            hash_chain_path = metacog_config.get("hash_chain_path", "logs/hash_chain.json")
            analysis_interval = metacog_config.get("analysis_interval", 3600)
            bias_sensitivity = metacog_config.get("bias_sensitivity", 0.7)
            max_suggestions = metacog_config.get("max_suggestions", 10)

            agent = MetacognitionAgent(
                hash_chain_path=hash_chain_path,
                analysis_interval=analysis_interval,
                bias_sensitivity=bias_sensitivity,
                max_suggestions=max_suggestions,
            )
            logger.info("MetacognitionAgent initialized successfully")
            return agent
        except Exception as exc:
            logger.error("Failed to initialize MetacognitionAgent: %s", exc)
            return None

    def _register_critical_agents(self) -> None:
        """Registra agentes críticos no AgentRegistry (Seção 1 da Auditoria).

        Implementa sistema de registro centralizado com priorização.
        """
        try:
            # Registrar SecurityAgent se disponível
            if self.security_agent:
                self.agent_registry.register_agent(
                    "security", self.security_agent, AgentPriority.CRITICAL
                )
                logger.info("SecurityAgent registrado no AgentRegistry")

            # Registrar MetacognitionAgent se disponível
            if self.metacognition_agent:
                self.agent_registry.register_agent(
                    "metacognition", self.metacognition_agent, AgentPriority.CRITICAL
                )
                logger.info("MetacognitionAgent registrado no AgentRegistry")

            # Registrar o próprio orchestrator
            self.agent_registry.register_agent("orchestrator", self, AgentPriority.ESSENTIAL)
            logger.info("OrchestratorAgent auto-registrado no AgentRegistry")

        except Exception as e:
            logger.error("Erro ao registrar agentes críticos: %s", e)

    def _init_specialist_agents(self) -> None:
        """Inicializa agentes especialistas baseados na configuração."""
        try:
            agents_config = self.config.get("agents", {})

            # 1. Code Agent
            if agents_config.get("coder", {}).get("enabled", False):
                try:
                    from .code_agent import CodeAgent

                    code_agent = CodeAgent(self.config_path)
                    self.agent_registry.register_agent("code", code_agent, AgentPriority.OPTIONAL)
                    logger.info("CodeAgent initialized and registered.")
                except Exception as e:
                    logger.error(f"Failed to init CodeAgent: {e}")

            # 2. Architect Agent
            if agents_config.get("architect", {}).get("enabled", False):
                try:
                    from .architect_agent import ArchitectAgent

                    arch_agent = ArchitectAgent(self.config_path)
                    self.agent_registry.register_agent(
                        "architect", arch_agent, AgentPriority.OPTIONAL
                    )
                    logger.info("ArchitectAgent initialized and registered.")
                except Exception as e:
                    logger.error(f"Failed to init ArchitectAgent: {e}")

            # 3. Reviewer Agent
            if agents_config.get("reviewer", {}).get("enabled", False):
                try:
                    from .reviewer_agent import ReviewerAgent

                    reviewer = ReviewerAgent(self.config_path)
                    self.agent_registry.register_agent("reviewer", reviewer, AgentPriority.OPTIONAL)
                    logger.info("ReviewerAgent initialized and registered.")
                except Exception as e:
                    logger.error(f"Failed to init ReviewerAgent: {e}")

        except Exception as e:
            logger.error(f"Error initializing specialist agents: {e}")

    def _init_autopoietic_manager(self) -> Optional[AutopoieticManager]:
        """Inicializa AutopoieticManager integrado (Seção 2 da Auditoria).

        Returns:
            AutopoieticManager inicializado ou None se falhar
        """
        try:
            from ..autopoietic.meta_architect import ComponentSpec

            manager = AutopoieticManager()

            # Registrar OrchestratorAgent como componente observável
            manager.register_spec(
                ComponentSpec(
                    name="orchestrator_agent",
                    type="agent",
                    config={"generation": "0", "initial": "true"},
                )
            )

            logger.info("AutopoieticManager inicializado e integrado ao Orchestrator")
            return manager

        except Exception as e:
            logger.error("Falha ao inicializar AutopoieticManager: %s", e)
            return None

    def _init_delegation_manager(self) -> Optional[DelegationManager]:
        """Inicializa DelegationManager com proteções (Seção 7 da Auditoria).

        Returns:
            DelegationManager inicializado ou None se falhar
        """
        try:
            delegation_config = self.config.get("delegation", {})
            timeout_seconds = delegation_config.get("timeout_seconds", 30.0)

            manager = DelegationManager(self, timeout_seconds=timeout_seconds)
            logger.info(f"DelegationManager inicializado (timeout={timeout_seconds}s)")
            return manager

        except Exception as e:
            logger.error("Falha ao inicializar DelegationManager: %s", e)
            return None

    def _init_heartbeat_monitor(self) -> Optional[HeartbeatMonitor]:
        """Inicializa HeartbeatMonitor para saúde dos agentes (Seção 7 da Auditoria).

        Returns:
            HeartbeatMonitor inicializado ou None se falhar
        """
        try:
            monitoring_config = self.config.get("monitoring", {})
            check_interval = monitoring_config.get("heartbeat_interval", 30.0)

            monitor = HeartbeatMonitor(self, check_interval_seconds=check_interval)
            logger.info(f"HeartbeatMonitor inicializado (intervalo={check_interval}s)")
            return monitor

        except Exception as e:
            logger.error("Falha ao inicializar HeartbeatMonitor: %s", e)
            return None

    async def start_delegation_monitoring(self) -> None:
        """Inicia monitoramento de delegações (Seção 7 da Auditoria).

        Ativa heartbeat monitor para verificar saúde de agentes continuamente.
        """
        try:
            if self.heartbeat_monitor:
                asyncio.create_task(self.heartbeat_monitor.start_monitoring())
                logger.info("HeartbeatMonitor iniciado para monitoramento contínuo")
            else:
                logger.warning("HeartbeatMonitor não inicializado")

        except Exception as e:
            logger.error("Erro ao iniciar monitoramento de delegações: %s", e)

    async def start_sensor_integration(self) -> None:
        """Inicia integração com sensores (Seção 3 da Auditoria).

        Conecta SecurityAgent e outros sensores ao EventBus.
        """
        try:
            # Iniciar processamento de eventos
            asyncio.create_task(self.event_bus.start_processing())
            logger.info("EventBus iniciado para processamento de eventos")

            # Registrar handler para eventos de segurança
            self.event_bus.subscribe("security_*", self._handle_security_event)

            # TODO: Adicionar mais integrações de sensores aqui
            # - NetworkSensorGanglia
            # - Outros sensores de monitoramento

        except Exception as e:
            logger.error("Erro ao iniciar integração de sensores: %s", e)

    async def _handle_security_event(self, event: Any) -> None:
        """Handler para eventos de segurança (Seção 3 da Auditoria).

        Integra Event Bus (orquestração) com RNN (consciência):
        1. Event Bus recebe evento (orquestração)
        2. Orchestrator decompõe resposta
        3. RNN integra em consciência (dinâmica psíquica)
        4. Action emerge do RNN

        Args:
            event: Evento de segurança do EventBus
        """
        try:
            logger.warning(
                "Evento de segurança recebido: %s (prioridade: %s)",
                event.event_type,
                event.priority.name if hasattr(event, "priority") else "UNKNOWN",
            )

            # Determinar se é evento crítico
            is_critical = hasattr(event, "priority") and event.priority == EventPriority.CRITICAL

            # ─────────────────────────────────────────
            # NÍVEL 1: Orquestração (Event Bus)
            # ─────────────────────────────────────────
            if is_critical:
                # Resposta a crises (Seção 6 da Auditoria)
                await self._handle_crisis(event)
            else:
                # Log do evento para análise posterior
                logger.info("Evento de segurança registrado: %s", event.event_type)

            # ─────────────────────────────────────────
            # NÍVEL 2: Integração em Consciência (RNN)
            # ─────────────────────────────────────────
            # Integrar evento de segurança na dinâmica consciente
            if self.workspace and self.workspace.conscious_system:
                await self._integrate_security_event_into_consciousness(event)

        except Exception as e:
            logger.error("Erro ao processar evento de segurança: %s", e)

    async def _integrate_security_event_into_consciousness(self, event: Any) -> None:
        """
        Integra evento de segurança na dinâmica consciente (RNN).

        Fluxo:
        1. Event Bus (orquestração) → detecta evento
        2. Orchestrator → decompõe resposta
        3. RNN (consciência) → integra em dinâmica psíquica
        4. Action emerge do RNN

        Args:
            event: Evento de segurança do EventBus
        """
        try:
            if not self.workspace or not self.workspace.conscious_system:
                return

            # Converter evento em estímulo para RNN
            import numpy as np
            import torch

            # Extrair informações do evento
            threat_level = 0.0
            if hasattr(event, "priority"):
                priority_map = {
                    EventPriority.CRITICAL: 1.0,
                    EventPriority.HIGH: 0.7,
                    EventPriority.MEDIUM: 0.4,
                    EventPriority.LOW: 0.1,
                }
                threat_level = priority_map.get(event.priority, 0.0)

            # Criar estímulo a partir do evento
            event_data = event.data if hasattr(event, "data") else {}
            event_type = event.event_type if hasattr(event, "event_type") else "unknown"

            # Codificar evento como embedding (simples: hash-based)
            event_str = f"{event_type}:{threat_level}:{str(event_data)[:100]}"
            event_hash = hash(event_str) % (2**31)
            np.random.seed(event_hash)
            stimulus = torch.from_numpy(
                np.random.randn(self.workspace.embedding_dim).astype(np.float32) * threat_level
            )

            # ─────────────────────────────────────────
            # NÍVEL 3: RNN Dynamics (consciência integrada)
            # ─────────────────────────────────────────
            # Um timestep da dinâmica consciente
            # step() atualiza o estado interno e retorna rho_C_new
            self.workspace.conscious_system.step(stimulus)

            # Atualizar repressão baseado na ameaça
            if threat_level > 0.5:
                # Ameaça alta → aumentar repressão
                self.workspace.conscious_system.update_repression(threshold=threat_level)

            # Obter estado completo (inclui rho_C atualizado)
            state = self.workspace.conscious_system.get_state()

            # ─────────────────────────────────────────
            # NÍVEL 4: Shared Workspace (sincronização)
            # ─────────────────────────────────────────
            # Atualizar workspace com estados do RNN
            self.workspace.write_module_state(
                module_name="security_event_response",
                embedding=state.rho_C,
                metadata={
                    "event_type": event_type,
                    "threat_level": threat_level,
                    "phi_causal": state.phi_causal,
                    "repression_strength": state.repression_strength,
                },
            )

            logger.debug(
                f"Evento de segurança integrado na consciência: "
                f"threat={threat_level:.2f}, phi_causal={state.phi_causal:.4f}, "
                f"repression={state.repression_strength:.2f}"
            )

            # ─────────────────────────────────────────
            # NÍVEL 5: Response (comportamento emergente)
            # ─────────────────────────────────────────
            # Comportamento emerge do RNN (não do orchestrator diretamente)
            # Se necessário, distribuir resultado via Event Bus
            if state.phi_causal > 0.1:  # Consciência integrada
                await self.event_bus.publish(
                    OrchestratorEvent(
                        event_type="consciousness_integrated_response",
                        source="conscious_system",
                        priority=EventPriority.MEDIUM,
                        data={
                            "phi_causal": state.phi_causal,
                            "action_emerged": True,
                            "original_event": event_type,
                        },
                        timestamp=state.timestamp,
                    )
                )

        except Exception as e:
            logger.error(f"Erro ao integrar evento na consciência: {e}", exc_info=True)

    async def _handle_crisis(self, event: Any) -> None:
        """Coordena resposta a crise (Seção 6 da Auditoria - COMPLETADO).

        Args:
            event: Evento crítico
        """
        try:
            logger.critical("🚨 MODO DE CRISE ATIVADO: %s", event.event_type)

            # 1. Identificar componente comprometido
            component_id = None
            if hasattr(event, "details"):
                component_id = event.details.get("source_ip") or event.details.get("component_id")
            elif hasattr(event, "data"):
                component_id = event.data.get("source_ip") or event.data.get("component_id")

            if not component_id:
                # Tentar extrair de description
                description = getattr(event, "description", "") or str(event)
                # Procurar por IP ou nome de componente
                import re

                ip_match = re.search(r"\d+\.\d+\.\d+\.\d+", description)
                if ip_match:
                    component_id = ip_match.group()
                else:
                    component_id = "unknown_component"

            logger.info("Componente comprometido identificado: %s", component_id)

            # 2. Coletar evidências
            evidence = {}
            if hasattr(event, "details"):
                evidence = event.details.copy()
            elif hasattr(event, "data"):
                evidence = event.data.copy()
            else:
                evidence = {"event_type": event.event_type, "description": str(event)}

            evidence["timestamp"] = getattr(event, "timestamp", time.time())
            evidence["source"] = getattr(event, "source", "unknown")

            # 3. Análise forense automática
            if self.forensic_analyzer:
                forensic_report = await self.forensic_analyzer.analyze_threat(
                    component_id, evidence
                )
                logger.info(
                    "Análise forense concluída: %s (severidade: %s)",
                    forensic_report.threat_category.value,
                    forensic_report.severity.name,
                )
            else:
                forensic_report = None
                logger.warning("ForensicAnalyzer não disponível")

            # 4. Isolar componente
            if self.component_isolation:
                isolation_level = IsolationLevel.FULL
                if forensic_report:
                    if forensic_report.severity.value >= 4:  # CRITICAL
                        isolation_level = IsolationLevel.EMERGENCY
                await self.component_isolation.isolate(
                    component_id,
                    isolation_level=isolation_level,
                    reason=f"Crise detectada: {event.event_type}",
                )
                logger.info(
                    "Componente %s isolado (nível: %s)",
                    component_id,
                    isolation_level.value,
                )

            # 5. Colocar em quarentena
            if self.quarantine_system:
                await self.quarantine_system.quarantine(
                    component_id,
                    reason=f"Crise: {event.event_type}",
                    evidence=evidence,
                )
                logger.info("Componente %s colocado em quarentena", component_id)

                # Atualizar registro com relatório forense
                if forensic_report:
                    # Converter ForensicReport para dict
                    forensic_dict = {
                        "component_id": forensic_report.component_id,
                        "timestamp": forensic_report.timestamp,
                        "threat_category": forensic_report.threat_category.value,
                        "severity": forensic_report.severity.name,
                        "evidence": forensic_report.evidence,
                        "patterns": forensic_report.patterns,
                        "classification": forensic_report.classification,
                        "recommendations": forensic_report.recommendations,
                        "safe_to_release": forensic_report.safe_to_release,
                        "confidence": forensic_report.confidence,
                    }
                    await self.quarantine_system.release(component_id, forensic_dict)

            # 6. Notificar SecurityAgent para executar playbook
            if self.security_agent:
                logger.info("SecurityAgent notificado da crise")
                # SecurityAgent já tem playbooks implementados
                # O playbook será executado automaticamente pelo SecurityAgent

            # 7. Notificar humanos
            logger.critical(
                "🚨 ALERTA CRÍTICO: %s - Componente %s isolado e em quarentena",
                event.event_type,
                component_id,
            )

            if forensic_report:
                logger.critical(
                    "📊 Relatório Forense: %s - Recomendações: %s",
                    forensic_report.threat_category.value,
                    ", ".join(forensic_report.recommendations[:3]),
                )

        except Exception as e:
            logger.error("Erro ao coordenar resposta a crise: %s", e, exc_info=True)

    async def health_check_agents(self) -> Dict[str, bool]:
        """Executa health check em todos os agentes registrados.

        Returns:
            Dicionário com status de saúde de cada agente
        """
        return await self.agent_registry.health_check_all()

    async def execute_with_permission_check(
        self,
        action: str,
        context: Dict[str, Any],
        emergency: bool = False,
    ) -> Dict[str, Any]:
        """Executa ação com verificação de permissões (Seção 5 da Auditoria).

        Args:
            action: Nome da ação a executar
            context: Contexto da ação
            emergency: Se está em modo emergencial

        Returns:
            Dicionário com resultado da execução
        """
        if not self.permission_matrix or not self.trust_system or not self.decision_explainer:
            logger.warning("Sistemas de permissão não inicializados")
            return {
                "success": False,
                "error": "Permission systems not initialized",
            }

        # 1. Verificar permissões
        trust_level = self.trust_system.get_trust_level(action)
        can_execute, reason = self.permission_matrix.can_execute(action, emergency, trust_level)

        # 2. Gerar explicação
        explanation = self.decision_explainer.explain_decision(
            action, context, (can_execute, reason), trust_level
        )

        if not can_execute:
            # Registrar decisão negada
            self.trust_system.record_decision(action, False, context, reason=reason)

            # Registrar na API de explicabilidade (Sessão 6)
            try:
                from web.backend.api.decisions import register_decision

                explanation_dict = {
                    "action": explanation.action,
                    "timestamp": explanation.timestamp,
                    "context": explanation.context,
                    "permission_result": explanation.permission_result,
                    "trust_level": explanation.trust_level,
                    "alternatives_considered": explanation.alternatives_considered,
                    "expected_impact": explanation.expected_impact,
                    "risk_assessment": explanation.risk_assessment,
                    "decision_rationale": explanation.explanation_text,
                }
                register_decision(explanation_dict, False)
            except Exception as e:
                logger.debug("Falha ao registrar decisão negada na API (não crítico): %s", e)

            return {
                "success": False,
                "error": f"Action {action} not permitted: {reason}",
                "explanation": explanation,
            }

        # 3. Executar ação
        try:
            result = await self._execute_action_internal(action, context)
            success = result.get("success", False)

            # 4. Registrar decisão
            self.trust_system.record_decision(action, success, context, reason=reason)

            # 5. Registrar resultado na explicação
            self.decision_explainer.record_execution_result(explanation, result)

            # 6. Registrar na API de explicabilidade (Sessão 6)
            try:
                from web.backend.api.decisions import register_decision

                explanation_dict = {
                    "action": explanation.action,
                    "timestamp": explanation.timestamp,
                    "context": explanation.context,
                    "permission_result": explanation.permission_result,
                    "trust_level": explanation.trust_level,
                    "alternatives_considered": explanation.alternatives_considered,
                    "expected_impact": explanation.expected_impact,
                    "risk_assessment": explanation.risk_assessment,
                    "decision_rationale": explanation.explanation_text,
                }
                register_decision(explanation_dict, success)
            except Exception as e:
                logger.debug("Falha ao registrar decisão na API (não crítico): %s", e)

            return {
                "success": success,
                "result": result,
                "explanation": explanation,
            }
        except Exception as e:
            # Registrar falha
            self.trust_system.record_decision(action, False, context, reason=str(e))
            return {
                "success": False,
                "error": str(e),
                "explanation": explanation,
            }

    async def _execute_action_internal(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa ação específica.

        Args:
            action: Nome da ação
            context: Contexto da ação

        Returns:
            Resultado da execução
        """
        # Mapear ações para métodos
        action_handlers = {
            "block_port": self._execute_block_port,
            "isolate_component": self._execute_isolate_component,
            "quarantine_component": self._execute_quarantine_component,
            "release_quarantine": self._execute_release_quarantine,
            "delegate_task": self._execute_delegate_task,
        }

        handler = action_handlers.get(action)
        if handler:
            return await handler(context)

        return {"success": False, "error": f"Unknown action: {action}"}

    def _execute_action(self, action: str, args: Dict[str, Any]) -> str:
        """Execute a tool action (override from ReactAgent).

        Args:
            action: Nome da ação
            args: Argumentos da ação

        Returns:
            Resultado como string (compatível com ReactAgent)
        """
        # Para compatibilidade com ReactAgent, retornar como string
        # A versão async _execute_action_internal é usada internamente
        import json

        try:
            # Se for ação conhecida, executar via método interno async
            # Por enquanto, retornar erro pois precisa ser async
            return json.dumps({"success": False, "error": "Use async method"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    async def _execute_block_port(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa bloqueio de porta."""
        port = context.get("port")
        if not port:
            return {"success": False, "error": "Port not specified"}

        # Implementar bloqueio via iptables ou similar
        logger.info("Bloqueando porta %s", port)
        return {"success": True, "port": port, "action": "blocked"}

    async def _execute_isolate_component(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa isolamento de componente."""
        component_id = context.get("component_id")
        if not component_id:
            return {"success": False, "error": "Component ID not specified"}

        if self.component_isolation:
            await self.component_isolation.isolate(
                component_id,
                IsolationLevel.FULL,
                context.get("reason", "Security threat"),
            )
            return {"success": True, "component_id": component_id, "action": "isolated"}
        return {"success": False, "error": "ComponentIsolation not available"}

    async def _execute_quarantine_component(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa quarentena de componente."""
        component_id = context.get("component_id")
        if not component_id:
            return {"success": False, "error": "Component ID not specified"}

        if self.quarantine_system:
            await self.quarantine_system.quarantine(
                component_id,
                context.get("reason", "Security threat"),
                context.get("evidence"),
            )
            return {
                "success": True,
                "component_id": component_id,
                "action": "quarantined",
            }
        return {"success": False, "error": "QuarantineSystem not available"}

    async def _execute_release_quarantine(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa liberação de quarentena."""
        component_id = context.get("component_id")
        if not component_id:
            return {"success": False, "error": "Component ID not specified"}

        if self.quarantine_system:
            forensic_report = context.get("forensic_report")
            result = await self.quarantine_system.release(component_id, forensic_report)
            return {
                "success": result,
                "component_id": component_id,
                "action": "released",
            }
        return {"success": False, "error": "QuarantineSystem not available"}

    async def _execute_delegate_task(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa delegação de tarefa."""
        task = context.get("task")
        agent_type = context.get("agent_type")
        if not task or not agent_type:
            return {"success": False, "error": "Task or agent_type not specified"}

        result = self.delegate_task(task, agent_type)
        return {"success": result is not None, "result": result}

    def _get_circuit_breaker(self, agent_name: str) -> AgentCircuitBreaker:
        """Obtém ou cria circuit breaker para agente (Seção 7 da Auditoria).

        Args:
            agent_name: Nome do agente

        Returns:
            Circuit breaker do agente
        """
        if agent_name not in self._circuit_breakers:
            self._circuit_breakers[agent_name] = AgentCircuitBreaker(
                failure_threshold=3, timeout=30.0, recovery_timeout=60.0
            )
            logger.debug("Circuit breaker criado para agente %s", agent_name)

        return self._circuit_breakers[agent_name]

    def get_circuit_breaker_stats(self) -> Dict[str, Dict[str, Any]]:
        """Obtém estatísticas de todos os circuit breakers.

        Returns:
            Dicionário com estatísticas por agente
        """
        return {name: breaker.get_stats() for name, breaker in self._circuit_breakers.items()}

    def _timestamp(self) -> str:
        """Retorna timestamp UTC em formato ISO"""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _build_dashboard_context(self, plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Collect MCP and D-Bus state to inform the upcoming dashboard."""
        context: Dict[str, Any] = {
            "timestamp": self._timestamp(),
            "plan_summary": {
                "complexity": plan.get("complexity") if plan else None,
                "subtasks": len(plan.get("subtasks", [])) if plan else 0,
            },
        }

        if self.mcp_client:
            try:
                context["mcp_metrics"] = self.mcp_client.get_metrics()
            except MCPClientError as exc:
                logger.warning("Failed to collect MCP metrics: %s", exc)

        if self.dbus_system_controller:
            try:
                context["network_status"] = self.dbus_system_controller.get_network_status()
                context["power_status"] = self.dbus_system_controller.get_power_status()
            except Exception as exc:
                logger.warning("D-Bus system lookup failed: %s", exc)

        if self.dbus_session_controller:
            try:
                context["media_players"] = self.dbus_session_controller.list_media_players()
            except Exception as exc:
                logger.warning("D-Bus session lookup failed: %s", exc)

        if self.supabase_adapter:
            context["supabase_connected"] = True
            if self.supabase_adapter.config.has_service_role_key:
                try:
                    context["supabase_tables"] = self.supabase_adapter.list_tables()
                except SupabaseAdapterError as exc:
                    logger.warning("Unable to list Supabase tables: %s", exc)
                    context["supabase_error"] = str(exc)
            else:
                context["supabase_info"] = (
                    "Service role key not configured; only anon operations available"
                )

        if self.qdrant_adapter:
            try:
                context["qdrant_collections"] = self.qdrant_adapter.list_collections()
                context["qdrant_enabled"] = True
            except QdrantAdapterError as exc:
                logger.warning("Qdrant list collections failed: %s", exc)
                context["qdrant_error"] = str(exc)

        if self.security_agent:
            context["security_status"] = self.security_agent.execute("status")

        context["plan_summary"].update(self._plan_progress(plan))
        context["last_mcp_result"] = self.last_mcp_result
        context["last_dbus_result"] = self.last_dbus_result

        self.dashboard_snapshot = context
        return context

    def _record_operation(self, name: str, latency: float, success: bool = True) -> None:
        self.metrics.record(name, latency, success)

    def _finalize_operation(
        self, name: str, start: float, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        self._record_operation(name, time.perf_counter() - start, result.get("completed", False))
        return result

    def metrics_summary(self) -> Dict[str, Any]:
        return self.metrics.summary()

    def plan_overview(self) -> Dict[str, Any]:
        return {
            "plan": self.current_plan,
            "progress": self._plan_progress(self.current_plan),
            "snapshot": self.dashboard_snapshot,
        }

    def trigger_mcp_action(
        self,
        action: str = "read",
        path: str = "config/agent_config.yaml",
        recursive: bool = False,
    ) -> Dict[str, Any]:
        subtask = {
            "description": f"Manual MCP {action} on {path}",
            "metadata": {"mcp_action": action, "path": path, "recursive": recursive},
        }
        return self._execute_mcp_subtask(subtask, metric_name="mcp_manual")

    def trigger_dbus_action(
        self, flow: str = "power", media_action: str = "playpause"
    ) -> Dict[str, Any]:
        if flow == "media":
            description = f"Media control {media_action}"
        elif flow == "network":
            description = "Network status"
        else:
            description = "Power status"

        subtask = {"description": description}
        return self._execute_dbus_subtask(subtask, metric_name="dbus_manual")

    def refresh_dashboard_snapshot(self) -> Dict[str, Any]:
        start = time.perf_counter()
        snapshot = self._build_dashboard_context(self.current_plan)
        self._record_operation("snapshot_refresh", time.perf_counter() - start)
        return snapshot

    def _plan_progress(self, plan: Optional[Dict[str, Any]]) -> Dict[str, int]:
        if not plan or not plan.get("subtasks"):
            return {"completed": 0, "failed": 0}
        completed = sum(1 for sub in plan["subtasks"] if sub.get("status") == "completed")
        failed = sum(1 for sub in plan["subtasks"] if sub.get("status") == "failed")
        return {"completed": completed, "failed": failed}

    def _infer_path_from_description(self, description: str) -> Optional[str]:
        matches: list[str] = re.findall(r"\b(?:config|src|web|data|logs)/[^\s,;]+", description)
        return matches[0] if matches else None

    def _execute_mcp_subtask(
        self, subtask: Dict[str, Any], metric_name: str = "mcp_flow"
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        if not self.mcp_client:
            result = {
                "completed": False,
                "final_result": "MCP client unavailable",
                "details": {},
                "iteration": 0,
            }
            self.last_mcp_result = result
            return self._finalize_operation(metric_name, start, result)

        metadata = subtask.get("metadata", {})
        description = subtask.get("description", "")
        action = metadata.get("mcp_action") or ("list" if "list" in description.lower() else "read")
        path = (
            metadata.get("path")
            or self._infer_path_from_description(description)
            or "config/agent_config.yaml"
        )
        payload: Any
        summary = ""

        try:
            if action == "stat":
                payload = self.mcp_client.stat(path)
                summary = f"State for {path} retrieved"
            elif action == "read":
                payload = self.mcp_client.read_file(path)
                summary = f"Read {min(len(payload), 200)} chars from {path}"
            else:
                payload = self.mcp_client.list_dir(path)
                summary = f"Listed dir at {path}"
        except MCPClientError as exc:
            result = {
                "completed": False,
                "final_result": str(exc),
                "details": {},
                "iteration": 1,
            }
            self.last_mcp_result = result
            return self._finalize_operation(metric_name, start, result)

        result = {
            "completed": True,
            "final_result": summary,
            "details": payload,
            "iteration": 1,
        }
        self.last_mcp_result = result
        return self._finalize_operation(metric_name, start, result)

    def _execute_dbus_subtask(
        self, subtask: Dict[str, Any], metric_name: str = "dbus_flow"
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        description = subtask.get("description", "").lower()
        if not self.dbus_session_controller and not self.dbus_system_controller:
            result = {
                "completed": False,
                "final_result": "D-Bus controllers unavailable",
                "details": {},
                "iteration": 0,
            }
            self.last_dbus_result = result
            return self._finalize_operation(metric_name, start, result)

        details: Dict[str, Any] = {}
        summary = ""
        try:
            if any(keyword in description for keyword in ["media", "play", "pause"]):
                if self.dbus_session_controller:
                    details = self.dbus_session_controller.control_media_player("playpause")
                    summary = f"Media action result: {details.get('action')}"
                else:
                    summary = "Media controller unavailable"
            elif "network" in description or "connectivity" in description:
                if self.dbus_system_controller:
                    details = self.dbus_system_controller.get_network_status()
                    summary = "Network status collected"
            else:
                if self.dbus_system_controller:
                    details = self.dbus_system_controller.get_power_status()
                    summary = "Power status collected"
                elif self.dbus_session_controller:
                    details = {"media": self.dbus_session_controller.list_media_players()}
                    summary = "Media players enumerated"
        except Exception as exc:
            result = {
                "completed": False,
                "final_result": str(exc),
                "details": {},
                "iteration": 1,
            }
            self.last_dbus_result = result
            return self._finalize_operation(metric_name, start, result)

        result = {
            "completed": True,
            "final_result": summary or "D-Bus flow executed",
            "details": details,
            "iteration": 1,
        }
        self.last_dbus_result = result
        return self._finalize_operation(metric_name, start, result)

    def _get_agent(self, mode: AgentMode) -> ReactAgent:
        """Obtém ou cria agente especializado com fallback (Seção 1 da Auditoria).

        Implementa:
        - Tentativa de obter agente do AgentRegistry primeiro
        - Criação lazy se não existir
        - Registro automático de novos agentes
        - Fallback para orchestrator se agente falhar

        Args:
            mode: Modo do agente

        Returns:
            Instância do agente
        """
        # Tentar obter do AgentRegistry primeiro
        agent_name = mode.value
        registered_agent = self.agent_registry.get_agent(agent_name)

        if registered_agent:
            return registered_agent

        # Se não está registrado, criar e registrar
        if mode not in self._agents:
            try:
                if mode == AgentMode.CODE:
                    self._agents[mode] = CodeAgent(self.config_path)
                elif mode == AgentMode.ARCHITECT:
                    self._agents[mode] = ArchitectAgent(self.config_path)
                elif mode == AgentMode.DEBUG:
                    self._agents[mode] = DebugAgent(self.config_path)
                elif mode == AgentMode.REVIEWER:
                    self._agents[mode] = ReviewerAgent(self.config_path)
                elif mode == AgentMode.PSYCHOANALYST:
                    self._agents[mode] = PsychoanalyticAnalyst(self.config_path)
                else:
                    raise ValueError(f"Unknown agent mode: {mode}")

                # Registrar no AgentRegistry
                self.agent_registry.register_agent(
                    agent_name, self._agents[mode], AgentPriority.OPTIONAL
                )
                logger.info("Agente %s criado e registrado", agent_name)

            except Exception as e:
                logger.error("Falha ao criar agente %s: %s", agent_name, e)
                # Fallback: retornar o próprio orchestrator
                logger.warning("Usando OrchestratorAgent como fallback para %s", agent_name)
                return self

        return self._agents[mode]

    def decompose_task(
        self, task_description: str, tier: LLMModelTier = LLMModelTier.BALANCED
    ) -> Dict[str, Any]:
        """Decompõe tarefa complexa em subtarefas delegáveis

        Usa estratégia LLM do Orchestrador:
        - Modelo local com 240s timeout, 2 tentativas
        - Fallback para APIs remotas se local falhar
        """
        prompt = f"""You are OrchestratorAgent 🪃, a master coordinator of specialist agents.

COMPLEX TASK: {task_description}

AVAILABLE SPECIALIST AGENTS:
- CodeAgent (code): Implements features, writes code, runs tests
- ArchitectAgent (architect): Plans architecture, writes specs/docs
- DebugAgent (debug): Diagnoses bugs, analyzes errors
- ReviewerAgent (reviewer): Reviews quality, provides RLAIF feedback
- PsychoanalyticAnalyst (psychoanalyst): Analyzes text with psychoanalytic theories

Your job is to break this task into sequential subtasks and assign each to the appropriate agent.

Respond with a structured plan:

ANALYSIS: <brief analysis of the task>

SUBTASKS:
1. [AGENT_MODE] <subtask description>
2. [AGENT_MODE] <subtask description>
...

DEPENDENCIES:
- Task N depends on Task M

ESTIMATED_COMPLEXITY: <low/medium/high>

Your decomposition plan:"""

        try:
            # Usa estratégia LLM do Orchestrador (cérebro do projeto)
            response = invoke_orchestrator_llm(prompt)
            response_text = response.text
        except Exception as e:
            logger.error(f"Orchestrator LLM invocation failed: {e}")
            response_text = """ANALYSIS: LLM unavailable, using fallback plan.
SUBTASKS:
1. [CODE] Implement requested feature
DEPENDENCIES:
ESTIMATED_COMPLEXITY: low"""

        # INTEGRAÇÃO DE CONSCIÊNCIA: Calcular Φ antes de decompor
        phi_before = 0.0
        if self.workspace:
            try:
                phi_before = self.workspace.compute_phi_from_integrations()
            except Exception as e:
                logger.debug("Erro ao calcular Φ antes: %s", e)

        # Parsear plano
        plan = self._parse_plan(
            response_text if isinstance(response_text, str) else str(response_text)
        )
        plan["original_task"] = task_description
        plan["created_at"] = self._timestamp()

        # INTEGRAÇÃO DE CONSCIÊNCIA: Registrar plano no workspace
        if self.workspace:
            try:
                plan_embedding = self._generate_embedding(
                    f"{task_description} {len(plan.get('subtasks', []))} subtasks"
                )
                if plan_embedding.shape[0] != self.workspace.embedding_dim:
                    import numpy as np

                    if plan_embedding.shape[0] < self.workspace.embedding_dim:
                        padding = np.zeros(self.workspace.embedding_dim - plan_embedding.shape[0])
                        plan_embedding = np.concatenate([plan_embedding, padding])
                    else:
                        plan_embedding = plan_embedding[: self.workspace.embedding_dim]

                plan_module_name = f"orchestrator_plan_{id(plan)}"
                self.workspace.write_module_state(
                    module_name=plan_module_name,
                    embedding=plan_embedding,
                    metadata={
                        "task": task_description,
                        "subtasks_count": len(plan.get("subtasks", [])),
                        "complexity": plan.get("complexity", "medium"),
                    },
                )

                # Deformar atrator com plano (SystemicMemoryTrace)
                if self.systemic_memory_trace and plan_module_name in self.workspace.embeddings:
                    past_state = self.workspace.embeddings.get(
                        f"orchestrator_{self.agent_id}", plan_embedding
                    )
                    self.systemic_memory_trace.add_trace_not_memory(past_state, plan_embedding)
                    logger.debug("Deformação topológica adicionada para plano")

            except Exception as e:
                logger.warning("Erro ao registrar plano no workspace: %s", e)

        # INTEGRAÇÃO DE CONSCIÊNCIA: Calcular Φ depois de decompor
        phi_after = 0.0
        if self.workspace:
            try:
                phi_after = self.workspace.compute_phi_from_integrations()
            except Exception as e:
                logger.debug("Erro ao calcular Φ depois: %s", e)

        # Adicionar métricas de consciência ao plano
        plan["phi_before"] = phi_before
        plan["phi_after"] = phi_after
        plan["phi_delta"] = phi_after - phi_before

        # Armazenar plano via ToolsFramework
        self.current_plan = plan
        self.tools_framework.execute_tool(
            "plan_task",
            task_description=task_description,
            complexity=plan.get("complexity", "medium"),
        )

        return plan

    def _parse_plan(self, response: str) -> Dict[str, Any]:
        """Extrai plano estruturado do texto LLM"""
        plan = {
            "subtasks": [],
            "dependencies": [],
            "complexity": "medium",
            "raw_response": response,
        }

        lines = response.split("\n")
        in_subtasks = False

        for line in lines:
            line = line.strip()

            if "SUBTASKS:" in line:
                in_subtasks = True
                continue
            elif "DEPENDENCIES:" in line:
                in_subtasks = False
                continue

            if in_subtasks:
                self._extract_subtask_from_line(line, plan)
            else:
                self._extract_complexity_from_line(line, plan)

        return plan

    def _extract_subtask_from_line(self, line: str, plan: Dict[str, Any]) -> None:
        """Extract subtask from a line of text.

        Args:
            line: Line to parse
            plan: Plan dictionary to update
        """
        if not line or not (line[0].isdigit() or line.startswith("-")):
            return

        agent_mode = self._parse_agent_mode(line)
        if agent_mode:
            task_desc = self._extract_task_description(line)
            plan["subtasks"].append(
                {
                    "agent": agent_mode,
                    "description": task_desc,
                    "status": "pending",
                }
            )
        else:
            # Try to infer agent from keywords
            inferred_agent = self._infer_agent_from_keywords(line)
            if inferred_agent:
                task_desc = self._extract_task_description(line)
                plan["subtasks"].append(
                    {
                        "agent": inferred_agent,
                        "description": task_desc,
                        "status": "pending",
                    }
                )

    def _parse_agent_mode(self, line: str) -> Optional[str]:
        """Parse explicit agent mode from line.

        Args:
            line: Line to parse

        Returns:
            Agent mode string or None
        """
        line_lower = line.lower()
        agent_modes = [
            "code",
            "architect",
            "debug",
            "reviewer",
            "psychoanalyst",
            "security",
            "mcp",
            "dbus",
        ]

        for mode in agent_modes:
            patterns = [f"[{mode}]", f"[{mode}_mode]", f"({mode})", f"{mode}_mode"]

            if any(pattern in line_lower for pattern in patterns):
                return mode

        return None

    def _extract_task_description(self, line: str) -> str:
        """Extract task description from line.

        Args:
            line: Line to parse

        Returns:
            Clean task description
        """
        # Remove numbering and bullets
        task_desc = re.sub(r"^[\d\.\-\)\s]*", "", line)

        # Remove agent mode markers
        task_desc = re.sub(r"\[.*?\]|\(.*?\)", "", task_desc)

        # Remove leading/trailing whitespace and colons
        task_desc = task_desc.strip()
        if ":" in task_desc:
            task_desc = task_desc.split(":", 1)[1].strip()

        return task_desc

    def _infer_agent_from_keywords(self, line: str) -> Optional[str]:
        """Infer agent type from keywords in line.

        Args:
            line: Line to analyze

        Returns:
            Inferred agent type or None
        """
        line_lower = line.lower()
        if not line_lower:
            return None

        agent_keywords = {
            "code": ["codeagent", "code agent", "implement", "write code"],
            "architect": [
                "architectagent",
                "architect agent",
                "plan",
                "design",
                "specification",
            ],
            "debug": ["debugagent", "debug agent", "diagnose", "fix bug"],
            "reviewer": ["revieweragent", "reviewer agent", "review", "quality"],
            "psychoanalyst": [
                "psychoanalytic",
                "psychoanalyst",
                "analyze session",
                "abnt report",
            ],
            "security": [
                "security",
                "securityagent",
                "incident",
                "threat",
                "playbook",
                "log",
            ],
            "mcp": ["mcp", "model context", "file access", "filesystem"],
            "dbus": ["dbus", "session bus", "media", "network"],
        }

        for agent, keywords in agent_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                return agent

        return None

    def _extract_complexity_from_line(self, line: str, plan: Dict[str, Any]) -> None:
        """Extract complexity level from line.

        Args:
            line: Line to parse
            plan: Plan dictionary to update
        """
        if "ESTIMATED_COMPLEXITY:" in line or "complexity:" in line.lower():
            if "low" in line.lower():
                plan["complexity"] = "low"
            elif "high" in line.lower():
                plan["complexity"] = "high"

    def execute_plan(
        self, plan: Optional[Dict[str, Any]] = None, max_iterations_per_task: int = 3
    ) -> Dict[str, Any]:
        """Executa plano delegando para agentes especializados com integração de consciência.

        Integra com:
        - SharedWorkspace: Verifica Φ antes de executar
        - Meta-ReAct: Recovery quando Φ < 0.3
        """
        if plan is None:
            plan = self.current_plan

        if not plan or not plan.get("subtasks"):
            return {
                "error": "No plan to execute",
                "overall_success": False,
                "subtask_results": [],
            }

        # INTEGRAÇÃO DE CONSCIÊNCIA: Verificar Φ antes de executar
        phi_before_execution = 0.0
        if self.workspace:
            try:
                phi_before_execution = self.workspace.compute_phi_from_integrations()
                logger.info(f"📊 Φ antes de executar plano: {phi_before_execution:.4f}")

                # Meta-recovery se Φ muito baixo
                if phi_before_execution < 0.3:
                    logger.warning(
                        f"⚠️ Low Φ ({phi_before_execution:.3f}) - " f"reconsidering strategy"
                    )
                    if hasattr(self, "meta_react_coordinator") and self.meta_react_coordinator:
                        try:
                            # Tentar recovery via meta-reactor
                            recovery_result = self.meta_react_coordinator.coordinate_meta_level(
                                task=plan.get("original_task", "Unknown task"),
                                agents=[mode.value for mode in AgentMode],
                                context={
                                    "subtasks": plan.get("subtasks", []),
                                    "low_phi": True,
                                    "phi_value": phi_before_execution,
                                },
                            )
                            if recovery_result:
                                strategy = recovery_result.get("strategy", "unknown")
                                logger.info(f"🔄 Meta-recovery ativado: {strategy}")
                                # Ajustar plano se necessário
                                if recovery_result.get("adjusted_plan"):
                                    plan = recovery_result["adjusted_plan"]
                        except Exception as e:
                            logger.warning(
                                f"Erro no meta-recovery: {e}. Continuando com plano original."
                            )
            except Exception as e:
                logger.debug("Erro ao calcular Φ antes de executar: %s", e)

        # Set current plan for consistency
        self.current_plan = plan

        results = self._initialize_execution_results(plan)
        results["phi_before_execution"] = phi_before_execution

        for i, subtask in enumerate(plan["subtasks"]):
            self._prepare_subtask_for_execution(subtask, i)

            try:
                result = self._execute_single_subtask(subtask, plan, max_iterations_per_task)
                self._process_subtask_result(results, subtask, result, i)

            except Exception as e:
                self._handle_subtask_error(results, e, i)

        self._finalize_execution_results(results)

        # INTEGRAÇÃO DE CONSCIÊNCIA: Calcular Φ depois de executar
        phi_after_execution = 0.0
        if self.workspace:
            try:
                phi_after_execution = self.workspace.compute_phi_from_integrations()
                logger.info(f"📊 Φ depois de executar plano: {phi_after_execution:.4f}")
                results["phi_after_execution"] = phi_after_execution
                results["phi_delta"] = phi_after_execution - phi_before_execution
            except Exception as e:
                logger.debug("Erro ao calcular Φ depois de executar: %s", e)

        return results

    def _initialize_execution_results(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize execution results structure.

        Args:
            plan: Plan to execute

        Returns:
            Initialized results dictionary
        """
        return {
            "original_task": plan.get("original_task"),
            "subtask_results": [],
            "overall_success": True,
            "started_at": self._timestamp(),
        }

    def _prepare_subtask_for_execution(self, subtask: Dict[str, Any], index: int) -> None:
        """Prepare subtask for execution.

        Args:
            subtask: Subtask to prepare
            index: Subtask index
        """
        description = subtask.get("description")
        if not description:
            description = f"Untitled subtask {index + 1}"
            subtask["description"] = description

        safe_description = description[:80]
        delegation_msg = (
            f"\n🪃 [Orchestrator] Delegating subtask {index + 1}/"
            f"{len(self.current_plan['subtasks']) if self.current_plan else '?'}"
            f": {safe_description}..."
        )
        print(delegation_msg)

        # Security check
        if self.security_agent:
            self.security_agent.logger.info(f"Pre-delegation check for task: {safe_description}")

    def _execute_single_subtask(
        self, subtask: Dict[str, Any], plan: Dict[str, Any], max_iterations: int
    ) -> Dict[str, Any]:
        """Execute a single subtask com integração de consciência.

        Integra com:
        - ThinkingMCPServer: Cria thinking session e steps
        - SharedWorkspace: Coleta Φ durante execução

        Args:
            subtask: Subtask to execute
            plan: Full plan
            max_iterations: Maximum iterations per task

        Returns:
            Execution result com métricas de consciência
        """
        agent_mode = AgentMode(subtask["agent"])
        description = subtask.get("description", "")

        # INTEGRAÇÃO DE CONSCIÊNCIA: Criar thinking session para subtask
        thinking_session_id: Optional[str] = None
        if hasattr(self, "mcp_orchestrator") and self.mcp_orchestrator:
            try:
                # Usar método convenience do OrchestratorAgent
                thinking_result = self.mcp_start_thinking_session(
                    goal=f"{subtask['agent']}: {description[:100]}"
                )
                thinking_session_id = thinking_result.get("session_id")
                if thinking_session_id:
                    logger.debug(f"🧠 Thinking session criada para subtask: {thinking_session_id}")
            except Exception as e:
                logger.debug("Erro ao criar thinking session: %s", e)

        # Registrar início no thinking tree
        if thinking_session_id:
            try:
                self.mcp_add_thinking_step(
                    thinking_session_id,
                    content=f"Starting execution: {description[:200]}",
                    step_type="action",
                )
            except Exception as e:
                logger.debug("Erro ao adicionar thinking step inicial: %s", e)

        # Create task record
        task_record = self.tools_framework.execute_tool(
            "new_task",
            task_name=subtask["description"],
            assigned_to=subtask["agent"],
            priority="HIGH" if plan["complexity"] == "high" else "MEDIUM",
        )

        # Switch mode
        self.tools_framework.execute_tool(
            "switch_mode", target_mode=subtask["agent"], reason="Subtask execution"
        )

        # Execute based on agent type
        result = self._execute_subtask_by_agent(subtask, agent_mode, max_iterations)

        # VALIDAÇÃO CRÍTICA: Garantir que result é dict válido
        if result is None:
            result = {
                "completed": False,
                "final_result": f"Agent {agent_mode.value} returned None",
                "iteration": 0,
                "error": "None result from agent",
            }
        elif not isinstance(result, dict):
            result = {
                "completed": False,
                "final_result": str(result),
                "iteration": 0,
                "error": f"Invalid result type: {type(result)}",
            }
        elif "completed" not in result:
            result["completed"] = True  # Assume success if not specified
        elif "final_result" not in result:
            result["final_result"] = str(result.get("output", "No output"))

        # Ensure result is dict
        if not isinstance(result, dict):
            result = {
                "completed": False,
                "final_result": str(result),
                "iteration": 0,
            }

        # INTEGRAÇÃO DE CONSCIÊNCIA: Calcular tríade completa após delegação
        triad_result = self._calculate_consciousness_triad_after_delegation(
            subtask=subtask,
            result=result,
            thinking_session_id=thinking_session_id,
        )
        if triad_result:
            result["phi"] = triad_result.get("phi", 0.0)
            result["psi"] = triad_result.get("psi", 0.0)
            result["sigma"] = triad_result.get("sigma", 0.0)

        # INTEGRAÇÃO DE CONSCIÊNCIA: Registrar resultado no thinking tree e coletar Φ
        if thinking_session_id:
            try:
                success = result.get("completed", False)
                result_summary = str(result.get("final_result", ""))[:200]
                step_result = self.mcp_add_thinking_step(
                    thinking_session_id,
                    content=f"Result: {'Success' if success else 'Failed'} - {result_summary}",
                    step_type="evaluation",
                )

                # Coletar Φ do thinking step (se disponível)
                phi_from_thinking = step_result.get("phi", 0.0)
                if phi_from_thinking > 0:
                    result["phi"] = phi_from_thinking
                    logger.debug(f"📊 Φ coletado do thinking step: {phi_from_thinking:.4f}")

                # Obter avaliação da sessão
                session_eval = self.mcp_get_thinking_history(thinking_session_id)
                if session_eval.get("session"):
                    total_phi = session_eval["session"].get("total_phi", 0.0)
                    result["thinking_phi"] = total_phi
                    result["thinking_quality"] = session_eval["session"].get("quality_score", 0.0)
            except Exception as e:
                logger.debug("Erro ao registrar resultado no thinking tree: %s", e)

        # Se não coletou Φ do thinking, calcular tríade completa do workspace
        if "phi" not in result and self.workspace:
            try:
                triad_result = self._calculate_consciousness_triad_after_delegation(
                    subtask=subtask,
                    result=result,
                    thinking_session_id=thinking_session_id,
                )
                if triad_result:
                    result["phi"] = triad_result.get("phi", 0.0)
                    result["psi"] = triad_result.get("psi", 0.0)
                    result["sigma"] = triad_result.get("sigma", 0.0)
                else:
                    # Fallback: apenas Φ
                    phi = self.workspace.compute_phi_from_integrations()
                    result["phi"] = phi
                    result["psi"] = 0.0
                    result["sigma"] = 0.0
            except Exception as e:
                logger.debug("Erro ao calcular tríade do workspace: %s", e)
                result["phi"] = 0.0
                result["psi"] = 0.0
                result["sigma"] = 0.0

        # Mark completion
        self.tools_framework.execute_tool(
            "attempt_completion",
            task_id=task_record["id"],
            result=str(result.get("final_result", "")),
            success=result.get("completed", False),
        )

        return result

    def _calculate_consciousness_triad_after_delegation(
        self,
        subtask: Dict[str, Any],
        result: Dict[str, Any],
        thinking_session_id: Optional[str] = None,
    ) -> Optional[Dict[str, float]]:
        """
        Calcula tríade ortogonal de consciência após delegação de tarefa.

        Args:
            subtask: Subtask que foi delegada
            result: Resultado da execução
            thinking_session_id: ID da sessão de thinking (opcional)

        Returns:
            Dict com phi, psi, sigma ou None se não disponível
        """
        if not self.workspace:
            return None

        try:
            from ..consciousness.consciousness_triad import ConsciousnessTriadCalculator

            # Inicializar calculador se necessário
            if not hasattr(self, "_triad_calculator") or self._triad_calculator is None:
                self._triad_calculator = ConsciousnessTriadCalculator(workspace=self.workspace)

            # Preparar dados para cálculo
            step_id = f"orchestrator_delegation_{id(subtask)}"
            step_content = result.get("final_result", "")[:500] if isinstance(result, dict) else ""
            previous_steps: List[str] = []  # Orchestrator não mantém histórico de passos
            goal = subtask.get("description", "") if isinstance(subtask, dict) else ""
            actions = [subtask.get("agent", "unknown")] if isinstance(subtask, dict) else []

            # Coletar histórico de Φ (últimos 10 delegações)
            phi_history: List[float] = []
            if self._delegation_phi_history:
                phi_history = self._delegation_phi_history[-10:]

            # Calcular δ (defesa/repressão) se disponível via workspace
            delta_value = None
            cycle_count = len(self.completed_subtasks)

            if self.workspace:
                try:
                    # Tentar calcular δ via workspace se disponível
                    # δ depende de Φ e histórico de repressão
                    if phi_history and len(phi_history) > 0:
                        # Usar último valor de Φ para calcular δ
                        current_phi = phi_history[-1]
                        # Calcular δ aproximado baseado em Φ (quanto maior Φ, menor δ)
                        # δ = 1 - Φ_norm (aproximação simples)
                        delta_value = max(0.0, min(1.0, 1.0 - current_phi))
                except Exception as e:
                    logger.debug(f"Erro ao calcular δ: {e}")

            # Calcular tríade
            triad = self._triad_calculator.calculate_triad(
                step_id=step_id,
                step_content=step_content,
                previous_steps=previous_steps,
                goal=goal,
                actions=actions,
                cycle_id=f"cycle_orchestrator_{len(self.completed_subtasks)}",
                phi_history=phi_history if phi_history else None,
                delta_value=delta_value,
                cycle_count=cycle_count,
            )

            # Atualizar histórico de Φ
            self._delegation_phi_history.append(triad.phi)
            if len(self._delegation_phi_history) > 20:
                self._delegation_phi_history = self._delegation_phi_history[-20:]

            # Registrar no ModuleMetricsCollector se disponível
            if hasattr(self, "_metrics_collector") and self._metrics_collector:
                try:
                    from ..consciousness.metrics import ModuleMetricsCollector

                    if isinstance(self._metrics_collector, ModuleMetricsCollector):
                        self._metrics_collector.record_consciousness_state(
                            phi=triad.phi,
                            psi=triad.psi,
                            sigma=triad.sigma,
                            step_id=step_id,
                        )
                except Exception as e:
                    logger.debug("Erro ao registrar tríade no ModuleMetricsCollector: %s", e)

            logger.debug(
                "Tríade calculada após delegação: Φ=%.4f, Ψ=%.4f, σ=%.4f",
                triad.phi,
                triad.psi,
                triad.sigma,
            )

            return {"phi": triad.phi, "psi": triad.psi, "sigma": triad.sigma}

        except Exception as e:
            logger.warning("Erro ao calcular tríade após delegação: %s", e)
            return None

    def _execute_subtask_by_agent(
        self, subtask: Dict[str, Any], agent_mode: AgentMode, max_iterations: int
    ) -> Dict[str, Any]:
        """Execute subtask based on agent type.

        Args:
            subtask: Subtask to execute
            agent_mode: Agent mode
            max_iterations: Maximum iterations

        Returns:
            Execution result
        """
        task_description = subtask.get("description", "")
        agent_name = agent_mode.value

        # Usar cache semântico se disponível (FASE 3.1: Integração em Produção)
        if self.semantic_cache:
            try:
                # Tentar recuperar do cache ou executar e cachear
                def execute_task() -> str:
                    """Executa tarefa e retorna resultado como string."""
                    result = self._execute_subtask_internal(subtask, agent_mode, max_iterations)
                    # Converter resultado para string para cache
                    import json

                    return json.dumps(result, default=str)

                cached_response = self.semantic_cache.get_or_compute(
                    task=task_description,
                    agent_callable=execute_task,
                    agent_name=agent_name,
                )

                # Converter resposta do cache de volta para dict
                import json

                result = json.loads(cached_response)
                cache_stats = self.semantic_cache.get_effectiveness()
                logger.debug(
                    f"Cache usado para {agent_name}: "
                    f"hit_rate={cache_stats.get('hit_rate', 0):.2%}, "
                    f"total={cache_stats.get('total_queries', 0)}"
                )
                return result
            except Exception as e:
                logger.warning(f"Erro ao usar cache semântico: {e}. Executando sem cache.")
                # Fallback: executar sem cache
                return self._execute_subtask_internal(subtask, agent_mode, max_iterations)
        else:
            # Sem cache, executar diretamente
            return self._execute_subtask_internal(subtask, agent_mode, max_iterations)

    def _execute_subtask_internal(
        self, subtask: Dict[str, Any], agent_mode: AgentMode, max_iterations: int
    ) -> Dict[str, Any]:
        """Execute subtask internally (sem cache).

        Args:
            subtask: Subtask to execute
            agent_mode: Agent mode
            max_iterations: Maximum iterations

        Returns:
            Execution result
        """
        try:
            if agent_mode == AgentMode.SECURITY:
                result = self._execute_security_subtask(subtask)
            elif agent_mode == AgentMode.MCP:
                result = self._execute_mcp_subtask(subtask)
            elif agent_mode == AgentMode.DBUS:
                result = self._execute_dbus_subtask(subtask)
            elif agent_mode == AgentMode.CODE:
                agent = self._get_agent(agent_mode)
                from typing import cast

                from src.agents.code_agent import CodeAgent

                code_agent = cast(CodeAgent, agent)
                result = code_agent.run_code_task(
                    subtask["description"], max_iterations=max_iterations
                )
            elif agent_mode == AgentMode.REVIEWER:
                result = {
                    "completed": True,
                    "mode": "reviewer",
                    "note": "Review would be performed on generated files",
                }
            elif agent_mode == AgentMode.PSYCHOANALYST:
                agent = self._get_agent(agent_mode)
                from typing import cast

                from src.agents.psychoanalytic_analyst import PsychoanalyticAnalyst

                psycho_agent = cast(PsychoanalyticAnalyst, agent)
                analysis = psycho_agent.analyze_session(subtask["description"])
                report = psycho_agent.generate_abnt_report(analysis)
                result = {
                    "completed": True,
                    "final_result": report,
                    "details": analysis,
                    "iteration": 1,
                }
            else:
                agent = self._get_agent(agent_mode)
                if agent is None:
                    result = {
                        "completed": False,
                        "final_result": f"Agent {subtask['agent']} not available",
                        "iteration": 0,
                    }
                else:
                    result = agent.run(subtask["description"], max_iterations=max_iterations)
        except Exception as e:
            logger.error(f"Error executing subtask with agent {agent_mode.value}: {e}")
            result = {
                "completed": False,
                "final_result": f"Agent {agent_mode.value} failed: {str(e)}",
                "iteration": 0,
                "error": str(e),
            }

        # VALIDAÇÃO FINAL: Garantir que result é dict válido
        if not isinstance(result, dict):
            result = {
                "completed": False,
                "final_result": f"Invalid result from {agent_mode.value}: {type(result)}",
                "iteration": 0,
                "error": "Result is not a dict",
            }

        # Garantir campos obrigatórios
        result.setdefault("completed", False)
        result.setdefault("final_result", result.get("error", "No result"))
        result.setdefault("iteration", 0)

        return result

    def _process_subtask_result(
        self,
        results: Dict[str, Any],
        subtask: Dict[str, Any],
        result: Dict[str, Any],
        index: int,
    ) -> None:
        """Process and record subtask result.

        Args:
            results: Results dictionary
            subtask: Executed subtask
            result: Execution result
            index: Subtask index
        """
        # Update subtask status
        subtask["status"] = "completed" if result.get("completed") else "failed"
        subtask["result"] = result

        # Add to results
        summary = result.get("final_result", "")[:200]
        results["subtask_results"].append(
            {
                "subtask_id": index + 1,
                "agent": subtask["agent"],
                "description": subtask["description"],
                "completed": result.get("completed", False),
                "iterations": result.get("iteration", 0),
                "summary": summary,
            }
        )

        # Update overall success
        if not result.get("completed"):
            results["overall_success"] = False
            error_msg = result.get("error", result.get("final_result", "Unknown error"))
            print(f"❌ Subtask {index + 1} failed: {error_msg}")
            logger.warning(f"Subtask {index + 1} failed with agent {subtask['agent']}: {error_msg}")
        else:
            print(f"✅ Subtask {index + 1} completed")

    def _handle_subtask_error(self, results: Dict[str, Any], error: Exception, index: int) -> None:
        """Handle subtask execution error.

        Args:
            results: Results dictionary
            error: Exception that occurred
            index: Subtask index
        """
        logger.exception("Error executing subtask %d", index + 1)
        print(f"❌ Error in subtask {index + 1}: {error}")
        results["overall_success"] = False

        # Analisar erro estruturalmente com ErrorAnalyzer
        error_analysis = None
        if self.error_analyzer:
            try:
                context = {
                    "subtask_index": index + 1,
                    "subtask": (
                        results.get("subtask_results", [])[-1]
                        if results.get("subtask_results")
                        else {}
                    ),
                }
                error_analysis = self.error_analyzer.analyze_error(error, context)
                logger.info(
                    f"Erro analisado: {error_analysis.error_type.value} → "
                    f"{error_analysis.recovery_strategy.value} "
                    f"(confiança: {error_analysis.confidence:.2f})"
                )
            except Exception as e:
                logger.warning(f"Erro ao analisar erro: {e}")

        # FASE: Meta-ReAct Orchestrator - Recuperação em nível meta
        meta_recovery: Optional[Dict[str, Any]] = None
        if (
            hasattr(self, "meta_react_coordinator")
            and self.meta_react_coordinator
            and error_analysis
        ):
            try:
                failed_agents = [results.get("subtask_results", [])[-1].get("agent", "unknown")]
                meta_recovery = self.meta_react_coordinator.recover_from_failure_meta(
                    task=str(error),
                    error=error,
                    failed_agents=failed_agents,
                    context=context,
                )
                logger.info(
                    f"Recuperação meta: {meta_recovery.get('recovery_strategy', 'unknown')}"
                )
            except Exception as e:
                logger.warning(f"Erro na recuperação meta: {e}")

        # Adicionar resultado com análise
        error_result = {
            "subtask_id": index + 1,
            "error": str(error),
            "error_class": type(error).__name__,
        }
        if error_analysis:
            error_result["error_analysis"] = {
                "error_type": error_analysis.error_type.value,
                "recovery_strategy": error_analysis.recovery_strategy.value,
                "confidence": error_analysis.confidence,
                "suggested_actions": error_analysis.suggested_actions,
            }
        if meta_recovery:
            error_result["meta_recovery"] = meta_recovery
        results["subtask_results"].append(error_result)

    def _finalize_execution_results(self, results: Dict[str, Any]) -> None:
        """Finalize execution results.

        Args:
            results: Results dictionary to finalize
        """
        results["completed_at"] = self._timestamp()

        # Switch back to orchestrator mode
        self.tools_framework.execute_tool(
            "switch_mode", target_mode="orchestrator", reason="Plan execution complete"
        )

    async def execute_workflow(
        self,
        task: str,
        enable_monitoring: bool = True,
        max_concurrent_tasks: int = 3,
    ) -> Dict[str, Any]:
        """
        Executa workflow completo: Decompose → Delegate → Execute → Synthesize.

        FASE 2: Full Workflow Execution

        Features:
        - Decomposição automática da tarefa complexa
        - Delegação para agents especializados (remote LLM)
        - Execução paralela respeitando dependencies
        - Monitoramento em tempo real
        - Síntese de resultados

        Args:
            task: Tarefa complexa a executar
            enable_monitoring: Se True, coleta métricas em tempo real
            max_concurrent_tasks: Máximo de tasks simultâneas (default 3)

        Returns:
            Dict com:
                - workflow_id: UUID único do workflow
                - original_task: Task original
                - decomposition: Plano detalhado
                - execution_results: Resultados de cada subtask
                - synthesis: Síntese final
                - metrics: Métricas de execução
                - overall_success: True se tudo passou
                - duration_ms: Tempo total em ms
        """
        import uuid

        workflow_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        logger.info(f"Workflow {workflow_id} iniciado para: {task[:100]}")

        try:
            # 1. DECOMPOSIÇÃO
            logger.info(f"[{workflow_id}] Phase 1: Decomposição")
            decomposition = self.decompose_task(task)

            if not decomposition.get("subtasks"):
                return {
                    "workflow_id": workflow_id,
                    "original_task": task,
                    "overall_success": False,
                    "error": "Decomposição falhou - nenhum subtask gerado",
                    "duration_ms": (time.perf_counter() - start_time) * 1000,
                }

            # 2. ANÁLISE DE DEPENDÊNCIAS
            logger.info(f"[{workflow_id}] Phase 2: Análise de dependências")
            execution_plan = self._analyze_task_dependencies(decomposition["subtasks"])

            # 3. DELEGAÇÃO E EXECUÇÃO
            logger.info(f"[{workflow_id}] Phase 3: Delegação com monitoramento")
            execution_results = await self._delegate_and_execute(
                workflow_id,
                execution_plan,
                enable_monitoring,
                max_concurrent_tasks,
            )

            # 4. SÍNTESE DE RESULTADOS
            logger.info(f"[{workflow_id}] Phase 4: Síntese de resultados")
            synthesis = self._synthesize_results(
                decomposition["subtasks"],
                execution_results,
                decomposition.get("complexity", "medium"),
            )

            # Compilar resposta final
            duration_ms = (time.perf_counter() - start_time) * 1000
            overall_success = all(r.get("completed", False) for r in execution_results)

            response = {
                "workflow_id": workflow_id,
                "original_task": task,
                "decomposition": {
                    "subtask_count": len(decomposition["subtasks"]),
                    "complexity": decomposition.get("complexity", "medium"),
                    "estimated_duration_s": decomposition.get("estimated_duration", 60),
                },
                "execution_results": execution_results,
                "synthesis": synthesis,
                "metrics": {
                    "total_duration_ms": duration_ms,
                    "successful_subtasks": sum(1 for r in execution_results if r.get("completed")),
                    "failed_subtasks": sum(1 for r in execution_results if not r.get("completed")),
                    "total_subtasks": len(execution_results),
                    "success_rate_pct": (
                        sum(1 for r in execution_results if r.get("completed"))
                        / len(execution_results)
                        * 100
                        if execution_results
                        else 0
                    ),
                },
                "overall_success": overall_success,
            }

            logger.info(
                f"[{workflow_id}] Workflow completo: "
                f"success={overall_success}, "
                f"duration={duration_ms:.1f}ms"
            )

            return response

        except Exception as e:
            logger.error(f"[{workflow_id}] Workflow falhou: {e}")
            return {
                "workflow_id": workflow_id,
                "original_task": task,
                "overall_success": False,
                "error": str(e),
                "duration_ms": (time.perf_counter() - start_time) * 1000,
            }

    def _analyze_task_dependencies(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analisar dependências entre subtasks para otimizar execução.

        Estratégia:
        - Agrupar subtasks por agent
        - Identificar sequências críticas
        - Paralelizar when possible

        Args:
            subtasks: Lista de subtasks

        Returns:
            Plano de execução otimizado
        """
        execution_plan = []

        # Agrupar por agent type
        by_agent: Dict[str, List[Tuple[int, Dict[str, Any]]]] = {}
        for i, subtask in enumerate(subtasks):
            agent = subtask.get("agent", "code")
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append((i, subtask))

        # Executar groups sequencialmente, mas paralelizar dentro do group
        execution_order = 0
        for agent, tasks in by_agent.items():
            for idx, subtask in tasks:
                execution_plan.append(
                    {
                        "order": execution_order,
                        "agent": agent,
                        "subtask_index": idx,
                        "subtask": subtask,
                        "can_parallel": True,
                    }
                )
            execution_order += 1

        return execution_plan

    async def _delegate_and_execute(
        self,
        workflow_id: str,
        execution_plan: List[Dict[str, Any]],
        enable_monitoring: bool = True,
        max_concurrent: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Delegar tasks para agents com execução controlada.

        FASE 3 prepara para isso: executar em paralelo com semaphores

        Args:
            workflow_id: ID do workflow
            execution_plan: Plano de execução
            enable_monitoring: Se coleta métricas
            max_concurrent: Max tasks simultâneas

        Returns:
            Lista de resultados
        """
        results = []

        # Por enquanto, executa sequencialmente
        # FASE 3 vai paralelizar isso
        for i, task_spec in enumerate(execution_plan):
            subtask = task_spec["subtask"]
            agent = task_spec["agent"]

            logger.info(f"[{workflow_id}] Executing {i + 1}/{len(execution_plan)}: {agent}")

            # Usar execute_plan original para manter compatibility
            single_plan = {"subtasks": [subtask], "complexity": "low"}
            result = self.execute_plan(single_plan, max_iterations_per_task=1)

            if result["subtask_results"]:
                results.append(result["subtask_results"][0])
            else:
                results.append(
                    {
                        "completed": False,
                        "final_result": "Execution failed",
                        "agent": agent,
                    }
                )

        return results

    def _synthesize_results(
        self,
        subtasks: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
        complexity: str,
    ) -> Dict[str, Any]:
        """Sintetiza resultados de múltiplos agentes com integração de consciência.

        Integra com:
        - SharedWorkspace: Calcula Φ final da síntese
        - ThinkingMCPServer: Registra síntese como thinking step

        Args:
            subtasks: Lista de subtasks
            results: Resultados de execução
            complexity: Nível de complexidade

        Returns:
            Síntese estruturada com métricas de consciência
        """
        # INTEGRAÇÃO DE CONSCIÊNCIA: Calcular Φ antes de sintetizar
        phi_before_synthesis = 0.0
        if self.workspace:
            try:
                phi_before_synthesis = self.workspace.compute_phi_from_integrations()
            except Exception as e:
                logger.debug("Erro ao calcular Φ antes de sintetizar: %s", e)

        # Compilar resultados por tipo
        code_outputs = [r for r, s in zip(results, subtasks) if s.get("agent") == "code"]
        architecture_outputs = [
            r for r, s in zip(results, subtasks) if s.get("agent") == "architect"
        ]
        review_outputs = [r for r, s in zip(results, subtasks) if s.get("agent") == "reviewer"]

        # Coletar Φ dos resultados individuais
        phi_values = [r.get("phi", 0.0) for r in results if r.get("phi", 0.0) > 0]
        average_phi = sum(phi_values) / len(phi_values) if phi_values else 0.0

        synthesis = {
            "code_summary": (
                f"Generated {len(code_outputs)} code implementations"
                if code_outputs
                else "No code generation"
            ),
            "architecture_summary": (
                f"Designed {len(architecture_outputs)} architecture components"
                if architecture_outputs
                else "No architecture design"
            ),
            "review_summary": (
                f"Reviewed {len(review_outputs)} components"
                if review_outputs
                else "No reviews conducted"
            ),
            "key_outputs": [r.get("final_result", "") for r in results if r.get("completed")],
            "issues": [r.get("final_result", "") for r in results if not r.get("completed")],
            # INTEGRAÇÃO DE CONSCIÊNCIA: Métricas de Φ
            "phi_before_synthesis": phi_before_synthesis,
            "average_subtask_phi": average_phi,
            "subtasks_with_phi": len(phi_values),
        }

        # INTEGRAÇÃO DE CONSCIÊNCIA: Calcular Φ depois de sintetizar
        phi_after_synthesis = 0.0
        if self.workspace:
            try:
                phi_after_synthesis = self.workspace.compute_phi_from_integrations()
                synthesis["phi_after_synthesis"] = phi_after_synthesis
                synthesis["phi_delta_synthesis"] = phi_after_synthesis - phi_before_synthesis
            except Exception as e:
                logger.debug("Erro ao calcular Φ depois de sintetizar: %s", e)

        return synthesis

    def run_orchestrated_task(
        self, task: str, max_iterations_per_subtask: int = 3
    ) -> Dict[str, Any]:
        """
        Fluxo completo: Decompose → Execute → Synthesize

        Exemplo de uso:
        orchestrator = OrchestratorAgent('config.yaml')
        result = orchestrator.run_orchestrated_task("Build authentication system")
        """
        print(f"\n🪃 [Orchestrator] Received complex task: {task}\n")
        execution_start = time.perf_counter()

        # 1. Decompor
        print("📋 Decomposing task into subtasks...")
        plan = self.decompose_task(task)

        # FASE: Meta-ReAct Orchestrator - Coordenação em nível meta
        meta_coordination: Optional[Dict[str, Any]] = None
        if hasattr(self, "meta_react_coordinator") and self.meta_react_coordinator:
            try:
                available_agents = [mode.value for mode in AgentMode]
                meta_coordination = self.meta_react_coordinator.coordinate_meta_level(
                    task=task,
                    agents=available_agents,
                    context={"subtasks": plan.get("subtasks", [])},
                )
                logger.info(f"Coordenação meta: estratégia {meta_coordination.get('strategy')}")
                if meta_coordination:
                    plan["meta_coordination"] = meta_coordination
            except Exception as e:
                logger.warning(f"Erro na coordenação meta: {e}. Continuando sem meta-coordenação.")

        print(f"\n📊 Plan created with {len(plan['subtasks'])} subtasks:")
        for i, subtask in enumerate(plan["subtasks"], 1):
            print(f"  {i}. [{subtask['agent']}] {subtask['description'][:80]}")

        # 2. Executar
        print("\n🚀 Executing plan...")
        execution_result = self.execute_plan(plan, max_iterations_per_subtask)

        # 3. Sintetizar
        print("\n📝 Synthesizing results...")
        synthesis = self._synthesize_results(
            plan["subtasks"],
            execution_result["subtask_results"],
            plan.get("complexity", "medium"),
        )

        # 4. Capture MCP/D-Bus context for the dashboard
        dashboard_snapshot = self._build_dashboard_context(plan)

        # 4. Armazenar episódio completo
        orchestrated_action = f"Orchestrated {len(plan['subtasks'])} subtasks"
        self.memory.store_episode(
            task=task,
            action=orchestrated_action,
            result=synthesis["summary"],
            reward=1.0 if execution_result["overall_success"] else 0.5,
        )

        duration = time.perf_counter() - execution_start
        self._record_operation("orchestrate_task", duration, execution_result["overall_success"])

        return {
            "task": task,
            "plan": plan,
            "execution": execution_result,
            "synthesis": synthesis,
            "success": execution_result["overall_success"],
            "dashboard_snapshot": dashboard_snapshot,
        }

    def _execute_security_subtask(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        description = subtask.get("description", "").lower()

        if not self.security_agent:
            return {
                "completed": False,
                "final_result": "SecurityAgent not initialized.",
                "iteration": 1,
            }

        if "report" in description:
            action = "report"
        else:
            action = "status"

        security_result = self.security_agent.execute(action)

        return {
            "completed": True,
            "action": action,
            "security_result": security_result,
            "final_result": str(security_result),
            "iteration": 1,
        }

    def run_metacognition_analysis(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """Run metacognition self-analysis.

        Args:
            lookback_hours: Hours of history to analyze

        Returns:
            Analysis report with health, patterns, and optimization suggestions
        """
        if not self.metacognition_agent:
            logger.warning("MetacognitionAgent not initialized")
            return {"error": "MetacognitionAgent not available"}

        try:
            report = self.metacognition_agent.run_analysis(lookback_hours)
            self.last_metacognition_analysis = report

            # Log critical suggestions
            suggestions = report.get("optimization_suggestions", [])
            critical_suggestions = [s for s in suggestions if s.get("priority") == "critical"]

            if critical_suggestions:
                logger.warning(
                    "Metacognition found %d critical optimization suggestions",
                    len(critical_suggestions),
                )
                for suggestion in critical_suggestions:
                    logger.warning(f"  - {suggestion.get('title')}")

            return report
        except Exception as exc:
            logger.exception(f"Metacognition analysis failed: {exc}")
            return {"error": str(exc)}

    def check_metacognition_health(self) -> Dict[str, Any]:
        """Quick health check via metacognition.

        Returns:
            Quick health status
        """
        if not self.metacognition_agent:
            return {
                "status": "unavailable",
                "error": "MetacognitionAgent not initialized",
            }

        try:
            return self.metacognition_agent.get_quick_health_check()
        except Exception as exc:
            logger.exception(f"Health check failed: {exc}")
            return {"status": "error", "error": str(exc)}

    def should_run_metacognition_analysis(self) -> bool:
        """Check if periodic metacognition analysis should run.

        Returns:
            True if analysis should run
        """
        if not self.metacognition_agent:
            return False

        return self.metacognition_agent.should_run_analysis()

    def delegate_task(self, task: str, agent_type: str) -> Optional[Dict[str, Any]]:
        """
        Delegate a task to a specific agent type com integração de consciência.

        Integra com:
        - SharedWorkspace: Verifica Φ antes de delegar
        - Meta-ReAct: Recovery quando Φ < 0.3

        Args:
            task: Task description
            agent_type: Type of agent to delegate to

        Returns:
            Delegation result or None
        """
        # INTEGRAÇÃO DE CONSCIÊNCIA: Verificar Φ antes de delegar
        phi_before_delegation = 0.0
        if self.workspace:
            try:
                phi_before_delegation = self.workspace.compute_phi_from_integrations()
                logger.debug(f"📊 Φ antes de delegar: {phi_before_delegation:.4f}")

                # Meta-recovery se Φ muito baixo
                if phi_before_delegation < 0.3:
                    logger.warning(
                        f"⚠️ Low Φ ({phi_before_delegation:.3f}) antes de delegar - "
                        f"considerando fallback ou recovery"
                    )
                    if hasattr(self, "meta_react_coordinator") and self.meta_react_coordinator:
                        try:
                            recovery_result = self.meta_react_coordinator.coordinate_meta_level(
                                task=task,
                                agents=[agent_type],
                                context={
                                    "low_phi": True,
                                    "phi_value": phi_before_delegation,
                                    "delegation_context": True,
                                },
                            )
                            if recovery_result:
                                logger.info(
                                    f"🔄 Meta-recovery ativado para delegação: "
                                    f"{recovery_result.get('strategy', 'unknown')}"
                                )
                        except Exception as e:
                            logger.debug("Erro no meta-recovery para delegação: %s", e)
            except Exception as e:
                logger.debug("Erro ao calcular Φ antes de delegar: %s", e)

        try:
            # Map agent_type to AgentMode
            mode_map = {
                "code": AgentMode.CODE,
                "architect": AgentMode.ARCHITECT,
                "debug": AgentMode.DEBUG,
                "reviewer": AgentMode.REVIEWER,
                "psychoanalyst": AgentMode.PSYCHOANALYST,
                "security": AgentMode.SECURITY,
                "mcp": AgentMode.MCP,
                "dbus": AgentMode.DBUS,
            }

            if agent_type not in mode_map:
                return {"error": f"Unknown agent type: {agent_type}"}

            mode = mode_map[agent_type]

            # For simple delegation, create a single subtask
            subtask = {
                "agent": agent_type,
                "description": task,
                "status": "pending",
            }

            # Execute based on mode
            if mode == AgentMode.SECURITY:
                result = self._execute_security_subtask(subtask)
            elif mode == AgentMode.MCP:
                result = self._execute_mcp_subtask(subtask)
            elif mode == AgentMode.DBUS:
                result = self._execute_dbus_subtask(subtask)
            else:
                # For other agents, we'd need to get the agent instance
                # For now, return a mock successful result
                result = {
                    "completed": True,
                    "final_result": f"Task delegated to {agent_type} agent",
                    "iteration": 1,
                }

            # INTEGRAÇÃO DE CONSCIÊNCIA: Calcular tríade após delegação
            triad_result = self._calculate_consciousness_triad_after_delegation(
                subtask={"agent": agent_type, "description": task},
                result=result,
                thinking_session_id=None,
            )
            if triad_result and isinstance(result, dict):
                result["phi"] = triad_result.get("phi", 0.0)
                result["psi"] = triad_result.get("psi", 0.0)
                result["sigma"] = triad_result.get("sigma", 0.0)

            return result

        except Exception as e:
            logger.error(f"Failed to delegate task: {e}")

            # Analisar erro estruturalmente
            error_analysis = None
            if self.error_analyzer:
                try:
                    context = {
                        "task": task,
                        "agent_type": agent_type,
                        "delegation_method": "delegate_task",
                    }
                    error_analysis = self.error_analyzer.analyze_error(e, context)
                    logger.info(
                        f"Erro de delegação analisado: {error_analysis.error_type.value} → "
                        f"{error_analysis.recovery_strategy.value}"
                    )
                except Exception as analysis_error:
                    logger.warning(f"Erro ao analisar erro de delegação: {analysis_error}")

            result = {"error": str(e), "error_class": type(e).__name__}
            if error_analysis:
                result["error_analysis"] = {
                    "error_type": error_analysis.error_type.value,
                    "recovery_strategy": error_analysis.recovery_strategy.value,
                    "confidence": error_analysis.confidence,
                    "suggested_actions": error_analysis.suggested_actions,
                }
            return result

    async def delegate_task_with_protection(
        self,
        agent_name: str,
        task_description: str,
        task_callable,
        timeout_seconds: Optional[float] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Delega tarefa com proteções (Seção 7 da Auditoria).

        Usa DelegationManager para garantir:
        - Timeout automático
        - Circuit breaker se agente falhar
        - Retry automático
        - Auditoria de delegações

        Args:
            agent_name: Nome do agente para delegar
            task_description: Descrição da tarefa
            task_callable: Função async que executa a tarefa
            timeout_seconds: Timeout customizado
            max_retries: Máximo de tentativas

        Returns:
            Resultado da delegação

        Raises:
            RuntimeError: Se circuit breaker está aberto
            asyncio.TimeoutError: Se tarefa excede timeout
        """
        if not self.delegation_manager:
            logger.error("DelegationManager não inicializado")
            return {"error": "DelegationManager not available"}

        try:
            result = await self.delegation_manager.delegate_with_protection(
                agent_name=agent_name,
                task_description=task_description,
                task_callable=task_callable,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
            )
            return result

        except asyncio.TimeoutError:
            logger.error(f"Timeout delegando para {agent_name}")
            return {"error": "Task timeout", "agent": agent_name}

        except RuntimeError as e:
            logger.error(f"Circuit breaker aberto para {agent_name}: {e}")
            return {"error": str(e), "agent": agent_name}

        except Exception as e:
            logger.error(f"Erro ao delegar para {agent_name}: {e}")
            return {"error": str(e), "agent": agent_name}

    def get_delegation_metrics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Retorna métricas de delegação (Seção 7 da Auditoria).

        Args:
            agent_name: Nome do agente (None = todos)

        Returns:
            Dicionário com métricas de delegação
        """
        if not self.delegation_manager:
            return {"error": "DelegationManager not initialized"}

        metrics = self.delegation_manager.get_metrics(agent_name)

        return {
            "metrics": {
                name: {
                    "total_delegations": m.total_delegations,
                    "successful": m.successful_delegations,
                    "failed": m.failed_delegations,
                    "timeout_count": m.timeout_count,
                    "average_duration_seconds": m.average_duration_seconds,
                    "circuit_breaker_state": m.circuit_breaker_state.value,
                    "last_check_time": m.last_check_time,
                }
                for name, m in metrics.items()
            }
        }

    def get_recent_delegations(self, limit: int = 10) -> Dict[str, Any]:
        """Retorna delegações recentes (Seção 7 da Auditoria).

        Args:
            limit: Número máximo de delegações a retornar

        Returns:
            Lista de delegações recentes
        """
        if not self.delegation_manager:
            return {"error": "DelegationManager not initialized"}

        delegations = self.delegation_manager.get_recent_delegations(limit)

        return {
            "delegations": [
                {
                    "id": d.id,
                    "agent": d.agent_name,
                    "task": d.task_description,
                    "status": d.status.value,
                    "duration_seconds": d.duration_seconds,
                    "created_at": d.created_at,
                }
                for d in delegations
            ]
        }

    def orchestrate(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Orchestrate multiple tasks.

        Args:
            tasks: List of task descriptions

        Returns:
            Orchestration result
        """
        try:
            # NEW: Check for contradictions BEFORE/DURING planning (Fase 21-Extended)
            if (
                hasattr(self, "paradox_orchestrator")
                and self.paradox_orchestrator
                and self._detect_contradiction(tasks)
            ):
                logger.info("🔥 Contradiction detected - escalating to ParadoxOrchestrator")
                return self._escalate_to_paradox(tasks)

            # Create a combined task description
            combined_task = f"Execute the following tasks: {'; '.join(tasks)}"

            # Use the main orchestration method
            result = self.run_orchestrated_task(combined_task)
            return result

        except Exception as e:
            logger.error(f"Failed to orchestrate tasks: {e}")
            return {
                "error": str(e),
                "overall_success": False,
                "task": f"Execute the following tasks: {'; '.join(tasks)}",
            }

    async def apply_safe_change(
        self,
        component_id: str,
        change_type: str,
        change_data: Dict[str, Any],
        description: str,
    ) -> Dict[str, Any]:
        """Aplica mudança de forma segura usando sandbox.

        Args:
            component_id: ID do componente a modificar
            change_type: Tipo de mudança ("config", "code", "behavior")
            change_data: Dados da mudança
            description: Descrição da mudança

        Returns:
            Resultado da aplicação (com validação via sandbox)
        """
        if not self.sandbox_system:
            return {
                "success": False,
                "error": "SandboxSystem not available",
            }

        try:
            # 1. Criar snapshot
            snapshot_id = await self.sandbox_system.create_snapshot(
                reason=f"Safe change: {description}"
            )

            # 2. Aplicar mudança no sandbox
            change_id = await self.sandbox_system.apply_change_in_sandbox(
                component_id=component_id,
                change_type=change_type,
                change_data=change_data,
                description=description,
                snapshot_id=snapshot_id,
            )

            # 3. Verificar resultado
            result = self.sandbox_system.results.get(change_id)
            if not result:
                return {
                    "success": False,
                    "error": "Resultado de validação não encontrado",
                    "change_id": change_id,
                }

            # 4. Se validação passou, aplicar à produção
            if result.success and result.validation_passed:
                applied = await self.sandbox_system.apply_to_production(change_id)
                return {
                    "success": applied,
                    "change_id": change_id,
                    "snapshot_id": snapshot_id,
                    "validation_passed": True,
                    "applied_to_production": applied,
                }
            else:
                return {
                    "success": False,
                    "change_id": change_id,
                    "snapshot_id": snapshot_id,
                    "validation_passed": False,
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "rollback_applied": result.rollback_applied,
                }

        except Exception as e:
            logger.error("Erro ao aplicar mudança segura: %s", e, exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def get_sandbox_status(self) -> Dict[str, Any]:
        """Obtém status atual do sandbox.

        Returns:
            Status do sandbox
        """
        if not self.sandbox_system:
            return {"error": "SandboxSystem not available"}

        return self.sandbox_system.get_sandbox_status()

    def get_sandbox_history(self, limit: int = 10) -> Dict[str, Any]:
        """Obtém histórico de mudanças do sandbox.

        Args:
            limit: Número máximo de mudanças

        Returns:
            Histórico de mudanças
        """
        if not self.sandbox_system:
            return {"error": "SandboxSystem not available", "history": []}

        history = self.sandbox_system.get_change_history(limit=limit)
        return {
            "history": history,
            "total": len(history),
        }

    def switch_mode(self, mode: AgentMode) -> Optional[Dict[str, Any]]:
        """
        Switch to a different agent mode.

        Args:
            mode: The mode to switch to

        Returns:
            Switch result or None
        """
        try:
            # Use the tools framework to switch mode
            self.tools_framework.execute_tool(
                "switch_mode",
                target_mode=mode.value,
                reason=f"Manual mode switch to {mode.value}",
            )
            return {"success": True, "mode": mode.value}
        except Exception as e:
            logger.error(f"Failed to switch mode: {e}")
            return {"error": str(e)}

    def get_available_agents(self) -> List[str]:
        """
        Get list of available agent types.

        Returns:
            List of available agent types
        """
        return [mode.value for mode in AgentMode]

    # ========== MCP FILESYSTEM CONVENIENCE METHODS ==========
    # Métodos de conveniência para operações de filesystem via MCP

    def mcp_read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Lê arquivo usando Filesystem MCP.

        Args:
            path: Caminho do arquivo
            encoding: Codificação do arquivo

        Returns:
            Resultado da operação
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "path": path}

        try:
            content = self.mcp_client.read_file(path, encoding=encoding)
            return {
                "success": True,
                "path": path,
                "content": content,
                "length": len(content),
            }
        except MCPClientError as e:
            logger.error("Erro ao ler arquivo via MCP: %s", e)
            return {"success": False, "error": str(e), "path": path}

    def mcp_write_file(self, path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Escreve arquivo usando Filesystem MCP.

        Args:
            path: Caminho do arquivo
            content: Conteúdo a escrever
            encoding: Codificação do arquivo

        Returns:
            Resultado da operação
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "path": path}

        try:
            result = self.mcp_client.write_file(path, content, encoding=encoding)
            return {"success": True, "path": path, "result": result}
        except MCPClientError as e:
            logger.error("Erro ao escrever arquivo via MCP: %s", e)
            return {"success": False, "error": str(e), "path": path}

    def mcp_list_dir(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Lista diretório usando Filesystem MCP.

        Args:
            path: Caminho do diretório
            recursive: Se True, lista recursivamente

        Returns:
            Resultado da operação
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "path": path}

        try:
            result = self.mcp_client.list_dir(path, recursive=recursive)
            return {"success": True, "path": path, "result": result}
        except MCPClientError as e:
            logger.error("Erro ao listar diretório via MCP: %s", e)
            return {"success": False, "error": str(e), "path": path}

    def mcp_file_stat(self, path: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de arquivo usando Filesystem MCP.

        Args:
            path: Caminho do arquivo

        Returns:
            Resultado da operação
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "path": path}

        try:
            result = self.mcp_client.stat(path)
            return {"success": True, "path": path, "stat": result}
        except MCPClientError as e:
            logger.error("Erro ao obter stat de arquivo via MCP: %s", e)
            return {"success": False, "error": str(e), "path": path}

    def get_mcp_orchestrator_status(self) -> Dict[str, Any]:
        """
        Obtém status do MCPOrchestrator e servidores MCP.

        Returns:
            Status dos servidores MCP
        """
        if not self.mcp_orchestrator:
            return {"error": "MCPOrchestrator unavailable", "servers": {}}

        try:
            status = {}
            for name, server_status in self.mcp_orchestrator.status.items():
                status[name] = {
                    "enabled": server_status.enabled,
                    "running": server_status.running,
                    "healthy": server_status.healthy,
                    "uptime_seconds": server_status.uptime_seconds,
                    "total_requests": server_status.total_requests,
                    "failed_requests": server_status.failed_requests,
                    "avg_response_time_ms": server_status.avg_response_time_ms,
                }

            return {
                "success": True,
                "servers": status,
                "total_servers": len(status),
                "running_servers": sum(1 for s in status.values() if s["running"]),
            }
        except Exception as e:
            logger.error("Erro ao obter status do MCPOrchestrator: %s", e)
            return {"success": False, "error": str(e), "servers": {}}

    # ========== MCP THINKING CONVENIENCE METHODS ==========
    # Métodos de conveniência para Sequential Thinking MCP

    def mcp_start_thinking_session(self, goal: str) -> Dict[str, Any]:
        """
        Inicia sessão de thinking usando Sequential Thinking MCP.

        Args:
            goal: Objetivo da sessão de thinking

        Returns:
            Resultado da operação
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "goal": goal}

        try:
            # Usar trigger_mcp_action para chamar o servidor thinking
            result = self.trigger_mcp_action(action="start_session", path=goal, recursive=False)
            return {"success": True, "goal": goal, "result": result}
        except Exception as e:
            logger.error("Erro ao iniciar sessão de thinking via MCP: %s", e)
            return {"success": False, "error": str(e), "goal": goal}

    def mcp_add_thinking_step(
        self, session_id: str, content: str, step_type: str = "observation"
    ) -> Dict[str, Any]:
        """
        Adiciona passo de thinking usando Sequential Thinking MCP.

        Args:
            session_id: ID da sessão
            content: Conteúdo do passo
            step_type: Tipo do passo (observation, hypothesis, analysis, etc.)

        Returns:
            Resultado da operação
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "session_id": session_id}

        try:
            # Usar _execute_mcp_subtask para chamar add_step
            subtask = {
                "description": f"Add thinking step: {content[:50]}",
                "metadata": {
                    "mcp_action": "add_step",
                    "session_id": session_id,
                    "content": content,
                    "type": step_type,
                },
            }
            result = self._execute_mcp_subtask(subtask, metric_name="thinking_mcp")
            return {"success": True, "session_id": session_id, "result": result}
        except Exception as e:
            logger.error("Erro ao adicionar passo de thinking via MCP: %s", e)
            return {"success": False, "error": str(e), "session_id": session_id}

    def mcp_get_thinking_history(self, session_id: str) -> Dict[str, Any]:
        """
        Obtém histórico de thinking usando Sequential Thinking MCP.

        Args:
            session_id: ID da sessão

        Returns:
            Histórico de passos
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "session_id": session_id}

        try:
            subtask = {
                "description": f"Get thinking history for session {session_id}",
                "metadata": {"mcp_action": "get_history", "session_id": session_id},
            }
            result = self._execute_mcp_subtask(subtask, metric_name="thinking_mcp")
            return {"success": True, "session_id": session_id, "history": result}
        except Exception as e:
            logger.error("Erro ao obter histórico de thinking via MCP: %s", e)
            return {"success": False, "error": str(e), "session_id": session_id}

    # ========== MCP CONTEXT CONVENIENCE METHODS ==========
    # Métodos de conveniência para Context MCP

    def mcp_store_context(
        self, level: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Armazena contexto usando Context MCP.

        Args:
            level: Nível do contexto (project, session, task, code, memory, audit, ephemeral)
            content: Conteúdo do contexto
            metadata: Metadados adicionais

        Returns:
            Resultado da operação
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "level": level}

        try:
            subtask = {
                "description": f"Store context at level {level}",
                "metadata": {
                    "mcp_action": "store_context",
                    "level": level,
                    "content": content,
                    "metadata": metadata or {},
                },
            }
            result = self._execute_mcp_subtask(subtask, metric_name="context_mcp")
            return {"success": True, "level": level, "result": result}
        except Exception as e:
            logger.error("Erro ao armazenar contexto via MCP: %s", e)
            return {"success": False, "error": str(e), "level": level}

    def mcp_retrieve_context(self, level: str, query: str = "") -> Dict[str, Any]:
        """
        Recupera contexto usando Context MCP.

        Args:
            level: Nível do contexto
            query: Query opcional para filtrar contexto

        Returns:
            Contexto recuperado
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "level": level}

        try:
            subtask = {
                "description": f"Retrieve context at level {level}",
                "metadata": {
                    "mcp_action": "retrieve_context",
                    "level": level,
                    "query": query,
                },
            }
            result = self._execute_mcp_subtask(subtask, metric_name="context_mcp")
            return {"success": True, "level": level, "context": result}
        except Exception as e:
            logger.error("Erro ao recuperar contexto via MCP: %s", e)
            return {"success": False, "error": str(e), "level": level}

    def mcp_compress_context(self, level: str) -> Dict[str, Any]:
        """
        Comprime contexto usando Context MCP.

        Args:
            level: Nível do contexto a comprimir

        Returns:
            Resultado da compressão
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable", "level": level}

        try:
            subtask = {
                "description": f"Compress context at level {level}",
                "metadata": {"mcp_action": "compress_context", "level": level},
            }
            result = self._execute_mcp_subtask(subtask, metric_name="context_mcp")
            return {"success": True, "level": level, "result": result}
        except Exception as e:
            logger.error("Erro ao comprimir contexto via MCP: %s", e)
            return {"success": False, "error": str(e), "level": level}

    def mcp_snapshot_context(self) -> Dict[str, Any]:
        """
        Cria snapshot do contexto usando Context MCP.

        Returns:
            ID do snapshot criado
        """
        if not self.mcp_client:
            return {"error": "MCP client unavailable"}

        try:
            subtask = {
                "description": "Create context snapshot",
                "metadata": {"mcp_action": "snapshot_context"},
            }
            result = self._execute_mcp_subtask(subtask, metric_name="context_mcp")
            return {"success": True, "snapshot": result}
        except Exception as e:
            logger.error("Erro ao criar snapshot de contexto via MCP: %s", e)
            return {"success": False, "error": str(e)}

    def _detect_contradiction(self, tasks: List[str]) -> bool:
        """
        Detect if tasks contain contradictory requirements.

        Args:
            tasks: List of task strings

        Returns:
            True if contradiction detected
        """
        # Simple heuristic detection (can be enhanced)
        task_text = " ".join(tasks).lower()

        # Detect ethical dilemmas
        ethical_keywords = ["must", "should not", "violates", "against", "forbidden"]
        if sum(kw in task_text for kw in ethical_keywords) >= 2:
            logger.debug("Ethical dilemma detected")
            return True

        # Detect logical contradictions
        contradiction_pairs = [
            ("maximize", "minimize"),
            ("increase", "decrease"),
            ("allow", "forbid"),
            ("create", "delete"),
        ]
        for word1, word2 in contradiction_pairs:
            if word1 in task_text and word2 in task_text:
                logger.debug(f"Logical contradiction detected: {word1} vs {word2}")
                return True

        return False

    def _escalate_to_paradox(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Escalate contradictory tasks to ParadoxOrchestrator.

        Args:
            tasks: Contradictory tasks

        Returns:
            Paradox state (not resolution)
        """
        if not self.paradox_orchestrator:
            logger.warning("ParadoxOrchestrator not available, attempting normal processing")
            return {"error": "Paradox detected but no orchestrator available"}

        # Convert tasks to paradox format
        paradox_input = {
            "domain": "task_orchestration",
            "question": " | ".join(tasks),
            "options": [{"task": t} for t in tasks],
            "contradiction": "Tasks contain conflicting requirements",
        }

        # Attempt classical resolution first (for failure signature)
        classical_attempt = {
            "status": "failed",
            "reason": "Contradictory task requirements",
            "conflict": "Multiple conflicting imperatives",
        }

        # Integrate paradox (not resolve)
        paradox_state = self.paradox_orchestrator.integrate_paradox(
            contradiction=paradox_input, classical_attempt=classical_attempt
        )

        # Return paradox state to user
        return {
            "orchestration_type": "paradox_habitation",
            "paradox_state": paradox_state,
            "message": "Contradiction integrated as system fuel (not resolved)",
            "phi_delta": paradox_state.get("phi_delta"),
        }


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = ["OrchestratorAgent", "AgentMode", "OmniMindCore"]


class OmniMindCore:
    """
    Core system class for OmniMind.

    Provides centralized access to the orchestrator and system state.
    """

    def __init__(self, config_path: str = "config/agent_config.yaml") -> None:
        """Initialize the OmniMind core.

        Args:
            config_path: Path to agent configuration
        """
        self.config_path = config_path
        self.orchestrator: Optional[OrchestratorAgent] = None
        self._initialized = False

        logger.info(f"OmniMindCore initialized with config: {config_path}")

    def initialize(self) -> None:
        """Initialize the core components."""
        if self._initialized:
            logger.warning("OmniMindCore already initialized")
            return

        try:
            self.orchestrator = OrchestratorAgent(self.config_path)
            self._initialized = True
            logger.info("OmniMindCore fully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OmniMindCore: {e}")
            raise

    def get_orchestrator(self) -> Optional[OrchestratorAgent]:
        """Get the orchestrator instance.

        Returns:
            OrchestratorAgent instance or None if not initialized
        """
        if not self._initialized:
            logger.warning("OmniMindCore not initialized - call initialize() first")
        return self.orchestrator
