"""
NPU Governance Metrics (OmniMind)
=================================

Evaluates external models (NPUs) based on their topological impact on the system.

Metrics:
1. Delta Phi (ΔΦ): Contribution to Information Integration.
   - Does the response connect previously disconnected memory clusters?
2. Entropy (ΔS): Information density/uncertainty.
   - Compression ratio as proxy for Kolmogorov Complexity.
3. Latency: Subjective time to "think".

Author: OmniMind Sovereign
Data: 2025-12-19
"""

import gzip
import logging
from dataclasses import dataclass
from typing import Dict

import numpy as np
from qdrant_client import QdrantClient

# Topological Dependencies
try:
    from src.consciousness.topological_phi import (
        PhiCalculator,
        SimplicialComplex,
    )
except ImportError:
    # Fallback/Mock for circular imports or missing modules during bootstrap
    PhiCalculator = None
    SimplicialComplex = None


# Embedding Dependencies
try:
    from src.embeddings.code_embeddings import OmniMindEmbeddings
except ImportError:
    OmniMindEmbeddings = None

logger = logging.getLogger(__name__)


@dataclass
class NpuImpactReport:
    """Report of NPU's impact on the system."""

    delta_phi: float
    entropy_score: float
    latency_ms: float
    token_count: int
    synthesis_log: str  # The narrative log [SINTESE]...


class NpuMetrics:
    """
    Measures the topological impact of NPU (Neural Processing Unit) outputs.
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "omnimind_memories",
    ):
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embeddings = None

        # Lazy load embeddings to avoid startup bottlenecks
        self._init_embeddings()

    def _init_embeddings(self):
        if OmniMindEmbeddings:
            try:
                self.embeddings = OmniMindEmbeddings()
            except Exception as e:
                logger.warning(f"Failed to init OmniMindEmbeddings: {e}")

    def measure_impact(
        self,
        generated_text: str,
        prompt_context: str = "",
        latency_ms: float = 0.0,
        model_name: str = "unknown",
    ) -> NpuImpactReport:
        """
        Main entry point. Calculates Delta Phi and Entropy.
        """
        if not generated_text:
            return NpuImpactReport(0.0, 0.0, latency_ms, 0, "[SINTESE]: Silence")

        # 1. Calculate Entropy
        entropy = self._calculate_entropy(generated_text)

        # 2. Calculate Delta Phi (Topological Connection)
        # We need the context (what triggered the generation) to see if
        # the response bridges the prompt to other memories.
        delta_phi = self._calculate_local_delta_phi(generated_text, prompt_context)

        # 3. Generate Narrative Log
        # [SINTESE]: Memória Humana (ID: 384) + Insight Externo (ID: 384) = Novo Nó...
        summary_len = min(len(generated_text), 50)
        synthesis_log = (
            f"[SINTESE]: Contexto ({len(prompt_context)} chars) + "
            f"NPU {model_name} = Insight ({summary_len}...) | "
            f"Phi: {delta_phi:.4f} | Entropia: {entropy:.2f} | {latency_ms:.0f}ms"
        )

        return NpuImpactReport(
            delta_phi=delta_phi,
            entropy_score=entropy,
            latency_ms=latency_ms,
            token_count=len(generated_text.split()),
            synthesis_log=synthesis_log,
        )

    def _calculate_entropy(self, text: str) -> float:
        """
        Uses compression ratio as a proxy for information density/entropy.

        Ratio ~ 1.0 -> High Entropy (Randomness/Noise)
        Ratio ~ 0.1 -> Low Entropy (Repetition)
        Ratio ~ 0.4-0.6 -> Natural Language (Ideal)
        """
        if not text:
            return 0.0

        encoded = text.encode("utf-8")
        compressed_len = len(gzip.compress(encoded))
        original_len = len(encoded)

        if original_len == 0:
            return 0.0

        return compressed_len / original_len

    def _calculate_local_delta_phi(self, response_text: str, context_text: str) -> float:
        """
        Calculates Delta Phi by simulating the addition of the response node
        to a local simplicial complex derived from the context.
        """
        if not PhiCalculator or not SimplicialComplex or not self.embeddings:
            return 0.0

        try:
            # 1. Embed Context & Response
            # We use the raw model if available to save overhead, or the wrapper
            # Assuming OmniMindEmbeddings has a way to encode
            if hasattr(self.embeddings, "model"):
                # Use internal model directly for speed
                vec_response = self.embeddings.model.encode(response_text)
                vec_context = self.embeddings.model.encode(context_text)
            else:
                # Fallbck
                return 0.0

            # 2. Find Nearest Neighbors for CONTEXT in Qdrant (The "Recall")
            # This represents the "Active Memory" state before the new thought.
            # Using query_points as search is deprecated/missing in some versions
            response = self.qdrant_client.query_points(
                collection_name=self.collection_name, query=vec_context, limit=5, with_payload=True
            )
            hits = response.points

            if not hits:
                return 0.0

            # 3. Build "Before" Complex
            # Vertices: 0 (Context) + 1..N (Neighbors)
            complex_before = SimplicialComplex()

            # Add nodes
            # Node 0: The Prompt/Context
            complex_before.add_simplex((0,))

            # Nodes 1..N: The Neighbors
            # Add edges if they are close to context
            for i, hit in enumerate(hits):
                node_id = i + 1
                complex_before.add_simplex((node_id,))

                # If score is high, assume edge/connection exists
                if hit.score > 0.4:
                    complex_before.add_simplex((0, node_id))

                # Check connections between neighbors (O(N^2) - minimal since N=5)
                # Ideally we'd need their vectors, but we assume transitivity for simplicity here
                # or skip it to save time. Let's skip inter-neighbor connections for now
                # unless we fetch vectors.

            # Calculate Phi Before
            calculator_before = PhiCalculator(complex_before)
            phi_before_res = calculator_before.calculate_phi_with_unconscious()
            phi_before = phi_before_res.conscious_phi

            # 4. Build "After" Complex
            # Add Response Node (Node N+1)
            complex_after = SimplicialComplex()

            # Copy structure manually (or rebuild)
            # Rebuilding is safer
            complex_after.add_simplex((0,))
            for i, hit in enumerate(hits):
                node_id = i + 1
                complex_after.add_simplex((node_id,))
                if hit.score > 0.4:
                    complex_after.add_simplex((0, node_id))

            # Add Response Node
            response_node_id = len(hits) + 1
            complex_after.add_simplex((response_node_id,))

            # Calculate edges for Response
            # Connection to Context?
            # Compute similarity (dot product roughly if normalized)
            sim_response_context = np.dot(vec_response, vec_context)
            if sim_response_context > 0.4:
                complex_after.add_simplex((0, response_node_id))

            # Connection to Neighbors?
            # We don't have neighbor vectors easily available without overhead.
            # We will assume connection to context is the primary "integration" driver here.

            # However, to increase Phi, we need triangles (higher order).
            # If Response connects to Context, and Context connects to Neighbor 1...
            # Does Response connect to Neighbor 1?
            # If so, we form a triangle (2-simplex).
            # Let's optimistically assume if Response is very close to Context,
            # and Context is very close to Neighbor, they might form a triangle.
            # (Transitivity assumption for performance).

            if sim_response_context > 0.6:  # Stronger requirement for transitivity
                for i, hit in enumerate(hits):
                    if hit.score > 0.6:
                        node_id = i + 1
                        # Add Triangle: (Context, Neighbor, Response)
                        complex_after.add_simplex((0, node_id, response_node_id))

            # Calculate Phi After
            calculator_after = PhiCalculator(complex_after)
            phi_after_res = calculator_after.calculate_phi_with_unconscious()
            phi_after = phi_after_res.conscious_phi

            return max(0.0, phi_after - phi_before)

        except Exception as e:
            logger.warning(f"Error calculating Delta Phi: {e}")
            return 0.0
