"""Tests for Vision Processor (Phase 12.1)."""

import pytest

from src.multimodal.vision_processor import (
    BoundingBox,
    DetectedObject,
    ObjectCategory,
    SceneAnalysis,
    SceneType,
    VideoFrame,
    VisionFeatures,
    VisionProcessor,
)


class TestBoundingBox:
    """Tests for BoundingBox dataclass."""

    def test_create_bounding_box(self) -> None:
        """Test creating a valid bounding box."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)

        assert bbox.x == 0.1
        assert bbox.y == 0.2
        assert bbox.width == 0.3
        assert bbox.height == 0.4

    def test_bounding_box_validation(self) -> None:
        """Test bounding box coordinate validation."""
        # Valid bbox
        BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0)

        # Invalid x
        with pytest.raises(ValueError, match="x must be between"):
            BoundingBox(x=1.5, y=0.0, width=0.5, height=0.5)

        # Invalid width
        with pytest.raises(ValueError, match="width must be between"):
            BoundingBox(x=0.0, y=0.0, width=-0.1, height=0.5)

    def test_bounding_box_area(self) -> None:
        """Test bounding box area calculation."""
        bbox = BoundingBox(x=0.0, y=0.0, width=0.5, height=0.4)
        assert bbox.area() == 0.2

    def test_bounding_box_center(self) -> None:
        """Test bounding box center calculation."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.4, height=0.6)
        center = bbox.center()
        assert abs(center[0] - 0.3) < 1e-10
        assert abs(center[1] - 0.5) < 1e-10


class TestDetectedObject:
    """Tests for DetectedObject dataclass."""

    def test_create_detected_object(self) -> None:
        """Test creating a detected object."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
        obj = DetectedObject(
            category=ObjectCategory.PERSON,
            label="person_1",
            confidence=0.95,
            bounding_box=bbox,
            attributes={"age": "adult", "gender": "unknown"},
        )

        assert obj.category == ObjectCategory.PERSON
        assert obj.label == "person_1"
        assert obj.confidence == 0.95
        assert obj.bounding_box == bbox
        assert obj.attributes["age"] == "adult"

    def test_detected_object_confidence_validation(self) -> None:
        """Test confidence validation."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)

        # Valid confidence
        DetectedObject(
            category=ObjectCategory.ANIMAL,
            label="cat",
            confidence=0.85,
            bounding_box=bbox,
        )

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            DetectedObject(
                category=ObjectCategory.ANIMAL,
                label="cat",
                confidence=1.5,
                bounding_box=bbox,
            )


class TestSceneAnalysis:
    """Tests for SceneAnalysis dataclass."""

    def test_create_scene_analysis(self) -> None:
        """Test creating scene analysis."""
        bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
        obj = DetectedObject(
            category=ObjectCategory.BUILDING,
            label="house",
            confidence=0.9,
            bounding_box=bbox,
        )

        analysis = SceneAnalysis(
            scene_type=SceneType.OUTDOOR,
            objects=[obj],
            dominant_colors=[(255, 0, 0), (0, 255, 0)],
            lighting="bright",
            complexity=0.7,
            description="An outdoor scene with a house",
        )

        assert analysis.scene_type == SceneType.OUTDOOR
        assert len(analysis.objects) == 1
        assert len(analysis.dominant_colors) == 2
        assert analysis.complexity == 0.7

    def test_scene_analysis_complexity_validation(self) -> None:
        """Test complexity validation."""
        # Valid complexity
        SceneAnalysis(scene_type=SceneType.INDOOR, complexity=0.5)

        # Invalid complexity
        with pytest.raises(ValueError, match="Complexity must be"):
            SceneAnalysis(scene_type=SceneType.INDOOR, complexity=1.5)


class TestVideoFrame:
    """Tests for VideoFrame dataclass."""

    def test_create_video_frame(self) -> None:
        """Test creating video frame."""
        frame = VideoFrame(
            frame_number=42,
            timestamp=1.4,
            image_hash="abc123",
            motion_score=0.6,
        )

        assert frame.frame_number == 42
        assert frame.timestamp == 1.4
        assert frame.image_hash == "abc123"
        assert frame.motion_score == 0.6

    def test_video_frame_validation(self) -> None:
        """Test video frame validation."""
        # Valid frame
        VideoFrame(frame_number=0, timestamp=0.0, image_hash="test")

        # Invalid frame number
        with pytest.raises(ValueError, match="Frame number must be"):
            VideoFrame(frame_number=-1, timestamp=0.0, image_hash="test")

        # Invalid timestamp
        with pytest.raises(ValueError, match="Timestamp must be"):
            VideoFrame(frame_number=0, timestamp=-1.0, image_hash="test")

        # Invalid motion score
        with pytest.raises(ValueError, match="Motion score must be"):
            VideoFrame(
                frame_number=0, timestamp=0.0, image_hash="test", motion_score=1.5
            )


class TestVisionFeatures:
    """Tests for VisionFeatures dataclass."""

    def test_create_vision_features(self) -> None:
        """Test creating vision features."""
        features = VisionFeatures(
            edge_density=0.7,
            texture_complexity=0.8,
            color_diversity=0.6,
            symmetry=0.5,
            spatial_layout={"top": 0.9, "bottom": 0.3},
        )

        assert features.edge_density == 0.7
        assert features.texture_complexity == 0.8
        assert features.color_diversity == 0.6
        assert features.symmetry == 0.5
        assert features.spatial_layout["top"] == 0.9

    def test_vision_features_validation(self) -> None:
        """Test vision features validation."""
        # Valid features
        VisionFeatures(
            edge_density=0.5,
            texture_complexity=0.5,
            color_diversity=0.5,
            symmetry=0.5,
        )

        # Invalid edge density
        with pytest.raises(ValueError, match="edge_density must be"):
            VisionFeatures(
                edge_density=1.5,
                texture_complexity=0.5,
                color_diversity=0.5,
                symmetry=0.5,
            )


class TestVisionProcessor:
    """Tests for VisionProcessor class."""

    def test_vision_processor_initialization(self) -> None:
        """Test vision processor initialization."""
        processor = VisionProcessor(max_objects_per_image=15, confidence_threshold=0.6)

        assert processor.max_objects_per_image == 15
        assert processor.confidence_threshold == 0.6

    def test_analyze_image(self) -> None:
        """Test image analysis."""
        processor = VisionProcessor()
        image_data = b"fake_image_data" * 100

        analysis = processor.analyze_image(image_data)

        assert isinstance(analysis, SceneAnalysis)
        assert isinstance(analysis.scene_type, SceneType)
        assert isinstance(analysis.objects, list)
        assert len(analysis.dominant_colors) > 0
        assert 0.0 <= analysis.complexity <= 1.0
        assert analysis.description != ""

    def test_analyze_image_with_id(self) -> None:
        """Test image analysis with custom ID."""
        processor = VisionProcessor()
        image_data = b"test_image_data" * 50

        analysis = processor.analyze_image(image_data, image_id="custom_id")

        assert isinstance(analysis, SceneAnalysis)
        cached = processor.get_cached_analysis("custom_id")
        assert cached is not None
        assert cached.scene_type == analysis.scene_type

    def test_analyze_image_object_detection(self) -> None:
        """Test that objects are detected in image."""
        processor = VisionProcessor(max_objects_per_image=10, confidence_threshold=0.5)
        image_data = b"image_with_objects" * 200

        analysis = processor.analyze_image(image_data)

        assert len(analysis.objects) > 0
        assert len(analysis.objects) <= 10  # Respects max_objects limit

        for obj in analysis.objects:
            assert isinstance(obj, DetectedObject)
            assert obj.confidence >= 0.5  # Respects confidence threshold
            assert isinstance(obj.category, ObjectCategory)
            assert isinstance(obj.bounding_box, BoundingBox)

    def test_process_video(self) -> None:
        """Test video processing."""
        processor = VisionProcessor()
        video_data = b"fake_video_data" * 10000

        frames = processor.process_video(video_data, fps=30, sample_rate=5)

        assert isinstance(frames, list)
        assert len(frames) > 0

        for frame in frames:
            assert isinstance(frame, VideoFrame)
            assert frame.frame_number >= 0
            assert frame.timestamp >= 0.0
            assert frame.image_hash != ""
            assert 0.0 <= frame.motion_score <= 1.0

    def test_process_video_sampling(self) -> None:
        """Test video frame sampling."""
        processor = VisionProcessor()
        video_data = b"video_data" * 5000

        # Sample every frame
        frames_all = processor.process_video(video_data, fps=30, sample_rate=1)

        # Sample every 10th frame
        frames_sampled = processor.process_video(video_data, fps=30, sample_rate=10)

        # Sampled should have fewer frames
        assert len(frames_sampled) < len(frames_all)

    def test_extract_features(self) -> None:
        """Test vision feature extraction."""
        processor = VisionProcessor()
        image_data = b"feature_extraction_test" * 100

        features = processor.extract_features(image_data)

        assert isinstance(features, VisionFeatures)
        assert 0.0 <= features.edge_density <= 1.0
        assert 0.0 <= features.texture_complexity <= 1.0
        assert 0.0 <= features.color_diversity <= 1.0
        assert 0.0 <= features.symmetry <= 1.0
        assert isinstance(features.spatial_layout, dict)

    def test_compare_images(self) -> None:
        """Test image comparison."""
        processor = VisionProcessor()
        image1 = b"identical_image_data" * 100
        image2 = b"identical_image_data" * 100
        image3 = b"different_image_data" * 100

        # Identical images should have high similarity
        similarity_same = processor.compare_images(image1, image2)
        assert similarity_same > 0.8

        # Different images should have lower similarity
        similarity_diff = processor.compare_images(image1, image3)
        assert 0.0 <= similarity_diff <= 1.0

    def test_cache_management(self) -> None:
        """Test cache management."""
        processor = VisionProcessor()
        image_data = b"cached_image" * 50

        # Analyze and cache
        analysis = processor.analyze_image(image_data, image_id="test_cache")

        # Retrieve from cache
        cached = processor.get_cached_analysis("test_cache")
        assert cached is not None
        assert cached.scene_type == analysis.scene_type

        # Clear cache
        processor.clear_cache()
        cached_after_clear = processor.get_cached_analysis("test_cache")
        assert cached_after_clear is None

    def test_get_cached_analysis_not_found(self) -> None:
        """Test retrieving non-existent cached analysis."""
        processor = VisionProcessor()

        cached = processor.get_cached_analysis("nonexistent_id")
        assert cached is None
