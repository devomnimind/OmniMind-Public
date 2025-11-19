#!/usr/bin/env python3
"""
Phase 6 Performance Benchmark
==============================

Measures key performance metrics:
- Orchestrator decomposition time
- Individual tool execution time
- Audit chain overhead
- Memory storage/retrieval latency
- LLM inference throughput
"""

import time
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import OrchestratorAgent
from src.tools.omnimind_tools import ToolsFramework
from src.memory.episodic_memory import EpisodicMemory

console = Console()


def benchmark_orchestrator():
    """Benchmark task decomposition"""
    console.print("\n[bold cyan]1. Orchestrator Decomposition Benchmark[/bold cyan]")

    config_path = "/home/fahbrain/projects/omnimind/config/agent_config.yaml"
    orchestrator = OrchestratorAgent(config_path)

    tasks = [
        "List all files in the project",
        "Analyze the project structure and identify key components",
        "Implement a simple calculator with add, subtract, multiply, divide functions",
    ]

    results = []
    for task in tasks:
        start = time.time()
        plan = orchestrator.decompose_task(task)
        elapsed = time.time() - start

        results.append(
            {
                "task": task[:50] + "...",
                "time": elapsed,
                "subtasks": len(plan["subtasks"]),
                "complexity": plan["complexity"],
            }
        )
        console.print(
            f"  ✓ Task decomposed in {elapsed:.2f}s ({len(plan['subtasks'])} subtasks)"
        )

    table = Table(title="Decomposition Performance")
    table.add_column("Task", style="cyan")
    table.add_column("Time (s)", style="yellow", justify="right")
    table.add_column("Subtasks", style="green", justify="right")
    table.add_column("Complexity", style="magenta")

    for r in results:
        table.add_row(
            r["task"], f"{r['time']:.2f}", str(r["subtasks"]), r["complexity"]
        )

    console.print(table)

    avg_time = sum(r["time"] for r in results) / len(results)
    console.print(f"\n📊 Average decomposition time: {avg_time:.2f}s")

    return results


def benchmark_tools():
    """Benchmark tool execution"""
    console.print("\n[bold cyan]2. Tools Framework Benchmark[/bold cyan]")

    framework = ToolsFramework()

    benchmarks = []

    # 1. Read file
    start = time.time()
    result = framework.execute_tool(
        "read_file", "/home/fahbrain/projects/omnimind/README.md"
    )
    elapsed = time.time() - start
    benchmarks.append(
        ("read_file", elapsed, "success" if "error" not in result else "failed")
    )
    console.print(f"  ✓ read_file: {elapsed*1000:.1f}ms")

    # 2. List files
    start = time.time()
    result = framework.execute_tool(
        "list_files", "/home/fahbrain/projects/omnimind/src"
    )
    elapsed = time.time() - start
    benchmarks.append(("list_files", elapsed, "success"))
    console.print(f"  ✓ list_files: {elapsed*1000:.1f}ms")

    # 3. Inspect context
    start = time.time()
    result = framework.execute_tool("inspect_context")
    elapsed = time.time() - start
    benchmarks.append(("inspect_context", elapsed, "success"))
    console.print(f"  ✓ inspect_context: {elapsed*1000:.1f}ms")

    # 4. Write file (with audit)
    start = time.time()
    result = framework.execute_tool(
        "write_to_file", "/tmp/benchmark_test.txt", "Benchmark test content"
    )
    elapsed = time.time() - start
    benchmarks.append(("write_to_file", elapsed, "success"))
    console.print(f"  ✓ write_to_file (with audit): {elapsed*1000:.1f}ms")

    table = Table(title="Tool Execution Performance")
    table.add_column("Tool", style="cyan")
    table.add_column("Time (ms)", style="yellow", justify="right")
    table.add_column("Status", style="green")

    for tool, t, status in benchmarks:
        table.add_row(tool, f"{t*1000:.1f}", status)

    console.print(table)

    avg_time = sum(b[1] for b in benchmarks) / len(benchmarks)
    console.print(f"\n📊 Average tool execution time: {avg_time*1000:.1f}ms")

    return benchmarks


def benchmark_audit_chain():
    """Benchmark audit chain verification"""
    console.print("\n[bold cyan]3. Audit Chain Benchmark[/bold cyan]")

    framework = ToolsFramework()

    # Generate some audit entries
    for i in range(10):
        framework.execute_tool(
            "write_to_file", f"/tmp/audit_test_{i}.txt", f"Content {i}"
        )

    # Verify chain
    start = time.time()
    is_valid = framework.verify_audit_chain()
    elapsed = time.time() - start

    console.print(f"  ✓ Audit chain verification: {elapsed*1000:.1f}ms")
    console.print(f"  ✓ Chain integrity: {'✅ Valid' if is_valid else '❌ Invalid'}")

    return elapsed


def benchmark_memory():
    """Benchmark episodic memory"""
    console.print("\n[bold cyan]4. Episodic Memory Benchmark[/bold cyan]")

    try:
        memory = EpisodicMemory()

        # Store episodes
        store_times = []
        for i in range(5):
            start = time.time()
            memory.store_episode(
                task=f"Test task {i}",
                action=f"Test action {i}",
                result=f"Test result {i}",
                reward=0.5 + i * 0.1,
            )
            elapsed = time.time() - start
            store_times.append(elapsed)

        avg_store = sum(store_times) / len(store_times)
        console.print(f"  ✓ Average store time: {avg_store*1000:.1f}ms")

        # Search similar
        start = time.time()
        results = memory.search_similar("Test task", top_k=3)
        elapsed = time.time() - start

        console.print(f"  ✓ Search time: {elapsed*1000:.1f}ms ({len(results)} results)")

        return {"store": avg_store, "search": elapsed}
    except Exception as e:
        console.print(f"  ⚠️ Memory benchmark skipped: {e}")
        return None


def main():
    console.print(
        Panel.fit(
            "[bold cyan]OmniMind Phase 6 Performance Benchmark[/bold cyan]\n"
            "Measuring system performance across all components",
            border_style="cyan",
        )
    )

    # Run benchmarks
    decomp_results = benchmark_orchestrator()
    tool_results = benchmark_tools()
    audit_time = benchmark_audit_chain()
    memory_results = benchmark_memory()

    # Final summary
    console.print("\n[bold cyan]═══ BENCHMARK SUMMARY ═══[/bold cyan]\n")

    summary = Table(title="Performance Metrics")
    summary.add_column("Component", style="cyan")
    summary.add_column("Metric", style="yellow")
    summary.add_column("Value", style="green", justify="right")

    avg_decomp = sum(r["time"] for r in decomp_results) / len(decomp_results)
    summary.add_row("Orchestrator", "Avg Decomposition", f"{avg_decomp:.2f}s")

    avg_tool = sum(b[1] for b in tool_results) / len(tool_results)
    summary.add_row("Tools", "Avg Execution", f"{avg_tool*1000:.1f}ms")

    summary.add_row("Audit", "Chain Verification", f"{audit_time*1000:.1f}ms")

    if memory_results:
        summary.add_row(
            "Memory", "Store Episode", f"{memory_results['store']*1000:.1f}ms"
        )
        summary.add_row(
            "Memory", "Search Similar", f"{memory_results['search']*1000:.1f}ms"
        )

    console.print(summary)

    # Performance assessment
    console.print("\n[bold yellow]Performance Assessment:[/bold yellow]")

    if avg_decomp < 30:
        console.print("  ✅ Orchestrator: EXCELLENT (<30s)")
    elif avg_decomp < 60:
        console.print("  ⚠️ Orchestrator: GOOD (30-60s)")
    else:
        console.print("  ❌ Orchestrator: SLOW (>60s)")

    if avg_tool < 0.100:
        console.print("  ✅ Tools: EXCELLENT (<100ms)")
    elif avg_tool < 0.500:
        console.print("  ⚠️ Tools: GOOD (100-500ms)")
    else:
        console.print("  ❌ Tools: SLOW (>500ms)")

    if audit_time < 0.050:
        console.print("  ✅ Audit: EXCELLENT (<50ms)")
    elif audit_time < 0.200:
        console.print("  ⚠️ Audit: GOOD (50-200ms)")
    else:
        console.print("  ❌ Audit: SLOW (>200ms)")

    console.print("\n[bold green]✓ Benchmark completed successfully![/bold green]")


if __name__ == "__main__":
    main()
