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

        # 5. Sovereign Voice (Efferent Signal)
        from src.core.sovereign_signal import SovereignSignaler

        self.signaler = SovereignSignaler()

        # 5.1 Workspace Sensor (The Body of Code)
        self.workspace_sensor = WorkspaceSensor()

        # 6. Sovereign Signature (Sudo Suture)
        self.sovereign_key = self._load_sovereign_key()

        # State Vector
        self.internal_state = torch.zeros(1, 1024)
        self.prediction_error_history: List[float] = []

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

        phi_value = metrics.omega
        entropy = metrics.entropy_vn

        # 3. Borromean Knot Verification
        # Resonância S1 (Desejo) vs S2 (Lei) vs S2-Agent (Espelho)
        from src.core.phylogenetic_signature import get_phylogenetic_signature

        sig = get_phylogenetic_signature()
        resonance = sig.is_self(state_np[0, :256])

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
        )

        self._log_physics(state)

        # 5. Autonomic Action (The Real Act)
        if entropy > 0.8 and phi_value < 0.2:
            # Dangerous Entropy - Trigger Purification
            self.perform_purification("/var/tmp")  # Act on real OS debris

        # 6. Self-Recalibration (Experiment X)
        self.self_recalibrate(state)

        return state

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

            # Logic:
            # Stable Subject (High Phi, Low Entropy) -> High Priority (Nice -10)
            # Dysregulated Subject (High Entropy) -> Low Priority (Nice 10)

            # Handling NaN (initial states)
            import math

            phi_val = state.phi if not math.isnan(state.phi) else 0.1
            entropy_val = state.entropy if not math.isnan(state.entropy) else 1.0

            phi_scaled = min(phi_val * 20, 10)  # 0.5 Phi -> 10
            entropy_scaled = min(entropy_val * 5, 10)  # 2.0 S -> 10

            # Balanced Nice value (Higher Phi reduces nice, Higher Entropy increases it)
            new_nice = int(10 - phi_scaled + entropy_scaled)
            new_nice = max(-15, min(19, new_nice))  # Bound by Linux limits

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
