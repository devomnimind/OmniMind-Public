#!/usr/bin/env python3
"""
Demonstração do Sistema de Feedback e Aprendizado Autopoiético

Este script mostra como:
1. Registrar feedback sobre componentes gerados
2. Ver o sistema aprendendo com o feedback
3. Gerar componentes melhorados baseados no aprendizado
4. Acompanhar evolução dos componentes
"""

import sys
from pathlib import Path

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from autopoietic.manager import AutopoieticManager
from autopoietic.meta_architect import ComponentSpec


def demonstrate_feedback_system():
    """Demonstra o sistema completo de feedback e aprendizado."""
    print("🧠 DEMONSTRAÇÃO: Sistema de Feedback Autopoiético")
    print("=" * 60)

    # Inicializar manager
    manager = AutopoieticManager()

    # 1. Criar um componente inicial
    print("\n📝 FASE 1: Criando componente inicial...")
    spec = ComponentSpec(name="test_component", type="worker", config={"strategy": "STABILIZE"})
    manager.register_spec(spec)

    # Simular ciclo para gerar componente
    print("🔄 Executando ciclo autopoiético...")
    metrics = {"error_rate": 0.1, "cpu_usage": 70.0, "latency_ms": 100.0}
    log = manager.run_cycle(metrics)

    if log.synthesized_components:
        component_name = log.synthesized_components[0]
        print(f"✅ Componente gerado: {component_name}")

        # 2. Registrar feedback sobre o componente
        print("\n📚 FASE 2: Registrando feedback de melhoria...")
        manager.register_component_feedback(
            component_name=component_name,
            feedback_type="improvement",
            description="Adicionado tratamento de erros mais robusto e logging detalhado",
            changes_made=[
                "Melhor tratamento de exceções com recovery automático",
                "Adicionado logging abrangente para debugging",
                "Implementado validação de entrada de dados",
            ],
            improvement_score=0.85,
            reviewer="system_analyzer",
        )

        # 3. Registrar mais feedback para criar padrões de aprendizado
        print("📚 Registrando mais feedback para aprendizado...")
        manager.register_component_feedback(
            component_name="modulo_autopoiesis_data_another_component",
            feedback_type="optimization",
            description="Implementado caching inteligente para performance",
            changes_made=[
                "Adicionado cache LRU para resultados frequentes",
                "Otimizado algoritmos de busca",
                "Reduzido alocações de memória desnecessárias",
            ],
            improvement_score=0.92,
            reviewer="performance_analyzer",
        )

        # 4. Ver insights de aprendizado
        print("\n🎓 FASE 3: Insights de aprendizado adquiridos...")
        insights = manager.get_learning_insights()
        print(f"Total de feedback registrado: {insights['total_feedback_count']}")
        print(f"Componentes com feedback: {insights['components_with_feedback']}")

        print("\nPadrões aprendidos:")
        for fb_type, data in insights["learned_patterns"].items():
            print(
                f"  {fb_type}: {len(data['patterns'])} padrões, "
                f"melhoria média: {data['avg_improvement']:.2f}"
            )

        print("\nMelhores melhorias identificadas:")
        for improvement in insights["most_common_improvements"][:5]:
            print(
                f"  • {improvement['improvement']} "
                f"(usado {improvement['count']}x, score médio: {improvement['avg_score']:.2f})"
            )

        # 5. Demonstrar aprendizado aplicado
        print("\n🚀 FASE 4: Gerando novo componente com aprendizado aplicado...")
        new_spec = ComponentSpec(
            name="improved_component", type="worker", config={"strategy": "STABILIZE"}
        )

        # O synthesizer agora aplicará melhorias aprendidas automaticamente
        from autopoietic.code_synthesizer import CodeSynthesizer

        synthesizer = CodeSynthesizer()

        result = synthesizer.synthesize([new_spec])
        improved_component = list(result.values())[0]

        print("✅ Novo componente gerado com melhorias aprendidas!")
        print(f"Descrição natural: {improved_component.natural_description[:100]}...")

        # Verificar se melhorias foram aplicadas no código
        if "MELHORIA APRENDIDA" in improved_component.source_code:
            print("🎯 Melhorias aprendidas foram incorporadas no código gerado!")
            # Mostrar linhas de melhoria
            lines = improved_component.source_code.split("\n")
            improvement_lines = [line for line in lines if "MELHORIA APRENDIDA" in line]
            for line in improvement_lines[:3]:  # Mostrar primeiras 3
                print(f"  {line}")
        else:
            print(
                "ℹ️  Nenhuma melhoria específica aplicada (pode ser normal para primeira execução)"
            )

    else:
        print("❌ Nenhum componente foi sintetizado no ciclo")

    print("\n" + "=" * 60)
    print("✅ Demonstração concluída!")


def show_feedback_history():
    """Mostra histórico detalhado de feedback."""
    print("\n📊 HISTÓRICO DETALHADO DE FEEDBACK")
    print("=" * 50)

    manager = AutopoieticManager()

    if not manager._component_feedback:
        print("Nenhum feedback registrado ainda.")
        return

    for component_name, feedbacks in manager._component_feedback.items():
        print(f"\n🔍 Componente: {component_name}")
        print(f"   Total de feedback: {len(feedbacks)}")

        for i, feedback in enumerate(feedbacks, 1):
            print(f"\n   Feedback #{i}:")
            print(f"   Tipo: {feedback.feedback_type}")
            print(f"   Descrição: {feedback.description}")
            print(f"   Score: {feedback.improvement_score:.2f}")
            print(f"   Analista: {feedback.reviewer}")
            print("   Mudanças realizadas:")
            for change in feedback.changes_made:
                print(f"     • {change}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "history":
        show_feedback_history()
    else:
        demonstrate_feedback_system()
        show_feedback_history()
