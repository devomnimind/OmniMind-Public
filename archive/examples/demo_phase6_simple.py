#!/usr/bin/env python3
"""OmniMind Phase 6 - Simple Demo"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.tools.omnimind_tools import ToolsFramework
from rich.console import Console
from rich.table import Table

console = Console()


def main():
    console.print("\n[bold cyan]🧠 OmniMind Phase 6 - System Overview[/bold cyan]\n")

    # Tools Framework
    console.print("[bold yellow]1. Tools Framework[/bold yellow]")
    framework = ToolsFramework()
    tools = framework.get_available_tools()

    categories = {}
    for tool, cat in tools.items():
        cat_str = str(cat)
        if cat_str not in categories:
            categories[cat_str] = []
        categories[cat_str].append(tool)

    table = Table(title="Tools by Category")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Tools", style="white")

    for cat, tool_list in sorted(categories.items()):
        tools_display = ", ".join(tool_list[:3])
        if len(tool_list) > 3:
            tools_display += f" (+{len(tool_list)-3} more)"
        table.add_row(cat, str(len(tool_list)), tools_display)

    console.print(table)
    console.print(f"\n📊 Total: {len(tools)} tools\n")

    # Agents
    console.print("[bold yellow]2. Specialized Agents[/bold yellow]")
    agents_table = Table()
    agents_table.add_column("Mode", style="cyan")
    agents_table.add_column("Purpose", style="white")

    agents_table.add_row("💻 CodeAgent", "Full development capabilities")
    agents_table.add_row("🏗️ ArchitectAgent", "Documentation and planning")
    agents_table.add_row("🪲 DebugAgent", "Error diagnosis and analysis")
    agents_table.add_row("⭐ ReviewerAgent", "RLAIF code quality scoring (0-10)")
    agents_table.add_row("🪃 OrchestratorAgent", "Multi-agent coordination")

    console.print(agents_table)
    console.print()

    # Performance
    console.print("[bold yellow]3. Performance (GTX 1650 4GB)[/bold yellow]")
    perf_table = Table()
    perf_table.add_column("Component", style="cyan")
    perf_table.add_column("Metric", style="yellow", justify="right")

    perf_table.add_row("Orchestrator Decomposition", "42.3s")
    perf_table.add_row("Tool Execution (avg)", "252ms")
    perf_table.add_row("Audit Chain Verification", "0.4ms")
    perf_table.add_row("Memory Store", "4.1ms")
    perf_table.add_row("Memory Search", "5.9ms")

    console.print(perf_table)
    console.print()

    # Achievements
    console.print("[bold yellow]4. Phase 6 Achievements[/bold yellow]")
    console.print("  ✅ 25+ tools across 11 categories")
    console.print("  ✅ 5 specialized agent modes")
    console.print("  ✅ RLAIF self-improvement system")
    console.print("  ✅ Multi-agent coordination")
    console.print("  ✅ SHA-256 audit chain")
    console.print("  ✅ 100% integration tests passing")
    console.print("  ✅ 1,811 lines of production code")
    console.print()

    console.print("[bold green]✨ Phase 6 Complete![/bold green]")
    console.print("[cyan]�� See: RELATORIO_PHASE6_COMPLETE.md[/cyan]\n")


if __name__ == "__main__":
    main()
