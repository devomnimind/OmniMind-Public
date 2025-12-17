from typing import Any, Dict

import pytest

from src.orchestrator.task_executor import TaskExecutor


@pytest.mark.asyncio
async def test_quantum_execution():
    """Teste: Execução quântica local com GPU"""
    executor = TaskExecutor()

    task: Dict[str, Any] = {
        "id": "test_quantum",
        "name": "Bell State Test",
        "action": "quantum_circuit",
        "params": {"n_qubits": 2},
        "timeout": 10,
    }

    task_id: str = str(task["id"])
    result = await executor.execute_task(task_id, task)

    assert result["status"] == "success"
    assert "result" in result
    # Check for backend info if available
    if "backend" in result["result"]:
        backend_name = result["result"]["backend"]
        print(f"✅ Quantum execution: {backend_name}")


@pytest.mark.asyncio
async def test_symbolic_execution():
    """Teste: Raciocínio simbólico via Ollama"""
    executor = TaskExecutor()

    task: Dict[str, Any] = {
        "id": "test_symbolic",
        "name": "Reasoning Test",
        "action": "symbolic_reasoning",
        "params": {"prompt": "What is 2+2?"},
        "timeout": 15,
    }

    task_id_symbolic: str = str(task["id"])
    result = await executor.execute_task(task_id_symbolic, task)

    assert result["status"] == "success"
    assert "response" in result["result"]
    print("✅ Symbolic execution: response received")


@pytest.mark.asyncio
async def test_error_handling():
    """Teste: Tratamento robusto de erros"""
    executor = TaskExecutor()

    # Task inválida
    task: Dict[str, Any] = {
        "id": "test_invalid",
        "name": "Invalid Task",
        # Falta 'action' - deve falhar graciosamente
        "timeout": 5,
    }

    task_id_invalid: str = str(task["id"])
    result = await executor.execute_task(task_id_invalid, task)

    assert result["status"] == "error"
    assert task["id"] in executor.failed_tasks
    print("✅ Error handling: properly caught and logged")


@pytest.mark.asyncio
async def test_workflow_execution():
    """Teste: Execução de workflow com dependências"""
    executor = TaskExecutor()

    workflow = [
        {
            "id": "q1",
            "name": "Q1",
            "action": "quantum_circuit",
            "params": {"n_qubits": 2},
            "timeout": 10,
        },
        {"id": "s1", "name": "S1", "action": "consciousness_check", "timeout": 5},
    ]

    results = await executor.execute_workflow(workflow)

    assert len(results) == 2
    assert all(r["status"] in ["success", "error"] for r in results.values())
    print(f"✅ Workflow execution: {len(results)} tasks completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
