#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.agents.orchestrator_agent import OrchestratorAgent
    print('Import successful')
    orch = OrchestratorAgent('config/agent_config.yaml')
    print('Orchestrator created')
    # Test with a task that should definitely fail
    result = orch.run_orchestrated_task('Execute a command that does not exist: nonexistent_command_xyz', max_iterations_per_subtask=1)
    print(f'Task completed with success: {result.get("success", False)}')
    print(f'Execution details: {len(result.get("execution", {}).get("subtask_results", []))} subtasks')
    
    # Print detailed results
    execution = result.get("execution", {})
    for i, subtask_result in enumerate(execution.get("subtask_results", [])):
        print(f'Subtask {i+1}: {subtask_result.get("description", "Unknown")}')
        print(f'  Completed: {subtask_result.get("completed", False)}')
        print(f'  Summary: {subtask_result.get("summary", "No summary")[:100]}...')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()