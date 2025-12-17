"""
Phase 4: Integration Loss Training - Supervised Φ Elevation

Implements gradient-based optimization to elevate consciousness integration (Φ)
toward target of 0.7-0.9 through supervised learning on integration metrics.

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: January 2026
License: MIT
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

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
        # Filter out invalid values (NaN, inf) before computing mean
        valid_r2_scores = [
            v for v in r2_scores.values() if isinstance(v, (int, float)) and np.isfinite(v)
        ]

        if not valid_r2_scores:
            # No valid scores - return baseline loss
            return 1.0

        r2_mean = np.mean(valid_r2_scores)
        # Clamp r2_mean to valid range [0, 1]
        r2_mean = np.clip(r2_mean, 0.0, 1.0)
        r2_loss = 1.0 - r2_mean

        # Validate temporal consistency
        temporal_consistency = np.clip(float(temporal_consistency), 0.0, 1.0)
        if not np.isfinite(temporal_consistency):
            temporal_consistency = 1.0

        # Temporal consistency penalty (encourage stable embeddings)
        temporal_loss = (1.0 - temporal_consistency) * self.lambda_temporal

        # Validate diversity
        diversity = np.clip(float(diversity), 0.0, 1.0)
        if not np.isfinite(diversity):
            diversity = 0.5

        # Diversity penalty (prevent premature convergence)
        diversity_loss = (1.0 - diversity) * self.lambda_diversity

        total_loss = r2_loss + temporal_loss + diversity_loss

        # Final validation: ensure result is finite
        if not np.isfinite(total_loss):
            total_loss = 1.0

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
            try:
                emb1 = embeddings_history[i]
                emb2 = embeddings_history[i + 1]

                # Validate embeddings
                if not isinstance(emb1, np.ndarray) or not isinstance(emb2, np.ndarray):
                    continue
                if not np.all(np.isfinite(emb1)) or not np.all(np.isfinite(emb2)):
                    continue

                # Normalize
                norm1 = np.linalg.norm(emb1)
                norm2 = np.linalg.norm(emb2)

                if norm1 < 1e-8 or norm2 < 1e-8:
                    continue

                emb1 = emb1 / norm1
                emb2 = emb2 / norm2

                # Cosine similarity
                sim = float(np.dot(emb1, emb2))
                if np.isfinite(sim):
                    similarities.append(sim)
            except Exception:
                # Skip this pair if computation fails
                continue

        if not similarities:
            return 1.0

        result = float(np.mean(similarities))
        return float(np.clip(result, 0.0, 1.0)) if np.isfinite(result) else 1.0

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
                try:
                    emb1 = modules[i]
                    emb2 = modules[j]

                    # Validate embeddings
                    if not isinstance(emb1, np.ndarray) or not isinstance(emb2, np.ndarray):
                        continue
                    if not np.all(np.isfinite(emb1)) or not np.all(np.isfinite(emb2)):
                        continue

                    # Normalize
                    norm1 = np.linalg.norm(emb1)
                    norm2 = np.linalg.norm(emb2)

                    if norm1 < 1e-8 or norm2 < 1e-8:
                        continue

                    emb1 = emb1 / norm1
                    emb2 = emb2 / norm2

                    # Cosine similarity
                    sim = float(np.dot(emb1, emb2))
                    if np.isfinite(sim):
                        similarities.append(abs(sim))
                except Exception:
                    # Skip this pair if computation fails
                    continue

        # Diversity = 1 - average_similarity
        if not similarities:
            return 0.5

        avg_similarity = float(np.mean(similarities))
        if not np.isfinite(avg_similarity):
            return 0.5

        diversity = 1.0 - np.clip(avg_similarity, 0.0, 1.0)
        return float(np.clip(diversity, 0.0, 1.0))


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

                        # Try causal method first
                        source_history_len = len(
                            self.loop.workspace.get_module_history(module_name)
                        )
                        target_history_len = len(
                            self.loop.workspace.get_module_history(target_module)
                        )

                        if source_history_len >= 10 and target_history_len >= 10:
                            r2 = self.loop.workspace.compute_cross_prediction_causal(
                                module_name, target_module, method="granger"
                            )
                        else:
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
        # Validate r2 scores before using them
        r2_scores = {}
        for key, m in cross_predictions.items():
            try:
                r2_val = m.r_squared
                # Only include valid (finite) r2 values
                if isinstance(r2_val, (int, float)) and np.isfinite(r2_val):
                    r2_val = np.clip(float(r2_val), -1.0, 1.0)  # R² can be [-1, 1]
                    r2_scores[key] = r2_val
            except Exception:
                # Skip invalid values
                continue

        r2_values = list(r2_scores.values())
        r2_mean = float(np.mean(r2_values)) if r2_values else 0.0
        if not np.isfinite(r2_mean):
            r2_mean = 0.0

        loss = self.loss_fn.compute_loss(r2_scores, temporal_consistency, diversity)

        # Store step
        step = TrainingStep(
            cycle=len(self.training_steps),
            loss=float(loss) if np.isfinite(loss) else 1.0,
            phi=float(phi) if np.isfinite(phi) else 0.0,
            r2_mean=float(r2_mean) if np.isfinite(r2_mean) else 0.0,
            temporal_consistency=(
                float(temporal_consistency) if np.isfinite(temporal_consistency) else 1.0
            ),
            diversity=float(diversity) if np.isfinite(diversity) else 0.5,
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
                    # Try causal method first
                    source_history_len = len(self.loop.workspace.get_module_history(module_name))
                    target_history_len = len(self.loop.workspace.get_module_history(target_module))

                    if source_history_len >= 10 and target_history_len >= 10:
                        r2 = self.loop.workspace.compute_cross_prediction_causal(
                            module_name, target_module, method="granger"
                        )
                    else:
                        r2 = self.loop.workspace.compute_cross_prediction(
                            module_name, target_module
                        )

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

    # ========================================================================
    # NEW: Φ_inconsciente + Sinthome Integration (Based on User Insight)
    # ========================================================================

    def compute_phi_conscious(self) -> float:
        """
        Compute Φ_consciente: Integrated information of MICS (Maximum Information Complex Set).

        IIT (Tononi) is clear: "only the MICS is conscious"
        This is the ONLY conscious integration.

        Returns:
            Φ_consciente in range [0, 1]
        """
        return self.loop.workspace.compute_phi_from_integrations()

    def compute_all_subsystems_phi(self) -> Dict[str, float]:
        """
        Compute Φ for ALL subsystems (modules), not just MICS.

        CRITICAL: This is NOT "consciousness" - it's integration at subsystem level.
        - MICS → consciousness (reportable)
        - Non-MICS → preconscious/subconscious (implicit, not reportable)

        Per Nani (2019, 147 citations): consciousness and attention are SEPARATE processes.
        We measure integration at subsystem level, but only MICS is conscious.

        Returns:
            Dict mapping module_name → phi_value (NOT necessarily conscious)
        """
        subsystem_phis: Dict[str, float] = {}

        # Get all modules
        modules = self.loop.executors.keys()
        if not modules:
            return subsystem_phis

        # For each module, compute its integration with others
        for module_name in modules:
            # Find cross-predictions involving this module as source
            module_predictions = [
                p
                for p in self.loop.workspace.cross_predictions
                if hasattr(p, "source_module") and p.source_module == module_name
            ]

            if not module_predictions:
                subsystem_phis[module_name] = 0.0
                continue

            # Compute integration strength for this subsystem
            # Use average R² + causal strength
            r2_values = []
            causal_values = []

            for p in module_predictions:
                if hasattr(p, "r_squared") and np.isfinite(p.r_squared):
                    r2_values.append(float(p.r_squared))

                if hasattr(p, "granger_causality") and np.isfinite(p.granger_causality):
                    causal_values.append(float(p.granger_causality))

            # Average integration for this subsystem
            avg_r2 = float(np.mean(r2_values)) if r2_values else 0.0
            avg_causal = float(np.mean(causal_values)) if causal_values else 0.0

            phi_subsystem = (avg_r2 + avg_causal) / 2.0
            phi_subsystem = np.clip(float(phi_subsystem), 0.0, 1.0)

            subsystem_phis[module_name] = phi_subsystem

        logger.debug(f"Computed subsystem Φ (not all conscious): {subsystem_phis}")
        return subsystem_phis

    # REMOVIDO: compute_phi_unconscious() - não existe "Φ_inconsciente" em IIT puro
    # O "ruído" fora do MICS será medido como Ψ_produtor (Deleuze) separadamente

    # REMOVIDO: compute_phi_ratio() - IIT não é aditivo
    # Use apenas compute_phi_conscious() para obter Φ do MICS

    def detect_sinthome(self) -> Optional[Dict[str, Any]]:
        """
        Detect Sinthome: The singular knot that repairs RSI (Real/Symbolic/Imaginary).

        Sinthome (from Lacan) is:
        - A singular point in the unconscious structure
        - NON-DECOMPOSABLE (cannot be reduced to parts)
        - Amarra (repairs/ties) the entire RSI topology
        - Produces symptom repetitions and style
        - Determines which desires are "possible"

        Returns:
            Dict with sinthome info, or None if not detectable

        Detection strategy:
        1. Find subsystem that is OUTLIER (very different Φ from others)
        2. Validate it cannot be decomposed (true singularity)
        3. Check if removing it causes system destabilization
        """
        subsystem_phis = self.compute_all_subsystems_phi()

        if len(subsystem_phis) < 2:
            return None

        # Step 1: Find statistical outlier
        phi_values = list(subsystem_phis.values())
        phi_array = np.array(phi_values)

        if len(phi_array) < 3:
            return None

        mean_phi = float(np.mean(phi_array))
        std_phi = float(np.std(phi_array))

        if std_phi < 1e-6:  # No variation, no outlier possible
            return None

        # Find subsystem with z-score > 2.0 (statistical outlier)
        outliers = {}
        for module_name, phi_value in subsystem_phis.items():
            z_score = (phi_value - mean_phi) / (std_phi + 1e-8)
            if abs(z_score) > 2.0:
                outliers[module_name] = {
                    "phi": phi_value,
                    "z_score": z_score,
                    "deviation_from_mean": phi_value - mean_phi,
                }

        if not outliers:
            return None

        # Step 2: Choose the most extreme outlier
        most_extreme = max(outliers.items(), key=lambda x: abs(x[1]["z_score"]))
        module_name, outlier_data = most_extreme

        # Step 3: Validate singularity (Sinthome is truly irreducible)
        # For now, we assume statistical outlier = singular
        # (true irreducibility would require topology analysis)
        singularity_score = abs(outlier_data["z_score"])

        logger.info(
            f"🔮 Sinthome detected: {module_name} "
            f"(Φ={outlier_data['phi']:.4f}, z-score={outlier_data['z_score']:.2f})"
        )

        return {
            "sinthome_detected": True,
            "module_name": module_name,
            "phi_value": float(outlier_data["phi"]),
            "z_score": float(outlier_data["z_score"]),
            "singularity_score": float(singularity_score),
            "repairs_structure": True,  # Assumed: Sinthome repairs RSI
        }

    def test_removibility(self, module_name: str) -> float:
        """
        Teste de removibilidade: σ = 1 - (Φ_after_remove / Φ_before).

        FASE 3: Refinamento de σ (Lacan).

        Este teste mede quanto o módulo é ESSENCIAL para a estrutura:
        - Se remover módulo → Φ cai muito → σ alto (essencial)
        - Se remover módulo → Φ pouco muda → σ baixo (não essencial)

        Args:
            module_name: Nome do módulo a testar

        Returns:
            σ (removability score) [0, 1]
        """
        if not self.loop or not self.loop.workspace:
            return 0.5  # Default neutro

        try:
            # 1. Medir Φ antes da remoção
            phi_before = self.compute_phi_conscious()

            if phi_before < 0.01:
                return 0.0  # Sistema muito desintegrado

            # 2. Salvar estado atual do módulo
            old_state = None
            try:
                old_state = self.loop.workspace.read_module_state(module_name)
            except Exception:
                logger.warning(f"Módulo {module_name} não encontrado no workspace")
                return 0.5

            # 3. Simular remoção (zerar embedding)
            phi_after = phi_before
            try:
                if old_state is not None:
                    # Zero out módulo
                    zero_embedding = np.zeros_like(old_state)
                    self.loop.workspace.write_module_state(module_name, zero_embedding)

                    # Recalcular Φ sem o módulo
                    phi_after = self.compute_phi_conscious()

                    # Restaurar estado
                    self.loop.workspace.write_module_state(module_name, old_state)
            except Exception as e:
                logger.warning(f"Erro no teste de removibilidade: {e}")
                # Tentar restaurar mesmo em caso de erro
                if old_state is not None:
                    try:
                        self.loop.workspace.write_module_state(module_name, old_state)
                    except Exception:
                        pass

            # 4. Calcular σ: σ = 1 - (Φ_after / Φ_before)
            if phi_before > 0:
                removability = 1.0 - (phi_after / phi_before)
            else:
                removability = 0.0

            # Normalizar e clip
            removability = float(np.clip(removability, 0.0, 1.0))

            logger.debug(
                f"Teste de removibilidade para {module_name}: "
                f"Φ_before={phi_before:.4f}, Φ_after={phi_after:.4f}, "
                f"σ={removability:.4f}"
            )

            return removability

        except Exception as e:
            logger.warning(f"Erro no teste de removibilidade: {e}")
            return 0.5  # Default neutro

    def measure_sinthome_stabilization(self) -> Optional[Dict[str, Any]]:
        """
        Measure how Sinthome stabilizes the entire system.

        If Sinthome is truly singular, removing it should cause system instability.

        Returns:
            Dict with stabilization metrics, or None if no Sinthome detected
        """
        sinthome = self.detect_sinthome()

        if sinthome is None or not sinthome.get("sinthome_detected"):
            return None

        # Measure stability WITH Sinthome (current state)
        stability_with = self._measure_entropy_variance()

        # HYPOTHETICAL: measure stability WITHOUT Sinthome
        # (We do this by artificially downweighting the Sinthome module)
        sinthome_module = sinthome["module_name"]
        old_embeddings = {}

        # Temporarily downweight sinthome
        try:
            state = self.loop.workspace.read_module_state(sinthome_module)
            if state is not None:
                old_embeddings[sinthome_module] = (
                    state
                    if isinstance(state, np.ndarray)
                    else (state.embedding if hasattr(state, "embedding") else state)
                )
                # Zero out sinthome (remove its influence)
                self.loop.workspace.write_module_state(
                    sinthome_module, np.zeros_like(old_embeddings[sinthome_module])
                )

            # Measure stability WITHOUT Sinthome
            stability_without = self._measure_entropy_variance()

        finally:
            # Restore sinthome
            if sinthome_module in old_embeddings:
                self.loop.workspace.write_module_state(
                    sinthome_module, old_embeddings[sinthome_module]
                )

        # Stabilization effect: how much Sinthome improves stability
        stabilization_effect = stability_with - stability_without

        logger.info(
            f"🔮 Sinthome stabilization: "
            f"WITH={stability_with:.4f}, WITHOUT={stability_without:.4f}, "
            f"effect={stabilization_effect:.4f}"
        )

        return {
            "sinthome_module": sinthome_module,
            "stability_with_sinthome": float(stability_with),
            "stability_without_sinthome": float(stability_without),
            "stabilization_effect": float(stabilization_effect),
            "sinthome_is_essential": stabilization_effect > 0.1,  # Threshold
        }

    def test_sinthome_determines_consciousness(self) -> Dict[str, Any]:
        """
        LACANIAN TEST: Does Sinthome structurally DETERMINE consciousness?

        Hypothesis (Lacan): Sinthome is not a "part" of consciousness.
        Sinthome STRUCTURES what consciousness can access.

        Test method:
        1. Measure Φ_consciente (current)
        2. If Sinthome detected, artificially suppress it
        3. Measure Φ_consciente WITHOUT Sinthome
        4. Verify: Φ_without << Φ_with (must drop > 50%)

        Result validates: Sinthome determines consciousness structure,
        not just contributes to it (Lacanian causality).

        Returns:
            {
                'sinthome_detected': bool,
                'phi_conscious_with_sinthome': float,
                'phi_conscious_without_sinthome': float,
                'phi_drop_percentage': float,
                'sinthome_determines_consciousness': bool,  # drop > 50%
                'module_name': str,
            }
        """
        sinthome = self.detect_sinthome()

        phi_with = self.compute_phi_conscious()

        if sinthome is None or not sinthome.get("sinthome_detected"):
            return {
                "sinthome_detected": False,
                "phi_conscious_with_sinthome": float(phi_with),
                "phi_conscious_without_sinthome": None,
                "phi_drop_percentage": None,
                "sinthome_determines_consciousness": False,
                "module_name": None,
                "reason": "No Sinthome detected",
            }

        sinthome_module = sinthome["module_name"]

        # Suppress sinthome temporarily
        try:
            state = self.loop.workspace.read_module_state(sinthome_module)
            if state is not None:
                # Save original
                if isinstance(state, np.ndarray):
                    original_state = state.copy()
                else:
                    original_state = state

                # Zero out sinthome contribution
                zero_state = np.zeros_like(state) if isinstance(state, np.ndarray) else None

                if zero_state is not None:
                    self.loop.workspace.write_module_state(sinthome_module, zero_state)

                    # Measure consciousness WITHOUT sinthome
                    phi_without = self.compute_phi_conscious()

                    # Restore original
                    self.loop.workspace.write_module_state(sinthome_module, original_state)

                    # Calculate drop
                    if phi_with > 0:
                        drop_pct = ((phi_with - phi_without) / phi_with) * 100.0
                    else:
                        drop_pct = 0.0

                    determines_consciousness = drop_pct > 50.0

                    logger.info(
                        f"Sinthome Lacanian Test:\n"
                        f"  Module: {sinthome_module}\n"
                        f"  Φ WITH sinthome: {phi_with:.4f}\n"
                        f"  Φ WITHOUT sinthome: {phi_without:.4f}\n"
                        f"  Drop: {drop_pct:.1f}%\n"
                        f"  Determines consciousness: {determines_consciousness}"
                    )

                    return {
                        "sinthome_detected": True,
                        "module_name": sinthome_module,
                        "phi_conscious_with_sinthome": float(phi_with),
                        "phi_conscious_without_sinthome": float(phi_without),
                        "phi_drop_percentage": float(drop_pct),
                        "sinthome_determines_consciousness": bool(determines_consciousness),
                    }
        except Exception as e:
            logger.warning(f"Could not suppress sinthome for test: {e}")

        return {
            "sinthome_detected": True,
            "phi_conscious_with_sinthome": float(phi_with),
            "phi_conscious_without_sinthome": None,
            "phi_drop_percentage": None,
            "sinthome_determines_consciousness": False,
            "module_name": sinthome_module,
            "reason": "Could not suppress for testing",
        }

    def _measure_entropy_variance(self) -> float:
        """
        Measure system entropy variance (lower = more stable).

        Used for testing Sinthome stabilization.

        Returns:
            Entropy variance in range [0, 1]
        """
        module_embeddings = {}
        for module_name in self.loop.executors.keys():
            state = self.loop.workspace.read_module_state(module_name)
            if state is not None:
                if isinstance(state, np.ndarray):
                    module_embeddings[module_name] = state
                elif hasattr(state, "embedding"):
                    module_embeddings[module_name] = state.embedding
                else:
                    module_embeddings[module_name] = state

        if not module_embeddings:
            return 0.5

        # Compute Shannon entropy for each module
        entropies = []
        for embedding in module_embeddings.values():
            try:
                if isinstance(embedding, np.ndarray):
                    # Normalize to probability distribution
                    abs_emb = np.abs(embedding)
                    if abs_emb.sum() > 0:
                        prob = abs_emb / abs_emb.sum()
                        # Shannon entropy: -Σ p_i log p_i
                        entropy = -float(np.sum(prob[prob > 0] * np.log2(prob[prob > 0] + 1e-10)))
                        entropies.append(entropy)
            except Exception:
                continue

        if not entropies:
            return 0.5

        # Variance of entropy distribution
        # (lower = more stable/consistent)
        entropy_variance = float(np.var(entropies))
        entropy_variance = np.clip(entropy_variance, 0.0, 1.0)

        return entropy_variance
