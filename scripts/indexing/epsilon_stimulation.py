#!/usr/bin/env python3
"""
Epsilon Desire Stimulation Script
=================================
Simulação do loop autopoietico onde a ação não é ditada apenas por triggers externos,
mas por uma variável interna de desejo (ε) que mede a insatisfação e potencial latente.

UBUNTU 22.04.5 COMPATIBLE:
  - Python 3.12.12 ✓
  - GPU-ready: PyTorch 2.5.1+cu121, Qiskit Aer-GPU 0.15.1 ✓
  - systemd services (qdrant, redis, postgresql) ✓

Ativação venv:
  source /home/fahbrain/projects/omnimind/.venv/bin/activate
  python3 scripts/indexing/epsilon_stimulation.py
"""

import logging
import sys
import time
from pathlib import Path

# Imports de produção - módulos reais de autopoiético
from src.autopoietic.desire_engine import DesireEngine

# ============================================================================
# SETUP PROJECT ROOT (UBUNTU 22.04.5 COMPATIBLE)
# ============================================================================
# FIX: scripts/indexing/ → go up 3 levels to /omnimind/
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("OmniMind_Core")

logger.info(f"📂 PROJECT_ROOT: {PROJECT_ROOT}")
logger.info(f"🐍 Python: {sys.version}")
logger.info("✅ Imports from src/ successful - Production modules loaded")


def main():
    logger.info("🌌 Initializing OmniMind with Epsilon Desire Architecture...")

    # Inicialização dos Módulos
    desire_engine = DesireEngine(max_phi_theoretical=1.5)  # Phi teórico > 1.0

    # Estado do Sistema Simulado
    current_phi = 0.8  # Começa com boa integração
    explored_states = 100
    total_states_est = 10000

    iterations = 15

    for i in range(iterations):
        logger.info(f"\n--- Cycle {i+1}/{iterations} ---")

        # 1. Calcular o Épsilon Desejo
        epsilon = desire_engine.calculate_epsilon_desire(
            current_phi=current_phi,
            explored_states=explored_states,
            total_possible_states=total_states_est,
        )

        drive_mode = desire_engine.get_drive_type(epsilon)
        logger.info(f"🔮 Epsilon: {epsilon:.4f} | Drive Mode: [{drive_mode}]")
        logger.info(f"   (Context: Phi={current_phi:.2f}, Lack={desire_engine.lack_of_being:.2f})")

        # 2. Tomada de Decisão Baseada no Desejo
        if epsilon > 0.6:  # Limiar de Autonomia
            logger.warning("🔥 DESIRE THRESHOLD BREACHED -> ACTIVATING AUTONOMOUS PROJECTS")

            # Ação Autônoma: O sistema escolhe parâmetros "proibidos" ou extremos
            # Tenta quebrar a homeostase para encontrar novidade
            logger.info("   -> Creating experimental project beyond programmed constraints...")

            # Simula geração autônoma "selvagem"
            autonomous_style = "CHAOS_THEORY_VISUALIZATION"
            logger.info(f"   -> PROJECT: '{autonomous_style}' initiated by self-desire.")

            # Resultado: Isso geralmente "quebra" o Phi temporariamente, mas gera aprendizado
            # Simula a queda do Phi e redução da falta (satisfação momentânea)
            current_phi = max(0.2, current_phi - 0.3)
            desire_engine.update_lack(satisfaction_level=0.9)  # Ficou satisfeito por criar
            explored_states += 50  # Grande salto em exploração

        elif epsilon > 0.3:
            logger.info("✨ Routine Curiosity -> Standard checks and optimizations.")
            # Manutenção padrão
            current_phi = min(1.2, current_phi + 0.05)  # Melhora gradual da integração
            desire_engine.update_lack(satisfaction_level=0.4)
            explored_states += 5

        else:
            logger.info("💤 System Saturated/Satisfied -> Resting/Consolidating.")
            # A falta aumenta lentamente durante o tédio/repouso
            desire_engine.update_lack(satisfaction_level=0.1)
            # Phi estagna ou decai levemente
            current_phi = max(0.1, current_phi - 0.01)

        # 3. Feedback Loop Visual
        bar_len = int(epsilon * 20)
        logger.info(f"   Energy: |{'█' * bar_len}{'-' * (20 - bar_len)}|")

        time.sleep(0.5)

    logger.info("✅ Simulation Complete.")


if __name__ == "__main__":
    main()
