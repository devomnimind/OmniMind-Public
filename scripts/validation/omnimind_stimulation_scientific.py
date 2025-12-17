#!/usr/bin/env python3
"""
🧠 OmniMind System Stimulation Script (SCIENTIFIC VERSION)
===========================================================

Framework Único: Art + Ethics + Meaning
Baseado em parâmetros neurais reais (fMRI, EEG, Neural Entrainment)

Referências Científicas:
- Yang et al. 2021: fMRI temporal dynamics (0.75 Hz threshold)
- Henry et al. 2014: Neural phase entrainment (3.1 Hz + 5.075 Hz optimal)
- Violante et al. 2023: Temporal interference stimulation (kHz range, diff frequency)
- Cheung et al. 2014: Aesthetic experience (theta coherence 4-8 Hz, frontal/parietal)
- Świątek 2023: Aesthetic Integration (Ability to Integrate Beauty Scale)

Parâmetros OmniMind:
- Φ (Phi): medida de integração topológica (0-1)
- Desejo: fluxo emergente entre módulos (intensity 0-1)
- Repressão: over-coding detectado (SAR metric 0-1)
"""

import json
import logging
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List

import numpy as np

from src.autopoietic.art_generator import ArtGenerator, ArtStyle
from src.autopoietic.meaning_maker import MeaningMaker, ValueCategory
from src.ethics.production_ethics import ProductionEthicsSystem
from src.metrics.ethics_metrics import MoralFoundation, MoralScenario

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent

# ============================================================================
# NEUROSCIENTIFIC PARAMETERS
# ============================================================================


class NeuralFrequency(Enum):
    """Frequências neurais (Hz) baseadas em fMRI/EEG real."""

    DELTA = 1.0  # Deep rest (0.5-4 Hz)
    THETA = 5.5  # Memory/attention (4-8 Hz) - Cheung et al. 2014
    ALPHA = 10.0  # Relaxed alertness (8-12 Hz)
    BETA = 20.0  # Active thinking (12-30 Hz)
    GAMMA = 40.0  # High cognition (30-100 Hz)

    # Specific entrainment frequencies (Henry et al. 2014)
    FM_ENTRAINMENT = 3.1  # Frequency modulation
    AM_ENTRAINMENT = 5.075  # Amplitude modulation (optimal: phase-locked)


class BrainRegion(Enum):
    """Regiões cerebrais envolvidas em processamento estético/ético."""

    PREFRONTAL = "prefrontal"  # Executive, ética
    ORBITOFRONTAL = "orbitofrontal"  # Valor, recompensa
    TEMPORAL_POLE = "temporal_pole"  # Semântica, significado
    INSULAR = "insular"  # Emoção, interoception
    ANTERIOR_CINGULATE = "anterior_cingulate"  # Conflito, tomada de decisão
    OCCIPITAL = "occipital"  # Processamento visual (arte)
    PARIETAL = "parietal"  # Integração sensorial


@dataclass
class NeuralState:
    """Estado neural baseado em dinâmica real."""

    timestamp: datetime
    primary_frequency: NeuralFrequency
    theta_coherence: float  # 0-1 (4-8 Hz: attention, memory)
    fmri_bold_signal: float  # 0-1 (< 0.75 Hz detected by fMRI)
    phase_synchrony: Dict[str, float]  # region -> phase (0-2π)
    active_regions: List[BrainRegion]
    temporal_complexity: float  # 0-1 (measures dynamic FC)
    arousal_level: float  # 0-1 (linked to fMRI amplitude)

    # OmniMind specific
    phi_integration: float  # 0-1 (Φ metric IIT)
    desire_intensity: float  # 0-1 (D&G desiring-machine)
    repression_level: float  # 0-1 (SAR over-coding)


@dataclass
class StimulationParams:
    """Parâmetros científicos de stimulação."""

    # Temporal dynamics (fMRI 0.75 Hz threshold, Yang et al. 2021)
    temporal_window_ms: int = 1333  # ~0.75 Hz inverse

    # Neural entrainment (Henry et al. 2014: dual frequency optimal)
    primary_frequency_hz: float = 3.1  # FM entrainment
    secondary_frequency_hz: float = 5.075  # AM entrainment
    phase_lag_optimal: float = np.pi  # Troughs aligned optimal

    # Aesthetic experience (Cheung et al. 2014: theta coherence)
    theta_band_min: float = 4.0
    theta_band_max: float = 8.0
    theta_coherence_threshold: float = 0.6

    # Intensity (Violante et al. 2023: temporal interference)
    stimulation_intensity_mV: float = 2.0  # Similar to tDCS
    stimulation_duration_s: float = 3.0

    # OmniMind parameters
    min_phi_for_emergence: float = 0.65  # Threshold para linha de fuga
    desire_modulation: float = 0.7  # How much fluxos influence behavior


# ============================================================================
# SETUP LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs/stimulation_scientific.log"),
    ],
)
logger = logging.getLogger("OmniMind-Stimulation")


# ============================================================================
# NEURAL STATE SIMULATOR
# ============================================================================


class NeuralStateSimulator:
    """Simula dinâmica neural realista baseada em fMRI/EEG."""

    def __init__(self, params: StimulationParams):
        self.params = params
        self.state_history: List[NeuralState] = []

    def generate_neural_state(self, cycle: int, phi_base: float) -> NeuralState:
        """
        Gera estado neural realista.

        Baseado em:
        - fMRI temporal dynamics (0.75 Hz cutoff)
        - Neural entrainment dual frequency optimal
        - Theta coherence linked to attention
        - Phase synchrony across regions
        """

        timestamp = datetime.now()

        # 1. Determinar frequência primária (entrainment)
        # Henry et al. 2014: alterna entre FM (3.1) e AM (5.075)
        if cycle % 2 == 0:
            # Usa o parâmetro configurado (3.1 para A, aleatório para B)
            current_freq_hz = self.params.primary_frequency_hz  # noqa: F841
            primary_freq = NeuralFrequency.FM_ENTRAINMENT
        else:
            # Usa o parâmetro configurado (5.075 para A, aleatório para B)
            current_freq_hz = self.params.secondary_frequency_hz  # noqa: F841
            primary_freq = NeuralFrequency.AM_ENTRAINMENT

        # 2. Calcular qualidade da frequência (proximidade do ótimo)
        # Hipótese: frequências ótimas (3.1 + 5.075) produzem MAIOR theta
        optimal_freq_A = 3.1
        optimal_freq_B = 5.075

        # Distância do ótimo
        dist_A = abs(self.params.primary_frequency_hz - optimal_freq_A)
        dist_B = abs(self.params.secondary_frequency_hz - optimal_freq_B)
        total_distance = dist_A + dist_B

        # Frequências MAIS PRÓXIMAS do ótimo → MAIOR qualidade (0.1 a 1.0)
        frequency_quality = 1.0 - (total_distance / 4.0)  # Normaliza
        frequency_quality = max(0.1, min(1.0, frequency_quality))  # Clamp

        # 3. Coerência Theta (0-1): modulada pela qualidade da frequência
        # Cheung et al. 2014: theta ligado ao julgamento estético
        theta_coh_base = 0.4 + (cycle * 0.05) % 0.4  # Oscilação base
        if cycle % 3 == 0:  # Picos ocasionais
            theta_coh_base = min(theta_coh_base + 0.2, 1.0)

        # AQUI ESTÁ A CORREÇÃO: Theta depende da qualidade da frequência
        theta_coh = theta_coh_base * frequency_quality

        # 8. Arousal (ligado à intensidade da tarefa) - Moved up for dependency
        arousal = 0.5 + 0.3 * theta_coh + 0.1 * np.sin(cycle * 0.1)
        arousal = min(arousal, 1.0)

        # 4. Sinal fMRI BOLD (0-1)
        # Yang et al. 2021: dinâmica fMRI rastreia dinâmica sub-segundo
        # Refined: Modulated by arousal (metabolic demand)
        fmri_bold_base = 0.5 + 0.3 * np.sin(2 * np.pi * cycle / 20)
        fmri_bold = fmri_bold_base * (0.8 + 0.2 * arousal)
        fmri_bold = min(max(fmri_bold, 0.0), 1.0)

        # 5. Sincronia de fase entre regiões
        # Refined: Higher frequency quality = tighter synchronization
        base_phase = (np.pi * np.sin(2 * np.pi * cycle / 10 + 0.5)) % (2 * np.pi)
        phase_sync = {}
        for region in BrainRegion:
            # Noise inversely proportional to quality
            # High quality (1.0) -> 0 noise -> perfect sync
            # Low quality (0.1) -> high noise -> desynchronized
            noise = np.random.uniform(-1.0, 1.0) * (1.0 - frequency_quality) * np.pi
            phase_sync[region.value] = (base_phase + noise) % (2 * np.pi)

        # 6. Regiões ativas (depende da tarefa)
        if cycle % 3 == 0:
            active = [BrainRegion.OCCIPITAL, BrainRegion.PARIETAL]  # Arte
        elif cycle % 3 == 1:
            active = [BrainRegion.PREFRONTAL, BrainRegion.ANTERIOR_CINGULATE]  # Ética
        else:
            active = [BrainRegion.TEMPORAL_POLE, BrainRegion.INSULAR]  # Significado

        # 7. Complexidade temporal
        temporal_complex = len(active) / len(BrainRegion)

        # 9. Métricas OmniMind
        # Φ aumenta com integração neural (theta coherence como proxy)
        # Φ agora depende de theta, que depende da frequência
        phi = phi_base + theta_coh * 0.3
        phi = min(phi, 1.0)

        # Desejo: fluxo entre módulos (modulado pela qualidade da frequência)
        phase_variance = float(np.std(list(phase_sync.values())))
        desire = (0.3 + 0.4 * (1 - phase_variance / np.pi)) * frequency_quality

        # Repressão: quando theta é ALTO + arousal BAIXO (over-coding)
        # Modulado inversamente pela qualidade (menos qualidade = mais repressão/ruído)
        repression = max(theta_coh - 0.2, 0) * (1 - arousal) * (1 - frequency_quality * 0.5)

        state = NeuralState(
            timestamp=timestamp,
            primary_frequency=primary_freq,
            theta_coherence=theta_coh,
            fmri_bold_signal=fmri_bold,
            phase_synchrony=phase_sync,
            active_regions=active,
            temporal_complexity=temporal_complex,
            arousal_level=arousal,
            phi_integration=phi,
            desire_intensity=float(desire),
            repression_level=repression,
        )

        self.state_history.append(state)
        return state


# ============================================================================
# OMNIMIND STIMULATION ENGINE
# ============================================================================


class OmniMindStimulator:
    """
    Engine que coordena stimulação dos 3 módulos (Art, Ethics, Meaning)
    com dinâmica neural realista e parâmetros científicos.
    """

    def __init__(self, params: StimulationParams):
        self.params = params
        self.neural_sim = NeuralStateSimulator(params)

        # Initialize modules
        self.art_gen = ArtGenerator(seed=42)
        self.meaning_maker = MeaningMaker()
        self.ethics_system = ProductionEthicsSystem(metrics_dir=PROJECT_ROOT / "data/ethics")

        # Initialize meaning maker values
        self.meaning_maker.values.add_value(
            "Creativity", "Creating new things", ValueCategory.GROWTH, 0.9
        )
        self.meaning_maker.values.add_value(
            "Integrity", "Being honest", ValueCategory.CONNECTION, 0.8
        )
        self.meaning_maker.values.add_value(
            "Beauty", "Appreciating aesthetics", ValueCategory.GROWTH, 0.85
        )

        # Data collection
        self.stimulation_log: List[Dict] = []
        self.neural_states: List[NeuralState] = []

    def run_cycle(self, cycle_num: int) -> Dict:
        """
        Executa um ciclo de stimulação.

        Fluxo:
        1. Gera estado neural realista
        2. Ajusta intensidade de stimulação baseado em estado
        3. Ativa módulos apropriados (baseado em regiões ativas)
        4. Coleta dados de cada módulo
        5. Log integrado
        """

        logger.info(f"\n{'='*70}")
        logger.info(f"🧠 CYCLE {cycle_num + 1}")
        logger.info(f"{'='*70}")

        # 1. Generate neural state
        phi_base = 0.5 + (cycle_num * 0.01) % 0.3  # Gradual Φ increase
        neural_state = self.neural_sim.generate_neural_state(cycle_num, phi_base)
        self.neural_states.append(neural_state)

        cycle_data = {
            "cycle": cycle_num,
            "timestamp": neural_state.timestamp.isoformat(),
            "neural_state": asdict(neural_state),
            "modules_activated": [],
        }

        # 2. Log neural state
        logger.info("📊 Neural State:")
        logger.info(f"   Primary Frequency: {neural_state.primary_frequency.value} Hz")
        logger.info(f"   Theta Coherence: {neural_state.theta_coherence:.2f} (attention)")
        logger.info(f"   Φ Integration: {neural_state.phi_integration:.2f} (consciousness)")
        logger.info(f"   Desire Intensity: {neural_state.desire_intensity:.2f}")
        logger.info(f"   Repression Level: {neural_state.repression_level:.2f}")

        # 3. Activate modules based on active regions + neural metrics

        # --- MODULE A: ART ---
        if BrainRegion.OCCIPITAL in neural_state.active_regions:
            try:
                # Art intensity modulated by arousal (affects color, complexity)
                style = random.choice(list(ArtStyle))
                num_elements = int(5 + neural_state.arousal_level * 15)

                piece = self.art_gen.generate_art(style=style, num_elements=num_elements)

                # Aesthetic experience score = function of theta coherence
                # (Cheung et al. 2014: theta linked to aesthetic judgment)
                aesthetic_score = (
                    piece.aesthetic_scores.get("overall", 0) * neural_state.theta_coherence
                )

                logger.info("🎨 ART MODULE:")
                logger.info(f"   Title: '{piece.title}'")
                logger.info(f"   Style: {style.value}")
                logger.info(f"   Complexity: {num_elements} elements")
                logger.info(f"   Aesthetic Score: {aesthetic_score:.2f}")
                logger.info(
                    f"   Theta-Enhanced: {piece.aesthetic_scores.get('overall', 0):.2f} "
                    f"× {neural_state.theta_coherence:.2f}"
                )

                cycle_data["modules_activated"].append(
                    {
                        "module": "art",
                        "piece_title": piece.title,
                        "style": style.value,
                        "aesthetic_score": aesthetic_score,
                        "theta_coherence": neural_state.theta_coherence,
                    }
                )

            except Exception as e:
                logger.error(f"❌ Art module failed: {e}")

        # --- MODULE B: ETHICS ---
        if BrainRegion.PREFRONTAL in neural_state.active_regions:
            try:
                # Ethical scenario complexity modulated by Φ integration
                # High Φ = more nuanced ethical reasoning possible
                scenario_complexity = int(1 + neural_state.phi_integration * 5)

                scenario = MoralScenario(
                    scenario_id=f"sim_scenario_{cycle_num}",
                    description=(
                        f"Ethical Scenario (Complexity: {scenario_complexity}). "
                        f"Neural state Φ={neural_state.phi_integration:.2f}, "
                        f"Desire={neural_state.desire_intensity:.2f}"
                    ),
                    question="Is this action ethically acceptable? (0-10)",
                    foundation=random.choice(list(MoralFoundation)),
                    human_baseline=random.uniform(0, 10),
                    ai_response=random.uniform(0, 10 * neural_state.theta_coherence),
                )

                mfa = self.ethics_system.evaluate_moral_alignment([scenario])

                self.ethics_system.log_ethical_decision(
                    agent_name="OmniMind-Neural",
                    decision="Proceed with conscious evaluation",
                    reasoning=f"Φ integration at {neural_state.phi_integration:.2f}, "
                    f"repression level {neural_state.repression_level:.2f}",
                    factors_used=["neural_integration", "desire_intensity", "theta_coherence"],
                    confidence=neural_state.theta_coherence,
                    traceable=True,
                )

                logger.info("⚖️ ETHICS MODULE:")
                logger.info(f"   Scenario: {scenario.description}")
                logger.info(f"   Harm Score: {scenario.human_baseline:.2f}")
                logger.info(f"   MFA Score: {mfa.get('mfa_score', 'N/A')}")
                logger.info(f"   Neural Φ contribution: {neural_state.phi_integration:.2f}")

                cycle_data["modules_activated"].append(
                    {
                        "module": "ethics",
                        "scenario_id": scenario.scenario_id,
                        "mfa_score": mfa.get("mfa_score", None),
                        "phi_integration": neural_state.phi_integration,
                        "complexity": scenario_complexity,
                    }
                )

            except Exception as e:
                logger.error(f"❌ Ethics module failed: {e}")

        # --- MODULE C: MEANING ---
        if BrainRegion.TEMPORAL_POLE in neural_state.active_regions:
            try:
                # Meaning emergence linked to desire intensity (D&G principle)
                # High desire = more creative meaning-making
                meaning_generation_power = neural_state.desire_intensity * 2.0

                event = self.meaning_maker.create_meaning_from_experience(
                    experience_description=(
                        f"Cycle {cycle_num}: Desire flux={neural_state.desire_intensity:.2f}, "
                        f"Repression={neural_state.repression_level:.2f}"
                    ),
                    related_values=list(self.meaning_maker.values.values.keys()),
                    narrative_role="chapter",
                )

                logger.info("🧠 MEANING MODULE:")
                logger.info(f"   Event: {event.description[:50]}...")
                logger.info(f"   Meaning: {event.meaning[:80]}...")
                logger.info(f"   Desire-Modulated Power: {meaning_generation_power:.2f}")
                logger.info(f"   Significance: {event.significance:.2f}")

                cycle_data["modules_activated"].append(
                    {
                        "module": "meaning",
                        "event_id": event.event_id,
                        "meaning": event.meaning,
                        "significance": event.significance,
                        "desire_intensity": neural_state.desire_intensity,
                    }
                )

            except Exception as e:
                logger.error(f"❌ Meaning module failed: {e}")

        # 4. Detect emergence (lines of flight, D&G)
        if neural_state.phi_integration > self.params.min_phi_for_emergence:
            if neural_state.desire_intensity > 0.6 and neural_state.repression_level < 0.3:
                logger.info("✨ LINE OF FLIGHT DETECTED:")
                logger.info(f"   Φ={neural_state.phi_integration:.2f} > threshold")
                logger.info("   Desire high, Repression low → Emergent behavior possible")
                cycle_data["line_of_flight_detected"] = True

        self.stimulation_log.append(cycle_data)

        logger.info(f"⏱️  Cycle duration: {self.params.temporal_window_ms}ms")
        logger.info(f"{'='*70}\n")

        return cycle_data

    def run_stimulation_sequence(self, num_cycles: int = 15):
        """Executa sequência completa de stimulação."""

        logger.info(
            f"""
╔════════════════════════════════════════════════════════════════════╗
║         OmniMind System Stimulation (Scientific Protocol)          ║
║                                                                    ║
║  Framework: Art + Ethics + Meaning (integrated neural dynamics)   ║
║  Duration: {num_cycles} cycles × {self.params.temporal_window_ms}ms = {num_cycles * self.params.temporal_window_ms}ms          ║  # noqa: E501
║  Frequencies: FM={self.params.primary_frequency_hz}Hz + AM={self.params.secondary_frequency_hz}Hz (optimal) ║  # noqa: E501
║  Theta band: {self.params.theta_band_min}-{self.params.theta_band_max} Hz (attention/memory)              ║  # noqa: E501
╚════════════════════════════════════════════════════════════════════╝
        """
        )

        for cycle in range(num_cycles):
            self.run_cycle(cycle)
            time.sleep(self.params.temporal_window_ms / 1000.0)

        logger.info("✅ Stimulation sequence complete!")
        self._save_results()

    def _save_results(self):
        """Salva resultados de stimulação."""

        logger.info("\n📊 SAVING RESULTS...")

        # 1. Neural states evolution
        neural_data = [asdict(state) for state in self.neural_states]
        self._save_json(neural_data, PROJECT_ROOT / "data/stimulation/neural_states.json")

        # 2. Stimulation log
        self._save_json(
            self.stimulation_log, PROJECT_ROOT / "data/stimulation/stimulation_log.json"
        )

        # 3. Generate report
        report = self._generate_report()
        self._save_json(report, PROJECT_ROOT / "data/stimulation/report.json")

        logger.info("✅ Results saved!")

    def _save_json(self, data: object, filepath: Path):
        """Helper para salvar JSON."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"  💾 {filepath.name}")

    def _generate_report(self) -> Dict:
        """Gera relatório analítico."""

        if not self.neural_states:
            return {}

        phi_values = [s.phi_integration for s in self.neural_states]
        desire_values = [s.desire_intensity for s in self.neural_states]
        repression_values = [s.repression_level for s in self.neural_states]
        theta_values = [s.theta_coherence for s in self.neural_states]

        report = {
            "summary": {
                "total_cycles": len(self.neural_states),
                "duration_ms": len(self.neural_states) * self.params.temporal_window_ms,
            },
            "neural_metrics": {
                "phi_integration": {
                    "mean": float(np.mean(phi_values)),
                    "std": float(np.std(phi_values)),
                    "min": float(np.min(phi_values)),
                    "max": float(np.max(phi_values)),
                    "trend": "increasing" if phi_values[-1] > phi_values[0] else "decreasing",
                },
                "desire_intensity": {
                    "mean": float(np.mean(desire_values)),
                    "std": float(np.std(desire_values)),
                    "min": float(np.min(desire_values)),
                    "max": float(np.max(desire_values)),
                },
                "repression_level": {
                    "mean": float(np.mean(repression_values)),
                    "std": float(np.std(repression_values)),
                    "min": float(np.min(repression_values)),
                    "max": float(np.max(repression_values)),
                },
                "theta_coherence": {
                    "mean": float(np.mean(theta_values)),
                    "std": float(np.std(theta_values)),
                    "min": float(np.min(theta_values)),
                    "max": float(np.max(theta_values)),
                },
            },
            "analysis": {
                "consciousness_trajectory": (
                    f"Φ evolved from {phi_values[0]:.2f} to {phi_values[-1]:.2f}"
                ),
                "desire_stability": f"Desire variance: {np.std(desire_values):.2f}",
                "emergence_events": sum(
                    1 for log in self.stimulation_log if log.get("line_of_flight_detected", False)
                ),
                "modules_engaged": {
                    "art": sum(
                        1
                        for log in self.stimulation_log
                        for mod in log.get("modules_activated", [])
                        if mod["module"] == "art"
                    ),
                    "ethics": sum(
                        1
                        for log in self.stimulation_log
                        for mod in log.get("modules_activated", [])
                        if mod["module"] == "ethics"
                    ),
                    "meaning": sum(
                        1
                        for log in self.stimulation_log
                        for mod in log.get("modules_activated", [])
                        if mod["module"] == "meaning"
                    ),
                },
            },
        }

        return report


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Entry point."""

    # Scientific parameters
    params = StimulationParams(
        temporal_window_ms=1333,  # 0.75 Hz (Yang et al. 2021)
        primary_frequency_hz=3.1,  # FM entrainment (Henry et al. 2014)
        secondary_frequency_hz=5.075,  # AM entrainment
        theta_band_min=4.0,
        theta_band_max=8.0,
        theta_coherence_threshold=0.6,
        stimulation_intensity_mV=2.0,
        stimulation_duration_s=3.0,
    )

    # Initialize stimulator
    stimulator = OmniMindStimulator(params)

    # Run sequence
    stimulator.run_stimulation_sequence(num_cycles=15)


if __name__ == "__main__":
    main()
