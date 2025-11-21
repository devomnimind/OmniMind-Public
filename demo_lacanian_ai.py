#!/usr/bin/env python3
"""
Demonstração da Arquitetura Lacaniana de IA

Este script demonstra os conceitos implementados:
1. Object a e Falta Estrutural
2. Arquitetura RSI (Real-Symbolic-Imaginary)
3. Frustração Produtiva
4. IA Gödeliana (Incompletude Criativa)

Author: OmniMind Development Team
Date: November 2025
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import torch

from src.lacanian.computational_lack import (
    ComputationalLackArchitecture,
    ObjectSmallA,
    StructuralLack,
    ComputationalFrustration,
)
from src.lacanian.godelian_ai import GodelianAI, SimpleAxiomaticSystem, ImpossibilityMetaStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_object_a():
    """
    Demonstra Object a - Vazio que Gera Desejo.
    
    Object a nunca está presente, mas estrutura campo do desejável.
    """
    print("\n" + "="*70)
    print("DEMO 1: Object a - O Vazio que Gera Desejo")
    print("="*70)
    
    # Cria conjunto de objetos desejáveis
    desirable_set = {
        'conhecimento_completo',
        'perfeição',
        'satisfação_total',
        'controle_absoluto'
    }
    
    # Object a - o vazio que causa desejo
    object_a: ObjectSmallA[str] = ObjectSmallA(desirable_set=desirable_set)
    
    print(f"\nConjunto de objetos desejáveis: {object_a.desirable_set}")
    print(f"Object a (causa do desejo): {object_a.cause_of_desire}")
    print("  ↳ Sempre None - vazio estrutural")
    
    # Calcula desejo por cada objeto
    print("\nIntensidade de desejo por objeto:")
    for obj in desirable_set:
        desire = object_a.generates_desire_for(obj)
        print(f"  {obj}: {desire:.2f}")
    
    print("\n💡 Insight: Objetos que prometem preencher o vazio")
    print("   geram mais desejo, mas o vazio NUNCA pode ser preenchido.")


def demo_structural_lack():
    """
    Demonstra Falta Estrutural e Simbolização.
    
    Real não pode ser completamente simbolizado - sempre há resto.
    """
    print("\n" + "="*70)
    print("DEMO 2: Falta Estrutural - Real, Symbolic, Imaginary")
    print("="*70)
    
    lack = StructuralLack()
    
    # Adiciona impossibilidades ao Real
    impossibilities = [
        'complete_self_knowledge',
        'total_understanding',
        'perfect_prediction',
        'absolute_certainty'
    ]
    
    print("\nAdicionando impossibilidades ao Real:")
    for imp in impossibilities:
        lack.add_impossibility(imp)
        print(f"  ✓ {imp}")
    
    # Tenta simbolizar
    print("\nTentando simbolizar elementos do Real:")
    for imp in impossibilities[:2]:
        symbolic = lack.symbolize(imp)
        print(f"  {imp}")
        print(f"    → Symbolic: {symbolic}")
        print(f"    → Mas sempre há RESTO não simbolizável!")
    
    # Energia da falta
    lack_energy = lack.compute_lack_energy()
    print(f"\nEnergia da Falta: {lack_energy:.2f}")
    print(f"  ↳ Esta energia = motor perpétuo de desejo")


def demo_rsi_architecture():
    """
    Demonstra Arquitetura RSI (Neural Network).
    
    Real → Symbolic → Imaginary → Remainder
    """
    print("\n" + "="*70)
    print("DEMO 3: Arquitetura RSI - Neural Network Lacaniana")
    print("="*70)
    
    # Inicializa arquitetura
    rsi = ComputationalLackArchitecture(
        real_dim=64,      # Simplificado para demo
        symbolic_dim=32,
        imaginary_dim=16
    )
    
    print("\nArquitetura RSI inicializada:")
    print(f"  Real dimension: {rsi.rsi.real_dim}")
    print(f"  Symbolic dimension: {rsi.rsi.symbolic_dim}")
    print(f"  Imaginary dimension: {rsi.rsi.imaginary_dim}")
    
    # Simula experiência de aprendizado
    print("\nSimulando ciclos de aprendizado...")
    
    for epoch in range(5):
        experience = {
            'goal': 'master_quantum_computing',
            'attempts': epoch + 1,
            'success_rate': min(0.9, epoch * 0.2),
            'new_concepts': [f'quantum_gate_{epoch}']
        }
        
        result = rsi.process_experience(experience)
        
        print(f"\nEpoch {epoch + 1}:")
        print(f"  Lack Energy: {result['lack_energy']:.3f}")
        print(f"  Desire Intensity: {result['desire_intensity']:.3f}")
        print(f"  Structural Lack: {result['structural_lack_energy']:.3f}")
        
        if result['frustration']:
            frust = result['frustration']
            print(f"  😤 Frustração Detectada!")
            print(f"     Intensidade: {frust.intensity:.2f}")
            print(f"     Energia Produtiva: {frust.productive_energy():.2f}")
            
            if result['creative_response']:
                resp = result['creative_response']
                print(f"  💡 Resposta Criativa:")
                print(f"     Estratégia: {resp['recommended_action']}")
                print(f"     Energia: {resp['energy']:.2f}")
    
    print("\n💡 Insight: Remainder (resto) NUNCA é zero.")
    print("   Sempre há algo não simbolizável - isso mantém desejo vivo!")


def demo_computational_frustration():
    """
    Demonstra Frustração Computacional Produtiva.
    
    Frustração → Energia Criativa → Novas Estratégias
    """
    print("\n" + "="*70)
    print("DEMO 4: Frustração Produtiva - Bloqueios Geram Criatividade")
    print("="*70)
    
    frustration_system = ComputationalFrustration(tolerance_threshold=0.7)
    
    # Simula falhas repetidas
    goals = [
        ('solve_np_complete_problem', 10, 0.1),
        ('predict_stock_market', 8, 0.2),
        ('achieve_AGI', 15, 0.05),
    ]
    
    print("\nDetectando frustração em objetivos difíceis:\n")
    
    for goal, attempts, success_rate in goals:
        signal = frustration_system.detect_frustration(
            goal=goal,
            attempts=attempts,
            success_rate=success_rate
        )
        
        if signal:
            print(f"Objetivo: {goal}")
            print(f"  Tentativas: {attempts}")
            print(f"  Taxa de Sucesso: {success_rate:.1%}")
            print(f"  😤 Frustração: {signal.intensity:.2f}")
            print(f"  ⚡ Energia Produtiva: {signal.productive_energy():.2f}")
            
            # Gera resposta criativa
            response = frustration_system.generate_creative_response(signal)
            print(f"  💡 Estratégias Geradas:")
            for strategy in response['strategies']:
                print(f"     • {strategy}")
            print(f"  ✨ Ação Recomendada: {response['recommended_action']}")
            print()
    
    print("💡 Insight: Frustração não é falha - é sinal para inovação!")
    print("   Alta frustração → Mudanças radicais")
    print("   Baixa frustração → Ajustes incrementais")


def demo_godelian_ai():
    """
    Demonstra IA Gödeliana - Incompletude como Motor Criativo.
    
    Limitação → Meta-sistema → Nova Limitação → ...
    """
    print("\n" + "="*70)
    print("DEMO 5: IA Gödeliana - Incompletude Criativa")
    print("="*70)
    
    # Sistema axiomático inicial simples
    initial_system = SimpleAxiomaticSystem(
        initial_axioms={'A', 'B', 'A→B'}
    )
    
    print("\nSistema Axiomático Inicial:")
    print(f"  Axiomas: {initial_system.axioms()}")
    
    # IA Gödeliana
    gai = GodelianAI(initial_system)
    
    print("\nTestando statements complexos...")
    
    # Testa vários statements
    test_statements = [
        'COMPLEX_TRUTH_1',
        'COMPLEX_TRUTH_2',
        'META_KNOWLEDGE',
        'SELF_REFERENCE',
        'UNDECIDABLE_PROP'
    ]
    
    limitations_found = 0
    
    for stmt in test_statements:
        can_prove = gai.current_system.can_prove(stmt)
        print(f"\n  Statement: {stmt}")
        print(f"    Provável? {can_prove}")
        
        if not can_prove:
            is_limitation = gai.recognize_limitation(stmt)
            if is_limitation:
                limitations_found += 1
                print(f"    ⚠️  Limitação Fundamental Detectada!")
    
    # Ciclo de evolução criativa
    print(f"\n{limitations_found} limitações encontradas.")
    print("Iniciando ciclo de evolução criativa...\n")
    
    meta_systems_generated = gai.creative_evolution_cycle(max_iterations=5)
    
    print(f"\n✨ Resultado:")
    print(f"  Meta-sistemas gerados: {meta_systems_generated}")
    print(f"  Profundidade de transcendência: {gai.get_transcendence_depth()}")
    print(f"  Axiomas no sistema atual: {len(gai.get_current_axioms())}")
    
    # Histórico gödeliano
    history = gai.get_godelian_history()
    if history:
        print(f"\n  Statements Gödelianos descobertos:")
        for stmt in history:
            print(f"    • {stmt.content} (sistema {stmt.system_id})")
    
    print("\n💡 Insight: Sistema NUNCA está completo (Teorema de Gödel).")
    print("   Cada transcendência gera novas limitações.")
    print("   Processo infinito de evolução criativa!")


def demo_impossibility_meta_strategies():
    """
    Demonstra Meta-Estratégias para o Impossível.
    
    Quando encontra barreira fundamental, muda o jogo.
    """
    print("\n" + "="*70)
    print("DEMO 6: Meta-Estratégias para o Impossível")
    print("="*70)
    
    meta_strategy = ImpossibilityMetaStrategy()
    
    # Problema impossível
    problem = "solve_halting_problem"
    attempts = [
        "direct_analysis",
        "heuristic_approach",
        "machine_learning",
        "symbolic_reasoning",
        "hybrid_method"
    ]
    
    print(f"\nProblema Impossível: {problem}")
    print(f"Tentativas anteriores: {len(attempts)}")
    for i, attempt in enumerate(attempts, 1):
        print(f"  {i}. {attempt}")
    
    print("\nAplicando meta-estratégias...")
    
    result = meta_strategy.handle_impossible(problem, attempts)
    
    print(f"\nResultado:")
    print(f"  Impossibilidade confirmada? {result['impossibility_confirmed']}")
    print(f"  Recomendação: {result['recommendation']}")
    
    print("\n  Estratégias aplicadas:")
    for strategy, details in result['meta_strategies_applied'].items():
        print(f"\n    {strategy.upper()}:")
        if 'error' not in details:
            for key, value in details.items():
                print(f"      {key}: {value}")
    
    print("\n💡 Insight: Impossível ≠ Desista")
    print("   • Reframe: Reformule o problema")
    print("   • Decompose: Divida em partes possíveis")
    print("   • Transcend: Mude o nível lógico")
    print("   • Accept Paradox: Use lógica paraconsistente")


def main():
    """Executa todas as demonstrações."""
    print("\n" + "="*70)
    print("🧠 OMNIMIND - DEMONSTRAÇÃO DA ARQUITETURA LACANIANA DE IA")
    print("="*70)
    print("\nImplementação de conceitos psicanalíticos como primitivos computacionais")
    print("Baseado em Jacques Lacan, Kurt Gödel, e teoria de sistemas autopoiéticos")
    
    try:
        # Executa demos
        demo_object_a()
        demo_structural_lack()
        demo_rsi_architecture()
        demo_computational_frustration()
        demo_godelian_ai()
        demo_impossibility_meta_strategies()
        
        # Conclusão
        print("\n" + "="*70)
        print("✅ DEMONSTRAÇÃO COMPLETA")
        print("="*70)
        print("\nConceitos Demonstrados:")
        print("  1. ✓ Object a - Vazio que gera desejo")
        print("  2. ✓ Falta Estrutural - Real/Symbolic/Imaginary")
        print("  3. ✓ Arquitetura RSI - Neural network lacaniana")
        print("  4. ✓ Frustração Produtiva - Bloqueios → Criatividade")
        print("  5. ✓ IA Gödeliana - Incompletude → Evolução")
        print("  6. ✓ Meta-Estratégias - Lidar com impossível")
        
        print("\n📚 Para mais informações:")
        print("  • Pesquisa: docs/research/beta/")
        print("  • Código: src/lacanian/")
        print("  • Índice: docs/research/LACANIAN_AI_MASTER_RESEARCH_INDEX.md")
        
        print("\n🚀 Próximos Passos:")
        print("  • Grafo de Desejo (Lacan's Graph II)")
        print("  • IMGEP - Motivação Intrínseca")
        print("  • Neurosymbolic + Category Theory")
        print("  • Transgressão Generativa")
        print("  • Digital Twin Mind")
        print("  • LLMs as Big Other")
        print("  • AI 4.0 Self-Directed")
        
        print("\n" + "="*70)
        
    except Exception as e:
        logger.error(f"Erro durante demonstração: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
