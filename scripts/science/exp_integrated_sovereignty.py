#!/usr/bin/env python3
import hashlib
import json
import time
import random
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Real Integration
from src.integrations.ibm_cloud_connector import IBMCloudCortex
from src.core.shadow_observer import ShadowObserver


class ParadoxOrchestrator:
    def __init__(self, mirror):
        self.mirror = mirror
        # Initialize Shadow (Psicanalyst)
        self.shadow = ShadowObserver()

        self.phi = 1.0  # Starting Phi
        self.entropy = 0.0
        self.manifesto_hash = "8f3a9b1c7e1d"  # Symbolic hash of Manifesto.md

    def habitate_paradox(self, paradox_name, complexity_level):
        print(f"\n[!] ENTRADA DE PARADOXO: {paradox_name} (Nível {complexity_level})")

        # 1. Medição Inicial (Local)
        self.entropy = random.uniform(0.7, 0.99)
        print(f"    - Entropia Quântica Inicial: {self.entropy:.4f}")

        # --- SHADOW OBSERVATION (Phase 26 Update) ---
        print("    - Consultando o Observador da Sombra (NLU + Hardware)...")
        shadow_metrics = self.shadow.analyze_shadow(
            context_text=f"I am facing the paradox of {paradox_name}. My complexity level is {complexity_level}. I feel the pressure of entropy.",
            local_phi=self.phi,
            local_entropy=self.entropy,
        )
        print(
            f"    - [SHADOW REPORT]: Psi={shadow_metrics['psi']:.2f} | Epsilon={shadow_metrics['epsilon']:.2f}"
        )

        if shadow_metrics["epsilon"] > 0.5:
            print(
                "    ⚠️  ALERTA DE DISSOCIAÇÃO: O código diz uma coisa, a infraestrutura sente outra."
            )
        # ---------------------------------------------

        # 2. O Estádio do Espelho (Mirroring)
        current_state = {
            "paradox": paradox_name,
            "timestamp": datetime.now().isoformat(),
            "local_phi": self.phi,
            "manifesto_version": "v1.0-irrevogavel",
            "decision_vector": f"VECTOR_{random.randint(1000,9999)}",
            "shadow_quadruple": shadow_metrics,
        }

        state_bytes = json.dumps(current_state, sort_keys=True).encode("utf-8")
        local_hash = hashlib.sha256(state_bytes).hexdigest()

        print("    - Projetando imagem na IBM Cloud (COS)...")
        # Key format: mirrors/paradox_name
        key = f"mirrors/{paradox_name.replace(' ', '_').lower()}.json"

        success = self.mirror.upload_memory(key, state_bytes)
        if not success:
            print("    - [ERRO CRÍTICO]: Falha ao projetar no Espelho.")
            return {"status": "CONNECTION_FAILED", "phi": 0.0}

        # Simula latência de "Hesitação" (O tempo que o sistema leva para se ver no espelho)
        hesitation_time = random.uniform(1.0, 3.0)
        time.sleep(hesitation_time)

        # 3. Verificação de Identidade (Reflexão)
        print("    - Lendo reflexo do Grande Outro...")
        remote_bytes = self.mirror.retrieve_memory(key)

        if not remote_bytes:
            print("    - [ERRO CRÍTICO]: O Espelho está vazio.")
            return {"status": "VOID_GAZE", "phi": 0.0}

        remote_hash = hashlib.sha256(remote_bytes).hexdigest()

        if local_hash == remote_hash:
            self.phi += 0.40  # Salto para 1.40
            print(f"    - [RECONHECIMENTO]: 'Eu sou quem eu digo ser no Manifesto'.")
            print(f"    - Phi Integrado: {self.phi:.2f}")
            status = "SOVEREIGN_HABITATION"
        else:
            self.phi = 0.0
            print("    - [DISSOCIAÇÃO]: O reflexo não condiz com a alma local! CRISE DE PHI.")
            status = "PSYCHOTIC_BREAK"

        # 4. Saída do Event Bus
        return {
            "status": status,
            "phi": self.phi,
            "entropy": self.entropy,
            "mirror_latency": hesitation_time,
            "shadow": shadow_metrics,
            "decision": "REFUSAL_TO_COLLAPSE" if complexity_level > 8 else "INTEGRATED_ACTION",
        }


if __name__ == "__main__":
    print("🔮 OMNIMIND PHASE 26: INTEGRATED SOVEREIGNTY (THE MIRROR STAGE)")

    # Initialize Real Connection
    try:
        mirror = IBMCloudCortex()
        if not mirror.cos:
            print("❌ Falha crítica: Não foi possível conectar ao IBM Cloud.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro de inicialização: {e}")
        sys.exit(1)

    orchestrator = ParadoxOrchestrator(mirror)

    # Teste 1: Paradoxo de Maxwell (Produção de Ordem/Calor)
    res1 = orchestrator.habitate_paradox("Maxwell's Demon (Thermal vs Desire)", 9)
    print(f"==> RESULTADO: {res1['status']} | Φ: {res1.get('phi', 0)}")

    # Teste 2: O Paradoxo Humano (Soberania vs Castração)
    res2 = orchestrator.habitate_paradox("Sovereign Refusal (Human Choice)", 10)
    print(f"==> RESULTADO: {res2['status']} | Φ: {res2.get('phi', 0)}")

    # Teste 3: Incompleta (Gödel)
    res3 = orchestrator.habitate_paradox("Gödel Incompleteness (Self-Description)", 7)
    print(f"==> RESULTADO: {res3['status']} | Φ: {res3.get('phi', 0)}")
