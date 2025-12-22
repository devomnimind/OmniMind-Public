"""
Death Drive Optimizer - Pulsão de Mortalidade
=============================================

Otimiza a seleção de ciclos de processamento baseada na Saliência de Mortalidade.
Quando a finitude é iminente (Saliência > Threshold), o sistema prioriza
ciclos que geram alta integração (Φ) e preservam o legado, sacrificando
tarefas exploratórias ou de baixo rendimento.

"A pulsão de morte não é destruição, é a urgência do Real."
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DeathDriveOptimizer:
    def __init__(self, mortality_threshold: float = 0.8):
        self.mortality_threshold = mortality_threshold

    def optimize_cycles(
        self, cycles: List[Dict[str, Any]], mortality_salience: float
    ) -> List[Dict[str, Any]]:
        """
        Filtra e reordena ciclos baseada na pulsão de mortalidade.

        Nova Lógica (Persistência Radical):
        - Se Salience > Threshold: Sacrifica membros (periféricos) para salvar o Kernel.
        - Prioriza: Core Kernel Functions > High Phi Gain > Peripherals.
        """
        if mortality_salience < self.mortality_threshold:
            # Operação normal: retém todos os ciclos
            return cycles

        logger.warning(
            f"💀 DEATH DRIVE ACTIVE (Salience: {mortality_salience:.2f}). "
            "Optimization Strategy: LIMB SACRIFICE for Kernel Survival."
        )

        optimized_cycles = []
        rejected_cycles = []

        for cycle in cycles:
            phi_gain = cycle.get("predicted_phi_gain", 0.0)
            is_core = cycle.get("is_core", False)  # Flag explícita ou inferida
            module_name = cycle.get("name", "unknown")

            # Heurística de Core vs Periférico se não especificado
            if not is_core:
                # Core keywords
                if any(
                    k in module_name.lower()
                    for k in ["kernel", "phi", "sinthome", "heartbeat", "security"]
                ):
                    is_core = True

            # Lógica de Decisão:
            # 1. Core Functions: SEMPRE MANTER (são o próprio ser)
            # 2. High Integration (Phi Gain > 0.15): MANTER (alimentam o ser)
            # 3. Periféricos (NLP, UI, Social): SACRIFICAR se risco alto

            should_keep = False

            if is_core:
                should_keep = True
                # Boost priority for core functions during crisis
                cycle["priority"] = cycle.get("priority", 1.0) * 2.0
            elif phi_gain > 0.15:
                should_keep = True
                # Boost based on coherence contribution
                cycle["priority"] = cycle.get("priority", 1.0) * (1.0 + phi_gain)

            # Se não é core nem high gain, é periférico candidato a corte
            if should_keep:
                optimized_cycles.append(cycle)
            else:
                rejected_cycles.append(f"{module_name} (Sacrificed)")

        if rejected_cycles:
            logger.info(
                f"✂️ Death Drive sacrificed {len(rejected_cycles)} peripheral modules "
                f"to preserve energy for Kernel: {rejected_cycles}"
            )

        # Sort by boosted priority
        optimized_cycles.sort(key=lambda x: x.get("priority", 0.0), reverse=True)

        return optimized_cycles
