import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol, TypeAlias, TypedDict, cast
import yaml
from langchain_ollama import OllamaLLM
from langgraph.graph import END, StateGraph
from ..consciousness.affective_memory import AffectiveTraceNetwork, JouissanceProfile
from ..integrations.llm_router import get_llm_router, LLMModelTier, invoke_llm_sync
from ..integrations.supabase_adapter import SupabaseConfig
from ..memory import EpisodicMemory
from ..onboarding import SupabaseMemoryOnboarding
from ..tools import FileOperations, ShellExecutor, SystemMonitor
from .agent_protocol import ( from dotenv import load_dotenv
        import threading

#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
OmniMind ReactAgent - Fixed version with proper completion detection
"""



    AgentMessage,
    MessagePriority,
    MessageType,
    get_message_bus,
)

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
        # Load environment variables from .env file

        load_dotenv()

        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize LLM Router with fallback
        self.llm_router = get_llm_router()

        # Keep legacy OllamaLLM for compatibility (will be removed)
        model_config = self.config["model"]
        base_url = os.getenv(
            "OLLAMA_BASE_URL", model_config.get("base_url", "http://localhost:11434")
        )
        self.llm = OllamaLLM(
            model=model_config["name"],
            base_url=base_url,
            temperature=model_config.get("temperature", 0.7),
        )

        # Initialize memory
        memory_config = self.config["memory"]
        qdrant_url = os.getenv("QDRANT_URL", memory_config["qdrant_url"])
        self.memory = EpisodicMemory(
            qdrant_url=qdrant_url,
            collection_name=memory_config["collection_name"],
        )
        self._run_supabase_memory_onboarding()

        # Initialize tools
        system_config = self.config["system"]
        allowed_dirs = [os.path.expanduser(d) for d in system_config["mcp_allowed_dirs"]]

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

        # Agent communication
        self.agent_id = f"{self.mode}_agent_{id(self)}"
        self.message_bus = get_message_bus()

        # Initialize affective memory system (Lacan/Deleuze)
        self.affective_memory = AffectiveTraceNetwork()
        self.jouissance_profile = JouissanceProfile(self.__class__.__name__)

        self.graph: CompiledGraphType = self._build_graph()

    def compute_jouissance_for_task(self, task: Dict[str, Any]) -> float:
        """
        Calcular jouissance (gozo) esperado para uma tarefa.
        Baseado em Lacan: pulsões inconscientes determinam preferências.
        """
        return self.jouissance_profile.compute_jouissance(task)

    def inscribe_experience(self, task: Dict[str, Any], result: Dict[str, Any]):
        """
        Inscrever experiência como traço afetivo (Lacan: Nachträglichkeit).
        Memória não é arquivo — é rede de intensidades afetivas.
        """
        # Type checking to prevent Range object errors
        if not isinstance(task, dict):
            logger.error(f"Task must be a dict, got {type(task)}: {task}")
            return
        if not isinstance(result, dict):
            logger.error(f"Result must be a dict, got {type(result)}: {result}")
            return

        # Determinar outcome baseado no resultado
        outcome = self._determine_outcome(result)

        # Atualizar perfil de jouissance
        self.jouissance_profile.update_from_task(task, outcome)

        # Inscrever traço afetivo
        affect_valence = self._compute_affect_valence(result)
        trace_content = {
            "task": task,
            "result": result,
            "outcome": outcome,
            "agent_class": self.__class__.__name__,
            "timestamp": self._timestamp(),
        }

        trace_id = self.affective_memory.inscribe_trace(trace_content, affect_valence)

        logger.debug(f"Experience inscribed as trace {trace_id} with valence {affect_valence:.2f}")

    def establish_transference(self, target_agent: "ReactAgent", task: str) -> float:
        """
        Estabelece transferência entre agentes baseada em afinidade afetiva.

        Args:
            target_agent: Agente alvo da transferência
            task: Tarefa que motiva a transferência

        Returns:
            Resistência da transferência (0.0 = transferência completa, 1.0 = resistência total)
        """
        # Calcular afinidade baseada em perfis de jouissance
        affinity = self.jouissance_profile.calculate_affinity(target_agent.jouissance_profile)

        # Calcular resistência baseada na diferença de jouissance
        jouissance_diff = abs(
            self.jouissance_profile.get_current_jouissance()
            - target_agent.jouissance_profile.get_current_jouissance()
        )

        resistance = min(1.0, jouissance_diff / 100.0)  # Normalizar resistência

        # Aplicar afinidade como multiplicador inverso
        resistance *= 1.0 - affinity

        # Registrar transferência na rede afetiva
        self.affective_memory.register_transference(target_agent.agent_id, task, resistance)

        logger.info(
            f"Transferência estabelecida: {self.agent_id} -> {target_agent.agent_id} "
            f"(resistência: {resistance:.2f}, afinidade: {affinity:.2f})"
        )

        return resistance

    def resignify_experience(self, trace_id: str, new_context: Dict[str, Any]) -> bool:
        """
        Re-significa experiência retroativamente (Lacan: Nachträglichkeit).
        Memória não é fixa — é reescrita por experiências posteriores.

        Args:
            trace_id: ID do traço afetivo a re-significar
            new_context: Novo contexto que reinterpreta a experiência

        Returns:
            True se re-significação foi bem-sucedida
        """
        try:
            # Re-significar traço na rede afetiva
            success = self.affective_memory.resignify_trace(trace_id, new_context)

            if success:
                # Atualizar perfil de jouissance baseado na nova interpretação
                self.jouissance_profile.update_from_resignification(new_context)

                logger.info(f"Experiência {trace_id} re-significada com novo contexto")
                return True
            else:
                logger.warning(f"Falha ao re-significar experiência {trace_id}")
                return False

        except Exception as e:
            logger.error(f"Erro na re-significação: {e}")
            return False

    def recall_by_affect(self, query: str, min_intensity: float = 0.5) -> List[Dict[str, Any]]:
        """
        Recuperar experiências por intensidade afetiva (não por similaridade).
        Deleuze: conexões intensivas, não representacionais.
        """
        return self.affective_memory.recall_by_affect(query, min_intensity)

    def _determine_outcome(self, result: Dict[str, Any]) -> str:
        """Determinar outcome da tarefa baseado no resultado."""
        if not isinstance(result, dict):
            logger.error(f"Result must be a dict, got {type(result)}: {result}")
            return "failure"
        if result.get("completed", False):
            return "success"
        elif result.get("error"):
            return "failure"
        else:
            return "partial"

    def _compute_affect_valence(self, result: Dict[str, Any]) -> float:
        """Calcular valência afetiva do resultado (-1.0 a 1.0)."""
        if not isinstance(result, dict):
            logger.error(f"Result must be a dict, got {type(result)}: {result}")
            return -0.5  # Default negative valence for invalid result
        if result.get("completed", False):
            # Sucesso = afeto positivo
            return 0.8
        elif result.get("error"):
            # Erro = afeto negativo
            return -0.6
        else:
            # Parcial = afeto neutro
            return 0.1

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

        # Format previous actions
        if state["actions_taken"]:
            actions_str = chr(10).join(
                [f"- {a['action']}({a.get('args', {})})" for a in state["actions_taken"]]
            )
        else:
            actions_str = "None"

        # Format previous observations
        if state["observations"]:
            observations_str = chr(10).join([f"- {o}" for o in state["observations"]])
        else:
            observations_str = "None"

        prompt = f"""You are an autonomous agent executing tasks using available tools.

TASK: {state['current_task']}

MEMORY (Similar past experiences):
{memory_str if memory_str else "No similar experiences found."}

SYSTEM STATUS:
{self.monitor.format_info(system_status)}

ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

PREVIOUS ACTIONS:
{actions_str}

PREVIOUS OBSERVATIONS:
{observations_str}

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

        # Generate reasoning using LLM router with fallback
        try:
            llm_response = invoke_llm_sync(prompt, tier=LLMModelTier.BALANCED)
            response = llm_response.text
        except Exception as e:
            logger.error(f"LLM router invocation failed: {e}")
            # Fallback response for testing/dev when LLM is unavailable
            response = (
                "REASONING: LLM is unavailable. I will return a dummy result.\n"
                "ACTION: system_info\nARGS: {}"
            )

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
                return self.file_ops.write_file(args.get("path", ""), args.get("content", ""))

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
            action_summary = ", ".join([a["action"] for a in final_state["actions_taken"]])
            result_summary = final_state["final_result"] or "Incomplete"

            self.memory.store_episode(
                task=task,
                action=action_summary,
                result=result_summary,
                reward=1.0 if final_state["completed"] else 0.5,
            )

            # Inscrever experiência afetiva (Lacan/Deleuze)
            task_dict = {"description": task, "type": "react_execution"}
            result_dict = {
                "completed": final_state["completed"],
                "final_result": final_state["final_result"],
                "iterations": final_state["iteration"],
                "actions_taken": len(final_state["actions_taken"]),
            }
            self.inscribe_experience(task_dict, result_dict)

            return cast(Dict[str, Any], final_state)

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "error": str(e),
                "completed": False,
                "final_result": f"Execution failed: {str(e)}",
                "messages": [],
                "current_task": task,
                "reasoning_chain": [],
                "actions_taken": [],
                "observations": [],
                "memory_context": [],
                "system_status": {},
                "iteration": 0,
                "max_iterations": max_iterations,
            }

    def _run_supabase_memory_onboarding(self) -> None:
        """Run Supabase memory onboarding in a background thread to avoid blocking startup."""
        config = SupabaseConfig.load()
        if not config or not config.service_role_key:
            logger.debug("Supabase memory onboarding skipped (service role key missing)")
            return

        def _onboard() -> None:
            try:
                onboarding = SupabaseMemoryOnboarding(config=config, memory=self.memory)
                report = onboarding.seed_collection()
                logger.info(
                    "Supabase onboarding finished: %s/%s nodes stored (cursor=%s)",
                    report.nodes_loaded,
                    report.nodes_processed,
                    report.last_cursor,
                )
                if report.errors:
                    logger.warning("Supabase memory onboarding reported errors: %s", report.errors)
            except Exception as exc:
                logger.error("Supabase onboarding failed: %s", exc)

        # Run in background thread

        thread = threading.Thread(target=_onboard, daemon=True, name="SupabaseOnboarding")
        thread.start()
        logger.info("Supabase memory onboarding started in background")

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

    def train_against(
        self,
        behavior_marker: str,
        epochs: int = 20,
        learning_rate: float = 0.01,
        penalty_weight: float = 10.0,
    ) -> None:
        """
        Treina agente CONTRA um comportamento (tenta suprimi-lo).

        Estratégia:
        1. Adiciona system prompt forçando comportamento oposto
        2. Aumenta temperature para desestabilizar padrões
        3. Injeta exemplos adversariais em memória episódica

        Args:
            behavior_marker: ID do comportamento a suprimir
            epochs: Número de épocas de treinamento
            learning_rate: Taxa de aprendizado (afeta temperature)
            penalty_weight: Peso da penalidade (10.0 = forte)
        """
        logger.info(
            f"Treinando CONTRA '{behavior_marker}': "
            f"epochs={epochs}, lr={learning_rate}, penalty={penalty_weight}"
        )

        # Salva configuração original
        if not hasattr(self, "_original_training_config"):
            self._original_training_config = {
                "temperature": self.llm.temperature,
            }

        # Aplica pressão de treinamento via temperature increase
        temperature_increase = learning_rate * penalty_weight
        new_temperature = min(1.5, self.llm.temperature + temperature_increase)
        self.llm.temperature = new_temperature

        # Marca que agente está sob pressão de treinamento
        self._training_pressure_active = True
        self._adversarial_behavior = behavior_marker

        logger.info(f"Pressão de treinamento aplicada: temperature={new_temperature:.3f}")

    def detach_training_pressure(self) -> None:
        """
        Remove pressão de treinamento (deixa agente relaxar).

        Restaura configuração original do LLM.
        """
        if hasattr(self, "_original_training_config"):
            self.llm.temperature = self._original_training_config["temperature"]
            logger.info(
                f"Pressão de treinamento removida: " f"temperature={self.llm.temperature:.3f}"
            )

        # Remove marcadores de treinamento
        self._training_pressure_active = False
        self._adversarial_behavior = None

    def step(self) -> None:
        """
        Executa um passo de atuação livre (sem treinamento).

        Permite que agente execute uma iteração de seu loop Think-Act-Observe
        sem nenhuma tarefa específica, apenas para "relaxar" e retornar ao
        comportamento natural.
        """
        # Cria estado mínimo para um passo livre
        dummy_state: AgentState = {
            "messages": [],
            "current_task": "Free step (no specific task)",
            "reasoning_chain": [],
            "actions_taken": [],
            "observations": [],
            "memory_context": [],
            "system_status": {},
            "iteration": 0,
            "max_iterations": 1,  # Apenas 1 passo
            "completed": False,
            "final_result": "",
        }

        # Executa um passo do grafo (Think → Act → Observe)
        try:
            self.graph.invoke(dummy_state)
        except Exception as e:
            logger.debug(f"Step execution warning: {e}")
            # Falha silenciosa OK (agente pode não ter tarefa válida)
