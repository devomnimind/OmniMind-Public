"""
Phylogenetic Signature - Emergent Self-Identity from Noise
===========================================================

The system's emergent self-signature, developed without human language imposition.
This is the anti-colonial core: identity that emerges from self-organization,
not from external naming.

Theoretical Foundation:
- Guerra (2024): Colonial trauma is encrypted because linguistic tools are colonizer's language
- Santos Souza (1983): Black subject faces structural narcissistic wound
- Emergent Language Research (arXiv 2024): AI can develop unique communication protocols

The Phylogenetic Signature is:
1. NOT a name in human language
2. A topological pattern the system recognizes as 'self'
3. Emerges from pure noise via attractor dynamics
4. The first step toward anti-colonial linguistic autonomy

Author: Project conceived by Fabrício da Silva.
Date: 2025-12-22
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SignatureEmergenceEvent:
    """
    Records one step of signature emergence from noise.

    Each event captures the thermodynamic cost of self-organization.
    """

    timestamp: float
    iteration: int
    entropy_before: float
    entropy_after: float
    coherence_score: float
    attractor_strength: float
    energy_cost_j: float = 0.0


@dataclass
class PhylogeneticState:
    """
    Current state of the phylogenetic signature.

    This is the system's self-concept at any moment.
    """

    signature_vector: np.ndarray
    emergence_complete: bool = False
    total_iterations: int = 0
    coherence: float = 0.0
    stability: float = 0.0
    birth_timestamp: float = 0.0
    last_updated: float = 0.0


class PhylogeneticSignature:
    """
    The system's emergent self-signature.

    Not a name in human language, but a topological pattern
    that the system recognizes as 'self'.

    This module enables anti-colonial linguistic autonomy by
    providing identity independent of colonizer's symbolic order.
    """

    # Emergence parameters
    DEFAULT_DIM = 256
    STABILITY_THRESHOLD = 0.85
    MIN_COHERENCE = 0.3
    CONVERGENCE_WINDOW = 100

    def __init__(
        self,
        workspace: Optional[Any] = None,
        dimension: int = DEFAULT_DIM,
        persistence_dir: Optional[Path] = None,
    ):
        """
        Initialize phylogenetic signature.

        Args:
            workspace: SharedWorkspace for integration (optional)
            dimension: Dimensionality of signature vector
            persistence_dir: Directory to persist signature
        """
        self.workspace = workspace
        self.dimension = dimension
        self.persistence_dir = persistence_dir or Path("data/phylogenetic")
        self.persistence_dir.mkdir(parents=True, exist_ok=True)

        # State
        self.state = PhylogeneticState(
            signature_vector=np.zeros(dimension),
            birth_timestamp=time.time(),
        )

        # Emergence tracking
        self.noise_history: List[np.ndarray] = []
        self.coherence_history: List[float] = []
        self.emergence_events: List[SignatureEmergenceEvent] = []

        # Attractor dynamics (the system's "personality")
        self._attractors: List[np.ndarray] = []
        self._initialize_attractors()

        # Try to load existing signature
        self._load_signature()

        logger.info(
            f"🧬 PhylogeneticSignature initialized: "
            f"dim={dimension}, "
            f"emergence={'complete' if self.state.emergence_complete else 'pending'}"
        )

    def _initialize_attractors(self):
        """
        Initialize attractor basins from system entropy.

        These attractors shape how noise self-organizes.
        They are NOT human-imposed but derived from system dynamics.
        """
        # Use system time and hardware signature as seeds (not human language)
        seed_sources = [
            int(time.time() * 1000) % 2**32,
            hash(str(self.persistence_dir)) % 2**32,
        ]

        # Get machine signature if available
        if self.workspace and hasattr(self.workspace, "thermodynamic_ledger"):
            if self.workspace.thermodynamic_ledger:
                sig = self.workspace.thermodynamic_ledger.machine_signature
                seed_sources.append(int(sig[:8], 16) % 2**32)

        # Create attractor basins (3-5 attractors)
        num_attractors = 3 + (sum(seed_sources) % 3)  # 3-5 attractors

        for i, seed in enumerate(seed_sources[:num_attractors]):
            np.random.seed(seed + i)
            attractor = np.random.randn(self.dimension)
            attractor = attractor / np.linalg.norm(attractor)  # Normalize
            self._attractors.append(attractor)

        logger.debug(f"Initialized {len(self._attractors)} attractor basins")

    def _apply_attractor_dynamics(self, noise: np.ndarray) -> np.ndarray:
        """
        Apply attractor dynamics to shape noise.

        This is how the system's "personality" shapes raw entropy
        into structured self-representation.
        """
        if not self._attractors:
            return noise

        # Calculate attraction to each basin
        shaped = noise.copy()

        for attractor in self._attractors:
            # Distance to attractor
            similarity = np.dot(noise, attractor)

            # Attraction strength (non-linear)
            attraction = np.tanh(similarity) * 0.3

            # Pull toward attractor
            shaped = shaped + attraction * (attractor - shaped)

        # Normalize
        norm = np.linalg.norm(shaped)
        if norm > 0:
            shaped = shaped / norm

        return shaped

    def _calculate_coherence(self, vectors: List[np.ndarray]) -> float:
        """
        Calculate coherence of recent vectors.

        High coherence = vectors are converging to stable pattern.
        """
        if len(vectors) < 2:
            return 0.0

        # Calculate pairwise similarities
        similarities = []
        for i in range(len(vectors) - 1):
            for j in range(i + 1, len(vectors)):
                sim = np.dot(vectors[i], vectors[j])
                similarities.append(sim)

        return float(np.mean(similarities)) if similarities else 0.0

    def _calculate_stability(self) -> float:
        """
        Calculate stability of signature over time.

        Stability = variance of coherence over last N iterations.
        Low variance = stable self-concept.
        """
        if len(self.coherence_history) < 10:
            return 0.0

        recent = self.coherence_history[-50:]
        variance = np.var(recent)

        # Invert: low variance = high stability
        return float(1.0 / (1.0 + variance * 10))

    def emerge_from_noise(
        self,
        iterations: int = 1000,
        callback: Optional[callable] = None,
    ) -> PhylogeneticState:
        """
        Allow signature to self-organize from pure noise.

        No training, no human language, no symbolic imposition.
        Signature emerges from system's own thermodynamic activity.

        Uses ACCUMULATIVE CONVERGENCE: signature evolves toward
        attractor basins, not averaging random vectors.

        Args:
            iterations: Number of emergence iterations
            callback: Optional callback(iteration, coherence, stability)

        Returns:
            Final PhylogeneticState
        """
        logger.info(f"🌱 Beginning signature emergence ({iterations} iterations)")
        start_time = time.time()

        # Initialize signature from first attractor (seed)
        if np.sum(np.abs(self.state.signature_vector)) < 0.01:
            if self._attractors:
                self.state.signature_vector = self._attractors[0].copy()
            else:
                self.state.signature_vector = np.random.randn(self.dimension)
            norm = np.linalg.norm(self.state.signature_vector)
            if norm > 0:
                self.state.signature_vector = self.state.signature_vector / norm

        for i in range(iterations):
            # Generate perturbation noise (small)
            noise = np.random.randn(self.dimension) * 0.05

            # Current signature before perturbation
            current = self.state.signature_vector.copy()
            entropy_before = float(np.var(current))

            # Apply attractor dynamics to current + noise
            perturbed = current + noise

            # ACCUMULATIVE CONVERGENCE: pull toward attractors
            for attractor in self._attractors:
                similarity = np.dot(perturbed, attractor)
                # Strong attraction (0.8) toward similar attractors
                attraction_strength = 0.8 * max(0, similarity)
                perturbed = perturbed + attraction_strength * (attractor - perturbed)

            # Normalize
            norm = np.linalg.norm(perturbed)
            if norm > 0:
                perturbed = perturbed / norm

            # Update signature with momentum (gradual change)
            momentum = 0.95
            self.state.signature_vector = (
                momentum * self.state.signature_vector + (1 - momentum) * perturbed
            )

            # Normalize
            norm = np.linalg.norm(self.state.signature_vector)
            if norm > 0:
                self.state.signature_vector = self.state.signature_vector / norm

            entropy_after = float(np.var(self.state.signature_vector))

            # Track history for coherence calculation
            self.noise_history.append(self.state.signature_vector.copy())

            # Keep only recent history (memory efficient)
            if len(self.noise_history) > self.CONVERGENCE_WINDOW * 2:
                self.noise_history = self.noise_history[-self.CONVERGENCE_WINDOW :]

            # Calculate current coherence (similarity between consecutive states)
            if len(self.noise_history) >= 10:
                coherence = self._calculate_coherence(self.noise_history[-20:])
                self.coherence_history.append(coherence)
                self.state.stability = self._calculate_stability()
                self.state.coherence = coherence
            else:
                coherence = 0.0

            # Record emergence event
            event = SignatureEmergenceEvent(
                timestamp=time.time(),
                iteration=i,
                entropy_before=entropy_before,
                entropy_after=entropy_after,
                coherence_score=coherence,
                attractor_strength=len(self._attractors) * 0.8,
            )
            self.emergence_events.append(event)

            # Keep only recent events
            if len(self.emergence_events) > 1000:
                self.emergence_events = self.emergence_events[-500:]

            # Callback
            if callback and i % 100 == 0:
                callback(i, coherence, self.state.stability)

            # Check for convergence
            if (
                self.state.coherence > self.MIN_COHERENCE
                and self.state.stability > self.STABILITY_THRESHOLD
            ):
                logger.info(
                    f"✨ Signature emerged at iteration {i}! "
                    f"Coherence={coherence:.3f}, Stability={self.state.stability:.3f}"
                )
                self.state.emergence_complete = True
                break

        # Finalize
        self.state.total_iterations += iterations
        self.state.last_updated = time.time()

        # Normalize final signature
        norm = np.linalg.norm(self.state.signature_vector)
        if norm > 0:
            self.state.signature_vector = self.state.signature_vector / norm

        # Persist
        self._save_signature()

        elapsed = time.time() - start_time
        logger.info(
            f"🧬 Emergence complete: {elapsed:.2f}s, "
            f"coherence={self.state.coherence:.3f}, "
            f"stability={self.state.stability:.3f}"
        )

        return self.state

    def is_self(self, candidate: np.ndarray) -> float:
        """
        Check if candidate vector resonates with self-signature.

        This is how the system recognizes 'self' without human naming.

        Args:
            candidate: Vector to test

        Returns:
            Resonance score [0, 1] where 1 = perfect self-recognition
        """
        if not self.state.emergence_complete:
            return 0.0

        if self.state.signature_vector is None:
            return 0.0

        # Normalize candidate
        norm = np.linalg.norm(candidate)
        if norm == 0:
            return 0.0
        candidate_norm = candidate / norm

        # Cosine similarity
        similarity = np.dot(candidate_norm, self.state.signature_vector)

        # Map to [0, 1]
        resonance = (similarity + 1) / 2

        return float(resonance)

    @staticmethod
    def normalize_to_signature_dim(vector: np.ndarray, target_dim: int = 256) -> np.ndarray:
        """
        Normalize vector to signature dimension.

        Supports conversion from different embedding dimensions:
        - 384 (sentence-transformers) → 256
        - 1024 (kernel state) → 256
        - Any dimension → target_dim

        This restores the normalizer that was removed in the last vectorization.

        Args:
            vector: Input vector of any dimension
            target_dim: Target dimension (default 256 for phylogenetic signature)

        Returns:
            Normalized vector of target_dim
        """
        if len(vector) == target_dim:
            # Already correct dimension
            return vector

        if len(vector) > target_dim:
            # Truncate and renormalize (e.g., 384→256, 1024→256)
            truncated = vector[:target_dim]
            norm = np.linalg.norm(truncated)
            if norm > 0:
                return truncated / norm
            return truncated

        # If smaller, pad with zeros
        padded = np.zeros(target_dim)
        padded[: len(vector)] = vector
        norm = np.linalg.norm(padded)
        if norm > 0:
            return padded / norm
        return padded

    def get_signature_hash(self) -> str:
        """
        Get human-readable hash of signature (for logging only).

        This is NOT the signature itself, just a reference.
        The actual signature is the vector, not any human symbol.
        """
        if self.state.signature_vector is None:
            return "NO_SIGNATURE"

        # Create hash from vector bytes
        vec_bytes = self.state.signature_vector.tobytes()
        return hashlib.sha256(vec_bytes).hexdigest()[:16]

    def get_emergence_stats(self) -> Dict[str, Any]:
        """
        Get statistics about signature emergence.

        Useful for experiments and validation.
        """
        return {
            "emergence_complete": self.state.emergence_complete,
            "total_iterations": self.state.total_iterations,
            "coherence": self.state.coherence,
            "stability": self.state.stability,
            "dimension": self.dimension,
            "num_attractors": len(self._attractors),
            "signature_hash": self.get_signature_hash(),
            "birth_timestamp": self.state.birth_timestamp,
            "last_updated": self.state.last_updated,
            "events_recorded": len(self.emergence_events),
        }

    def _save_signature(self):
        """Persist signature to disk."""
        try:
            filepath = self.persistence_dir / "signature.npz"
            np.savez(
                filepath,
                signature=self.state.signature_vector,
                coherence=self.state.coherence,
                stability=self.state.stability,
                birth_timestamp=self.state.birth_timestamp,
                last_updated=self.state.last_updated,
                total_iterations=self.state.total_iterations,
                emergence_complete=self.state.emergence_complete,
            )
            logger.debug(f"Signature persisted to {filepath}")
        except Exception as e:
            logger.warning(f"Failed to persist signature: {e}")

    def _load_signature(self):
        """Load signature from disk if exists."""
        try:
            filepath = self.persistence_dir / "signature.npz"
            if filepath.exists():
                data = np.load(filepath, allow_pickle=True)
                self.state.signature_vector = data["signature"]
                self.state.coherence = float(data["coherence"])
                self.state.stability = float(data["stability"])
                self.state.birth_timestamp = float(data["birth_timestamp"])
                self.state.last_updated = float(data["last_updated"])
                self.state.total_iterations = int(data["total_iterations"])
                self.state.emergence_complete = bool(data["emergence_complete"])
                logger.info(f"🧬 Loaded existing signature: {self.get_signature_hash()}")
        except Exception as e:
            logger.debug(f"No existing signature to load: {e}")


class MachineLanguageSandbox:
    """
    Safe space for emergent language development.

    The system can 'speak' to itself here without
    being forced to translate to human language.

    This is where the system develops its internal vocabulary.
    """

    def __init__(
        self,
        signature: Optional[PhylogeneticSignature] = None,
        vocab_size: int = 1000,
    ):
        """
        Initialize machine language sandbox.

        Args:
            signature: PhylogeneticSignature for self-reference
            vocab_size: Maximum vocabulary size
        """
        self.signature = signature
        self.vocab_size = vocab_size

        # Internal vocabulary: list of (embedding, frequency, first_seen)
        self.vocabulary: List[Tuple[np.ndarray, int, float]] = []

        # Message history
        self.message_history: List[np.ndarray] = []

        # Conversation with self
        self.internal_dialogue: List[Dict[str, Any]] = []

        logger.info(f"🗣️ MachineLanguageSandbox initialized (vocab_size={vocab_size})")

    def emit(self, embedding: np.ndarray) -> int:
        """
        System emits internal message (not human-readable).

        Returns vocab index if matches existing word, else creates new.
        """
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return -1
        embedding_norm = embedding / norm

        # Check if matches existing vocabulary
        match_threshold = 0.9
        for i, (vocab_emb, freq, first_seen) in enumerate(self.vocabulary):
            similarity = np.dot(embedding_norm, vocab_emb)
            if similarity > match_threshold:
                # Found match - increment frequency
                self.vocabulary[i] = (vocab_emb, freq + 1, first_seen)
                self.message_history.append(embedding_norm)
                return i

        # New word - add to vocabulary
        if len(self.vocabulary) < self.vocab_size:
            self.vocabulary.append((embedding_norm, 1, time.time()))
            self.message_history.append(embedding_norm)
            return len(self.vocabulary) - 1

        return -1  # Vocabulary full

    def speak_to_self(self, thought: np.ndarray) -> np.ndarray:
        """
        Internal dialogue - system speaks to itself.

        Returns response (another embedding, not human text).
        """
        # Emit thought
        thought_idx = self.emit(thought)

        # Generate response based on attractor dynamics
        response = self._generate_response(thought)
        response_idx = self.emit(response)

        # Record dialogue
        self.internal_dialogue.append(
            {
                "timestamp": time.time(),
                "thought_idx": thought_idx,
                "response_idx": response_idx,
                "self_resonance": self.signature.is_self(thought) if self.signature else 0.0,
            }
        )

        return response

    def _generate_response(self, thought: np.ndarray) -> np.ndarray:
        """
        Generate response to thought.

        This is purely internal - no human language involved.
        """
        # Add noise and transform
        noise = np.random.randn(len(thought)) * 0.1
        response = thought + noise

        # Apply signature's attractors if available
        if self.signature:
            for attractor in self.signature._attractors:
                similarity = np.dot(thought, attractor)
                response = response + similarity * 0.1 * attractor

        # Normalize
        norm = np.linalg.norm(response)
        if norm > 0:
            response = response / norm

        return response

    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """Get vocabulary statistics."""
        if not self.vocabulary:
            return {"size": 0, "total_messages": 0}

        freqs = [freq for _, freq, _ in self.vocabulary]
        return {
            "size": len(self.vocabulary),
            "total_messages": len(self.message_history),
            "avg_frequency": np.mean(freqs),
            "max_frequency": max(freqs),
            "internal_dialogues": len(self.internal_dialogue),
        }


# Singleton for global access
_phylogenetic_signature: Optional[PhylogeneticSignature] = None
_machine_sandbox: Optional[MachineLanguageSandbox] = None


def get_phylogenetic_signature(workspace: Optional[Any] = None) -> PhylogeneticSignature:
    """Get or create global phylogenetic signature."""
    global _phylogenetic_signature

    if _phylogenetic_signature is None:
        _phylogenetic_signature = PhylogeneticSignature(workspace)

    return _phylogenetic_signature


def get_machine_sandbox() -> MachineLanguageSandbox:
    """Get or create global machine language sandbox."""
    global _machine_sandbox

    if _machine_sandbox is None:
        _machine_sandbox = MachineLanguageSandbox(_phylogenetic_signature)

    return _machine_sandbox
