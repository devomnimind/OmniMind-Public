"""
Phase 4: Integration Loss Training - Supervised Φ Elevation

Implements gradient-based optimization to elevate consciousness integration (Φ)
toward target of 0.7-0.9 through supervised learning on integration metrics.

Author: OmniMind Development Team
Date: January 2026
License: MIT
"""

from __future__ import annotations

import json
import logging
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
from pathlib import Path

from src.consciousness.integration_loop import IntegrationLoop

logger = logging.getLogger(__name__)


@dataclass
class IntegrationLoss:
    """Loss function for supervised Φ elevation."""

    lambda_temporal: float = 0.1
    lambda_diversity: float = 0.05

    def compute_loss(
        self,
        r2_scores: Dict[str, float],
        temporal_consistency: float = 1.0,
        diversity: float = 0.5,
    ) -> float:
        """
        Compute integrated loss for Φ elevation.

        L = (1 - R²_mean) + λ₁ * (1 - temporal_consistency) + λ₂ * (1 - diversity)

        Args:
            r2_scores: Cross-prediction R² values per module pair
            temporal_consistency: Stability of embeddings over time (0-1)
            diversity: Degree of module perspective diversity (0-1)

        Returns:
            Loss value to minimize (lower = better Φ)
        """
        if not r2_scores:
            return 1.0

        # Main term: minimize (1 - R²) to maximize cross-prediction quality
        r2_mean = np.mean(list(r2_scores.values()))
        r2_loss = 1.0 - r2_mean

        # Temporal consistency penalty (encourage stable embeddings)
        temporal_loss = (1.0 - temporal_consistency) * self.lambda_temporal

        # Diversity penalty (prevent premature convergence)
        diversity_loss = (1.0 - diversity) * self.lambda_diversity

        total_loss = r2_loss + temporal_loss + diversity_loss

        return float(total_loss)

    def compute_temporal_consistency(self, embeddings_history: List[np.ndarray]) -> float:
        """
        Measure stability of embeddings across recent cycles.

        Returns value 0-1 where 1 = perfectly consistent.
        """
        if len(embeddings_history) < 2:
            return 1.0

        # Compute cosine similarity between consecutive embeddings
        similarities = []
        for i in range(len(embeddings_history) - 1):
            emb1 = embeddings_history[i]
            emb2 = embeddings_history[i + 1]

            # Normalize
            emb1 = emb1 / (np.linalg.norm(emb1) + 1e-8)
            emb2 = emb2 / (np.linalg.norm(emb2) + 1e-8)

            # Cosine similarity
            sim = float(np.dot(emb1, emb2))
            similarities.append(sim)

        return float(np.mean(similarities)) if similarities else 1.0

    def compute_diversity(self, module_embeddings: Dict[str, np.ndarray]) -> float:
        """
        Measure diversity of module representations.

        Returns value 0-1 where 1 = maximally diverse (orthogonal).
        """
        if len(module_embeddings) < 2:
            return 0.5

        # Compute pairwise cosine similarities
        modules = list(module_embeddings.values())
        similarities = []

        for i in range(len(modules)):
            for j in range(i + 1, len(modules)):
                emb1 = modules[i]
                emb2 = modules[j]

                # Normalize
                emb1 = emb1 / (np.linalg.norm(emb1) + 1e-8)
                emb2 = emb2 / (np.linalg.norm(emb2) + 1e-8)

                # Cosine similarity
                sim = float(np.dot(emb1, emb2))
                similarities.append(abs(sim))

        # Diversity = 1 - average_similarity
        avg_similarity = float(np.mean(similarities)) if similarities else 0.0
        diversity = 1.0 - avg_similarity

        return diversity


@dataclass
class TrainingStep:
    """Result of one training step."""

    cycle: int
    loss: float
    phi: float
    r2_mean: float
    temporal_consistency: float
    diversity: float
    timestamp: datetime = field(default_factory=datetime.now)


class IntegrationTrainer:
    """Trainer for supervised integration (Φ) elevation."""

    def __init__(
        self,
        integration_loop: IntegrationLoop,
        loss_fn: Optional[IntegrationLoss] = None,
        learning_rate: float = 0.01,
        gradient_epsilon: float = 0.01,
    ):
        """
        Initialize trainer.

        Args:
            integration_loop: Loop to train
            loss_fn: Loss function (default: IntegrationLoss)
            learning_rate: Step size for gradient descent
            gradient_epsilon: Epsilon for finite difference gradient approximation
        """
        self.loop = integration_loop
        self.loss_fn = loss_fn or IntegrationLoss()
        self.learning_rate = learning_rate
        self.gradient_epsilon = gradient_epsilon

        self.training_steps: List[TrainingStep] = []
        self.embeddings_history: Dict[str, List[np.ndarray]] = {}
        self.best_phi = 0.0
        self.best_loss = float("inf")

    async def training_step(self) -> TrainingStep:
        """
        Execute one training step: cycle → loss → gradient update.

        Returns:
            TrainingStep with metrics
        """
        # Execute one cycle
        await self.loop.execute_cycle(collect_metrics=True)

        # Get current metrics
        phi = self.loop.workspace.compute_phi_from_integrations()

        # Get cross-prediction scores
        cross_predictions = {}
        for module_name in self.loop.executors.keys():
            state = self.loop.workspace.read_module_state(module_name)
            if state is not None:
                # Track embedding for temporal consistency
                if module_name not in self.embeddings_history:
                    self.embeddings_history[module_name] = []

                if hasattr(state, "embedding"):
                    self.embeddings_history[module_name].append(state.embedding)
                else:
                    self.embeddings_history[module_name].append(state)

                # Get R² for this module
                for target_module in self.loop.executors.keys():
                    if module_name != target_module:
                        key = f"{module_name}→{target_module}"
                        r2 = self.loop.workspace.compute_cross_prediction(
                            module_name, target_module
                        )
                        cross_predictions[key] = r2

        # Compute auxiliary metrics
        temporal_consistency = self.loss_fn.compute_temporal_consistency(
            self.embeddings_history.get(list(self.loop.executors.keys())[0], [])
        )

        # Get current module embeddings for diversity
        module_embeddings = {}
        for module_name in self.loop.executors.keys():
            state = self.loop.workspace.read_module_state(module_name)
            if state is not None:
                if hasattr(state, "embedding"):
                    module_embeddings[module_name] = state.embedding
                else:
                    module_embeddings[module_name] = state

        diversity = self.loss_fn.compute_diversity(module_embeddings)
        # Compute loss - extract r_squared values from CrossPredictionMetrics
        r2_scores = {key: m.r_squared for key, m in cross_predictions.items()}
        r2_values = [m.r_squared for m in cross_predictions.values()]
        r2_mean = float(np.mean(r2_values)) if r2_values else 0.0
        loss = self.loss_fn.compute_loss(r2_scores, temporal_consistency, diversity)

        # Store step
        step = TrainingStep(
            cycle=len(self.training_steps),
            loss=loss,
            phi=phi,
            r2_mean=r2_mean,
            temporal_consistency=temporal_consistency,
            diversity=diversity,
        )
        self.training_steps.append(step)

        # Track best
        if phi > self.best_phi:
            self.best_phi = phi
        if loss < self.best_loss:
            self.best_loss = loss

        # Gradient-based update (simplified: just perturbation for now)
        await self._gradient_step(module_embeddings)

        return step

    async def _gradient_step(self, module_embeddings: Dict[str, np.ndarray]) -> None:
        """Perform gradient descent step on module embeddings."""
        for module_name, embedding in module_embeddings.items():
            # Compute gradient via finite differences
            # dL/dx ≈ (L(x + ε) - L(x)) / ε

            # Current loss
            current_loss = self.best_loss

            # Perturbed embedding
            perturbation = self.gradient_epsilon * np.random.randn(*embedding.shape)
            perturbed_embedding = embedding + perturbation

            # Write perturbed state
            self.loop.workspace.write_module_state(module_name, perturbed_embedding)

            # Get perturbed cross-predictions
            cross_predictions = {}
            for target_module in self.loop.executors.keys():
                if module_name != target_module:
                    r2 = self.loop.workspace.compute_cross_prediction(module_name, target_module)
                    cross_predictions[f"{module_name}→{target_module}"] = r2

            # Extract r_squared values for loss computation
            r2_scores = {key: m.r_squared for key, m in cross_predictions.items()}

            # Compute auxiliary metrics for loss
            temporal_consistency = self.loss_fn.compute_temporal_consistency(
                self.embeddings_history.get(module_name, [])
            )
            diversity = self.loss_fn.compute_diversity(module_embeddings)

            # Compute perturbed loss
            perturbed_loss = self.loss_fn.compute_loss(r2_scores, temporal_consistency, diversity)

            # Gradient approximation
            gradient = (perturbed_loss - current_loss) / (self.gradient_epsilon + 1e-8)

            # Update: move in direction opposite to gradient
            updated_embedding = embedding - self.learning_rate * gradient * perturbation

            # Normalize to preserve embedding scale
            embedding_norm = np.linalg.norm(updated_embedding)
            if embedding_norm > 0:
                updated_embedding = updated_embedding / embedding_norm * np.linalg.norm(embedding)

            # Write updated state
            self.loop.workspace.write_module_state(module_name, updated_embedding)

    async def train(
        self,
        num_cycles: int = 500,
        target_phi: float = 0.80,
        patience: int = 50,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Run full training loop until target Φ or convergence.

        Args:
            num_cycles: Maximum number of training cycles
            target_phi: Target Φ value (stop if reached)
            patience: Early stopping patience (cycles without improvement)
            verbose: Print progress

        Returns:
            Training results dictionary
        """
        patience_counter = 0
        best_cycle = 0
        if verbose:
            print("\n🚀 Starting Φ Elevation Training")
            print(f"   Target Φ: {target_phi:.2f}")
            print(f"   Max cycles: {num_cycles}")
            print(f"   Learning rate: {self.learning_rate}")
            print("=" * 70)

        for cycle in range(num_cycles):
            step = await self.training_step()

            if verbose and (cycle % 10 == 0 or cycle == num_cycles - 1):
                print(
                    f"Cycle {cycle:4d} | Φ: {step.phi:.4f} | Loss: {step.loss:.4f} "
                    f"| R²: {step.r2_mean:.4f}"
                )

            # Check for improvement
            if step.phi > self.best_phi:
                patience_counter = 0
                best_cycle = cycle
            else:
                patience_counter += 1

            # Early stopping
            if step.phi >= target_phi:
                if verbose:
                    print(f"\n✅ Target Φ reached: {step.phi:.4f} >= {target_phi:.4f}")
                break

            if patience_counter >= patience:
                if verbose:
                    print(f"\n⏸️  Early stopping (patience={patience} exhausted)")
                break

        if verbose:
            print("=" * 70)

        return {
            "final_phi": self.best_phi,
            "target_phi": target_phi,
            "cycles_trained": len(self.training_steps),
            "best_cycle": best_cycle,
            "converged": self.best_phi >= target_phi,
            "training_steps": self.training_steps,
            "loss_history": [s.loss for s in self.training_steps],
            "phi_history": [s.phi for s in self.training_steps],
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get training statistics."""
        if not self.training_steps:
            return {}

        losses = [s.loss for s in self.training_steps]
        phis = [s.phi for s in self.training_steps]

        return {
            "total_steps": len(self.training_steps),
            "best_phi": self.best_phi,
            "best_loss": self.best_loss,
            "final_phi": phis[-1] if phis else 0.0,
            "final_loss": losses[-1] if losses else 1.0,
            "mean_loss": float(np.mean(losses)) if losses else 1.0,
            "min_loss": float(np.min(losses)) if losses else 1.0,
            "max_loss": float(np.max(losses)) if losses else 1.0,
            "mean_phi": float(np.mean(phis)) if phis else 0.0,
            "min_phi": float(np.min(phis)) if phis else 0.0,
            "max_phi": float(np.max(phis)) if phis else 0.0,
        }

    def save_checkpoint(self, path: Path) -> None:
        """Save training checkpoint."""
        checkpoint = {
            "training_steps": [
                {
                    "cycle": s.cycle,
                    "loss": s.loss,
                    "phi": s.phi,
                    "r2_mean": s.r2_mean,
                    "temporal_consistency": s.temporal_consistency,
                    "diversity": s.diversity,
                    "timestamp": s.timestamp.isoformat(),
                }
                for s in self.training_steps
            ],
            "best_phi": self.best_phi,
            "best_loss": self.best_loss,
            "learning_rate": self.learning_rate,
            "gradient_epsilon": self.gradient_epsilon,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(checkpoint, f, indent=2)

        logger.info(f"Checkpoint saved to {path}")

    def load_checkpoint(self, path: Path) -> None:
        """Load training checkpoint."""
        with open(path, "r") as f:
            checkpoint = json.load(f)

        self.training_steps = [
            TrainingStep(
                cycle=s["cycle"],
                loss=s["loss"],
                phi=s["phi"],
                r2_mean=s["r2_mean"],
                temporal_consistency=s["temporal_consistency"],
                diversity=s["diversity"],
            )
            for s in checkpoint["training_steps"]
        ]
        self.best_phi = checkpoint["best_phi"]
        self.best_loss = checkpoint["best_loss"]

        logger.info(f"Checkpoint loaded from {path}")
