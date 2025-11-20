#!/usr/bin/env python3
"""
OmniMind ReactAgent - Fixed version with proper completion detection
"""

import json
import logging
import os
import time
import yaml
from datetime import datetime, timezone
from typing import Any, Dict, List, Protocol, TypeAlias, TypedDict, cast, Optional

from langchain_ollama import OllamaLLM
from langgraph.graph import END, StateGraph

from .agent_protocol import AgentMessage, MessagePriority, MessageType, get_message_bus
from ..integrations.supabase_adapter import SupabaseConfig
from ..memory import EpisodicMemory
from ..onboarding import SupabaseMemoryOnboarding
from ..tools import FileOperations, ShellExecutor, SystemMonitor

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for ReAct agent execution."""

    messages: List[str]
    current_task: str
    reasoning_chain: List[str]
    actions_taken: List[Dict[str, Any]]
    observations: List[str]
    memory_context: List[Dict[str, Any]]
    system_status: Dict[str, Any]
    iteration: int
    max_iterations: int
    completed: bool
    final_result: str


class GraphInvoker(Protocol):
    def invoke(self, state: AgentState) -> AgentState: ...


CompiledGraphType: TypeAlias = Any  # langgraph 1.0.3 compiled graph return type


class ReactAgent:
    """
    Base ReAct (Reasoning + Acting) agent with Think-Act-Observe loop.

    Architecture:
        THINK → Query memory + System status → Generate reasoning
        ACT → Parse reasoning → Execute tool
        OBSERVE → Process result → Check completion → Continue or End
    """

    def __init__(self, config_path: str):
        """Initialize agent with configuration."""
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize LLM
        model_config = self.config["model"]
        self.llm = OllamaLLM(
            model=model_config["name"],
            base_url=model_config.get("base_url", "http://localhost:11434"),
            temperature=model_config.get("temperature", 0.7),
        )

        # Initialize memory
        memory_config = self.config["memory"]
        self.memory = EpisodicMemory(
            qdrant_url=memory_config["qdrant_url"],
            collection_name=memory_config["collection_name"],
        )
        self._run_supabase_memory_onboarding()

        # Initialize tools
        system_config = self.config["system"]
        allowed_dirs = [
            os.path.expanduser(d) for d in system_config["mcp_allowed_dirs"]
        ]

        self.file_ops = FileOperations(allowed_dirs=allowed_dirs)
        self.shell = ShellExecutor(
            whitelist=system_config["shell_whitelist"],
            timeout=system_config["shell_timeout"],
        )
        self.monitor = SystemMonitor()

        # Expose attributes for type checking and testing
        self.mode: str = "react"
        self.tools: List[Any] = [self.file_ops, self.shell, self.monitor]

        # Agent communication
        self.agent_id = f"{self.mode}_agent_{id(self)}"
        self.message_bus = get_message_bus()

        self.graph: CompiledGraphType = self._build_graph()

    def _timestamp(self) -> str:
        """Generate ISO timestamp for logging"""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _build_graph(self) -> Any:
        """Build LangGraph state machine."""
        workflow: StateGraph[AgentState] = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("think", self._think_node)
        workflow.add_node("act", self._act_node)
        workflow.add_node("observe", self._observe_node)

        # Set entry point
        workflow.set_entry_point("think")

        # Add edges
        workflow.add_edge("think", "act")
        workflow.add_edge("act", "observe")
        workflow.add_conditional_edges(
            "observe", self._should_continue, {"continue": "think", "end": END}
        )

        return workflow.compile()

    def _think_node(self, state: AgentState) -> AgentState:
        """
        THINK: Generate reasoning based on task, memory, and system status.
        """
        # Get similar experiences from memory
        similar_episodes = self.memory.search_similar(
            state["current_task"], top_k=3, min_reward=0.5
        )

        # Get current system status
        system_status = self.monitor.get_info()
        state["system_status"] = system_status

        # Format memory context
        memory_str = ""
        if similar_episodes:
            memory_str = "\n".join(
                [
                    f"{i+1}. Task: {ep['task']}\n"
                    f"   Action: {ep['action']}\n"
                    f"   Result: {ep['result'][:200]}..."
                    for i, ep in enumerate(similar_episodes)
                ]
            )

        # Build prompt
        shell_whitelist = ", ".join(self.config["system"]["shell_whitelist"])

        prompt = f"""You are an autonomous agent executing tasks using available tools.

TASK: {state['current_task']}

MEMORY (Similar past experiences):
{memory_str if memory_str else "No similar experiences found."}

SYSTEM STATUS:
{self.monitor.format_info(system_status)}

ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

PREVIOUS ACTIONS:
{chr(10).join([f"- {a['action']}({a.get('args', {})})" for a in state['actions_taken']]) if state['actions_taken'] else "None"}

PREVIOUS OBSERVATIONS:
{chr(10).join([f"- {o}" for o in state['observations']]) if state['observations'] else "None"}

AVAILABLE TOOLS:
1. read_file(path: str) - Read file contents
2. write_file(path: str, content: str) - Write to file
3. list_files(path: str) - List directory contents
4. execute_shell(command: str) - Execute shell command
    (whitelist: {shell_whitelist})
5. system_info() - Get system status

INSTRUCTIONS:
Think step-by-step about what action to take next. Then specify:

REASONING: <your thinking process>
ACTION: <tool_name>
ARGS: <json dict of arguments>

Your response:"""

        # Generate reasoning
        response = self.llm.invoke(prompt)
        state["reasoning_chain"].append(response)
        state["messages"].append(f"[THINK] {response[:500]}...")

        return state

    def _act_node(self, state: AgentState) -> AgentState:
        """
        ACT: Parse reasoning and execute chosen action.
        """
        if not state["reasoning_chain"]:
            return state

        # Parse last reasoning
        reasoning = state["reasoning_chain"][-1]

        # Extract action and args
        action = "system_info"  # Default
        args = {}

        for line in reasoning.split("\n"):
            line = line.strip()
            if line.startswith("ACTION:"):
                action = line.split("ACTION:")[1].strip()
            elif line.startswith("ARGS:"):
                args_str = line.split("ARGS:")[1].strip()
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}

        # Execute action
        result = self._execute_action(action, args)

        # Record action
        action_record = {
            "action": action,
            "args": args,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        state["actions_taken"].append(action_record)
        state["messages"].append(f"[ACT] {action}({args}) -> {result[:500]}...")

        return state

    def _execute_action(self, action: str, args: Dict[str, Any]) -> str:
        """Execute a tool action."""
        try:
            if action == "read_file":
                return self.file_ops.read_file(args.get("path", ""))

            elif action == "write_file":
                return self.file_ops.write_file(
                    args.get("path", ""), args.get("content", "")
                )

            elif action == "list_files":
                return self.file_ops.list_files(args.get("path", "."))

            elif action == "execute_shell":
                return self.shell.execute(args.get("command", ""))

            elif action == "system_info":
                return self.monitor.format_info(self.monitor.get_info())

            else:
                return f"Unknown action: {action}"

        except Exception as e:
            return f"Error executing {action}: {str(e)}"

    def _observe_node(self, state: AgentState) -> AgentState:
        """
        OBSERVE: Process action results and check completion.
        """
        if state["actions_taken"]:
            last_action = state["actions_taken"][-1]
            action_name = last_action["action"]
            result_snippet = str(last_action["result"])[:200]
            observation = f"Action '{action_name}' completed. Result: {result_snippet}"

            state["observations"].append(observation)
            state["messages"].append(f"[OBSERVE] {observation}")

            # ✅ FIX: Check completion based on keywords in observation
            success_keywords = ["success", "completed", "done", "written"]
            if any(word in observation.lower() for word in success_keywords):
                state["completed"] = True
                state["final_result"] = observation

        state["iteration"] += 1
        return state

    def _should_continue(self, state: AgentState) -> str:
        """
        Decide if agent should continue or terminate.
        ✅ FIX: Only check flags, don't modify state here.
        """
        # Check max iterations
        if state["iteration"] >= state["max_iterations"]:
            return "end"

        # Check if completed (flag set in _observe_node)
        if state["completed"]:
            return "end"

        return "continue"

    def run(self, task: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Execute agent on given task.

        Args:
            task: Task description
            max_iterations: Maximum number of think-act-observe cycles

        Returns:
            Final state with results
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [],
            "current_task": task,
            "reasoning_chain": [],
            "actions_taken": [],
            "observations": [],
            "memory_context": [],
            "system_status": {},
            "iteration": 0,
            "max_iterations": max_iterations,
            "completed": False,
            "final_result": "",
        }

        # Run state machine
        try:
            final_state = self.graph.invoke(initial_state)

            # Store episode in memory
            action_summary = ", ".join(
                [a["action"] for a in final_state["actions_taken"]]
            )
            result_summary = final_state["final_result"] or "Incomplete"

            self.memory.store_episode(
                task=task,
                action=action_summary,
                result=result_summary,
                reward=1.0 if final_state["completed"] else 0.5,
            )

            return cast(Dict[str, Any], final_state)

        except Exception as e:
            return {"error": str(e), "completed": False, "final_result": None}

    def _run_supabase_memory_onboarding(self) -> None:
        config = SupabaseConfig.load()
        if not config or not config.service_role_key:
            logger.debug(
                "Supabase memory onboarding skipped (service role key missing)"
            )
            return

        onboarding = SupabaseMemoryOnboarding(config=config, memory=self.memory)
        report = onboarding.seed_collection()
        logger.info(
            "Started Supabase onboarding: %s/%s nodes stored (cursor=%s)",
            report.nodes_loaded,
            report.nodes_processed,
            report.last_cursor,
        )
        if report.errors:
            logger.warning(
                "Supabase memory onboarding reported errors: %s", report.errors
            )

    async def send_message(
        self,
        recipient: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
    ) -> None:
        """
        Envia mensagem para outro agente.

        Args:
            recipient: ID do agente destinatário
            message_type: Tipo da mensagem
            payload: Dados da mensagem
            priority: Prioridade da mensagem
        """
        message = AgentMessage(
            message_id=str(id(self)) + str(time.time()),
            message_type=message_type,
            sender=self.agent_id,
            recipient=recipient,
            payload=payload,
            priority=priority,
        )
        await self.message_bus.send_message(message)

    async def receive_message(self, timeout: float = 1.0) -> Optional[AgentMessage]:
        """
        Recebe mensagem da fila do agente.

        Args:
            timeout: Timeout em segundos

        Returns:
            Mensagem recebida ou None
        """
        return await self.message_bus.receive_message(self.agent_id, timeout)
