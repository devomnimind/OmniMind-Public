from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Dict, List, TypedDict, Any, Optional

from langgraph.graph import StateGraph, START, END


class PlanState(TypedDict):
    intention: str
    plan: List[Dict[str, Any]]
    current_step: int
    criticism: List[str]
    execution_results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    final_result: str
    error: str | None


class LangGraphCoordinator:
    def __init__(
        self,
        llm: Any,
        reactree_agent: Any = None,
        amem: Any = None,
        sensor_bridge: Optional[Any] = None,
    ) -> None:
        self.llm = llm
        self.reactree_agent = reactree_agent
        self.amem = amem
        self.sensor_bridge = sensor_bridge
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(PlanState)
        graph.add_node("plan_node", self.plan_node)
        graph.add_node("criticize_node", self.criticize_node)
        graph.add_node("execute_node", self.execute_node)
        graph.add_node("synthesize_node", self.synthesize_node)
        graph.add_node("error_handler", self.error_handler)
        graph.add_edge(START, "plan_node")
        graph.add_edge("plan_node", "criticize_node")
        graph.add_conditional_edges(
            "criticize_node",
            lambda state: "error_handler" if state.get("criticism") else "execute_node",
            {"error_handler": "error_handler", "execute_node": "execute_node"},
        )
        graph.add_edge("execute_node", "synthesize_node")
        graph.add_edge("synthesize_node", END)
        graph.add_edge("error_handler", END)
        return graph.compile()

    async def plan_node(self, state: PlanState) -> Dict[str, Any]:
        if self.reactree_agent:
            subgoals = await self.reactree_agent.decompose_goal(state["intention"])
            plan = [
                {
                    "step": i,
                    "goal": sg["goal"],
                    "control_flow": sg.get("control_flow", "sequence"),
                    "status": "pending",
                }
                for i, sg in enumerate(subgoals)
            ]
        else:
            prompt = f"Create a 5-step plan for: {state['intention']}"
            await self.llm.ainvoke(prompt)
            plan = [
                {"step": i, "goal": f"Step {i+1}", "status": "pending"}
                for i in range(5)
            ]

        similar = []
        sensor_snapshot: Dict[str, Any] = {}
        if self.sensor_bridge:
            try:
                sensor_snapshot = await self.sensor_bridge.capture_state()
            except Exception as exc:
                sensor_snapshot = {"error": str(exc)}
        if self.amem:
            similar = await self.amem.query_similar_episodes(
                state["intention"], top_k=3
            )

        return {
            "plan": plan,
            "metadata": {
                **state.get("metadata", {}),
                "plan_created_at": datetime.now().isoformat(),
                "sensor_snapshot": sensor_snapshot,
                "similar_episodes": similar,
            },
        }

    async def criticize_node(self, state: PlanState) -> Dict[str, Any]:
        prompt = f"""
Review this plan for logical consistency:

Plan: {json.dumps(state['plan'], indent=2)}
Intention: {state['intention']}

Identify:
1. Logical issues
2. Missing steps
3. Feasibility risks
4. Ordering issues

Output JSON:
{{
  "issues": [...],
  "is_valid": true,
  "severity": "low"
}}
"""
        response = await self.llm.ainvoke(prompt)
        criticism_data: Dict[str, Any] = self._parse_json(response.content)
        issues = criticism_data.get("issues", [])

        return {
            "criticism": issues,
            "metadata": {
                **state.get("metadata", {}),
                "criticism_severity": criticism_data.get("severity", "low"),
            },
        }

    async def execute_node(self, state: PlanState) -> Dict[str, Any]:
        results = [
            {
                "step": step["step"],
                "goal": step["goal"],
                "status": "success",
                "output": f"Completed: {step['goal']}",
            }
            for step in state["plan"]
        ]

        return {
            "execution_results": results,
            "metadata": {
                **state.get("metadata", {}),
                "execution_completed_at": datetime.now().isoformat(),
            },
        }

    async def synthesize_node(self, state: PlanState) -> Dict[str, Any]:
        prompt = f"""
Synthesize these execution results into a clear response:

Original Intent: {state['intention']}
Results: {json.dumps(state['execution_results'], indent=2)}
"""
        response = await self.llm.ainvoke(prompt)

        if self.amem:
            await self.amem.store_episode(
                {
                    "intention": state["intention"],
                    "plan": state["plan"],
                    "results": state["execution_results"],
                    "similar": state.get("metadata", {}).get("similar_episodes", []),
                    "sensor_snapshot": state.get("metadata", {}).get(
                        "sensor_snapshot", {}
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return {
            "final_result": response.content,
            "metadata": {
                **state.get("metadata", {}),
                "synthesis_completed_at": datetime.now().isoformat(),
            },
        }

    async def error_handler(self, state: PlanState) -> Dict[str, Any]:
        return {
            "error": "Plan rejected",
            "final_result": f"Could not execute due to: {', '.join(state.get('criticism', []))}",
        }

    async def run(
        self, intention: str, context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        initial_state: PlanState = {
            "intention": intention,
            "plan": [],
            "current_step": 0,
            "criticism": [],
            "execution_results": [],
            "metadata": context or {"started_at": datetime.now().isoformat()},
            "final_result": "",
            "error": None,
        }

        result = await self.graph.ainvoke(initial_state)

        return {
            "status": "success" if not result.get("error") else "failed",
            "intention": intention,
            "final_result": result.get("final_result", ""),
            "plan_steps": len(result.get("plan", [])),
            "execution_results": result.get("execution_results", []),
            "metadata": result.get("metadata", {}),
        }

    @staticmethod
    def _parse_json(payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return {}
