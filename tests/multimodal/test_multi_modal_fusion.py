"""Tests for Multi-Modal Fusion (Phase 12.3)."""

from datetime import datetime, timedelta

import pytest

from src.multimodal.multi_modal_fusion import (
    AttentionWeights,
    CrossModalMatch,
    CrossModalQuery,
    FusedRepresentation,
    FusionStrategy,
    Modality,
    ModalityInput,
    MultiModalFusion,
)


class TestModalityInput:
    """Tests for ModalityInput dataclass."""

    def test_create_modality_input(self) -> None:
        """Test creating modality input."""
        features = {"feature1": 0.5, "feature2": 0.8}
        inp = ModalityInput(
            modality=Modality.VISION,
            features=features,
            confidence=0.9,
            metadata={"source": "camera"},
        )

        assert inp.modality == Modality.VISION
        assert inp.features == features
        assert inp.confidence == 0.9
        assert inp.metadata["source"] == "camera"

    def test_modality_input_validation(self) -> None:
        """Test modality input validation."""
        # Valid input
        ModalityInput(modality=Modality.AUDIO, features={}, confidence=0.8)

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            ModalityInput(modality=Modality.AUDIO, features={}, confidence=1.5)


class TestAttentionWeights:
    """Tests for AttentionWeights dataclass."""

    def test_create_attention_weights(self) -> None:
        """Test creating attention weights."""
        weights = AttentionWeights(
            weights={Modality.VISION: 0.6, Modality.AUDIO: 0.4},
            strategy="learned",
            confidence=0.9,
        )

        assert abs(weights.get_weight(Modality.VISION) - 0.6) < 0.01
        assert abs(weights.get_weight(Modality.AUDIO) - 0.4) < 0.01
        assert weights.strategy == "learned"

    def test_attention_weights_normalization(self) -> None:
        """Test that attention weights are normalized."""
        weights = AttentionWeights(
            weights={Modality.VISION: 2.0, Modality.AUDIO: 3.0}
        )

        # Should be normalized to sum to 1.0
        total = weights.get_weight(Modality.VISION) + weights.get_weight(
            Modality.AUDIO
        )
        assert abs(total - 1.0) < 1e-10

    def test_attention_weights_validation(self) -> None:
        """Test attention weights validation."""
        # Valid weights
        AttentionWeights(weights={}, confidence=0.8)

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            AttentionWeights(weights={}, confidence=1.5)

    def test_get_weight_missing_modality(self) -> None:
        """Test getting weight for non-existent modality."""
        weights = AttentionWeights(weights={Modality.VISION: 1.0})

        assert weights.get_weight(Modality.AUDIO) == 0.0


class TestFusedRepresentation:
    """Tests for FusedRepresentation dataclass."""

    def test_create_fused_representation(self) -> None:
        """Test creating fused representation."""
        features = {"fused_feat1": 0.7, "fused_feat2": 0.3}
        attention = AttentionWeights(weights={Modality.VISION: 1.0})

        fused = FusedRepresentation(
            features=features,
            modalities_used=[Modality.VISION, Modality.AUDIO],
            fusion_strategy=FusionStrategy.HYBRID,
            attention_weights=attention,
            confidence=0.85,
            interpretation="Fused vision and audio",
        )

        assert fused.features == features
        assert len(fused.modalities_used) == 2
        assert fused.fusion_strategy == FusionStrategy.HYBRID
        assert fused.confidence == 0.85

    def test_fused_representation_validation(self) -> None:
        """Test fused representation validation."""
        attention = AttentionWeights(weights={})

        # Valid representation
        FusedRepresentation(
            features={},
            modalities_used=[],
            fusion_strategy=FusionStrategy.EARLY,
            attention_weights=attention,
            confidence=0.9,
        )

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            FusedRepresentation(
                features={},
                modalities_used=[],
                fusion_strategy=FusionStrategy.EARLY,
                attention_weights=attention,
                confidence=1.5,
            )


class TestCrossModalQuery:
    """Tests for CrossModalQuery dataclass."""

    def test_create_cross_modal_query(self) -> None:
        """Test creating cross-modal query."""
        query = CrossModalQuery(
            query_text="Find matching audio",
            source_modality=Modality.VISION,
            target_modalities=[Modality.AUDIO, Modality.TEXT],
            max_results=5,
        )

        assert query.query_text == "Find matching audio"
        assert query.source_modality == Modality.VISION
        assert len(query.target_modalities) == 2
        assert query.max_results == 5

    def test_cross_modal_query_validation(self) -> None:
        """Test cross-modal query validation."""
        # Valid query
        CrossModalQuery(
            query_text="test", source_modality=Modality.TEXT, max_results=10
        )

        # Invalid max_results
        with pytest.raises(ValueError, match="Max results must be"):
            CrossModalQuery(
                query_text="test", source_modality=Modality.TEXT, max_results=0
            )


class TestCrossModalMatch:
    """Tests for CrossModalMatch dataclass."""

    def test_create_cross_modal_match(self) -> None:
        """Test creating cross-modal match."""
        match = CrossModalMatch(
            query_modality=Modality.VISION,
            match_modality=Modality.AUDIO,
            similarity=0.85,
            matched_features={"feature1": 0.5},
            interpretation="Vision matched audio",
        )

        assert match.query_modality == Modality.VISION
        assert match.match_modality == Modality.AUDIO
        assert match.similarity == 0.85
        assert match.interpretation == "Vision matched audio"

    def test_cross_modal_match_validation(self) -> None:
        """Test cross-modal match validation."""
        # Valid match
        CrossModalMatch(
            query_modality=Modality.TEXT,
            match_modality=Modality.VISION,
            similarity=0.9,
            matched_features={},
        )

        # Invalid similarity
        with pytest.raises(ValueError, match="Similarity must be"):
            CrossModalMatch(
                query_modality=Modality.TEXT,
                match_modality=Modality.VISION,
                similarity=1.5,
                matched_features={},
            )


class TestMultiModalFusion:
    """Tests for MultiModalFusion class."""

    def test_multimodal_fusion_initialization(self) -> None:
        """Test multi-modal fusion initialization."""
        fusion = MultiModalFusion(
            default_strategy=FusionStrategy.LATE, enable_attention=False
        )

        assert fusion.default_strategy == FusionStrategy.LATE
        assert fusion.enable_attention is False

    def test_fuse_modalities_single(self) -> None:
        """Test fusing a single modality."""
        fusion = MultiModalFusion()

        vision_input = ModalityInput(
            modality=Modality.VISION,
            features={"brightness": 0.7, "contrast": 0.5},
            confidence=0.9,
        )

        fused = fusion.fuse_modalities([vision_input])

        assert isinstance(fused, FusedRepresentation)
        assert Modality.VISION in fused.modalities_used
        assert len(fused.features) > 0
        assert 0.0 <= fused.confidence <= 1.0

    def test_fuse_modalities_multiple(self) -> None:
        """Test fusing multiple modalities."""
        fusion = MultiModalFusion()

        vision_input = ModalityInput(
            modality=Modality.VISION,
            features={"brightness": 0.7},
            confidence=0.9,
        )

        audio_input = ModalityInput(
            modality=Modality.AUDIO,
            features={"volume": 0.5},
            confidence=0.8,
        )

        fused = fusion.fuse_modalities([vision_input, audio_input])

        assert len(fused.modalities_used) == 2
        assert Modality.VISION in fused.modalities_used
        assert Modality.AUDIO in fused.modalities_used
        assert len(fused.features) > 0

    def test_fuse_modalities_empty(self) -> None:
        """Test that empty input list raises error."""
        fusion = MultiModalFusion()

        with pytest.raises(ValueError, match="At least one modality"):
            fusion.fuse_modalities([])

    def test_fuse_modalities_early_strategy(self) -> None:
        """Test early fusion strategy."""
        fusion = MultiModalFusion()

        inputs = [
            ModalityInput(
                modality=Modality.VISION, features={"feat1": 0.5}, confidence=0.9
            ),
            ModalityInput(
                modality=Modality.AUDIO, features={"feat2": 0.7}, confidence=0.8
            ),
        ]

        fused = fusion.fuse_modalities(inputs, strategy=FusionStrategy.EARLY)

        assert fused.fusion_strategy == FusionStrategy.EARLY
        # Early fusion should have modality-prefixed features
        feature_keys = list(fused.features.keys())
        assert any("vision" in key.lower() for key in feature_keys) or any(
            "audio" in key.lower() for key in feature_keys
        )

    def test_fuse_modalities_late_strategy(self) -> None:
        """Test late fusion strategy."""
        fusion = MultiModalFusion()

        inputs = [
            ModalityInput(
                modality=Modality.VISION, features={"feat1": 0.5}, confidence=0.9
            ),
            ModalityInput(
                modality=Modality.AUDIO, features={"feat1": 0.7}, confidence=0.8
            ),
        ]

        fused = fusion.fuse_modalities(inputs, strategy=FusionStrategy.LATE)

        assert fused.fusion_strategy == FusionStrategy.LATE
        assert len(fused.features) > 0

    def test_fuse_modalities_hybrid_strategy(self) -> None:
        """Test hybrid fusion strategy."""
        fusion = MultiModalFusion()

        inputs = [
            ModalityInput(
                modality=Modality.VISION, features={"feat1": 0.5}, confidence=0.9
            ),
        ]

        fused = fusion.fuse_modalities(inputs, strategy=FusionStrategy.HYBRID)

        assert fused.fusion_strategy == FusionStrategy.HYBRID

    def test_cross_modal_query_basic(self) -> None:
        """Test basic cross-modal query."""
        fusion = MultiModalFusion()

        query = CrossModalQuery(
            query_text="Find audio matching this image",
            source_modality=Modality.VISION,
            target_modalities=[Modality.AUDIO],
            max_results=3,
        )

        available = [
            ModalityInput(
                modality=Modality.AUDIO, features={"feat1": 0.5}, confidence=0.9
            ),
            ModalityInput(
                modality=Modality.AUDIO, features={"feat2": 0.7}, confidence=0.8
            ),
        ]

        matches = fusion.cross_modal_query(query, available)

        assert isinstance(matches, list)
        assert len(matches) <= 3
        for match in matches:
            assert isinstance(match, CrossModalMatch)
            assert match.match_modality == Modality.AUDIO
            assert 0.0 <= match.similarity <= 1.0

    def test_cross_modal_query_no_targets(self) -> None:
        """Test cross-modal query without specific target modalities."""
        fusion = MultiModalFusion()

        query = CrossModalQuery(
            query_text="Find anything", source_modality=Modality.VISION
        )

        available = [
            ModalityInput(modality=Modality.AUDIO, features={}, confidence=0.9),
            ModalityInput(modality=Modality.TEXT, features={}, confidence=0.8),
        ]

        matches = fusion.cross_modal_query(query, available)

        # Should find non-vision modalities
        assert len(matches) > 0

    def test_align_modalities(self) -> None:
        """Test modality alignment."""
        fusion = MultiModalFusion()

        vision = ModalityInput(
            modality=Modality.VISION, features={"feat1": 0.5}, confidence=0.9
        )

        audio = ModalityInput(
            modality=Modality.AUDIO, features={"feat1": 0.6}, confidence=0.8
        )

        alignments = fusion.align_modalities(vision_input=vision, audio_input=audio)

        assert isinstance(alignments, dict)
        assert len(alignments) > 0
        # Check that alignment score exists
        assert any("vision" in key.lower() and "audio" in key.lower() for key in alignments.keys())

    def test_align_modalities_insufficient_inputs(self) -> None:
        """Test alignment with insufficient inputs."""
        fusion = MultiModalFusion()

        vision = ModalityInput(modality=Modality.VISION, features={}, confidence=0.9)

        alignments = fusion.align_modalities(vision_input=vision)

        # Should return empty dict with only one modality
        assert alignments == {}

    def test_align_modalities_all_three(self) -> None:
        """Test aligning all three modalities."""
        fusion = MultiModalFusion()

        vision = ModalityInput(modality=Modality.VISION, features={}, confidence=0.9)
        audio = ModalityInput(modality=Modality.AUDIO, features={}, confidence=0.8)
        text = ModalityInput(modality=Modality.TEXT, features={}, confidence=0.7)

        alignments = fusion.align_modalities(
            vision_input=vision, audio_input=audio, text_input=text
        )

        # Should have 3 pairwise alignments (vision-audio, vision-text, audio-text)
        assert len(alignments) == 3

    def test_attention_weighting(self) -> None:
        """Test that attention weights are applied."""
        fusion = MultiModalFusion(enable_attention=True)

        inputs = [
            ModalityInput(
                modality=Modality.VISION, features={"feat1": 0.5}, confidence=1.0
            ),
            ModalityInput(
                modality=Modality.AUDIO, features={"feat1": 0.7}, confidence=0.5
            ),
        ]

        fused = fusion.fuse_modalities(inputs)

        # Attention weights should reflect confidence
        assert fused.attention_weights.get_weight(Modality.VISION) > 0
        assert fused.attention_weights.get_weight(Modality.AUDIO) > 0

    def test_no_attention_weighting(self) -> None:
        """Test uniform weighting when attention is disabled."""
        fusion = MultiModalFusion(enable_attention=False)

        inputs = [
            ModalityInput(
                modality=Modality.VISION, features={"feat1": 0.5}, confidence=1.0
            ),
            ModalityInput(
                modality=Modality.AUDIO, features={"feat1": 0.7}, confidence=0.3
            ),
        ]

        fused = fusion.fuse_modalities(inputs)

        # Should use uniform strategy
        assert fused.attention_weights.strategy == "uniform"

    def test_modality_history(self) -> None:
        """Test modality history tracking."""
        fusion = MultiModalFusion()

        vision = ModalityInput(modality=Modality.VISION, features={}, confidence=0.9)
        audio = ModalityInput(modality=Modality.AUDIO, features={}, confidence=0.8)

        fusion.fuse_modalities([vision, audio])

        history = fusion.get_modality_history()
        assert len(history) == 2

        vision_history = fusion.get_modality_history(modality=Modality.VISION)
        assert len(vision_history) == 1
        assert vision_history[0].modality == Modality.VISION

    def test_clear_history(self) -> None:
        """Test clearing modality history."""
        fusion = MultiModalFusion()

        vision = ModalityInput(modality=Modality.VISION, features={}, confidence=0.9)
        fusion.fuse_modalities([vision])

        assert len(fusion.get_modality_history()) == 1

        fusion.clear_history()

        assert len(fusion.get_modality_history()) == 0
