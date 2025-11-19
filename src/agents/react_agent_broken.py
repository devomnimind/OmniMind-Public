"""
ReAct Agent Base for OmniMind
Implements Think → Act → Observe pattern using LangGraph.
"""

from typing import TypeAlias, TypedDict, List, Dict, Any, Optional
from datetime import datetime
import yaml

from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, CompiledStateGraph, END

from ..memory import EpisodicMemory
from ..tools import FileOperations, ShellExecutor, SystemMonitor


class AgentState(TypedDict):
    """State structure for ReAct agent."""

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
    final_result: Optional[str]


CompiledGraphType: TypeAlias = CompiledStateGraph[AgentState]


class ReactAgent:
    """
    Base ReAct agent implementing Think → Act → Observe loop.
    Uses LangGraph for state management.
    """

    def __init__(self, config_path: str = "config/agent_config.yaml"):
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize LLM
        model_config = self.config["model"]
        self.llm = Ollama(
            model=model_config["name"],
            base_url=model_config["base_url"],
            temperature=model_config["temperature"],
        )

        # Initialize memory
        memory_config = self.config["memory"]
        self.memory = EpisodicMemory(
            qdrant_url=memory_config["qdrant_url"],
            collection_name=memory_config["collection_name"],
        )

        # Initialize tools
        system_config = self.config["system"]
        self.file_ops = FileOperations(system_config["mcp_allowed_dirs"])
        self.shell = ShellExecutor(
            system_config["shell_whitelist"], system_config["shell_timeout"]
        )
        self.monitor = SystemMonitor()

        # Expose attributes for type checking and testing
        self.mode: str = "react"
        self.tools: List[Any] = [self.file_ops, self.shell, self.monitor]

        # Build state graph
        self.graph: CompiledGraphType = self._build_graph()

    def _build_graph(self) -> CompiledGraphType:
        """Build LangGraph state machine for ReAct pattern."""
        workflow: StateGraph[AgentState] = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("think", self._think_node)
        workflow.add_node("act", self._act_node)
        workflow.add_node("observe", self._observe_node)

        # Define edges
        workflow.set_entry_point("think")
        workflow.add_edge("think", "act")
        workflow.add_edge("act", "observe")

        # Conditional edge: continue or end
        workflow.add_conditional_edges(
            "observe", self._should_continue, {"continue": "think", "end": END}
        )

        return workflow.compile()

    def _think_node(self, state: AgentState) -> AgentState:
        """
        THINK: Query memory for similar experiences and generate reasoning.
        """
        task = state["current_task"]

        # Search memory for similar past experiences
        similar = self.memory.search_similar(task, top_k=3, min_reward=0.5)
        state["memory_context"] = similar  # type: ignore[typeddict-item]

        # Build context
        memory_context = ""
        if similar:
            memory_context = "\n\nSimilar past experiences:\n"
            for i, exp in enumerate(similar, 1):
                memory_context += f"{i}. Task: {exp['task']}\n"
                memory_context += f"   Action: {exp['action']}\n"
                memory_context += (
                    f"   Result: {exp['result']} (reward: {exp['reward']})\n"
                )

        # Get system status
        sys_info = self.monitor.get_info()
        state["system_status"] = sys_info

        # Generate reasoning
        prompt = f"""You are an autonomous AI agent. Analyze this task and decide what action to take.

Task: {task}

Current iteration: {state['iteration']}/{state['max_iterations']}
{memory_context}

System status:
CPU: {sys_info['cpu']['percent']:.1f}%
RAM: {sys_info['memory']['used_gb']:.1f}/{sys_info['memory']['total_gb']:.1f} GB

Previous actions: {len(state['actions_taken'])}
Previous observations: {state['observations'][-1] if state['observations'] else 'None'}

Think step-by-step:
1. What is the goal?
2. What information do I have?
3. What should I do next?
4. Which tool should I use?

Available tools:
- read_file(path) - Read a file
- write_file(path, content) - Write to a file
- list_files(path) - List directory contents
- execute_shell(command) - Run whitelisted shell command
- system_info() - Get system metrics

Respond with your reasoning and chosen action in this format:
REASONING: <your step-by-step thinking>
ACTION: <tool_name>
ARGS: <arguments as JSON>
"""

        try:
            response = self.llm.invoke(prompt)
            state["reasoning_chain"].append(response)
            state["messages"].append(f"[THINK] {response[:200]}...")
        except Exception as e:
            state["messages"].append(f"[THINK ERROR] {str(e)}")

        return state

    def _act_node(self, state: AgentState) -> AgentState:
        """
        ACT: Execute the chosen action using appropriate tool.
        """
        # Parse last reasoning to extract action
        if not state["reasoning_chain"]:
            state["messages"].append("[ACT] No reasoning available")
            return state

        last_reasoning = state["reasoning_chain"][-1]

        # Simple parsing (in production, use structured output)
        action = "system_info"  # Default action
        args = {}

        if "ACTION:" in last_reasoning:
            action_line = [
                line for line in last_reasoning.split("\n") if "ACTION:" in line
            ]
            if action_line:
                action = action_line[0].split("ACTION:")[1].strip().lower()

        if "ARGS:" in last_reasoning:
            args_line = [line for line in last_reasoning.split("\n") if "ARGS:" in line]
            if args_line:
                try:
                    import json

                    args = json.loads(args_line[0].split("ARGS:")[1].strip())
                except:
                    args = {}

        # Execute action
        result = self._execute_action(action, args)

        action_record = {
            "action": action,
            "args": args,
            "result": result[:500],  # Truncate long results
            "timestamp": datetime.utcnow().isoformat(),
        }

        state["actions_taken"].append(action_record)
        state["messages"].append(f"[ACT] {action}({args}) -> {result[:100]}...")

        return state

    def _execute_action(self, action: str, args: Dict[str, Any]) -> str:
        """Execute tool action."""
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
        OBSERVE: Process action results and update state.
        """
        if state["actions_taken"]:
            last_action = state["actions_taken"][-1]
            observation = f"Action '{last_action['action']}' completed. Result: {last_action['result'][:200]}"
            state["observations"].append(observation)
            state["messages"].append(f"[OBSERVE] {observation}")

        state["iteration"] += 1

        return state

    def _should_continue(self, state: AgentState) -> str:
        """Decide if agent should continue or terminate."""
        # Check max iterations
        if state["iteration"] >= state["max_iterations"]:
            return "end"

        # Check if task is completed (flag set in _observe_node)
        if state["completed"]:
            return "end"

        return "continue"

    def run(self, task: str, max_iterations: int = 5) -> AgentState:
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
            "final_result": None,
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

            return final_state

        except Exception as e:
            # Return initial state with error information
            error_state = initial_state.copy()
            error_state["messages"].append(f"[ERROR] {str(e)}")
            error_state["completed"] = False
            error_state["final_result"] = f"Error: {str(e)}"
            return error_state
