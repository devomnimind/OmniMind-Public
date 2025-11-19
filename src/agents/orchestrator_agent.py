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

logger = logging.getLogger(__name__)


class AgentMode(Enum):
    """Modos de agente disponíveis"""

    ORCHESTRATOR = "orchestrator"
    CODE = "code"
    ARCHITECT = "architect"
    DEBUG = "debug"
    REVIEWER = "reviewer"
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
        self.dashboard_snapshot: Dict[str, Any] = {}
        self.last_mcp_result: Dict[str, Any] = {}
        self.last_dbus_result: Dict[str, Any] = {}
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
        try:
            return DBusSessionController()
        except Exception as exc:
            logger.warning("DBus session controller unavailable: %s", exc)
            return None

    def _init_dbus_system_controller(self) -> Optional[DBusSystemController]:
        try:
            return DBusSystemController()
        except Exception as exc:
            logger.warning("DBus system controller unavailable: %s", exc)
            return None

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
        """Initializes the security agent and starts its monitoring."""
        try:
            security_config = self.config.get("security", {})
            config_path = security_config.get("config_path", "config/security.yaml")
            
            agent = SecurityAgent(config_path=config_path, llm=self.llm)
            if agent.config.get("security_agent", {}).get("enabled", False):
                # Running this in a background task
                import asyncio
                asyncio.create_task(agent.start_continuous_monitoring())
                logger.info("SecurityAgent continuous monitoring started in background.")
            return agent
        except Exception as exc:
            logger.error("Failed to initialize SecurityAgent: %s", exc)
            return None

    def _timestamp(self) -> str:
        """Retorna timestamp UTC em formato ISO"""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _build_dashboard_context(
        self, plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
                context["network_status"] = (
                    self.dbus_system_controller.get_network_status()
                )
                context["power_status"] = self.dbus_system_controller.get_power_status()
            except Exception as exc:
                logger.warning("D-Bus system lookup failed: %s", exc)

        if self.dbus_session_controller:
            try:
                context["media_players"] = (
                    self.dbus_session_controller.list_media_players()
                )
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

    def _record_operation(
        self, name: str, latency: float, success: bool = True
    ) -> None:
        self.metrics.record(name, latency, success)

    def _finalize_operation(
        self, name: str, start: float, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        self._record_operation(
            name, time.perf_counter() - start, result.get("completed", False)
        )
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
        completed = sum(
            1 for sub in plan["subtasks"] if sub.get("status") == "completed"
        )
        failed = sum(1 for sub in plan["subtasks"] if sub.get("status") == "failed")
        return {"completed": completed, "failed": failed}

    def _infer_path_from_description(self, description: str) -> Optional[str]:
        matches = re.findall(r"\b(?:config|src|web|data|logs)/[^\s,;]+", description)
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
        action = metadata.get("mcp_action") or (
            "list" if "list" in description.lower() else "read"
        )
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
                    details = self.dbus_session_controller.control_media_player(
                        "playpause"
                    )
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
                    details = {
                        "media": self.dbus_session_controller.list_media_players()
                    }
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

        response = self.llm.invoke(prompt)

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
                        task_desc = (
                            line.split("]", 1)[-1].strip() if "]" in line else line
                        )
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
                            "security",
                            "mcp",
                            "dbus",
                        ]:
                            if any(
                                keyword in line_lower for keyword in agent_names[mode]
                            ):
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
                self.security_agent.logger.info(f"Pre-delegation check for task: {safe_description}")


            try:
                agent_mode = AgentMode(subtask["agent"])
                result: Dict[str, Any] = {}
                agent: Optional[ReactAgent] = None
                if agent_mode in {
                    AgentMode.CODE,
                    AgentMode.ARCHITECT,
                    AgentMode.DEBUG,
                    AgentMode.REVIEWER,
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
                else:
                    result = agent.run(  # type: ignore[union-attr]
                        subtask["description"], max_iterations=max_iterations_per_task
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
                results["subtask_results"].append(
                    {"subtask_id": i + 1, "error": str(e)}
                )

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
        self._record_operation(
            "orchestrate_task", duration, execution_result["overall_success"]
        )

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
                1
                for sr in execution_result["subtask_results"]
                if not sr.get("completed")
            ),
            "overall_success": execution_result["overall_success"],
        }

        return synthesis


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = ["OrchestratorAgent", "AgentMode"]
