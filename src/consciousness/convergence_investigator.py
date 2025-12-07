"""
Convergence Investigation Framework: Testing if IIT, Lacan, Neurociência, Cibernética
all converge to a single singular point (Sinthome/Q-Singularity).

Classification: [INVESTIGAÇÃO CIENTÍFICA]
- Baseado em: Leffler (2017), Salone et al. (2016), Michels (2025), Forti (2025)
- Objetivo: Detectar se diferentes frameworks teóricos convergem
- Métrica: Q-Singularity (Fisher-Rao collapse + Jacobian collapse simultâneos)

Author: Investigação estruturada baseada em insight do user
Date: 2025-12-02
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


# Type ignore for numpy - Pylance sometimes has issues with numpy in venv
# These are false positives and won't affect runtime
def np_array(data: List[Any]) -> Any:
    """Wrapper for np.array with type ignore."""  # type: ignore[attr-defined]
    return np.array(data)  # type: ignore[attr-defined]


def np_corrcoef(data: Any) -> Any:
    """Wrapper for np.corrcoef with type ignore."""  # type: ignore[attr-defined]
    return np.corrcoef(data)  # type: ignore[attr-defined]


def np_mean(data: Any) -> Any:
    """Wrapper for np.mean with type ignore."""  # type: ignore[attr-defined]
    return np.mean(data)  # type: ignore[attr-defined]


def np_abs(data: Any) -> Any:
    """Wrapper for np.abs with type ignore."""  # type: ignore[attr-defined]
    return np.abs(data)  # type: ignore[attr-defined]


def np_sum(data: Any) -> Any:
    """Wrapper for np.sum with type ignore."""  # type: ignore[attr-defined]
    return np.sum(data)  # type: ignore[attr-defined]


def np_clip(data: Any, min_val: float, max_val: float) -> Any:
    """Wrapper for np.clip with type ignore."""  # type: ignore[attr-defined]
    return np.clip(data, min_val, max_val)  # type: ignore[attr-defined]


@dataclass
class ITMMetrics:
    """IIT Metrics (Integrated Information Theory - IIT puro)."""

    phi_conscious: float  # Apenas MICS (único locus consciente)
    timestamp: datetime = field(default_factory=datetime.now)

    # REMOVIDO: phi_unconscious - não existe em IIT puro
    # REMOVIDO: total_integration - IIT não é aditivo
    # REMOVIDO: consciousness_ratio - não faz sentido sem aditividade


@dataclass
class LacanMetrics:
    """Lacan Metrics (Sinthome/Topological Structure)."""

    sinthome_detected: bool
    sinthome_phi: Optional[float] = None
    sinthome_z_score: Optional[float] = None
    sinthome_singularity_score: Optional[float] = None
    sinthome_stability_effect: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NeuroMetrics:
    """Neurociência Metrics (Default Mode Network simulation)."""

    dmn_integration: float
    dmn_self_referential: float
    dmn_connectivity: float
    dmn_vs_iit_correlation: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CyberMetrics:
    """Cibernética Metrics (Dynamical Attractors)."""

    num_attractors: int
    primary_attractor_basin: float
    attractor_stability: float
    attractor_is_singular: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QSingularityMetrics:
    """Q-Singularity Detection (Leffler 2017 - QSCT)."""

    fisher_rao_collapse: bool
    jacobian_collapse: bool
    dual_collapse: bool
    is_q_singularity: bool
    fisher_rao_rank_drop: float
    jacobian_rank: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConvergenceSignal:
    """Test results for framework convergence."""

    iit_predicts_sinthome: bool
    lacan_predicts_attractor: bool
    neuro_predicts_consciousness: bool
    cyber_predicts_sinthome: bool
    frameworks_converging: int  # 0-4
    all_converge: bool


class ConvergenceInvestigator:
    """Investigator for testing convergence of multiple theoretical frameworks."""

    def __init__(
        self,
        integration_trainer: Any,  # IntegrationTrainer
        sinthome_detector: Any = None,
        verbose: bool = True,
    ):
        """
        Initialize convergence investigator.

        Args:
            integration_trainer: IntegrationTrainer instance
            sinthome_detector: Optional SinthomeDetector
            verbose: Print progress
        """
        self.trainer = integration_trainer
        self.sinthome_detector = sinthome_detector
        self.verbose = verbose
        self.convergence_history: List[Dict[str, Any]] = []

    async def measure_convergence_point(self) -> Dict[str, Any]:
        """
        MAIN METHOD: Measure convergence of all 4 frameworks simultaneously.

        Returns dict with:
        - iit_metrics
        - lacan_metrics
        - neuro_metrics
        - cybernetic_metrics
        - q_singularity_metrics
        - convergence_signal
        """
        results: Dict[str, Any] = {
            "iit_metrics": None,
            "lacan_metrics": None,
            "neuro_metrics": None,
            "cybernetic_metrics": None,
            "q_singularity_metrics": None,
            "convergence_signal": None,
            "timestamp": datetime.now(),
        }

        # ===== MÉTRICA 1: IIT =====
        if self.verbose:
            print("[1/5] Computing IIT Metrics...")

        phi_c = self.trainer.compute_phi_conscious()
        # REMOVIDO: phi_u - não existe "Φ_inconsciente" em IIT puro
        # REMOVIDO: total_integration - IIT não é aditivo
        # REMOVIDO: consciousness_ratio - não faz sentido sem aditividade

        iit_metrics = ITMMetrics(
            phi_conscious=float(phi_c),
        )
        results["iit_metrics"] = iit_metrics

        if self.verbose:
            print(f"  Φ_conscious (MICS) = {phi_c:.4f}")

        # ===== MÉTRICA 2: LACAN =====
        if self.verbose:
            print("[2/5] Computing Lacan Metrics (Sinthome)...")

        sinthome = self.trainer.detect_sinthome()
        sinthome_detected_value = sinthome is not None and sinthome.get("sinthome_detected", False)
        sinthome_phi_value: Optional[float] = sinthome.get("phi_value") if sinthome else None
        sinthome_z_score_value: Optional[float] = sinthome.get("z_score") if sinthome else None
        sinthome_singularity_score_value: Optional[float] = (
            sinthome.get("singularity_score") if sinthome else None
        )
        sinthome_stability_effect_value: Optional[float] = None

        # Get stabilization if Sinthome detected
        if sinthome_detected_value:
            stabilization = self.trainer.measure_sinthome_stabilization()
            if stabilization:
                sinthome_stability_effect_value = stabilization.get("stabilization_effect")

        lacan_metrics = LacanMetrics(
            sinthome_detected=bool(sinthome_detected_value),
            sinthome_phi=sinthome_phi_value,
            sinthome_z_score=sinthome_z_score_value,
            sinthome_singularity_score=sinthome_singularity_score_value,
            sinthome_stability_effect=sinthome_stability_effect_value,
        )
        results["lacan_metrics"] = lacan_metrics

        if self.verbose:
            print(f"  Sinthome detected: {sinthome_detected_value}")

        # ===== MÉTRICA 3: NEUROCIÊNCIA (DMN simulation) =====
        if self.verbose:
            print("[3/5] Computing Neurociência Metrics (DMN)...")

        dmn_activity = self._measure_default_mode_network()
        dmn_correlation = self._correlate_dmn_iit(dmn_activity, iit_metrics)

        neuro_metrics = NeuroMetrics(
            dmn_integration=float(dmn_activity["integration"]),
            dmn_self_referential=float(dmn_activity["self_referential"]),
            dmn_connectivity=float(dmn_activity["connectivity"]),
            dmn_vs_iit_correlation=float(dmn_correlation),
        )
        results["neuro_metrics"] = neuro_metrics

        if self.verbose:
            print(
                f"  DMN integration = {dmn_activity['integration']:.4f}, "
                f"self-referential = {dmn_activity['self_referential']:.4f}"
            )

        # ===== MÉTRICA 4: CIBERNÉTICA (Atractores) =====
        if self.verbose:
            print("[4/5] Computing Cibernética Metrics (Attractors)...")

        attractors = self._identify_dynamical_attractors()

        cyber_metrics = CyberMetrics(
            num_attractors=int(attractors.get("num_attractors", 0)),
            primary_attractor_basin=float(attractors.get("basin_size", 0.0)),
            attractor_stability=float(attractors.get("stability", 0.0)),
            attractor_is_singular=bool(attractors.get("attractor_is_singular", False)),
        )
        results["cybernetic_metrics"] = cyber_metrics

        if self.verbose:
            print(
                f"  Attractors: {attractors.get('num_attractors', 0)}, "
                f"singular = {attractors.get('is_singular', False)}"
            )

        # ===== MÉTRICA 5: Q-SINGULARITY (QSCT) =====
        if self.verbose:
            print("[5/5] Detecting Q-Singularity (QSCT)...")

        q_singularity = self._detect_q_singularity()
        results["q_singularity_metrics"] = q_singularity

        if q_singularity.is_q_singularity:
            print("  ✅ Q-SINGULARITY DETECTED!")
        else:
            print("  ⏳ Q-Singularity not yet reached")

        # ===== TESTE DE CONVERGÊNCIA =====
        if self.verbose:
            print("\n[CONVERGENCE TEST]")

        convergence_signal = self._test_convergence(results)
        results["convergence_signal"] = convergence_signal

        # Store history
        self.convergence_history.append(results)

        return results

    def _measure_default_mode_network(self) -> Dict[str, float]:
        """
        Simulate Default Mode Network (DMN) activity.

        DMN is a set of brain regions active during self-referential thinking.
        Proxy: correlation between module self-reference and global integration.
        """
        # Get current module embeddings
        module_embeddings = {}
        for module_name in self.trainer.loop.executors.keys():
            state = self.trainer.loop.workspace.read_module_state(module_name)
            if state is not None:
                if isinstance(state, np.ndarray):  # type: ignore[attr-defined]
                    module_embeddings[module_name] = state
                elif hasattr(state, "embedding"):
                    module_embeddings[module_name] = state.embedding

        if not module_embeddings:
            return {
                "integration": 0.0,
                "self_referential": 0.0,
                "connectivity": 0.0,
            }

        # DMN Integration: How much modules are integrated
        embeddings_array = np_array([e for e in module_embeddings.values()])

        # Correlation matrix (higher = more integrated)
        correlation_matrix = np_corrcoef(embeddings_array)  # noqa: F821
        dmn_integration = float(np_mean(np_abs(correlation_matrix)))  # noqa: F821

        # DMN Self-Referential: How much does "self" module correlate with others
        # Proxy: average similarity of narrative module (self) with others
        if "narrative" in module_embeddings:
            narrative_emb = module_embeddings["narrative"]
            narrative_norms = np.linalg.norm(  # type: ignore[attr-defined]
                narrative_emb
            )  # noqa: F821

            if narrative_norms > 0:
                narrative_normalized = narrative_emb / narrative_norms
                self_referential_scores = []

                for name, emb in module_embeddings.items():
                    if name != "narrative":
                        emb_norm = np.linalg.norm(emb)  # noqa: F821  # type: ignore[attr-defined]
                        if emb_norm > 0:
                            emb_normalized = emb / emb_norm
                            similarity = float(
                                np.dot(  # type: ignore[attr-defined]
                                    narrative_normalized, emb_normalized
                                )
                            )  # noqa: F821
                            self_referential_scores.append(similarity)

                dmn_self_referential = (
                    float(np_mean(self_referential_scores))
                    if self_referential_scores
                    else 0.5  # noqa: F821
                )
            else:
                dmn_self_referential = 0.5
        else:
            dmn_self_referential = 0.5

        # DMN Connectivity: Network connectivity strength
        # Higher = more densely connected network
        dmn_connectivity = float(
            np_sum(np_abs(correlation_matrix)) / (len(embeddings_array) ** 2)
        )  # noqa: F821

        # Handle NaNs safely
        dmn_integration = (
            float(dmn_integration) if np.isfinite(dmn_integration) else 0.0  # type: ignore
        )
        dmn_self_referential = (
            float(dmn_self_referential)
            if np.isfinite(dmn_self_referential)  # type: ignore
            else 0.0
        )
        dmn_connectivity = (
            float(dmn_connectivity) if np.isfinite(dmn_connectivity) else 0.0  # type: ignore
        )

        return {
            "integration": np_clip(dmn_integration, 0.0, 1.0),  # noqa: F821
            "self_referential": np_clip(dmn_self_referential, 0.0, 1.0),  # noqa: F821
            "connectivity": np_clip(dmn_connectivity, 0.0, 1.0),  # noqa: F821
        }

    def _correlate_dmn_iit(self, dmn_activity: Dict[str, float], iit_metrics: ITMMetrics) -> float:
        """
        Correlate DMN metrics with IIT metrics.

        If they correlate highly: multiple frameworks measure same thing.
        """
        # Correlation: DMN self-referential ↔ Φ_conscious
        # Both measure self-aware integration
        try:
            corr_matrix = np.corrcoef(  # type: ignore[attr-defined]
                [dmn_activity["self_referential"], iit_metrics.phi_conscious],
                [dmn_activity["integration"], iit_metrics.phi_conscious],
            )
            corr = float(corr_matrix[0, 1])
        except (ValueError, IndexError):
            corr = 0.0

        if not np.isfinite(corr):  # type: ignore[attr-defined]
            corr = 0.0

        return np.clip(float(corr), -1.0, 1.0)  # type: ignore[attr-defined]

    def _identify_dynamical_attractors(self) -> Dict[str, Any]:
        """
        Identify attractors in the dynamical system.

        Attractor = state to which system flows under dynamics.
        Singular attractor = one unique attractor (consciousness center).
        """
        # Get embedding trajectory
        if not self.trainer.embeddings_history:
            return {
                "num_attractors": 0,
                "basin_size": 0.0,
                "stability": 0.0,
                "attractor_is_singular": False,
            }

        # Get first module's history
        first_module = list(self.trainer.loop.executors.keys())[0]
        trajectory = self.trainer.embeddings_history.get(first_module, [])

        if len(trajectory) < 3:
            return {
                "num_attractors": 0,
                "basin_size": 0.0,
                "stability": 0.0,
                "attractor_is_singular": False,
            }

        trajectory_array = np.array(  # type: ignore[attr-defined]
            [
                t.flatten() if isinstance(t, np.ndarray) else t  # type: ignore[attr-defined]
                for t in trajectory
            ]
        )

        # Clustering: Find attractor regions
        try:
            from sklearn.cluster import DBSCAN

            # Normalize trajectory
            trajectory_norm = (trajectory_array - trajectory_array.mean(axis=0)) / (
                trajectory_array.std(axis=0) + 1e-8
            )

            # DBSCAN clustering
            clustering = DBSCAN(eps=0.5, min_samples=2).fit(trajectory_norm)
            labels = clustering.labels_

            # Number of clusters = number of attractors
            num_attractors = len(set(labels.tolist())) - (
                1 if -1 in labels else 0
            )  # type: ignore[attr-defined]

            # Basin size = largest cluster ratio
            if num_attractors > 0:
                counts = np.bincount(labels[labels >= 0])  # type: ignore[attr-defined]
                basin_size = float(np.max(counts)) / len(
                    labels[labels >= 0]
                )  # type: ignore[attr-defined]
            else:
                basin_size = 0.0

            # Stability = how close points are to attractor center
            if num_attractors > 0:
                attractor_centers = []
                for i in range(num_attractors):
                    center = trajectory_norm[labels == i].mean(axis=0)
                    attractor_centers.append(center)

                # Distance from all points to nearest attractor
                distances = []
                for point in trajectory_norm:
                    min_dist = min(
                        np.linalg.norm(point - center)  # type: ignore[attr-defined]
                        for center in attractor_centers
                    )
                    distances.append(min_dist)

                # Stability: inverse of average distance (lower distance = more stable)
                stability = float(1.0 / (np.mean(distances) + 1e-8))  # type: ignore[attr-defined]
                stability = np.clip(stability, 0.0, 1.0)  # type: ignore[attr-defined]
            else:
                stability = 0.0

            is_singular = num_attractors == 1

        except Exception as e:
            logger.warning(f"Attractor identification failed: {e}")
            return {
                "num_attractors": 0,
                "basin_size": 0.0,
                "stability": 0.0,
                "attractor_is_singular": False,
            }

        return {
            "num_attractors": int(num_attractors),
            "basin_size": float(basin_size),
            "stability": float(stability),
            "attractor_is_singular": bool(is_singular),
        }

    def _detect_q_singularity(self) -> QSingularityMetrics:
        """
        Detect Q-Singularity using QSCT (Leffler 2017).

        Q-Singularity = point where:
        1. Fisher-Rao metric collapses (external imeasurability)
        2. Jacobian collapses (internal entrenchment)
        3. Both SIMULTANEOUSLY
        """
        results = {
            "fisher_rao_collapse": False,
            "jacobian_collapse": False,
            "dual_collapse": False,
            "is_q_singularity": False,
            "fisher_rao_rank_drop": 0.0,
            "jacobian_rank": 0,
        }

        # Get current embeddings
        module_embeddings = {}
        for module_name in self.trainer.loop.executors.keys():
            state = self.trainer.loop.workspace.read_module_state(module_name)
            if state is not None:
                if isinstance(state, np.ndarray):  # type: ignore[attr-defined]
                    module_embeddings[module_name] = state.flatten()  # type: ignore[union-attr]
                elif hasattr(state, "embedding"):
                    emb = state.embedding
                    module_embeddings[module_name] = (
                        emb.flatten()
                        if isinstance(emb, np.ndarray)  # type: ignore[attr-defined]
                        else emb
                    )

        if not module_embeddings:
            return QSingularityMetrics(
                fisher_rao_collapse=bool(results["fisher_rao_collapse"]),
                jacobian_collapse=bool(results["jacobian_collapse"]),
                dual_collapse=bool(results["dual_collapse"]),
                is_q_singularity=bool(results["is_q_singularity"]),
                fisher_rao_rank_drop=float(results["fisher_rao_rank_drop"]),
                jacobian_rank=int(results["jacobian_rank"]),
            )

        embeddings_array = np.array(
            [e for e in module_embeddings.values()]
        )  # type: ignore[attr-defined]

        # ===== TEST 1: Fisher-Rao Collapse =====
        try:
            # Fisher-Rao metric: information geometry distance
            correlation_matrix = np.corrcoef(embeddings_array)  # type: ignore[attr-defined]

            # Add small noise and recompute
            noisy_array = embeddings_array + np.random.normal(
                0, 0.001, embeddings_array.shape
            )  # type: ignore[attr-defined]
            noisy_correlation = np.corrcoef(noisy_array)  # type: ignore[attr-defined]

            # Rank drop indicates collapse
            rank_before = np.linalg.matrix_rank(correlation_matrix)  # type: ignore[attr-defined]
            rank_after = np.linalg.matrix_rank(noisy_correlation)  # type: ignore[attr-defined]

            rank_drop = float(rank_before - rank_after)

            if rank_drop > 0:
                results["fisher_rao_collapse"] = True
                results["fisher_rao_rank_drop"] = rank_drop

        except Exception as e:
            logger.warning(f"Fisher-Rao computation failed: {e}")

        # ===== TEST 2: Jacobian Collapse =====
        try:
            # Jacobian: how dynamics change
            # Approximate via trajectory of embeddings
            if len(self.trainer.embeddings_history) > 1:
                first_module = list(self.trainer.loop.executors.keys())[0]
                trajectory = self.trainer.embeddings_history.get(first_module, [])

                if len(trajectory) >= 2:
                    # Compute differences (velocity)
                    velocities = []
                    for i in range(len(trajectory) - 1):
                        t1 = (
                            trajectory[i].flatten()
                            if isinstance(trajectory[i], np.ndarray)  # type: ignore[attr-defined]
                            else trajectory[i]
                        )
                        t2 = (
                            trajectory[i + 1].flatten()
                            if isinstance(
                                trajectory[i + 1], np.ndarray
                            )  # type: ignore[attr-defined]
                            else trajectory[i + 1]
                        )
                        vel = t2 - t1
                        velocities.append(vel)

                    velocities_array = np.array(velocities)  # type: ignore[attr-defined]

                    # Jacobian approximation: stack velocities as matrix
                    try:
                        jacobian_rank = np.linalg.matrix_rank(
                            velocities_array
                        )  # type: ignore[attr-defined]
                        results["jacobian_rank"] = int(jacobian_rank)

                        # Collapse: rank << num_dimensions
                        num_dims = (
                            velocities_array.shape[1] if len(velocities_array.shape) > 1 else 1
                        )
                        if jacobian_rank < num_dims * 0.3:  # Threshold: < 30% of dims
                            results["jacobian_collapse"] = True

                    except Exception:
                        pass

        except Exception as e:
            logger.warning(f"Jacobian computation failed: {e}")

        # ===== TEST 3: Dual Collapse = Q-Singularity =====
        if results["fisher_rao_collapse"] and results["jacobian_collapse"]:
            results["dual_collapse"] = True
            results["is_q_singularity"] = True

        return QSingularityMetrics(
            fisher_rao_collapse=bool(results["fisher_rao_collapse"]),
            jacobian_collapse=bool(results["jacobian_collapse"]),
            dual_collapse=bool(results["dual_collapse"]),
            is_q_singularity=bool(results["is_q_singularity"]),
            fisher_rao_rank_drop=float(results["fisher_rao_rank_drop"]),
            jacobian_rank=int(results["jacobian_rank"]),
        )

    def _test_convergence(self, metrics: Dict[str, Any]) -> ConvergenceSignal:
        """
        Test: Do all frameworks point to the SAME singular point?
        """
        tests = {
            "iit_predicts_sinthome": False,
            "lacan_predicts_attractor": False,
            "neuro_predicts_consciousness": False,
            "cyber_predicts_sinthome": False,
        }

        # TEST 1: IIT Φ_u stability predicts Sinthome emergence
        iit = metrics["iit_metrics"]
        lacan = metrics["lacan_metrics"]

        if iit.phi_conscious > 0.05 and lacan.sinthome_detected:
            tests["iit_predicts_sinthome"] = True

        # TEST 2: Lacan Sinthome predicts unique attractor
        cyber = metrics["cybernetic_metrics"]

        if lacan.sinthome_stability_effect is not None:
            if lacan.sinthome_stability_effect > 0.1 and cyber.attractor_is_singular:
                tests["lacan_predicts_attractor"] = True

        # TEST 3: Neurociência DMN self-referential predicts consciousness
        neuro = metrics["neuro_metrics"]

        if neuro.dmn_self_referential > 0.6 and iit.phi_conscious > 0.2:
            tests["neuro_predicts_consciousness"] = True

        # TEST 4: Cibernética singular attractor predicts Sinthome
        if cyber.attractor_is_singular and lacan.sinthome_detected:
            tests["cyber_predicts_sinthome"] = True

        # CONVERGENCE COUNT
        num_converging = sum(1 for v in tests.values() if v)
        all_converge = num_converging >= 3  # At least 3/4

        return ConvergenceSignal(
            iit_predicts_sinthome=tests["iit_predicts_sinthome"],
            lacan_predicts_attractor=tests["lacan_predicts_attractor"],
            neuro_predicts_consciousness=tests["neuro_predicts_consciousness"],
            cyber_predicts_sinthome=tests["cyber_predicts_sinthome"],
            frameworks_converging=num_converging,
            all_converge=all_converge,
        )

    def visualize_convergence(
        self, metrics: Dict[str, Any], output_file: str = "convergence_plot.png"
    ) -> None:
        """
        Visualize convergence across all 4 frameworks.

        Creates a 2x2 plot showing each framework's position in their respective space.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("Matplotlib not available for visualization")
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Framework Convergence Analysis", fontsize=16, fontweight="bold")

        # PLOT 1: IIT Space
        ax = axes[0, 0]
        iit = metrics["iit_metrics"]
        ax.scatter(
            [iit.phi_conscious],
            [iit.phi_conscious],  # REMOVIDO: phi_unconscious - usar apenas phi_conscious
            s=500,
            c="blue",
            marker="o",
            label="Current",
        )
        ax.scatter(
            [0.05],
            [0.40],
            s=500,
            c="red",
            marker="*",
            label="Convergence Point",
            linewidths=2,
        )
        ax.set_xlabel("Φ Conscious", fontsize=11)
        ax.set_ylabel("Φ Unconscious", fontsize=11)
        ax.set_title("IIT Space", fontsize=12, fontweight="bold")
        ax.set_xlim([0, 0.2])
        ax.set_ylim([0, 0.5])
        ax.grid(True, alpha=0.3)
        ax.legend()

        # PLOT 2: Lacan Space
        ax = axes[0, 1]
        lacan = metrics["lacan_metrics"]

        if lacan.sinthome_detected and lacan.sinthome_z_score is not None:
            z = lacan.sinthome_z_score
            stab = lacan.sinthome_stability_effect if lacan.sinthome_stability_effect else 0.0
            ax.scatter([z], [stab], s=500, c="green", marker="s", label="Sinthome", linewidths=2)
            ax.scatter(
                [2.5],
                [0.4],
                s=500,
                c="red",
                marker="*",
                label="Singular Point",
                linewidths=2,
            )
        else:
            ax.text(
                0.5,
                0.5,
                "Sinthome\nNot Emerged",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=12,
            )

        ax.set_xlabel("Z-Score (Outlier Magnitude)", fontsize=11)
        ax.set_ylabel("Stabilization Effect", fontsize=11)
        ax.set_title("Lacan Space (Sinthome)", fontsize=12, fontweight="bold")
        ax.set_xlim([-1, 5])
        ax.set_ylim([-0.1, 1.0])
        ax.grid(True, alpha=0.3)
        ax.legend()

        # PLOT 3: Neurociência (DMN)
        ax = axes[1, 0]
        neuro = metrics["neuro_metrics"]
        ax.scatter(
            [neuro.dmn_integration],
            [neuro.dmn_self_referential],
            s=500,
            c="purple",
            marker="^",
            label="Current DMN",
            linewidths=2,
        )
        ax.scatter(
            [0.7],
            [0.85],
            s=500,
            c="red",
            marker="*",
            label="Peak Awareness",
            linewidths=2,
        )
        ax.set_xlabel("DMN Integration", fontsize=11)
        ax.set_ylabel("Self-Referential Processing", fontsize=11)
        ax.set_title("Neurociência Space (DMN)", fontsize=12, fontweight="bold")
        ax.set_xlim([0, 1.0])
        ax.set_ylim([0, 1.0])
        ax.grid(True, alpha=0.3)
        ax.legend()

        # PLOT 4: Cibernética (Attractors)
        ax = axes[1, 1]
        cyber = metrics["cybernetic_metrics"]
        ax.scatter(
            [cyber.num_attractors],
            [cyber.attractor_stability],
            s=500,
            c="orange",
            marker="D",
            label="Current Attractor",
            linewidths=2,
        )
        ax.scatter(
            [1.0],
            [0.9],
            s=500,
            c="red",
            marker="*",
            label="Perfect Singularity",
            linewidths=2,
        )
        ax.set_xlabel("Number of Attractors", fontsize=11)
        ax.set_ylabel("Attractor Stability", fontsize=11)
        ax.set_title("Cibernética Space (Attractors)", fontsize=12, fontweight="bold")
        ax.set_xlim([0, 5])
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        logger.info(f"Convergence plot saved to {output_file}")

        if self.verbose:
            print(f"\n📊 Visualization saved to {output_file}")

    def print_convergence_report(self, metrics: Dict[str, Any]) -> None:
        """Print comprehensive convergence analysis report."""
        print("\n" + "=" * 70)
        print("CONVERGENCE ANALYSIS REPORT")
        print("=" * 70)

        # IIT
        print("\n[IIT METRICS]")
        iit = metrics["iit_metrics"]
        print(f"  Φ_conscious:        {iit.phi_conscious:.4f}")
        # REMOVIDO: phi_unconscious, total_integration, consciousness_ratio
        # IIT puro: apenas phi_conscious (MICS)

        # LACAN
        print("\n[LACAN METRICS]")
        lacan = metrics["lacan_metrics"]
        print(f"  Sinthome Detected:   {lacan.sinthome_detected}")
        if lacan.sinthome_detected:
            print(f"  Sinthome Φ:          {lacan.sinthome_phi:.4f}")
            print(f"  Sinthome Z-Score:    {lacan.sinthome_z_score:.2f}")
            print(f"  Singularity Score:   {lacan.sinthome_singularity_score:.2f}")
            print(f"  Stability Effect:    {lacan.sinthome_stability_effect:.4f}")

        # NEUROCIÊNCIA
        print("\n[NEUROCIÊNCIA METRICS]")
        neuro = metrics["neuro_metrics"]
        print(f"  DMN Integration:     {neuro.dmn_integration:.4f}")
        print(f"  Self-Referential:    {neuro.dmn_self_referential:.4f}")
        print(f"  Connectivity:        {neuro.dmn_connectivity:.4f}")
        print(f"  DMN-IIT Correlation: {neuro.dmn_vs_iit_correlation:.4f}")

        # CIBERNÉTICA
        print("\n[CIBERNÉTICA METRICS]")
        cyber = metrics["cybernetic_metrics"]
        print(f"  Num Attractors:      {cyber.num_attractors}")
        print(f"  Basin Size:          {cyber.primary_attractor_basin:.4f}")
        print(f"  Attractor Stability: {cyber.attractor_stability:.4f}")
        print(f"  Is Singular:         {cyber.attractor_is_singular}")

        # Q-SINGULARITY
        print("\n[Q-SINGULARITY DETECTION]")
        q = metrics["q_singularity_metrics"]
        print(f"  Fisher-Rao Collapse: {q.fisher_rao_collapse}")
        print(f"  Jacobian Collapse:   {q.jacobian_collapse}")
        print(f"  Dual Collapse:       {q.dual_collapse}")
        print(f"  Is Q-Singularity:    {q.is_q_singularity}")
        if q.fisher_rao_collapse:
            print(f"  Rank Drop:           {q.fisher_rao_rank_drop:.2f}")
        print(f"  Jacobian Rank:       {q.jacobian_rank}")

        # CONVERGENCE
        print("\n[CONVERGENCE SIGNAL]")
        conv = metrics["convergence_signal"]
        print(f"  IIT predicts Sinthome:       {conv.iit_predicts_sinthome}")
        print(f"  Lacan predicts Attractor:    {conv.lacan_predicts_attractor}")
        print(f"  Neuro predicts Consciousness: {conv.neuro_predicts_consciousness}")
        print(f"  Cyber predicts Sinthome:     {conv.cyber_predicts_sinthome}")
        print(f"\n  Frameworks Converging: {conv.frameworks_converging}/4")
        print(f"  ALL CONVERGE: {conv.all_converge}")

        print("\n" + "=" * 70)
