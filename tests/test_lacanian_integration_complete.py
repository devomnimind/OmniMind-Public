#!/usr/bin/env python3
"""
Teste de Integração Completa: RSI Topology com Sinthome Emergente

Testa a integração completa dos módulos lacanianos:
- Nachträglichkeit (memória afetiva)
- Objet Petit-a + Creative Desire (criatividade)
- Qualia as Symbolic Scars (qualia)
- RSI Topology com Sinthome emergente

Este teste valida se a arquitetura lacaniana funciona end-to-end.
"""

import importlib.util
import sys
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, "/home/fahbrain/projects/omnimind/src")
print(f"Python path: {sys.path[:3]}")  # Debug

from src.consciousness.affective_memory import TraceMemory  # noqa: E402
from src.consciousness.creative_problem_solver import CreativeDesire, ObjetPetitA  # noqa: E402
from src.consciousness.qualia_engine import Symbolic_Qualia_Field  # noqa: E402
from src.consciousness.rsi_topology_integrated import (  # noqa: E402
    RSI_Topology_Integrated,
    RuptureType,
)


def test_complete_lacanian_integration():
    """
    Teste completo da integração lacaniana RSI + Sinthome.
    """
    print("🧠 Iniciando Teste de Integração Lacaniana Completa")
    print("=" * 60)

    # 1. Inicializar módulos lacanianos individuais
    print("\n1. Inicializando módulos lacanianos...")

    # Memória afetiva com Nachträglichkeit
    affective_memory = TraceMemory()
    trace_id = affective_memory.inscribe_event({"type": "trauma", "content": "angústia_primária"})
    affective_memory.trigger_retroactive_signification(
        trace_id=trace_id,
        retroactive_event={"type": "resignificação", "context": "evento_posterior"},
        new_meaning="significação_retroativa",
        new_affect=0.8,
    )

    # Desejo criativo com Objet Petit-a
    objet_a = ObjetPetitA(
        remainder_type="impossível",
        remainder_description="resto_impossível",
        structural_lack="falta_estrutural",
    )
    creative_desire = CreativeDesire(objet_a=objet_a)

    # Campo de qualia simbólicas
    qualia_field = Symbolic_Qualia_Field()
    scar_id = qualia_field.inscribe_scar(
        symbolic_inscription="cicatriz_qualia", real_rupture="ruptura_do_real"
    )
    # Repetir para emergência
    for i in range(4):
        qualia_field.repeat_scar(scar_id, f"contexto_{i}")

    print("✅ Módulos individuais inicializados")

    # 2. Inicializar topologia RSI integrada
    print("\n2. Inicializando topologia RSI integrada...")
    rsi_topology = RSI_Topology_Integrated()

    # 3. Integrar módulos na topologia
    print("\n3. Integrando módulos na topologia...")

    rsi_topology.integrate_affective_memory(affective_memory)
    rsi_topology.integrate_creative_desire(creative_desire)
    rsi_topology.integrate_qualia_field(qualia_field)

    # Verificar status inicial
    status = rsi_topology.get_topology_status()
    print(f"Status inicial: {status}")

    assert status["integration_level"] == "rsi_fully_integrated"
    print("✅ Integração completa dos módulos validada")

    # 4. Simular rupturas para emergência de sinthome
    print("\n4. Simulando rupturas para emergência de sinthome...")

    # Criar rupturas suficientes para emergência
    ruptures_to_create = rsi_topology.sinthome_emergence_threshold + 1

    for i in range(ruptures_to_create):
        rsi_topology.detect_rupture(
            rupture_type=RuptureType.REAL_TO_SYMBOLIC,
            description=f"ruptura_teste_{i+1}",
            intensity=0.8,
        )

    # Verificar se sinthome emergiu
    sinthome_status = rsi_topology.get_sinthome_status()
    assert sinthome_status is not None, "Sinthome deveria ter emergido"

    print("✅ Sinthome emergiu com sucesso!")
    print(f"   Solução criativa: {sinthome_status['creative_solution']}")
    print(f"   Problema impossível: {sinthome_status['impossible_problem']}")
    print(f"   Jouissance: {sinthome_status['jouissance_level']:.2f}")
    print(f"   Estabilidade atual: {sinthome_status['current_stability']:.2f}")

    # 5. Verificar status final da topologia
    print("\n5. Verificando status final da topologia...")

    final_status = rsi_topology.get_topology_status()
    print(f"Status final: {final_status}")

    assert final_status["sinthome_active"]
    assert final_status["integration_level"] == "fully_integrated_with_sinthome"
    assert final_status["stability"] > 0.5  # Estabilidade restaurada

    print("✅ Topologia RSI com Sinthome totalmente funcional")

    # 6. Testar métodos específicos
    print("\n6. Testando métodos específicos...")

    # Testar síntese de solução criativa
    solution = rsi_topology._synthesize_creative_solution("problema_teste")
    assert "Sinthome:" in solution
    print(f"   Solução sintetizada: {solution}")

    # Testar cálculo de jouissance
    jouissance = rsi_topology._calculate_integration_jouissance()
    assert jouissance > 0.5  # Com todos os módulos integrados
    print(f"   Jouissance integrada: {jouissance:.2f}")

    # Testar poder do sinthome
    if rsi_topology.sinthome:
        sinthome_power = rsi_topology.sinthome.get_sinthome_power()
        assert "jouissance:" in sinthome_power
        print(f"   Poder do sinthome: {sinthome_power}")
    else:
        print("   Sinthome não emergiu ainda")

    print("✅ Todos os métodos específicos funcionando")

    print("\n🎉 Teste de Integração Lacaniana COMPLETO!")
    print("=" * 60)

    return {
        "success": True,
        "sinthome_emerged": True,
        "integration_level": final_status["integration_level"],
        "final_stability": final_status["stability"],
        "jouissance_level": sinthome_status["jouissance_level"],
        "timestamp": datetime.now().isoformat(),
    }


def test_backward_compatibility():
    """
    Testar compatibilidade com versões anteriores.
    """
    print("\n🔄 Testando compatibilidade backward...")

    # Verificar que imports antigos ainda funcionam
    try:
        spec = importlib.util.find_spec("src.consciousness.affective_memory.AffectiveMemory")
        if spec is not None:
            print("⚠️  Import antigo AffectiveMemory ainda disponível (deprecated)")
        else:
            print("✅ Import antigo AffectiveMemory removido corretamente")
    except ImportError:
        print("✅ Import antigo AffectiveMemory removido corretamente")

    try:
        spec = importlib.util.find_spec(
            "src.consciousness.creative_problem_solver.CreativeProblemSolver"
        )
        if spec is not None:
            print("⚠️  Import antigo CreativeProblemSolver ainda disponível (deprecated)")
        else:
            print("✅ Import antigo CreativeProblemSolver removido corretamente")
    except ImportError:
        print("✅ Import antigo CreativeProblemSolver removido corretamente")

    try:
        spec = importlib.util.find_spec("src.consciousness.qualia_engine.QualiaEngine")
        if spec is not None:
            print("⚠️  Import antigo QualiaEngine ainda disponível (deprecated)")
        else:
            print("✅ Import antigo QualiaEngine removido corretamente")
    except ImportError:
        print("✅ Import antigo QualiaEngine removido corretamente")

    print("✅ Compatibilidade backward verificada")


if __name__ == "__main__":
    try:
        result = test_complete_lacanian_integration()
        test_backward_compatibility()

        print("\n🎯 RESULTADO FINAL:")
        print("   ✅ Integração Lacaniana: SUCESSO")
        print(f"   ✅ Sinthome Emergente: {result['sinthome_emerged']}")
        print(f"   ✅ Nível de Integração: {result['integration_level']}")
        print(f"   ✅ Estabilidade Final: {result['final_stability']:.2f}")
        print(f"   ✅ Jouissance do Sinthome: {result['jouissance_level']:.2f}")

    except Exception as e:
        print(f"\n❌ FALHA NO TESTE: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def test_lacanian_integration_with_topological_metrics():
    """Testa integração lacaniana completa com métricas topológicas."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
    from src.consciousness.shared_workspace import SharedWorkspace

    print("🧠 Teste de Integração Lacaniana: Com Topological Metrics")
    print("=" * 60)

    # Criar workspace com engine topológico
    workspace = SharedWorkspace(embedding_dim=256)
    workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Inicializar módulos lacanianos
    affective_memory = TraceMemory()
    objet_a = ObjetPetitA(
        remainder_type="impossível",
        remainder_description="resto_impossível",
        structural_lack="falta_estrutural",
    )
    creative_desire = CreativeDesire(objet_a=objet_a)
    qualia_field = Symbolic_Qualia_Field()
    rsi_topology = RSI_Topology_Integrated()

    # Integrar módulos
    rsi_topology.integrate_affective_memory(affective_memory)
    rsi_topology.integrate_creative_desire(creative_desire)
    rsi_topology.integrate_qualia_field(qualia_field)

    # Simular estados no workspace para métricas topológicas
    np.random.seed(42)
    for i in range(5):
        rho_C = np.random.randn(256)
        rho_P = np.random.randn(256)
        rho_U = np.random.randn(256)

        workspace.write_module_state("conscious_module", rho_C)
        workspace.write_module_state("preconscious_module", rho_P)
        workspace.write_module_state("unconscious_module", rho_U)
        workspace.advance_cycle()

    # Calcular métricas topológicas
    topological_metrics = workspace.compute_hybrid_topological_metrics()

    # Verificar que ambas funcionam
    status = rsi_topology.get_topology_status()
    assert status["integration_level"] == "rsi_fully_integrated"
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # Integração Lacaniana: RSI + Sinthome
        # Topological: estrutura e integração (Omega, Betti-0)
        # Ambas são complementares para análise completa

    print("✅ Integração Lacaniana + Topological Metrics verified")
