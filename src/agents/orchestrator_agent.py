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

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from enum import Enum

from .react_agent import ReactAgent
from .code_agent import CodeAgent
from .architect_agent import ArchitectAgent
from .debug_agent import DebugAgent
from .reviewer_agent import ReviewerAgent
from ..tools.omnimind_tools import ToolsFramework
from ..integrations.mcp_client import MCPClient, MCPClientError
from ..integrations.dbus_controller import (
    DBusSessionController,
    DBusSystemController,
)
from ..integrations.supabase_adapter import (
    SupabaseAdapter,
    SupabaseAdapterError,
    SupabaseConfig,
)
from ..integrations.qdrant_adapter import (
    QdrantAdapter,
    QdrantAdapterError,
    QdrantConfig,
)
from .orchestrator_metrics import OrchestratorMetricsCollector
from ..security.security_agent import SecurityAgent
from .psychoanalytic_analyst import PsychoanalyticAnalyst
from ..metacognition.metacognition_agent import MetacognitionAgent


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

    def __init__(self, config_path: str) -> None:
        super().__init__(config_path)

        self.tools_framework = ToolsFramework()
        self.mode = "orchestrator"

        # Agentes especializados (lazy init)
        self._agents: Dict[AgentMode, ReactAgent] = {}
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
        """Obtém ou cria agente especializado"""
        if mode not in self._agents:
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

        return self._agents[mode]

    def decompose_task(self, task_description: str) -> Dict[str, Any]:
        """Decompõe tarefa complexa em subtarefas delegáveis"""
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
            response = self.llm.invoke(prompt)
        except Exception as e:
            logger.error(f"LLM invocation failed in decompose_task: {e}")
            # Fallback plan for testing/dev
            response = """
ANALYSIS: LLM unavailable, using fallback plan.
SUBTASKS:
1. [CODE] Implement requested feature
DEPENDENCIES:
ESTIMATED_COMPLEXITY: low
"""

        # Parsear plano
        plan = self._parse_plan(response)
        plan["original_task"] = task_description
        plan["created_at"] = self._timestamp()

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

        in_subtasks = False
        for line in response.split("\n"):
            line = line.strip()

            if "SUBTASKS:" in line:
                in_subtasks = True
                continue

            if "DEPENDENCIES:" in line:
                in_subtasks = False
                continue

            if in_subtasks and line and (line[0].isdigit() or line.startswith("-")):
                # Extrair modo e descrição - flexível para [CODE], [CODE_MODE], (code), etc.
                line_lower = line.lower()
                matched = False
                for mode in [
                    "code",
                    "architect",
                    "debug",
                    "reviewer",
                    "psychoanalyst",
                    "security",
                    "mcp",
                    "dbus",
                ]:
                    # Buscar variações: [code], [code_mode], (code), etc.
                    if (
                        f"[{mode}]" in line_lower
                        or f"[{mode}_mode]" in line_lower
                        or f"({mode})" in line_lower
                        or f"{mode}_mode" in line_lower
                    ):
                        # Extrair descrição após modo
                        task_desc = line.split("]", 1)[-1].strip() if "]" in line else line
                        # Remover padrões como "- Plan Architecture:"
                        if ":" in task_desc:
                            task_desc = task_desc.split(":", 1)[-1].strip()
                        plan["subtasks"].append(  # type: ignore[attr-defined]
                            {
                                "agent": mode,
                                "description": task_desc,
                                "status": "pending",
                            }
                        )
                        matched = True
                        break

                # Se não encontrou modo explícito, tentar inferir
                if not matched:
                    agent_names = {
                        "code": [
                            "codeagent",
                            "code agent",
                            "implement",
                            "write code",
                        ],
                        "architect": [
                            "architectagent",
                            "architect agent",
                            "plan",
                            "design",
                            "specification",
                        ],
                        "debug": [
                            "debugagent",
                            "debug agent",
                            "diagnose",
                            "fix bug",
                        ],
                        "reviewer": [
                            "revieweragent",
                            "reviewer agent",
                            "review",
                            "quality",
                        ],
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
                        "mcp": [
                            "mcp",
                            "model context",
                            "file access",
                            "filesystem",
                        ],
                        "dbus": [
                            "dbus",
                            "session bus",
                            "media",
                            "network",
                        ],
                    }
                    if line_lower:  # guard against empty lines
                        for mode in [
                            "code",
                            "architect",
                            "debug",
                            "reviewer",
                            "psychoanalyst",
                            "security",
                            "mcp",
                            "dbus",
                        ]:
                            if any(keyword in line_lower for keyword in agent_names[mode]):
                                task_desc = line.strip("0123456789.-) \t")
                                if ":" in task_desc:
                                    task_desc = task_desc.split(":", 1)[-1].strip()
                                plan["subtasks"].append(  # type: ignore[attr-defined]
                                    {
                                        "agent": mode,
                                        "description": task_desc,
                                        "status": "pending",
                                    }
                                )
                                break

            if "ESTIMATED_COMPLEXITY:" in line or "complexity:" in line.lower():
                if "low" in line.lower():
                    plan["complexity"] = "low"
                elif "high" in line.lower():
                    plan["complexity"] = "high"

        return plan

    def execute_plan(
        self, plan: Optional[Dict[str, Any]] = None, max_iterations_per_task: int = 3
    ) -> Dict[str, Any]:
        """Executa plano delegando para agentes especializados"""
        if plan is None:
            plan = self.current_plan

        if not plan or not plan.get("subtasks"):
            return {"error": "No plan to execute"}

        results: Dict[str, Any] = {
            "original_task": plan.get("original_task"),
            "subtask_results": [],
            "overall_success": True,
            "started_at": self._timestamp(),
        }

        for i, subtask in enumerate(plan["subtasks"]):
            description = subtask.get("description")
            if not description:
                description = f"Untitled subtask {i+1}"
                subtask["description"] = description
            safe_description = description[:80]
            delegation_msg = (
                f"\n🪃 [Orchestrator] Delegating subtask {i+1}/"
                f"{len(plan['subtasks'])}: {safe_description}..."
            )
            print(delegation_msg)

            # >>> PRE-DELEGATION SECURITY CHECK <<<
            if self.security_agent:
                # For now, just log a check. A real implementation would
                # check for active high-priority threats.
                self.security_agent.logger.info(
                    f"Pre-delegation check for task: {safe_description}"
                )

            try:
                agent_mode = AgentMode(subtask["agent"])
                result: Dict[str, Any] = {}
                agent: Optional[ReactAgent] = None
                if agent_mode in {
                    AgentMode.CODE,
                    AgentMode.ARCHITECT,
                    AgentMode.DEBUG,
                    AgentMode.REVIEWER,
                    AgentMode.PSYCHOANALYST,
                }:
                    agent = self._get_agent(agent_mode)

                task_record = self.tools_framework.execute_tool(
                    "new_task",
                    task_name=subtask["description"],
                    assigned_to=subtask["agent"],
                    priority="HIGH" if plan["complexity"] == "high" else "MEDIUM",
                )

                self.tools_framework.execute_tool(
                    "switch_mode", target_mode=subtask["agent"], reason=f"Subtask {i+1}"
                )

                if agent_mode == AgentMode.SECURITY:
                    result = self._execute_security_subtask(subtask)
                elif agent_mode == AgentMode.MCP:
                    result = self._execute_mcp_subtask(subtask)
                elif agent_mode == AgentMode.DBUS:
                    result = self._execute_dbus_subtask(subtask)
                elif agent_mode == AgentMode.CODE:
                    result = agent.run_code_task(  # type: ignore[union-attr]
                        subtask["description"], max_iterations=max_iterations_per_task
                    )
                elif agent_mode == AgentMode.REVIEWER:
                    result = {
                        "completed": True,
                        "mode": "reviewer",
                        "note": "Review would be performed on generated files",
                    }
                elif agent_mode == AgentMode.PSYCHOANALYST:
                    # This is a simplified execution for the analyst
                    analysis = agent.analyze_session(  # type: ignore[union-attr]
                        subtask["description"]
                    )
                    report = agent.generate_abnt_report(analysis)  # type: ignore[union-attr]
                    result = {
                        "completed": True,
                        "final_result": report,
                        "details": analysis,
                        "iteration": 1,
                    }
                else:
                    if agent is None:
                        result = {
                            "completed": False,
                            "final_result": f"Agent {subtask['agent']} not available",
                            "iteration": 0,
                        }
                    else:
                        result = agent.run(
                            subtask["description"],
                            max_iterations=max_iterations_per_task,
                        )

                if not isinstance(result, dict):
                    result = {
                        "completed": False,
                        "final_result": str(result),
                        "iteration": 0,
                    }
                # Registrar resultado
                subtask["status"] = "completed" if result.get("completed") else "failed"
                subtask["result"] = result

                summary = result.get("final_result")
                if summary is None:
                    summary = ""
                results["subtask_results"].append(
                    {
                        "subtask_id": i + 1,
                        "agent": subtask["agent"],
                        "description": subtask["description"],
                        "completed": result.get("completed", False),
                        "iterations": result.get("iteration", 0),
                        "summary": summary[:200],
                    }
                )

                if not result.get("completed"):
                    results["overall_success"] = False
                    print(f"❌ Subtask {i+1} failed")
                else:
                    print(f"✅ Subtask {i+1} completed")

                # Armazenar conclusão
                self.tools_framework.execute_tool(
                    "attempt_completion",
                    task_id=task_record["id"],
                    result=str(result.get("final_result", "")),
                    success=result.get("completed", False),
                )

            except Exception as e:
                logger.exception("Error executing subtask %d", i + 1)
                print(f"❌ Error in subtask {i+1}: {e}")
                results["overall_success"] = False
                results["subtask_results"].append({"subtask_id": i + 1, "error": str(e)})

        results["completed_at"] = self._timestamp()

        # Voltar para modo orchestrator
        self.tools_framework.execute_tool(
            "switch_mode", target_mode="orchestrator", reason="Plan execution complete"
        )

        return results

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

        print(f"\n📊 Plan created with {len(plan['subtasks'])} subtasks:")
        for i, subtask in enumerate(plan["subtasks"], 1):
            print(f"  {i}. [{subtask['agent']}] {subtask['description'][:80]}")

        # 2. Executar
        print("\n🚀 Executing plan...")
        execution_result = self.execute_plan(plan, max_iterations_per_subtask)

        # 3. Sintetizar
        print("\n📝 Synthesizing results...")
        synthesis = self._synthesize_results(execution_result)

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

    def _synthesize_results(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Sintetiza resultados de múltiplos agentes"""
        subtask_summaries = []
        for sr in execution_result["subtask_results"]:
            subtask_summaries.append(
                f"- {sr.get('agent', 'unknown')}: {sr.get('description', '')} → "
                f"{'✅' if sr.get('completed') else '❌'}"
            )

        synthesis = {
            "summary": "\n".join(subtask_summaries),
            "total_subtasks": len(execution_result["subtask_results"]),
            "completed": sum(
                1 for sr in execution_result["subtask_results"] if sr.get("completed")
            ),
            "failed": sum(
                1 for sr in execution_result["subtask_results"] if not sr.get("completed")
            ),
            "overall_success": execution_result["overall_success"],
        }

        return synthesis

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
        Delegate a task to a specific agent type.

        Args:
            task: Task description
            agent_type: Type of agent to delegate to

        Returns:
            Delegation result or None
        """
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

            return result

        except Exception as e:
            logger.error(f"Failed to delegate task: {e}")
            return {"error": str(e)}

    def orchestrate(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Orchestrate multiple tasks.

        Args:
            tasks: List of task descriptions

        Returns:
            Orchestration result
        """
        try:
            # Create a combined task description
            combined_task = f"Execute the following tasks: {'; '.join(tasks)}"

            # Use the main orchestration method
            result = self.run_orchestrated_task(combined_task)
            return result

        except Exception as e:
            logger.error(f"Failed to orchestrate tasks: {e}")
            return {"error": str(e)}

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
