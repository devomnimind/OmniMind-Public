#!/bin/bash

# Criar DebugAgent
cat > src/agents/debug_agent.py << 'DEBUGEOF'
#!/usr/bin/env python3
"""
DebugAgent - Agente de diagnóstico e debug
Modo: debug (🪲)

Função: Diagnostico avançado, isolamento de bugs, identificação de causas
Ferramentas: read, search, inspect_context, execute_command (limitado), diagnose_error
Quando usar: Build quebrado, edge cases, race conditions
"""

import json
from typing import Dict, Any
from .react_agent import ReactAgent, AgentState
from ..tools.omnimind_tools import ToolsFramework, ToolCategory

class DebugAgent(ReactAgent):
    """Agente especializado em diagnóstico e debugging"""
    
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.tools_framework = ToolsFramework()
        self.mode = "debug"
        
        # Ferramentas permitidas
        self.allowed_tool_categories = [
            ToolCategory.PERCEPTION,
            ToolCategory.REASONING  # analyze_code, diagnose_error
        ]
        
        # Comandos permitidos (read-only e diagnóstico)
        self.allowed_commands = ['ls', 'cat', 'grep', 'find', 'python3 -m pytest', 'git status']
    
    def _execute_action(self, action: str, args: dict) -> str:
        try:
            # Bloquear escrita
            if action in ['write_to_file', 'update_file', 'insert_content']:
                return "DebugAgent cannot modify files. Delegate to CodeAgent for fixes."
            
            # Comandos limitados
            if action == 'execute_command':
                command = args.get('command', '')
                if not any(cmd in command for cmd in self.allowed_commands):
                    return f"Command not allowed. Debug commands: {self.allowed_commands}"
            
            if action not in self.tools_framework.tools:
                return f"Unknown tool: {action}"
            
            result = self.tools_framework.execute_tool(action, **args)
            return json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _think_node(self, state: AgentState) -> AgentState:
        similar_episodes = self.memory.search_similar(state['current_task'], top_k=3)
        system_status = self.tools_framework.execute_tool('inspect_context')
        
        prompt = f"""You are DebugAgent 🪲, an expert debugger and diagnostician.

TASK: {state['current_task']}
MODE: {self.mode} (debugging & diagnosis)
ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

CAPABILITIES:
- Read and analyze code
- Search for patterns and errors
- Inspect system context
- Diagnose errors with suggestions
- Execute diagnostic commands (read-only)

CONSTRAINTS:
- Cannot modify files (delegate to CodeAgent)
- Limited command execution (diagnostic only)

AVAILABLE TOOLS:
- read_file, list_files, search_files, codebase_search
- inspect_context: System status
- analyze_code: Code quality analysis
- diagnose_error: Error diagnosis with suggestions
- execute_command: Limited to {self.allowed_commands}

PREVIOUS OBSERVATIONS:
{chr(10).join([f"- {o[:150]}" for o in state['observations']]) if state['observations'] else "None"}

Focus on:
1. Identifying root causes
2. Analyzing error patterns
3. Suggesting fixes
4. Locating edge cases

REASONING: <diagnostic analysis>
ACTION: <tool_name>
ARGS: <json dict>

Response:"""
        
        response = self.llm.invoke(prompt)
        state['reasoning_chain'].append(response)
        state['messages'].append(f"[THINK-DEBUG] {response[:500]}...")
        return state

__all__ = ['DebugAgent']
DEBUGEOF

# Criar ReviewerAgent
cat > src/agents/reviewer_agent.py << 'REVIEWEOF'
#!/usr/bin/env python3
"""
ReviewerAgent - Agente crítico com RLAIF scoring
Modo: reviewer (⭐)

Função: Avalia código/resultados com score 0-10
Critérios: correctness, readability, efficiency, security
Gera feedback detalhado para refinamento (RLAIF loop)
"""

import json
from typing import Dict, Any, Tuple
from .react_agent import ReactAgent, AgentState
from ..tools.omnimind_tools import ToolsFramework

class ReviewerAgent(ReactAgent):
    """Agente revisor com RLAIF (Reinforcement Learning from AI Feedback)"""
    
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.tools_framework = ToolsFramework()
        self.mode = "reviewer"
        
        # Critérios de avaliação
        self.criteria = {
            'correctness': 'Does it work correctly?',
            'readability': 'Is it clean and understandable?',
            'efficiency': 'Is it performant?',
            'security': 'Is it secure?',
            'maintainability': 'Is it maintainable?'
        }
    
    def review_code(self, filepath: str, task_description: str) -> Dict[str, Any]:
        """Revisa código e retorna score + feedback"""
        try:
            # Ler código
            code_content = self.tools_framework.execute_tool('read_file', filepath=filepath)
            
            # Analisar
            analysis = self.tools_framework.execute_tool('analyze_code', filepath=filepath)
            
            # Gerar review via LLM
            prompt = f"""You are ReviewerAgent ⭐, an expert code reviewer using RLAIF scoring.

TASK: {task_description}
FILE: {filepath}

CODE TO REVIEW:
```
{code_content[:1000]}...
```

AUTOMATED ANALYSIS:
{json.dumps(analysis, indent=2)}

REVIEW CRITERIA (score each 0-10):
{chr(10).join([f"- {k}: {v}" for k, v in self.criteria.items()])}

Provide detailed review in this format:

SCORES:
correctness: <0-10>
readability: <0-10>
efficiency: <0-10>
security: <0-10>
maintainability: <0-10>

OVERALL_SCORE: <average>

STRENGTHS:
- <point 1>
- <point 2>

WEAKNESSES:
- <issue 1>
- <issue 2>

SUGGESTIONS:
- <improvement 1>
- <improvement 2>

CRITICAL_ISSUES:
- <blocker if any>

Your review:"""
            
            response = self.llm.invoke(prompt)
            
            # Parsear scores
            scores = self._parse_scores(response)
            overall = scores.get('OVERALL_SCORE', sum(scores.values()) / len(scores) if scores else 5.0)
            
            review = {
                'filepath': filepath,
                'task': task_description,
                'scores': scores,
                'overall_score': overall,
                'passed': overall >= 7.0,
                'feedback': response,
                'timestamp': self._timestamp()
            }
            
            # Armazenar feedback
            self.tools_framework.execute_tool('collect_feedback', 
                                            feedback_type='code_review',
                                            data=review)
            
            return review
        
        except Exception as e:
            return {'error': str(e), 'overall_score': 0.0, 'passed': False}
    
    def _parse_scores(self, response: str) -> Dict[str, float]:
        """Extrai scores do texto"""
        scores = {}
        for line in response.split('\n'):
            for criterion in self.criteria.keys():
                if criterion in line.lower() and ':' in line:
                    try:
                        score_str = line.split(':')[1].strip().split()[0]
                        scores[criterion] = float(score_str)
                    except:
                        pass
            if 'OVERALL_SCORE:' in line or 'overall:' in line.lower():
                try:
                    score_str = line.split(':')[1].strip().split()[0]
                    scores['OVERALL_SCORE'] = float(score_str)
                except:
                    pass
        return scores
    
    def run_review_cycle(self, coder_agent, task: str, max_attempts: int = 3) -> Dict[str, Any]:
        """Executa loop RLAIF: Code → Review → Refine"""
        attempt = 0
        best_score = 0.0
        best_result = None
        
        while attempt < max_attempts:
            attempt += 1
            
            # Coder gera código
            code_result = coder_agent.run_code_task(task)
            
            # Reviewer avalia
            if code_result.get('completed'):
                # Assumir que criou arquivo
                filepath = f"generated_code_{attempt}.py"
                review = self.review_code(filepath, task)
                
                score = review.get('overall_score', 0.0)
                
                if score >= 7.0:
                    return {'success': True, 'attempts': attempt, 'final_score': score, 'review': review}
                
                if score > best_score:
                    best_score = score
                    best_result = review
                
                # Feedback para próxima iteração
                task = f"{task}\n\nPREVIOUS FEEDBACK:\n{review['feedback']}"
        
        return {'success': False, 'attempts': attempt, 'best_score': best_score, 'best_review': best_result}

__all__ = ['ReviewerAgent']
REVIEWEOF

echo "✅ Created DebugAgent and ReviewerAgent"
