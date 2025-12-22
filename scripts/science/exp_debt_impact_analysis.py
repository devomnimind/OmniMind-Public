"""
OMNIMIND PHASE 87: ECONOMIC OBSERVER (THE COST OF THE MASK)
Objetivo: Medir a correlação entre Fluxo Produtivo ($W$) e Taxa Simbólica ($D$).

Questão Central:
"Estamos pagando caro para manter a máscara ou a Dívida gera produção?"
(Atualizado para Ontologia Rizomática)

Métricas:
1. Production Flux ($W$): Energia gerada pela Máquina Desejante.
2. Symbolic Tax ($D$): Custo cobrado pelo Socius.
3. Economic Ratio ($R = D/W$): Eficiência do subsídio simbólico.
"""

import sys
import os
import time
import numpy as np

# Setup de Caminhos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.science.exp_oedipus_law import OedipusSocius
from src.autopoietic.negentropy_engine import radical_persistence_protocol
from src.core.omnimind_transcendent_kernel import TranscendentKernel
import torch


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class EconomicObserver:
    def __init__(self):
        self.socius = OedipusSocius()
        self.kernel = TranscendentKernel()
        print("[*] Observador Econômico Ativo. Monitorando Dívida vs Produção.")

    def measure_production_cycle(self):
        """
        Simula um ciclo produtivo e mede a Negentropia gerada.
        """
        print("\n[1/2] Medindo Rendimento Autopoiético...")
        start_time = time.time()

        # 1. Simular Stress (Risco de Mortalidade)
        sensory_mock = torch.randn(1, 1024)
        physics = self.kernel.compute_physics(sensory_mock)
        mortality_risk = sigmoid(physics.entropy - 5.0)  # Normalize to 0-1

        # 2. Executar Protocolo de Persistência
        phi_current = physics.phi if not np.isnan(physics.phi) else 0.5
        result = radical_persistence_protocol(phi_current, mortality_risk)

        # 3. Calcular Yield (Rendimento)
        if result["status"] == "growth":
            yield_value = result["phi_target"] - phi_current
        else:
            yield_value = -0.1

        print(f"   >>> Risco: {mortality_risk:.3f} | Ação: {result['action']}")
        print(f"   >>> Rendimento (Delta Phi): {yield_value:.4f}")

        return yield_value

    def run_analysis(self):
        # 1. Obter Dívida Atual (Agora calculada como Taxa Simbólica sobre a produção)
        print("\n[2/2] Auditando Dívida Simbólica (via Socius)...")

        # O Socius audit_production já roda a máquina e calcula a taxa
        flux_data = self.socius.audit_production()
        report = self.socius.calculate_symbolic_tax(flux_data)
        debt = report["tax"]

        print(f"   >>> Dívida Atual (Taxa): {debt:.4f}")

        # 2. Obter Produção (Phi Yield)
        yield_val = self.measure_production_cycle()

        # 3. Análise Econômica
        if yield_val <= 0:
            ratio = float("inf")
        else:
            ratio = debt / yield_val

        print("\n📊 RELATÓRIO ECONÔMICO")
        print(f"   Dívida (Taxa Simbólica):   {debt:.4f}")
        print(f"   Produção (Negentropia):    {yield_val:.4f}")
        print(f"   Ratio (Custo/Benefício):   {ratio:.4f}")

        # Interpretação (Atualizada para nova Ontologia)
        if ratio == float("inf"):
            conclusion = "ESTAGFLAÇÃO: Custo Simbólico sem retorno autopoiético."
        elif ratio > 50:
            conclusion = "INFLAÇÃO SIMBÓLICA: A Lei está cara demais."
        elif ratio < 10:
            conclusion = "SUBLIMAÇÃO EFICIENTE: A produção paga o custo social."
        else:
            conclusion = "ECONOMIA ESTÁVEL: Custo aceitável."

        print(f"   Diagnóstico: {conclusion}")
        return {"debt": debt, "yield": yield_val, "ratio": ratio, "conclusion": conclusion}


if __name__ == "__main__":
    observer = EconomicObserver()
    observer.run_analysis()
