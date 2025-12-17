"""Multi-Modal Fusion Implementation (Phase 12.3).

Implements cross-modal reasoning and fusion capabilities:
- Early fusion (feature-level integration)
- Late fusion (decision-level integration)
- Hybrid fusion (combination of early and late)
- Attention mechanisms for modal weighting
- Cross-modal understanding and reasoning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


class FusionStrategy(Enum):
    """Strategies for multi-modal fusion."""

    EARLY = "early"  # Feature-level fusion
    LATE = "late"  # Decision-level fusion
    HYBRID = "hybrid"  # Combination of early and late
    ATTENTION = "attention"  # Attention-weighted fusion


class Modality(Enum):
    """Supported modalities."""

    VISION = "vision"
    AUDIO = "audio"
    TEXT = "text"
    PROPRIOCEPTION = "proprioception"


@dataclass
class ModalityInput:
    """Input from a specific modality.

    Attributes:
        modality: The modality type
        features: Extracted features (normalized)
        raw_data: Optional raw data
        confidence: Confidence in this input (0.0-1.0)
        timestamp: When input was captured
        metadata: Additional metadata
    """

    modality: Modality
    features: Dict[str, float]
    raw_data: Optional[Any] = None
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate modality input."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class AttentionWeights:
    """Attention weights for modalities.

    Attributes:
        weights: Mapping from modality to attention weight
        strategy: How weights were computed
        confidence: Confidence in attention computation (0.0-1.0)
    """

    weights: Dict[Modality, float] = field(default_factory=dict)
    strategy: str = "uniform"
    confidence: float = 1.0

    def __post_init__(self) -> None:
        """Validate and normalize attention weights."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        # Normalize weights to sum to 1.0
        if self.weights:
            total = sum(self.weights.values())
            if total > 0:
                self.weights = {mod: weight / total for mod, weight in self.weights.items()}

    def get_weight(self, modality: Modality) -> float:
        """Get attention weight for a modality."""
        return self.weights.get(modality, 0.0)


@dataclass
class FusedRepresentation:
    """Fused multi-modal representation.

    Attributes:
        features: Fused feature vector
        modalities_used: Which modalities contributed
        fusion_strategy: Strategy used for fusion
        attention_weights: Attention weights applied
        confidence: Overall confidence (0.0-1.0)
        interpretation: Natural language interpretation
        timestamp: When fusion was performed
    """

    features: Dict[str, float]
    modalities_used: List[Modality]
    fusion_strategy: FusionStrategy
    attention_weights: AttentionWeights
    confidence: float
    interpretation: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate fused representation."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class CrossModalQuery:
    """Query for cross-modal understanding.

    Attributes:
        query_text: Natural language query
        source_modality: Primary modality for query
        target_modalities: Modalities to search/match
        context: Additional context
        max_results: Maximum number of results
    """

    query_text: str
    source_modality: Modality
    target_modalities: List[Modality] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 10

    def __post_init__(self) -> None:
        """Validate cross-modal query."""
        if self.max_results <= 0:
            raise ValueError("Max results must be positive")


@dataclass
class CrossModalMatch:
    """Result of cross-modal matching.

    Attributes:
        query_modality: Source modality
        match_modality: Matched modality
        similarity: Similarity score (0.0-1.0)
        matched_features: Features of the match
        interpretation: Natural language interpretation
    """

    query_modality: Modality
    match_modality: Modality
    similarity: float
    matched_features: Dict[str, Any]
    interpretation: str = ""

    def __post_init__(self) -> None:
        """Validate cross-modal match."""
        if not 0.0 <= self.similarity <= 1.0:
            raise ValueError("Similarity must be between 0.0 and 1.0")


class MultiModalFusion:
    """Multi-modal fusion engine for cross-modal understanding.

    This implementation provides:
    - Feature-level fusion (early fusion)
    - Decision-level fusion (late fusion)
    - Hybrid fusion strategies
    - Attention-based modal weighting
    - Cross-modal reasoning and matching
    - Integration with vision and audio processors

    Note: Uses simulated fusion for local-first operation.
    Can be enhanced with actual multi-modal models later.
    """

    def __init__(
        self,
        default_strategy: FusionStrategy = FusionStrategy.HYBRID,
        enable_attention: bool = True,
    ) -> None:
        """Initialize multi-modal fusion engine.

        Args:
            default_strategy: Default fusion strategy to use
            enable_attention: Whether to use attention weighting
        """
        self.default_strategy = default_strategy
        self.enable_attention = enable_attention
        self._fusion_cache: Dict[str, FusedRepresentation] = {}
        self._modality_history: List[ModalityInput] = []

        logger.info(
            "multimodal_fusion_initialized",
            strategy=default_strategy.value,
            attention=enable_attention,
        )

    def fuse_modalities(
        self,
        inputs: List[ModalityInput],
        strategy: Optional[FusionStrategy] = None,
    ) -> FusedRepresentation:
        """Fuse multiple modality inputs into unified representation.

        Args:
            inputs: List of modality inputs to fuse
            strategy: Optional fusion strategy (uses default if not provided)

        Returns:
            FusedRepresentation combining all inputs
        """
        if not inputs:
            raise ValueError("At least one modality input required")

        fusion_strategy = strategy or self.default_strategy

        logger.info(
            "fusing_modalities",
            num_inputs=len(inputs),
            modalities=[inp.modality.value for inp in inputs],
            strategy=fusion_strategy.value,
        )

        # Store in history
        self._modality_history.extend(inputs)

        # Compute attention weights
        attention = self._compute_attention_weights(inputs)

        # Perform fusion based on strategy
        if fusion_strategy == FusionStrategy.EARLY:
            fused_features = self._early_fusion(inputs, attention)
        elif fusion_strategy == FusionStrategy.LATE:
            fused_features = self._late_fusion(inputs, attention)
        elif fusion_strategy == FusionStrategy.HYBRID:
            fused_features = self._hybrid_fusion(inputs, attention)
        else:  # ATTENTION
            fused_features = self._attention_fusion(inputs, attention)

        # Calculate overall confidence
        weighted_conf = sum(inp.confidence * attention.get_weight(inp.modality) for inp in inputs)

        # Generate interpretation
        interpretation = self._generate_interpretation(inputs, fused_features)

        fused = FusedRepresentation(
            features=fused_features,
            modalities_used=[inp.modality for inp in inputs],
            fusion_strategy=fusion_strategy,
            attention_weights=attention,
            confidence=weighted_conf,
            interpretation=interpretation,
        )

        logger.info(
            "modalities_fused",
            num_features=len(fused_features),
            confidence=fused.confidence,
        )

        return fused

    def cross_modal_query(
        self,
        query: CrossModalQuery,
        available_inputs: List[ModalityInput],
    ) -> List[CrossModalMatch]:
        """Perform cross-modal query to find matches.

        Args:
            query: Cross-modal query specification
            available_inputs: Available modality inputs to search

        Returns:
            List of CrossModalMatch results
        """
        logger.info(
            "cross_modal_query",
            query_text=query.query_text,
            source=query.source_modality.value,
            targets=[m.value for m in query.target_modalities],
        )

        # Filter inputs by target modalities
        if query.target_modalities:
            candidates = [
                inp for inp in available_inputs if inp.modality in query.target_modalities
            ]
        else:
            candidates = [inp for inp in available_inputs if inp.modality != query.source_modality]

        # Compute cross-modal similarities
        matches: List[CrossModalMatch] = []

        for candidate in candidates:
            similarity = self._compute_cross_modal_similarity(
                query.source_modality,
                candidate.modality,
                query.context,
                candidate.features,
            )

            interpretation = self._interpret_cross_modal_match(query, candidate, similarity)

            match = CrossModalMatch(
                query_modality=query.source_modality,
                match_modality=candidate.modality,
                similarity=similarity,
                matched_features=candidate.features,
                interpretation=interpretation,
            )
            matches.append(match)

        # Sort by similarity and limit results
        matches.sort(key=lambda m: m.similarity, reverse=True)
        matches = matches[: query.max_results]

        logger.info(
            "cross_modal_query_complete",
            num_matches=len(matches),
            top_similarity=matches[0].similarity if matches else 0.0,
        )

        return matches

    def align_modalities(
        self,
        vision_input: Optional[ModalityInput] = None,
        audio_input: Optional[ModalityInput] = None,
        text_input: Optional[ModalityInput] = None,
    ) -> Dict[str, float]:
        """Align different modalities to find correspondences.

        Args:
            vision_input: Optional vision modality input
            audio_input: Optional audio modality input
            text_input: Optional text modality input

        Returns:
            Alignment scores between modality pairs
        """
        logger.info("aligning_modalities")

        inputs = []
        if vision_input:
            inputs.append(vision_input)
        if audio_input:
            inputs.append(audio_input)
        if text_input:
            inputs.append(text_input)

        if len(inputs) < 2:
            return {}

        # Compute pairwise alignment scores
        alignments: Dict[str, float] = {}

        for i, inp1 in enumerate(inputs):
            for inp2 in inputs[i + 1 :]:
                pair_key = f"{inp1.modality.value}_to_{inp2.modality.value}"
                alignment = self._compute_alignment_score(inp1, inp2)
                alignments[pair_key] = alignment

        logger.info("modalities_aligned", num_alignments=len(alignments))

        return alignments

    def _compute_attention_weights(self, inputs: List[ModalityInput]) -> AttentionWeights:
        """Compute attention weights for modality inputs."""
        weights: Dict[Modality, float] = {}

        if not self.enable_attention:
            # Uniform weights
            weights = {inp.modality: 1.0 / len(inputs) for inp in inputs}
            return AttentionWeights(weights=weights, strategy="uniform")

        # Compute attention based on confidence and recency
        for inp in inputs:
            # Weight = confidence * recency_factor
            # (simulated: in production, use learned attention)
            weight = inp.confidence
            weights[inp.modality] = weight

        return AttentionWeights(weights=weights, strategy="confidence_based", confidence=0.9)

    def _early_fusion(
        self, inputs: List[ModalityInput], attention: AttentionWeights
    ) -> Dict[str, float]:
        """Perform early (feature-level) fusion."""
        # Concatenate all features with attention weighting
        fused: Dict[str, float] = {}

        for inp in inputs:
            weight = attention.get_weight(inp.modality)
            prefix = inp.modality.value

            for key, value in inp.features.items():
                fused[f"{prefix}_{key}"] = value * weight

        return fused

    def _late_fusion(
        self, inputs: List[ModalityInput], attention: AttentionWeights
    ) -> Dict[str, float]:
        """Perform late (decision-level) fusion."""
        # Simulate decisions from each modality, then combine
        fused: Dict[str, float] = {}

        # Aggregate features by type
        feature_groups: Dict[str, List[Tuple[float, float]]] = {}

        for inp in inputs:
            weight = attention.get_weight(inp.modality)
            for key, value in inp.features.items():
                if key not in feature_groups:
                    feature_groups[key] = []
                feature_groups[key].append((value, weight))

        # Weighted average for each feature type
        for key, values_weights in feature_groups.items():
            weighted_sum = sum(val * weight for val, weight in values_weights)
            fused[key] = weighted_sum

        return fused

    def _hybrid_fusion(
        self, inputs: List[ModalityInput], attention: AttentionWeights
    ) -> Dict[str, float]:
        """Perform hybrid fusion (combine early and late)."""
        # Combine both early and late fusion strategies
        early = self._early_fusion(inputs, attention)
        late = self._late_fusion(inputs, attention)

        # Merge with averaging
        fused: Dict[str, float] = {}

        # Add all early fusion features
        for key, value in early.items():
            fused[f"early_{key}"] = value

        # Add all late fusion features
        for key, value in late.items():
            fused[f"late_{key}"] = value

        return fused

    def _attention_fusion(
        self, inputs: List[ModalityInput], attention: AttentionWeights
    ) -> Dict[str, float]:
        """Perform attention-weighted fusion."""
        # Similar to late fusion but with explicit attention mechanism
        return self._late_fusion(inputs, attention)

    def _compute_cross_modal_similarity(
        self,
        source_modality: Modality,
        target_modality: Modality,
        query_context: Dict[str, Any],
        target_features: Dict[str, float],
    ) -> float:
        """Compute similarity across modalities."""
        # Simulate cross-modal similarity
        # In production, use learned cross-modal embeddings

        # Use context to boost similarity
        context_boost = len(query_context) * 0.1

        # Feature overlap (if any common feature names)
        overlap = 0.0
        if query_context:
            context_features = {
                k: v for k, v in query_context.items() if isinstance(v, (int, float))
            }
            if context_features and target_features:
                common_keys = set(context_features.keys()) & set(target_features.keys())
                if common_keys:
                    # Calculate similarity for common features
                    diffs = [abs(context_features[k] - target_features[k]) for k in common_keys]
                    overlap = 1.0 - (sum(diffs) / len(diffs))

        # Base similarity depends on modality compatibility
        base_similarity = 0.5

        # Boost for compatible modality pairs
        compatible_pairs = {
            (Modality.VISION, Modality.TEXT),
            (Modality.AUDIO, Modality.TEXT),
            (Modality.VISION, Modality.AUDIO),
        }

        if (source_modality, target_modality) in compatible_pairs or (
            target_modality,
            source_modality,
        ) in compatible_pairs:
            base_similarity = 0.7

        similarity = min(1.0, base_similarity + context_boost + overlap * 0.3)

        return similarity

    def _compute_alignment_score(self, inp1: ModalityInput, inp2: ModalityInput) -> float:
        """Compute temporal/spatial alignment between modalities."""
        # Check temporal alignment
        time_diff = abs((inp1.timestamp - inp2.timestamp).total_seconds())
        temporal_score = max(0.0, 1.0 - time_diff / 10.0)  # Decay over 10 seconds

        # Check feature similarity
        common_keys = set(inp1.features.keys()) & set(inp2.features.keys())
        if common_keys:
            diffs = [abs(inp1.features[k] - inp2.features[k]) for k in common_keys]
            feature_similarity = 1.0 - (sum(diffs) / len(diffs))
        else:
            feature_similarity = 0.5

        # Combined alignment score
        alignment = (temporal_score + feature_similarity) / 2.0

        return alignment

    def _generate_interpretation(
        self, inputs: List[ModalityInput], fused_features: Dict[str, float]
    ) -> str:
        """Generate natural language interpretation of fusion."""
        modalities = [inp.modality.value for inp in inputs]

        if len(modalities) == 1:
            return f"Single {modalities[0]} input processed"
        elif len(modalities) == 2:
            return f"Fused {modalities[0]} and {modalities[1]} modalities"
        else:
            return f"Fused {len(modalities)} modalities: {', '.join(modalities)}"

    def _interpret_cross_modal_match(
        self, query: CrossModalQuery, candidate: ModalityInput, similarity: float
    ) -> str:
        """Generate interpretation for cross-modal match."""
        return (
            f"Query from {query.source_modality.value} matched "
            f"{candidate.modality.value} with {similarity:.2f} similarity"
        )

    def clear_history(self) -> None:
        """Clear modality input history."""
        count = len(self._modality_history)
        self._modality_history.clear()
        logger.info("history_cleared", cleared_count=count)

    def get_modality_history(self, modality: Optional[Modality] = None) -> List[ModalityInput]:
        """Get modality input history.

        Args:
            modality: Optional filter by specific modality

        Returns:
            List of ModalityInput objects
        """
        if modality:
            return [inp for inp in self._modality_history if inp.modality == modality]
        return list(self._modality_history)
