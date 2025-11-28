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
    print(f'Task completed with success: {result.get("success", False) if isinstance(result, dict) else False}')
    print(f'Execution details: {len(result.get("execution", {}).get("subtask_results", [])) if isinstance(result, dict) else 0} subtasks')
    
    # Print detailed results
    execution = result.get("execution", {}) if isinstance(result, dict) else {}
    for i, subtask_result in enumerate(execution.get("subtask_results", []) if isinstance(execution, dict) else []):
        print(f'Subtask {i+1}: {subtask_result.get("description", "Unknown") if isinstance(subtask_result, dict) else "Invalid result"}')
        print(f'  Completed: {subtask_result.get("completed", False) if isinstance(subtask_result, dict) else False}')
        print(f'  Summary: {subtask_result.get("summary", "No summary")[:100] if isinstance(subtask_result, dict) else "Invalid result"}...')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()