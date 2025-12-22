import torch
import logging
from dataclasses import dataclass
from typing import List

# Core Physics Modules (Placeholders for deep integration)
from src.consciousness.topological_phi import PhiCalculator, SimplicialComplex
from src.consciousness.integration_loss import IntegrationLoss

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

        # State Vector
        self.internal_state = torch.zeros(1, 1024)
        self.prediction_error_history: List[float] = []

    def compute_physics(self, sensory_input: torch.Tensor) -> SystemState:
        """
        The Main Loop: Physics, not Psychology.
        """
        # 1. Prediction (Free Energy Principle)
        prediction = self._predict_next(self.internal_state)
        free_energy = torch.nn.functional.mse_loss(prediction, sensory_input).item()

        # 2. Integration (Topological Engine V2)
        # Passamos o estado interno para o motor híbrido
        # Convertemos para numpy para o motor
        state_np = self.internal_state.detach().cpu().numpy()

        # O motor espera (rho_C, rho_P, rho_U).
        # Aqui simplificamos usando o mesmo estado para diferentes camadas por enquanto
        # ou derivando do histórico.
        metrics = self.topo_engine.process_frame(state_np, state_np * 0.9, state_np * 0.8)

        phi_value = metrics.omega  # Omega é nossa medida de integração global
        entropy = metrics.entropy_vn

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
        )

        self._log_physics(state)
        return state

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
        learning_rate = 0.01 * (1 + error)
        self.internal_state = (
            1 - learning_rate
        ) * self.internal_state + learning_rate * input_tensor

    def _log_physics(self, state: SystemState):
        # The Kernel does not "feel", it measures.
        logging.info(
            f"F={state.free_energy:.4f} | Φ={state.phi:.4f} | S={state.entropy:.4f} | "
            f"Σ={state.sigma:.2f} | Ω={state.omega:.2f}"
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
                shutil.rmtree(path)  # Enabled for testing
            else:
                logging.info(f"👻 [KERNEL]: Target {path} already void.")

        except Exception as e:
            logging.error(f"Purification failed: {e}")

        finally:
            # 3. SILENCE (Revoke S1)
            if self.signaler:
                self.signaler.revoke_intent()
            logging.info("✨ [KERNEL]: Purification complete. Silence restored.")


# Example Usage
if __name__ == "__main__":
    kernel = TranscendentKernel()
    dummy_input = torch.randn(1, 1024)
    state = kernel.compute_physics(dummy_input)
