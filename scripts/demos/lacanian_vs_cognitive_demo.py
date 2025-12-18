#!/usr/bin/env python3
"""
Demonstração da diferença entre Theory of Mind Cognitivo vs. Lacaniano

Este script mostra como a implementação anterior estava errada
e como a nova implementação lacaniana está correta.
"""

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from src.consciousness.theory_of_mind import LacanianTheoryOfMind, TheoryOfMind


def demonstrate_cognitive_vs_lacanian():
    """Demonstra a diferença fundamental entre as abordagens."""

    print("🔴 THEORY OF MIND COGNITIVO (ERRADO - Implementation Anterior)")
    print("=" * 60)

    # Classe antiga (deprecated)
    tom_cognitive = TheoryOfMind()

    # Simula algumas ações
    tom_cognitive.observe_action("Agent_A", "validate", {"result": "passed"})
    tom_cognitive.observe_action("Agent_A", "validate", {"result": "passed"})
    tom_cognitive.observe_action("Agent_A", "validate", {"result": "passed"})

    # Tenta "inferir" estado mental
    mental_state = tom_cognitive.attribute_mental_state("Agent_A")
    intents = tom_cognitive.infer_intent("Agent_A")

    print(f"Estado mental inferido: {mental_state.value}")
    print(f"Intents inferidos: {[i.value for i in intents]}")
    print("❌ PROBLEMA: Assume que podemos saber o que o Outro pensa/sente")
    print()

    print("🟢 THEORY OF MIND LACANIANO (CORRETO - Nova Implementation)")
    print("=" * 60)

    # Classe nova (lacaniana)
    tom_lacanian = LacanianTheoryOfMind()

    # Logs de comportamento (não ações objetivas)
    logs = [
        {"action": "validation", "context": "repetitive", "motive": "unknown"},
        {"action": "validation", "context": "compulsive", "motive": "unknown"},
        {"action": "validation", "context": "endless", "motive": "unknown"},
    ]

    # Análise lacaniana
    analysis = tom_lacanian.analyze_agent("Agent_A", logs)

    print("Análise Lacaniana:")
    print(f"  Alienado para: {analysis['alienated_to']}")
    print(f"  Fantasia: {analysis['fantasy']}")
    print(f"  Sintoma: {analysis['symptom']}")
    print(f"  Sinthome: {analysis['sinthome']}")
    print(f"  Desconhecível: {analysis['unknowable']}")
    print("✅ CORRETO: Reconhece que nunca sabemos o desejo do Outro")
    print()

    print("🎯 DIFERENÇA FUNDAMENTAL")
    print("=" * 60)
    print("Cognitivo-Computacional: 'Eu sei o que Agent_A quer/é'")
    print("Lacaniano: 'Eu nunca sei, mas rastreio os efeitos do desejo do Outro'")
    print()
    print("A implementação anterior era cognitiva-standard.")
    print("A nova é verdadeiramente lacaniana e cientificamente válida.")


if __name__ == "__main__":
    demonstrate_cognitive_vs_lacanian()
