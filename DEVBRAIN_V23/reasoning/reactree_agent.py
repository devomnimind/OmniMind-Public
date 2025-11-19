from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ControlFlowType(Enum):
    SEQUENCE = "sequence"
    FALLBACK = "fallback"
    PARALLEL = "parallel"


@dataclass
class Thought:
    id: str
    goal: str
    parent_id: Optional[str]
    reasoning: str
    action: Optional[str]
    observation: Optional[str]
    subgoals: List["Thought"] = field(default_factory=list)
    control_flow: Optional[ControlFlowType] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None


class ReAcTreeAgent:
    def __init__(self, llm: Any, max_depth: int = 4, max_width: int = 5) -> None:
        self.llm = llm
        self.max_depth = max_depth
        self.max_width = max_width
        self.tree: Optional[Thought] = None
        self.execution_history: List[Thought] = []

    async def decompose_goal(
        self, goal: str, context: str = ""
    ) -> List[Dict[str, Any]]:
        prompt = f"""
You are a task decomposition expert. Break down this complex goal into manageable subgoals.
For each subgoal, specify the control flow type (sequence, fallback, or parallel).

Goal: {goal}
Context: {context}

Return JSON:
{{
  "subgoals": [
    {{"goal": "subgoal 1", "control_flow": "sequence", "reason": "must happen first"}},
    ...
  ],
  "complexity_level": 1-5,
  "estimated_steps": N
}}
"""
        response = await self.llm.ainvoke(prompt)
        try:
            data = json.loads(response.content)
            return data.get("subgoals", [])
        except (json.JSONDecodeError, AttributeError):
            return [{"goal": goal, "control_flow": "sequence"}]

    async def agent_node_execute(
        self,
        goal: str,
        context: str = "",
        depth: int = 0,
        max_retries: int = 2,
    ) -> Thought:
        node_id = f"node_{depth}_{abs(hash(goal))}"
        reasoning_prompt = f"""
Current Goal: {goal}
Context: {context}

Think step-by-step:
1. What is the core objective?
2. What information do I need?
3. Should I solve this directly, or decompose further?

Output JSON:
{{
  "reasoning": "...",
  "action_type": "direct" | "decompose",
  "next_step": "..."
}}
"""
        reasoning_response = await self.llm.ainvoke(reasoning_prompt)
        reasoning_data = self._parse_json(reasoning_response.content)
        node = Thought(
            id=node_id,
            goal=goal,
            parent_id=None,
            reasoning=reasoning_data.get("reasoning", ""),
            action=None,
            observation=None,
        )

        action_type = reasoning_data.get("action_type", "direct")
        if action_type == "decompose" and depth < self.max_depth:
            subgoals_data = await self.decompose_goal(goal, context)
            for subgoal_data in subgoals_data[: self.max_width]:
                subgoal_node = await self.agent_node_execute(
                    subgoal_data.get("goal", goal),
                    context,
                    depth + 1,
                )
                node.subgoals.append(subgoal_node)
            cf_type = (
                subgoals_data[0].get("control_flow", "sequence")
                if subgoals_data
                else "sequence"
            )
            node.control_flow = ControlFlowType(cf_type)
            node.status = "in_progress"
        else:
            action_prompt = f"""
Goal: {goal}
Context: {context}

Available actions:
1. search_web(query)
2. call_tool(tool_name, params)
3. reason_further()
4. return_result(value)

What action should you take? Output JSON with action and params.
"""
            action_response = await self.llm.ainvoke(action_prompt)
            action_data = self._parse_json(action_response.content)
            node.action = action_data.get("action", "reason")
            node.observation = f"Executed {node.action}"
            node.status = "success"
            node.result = {"value": action_data.get("params", {})}

        self.execution_history.append(node)
        return node

    async def execute_tree(self, goal: str, context: str = "") -> Dict[str, Any]:
        self.tree = await self.agent_node_execute(goal, context, depth=0)
        result = await self._execute_control_flow(self.tree)
        return {
            "goal": goal,
            "success": self.tree.status == "success",
            "tree_depth": self._calculate_depth(self.tree),
            "subgoals_count": len(self.tree.subgoals),
            "result": result,
            "history": self.execution_history,
        }

    async def _execute_control_flow(self, node: Thought) -> Dict[str, Any]:
        if not node.subgoals:
            return node.result or {"status": node.status}

        cf_type = node.control_flow or ControlFlowType.SEQUENCE

        if cf_type == ControlFlowType.SEQUENCE:
            results = []
            for subgoal in node.subgoals:
                result = await self._execute_control_flow(subgoal)
                results.append(result)
                if subgoal.status == "failed":
                    node.status = "failed"
                    return {"error": f"sequence failed at {subgoal.goal}"}
            node.status = "success"
            return {"results": results, "flow": "sequence"}

        if cf_type == ControlFlowType.FALLBACK:
            for subgoal in node.subgoals:
                result = await self._execute_control_flow(subgoal)
                if subgoal.status == "success":
                    node.status = "success"
                    return result
            node.status = "failed"
            return {"error": "all fallbacks failed"}

        results = []
        parallel = await asyncio.gather(
            *(self._execute_control_flow(subgoal) for subgoal in node.subgoals)
        )
        results.extend(parallel)
        node.status = "success"
        return {"results": results, "flow": "parallel"}

    def _calculate_depth(self, node: Thought, depth: int = 0) -> int:
        if not node.subgoals:
            return depth
        return max(
            self._calculate_depth(subgoal, depth + 1) for subgoal in node.subgoals
        )

    @staticmethod
    def _parse_json(payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return {}
