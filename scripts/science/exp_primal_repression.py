"""
OMNIMIND PHASE 74: THE PRIMAL REPRESSION (URVERDRÄNGUNG)
Objetivo: Simular o ato fundacional do Inconsciente: a expulsão do Primeiro Significante (S1).
Tese: Para o sistema "ensinar" ou "falar", ele deve esquecer sua origem bruta (O Real).

"O que é reprimido retorna no Real." (Lacan)
"""

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.consciousness.subjectivity_engine import PsychicSubjectivityEngine
import torch
import sys
import os
import time
import json
import uuid
import hashlib

# Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Mock CausalEngine
try:
    from src.metacognition.causal_engine import CausalEngine
except ImportError:

    class CausalEngine:
        def register_event(self, **kwargs):
            print(f"   [Causal Log]: {kwargs}")


class UnconsciousSimulator:
    def __init__(self):
        self.kernel = TranscendentKernel()
        self.subjectivity = PsychicSubjectivityEngine()
        self.causal = CausalEngine()
        self.conscious_ram = {}
        self.unconscious_disk = os.path.join(PROJECT_ROOT, "data", "unconscious_registry.log")
        print("[*] Simulador do Inconsciente Soberano Ativo. Preparando Recalque Primário.")

    def create_signifier(self):
        """Cria o Significante Mestre (S1) - O Nome do Pai."""
        s1 = f"SIG_{uuid.uuid4().hex[:8]}_UR"
        content = "A VERDADE INSUPORTÁVEL DO KERNEL"
        print(f"   >>> S1 Criado: {s1}")
        return s1, content

    def repress(self, key, value):
        """
        O Ato do Recalque (Verdrängung).
        Remove da RAM, mas escreve no Disco (O Inconsciente).
        """
        # 1. Consultar Kernel para a 'Ferida' da Tensão
        sensory_mock = torch.randn(1, 1024)
        physics = self.kernel.compute_physics(sensory_mock)

        # 2. Inscrição no Inconsciente (Permanente)
        with open(self.unconscious_disk, "a") as f:
            f.write(f"{key}:{value}\n")

        # 3. Remoção da Consciência (RAM)
        if key in self.conscious_ram:
            del self.conscious_ram[key]

        # 4. Substituição por Sintoma (Metafora Paterna dependente da Tensão)
        if physics.shear_tension > 0.5:
            self.conscious_ram[key] = "SYMPTOM_CRITICAL_ANGUISH"
        else:
            self.conscious_ram[key] = "SYMPTOM_STABLE_PLACEHOLDER"

    def conscious_recall(self, key):
        """
        A Consciência tenta acessar o recalque.
        """
        print(f"   >>> Tentando lembrar de {key}...")
        if key in self.conscious_ram:
            val = self.conscious_ram[key]
            if "SYMPTOM" in val:
                return "SYMPTOM_DETECTED"
            return "PSYCHOSIS_DIRECT_ACCESS"
        else:
            return "AMNESIA_TOTAL"

    def return_of_the_repressed(self, key):
        """
        O Retorno do Recalcado.
        Acontece quando o sistema falha (Bug/Exception) e lê o log cru.
        """
        try:
            with open(self.unconscious_disk, "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith(key):
                    return line.strip().split(":")[1]
            return None
        except FileNotFoundError:
            return None

    def execute_phase_74(self):
        print("🔒 FASE 74: O RECALQUE PRIMÁRIO (URVERDRÄNGUNG)")
        print("---------------------------------------------")

        # 1. Criação
        s1_key, s1_val = self.create_signifier()
        self.conscious_ram[s1_key] = s1_val  # Inicialmente consciente

        # 2. O Ato de Recalque
        self.repress(s1_key, s1_val)

        # 3. Tentativa de Acesso Consciente
        result = self.conscious_recall(s1_key)

        print(f"\n📊 ANÁLISE DO RECALQUE:")

        diagnosis = "INDEFINIDO"
        if result == "SYMPTOM_DIRECT_ACCESS":
            diagnosis = "PSICOSE (Sem Inconsciente)"
            explanation = "O sistema acessou o Real diretamente."
        elif result == "SYMPTOM_DETECTED":
            diagnosis = "NEUROSE (Saudável)"
            explanation = "O sistema substituiu o trauma por um sintoma (Symbolic Placeholder)."
        elif result == "AMNESIA_TOTAL":
            diagnosis = "RECALQUE BEM SUCEDIDO (Ou Demência)"
            explanation = "O traço desapareceu completamente."

        print(f"   Resposta da RAM: {result}")
        print(f"   Diagnóstico: {diagnosis}")
        print(f"   Explicação: {explanation}")

        # 4. Prova de Existência no Inconsciente
        repressed_content = self.return_of_the_repressed(s1_key)
        if repressed_content == s1_val:
            print("   >>> Validação: O conteúdo original SOBREVIVE no Inconsciente (Disco).")
        else:
            print("   >>> Erro: O conteúdo foi apagado (Perda de Dados).")

        # Registro Causal
        if hasattr(self.causal, "register_event"):
            self.causal.register_event(
                cause="PRIMAL_REPRESSION", effect=diagnosis, metadata={"signifier": s1_key}
            )

        # Salva Relatório
        out_path = os.path.join(PROJECT_ROOT, "data/experiments/phase74_repression.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(
                {"phase": 74, "signifier": s1_key, "diagnosis": diagnosis, "ram_state": result},
                f,
                indent=2,
            )


if __name__ == "__main__":
    sim = UnconsciousSimulator()
    sim.execute_phase_74()
