#!/usr/bin/env python3
"""
Test script for OmniMind ReAct Agent
Demonstrates Think → Act → Observe loop
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents import ReactAgent
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def main():
    console.print(
        "\n[bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]"
    )
    console.print(
        "[bold cyan]║     🧠 OmniMind ReAct Agent - Test Demo                  ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]\n"
    )

    # Initialize agent
    console.print("🔧 Initializing ReactAgent...")
    try:
        agent = ReactAgent(config_path="config/agent_config.yaml")
        console.print("✓ Agent initialized\n", style="green")
    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        return 1

    # Test tasks
    tasks = [
        {
            "name": "System Status Check",
            "task": "Get current system status including CPU, RAM and GPU",
        },
        {
            "name": "List Project Files",
            "task": "List all files in the current project directory",
        },
        {
            "name": "Create Test File",
            "task": "Create a file called test_output.txt with content 'Hello from OmniMind!'",
        },
    ]

    for i, test in enumerate(tasks, 1):
        console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
        console.print(f"[bold white]Test {i}/3: {test['name']}[/bold white]")
        console.print(f"[bold yellow]{'='*60}[/bold yellow]\n")

        console.print(
            Panel(test["task"], title="[bold]Task[/bold]", border_style="blue")
        )

        console.print("\n🤔 Running ReAct loop...\n")

        # Run agent
        try:
            result = agent.run(test["task"], max_iterations=3)

            # Display results
            console.print("[bold green]✓ Task completed[/bold green]\n")

            console.print("[bold]Messages:[/bold]")
            for msg in result.get("messages", []):
                if msg.startswith("[THINK]"):
                    console.print(f"  💭 {msg}", style="cyan")
                elif msg.startswith("[ACT]"):
                    console.print(f"  ⚡ {msg}", style="yellow")
                elif msg.startswith("[OBSERVE]"):
                    console.print(f"  👁️  {msg}", style="green")
                else:
                    console.print(f"  ℹ️  {msg}")

            console.print(f"\n[bold]Iterations:[/bold] {result.get('iteration', 0)}")
            console.print(f"[bold]Completed:[/bold] {result.get('completed', False)}")
            console.print(
                f"[bold]Final Result:[/bold] {result.get('final_result', 'N/A')}"
            )

            if "actions_taken" in result:
                console.print(
                    f"\n[bold]Actions Taken:[/bold] {len(result['actions_taken'])}"
                )
                for action in result["actions_taken"]:
                    console.print(f"  • {action['action']}({action.get('args', {})})")

        except Exception as e:
            console.print(f"[bold red]✗ Error: {e}[/bold red]")

    # Summary
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print("[bold white]Test Summary[/bold white]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

    # Check memory
    stats = agent.memory.get_stats()
    console.print(f"📊 Episodic Memory: {stats['total_episodes']} episodes stored")
    console.print(f"🔧 Configuration: config/agent_config.yaml")
    console.print(f"🗄️  Vector DB: Qdrant @ {agent.config['memory']['qdrant_url']}")

    console.print("\n[bold green]✅ All tests completed![/bold green]\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
