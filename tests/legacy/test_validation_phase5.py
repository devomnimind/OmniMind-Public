#!/usr/bin/env python3
"""
Phase 5 Validation Test - Verify completion flag works correctly
"""

import sys

sys.path.insert(0, ".")

from src.agents import ReactAgent
from rich.console import Console
from rich.table import Table

console = Console()


def test_completion_flags():
    """Test that completed flag is set correctly"""
    agent = ReactAgent("config/agent_config.yaml")

    console.print("\n[bold cyan]═══ PHASE 5 VALIDATION TEST ═══[/bold cyan]\n")

    tests = [
        ("System Info", "Get system status", True),
        (
            "File Write",
            "Create file validation_test.txt with content 'Phase 5 validated'",
            True,
        ),
        ("File Read", "Read the file validation_test.txt", True),
    ]

    results = []

    for name, task, expected_complete in tests:
        console.print(f"[yellow]Testing:[/yellow] {name}")
        result = agent.run(task, max_iterations=3)

        passed = result["completed"] == expected_complete
        results.append(
            {
                "name": name,
                "completed": result["completed"],
                "expected": expected_complete,
                "iterations": result["iteration"],
                "passed": passed,
            }
        )

        icon = "✅" if passed else "❌"
        console.print(
            f"{icon} Completed={result['completed']}, Iterations={result['iteration']}\n"
        )

    # Summary table
    table = Table(title="Validation Results")
    table.add_column("Test", style="cyan")
    table.add_column("Expected", style="blue")
    table.add_column("Actual", style="green")
    table.add_column("Iterations", style="yellow")
    table.add_column("Status", style="bold")

    for r in results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        table.add_row(
            r["name"],
            str(r["expected"]),
            str(r["completed"]),
            str(r["iterations"]),
            status,
        )

    console.print(table)

    # Final verdict
    all_passed = all(r["passed"] for r in results)
    if all_passed:
        console.print("\n[bold green]🎉 ALL VALIDATION TESTS PASSED![/bold green]")
        console.print("[green]✅ Phase 5 is production-ready[/green]")
        console.print("[green]✅ Ready to proceed to Phase 6[/green]\n")
        return 0
    else:
        console.print("\n[bold red]❌ VALIDATION FAILED[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(test_completion_flags())
