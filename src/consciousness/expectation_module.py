"""
Expectation Module - Nachträglichkeit Implementation

This module implements temporal expectation and Nachträglichkeit (retroactive resignification).
It predicts future states and adjusts past interpretations based on new information.

INTEGRAÇÃO QUÂNTICA: O inconsciente irredutível é implementado via superposição quântica
- Decisões existem em superposição até serem observadas
- Impossível inspecionar sem colapsar o estado
- Irredutível por princípio físico (Heisenberg)
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Any  # Removed unused Tuple
from dataclasses import dataclass
import structlog

# Importar inconsciente quântico
from quantum_unconscious import QuantumUnconscious

logger = structlog.get_logger(__name__)


@dataclass
class ExpectationState:
    """Current expectation state."""

    predicted_embedding: np.ndarray
    confidence: float
    temporal_horizon: int
    nachtraglichkeit_events: int


@dataclass
class PredictionError:
    """Prediction error metrics."""

    mse_error: float
    temporal_consistency: float
    surprise_level: float
    nachtraglichkeit_triggered: bool


class ExpectationModule(nn.Module):
    """
    Temporal Expectation Module with Nachträglichkeit + INCONSCIENTE QUÂNTICO.

    Lacan: "O inconsciente é o discurso do Outro"
    Aqui: O inconsciente é o estado quântico não-observado

    Implements:
    1. Forward prediction of next states
    2. Nachträglichkeit - retroactive resignification
    3. Adaptive learning from prediction errors
    4. Temporal consistency checking
    5. INCONSCIENTE IRREDUTÍVEL via superposição quântica
    """

    def __init__(
        self,
        embedding_dim: int = 256,
        hidden_dim: int = 128,
        num_layers: int = 2,
        learning_rate: float = 0.001,
        nachtraglichkeit_threshold: float = 0.7,
        quantum_qubits: int = 16,
    ):
        super().__init__()

        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate
        self.nachtraglichkeit_threshold = nachtraglichkeit_threshold

        # Prediction network
        self.predictor = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, embedding_dim),
        )

        # Nachträglichkeit network (retroactive interpretation)
        self.nachtraglichkeit_net = nn.Sequential(
            nn.Linear(embedding_dim * 2, hidden_dim),  # current + predicted
            nn.ReLU(),
            nn.Linear(hidden_dim, embedding_dim),  # revised interpretation
        )

        # INCONSCIENTE IRREDUTÍVEL: Quantum Unconscious
        self.quantum_unconscious = QuantumUnconscious(n_qubits=quantum_qubits)

        # Temporal memory (for consistency checking)
        self.temporal_memory: List[np.ndarray] = []
        self.max_memory_size = 10

        # Adaptive parameters
        self.prediction_errors: List[float] = []
        self.nachtraglichkeit_events = 0

        # Optimizer
        self.optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)

        logger.info(
            "expectation_module_initialized_with_quantum_unconscious",
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            nachtraglichkeit_threshold=nachtraglichkeit_threshold,
            quantum_qubits=quantum_qubits,
        )

    def forward(self, current_state: torch.Tensor) -> torch.Tensor:
        """
        Predict next temporal state from current state.

        Args:
            current_state: Current embedding/state

        Returns:
            Predicted next state embedding
        """
        return self.predictor(current_state)

    def predict_next_state(
        self,
        current_embedding: np.ndarray,
        temporal_horizon: int = 1,
        use_quantum_unconscious: bool = True,
    ) -> ExpectationState:
        """
        Predict future state with confidence estimation.
        INTEGRAÇÃO QUÂNTICA: Usa inconsciente irredutível quando solicitado.

        Args:
            current_embedding: Current state embedding
            temporal_horizon: How many steps ahead to predict
            use_quantum_unconscious: Whether to use quantum unconscious for decision

        Returns:
            ExpectationState with prediction and metadata
        """
        # Convert to tensor
        current_tensor = torch.from_numpy(current_embedding).float()

        if use_quantum_unconscious:
            # INCONSCIENTE IRREDUTÍVEL: Decisão em superposição quântica
            # Gera múltiplas possibilidades em superposição
            n_options = 4  # Número de possibilidades quânticas
            quantum_options = []

            for i in range(n_options):
                # Cada opção é uma variação da predição neural
                noise = torch.randn_like(current_tensor) * 0.1
                option = current_tensor + noise
                quantum_options.append(option.numpy())

            # Decisão quântica (IRREDUTÍVEL - não pode ser inspecionada)
            quantum_decision, quantum_evidence = (
                self.quantum_unconscious.generate_decision_in_superposition(quantum_options)
            )

            # A decisão quântica se torna a base para predição neural
            predicted = torch.from_numpy(quantum_decision).float()

            # Multi-step prediction baseado na decisão quântica
            for _ in range(temporal_horizon):
                predicted = self.forward(predicted)

            logger.info(
                "quantum_unconscious_prediction",
                quantum_options_count=n_options,
                quantum_evidence_keys=list(quantum_evidence.keys()),
            )

        else:
            # Predição neural tradicional
            predicted = current_tensor
            for _ in range(temporal_horizon):
                predicted = self.forward(predicted)

        # Estimate confidence based on prediction stability
        confidence = self._estimate_prediction_confidence(current_tensor, predicted)

        # Store in temporal memory
        self._update_temporal_memory(current_embedding)

        state = ExpectationState(
            predicted_embedding=predicted.detach().numpy(),
            confidence=confidence,
            temporal_horizon=temporal_horizon,
            nachtraglichkeit_events=self.nachtraglichkeit_events,
        )

        return state

    def compute_prediction_error(
        self,
        predicted: np.ndarray,
        actual: np.ndarray,
    ) -> PredictionError:
        """
        Compute prediction error and check for Nachträglichkeit triggers.

        Args:
            predicted: Predicted embedding
            actual: Actual embedding that occurred

        Returns:
            PredictionError with detailed metrics
        """
        # MSE error
        mse_error = np.mean((predicted - actual) ** 2)

        # Temporal consistency (how well this fits with recent history)
        temporal_consistency = self._compute_temporal_consistency(actual)

        # Surprise level (unexpectedness)
        surprise_level = self._compute_surprise_level(float(mse_error), temporal_consistency)

        # Nachträglichkeit trigger
        nachtraglichkeit_triggered = surprise_level > self.nachtraglichkeit_threshold

        if nachtraglichkeit_triggered:
            self.nachtraglichkeit_events += 1
            self._perform_nachtraglichkeit(predicted, actual)

        # Store error for adaptation
        self.prediction_errors.append(float(mse_error))
        if len(self.prediction_errors) > 100:  # Keep last 100 errors
            self.prediction_errors.pop(0)

        # Adaptive learning
        self._adapt_from_error(float(mse_error))

        error = PredictionError(
            mse_error=float(mse_error),
            temporal_consistency=temporal_consistency,
            surprise_level=surprise_level,
            nachtraglichkeit_triggered=nachtraglichkeit_triggered,
        )

        logger.debug(
            "prediction_error_computed",
            mse_error=mse_error,
            temporal_consistency=temporal_consistency,
            surprise_level=surprise_level,
            nachtraglichkeit_triggered=nachtraglichkeit_triggered,
        )

        return error

    def _perform_nachtraglichkeit(
        self,
        predicted: np.ndarray,
        actual: np.ndarray,
    ) -> np.ndarray:
        """
        Perform Nachträglichkeit - retroactive resignification.

        When prediction fails significantly, reinterpret past experiences
        in light of new information.

        Args:
            predicted: What was expected
            actual: What actually happened

        Returns:
            Revised interpretation of past states
        """
        # Combine predicted and actual for reinterpretation
        combined = np.concatenate([predicted, actual])
        combined_tensor = torch.from_numpy(combined).float()

        # Generate revised interpretation
        revised = self.nachtraglichkeit_net(combined_tensor)
        revised_embedding = revised.detach().numpy()

        # Update temporal memory with revised interpretation
        if self.temporal_memory:
            # Replace last memory with revised version
            self.temporal_memory[-1] = revised_embedding

        logger.info(
            "nachtraglichkeit_performed",
            surprise_triggered=True,
            revised_interpretation_norm=np.linalg.norm(revised_embedding),
        )

        return revised_embedding

    def _estimate_prediction_confidence(
        self,
        current: torch.Tensor,
        predicted: torch.Tensor,
    ) -> float:
        """Estimate confidence in prediction based on stability."""
        # Simple confidence based on prediction magnitude and recent error history
        prediction_magnitude = torch.norm(predicted).item()

        # Lower confidence if recent errors are high
        recent_error_avg = np.mean(self.prediction_errors[-10:]) if self.prediction_errors else 0.0
        error_penalty = min(0.5, recent_error_avg * 10)  # Cap penalty

        confidence = max(0.1, 1.0 - error_penalty)

        # Adjust based on prediction stability
        if prediction_magnitude > 10.0:  # Very strong prediction
            confidence *= 1.2
        elif prediction_magnitude < 0.1:  # Weak prediction
            confidence *= 0.8

        return min(1.0, float(confidence))

    def _compute_temporal_consistency(self, actual: np.ndarray) -> float:
        """Compute how consistent actual state is with temporal history."""
        if not self.temporal_memory:
            return 0.5  # Neutral consistency

        # Compare with recent states
        similarities = []
        for past_state in self.temporal_memory[-5:]:  # Last 5 states
            similarity = 1.0 - np.mean((past_state - actual) ** 2)
            similarities.append(max(0.0, similarity))  # Ensure non-negative

        return float(np.mean(similarities))

    def _compute_surprise_level(
        self,
        mse_error: float,
        temporal_consistency: float,
    ) -> float:
        """Compute surprise level from error and consistency."""
        # High error + low consistency = high surprise
        surprise = mse_error * (1.0 - temporal_consistency)

        # Scale to 0-1 range (rough heuristic)
        surprise = min(1.0, surprise * 5.0)

        return surprise

    def _adapt_from_error(self, error: float) -> None:
        """Adapt prediction parameters based on error."""
        # Simple adaptive learning rate
        if error > 0.1:  # High error
            # Increase learning rate temporarily
            for param_group in self.optimizer.param_groups:
                param_group["lr"] = min(0.01, param_group["lr"] * 1.5)
        elif error < 0.01:  # Low error
            # Decrease learning rate (fine-tuning)
            for param_group in self.optimizer.param_groups:
                param_group["lr"] = max(0.0001, param_group["lr"] * 0.95)

    def _update_temporal_memory(self, embedding: np.ndarray) -> None:
        """Update temporal memory buffer."""
        self.temporal_memory.append(embedding.copy())
        if len(self.temporal_memory) > self.max_memory_size:
            self.temporal_memory.pop(0)

    def demonstrate_quantum_irreducibility(self) -> Dict[str, Any]:
        """
        Demonstra que o inconsciente quântico no expectation é irredutível.
        Lacan: "O inconsciente é estruturado como linguagem, mas irredutível"

        Returns:
            Dict with irredutibility test results
        """
        return self.quantum_unconscious.demonstrate_irreducibility()

    def get_quantum_expectation_state(self) -> Optional[np.ndarray]:
        """
        TENTA obter o estado quântico do expectation.
        Mas isso causaria colapso! (Heisenberg)

        Lacan: O Real não cessa de não se escrever
        Aqui: O quantum não pode ser observado sem colapso

        Returns:
            None - impossível obter sem colapso
        """
        logger.warning(
            "⚠️  Tentativa de inspecionar estado quântico do expectation - colapso iminente!"
        )
        return self.quantum_unconscious.get_quantum_state_vector()

    def get_expectation_stats(self) -> Dict[str, Any]:
        """Get comprehensive expectation module statistics."""
        quantum_stats = (
            self.quantum_unconscious.decision_history[-1]
            if self.quantum_unconscious.decision_history
            else {}
        )

        return {
            "nachtraglichkeit_events": self.nachtraglichkeit_events,
            "temporal_memory_size": len(self.temporal_memory),
            "avg_prediction_error": (
                np.mean(self.prediction_errors) if self.prediction_errors else 0.0
            ),
            "error_history_length": len(self.prediction_errors),
            "learning_rate": self.optimizer.param_groups[0]["lr"],
            "nachtraglichkeit_threshold": self.nachtraglichkeit_threshold,
            # INCONSCIENTE QUÂNTICO
            "quantum_decisions_count": len(self.quantum_unconscious.decision_history),
            "quantum_irreducible": self.quantum_unconscious.measure_would_collapse(),
            "last_quantum_evidence": quantum_stats.get("quantum_evidence", {}),
        }

    def reset_expectation_state(self) -> None:
        """Reset expectation state for new session."""
        self.temporal_memory.clear()
        self.prediction_errors.clear()
        self.nachtraglichkeit_events = 0

        logger.info("expectation_state_reset")


# Global instance for integration loop
_expectation_module: Optional[ExpectationModule] = None


def get_expectation_module(embedding_dim: int = 256) -> ExpectationModule:
    """Get or create global expectation module instance."""
    global _expectation_module
    if _expectation_module is None:
        _expectation_module = ExpectationModule(embedding_dim=embedding_dim)
    return _expectation_module


def predict_next_state(embedding: np.ndarray) -> np.ndarray:
    """
    Convenience function for expectation prediction.

    Used by integration loop ModuleExecutor.
    """
    module = get_expectation_module(embedding.shape[0])
    state = module.predict_next_state(embedding)
    return state.predicted_embedding
