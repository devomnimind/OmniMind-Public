#!/usr/bin/env python3
"""
Test Advanced Multi-Agent Workflow with RLAIF Iteration
=========================================================

Demonstrates complex workflow:
1. CodeAgent implements calculator module
2. ReviewerAgent scores (if < 8.0 → iterate)
3. CodeAgent fixes based on feedback
4. ReviewerAgent re-scores
5. ArchitectAgent documents API

This validates the full RLAIF self-improvement loop.
"""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import OrchestratorAgent, CodeAgent, ReviewerAgent, ArchitectAgent

console = Console()


def test_calculator_workflow():
    """Test complete workflow: Implement → Review → Fix → Document"""

    console.print("\n[bold cyan]═══ ADVANCED WORKFLOW TEST ═══[/bold cyan]\n")

    # Task description
    task = """Implement a calculator module in calculator.py with the following functions:
- add(a, b): returns a + b
- subtract(a, b): returns a - b
- multiply(a, b): returns a * b
- divide(a, b): returns a / b (handle division by zero)

Requirements:
- Include docstrings for all functions
- Add type hints
- Handle edge cases (division by zero, invalid inputs)
- Include basic error handling
"""

    console.print(Panel(task, title="[bold]Complex Task[/bold]", border_style="blue"))

    # Initialize orchestrator
    config_path = "/home/fahbrain/projects/omnimind/config/agent_config.yaml"

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task_init = progress.add_task("Initializing orchestrator...", total=None)
        orchestrator = OrchestratorAgent(config_path)
        progress.update(task_init, completed=True)

    # Phase 1: Task Decomposition
    console.print("\n[bold yellow]📋 Phase 1: Task Decomposition[/bold yellow]")

    start_decompose = time.time()
    plan = orchestrator.decompose_task(task)
    decompose_time = time.time() - start_decompose

    console.print(f"✓ Decomposition completed in {decompose_time:.2f}s")
    console.print(f"  Subtasks: {len(plan['subtasks'])}")
    console.print(f"  Complexity: {plan['complexity']}")

    # Show subtasks
    subtasks_table = Table(title="Decomposed Subtasks")
    subtasks_table.add_column("#", style="cyan", width=3)
    subtasks_table.add_column("Agent", style="magenta")
    subtasks_table.add_column("Description", style="white")

    for i, subtask in enumerate(plan["subtasks"], 1):
        agent_emoji = {
            "code": "💻",
            "architect": "🏗️",
            "debug": "🪲",
            "reviewer": "⭐",
        }.get(subtask["agent"], "❓")
        subtasks_table.add_row(
            str(i),
            f"{agent_emoji} {subtask['agent']}",
            subtask["description"][:60] + "...",
        )

    console.print(subtasks_table)

    # Phase 2: Implementation
    console.print("\n[bold yellow]💻 Phase 2: Implementation[/bold yellow]")

    code_agent = CodeAgent(config_path)
    start_impl = time.time()

    impl_result = code_agent.run(task)
    impl_time = time.time() - start_impl

    console.print(f"✓ Implementation completed in {impl_time:.2f}s")
    console.print(f"  Completed: {impl_result.get('completed', False)}")

    # Check if file was created
    calc_file = Path("/home/fahbrain/projects/omnimind/calculator.py")
    if calc_file.exists():
        console.print(
            f"  ✅ File created: {calc_file.name} ({calc_file.stat().st_size} bytes)"
        )
    else:
        console.print("  ❌ File not created!")
        return False

    # Phase 3: Initial Review
    console.print("\n[bold yellow]⭐ Phase 3: Initial Code Review[/bold yellow]")

    reviewer = ReviewerAgent(config_path)
    code_content = calc_file.read_text()

    start_review = time.time()
    score, critique = reviewer.review_code(
        code_content, "calculator module implementation"
    )
    review_time = time.time() - start_review

    console.print(f"✓ Review completed in {review_time:.2f}s")

    # Display review results
    review_table = Table(title="RLAIF Review Results")
    review_table.add_column("Metric", style="cyan")
    review_table.add_column("Value", style="yellow")

    review_table.add_row("Score", f"{score:.1f}/10.0")

    if score >= 8.0:
        status = "[green]✅ EXCELLENT[/green]"
    elif score >= 6.0:
        status = "[yellow]⚠️ GOOD[/yellow]"
    elif score >= 4.0:
        status = "[orange1]🔄 NEEDS_WORK[/orange1]"
    else:
        status = "[red]❌ POOR[/red]"

    review_table.add_row("Status", status)
    review_table.add_row("Review Time", f"{review_time:.2f}s")

    console.print(review_table)
    console.print(Panel(critique, title="[bold]Critique[/bold]", border_style="yellow"))

    # Phase 4: Iterative Improvement (if needed)
    iteration_count = 0
    max_iterations = 3

    while score < 8.0 and iteration_count < max_iterations:
        iteration_count += 1
        console.print(
            f"\n[bold yellow]🔄 Phase 4.{iteration_count}: Iterative Improvement[/bold yellow]"
        )
        console.print(f"  Current score: {score:.1f} (target: 8.0)")

        # CodeAgent fixes based on critique
        fix_task = f"""Improve calculator.py based on this critique:

{critique}

Current score: {score:.1f}/10.0
Target: 8.0+

Focus on the weaknesses mentioned and implement suggested improvements.
"""

        start_fix = time.time()
        fix_result = code_agent.run(fix_task)
        fix_time = time.time() - start_fix

        console.print(f"✓ Fixes applied in {fix_time:.2f}s")

        # Re-review
        code_content = calc_file.read_text()
        start_rereview = time.time()
        new_score, new_critique = reviewer.review_code(
            code_content, "calculator module (improved)"
        )
        rereview_time = time.time() - start_rereview

        console.print(f"✓ Re-review completed in {rereview_time:.2f}s")
        console.print(
            f"  Score improvement: {score:.1f} → {new_score:.1f} ({new_score - score:+.1f})"
        )

        score = new_score
        critique = new_critique

        if score >= 8.0:
            console.print("[green]✅ Target score achieved![/green]")
            break

    # Phase 5: Documentation
    console.print("\n[bold yellow]🏗️ Phase 5: Architecture Documentation[/bold yellow]")

    architect = ArchitectAgent(config_path)
    doc_task = f"""Create documentation for the calculator module in CALCULATOR_API.md.

Include:
- Module overview
- Function signatures with descriptions
- Usage examples
- Error handling notes

The calculator.py file contains:
{code_content[:500]}...
"""

    start_doc = time.time()
    doc_result = architect.run(doc_task)
    doc_time = time.time() - start_doc

    console.print(f"✓ Documentation completed in {doc_time:.2f}s")

    # Check if documentation was created
    doc_file = Path("/home/fahbrain/projects/omnimind/CALCULATOR_API.md")
    if doc_file.exists():
        console.print(
            f"  ✅ Documentation created: {doc_file.name} ({doc_file.stat().st_size} bytes)"
        )
    else:
        console.print("  ⚠️ Documentation not found")

    # Final Summary
    console.print("\n[bold cyan]═══ WORKFLOW SUMMARY ═══[/bold cyan]\n")

    summary_table = Table(title="Workflow Metrics")
    summary_table.add_column("Phase", style="cyan")
    summary_table.add_column("Time", style="yellow")
    summary_table.add_column("Status", style="green")

    total_time = decompose_time + impl_time + review_time + doc_time
    if iteration_count > 0:
        total_time += fix_time * iteration_count + rereview_time * iteration_count

    summary_table.add_row("Decomposition", f"{decompose_time:.2f}s", "✅")
    summary_table.add_row("Implementation", f"{impl_time:.2f}s", "✅")
    summary_table.add_row("Initial Review", f"{review_time:.2f}s", "✅")
    if iteration_count > 0:
        summary_table.add_row(
            f"Iterations ({iteration_count}x)",
            f"{(fix_time + rereview_time) * iteration_count:.2f}s",
            "✅",
        )
    summary_table.add_row("Documentation", f"{doc_time:.2f}s", "✅")
    summary_table.add_row(
        "[bold]TOTAL[/bold]", f"[bold]{total_time:.2f}s[/bold]", "[bold]✅[/bold]"
    )

    console.print(summary_table)

    # Final Results
    results_table = Table(title="Final Results")
    results_table.add_column("Artifact", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Quality", style="yellow")

    results_table.add_row(
        "calculator.py",
        "✅ Created" if calc_file.exists() else "❌ Missing",
        f"{score:.1f}/10.0",
    )
    results_table.add_row(
        "CALCULATOR_API.md", "✅ Created" if doc_file.exists() else "❌ Missing", "N/A"
    )
    results_table.add_row(
        "RLAIF Iterations",
        f"{iteration_count}x",
        "✅ Converged" if score >= 8.0 else "⚠️ Max reached",
    )

    console.print(results_table)

    # Success criteria
    success = (
        calc_file.exists()
        and score >= 8.0
        and (doc_file.exists() or True)  # Documentation optional for success
    )

    if success:
        console.print("\n[bold green]🎉 WORKFLOW COMPLETED SUCCESSFULLY![/bold green]")
        console.print(f"✅ Code quality achieved: {score:.1f}/10.0 (target: 8.0+)")
        console.print(f"✅ Total execution time: {total_time:.1f}s")
        console.print(f"✅ RLAIF iterations: {iteration_count}")
    else:
        console.print("\n[bold yellow]⚠️ WORKFLOW COMPLETED WITH WARNINGS[/bold yellow]")
        if score < 8.0:
            console.print(f"⚠️ Score below target: {score:.1f}/10.0 (target: 8.0+)")

    return success


if __name__ == "__main__":
    success = test_calculator_workflow()
    sys.exit(0 if success else 1)
