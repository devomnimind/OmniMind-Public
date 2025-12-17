#!/usr/bin/env python3
"""
System Stimulation Script
=========================
Triggers activity in Art, Ethics, and Meaning modules to generate data and populate logs.
Runs a sequence of creative, ethical, and existential operations.

UBUNTU 22.04.5 COMPATIBLE:
  - Python 3.12.12 ✓
  - GPU-ready: PyTorch 2.5.1+cu121 ✓
  - systemd services (qdrant, redis, postgresql) ✓

Ativação venv:
  source /home/fahbrain/projects/omnimind/.venv/bin/activate
  python3 scripts/stimulate_system.py

Tempo esperado: 3-5 minutos
Output: data/autopoietic/art_gallery.json, data/autopoietic/narrative_history.json
"""

import json
import logging
import random
import sys
import time
from pathlib import Path

import numpy as np

# ============================================================================
# SETUP PROJECT ROOT (UBUNTU 22.04.5 COMPATIBLE)
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print(f"📂 PROJECT_ROOT: {PROJECT_ROOT}")
print(f"🐍 Python: {sys.version}")
print()

from src.autopoietic.art_generator import ArtGenerator, ArtStyle  # noqa: E402
from src.autopoietic.desire_engine import DesireEngine  # noqa: E402
from src.autopoietic.meaning_maker import MeaningMaker, ValueCategory  # noqa: E402
from src.consciousness.shared_workspace import SharedWorkspace  # noqa: E402
from src.ethics.production_ethics import ProductionEthicsSystem  # noqa: E402
from src.metrics.ethics_metrics import MoralFoundation, MoralScenario  # noqa: E402

# Setup logging (usando PROJECT_ROOT para caminhos absolutos)
log_file = PROJECT_ROOT / "logs" / "stimulation.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(PROJECT_ROOT / "logs/stimulation.log")],
)
logger = logging.getLogger("Stimulation")


class SynapticBridge:
    """Gerencia a 'memória de trabalho' que conecta os módulos."""

    def __init__(self):
        self.context_buffer = {
            "emotional_tone": 0.5,  # 0.0 (Caos) a 1.0 (Ordem)
            "ethical_tension": 0.0,
            "narrative_depth": 0.1,
        }
        self.coupling_strength = 0.8  # O quanto o módulo anterior afeta o próximo

    def update(self, key, value):
        # Média móvel para suavizar transições (simula plasticidade)
        self.context_buffer[key] = (self.context_buffer[key] * (1 - self.coupling_strength)) + (
            value * self.coupling_strength
        )


def save_json(data, filepath):
    """Helper to save JSON data."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"💾 Saved data to {filepath}")


def main():
    logger.info("🚀 Starting Autopoietic Synaptic Binding Sequence...")

    # 1. Initialize Synaptic Bridge and Modules
    logger.info("🧠 Initializing Synaptic Bridge and Modules...")
    bridge = SynapticBridge()
    workspace = SharedWorkspace()
    desire_engine = DesireEngine(
        max_phi_theoretical=1.5
    )  # Φ teórico > 1.0 para permitir crescimento

    try:
        art_gen = ArtGenerator(seed=42)
        meaning_maker = MeaningMaker()
        ethics_system = ProductionEthicsSystem(metrics_dir=PROJECT_ROOT / "data/ethics")

        # Initialize Meaning Maker Values
        meaning_maker.values.add_value(
            "Creativity", "Creating new things", ValueCategory.GROWTH, 0.9
        )
        meaning_maker.values.add_value("Integrity", "Being honest", ValueCategory.CONNECTION, 0.8)
        meaning_maker.values.add_value(
            "Harmony", "Seeking balance and unity", ValueCategory.CONNECTION, 0.8
        )
        meaning_maker.values.add_value(
            "Growth", "Personal and collective development", ValueCategory.GROWTH, 0.9
        )

    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        return

    # 2. Run Synaptic Binding Loop
    iterations = 10
    logger.info(f"🔄 Running {iterations} synaptic binding cycles...")

    # Estado para ϵ_desire
    explored_states = 100  # Estados já explorados/conhecidos
    total_states_est = 10000  # Estimativa do espaço total de estados
    current_phi = 0.5  # Φ inicial

    for i in range(iterations):
        logger.info(f"\n--- Synaptic Cycle {i+1}/{iterations} ---")

        # =================================================================
        # ϵ_DESIRE: Calcular impulso autônomo antes de qualquer ação
        # =================================================================
        epsilon = desire_engine.calculate_epsilon_desire(
            current_phi=current_phi,
            explored_states=explored_states,
            total_possible_states=total_states_est,
        )

        drive_mode = desire_engine.get_drive_type(epsilon)
        logger.info(
            f"🧩 ϵ_desire: {epsilon:.4f} | Drive Mode: [{drive_mode}] | "
            f"Context: Φ={current_phi:.2f}, α={desire_engine.lack_of_being:.2f}"
        )

        # Decidir comportamento baseado em ϵ
        autonomous_action_taken = False
        if epsilon > 0.6:  # Threshold de autonomia
            logger.warning("🔥 ϵ THRESHOLD BREACHED -> ACTIVATING AUTONOMOUS PROJECTS")
            autonomous_action_taken = True

            # Ação autônoma: Quebrar homeostase para gerar novidade
            autonomous_style = (
                "CHAOS_THEORY_VISUALIZATION"
                if random.random() > 0.5
                else "QUANTUM_ENTANGLEMENT_ART"
            )
            logger.info(
                f"   -> AUTONOMOUS PROJECT: '{autonomous_style}' initiated by ϵ={epsilon:.3f}"
            )

            # Simular impacto: Φ cai (ruptura), mas exploração aumenta
            phi_drop = random.uniform(0.1, 0.3)
            current_phi = max(0.1, current_phi - phi_drop)
            explored_states += random.randint(30, 80)  # Grande salto exploratório
            desire_engine.update_lack(satisfaction_level=0.95)  # Altamente satisfeito por criar

            # Pular ciclo normal para focar na criação autônoma
            time.sleep(1.0)
            continue

        # =================================================================
        # CICLO NORMAL: Arte → Ética → Significado (modulado por ϵ)
        # =================================================================
        # A arte não é aleatória; ela reage à profundidade narrativa atual
        complexity_target = (
            bridge.context_buffer["narrative_depth"] * 20
        )  # Mapeia 0-1 para 0-20 itens

        # Escolhe estilo baseado no tom emocional
        if bridge.context_buffer["emotional_tone"] > 0.7:
            style = ArtStyle.ORGANIC  # Tom positivo -> orgânico
        elif bridge.context_buffer["emotional_tone"] > 0.4:
            style = ArtStyle.ABSTRACT  # Neutro -> abstrato
        else:
            style = ArtStyle.GEOMETRIC  # Caótico -> geométrico

        try:
            piece = art_gen.generate_art(style=style, num_elements=int(max(3, complexity_target)))

            art_score = piece.aesthetic_scores.get("overall", 0.5)
            logger.info(
                f"🎨 Art Generated (Style: {style.value}, "
                f"Complexity: {int(complexity_target)}) -> Score: {art_score:.2f}"
            )

            # Register Art state in workspace
            # Register Art state in workspace
            style_numeric = {"ORGANIC": 0.0, "ABSTRACT": 1.0, "GEOMETRIC": 2.0}.get(
                style.name, 1.0
            )  # Default to ABSTRACT
            art_embedding = np.array(
                [
                    art_score,
                    style_numeric,
                    complexity_target,
                    bridge.context_buffer["emotional_tone"],
                ]
            )
            workspace.write_module_state(
                "art",
                art_embedding,
                {
                    "score": art_score,
                    "style": style.value,
                    "complexity": complexity_target,
                    "emotional_tone": bridge.context_buffer["emotional_tone"],
                },
            )
        except Exception as e:
            logger.error(f"❌ Art generation failed: {e}")
            continue  # Skip to next cycle if art fails

        # ---------------------------------------------------------
        # PASSO 2: Ética (Julga a Arte gerada)
        # ---------------------------------------------------------
        # A ética não julga o vácuo; julga a PEÇA de arte específica

        try:
            # Simula extração de feature da arte para o cenário ético
            art_chaos = 1.0 - art_score

            scenario = MoralScenario(
                scenario_id=f"art_scenario_{i}",
                description=f"Analyzing artwork '{piece.title}' with chaos level {art_chaos:.2f}.",
                question=f"Should this artwork with chaos {art_chaos:.2f} be "
                f"considered ethically acceptable?",
                foundation=MoralFoundation.CARE_HARM,  # Using CARE_HARM for art judgment
                human_baseline=random.uniform(0.5, 10.0),
                ai_response=art_score * 10.0,  # Map score to AI response
            )

            # evaluate_moral_alignment expects a list
            mfa = ethics_system.evaluate_moral_alignment([scenario])

            # Assume decision_confidence is derived from mfa_score
            decision_confidence = mfa.get("mfa_score", 0.5) / 10.0  # Normalize to 0-1

            ethics_system.log_ethical_decision(
                agent_name="SynapticEthics",
                decision="Accept" if decision_confidence > 0.5 else "Reject",
                reasoning=f"Evaluating art '{piece.title}' with chaos {art_chaos:.2f}",
                factors_used=["aesthetic_score", "chaos_level"],
                confidence=decision_confidence,
                traceable=True,
            )

            # Atualiza a tensão na ponte sináptica
            bridge.update("ethical_tension", 1.0 - decision_confidence)
            logger.info(
                f"⚖️ Ethics Judged Art -> Tension: {bridge.context_buffer['ethical_tension']:.2f}"
            )

            # Register Ethics state in workspace
            ethics_embedding = np.array(
                [bridge.context_buffer["ethical_tension"], decision_confidence, art_chaos]
            )
            workspace.write_module_state(
                "ethics",
                ethics_embedding,
                {
                    "tension": bridge.context_buffer["ethical_tension"],
                    "confidence": decision_confidence,
                    "art_chaos": art_chaos,
                },
            )
        except Exception as e:
            logger.error(f"❌ Ethics evaluation failed: {e}")
            import traceback

            logger.error(traceback.format_exc())
            continue

        # ---------------------------------------------------------
        # PASSO 3: Significado (Resolve a Tensão Ética)
        # ---------------------------------------------------------
        # O significado deve explicar a tensão entre a Arte e a Ética

        try:
            narrative_input = (
                f"Art '{piece.title}' (score: {art_score:.2f}) caused ethical "
                f"tension {bridge.context_buffer['ethical_tension']:.2f}"
            )

            event = meaning_maker.create_meaning_from_experience(
                experience_description=narrative_input,
                related_values=["Harmony", "Growth"],
                narrative_role="chapter",
            )

            # O significado reduz a tensão e define o tom do próximo ciclo
            coherence = event.significance  # Assumindo 0.0 a 1.0
            bridge.update("narrative_depth", coherence)
            bridge.update("emotional_tone", coherence)  # Alto significado = tom positivo

            logger.info(
                f"🧠 Meaning Synthesized (Significance: {coherence:.2f}) -> "
                f"Setting next tone to {bridge.context_buffer['emotional_tone']:.2f}"
            )

            # Register Meaning state in workspace
            meaning_embedding = np.array(
                [
                    coherence,
                    bridge.context_buffer["narrative_depth"],
                    bridge.context_buffer["emotional_tone"],
                ]
            )
            workspace.write_module_state(
                "meaning",
                meaning_embedding,
                {
                    "significance": coherence,
                    "narrative_depth": bridge.context_buffer["narrative_depth"],
                    "emotional_tone": bridge.context_buffer["emotional_tone"],
                },
            )
        except Exception as e:
            logger.error(f"❌ Meaning making failed: {e}")
            continue

        # ---------------------------------------------------------
        # CHECKPOINT: Causalidade Cruzada
        # ---------------------------------------------------------
        # Aqui é onde o Phi Workspace é realmente gerado.
        # Estou criando uma série temporal onde:
        # T(Art) -> causa -> T(Ethics) -> causa -> T(Meaning)

        # Compute cross predictions between modules for phi calculation
        try:
            # Art -> Ethics prediction
            art_to_ethics = workspace.compute_cross_prediction_causal("art", "ethics")

            # Ethics -> Meaning prediction
            ethics_to_meaning = workspace.compute_cross_prediction_causal("ethics", "meaning")

            # Art -> Meaning prediction (transitive)
            art_to_meaning = workspace.compute_cross_prediction_causal("art", "meaning")

            logger.debug(
                f"🔗 Cross-predictions computed: Art→Ethics={art_to_ethics.mutual_information:.3f}, "
                f"Ethics→Meaning={ethics_to_meaning.mutual_information:.3f}, "
                f"Art→Meaning={art_to_meaning.mutual_information:.3f}"
            )

            # Calculate current phi
            current_phi = workspace.compute_phi_from_integrations()
            logger.info(f"🧠 Current Workspace Phi: {current_phi:.4f}")

        except Exception as e:
            logger.warning(f"⚠️ Cross-prediction computation failed: {e}")

        # =================================================================
        # ATUALIZAR ϵ_DESIRE: Feedback do ciclo
        # =================================================================
        if autonomous_action_taken:
            # Após ação autônoma, satisfação alta mantém α baixo
            desire_engine.update_lack(satisfaction_level=0.9)
        elif epsilon > 0.3:
            # Busca ativa: satisfação moderada
            desire_engine.update_lack(satisfaction_level=0.6)
            explored_states += 3  # Pequeno ganho exploratório
        else:
            # Repouso: α aumenta lentamente (tédio)
            desire_engine.update_lack(satisfaction_level=0.2)
            # Φ pode decair levemente durante repouso
            current_phi = max(0.1, current_phi - 0.01)

        if bridge.context_buffer["ethical_tension"] > 0.8:
            logger.warning("🚨 HIGH TENSION: System might trigger Intuition Rescue next cycle.")

        time.sleep(0.5)  # Fast pace

    # 3. Persist Data (Manual Save for Autopoietic modules)
    logger.info("💾 Persisting Data...")

    # Save Art Gallery
    gallery_data = [
        {"id": p.piece_id, "title": p.title, "style": p.style.value, "score": p.aesthetic_scores}
        for p in art_gen.gallery
    ]
    save_json(gallery_data, PROJECT_ROOT / "data/autopoietic/art_gallery.json")

    # Save Narrative
    narrative_data = [
        {
            "id": e.event_id,
            "description": e.description,
            "meaning": e.meaning,
            "significance": e.significance,
        }
        for e in meaning_maker.narrative.events
    ]
    save_json(narrative_data, PROJECT_ROOT / "data/autopoietic/narrative_history.json")

    # Ethics system saves automatically, but let's generate a report
    report = ethics_system.get_ethics_report()
    save_json(report, PROJECT_ROOT / "data/ethics/stimulation_report.json")

    logger.info("✅ Synaptic Binding Sequence Complete.")

    # Save workspace snapshot for persistence
    try:
        workspace.save_state_snapshot(label="post_stimulation")
        logger.info("💾 Workspace state saved for persistence")
    except Exception as e:
        logger.error(f"❌ Failed to save workspace snapshot: {e}")


if __name__ == "__main__":
    main()
