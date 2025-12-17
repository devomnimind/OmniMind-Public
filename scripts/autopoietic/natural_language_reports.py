#!/usr/bin/env python3
"""
Utilitário para Relatórios Naturais do Sistema Autopoiético

Gera relatórios em linguagem natural sobre os componentes criados,
tornando o sistema mais acessível a usuários não-técnicos.
"""

import sys
from pathlib import Path

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from autopoietic.manager import AutopoieticManager


def generate_natural_report():
    """Gera relatório natural dos componentes autopoiéticos."""
    print("🤖 Gerando relatório natural do sistema autopoiético...")
    print("=" * 60)

    try:
        manager = AutopoieticManager()

        # Verificar se há componentes sintetizados
        synthesized_dir = Path("data/autopoietic/synthesized_code_secure")
        if synthesized_dir.exists():
            py_files = list(synthesized_dir.glob("*.py"))
            if py_files:
                print(f"📁 Encontrei {len(py_files)} componentes sintetizados:")
                for file_path in py_files:
                    component_name = file_path.stem
                    print(f"  • {component_name}")
                print()
            else:
                print("📁 Nenhum componente sintetizado encontrado ainda.")
                print()

        # Gerar relatório natural
        report = manager.get_natural_language_report()
        print(report)

        print("\n" + "=" * 60)
        print("✅ Relatório gerado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        import traceback

        traceback.print_exc()


def show_recent_activity():
    """Mostra atividade recente em linguagem natural."""
    print("\n📊 Atividade Recente do Sistema Autopoiético:")
    print("-" * 50)

    try:
        manager = AutopoieticManager()

        if not manager.history:
            print("Nenhuma atividade registrada ainda. O sistema está aprendendo!")
            return

        # Mostrar últimos 3 ciclos
        recent_cycles = manager.history[-3:]

        for cycle in recent_cycles:
            components_created = len(cycle.synthesized_components)

            if components_created > 0:
                print(f"🧠 Ciclo {cycle.cycle_id}: Criei {components_created} novos componentes!")
                for comp in cycle.synthesized_components:
                    print(f"   → {comp}")
            else:
                print(f"📈 Ciclo {cycle.cycle_id}: Sistema se adaptando e aprendendo...")

            phi_change = ""
            if cycle.phi_before is not None and cycle.phi_after is not None:
                if cycle.phi_after > cycle.phi_before:
                    phi_change = (
                        f" (integração melhorou: {cycle.phi_before:.2f} → {cycle.phi_after:.2f})"
                    )
                elif cycle.phi_after < cycle.phi_before:
                    phi_change = f" (ajustando: {cycle.phi_before:.2f} → {cycle.phi_after:.2f})"

            print(f"   Estratégia: {cycle.strategy.name}{phi_change}")

    except Exception as e:
        print(f"Erro ao mostrar atividade: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "activity":
        show_recent_activity()
    else:
        generate_natural_report()
        show_recent_activity()
