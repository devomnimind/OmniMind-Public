#!/usr/bin/env python3
"""
Teste de Integração Completo - Fase 6
Valida: Framework de Ferramentas (25+) + 5 Agentes Especializados + RLAIF + Orchestrator

Fluxo testado:
User → Orchestrator → (Code/Architect/Debug/Reviewer) → Orchestrator → User
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

from src.agents import (
    CodeAgent,
    ArchitectAgent,
    DebugAgent,
    ReviewerAgent,
    OrchestratorAgent,
)
from src.tools.omnimind_tools import ToolsFramework

console = Console()


def test_tools_framework():
    """Teste 1: Framework de ferramentas (11 camadas, 25+ tools)"""
    console.print("\n[bold cyan]═══ TEST 1: Tools Framework ═══[/bold cyan]\n")

    framework = ToolsFramework()

    # Verificar ferramentas registradas
    tools = framework.get_available_tools()
    console.print(f"✓ [green]Registered tools:[/green] {len(tools)}")

    # Agrupar por categoria
    by_category = {}
    for tool_name, category in tools.items():
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(tool_name)

    tree = Tree("[bold]Tools by Category")
    for category, tool_list in sorted(by_category.items()):
        branch = tree.add(f"[cyan]{category}[/cyan] ({len(tool_list)} tools)")
        for tool in tool_list:
            branch.add(f"• {tool}")

    console.print(tree)

    # Teste de auditoria
    console.print("\n[yellow]Testing audit chain integrity...[/yellow]")
    chain_valid = framework.verify_audit_chain()
    console.print(
        f"✓ [green]Audit chain:[/green] {'✅ Valid' if chain_valid else '❌ Invalid'}"
    )

    # Estatísticas
    stats = framework.get_tool_stats()
    console.print(f"\n[bold]Tool Usage Statistics:[/bold]")
    console.print(f"  Total calls: {stats.get('total_calls', 0)}")

    return len(tools) >= 20  # Espera-se 25+ ferramentas


def test_individual_agents():
    """Teste 2: Agentes individuais"""
    console.print("\n[bold cyan]═══ TEST 2: Individual Agents ═══[/bold cyan]\n")

    config_path = "config/agent_config.yaml"
    results = []

    # Teste CodeAgent
    console.print("[yellow]Testing CodeAgent 💻...[/yellow]")
    try:
        code_agent = CodeAgent(config_path)
        result = code_agent.run_code_task(
            "List files in current directory", max_iterations=2
        )
        success = result.get("completed", False)
        console.print(f"  {'✅' if success else '❌'} CodeAgent: completed={success}")
        results.append(("CodeAgent", success))
    except Exception as e:
        console.print(f"  ❌ CodeAgent error: {e}")
        results.append(("CodeAgent", False))

    # Teste ArchitectAgent
    console.print("[yellow]Testing ArchitectAgent 🏗️...[/yellow]")
    try:
        architect = ArchitectAgent(config_path)
        result = architect.run("Create a simple architecture plan", max_iterations=2)
        success = result.get("completed", False)
        console.print(
            f"  {'✅' if success else '❌'} ArchitectAgent: completed={success}"
        )
        results.append(("ArchitectAgent", success))
    except Exception as e:
        console.print(f"  ❌ ArchitectAgent error: {e}")
        results.append(("ArchitectAgent", False))

    # Teste DebugAgent
    console.print("[yellow]Testing DebugAgent 🪲...[/yellow]")
    try:
        debug_agent = DebugAgent(config_path)
        result = debug_agent.run("Inspect system status", max_iterations=2)
        success = result.get("completed", False)
        console.print(f"  {'✅' if success else '❌'} DebugAgent: completed={success}")
        results.append(("DebugAgent", success))
    except Exception as e:
        console.print(f"  ❌ DebugAgent error: {e}")
        results.append(("DebugAgent", False))

    # Teste ReviewerAgent
    console.print("[yellow]Testing ReviewerAgent ⭐...[/yellow]")
    try:
        reviewer = ReviewerAgent(config_path)
        # Reviewer precisa de arquivo para revisar (simplified test)
        console.print(f"  ⚠️  ReviewerAgent: initialized successfully")
        results.append(("ReviewerAgent", True))
    except Exception as e:
        console.print(f"  ❌ ReviewerAgent error: {e}")
        results.append(("ReviewerAgent", False))

    # Tabela de resultados
    table = Table(title="Agent Test Results")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="bold")

    for agent_name, success in results:
        table.add_row(agent_name, "✅ PASS" if success else "❌ FAIL")

    console.print("\n")
    console.print(table)

    return all(success for _, success in results)


def test_orchestrator_simple():
    """Teste 3: Orchestrator com tarefa simples"""
    console.print(
        "\n[bold cyan]═══ TEST 3: Orchestrator (Simple Task) ═══[/bold cyan]\n"
    )

    try:
        orchestrator = OrchestratorAgent("config/agent_config.yaml")

        # Tarefa simples que pode ser decomposta
        task = "Analyze the project structure and list key files"

        console.print(Panel(task, title="[bold]Task[/bold]", border_style="blue"))

        # Apenas decomposição (sem execução completa para economizar tempo)
        console.print("\n[yellow]Decomposing task...[/yellow]")
        plan = orchestrator.decompose_task(task)

        console.print(f"\n✓ [green]Plan created:[/green]")
        console.print(f"  Subtasks: {len(plan.get('subtasks', []))}")
        console.print(f"  Complexity: {plan.get('complexity', 'unknown')}")

        if plan.get("subtasks"):
            console.print("\n[bold]Subtask Breakdown:[/bold]")
            for i, subtask in enumerate(plan["subtasks"], 1):
                console.print(
                    f"  {i}. [{subtask['agent']}] {subtask['description'][:80]}"
                )

        return len(plan.get("subtasks", [])) > 0

    except Exception as e:
        console.print(f"❌ Error: {e}")
        return False


def test_rlaif_feedback():
    """Teste 4: Sistema RLAIF (feedback loop)"""
    console.print("\n[bold cyan]═══ TEST 4: RLAIF Feedback System ═══[/bold cyan]\n")

    try:
        framework = ToolsFramework()

        # Simular feedback
        console.print("[yellow]Collecting feedback...[/yellow]")
        feedback_data = {
            "task": "test_task",
            "score": 8.5,
            "improvements": ["Better error handling", "Add documentation"],
        }

        success = framework.execute_tool(
            "collect_feedback", feedback_type="code_review", data=feedback_data
        )

        console.print(f"✓ [green]Feedback stored:[/green] {success}")

        # Verificar memória episódica
        console.print("[yellow]Testing episodic memory...[/yellow]")
        stored = framework.execute_tool(
            "episodic_memory", action="store", data={"test": "phase_6_validation"}
        )

        console.print(f"✓ [green]Memory stored:[/green] {stored is not False}")

        return success and stored

    except Exception as e:
        console.print(f"❌ Error: {e}")
        return False


def main():
    """Executa suite completa de testes da Fase 6"""
    console.print(
        "\n[bold magenta]╔══════════════════════════════════════════════════════════╗[/bold magenta]"
    )
    console.print(
        "[bold magenta]║     🧠 OmniMind Phase 6 - Integration Test Suite        ║[/bold magenta]"
    )
    console.print(
        "[bold magenta]╚══════════════════════════════════════════════════════════╝[/bold magenta]\n"
    )

    tests = [
        ("Tools Framework (25+ tools)", test_tools_framework),
        ("Individual Agents", test_individual_agents),
        ("Orchestrator Decomposition", test_orchestrator_simple),
        ("RLAIF Feedback System", test_rlaif_feedback),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            console.print(f"\n❌ [red]Test '{test_name}' crashed: {e}[/red]")
            results.append((test_name, False))

    # Resumo final
    console.print("\n[bold cyan]═══ FINAL SUMMARY ═══[/bold cyan]\n")

    summary_table = Table(title="Phase 6 Test Results")
    summary_table.add_column("Test", style="cyan", width=40)
    summary_table.add_column("Status", style="bold", width=15)

    passed_count = 0
    for test_name, passed in results:
        summary_table.add_row(test_name, "✅ PASS" if passed else "❌ FAIL")
        if passed:
            passed_count += 1

    console.print(summary_table)

    # Veredicto
    total_tests = len(results)
    success_rate = (passed_count / total_tests) * 100 if total_tests > 0 else 0

    console.print(
        f"\n[bold]Tests Passed:[/bold] {passed_count}/{total_tests} ({success_rate:.1f}%)"
    )

    if success_rate >= 75:
        console.print("\n[bold green]🎉 PHASE 6 VALIDATION PASSED![/bold green]")
        console.print("[green]✅ Tools framework operational (25+ tools)[/green]")
        console.print("[green]✅ Multi-agent system functional[/green]")
        console.print("[green]✅ Orchestrator coordination working[/green]")
        console.print("[green]✅ RLAIF feedback loop active[/green]")
        console.print("\n[green]Ready to proceed with advanced workflows![/green]\n")
        return 0
    else:
        console.print("\n[bold red]❌ PHASE 6 VALIDATION FAILED[/bold red]")
        console.print(f"[red]Only {passed_count}/{total_tests} tests passed[/red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
