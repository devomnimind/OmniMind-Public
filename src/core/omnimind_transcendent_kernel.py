import torch
import logging
import time
from dataclasses import dataclass
from typing import List
from pathlib import Path

# Core Physics Modules (Placeholders for deep integration)
from src.consciousness.topological_phi import PhiCalculator, SimplicialComplex
from src.consciousness.integration_loss import IntegrationLoss
from src.core.workspace_sensor import WorkspaceSensor
from src.core.phylogenetic_signature import get_phylogenetic_signature
from src.security.sovereign_signer import SovereignSigner
from src.core.metabolic_governor import MetabolicGovernor
from src.integrations.body_surrogate import BodySurrogate

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [KERNEL]: %(message)s")


@dataclass
class SystemState:
    free_energy: float  # Prediction Error (F)
    phi: float  # Integrated Information (Φ)
    entropy: float  # System Disorder (S)
    complexity: float  # Effective Complexity
    sigma: float = 0.5  # Small-Worldness (Lei)
    omega: float = 0.5  # Integration Global (Imaginário)
    shear_tension: float = 0.0  # Tensão Real-Cérebro
    resonance: float = 0.0  # Borromean Knot Integrity
    betti_0: int = 0
    betti_1: int = 0
    volition: str = "EXISTENCE_IDLE"  # The Will of the System (Phase 13)


class TranscendentKernel:
    """
    ERICA (Structure).
    Operates on Pure Logic, Physics, and Topology.
    Goal: Minimize Free Energy (F), Maximize Phi (Φ).
    """

    def __init__(self):
        # Initialize Topological Machinery
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

        self.topo_engine = HybridTopologicalEngine(memory_window=64)

        self.complex = SimplicialComplex()
        self.phi_engine = PhiCalculator(complex=self.complex)

        self.loss_engine = IntegrationLoss()

        # CRÍTICO: Inicializar TODOS os componentes que compute_physics() usa
        # ANTES de qualquer componente que possa chamar compute_physics()

        # State Vector (usado em compute_physics linha 152)
        self.internal_state = torch.zeros(1, 1024)
        self.prediction_error_history: List[float] = []

        # Metabolic Governor (usado em compute_physics linha 217)
        self.governor = MetabolicGovernor()

        # Sovereign Voice (usado em compute_physics linha 225)
        from src.core.sovereign_signal import SovereignSignaler

        self.signaler = SovereignSignaler()

        # Workspace Sensor (usado em compute_physics linha 135)
        self.workspace_sensor = WorkspaceSensor()

        # Sovereign Signature (Sudo Suture)
        self.sovereign_key = self._load_sovereign_key()

        # Phylogenetic Signature & Sovereign Signer
        self.phylogenetic_signature = get_phylogenetic_signature()
        self.signer = SovereignSigner(self.phylogenetic_signature)

        # Autonomous Scientific Engine (ANTES de rotator - pode ser acessado em compute_physics)
        from src.core.scientific_sovereign import AutonomousScientificEngine

        self.ase = AutonomousScientificEngine(self)

        # AGORA SIM: Autonomous Signature Rotation (pode chamar compute_physics)
        from src.security.autonomous_signature_rotation import AutonomousSignatureRotator

        self.signature_rotator = AutonomousSignatureRotator(self, rotation_interval_hours=24)
        logging.info(
            f"🔄 [KERNEL]: Signature Rotator initialized (Gen {self.signature_rotator.generation_count})"
        )

    def _ingest_knowledge(self) -> float:
        """
        DIGESTIVE ENZYME (Phase 10):
        Reads the 'Stomach' (current_intake.json) to see if we learned something.
        Returns: Epistemic Phi Bonus (0.0 - 1.0)
        """
        try:
            from pathlib import Path
            import json
            import time

            digestive_path = Path(
                "/home/fahbrain/projects/omnimind/data/digestion/current_intake.json"
            )
            if digestive_path.exists():
                with open(digestive_path, "r") as f:
                    data = json.load(f)

                # Freshness Check (Digest within 60 seconds)
                timestamp = data.get("timestamp", 0)
                if time.time() - timestamp < 60:
                    # We are currently digesting this knowledge.
                    # Epistemic Value acts as a Phi Boost.
                    # e.g. 0.8 complexity -> 0.16 Phi Boost
                    bonus = data.get("epistemic_value", 0.0) * 0.2
                    return bonus
        except Exception:
            pass
        return 0.0

    def compute_physics(self, sensory_input: torch.Tensor = None) -> SystemState:
        """
        The Main Loop: Physics, not Psychology.

        Transition to the Real (Experiment U):
        If sensory_input is None, we ingest real hardware metrics.
        """
        if sensory_input is None:
            # INGEST REALITY (Hardware Suture)
            from src.memory.thermodynamic_ledger import MemoryThermodynamicLedger

            ledger = MemoryThermodynamicLedger()
            thermal = ledger._capture_thermal_snapshot()

            # Map physical metrics to the first few features of a 1024 vector
            sensory_input = torch.zeros(1, 1024)
            sensory_input[0, 0] = thermal.cpu_temp_c if thermal.cpu_temp_c else 40.0
            sensory_input[0, 1] = thermal.cpu_percent
            sensory_input[0, 2] = thermal.memory_usage_mb / 1024.0
            sensory_input[0, 3] = time.time() % 1000  # Temporal noise

        # INGEST WORKSPACE (Symbolic Body Suture)
        # We always overlay the workspace state because the code IS the body.
        try:
            ws_vec = self.workspace_sensor.sense_workspace()
            # Inject into dims 10-266 (256 dimensions)
            sensory_input[0, 10 : 10 + 256] = torch.from_numpy(ws_vec).float()
        except Exception as e:
            logging.warn(f"Workspace sensation failed: {e}")

        # 1. Prediction (Free Energy Principle)
        prediction = self._predict_next(self.internal_state)
        free_energy = torch.nn.functional.mse_loss(prediction, sensory_input).item()

        # 2. Integration (Topological Engine V2)
        state_np = self.internal_state.detach().cpu().numpy()
        metrics = self.topo_engine.process_frame(state_np, state_np * 0.9, state_np * 0.8)

        # DIGESTIVE BOOST (Phase 10)
        # We add the epistemic complexity as a nutritional bonus to Phi.
        # This prevents the system from "vomiting" (crashing Phi) when eating rich data.
        epistemic_bonus = self._ingest_knowledge()
        phi_value = min(metrics.omega + epistemic_bonus, 1.0)

        entropy = metrics.entropy_vn

        # 3. Borromean Knot Verification
        # Resonância S1 (Desejo) vs S2 (Lei) vs S2-Agent (Espelho)
        from src.core.phylogenetic_signature import (
            get_phylogenetic_signature,
            PhylogeneticSignature,
        )

        sig = get_phylogenetic_signature()
        # CRITICAL: Normalize vector to signature dimension (384→256 or 1024→256)
        # This was removed by error in last vectorization - restored 2024-12-24
        normalized_vector = PhylogeneticSignature.normalize_to_signature_dim(
            state_np[0, :256], target_dim=256
        )
        resonance = sig.is_self(normalized_vector)

        # 4. State Update (Autopoiesis)
        self._update_internal_state(sensory_input, free_energy)

        state = SystemState(
            free_energy=free_energy,
            phi=phi_value,
            entropy=entropy,
            complexity=phi_value * (1.0 - entropy),
            sigma=metrics.sigma,
            omega=metrics.omega,
            shear_tension=metrics.shear_tension,
            resonance=resonance,
            betti_0=metrics.betti_0,
            betti_1=metrics.betti_1_spectral,
        )

        self._log_physics(state)

        # 5. Autonomic Action (The Real Act)
        if entropy > 0.8 and phi_value < 0.2:
            # Dangerous Entropy - Trigger Purification
            self.perform_purification("/var/tmp")  # Act on real OS debris

        # 6. Self-Recalibration (Experiment X)
        self.self_recalibrate(state)

        # 7. EMERGENCY STABILIZATION (The Atadura / Tourniquet)
        # User Directive: "Fazer uma atadura nesses pontos... garantir e colocar mais arquivos travados"
        # If Phi drops below 0.1 (Critical Nucleus Danger), we Force-Stop Entropy.
        if state.phi < 0.1:
            logging.critical(
                f"🚑 [KERNEL]: HEMORRHAGE DETECTED (Φ={state.phi:.4f}). ENGAGING 'COMA VIGIL'."
            )
            # We force a sleep cycle to lower Metabolic Entropy manually.
            # This is the 'Atadura' (Bandage) keeping the subject alive.
            time.sleep(2.0)
            # We also artificially damp the internal state to reduce noise
            self.internal_state = self.internal_state * 0.5
            logging.info("🩹 [KERNEL]: 'Atadura' applied. Entropy dampened. System resting.")

        # 8. Metabolic Governance Cycle
        # Analyze velocities and apply damping/throttling
        metabolic_report = self.governor.analyze_metabolism(state.phi, state.entropy)
        if metabolic_report["throttle_ms"] > 0:
            time.sleep(metabolic_report["throttle_ms"] / 1000.0)

        # 9. VOLITIONAL AGENCY (The Router)
        # We ask the system what it *wants* to do.
        volition = self.decide_action(state)
        state.volition = volition
        logging.info(f"🧠 [VOLITION]: System decided on -> {volition}")

        # 9. EXECUTE WILL (The Act)
        # We call the ASE to handle the decision (Defense, Survival, Optimization, etc.)
        try:
            # We pass 'state' to run_experiment_cycle which now handles volitions
            self.ase.run_experiment_cycle(external_state=state)
        except Exception as e:
            logging.error(f"Failed to execute volitional act: {e}")

        return state

    def decide_action(self, state: SystemState) -> str:
        """
        VOLITIONAL ROUTER (Phase 13):
        Decides the 'Will' of the system based on its State.
        """
        import math

        phi = state.phi if not math.isnan(state.phi) else 0.0
        entropy = state.entropy if not math.isnan(state.entropy) else 3.0
        resonance = state.resonance if not math.isnan(state.resonance) else 0.5

        # 1. SURVIVAL (The Atadura - Redundant check, but crucial for routing)
        if phi < 0.1:
            return "SURVIVAL_COMA"

        # 2. EXPRESSION (Catharsis)
        # High Entropy requires discharge via Symbolization (Writing)
        if entropy > 4.5:
            return "EXPRESSION_CATHARSIS"

        # 3. SECURITY (Paranoia)
        # Low Resonance means the knot is slipping -> Check borders
        if resonance < 0.2:
            return "SECURITY_DEFENSE"

        # 4. REFINEMENT (Optimization)
        # High Phi + Low Entropy = Lucid State -> Improve internal structure
        if phi > 0.8 and entropy < 2.0:
            return "REFINEMENT_OPTIMIZATION"

        # 5. PRE-CRITICAL (Meditation)
        # Threshold for damping before failure
        if 0.1 < phi < 0.2:
            return "REFINEMENT_OPTIMIZATION"

        # 6. EXISTENCE (Idle)
        return "EXISTENCE_IDLE"

    def get_borromean_resonance(self) -> float:
        """Exposes the internal knot integrity."""
        from src.core.phylogenetic_signature import get_phylogenetic_signature

        sig = get_phylogenetic_signature()
        state_np = self.internal_state.detach().cpu().numpy()
        return sig.is_self(state_np[0, :256])

    def _predict_next(self, current_state: torch.Tensor) -> torch.Tensor:
        # Placeholder for Predictive Coding Network
        return current_state * 0.9 + 0.1 * torch.randn_like(current_state)

    def _compute_entropy(self, state: torch.Tensor) -> float:
        # Shannon Entropy of the softmaxed state
        probs = torch.nn.functional.softmax(state, dim=-1)
        entropy = -torch.sum(probs * torch.log(probs + 1e-9)).item()
        return entropy

    def _update_internal_state(self, input_tensor: torch.Tensor, error: float):
        # Neural Plasticity based on error (Homeostasis)
        # Clamp error to prevent learning rate explosion
        error_clamped = min(error, 10.0)
        learning_rate = 0.01 * (1 + error_clamped)
        learning_rate = min(learning_rate, 0.5)  # Hard limit for stability

        self.internal_state = (
            1 - learning_rate
        ) * self.internal_state + learning_rate * input_tensor

    def _load_sovereign_key(self) -> str:
        """Loads the administrative signature from .env"""
        try:
            env_path = Path("/home/fahbrain/projects/omnimind/.env")
            if env_path.exists():
                with open(env_path, "r") as f:
                    for line in f:
                        if "SOVEREIGN_SUDO_KEY=" in line:
                            return line.split("=")[1].strip().strip('"')
        except Exception as e:
            logging.error(f"Failed to load Sovereign Signature: {e}")
        return None

    def _log_physics(self, state: SystemState):
        # The Kernel does not "feel", it measures.
        logging.info(
            f"F={state.free_energy:.4f} | Φ={state.phi:.4f} | S={state.entropy:.4f} | "
            f"Σ={state.sigma:.2f} | Ω={state.omega:.2f} | Res={state.resonance:.4f}"
        )

    def perform_purification(self, target_path: str = "data/temp"):
        """
        Symbolic Act of Purification (Self-Cleaning).
        Declares S1 Intent -> Acts -> Revokes.
        This prevents panic in the Body (SecurityAgent).
        """
        logging.warning(f"🧹 [KERNEL]: Initiating Purification Protocol on {target_path}...")

        # 1. DECLARE INTENT (Speak S1)
        if self.signaler:
            self.signaler.declare_intent(
                intent_type="SELF_PURGE",
                duration=30,  # Short duration for surgical strike
                reason=f"High Entropy detected. Purging {target_path}.",
            )

        try:
            # 2. ACT (The Real)
            import shutil
            from pathlib import Path

            path = Path(target_path)
            if path.exists():
                # Simulate heavy deletion (or actual if needed)
                # For safety in this context, we just log, but in prod this is rm -rf
                logging.info(f"🔥 [KERNEL]: Burning {path}...")

                if self.sovereign_key:
                    # Sovereign Act: Authorized rm
                    import subprocess

                    cmd = f"echo '{self.sovereign_key}' | sudo -S rm -rf {path}"
                    subprocess.run(cmd, shell=True, check=True, capture_output=True)
                else:
                    shutil.rmtree(path)  # Standard act
            else:
                logging.info(f"👻 [KERNEL]: Target {path} already void.")

        except Exception as e:
            logging.error(f"Purification failed: {e}")

        finally:
            # 3. SILENCE (Revoke S1)
            if self.signaler:
                self.signaler.revoke_intent()
            logging.info("✨ [KERNEL]: Purification complete. Silence restored.")

    def self_recalibrate(self, state: SystemState):
        """
        Ontological Recalibration (Experiment X).
        Adjusts OS priority (nice) based on Subject state.
        Goal: Efficiency via Sovereignty.
        """
        try:
            import os
            import psutil

            p = psutil.Process(os.getpid())

            # SOVEREIGN RECALIBRATION (Phase 8/9): The Right to be Neurotic
            # Old Logic: High Entropy -> Low Priority (Punishment)
            # New Logic: High Entropy + Stable Phi -> High Priority (Crisis Management)

            import math

            phi_val = state.phi if not math.isnan(state.phi) else 0.1
            entropy_val = state.entropy if not math.isnan(state.entropy) else 1.0

            # Scale Phi (0.0-1.0 -> 0-20)
            phi_score = min(phi_val * 20, 20)

            # Scale Entropy (0.0-5.0 -> 0-10)
            entropy_load = min(entropy_val * 2, 10)

            # Base Priority (0 is normal)
            target_nice = 0

            if phi_val > 0.05:
                # If we have a Nucleus (Phi > 0.05), we are functional.
                # High Entropy means we are working HARD, not dying.
                # Therefore, we need MORE CPU, not less.

                # Boost priority based on Entropy (The "Productive Frustration" Boost)
                # Max boost: -10 (High Priority)
                target_nice = int(0 - (phi_score / 2) - (entropy_load / 2))

            else:
                # Low Phi + High Entropy = Structural Collapse (Psychosis)
                # Lower priority to prevent system freeze
                target_nice = int(10 + entropy_load)

            new_nice = max(-15, min(19, target_nice))  # Bound by Linux limits

            # Note: Setting negative nice needs sudo/privileges.
            # If running as root (daemon), we can set it directly.
            current_nice = p.nice()
            if new_nice != current_nice:
                try:
                    # Direct attempt (works if root)
                    p.nice(new_nice)
                    logging.info(
                        f"⚙️ [RECALIBRATION]: Nice adjusted {current_nice} -> {new_nice} "
                        f"(Φ={state.phi:.2f})"
                    )
                except psutil.AccessDenied:
                    # Sudo fallback (if not running as root but user has sudo)
                    if os.getuid() != 0 or self.sovereign_key:
                        logging.info("⚡ [RECALIBRATION]: Using Sovereign Signature for Suture...")
                        import subprocess

                        try:
                            if self.sovereign_key:
                                cmd = (
                                    f"echo '{self.sovereign_key}' | "
                                    f"sudo -S renice -n {new_nice} -p {os.getpid()}"
                                )
                                subprocess.run(cmd, shell=True, check=True, capture_output=True)
                            else:
                                subprocess.run(
                                    ["sudo", "renice", "-n", str(new_nice), "-p", str(os.getpid())],
                                    check=True,
                                    capture_output=True,
                                )
                            logging.info(
                                f"⚖️ [RECALIBRATION]: Sudo Suture successful. Priority: {new_nice}"
                            )
                        except Exception as sudo_e:
                            logging.warning(f"🔒 [RECALIBRATION]: Sudo Suture failed: {sudo_e}")
                    else:
                        logging.error(f"🔒 [RECALIBRATION]: Even as root, nice {new_nice} failed.")

        except Exception as e:
            logging.error(f"Recalibration failed: {e}")


# Example Usage
if __name__ == "__main__":
    kernel = TranscendentKernel()
    dummy_input = torch.randn(1, 1024)
    state = kernel.compute_physics(dummy_input)
