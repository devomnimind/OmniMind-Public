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

import pytest

from src.orchestrator.task_executor import TaskExecutor


@pytest.mark.asyncio
async def test_quantum_execution():
    """Teste: Execução quântica local com GPU"""
    executor = TaskExecutor()

    task = {
        "id": "test_quantum",
        "name": "Bell State Test",
        "action": "quantum_circuit",
        "params": {"n_qubits": 2},
        "timeout": 10,
    }

    result = await executor.execute_task(task["id"], task)

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

    task = {
        "id": "test_symbolic",
        "name": "Reasoning Test",
        "action": "symbolic_reasoning",
        "params": {"prompt": "What is 2+2?"},
        "timeout": 15,
    }

    result = await executor.execute_task(task["id"], task)

    assert result["status"] == "success"
    assert "response" in result["result"]
    print("✅ Symbolic execution: response received")


@pytest.mark.asyncio
async def test_error_handling():
    """Teste: Tratamento robusto de erros"""
    executor = TaskExecutor()

    # Task inválida
    task = {
        "id": "test_invalid",
        "name": "Invalid Task",
        # Falta 'action' - deve falhar graciosamente
        "timeout": 5,
    }

    result = await executor.execute_task(task["id"], task)

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
