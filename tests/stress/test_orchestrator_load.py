import asyncio
import time
import pytest
from src.orchestrator.task_executor import TaskExecutor

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


async def run_load_test(num_tasks: int):
    """Helper to run N tasks and return stats."""
    executor = TaskExecutor()
    tasks = []

    # Mix of tasks: Quantum (simulated), Symbolic (mocked/real), Simple
    for i in range(num_tasks):
        task_type = i % 3
        if task_type == 0:
            task = {
                "id": f"load_q_{i}",
                "name": f"Quantum Load {i}",
                "action": "quantum_circuit",
                "params": {"n_qubits": 2},  # Will use local simulator
                "timeout": 10,
            }
        elif task_type == 1:
            task = {
                "id": f"load_s_{i}",
                "name": f"Symbolic Load {i}",
                "action": "symbolic_reasoning",
                "params": {"prompt": "ping"},  # Short prompt
                "timeout": 10,
            }
        else:
            task = {
                "id": f"load_c_{i}",
                "name": f"Consciousness Load {i}",
                "action": "consciousness_check",
                "timeout": 5,
            }
        tasks.append(task)

    start_time = time.time()
    # Execute concurrently
    # TaskExecutor.execute_workflow is sequential currently.
    # We should test concurrent execution via asyncio.gather to stress it.

    futures = [executor.execute_task(t["id"], t) for t in tasks]
    results = await asyncio.gather(*futures)
    end_time = time.time()

    duration = end_time - start_time
    success_count = sum(1 for r in results if r["status"] == "success")

    return {
        "total": num_tasks,
        "success": success_count,
        "duration": duration,
        "tps": num_tasks / duration if duration > 0 else 0,
    }


@pytest.mark.asyncio
async def test_load_004_tasks():
    """Baseline: 4 tasks"""
    stats = await run_load_test(4)
    print(
        f"\n[LOAD 4] Success: {stats['success']}/{stats['total']} "
        f"in {stats['duration']:.2f}s ({stats['tps']:.1f} TPS)"
    )
    assert stats["success"] == 4


@pytest.mark.asyncio
async def test_load_008_tasks():
    """Ramp-up: 8 tasks"""
    stats = await run_load_test(8)
    print(
        f"\n[LOAD 8] Success: {stats['success']}/{stats['total']} "
        f"in {stats['duration']:.2f}s ({stats['tps']:.1f} TPS)"
    )
    assert stats["success"] >= 7  # Allow 1 failure


@pytest.mark.asyncio
async def test_load_016_tasks():
    """Ramp-up: 16 tasks"""
    stats = await run_load_test(16)
    print(
        f"\n[LOAD 16] Success: {stats['success']}/{stats['total']} "
        f"in {stats['duration']:.2f}s ({stats['tps']:.1f} TPS)"
    )
    assert stats["success"] >= 15


@pytest.mark.asyncio
async def test_load_032_tasks():
    """Ramp-up: 32 tasks"""
    stats = await run_load_test(32)
    print(
        f"\n[LOAD 32] Success: {stats['success']}/{stats['total']} "
        f"in {stats['duration']:.2f}s ({stats['tps']:.1f} TPS)"
    )
    assert stats["success"] >= 30


@pytest.mark.asyncio
async def test_load_064_tasks():
    """Stress: 64 tasks"""
    stats = await run_load_test(64)
    print(
        f"\n[LOAD 64] Success: {stats['success']}/{stats['total']} "
        f"in {stats['duration']:.2f}s ({stats['tps']:.1f} TPS)"
    )
    assert stats["success"] >= 60


@pytest.mark.asyncio
async def test_load_128_tasks():
    """Max Stress: 128 tasks"""
    stats = await run_load_test(128)
    print(
        f"\n[LOAD 128] Success: {stats['success']}/{stats['total']} "
        f"in {stats['duration']:.2f}s ({stats['tps']:.1f} TPS)"
    )
    assert stats["success"] >= 120  # >90% success rate
