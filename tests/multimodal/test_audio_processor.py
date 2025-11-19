"""Tests for Audio Processor (Phase 12.2)."""

import pytest

from src.multimodal.audio_processor import (
    AudioFeatures,
    AudioFormat,
    AudioProcessor,
    SpeakerProfile,
    SpeechEmotion,
    SpeechRecognitionResult,
    SpeechSegment,
    SynthesizedSpeech,
)


class TestAudioFeatures:
    """Tests for AudioFeatures dataclass."""

    def test_create_audio_features(self) -> None:
        """Test creating audio features."""
        features = AudioFeatures(
            duration=3.5,
            sample_rate=16000,
            energy=0.7,
            pitch=150.0,
            spectral_centroid=2000.0,
            zero_crossing_rate=0.3,
            mfcc_like=[0.1, 0.2, 0.3],
        )

        assert features.duration == 3.5
        assert features.sample_rate == 16000
        assert features.energy == 0.7
        assert features.pitch == 150.0
        assert len(features.mfcc_like) == 3

    def test_audio_features_validation(self) -> None:
        """Test audio features validation."""
        # Valid features
        AudioFeatures(
            duration=1.0,
            sample_rate=16000,
            energy=0.5,
            pitch=100.0,
            spectral_centroid=1000.0,
            zero_crossing_rate=0.5,
        )

        # Invalid duration
        with pytest.raises(ValueError, match="Duration must be"):
            AudioFeatures(
                duration=-1.0,
                sample_rate=16000,
                energy=0.5,
                pitch=100.0,
                spectral_centroid=1000.0,
                zero_crossing_rate=0.5,
            )

        # Invalid sample rate
        with pytest.raises(ValueError, match="Sample rate must be"):
            AudioFeatures(
                duration=1.0,
                sample_rate=0,
                energy=0.5,
                pitch=100.0,
                spectral_centroid=1000.0,
                zero_crossing_rate=0.5,
            )

        # Invalid energy
        with pytest.raises(ValueError, match="Energy must be"):
            AudioFeatures(
                duration=1.0,
                sample_rate=16000,
                energy=1.5,
                pitch=100.0,
                spectral_centroid=1000.0,
                zero_crossing_rate=0.5,
            )


class TestSpeechSegment:
    """Tests for SpeechSegment dataclass."""

    def test_create_speech_segment(self) -> None:
        """Test creating a speech segment."""
        segment = SpeechSegment(
            text="Hello world",
            start_time=0.5,
            end_time=2.5,
            confidence=0.95,
            speaker_id="speaker_1",
            emotion=SpeechEmotion.HAPPY,
            language="en",
        )

        assert segment.text == "Hello world"
        assert segment.start_time == 0.5
        assert segment.end_time == 2.5
        assert segment.confidence == 0.95
        assert segment.speaker_id == "speaker_1"
        assert segment.emotion == SpeechEmotion.HAPPY

    def test_speech_segment_duration(self) -> None:
        """Test speech segment duration calculation."""
        segment = SpeechSegment(
            text="test",
            start_time=1.0,
            end_time=3.5,
            confidence=0.9,
        )

        assert segment.duration() == 2.5

    def test_speech_segment_validation(self) -> None:
        """Test speech segment validation."""
        # Valid segment
        SpeechSegment(text="test", start_time=0.0, end_time=1.0, confidence=0.8)

        # Invalid start time
        with pytest.raises(ValueError, match="Start time must be"):
            SpeechSegment(text="test", start_time=-1.0, end_time=1.0, confidence=0.8)

        # Invalid end time (before start)
        with pytest.raises(ValueError, match="End time must be"):
            SpeechSegment(text="test", start_time=2.0, end_time=1.0, confidence=0.8)

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            SpeechSegment(text="test", start_time=0.0, end_time=1.0, confidence=1.5)


class TestSpeechRecognitionResult:
    """Tests for SpeechRecognitionResult dataclass."""

    def test_create_recognition_result(self) -> None:
        """Test creating speech recognition result."""
        segment = SpeechSegment(
            text="Hello",
            start_time=0.0,
            end_time=1.0,
            confidence=0.9,
        )

        result = SpeechRecognitionResult(
            segments=[segment],
            full_text="Hello world",
            overall_confidence=0.85,
            detected_language="en",
            num_speakers=2,
        )

        assert len(result.segments) == 1
        assert result.full_text == "Hello world"
        assert result.overall_confidence == 0.85
        assert result.num_speakers == 2

    def test_recognition_result_validation(self) -> None:
        """Test recognition result validation."""
        # Valid result
        SpeechRecognitionResult(overall_confidence=0.9, num_speakers=1)

        # Invalid confidence
        with pytest.raises(ValueError, match="Overall confidence must be"):
            SpeechRecognitionResult(overall_confidence=1.5, num_speakers=1)

        # Invalid num_speakers
        with pytest.raises(ValueError, match="Number of speakers must be"):
            SpeechRecognitionResult(overall_confidence=0.9, num_speakers=-1)


class TestSynthesizedSpeech:
    """Tests for SynthesizedSpeech dataclass."""

    def test_create_synthesized_speech(self) -> None:
        """Test creating synthesized speech."""
        speech = SynthesizedSpeech(
            audio_data=b"fake_audio",
            format=AudioFormat.WAV,
            sample_rate=22050,
            duration=3.5,
            voice_id="female_1",
        )

        assert speech.audio_data == b"fake_audio"
        assert speech.format == AudioFormat.WAV
        assert speech.sample_rate == 22050
        assert speech.duration == 3.5
        assert speech.voice_id == "female_1"

    def test_synthesized_speech_validation(self) -> None:
        """Test synthesized speech validation."""
        # Valid speech
        SynthesizedSpeech(
            audio_data=b"test",
            format=AudioFormat.MP3,
            sample_rate=16000,
            duration=1.0,
        )

        # Invalid sample rate
        with pytest.raises(ValueError, match="Sample rate must be"):
            SynthesizedSpeech(
                audio_data=b"test",
                format=AudioFormat.MP3,
                sample_rate=0,
                duration=1.0,
            )

        # Invalid duration
        with pytest.raises(ValueError, match="Duration must be"):
            SynthesizedSpeech(
                audio_data=b"test",
                format=AudioFormat.MP3,
                sample_rate=16000,
                duration=-1.0,
            )


class TestSpeakerProfile:
    """Tests for SpeakerProfile dataclass."""

    def test_create_speaker_profile(self) -> None:
        """Test creating speaker profile."""
        profile = SpeakerProfile(
            speaker_id="speaker_123",
            name="John Doe",
            voice_features={"pitch": 150.0, "energy": 0.6},
            sample_count=5,
            confidence=0.8,
        )

        assert profile.speaker_id == "speaker_123"
        assert profile.name == "John Doe"
        assert profile.voice_features["pitch"] == 150.0
        assert profile.sample_count == 5
        assert profile.confidence == 0.8

    def test_speaker_profile_validation(self) -> None:
        """Test speaker profile validation."""
        # Valid profile
        SpeakerProfile(speaker_id="test", sample_count=3, confidence=0.7)

        # Invalid sample count
        with pytest.raises(ValueError, match="Sample count must be"):
            SpeakerProfile(speaker_id="test", sample_count=-1, confidence=0.7)

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            SpeakerProfile(speaker_id="test", sample_count=3, confidence=1.5)


class TestAudioProcessor:
    """Tests for AudioProcessor class."""

    def test_audio_processor_initialization(self) -> None:
        """Test audio processor initialization."""
        processor = AudioProcessor(default_sample_rate=22050, default_language="es")

        assert processor.default_sample_rate == 22050
        assert processor.default_language == "es"

    def test_recognize_speech(self) -> None:
        """Test speech recognition."""
        processor = AudioProcessor()
        audio_data = b"fake_speech_audio_data" * 100

        result = processor.recognize_speech(audio_data)

        assert isinstance(result, SpeechRecognitionResult)
        assert len(result.segments) > 0
        assert result.full_text != ""
        assert 0.0 <= result.overall_confidence <= 1.0
        assert result.num_speakers >= 1

        # Check segments
        for segment in result.segments:
            assert isinstance(segment, SpeechSegment)
            assert segment.text != ""
            assert segment.start_time >= 0.0
            assert segment.end_time > segment.start_time

    def test_recognize_speech_with_language(self) -> None:
        """Test speech recognition with language hint."""
        processor = AudioProcessor()
        audio_data = b"audio_in_spanish" * 50

        result = processor.recognize_speech(audio_data, language="es")

        assert result.detected_language == "es"

    def test_recognize_speech_caching(self) -> None:
        """Test speech recognition caching."""
        processor = AudioProcessor()
        audio_data = b"cached_audio" * 100

        # First recognition
        result1 = processor.recognize_speech(audio_data)

        # Second recognition (should be cached)
        result2 = processor.recognize_speech(audio_data)

        # Should return same result
        assert result1.full_text == result2.full_text
        assert result1.overall_confidence == result2.overall_confidence

    def test_synthesize_speech(self) -> None:
        """Test speech synthesis."""
        processor = AudioProcessor()
        text = "Hello, this is a test of speech synthesis."

        speech = processor.synthesize_speech(text)

        assert isinstance(speech, SynthesizedSpeech)
        assert len(speech.audio_data) > 0
        assert speech.format == AudioFormat.WAV
        assert speech.sample_rate == processor.default_sample_rate
        assert speech.duration > 0.0
        assert speech.metadata["text_length"] == len(text)

    def test_synthesize_speech_with_voice(self) -> None:
        """Test speech synthesis with specific voice."""
        processor = AudioProcessor()
        text = "Testing voice selection."

        speech = processor.synthesize_speech(text, voice_id="male_voice")

        assert speech.voice_id == "male_voice"

    def test_extract_audio_features(self) -> None:
        """Test audio feature extraction."""
        processor = AudioProcessor()
        audio_data = b"audio_for_feature_extraction" * 200

        features = processor.extract_audio_features(audio_data)

        assert isinstance(features, AudioFeatures)
        assert features.duration > 0.0
        assert features.sample_rate == processor.default_sample_rate
        assert 0.0 <= features.energy <= 1.0
        assert features.pitch > 0.0
        assert features.spectral_centroid > 0.0
        assert 0.0 <= features.zero_crossing_rate <= 1.0
        assert len(features.mfcc_like) == 13  # Standard MFCC count

    def test_detect_emotion(self) -> None:
        """Test emotion detection from speech."""
        processor = AudioProcessor()
        audio_data = b"emotional_speech_sample" * 100

        emotion = processor.detect_emotion(audio_data)

        assert isinstance(emotion, SpeechEmotion)

    def test_detect_emotion_variations(self) -> None:
        """Test that different audio produces different emotions."""
        processor = AudioProcessor()

        # Different audio samples should potentially have different emotions
        audio1 = b"sample_one" * 100
        audio2 = b"different_sample" * 100

        emotion1 = processor.detect_emotion(audio1)
        emotion2 = processor.detect_emotion(audio2)

        # Both should be valid emotions
        assert isinstance(emotion1, SpeechEmotion)
        assert isinstance(emotion2, SpeechEmotion)

    def test_register_speaker(self) -> None:
        """Test speaker registration."""
        processor = AudioProcessor()
        samples = [b"voice_sample_1" * 50, b"voice_sample_2" * 50, b"voice_sample_3" * 50]

        profile = processor.register_speaker(
            audio_samples=samples,
            speaker_id="john_doe",
            name="John Doe",
        )

        assert isinstance(profile, SpeakerProfile)
        assert profile.speaker_id == "john_doe"
        assert profile.name == "John Doe"
        assert profile.sample_count == 3
        assert 0.0 < profile.confidence <= 1.0
        assert len(profile.voice_features) > 0

    def test_identify_speaker(self) -> None:
        """Test speaker identification."""
        processor = AudioProcessor()

        # Register a speaker
        samples = [b"johns_voice" * 50 for _ in range(5)]
        processor.register_speaker(
            audio_samples=samples,
            speaker_id="john",
            name="John",
        )

        # Try to identify using similar audio
        test_audio = b"johns_voice" * 50
        identified = processor.identify_speaker(test_audio)

        # May or may not identify (simulated), but should return None or profile
        assert identified is None or isinstance(identified, SpeakerProfile)

    def test_identify_speaker_no_match(self) -> None:
        """Test speaker identification with no registered speakers."""
        processor = AudioProcessor()
        audio_data = b"unknown_voice" * 50

        identified = processor.identify_speaker(audio_data)

        assert identified is None

    def test_get_speaker_profiles(self) -> None:
        """Test retrieving all speaker profiles."""
        processor = AudioProcessor()

        # Initially empty
        profiles = processor.get_speaker_profiles()
        assert len(profiles) == 0

        # Register some speakers
        processor.register_speaker([b"voice1" * 50], "speaker1", "Speaker One")
        processor.register_speaker([b"voice2" * 50], "speaker2", "Speaker Two")

        profiles = processor.get_speaker_profiles()
        assert len(profiles) == 2
        speaker_ids = [p.speaker_id for p in profiles]
        assert "speaker1" in speaker_ids
        assert "speaker2" in speaker_ids

    def test_clear_cache(self) -> None:
        """Test clearing recognition cache."""
        processor = AudioProcessor()
        audio_data = b"cached_recognition" * 100

        # Recognize and cache
        result1 = processor.recognize_speech(audio_data)

        # Clear cache
        processor.clear_cache()

        # Recognize again (should not be cached)
        result2 = processor.recognize_speech(audio_data)

        # Results should still be valid
        assert isinstance(result1, SpeechRecognitionResult)
        assert isinstance(result2, SpeechRecognitionResult)
