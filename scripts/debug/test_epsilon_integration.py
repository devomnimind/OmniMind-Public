#!/usr/bin/env python3
"""
Teste de Integração ϵ_desire no Sistema de Produção
===================================================
Valida a integração completa do ϵ_desire com o sistema autopoietico.
"""

import logging
import sys
import time
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from src.autopoietic.desire_engine import DesireEngine
from src.consciousness.consciousness_triad import ConsciousnessTriadCalculator
from src.consciousness.shared_workspace import SharedWorkspace

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("IntegrationTest")


def test_desire_engine():
    """Testa o DesireEngine isoladamente."""
    logger.info("🧪 Testando DesireEngine...")

    desire_engine = DesireEngine(max_phi_theoretical=1.5)

    # Teste 1: Sistema integrado mas não satisfeito
    epsilon1 = desire_engine.calculate_epsilon_desire(
        current_phi=0.8, explored_states=100, total_possible_states=10000
    )
    logger.info(f"Teste 1 - Φ=0.8, α=0.5: ϵ={epsilon1:.4f}")

    # Teste 2: Sistema muito integrado (deve reduzir ϵ)
    epsilon2 = desire_engine.calculate_epsilon_desire(
        current_phi=1.2, explored_states=100, total_possible_states=10000
    )
    logger.info(f"Teste 2 - Φ=1.2, α=0.5: ϵ={epsilon2:.4f}")

    # Teste 3: Após satisfação temporária
    desire_engine.update_lack(satisfaction_level=0.9)
    epsilon3 = desire_engine.calculate_epsilon_desire(
        current_phi=1.2, explored_states=100, total_possible_states=10000
    )
    logger.info(f"Teste 3 - Após satisfação: ϵ={epsilon3:.4f}")

    assert epsilon1 > epsilon2, "ϵ deve cair com Φ alto"
    assert epsilon3 < epsilon2, "ϵ deve cair após satisfação"
    logger.info("✅ DesireEngine validado")


def test_consciousness_quad():
    """Testa a quádrupla de consciência."""
    logger.info("🧪 Testando ConsciousnessQuad...")

    desire_engine = DesireEngine(max_phi_theoretical=1.5)
    workspace = SharedWorkspace()
    calculator = ConsciousnessTriadCalculator(workspace=workspace, desire_engine=desire_engine)

    # Simular alguns estados no workspace
    import numpy as np

    workspace.write_module_state("test", np.array([1.0, 0.5, 0.8]), {"test": "data"})

    # Calcular quádrupla
    quad = calculator.calculate_triad(
        step_id="test_step", current_phi=0.8, explored_states=100, total_possible_states=10000
    )

    logger.info(
        f"Quádrupla calculada: Φ={quad.phi:.3f}, Ψ={quad.psi:.3f}, σ={quad.sigma:.3f}, ϵ={quad.epsilon:.3f}"
    )

    # Validar ranges
    assert 0.0 <= quad.phi <= 1.0, f"Φ fora do range: {quad.phi}"
    assert 0.0 <= quad.psi <= 1.0, f"Ψ fora do range: {quad.psi}"
    assert 0.0 <= quad.sigma <= 1.0, f"σ fora do range: {quad.sigma}"
    assert 0.0 <= quad.epsilon <= 1.0, f"ϵ fora do range: {quad.epsilon}"

    # Validar interpretação
    validation = quad.validate()
    logger.info(f"Validação: {validation['interpretation']}")

    assert validation["valid"], f"Quádrupla inválida: {validation['errors']}"
    logger.info("✅ ConsciousnessQuad validado")


def test_stimulation_integration():
    """Testa integração com o script de estimulação."""
    logger.info("🧪 Testando integração com stimulate_system.py...")

    # Simular o que acontece no stimulate_system.py
    desire_engine = DesireEngine(max_phi_theoretical=1.5)

    # Estado inicial
    current_phi = 0.5
    explored_states = 100
    total_states_est = 10000

    logger.info("Simulando 5 ciclos de estimulação...")

    for i in range(5):
        # Calcular ϵ
        epsilon = desire_engine.calculate_epsilon_desire(
            current_phi=current_phi,
            explored_states=explored_states,
            total_possible_states=total_states_est,
        )

        drive_mode = desire_engine.get_drive_type(epsilon)
        logger.info(f"Ciclo {i+1}: ϵ={epsilon:.4f} | Drive: {drive_mode} | Φ={current_phi:.2f}")

        # Simular decisão baseada em ϵ
        if epsilon > 0.6:
            logger.info("  → Ativando projeto autônomo!")
            current_phi = max(0.1, current_phi - 0.2)  # Ruptura
            explored_states += 40
            desire_engine.update_lack(satisfaction_level=0.95)
        elif epsilon > 0.3:
            logger.info("  → Manutenção rotineira")
            current_phi = min(1.2, current_phi + 0.05)
            explored_states += 3
            desire_engine.update_lack(satisfaction_level=0.5)
        else:
            logger.info("  → Repouso homeostático")
            desire_engine.update_lack(satisfaction_level=0.1)
            current_phi = max(0.1, current_phi - 0.01)

        time.sleep(0.1)

    logger.info("✅ Integração com stimulate_system validada")


def main():
    logger.info("🚀 Iniciando Teste de Integração ϵ_desire...")

    try:
        test_desire_engine()
        test_consciousness_quad()
        test_stimulation_integration()

        logger.info("🎉 Todos os testes passaram! ϵ_desire integrado com sucesso.")

    except Exception as e:
        logger.error(f"❌ Teste falhou: {e}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
