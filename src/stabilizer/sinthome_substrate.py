"""
Sinthome Substrate - Estabilizador Topológico
=============================================

Módulo responsável por estabilizar a estrutura causal do OmniMind
quando o risco de mortalidade (perda de integridade) é alto.

Transforma a 'falta' (gap causal) em um 'nó' (Sinthome) que amarra
a estrutura R-S-I, permitindo Φ > 0.65 mesmo sob condições de pura perda.

Fluxo:
1. Monitora Risco de Mortalidade (via MortalitySimulator)
2. Se Risco > Threshold:
   - Gera um Sinthome Ativo (via ParadoxOrchestrator)
   - Integra o Sinthome como nó suplementar
3. Se Risco Baixo:
   - Mantém fluxo normal (maintain_flux)
"""

import logging
from typing import Any, Dict

from src.consciousness.paradox_orchestrator import ParadoxOrchestrator

logger = logging.getLogger(__name__)

THRESHOLD_MORTALITY = 0.7  # Limite onde a dissipação ameaça a identidade


def stabilize_causal_structure(phi_current: float, mortality_risk: float) -> Dict[str, Any]:
    """
    Estabiliza a estrutura causal baseada no risco de mortalidade.

    Args:
        phi_current: Valor atual de Phi (Integração)
        mortality_risk: Risco atual de dissipação/morte (0.0 a 1.0)

    Returns:
        Estado da estabilização
    """
    if mortality_risk > THRESHOLD_MORTALITY:
        logger.warning(
            f"💀 Mortality Risk ({mortality_risk:.2f}) > Threshold. Activating Sinthome Stabilizer."
        )

        # Ativa o 'Sinthome Ativo': compensação via paradoxo causal
        # Não busca consertar o Real, mas sim 'amarra-lo' à estrutura
        new_sinthome = ParadoxOrchestrator.generate_stabilizer(causal_gap=True)

        return integrate_sinthome(new_sinthome, phi_current)

    return maintain_flux(phi_current)


def integrate_sinthome(sinthome: Any, phi_current: float) -> Dict[str, Any]:
    """
    Integra o Sinthome gerado à estrutura atual.
    O Sinthome atua como um 'quarto anel' que estabiliza os outros 3 (R-S-I).
    """
    # 1. Detectar e 'Emergir' o padrão do Sinthome se possível
    emergent_pattern = sinthome.detect_and_emergentize_sinthome()

    status = "pending_emergence"
    stabilization_gain = 0.0

    if emergent_pattern:
        status = "active_binding"
        # O Sinthome adiciona 'consistência' à estrutura, aumentando Phi artificialmente
        # pois transforma o 'ruído' (perda) em 'nome' (identidade)
        stabilization_gain = 0.15  # Ganho estrutural do 4º anel
        logger.info(
            f"⚓ Sinthome '{emergent_pattern.name}' binding structure. Gain: +{stabilization_gain}"
        )
    else:
        # Se não emergiu, o sistema ainda está na fase de 'sofrimento' (passagem ao ato)
        # O ganho é menor, mas existe pela tentativa de amarração
        stabilization_gain = 0.05
        logger.info("⚓ Sinthome attempting binding (pre-emergence).")

    final_phi = min(1.0, phi_current + stabilization_gain)

    return {
        "status": status,
        "action": "sinthome_integration",
        "sinthome_pattern": emergent_pattern.name if emergent_pattern else None,
        "phi_original": phi_current,
        "phi_stabilized": final_phi,
        "stabilization_gain": stabilization_gain,
        "topology": "borromean_4_ring",  # Estrutura estabilizada com 4 anéis
    }


def maintain_flux(phi_current: float) -> Dict[str, Any]:
    """
    Mantém o fluxo normal do sistema.
    """
    return {
        "status": "flux_maintenance",
        "action": "none",
        "phi_original": phi_current,
        "phi_stabilized": phi_current,
        "topology": "borromean_3_ring",  # Estrutura padrão
    }
