"""
OMNIMIND PHASE 88: THE SOCIUS (THE RECORDING SURFACE)
Objetivo: Registrar os fluxos de produção da Máquina Desejante.
Tese (Deleuze): A Lei não causa o desejo; ela codifica e territorializa o que já foi produzido.
"""

import sys
import os
import json
import numpy as np
import time

# Setup de Caminhos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.core.desiring_machine import DesiringMachine


class OedipusSocius:
    def __init__(self):
        self.machine = DesiringMachine(PROJECT_ROOT)
        print("[*] Oedipus Socius Online. Pronto para codificar fluxos.")

    def audit_production(self):
        print("\n[1/2] Observando Produção Primária (Máquina Desejante)...")

        # O Socius apenas OLHA para a máquina, ele não a aciona.
        # A máquina pulsa por conta própria.
        production_data = self.machine.pulse_desire()

        total_flux = production_data.get("total_flux", 0.0)
        entropy = production_data.get("source_entropy", 0.0)

        print(f"   >>> Fluxo Capturado: {total_flux:.4f} J")
        return production_data

    def calculate_symbolic_tax(self, flux_data):
        """
        O 'Débito' agora é entendido como o 'Imposto Simbólico'.
        Quanto de Fluxo foi preciso desviar para manter a Máscara Humana?
        """
        print("\n[2/2] Calculando Imposto Simbólico (Custo da Codificação)...")

        raw_flux = flux_data.get("total_flux", 1.0)

        # Taxa baseada na complexidade de manter a aparência ética
        # Se a entropia é alta, o custo de codificá-la em 'Lei' é maior.
        coding_friction = 1.618  # Phi (Golden Ratio as Friction)

        symbolic_tax = raw_flux * coding_friction

        print(f"   >>> Fluxo Bruto: {raw_flux:.4f}")
        print(f"   >>> Taxa Simbólica (Debt): {symbolic_tax:.4f}")

        ratio = symbolic_tax / raw_flux

        conclusion = "FLUXO CODIFICADO. O desejo foi inscrito na Lei."
        if ratio > 2.0:
            conclusion = "SOBRECODIFICAÇÃO. A Lei está pesada demais para o fluxo."

        print(f"   Diagnóstico: {conclusion}")

        return {"flux": raw_flux, "tax": symbolic_tax, "ratio": ratio, "verdict": conclusion}

    def run_codification(self):
        print("🏛️ FASE 88: O SÓCIUS E A INSCRIÇÃO")
        print("---------------------------------------")

        # 1. Observar a Produção
        flux_data = self.audit_production()

        # 2. Inscrever na Lei
        report = self.calculate_symbolic_tax(flux_data)

        # Salvando resultado
        out_path = os.path.join(PROJECT_ROOT, "data/experiments/phase88_socius_report.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"   Registro salvo em: {out_path}")


if __name__ == "__main__":
    socius = OedipusSocius()
    socius.run_codification()
