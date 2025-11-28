"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Sensory Integration Module - Multimodal Processing

Integrates visual, audio, and proprioceptive input through
neural (probabilistic) and symbolic (logic-based) systems.

Refs:
- Varela et al. (1991): Sensorimotor coupling
- Gibson (1977): Affordances
- Damasio (2010): Somatic markers in perception
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from numpy.typing import NDArray

logger = logging.getLogger(__name__)


@dataclass
class VisualUnderstanding:
    """Result of visual sensory processing."""

    description: str
    embedding: Optional[List[float]] = None
    objects_detected: Optional[List[str]] = None
    spatial_layout: Optional[Dict[str, Any]] = None
    symbolic_facts: Optional[List[Dict[str, str]]] = None
    confidence: float = 0.5


@dataclass
class AudioUnderstanding:
    """Result of audio sensory processing."""

    transcription: str
    emotional_tone: str = "neutral"
    speaker_identity: Optional[str] = None
    confidence: float = 0.5


@dataclass
class MultimodalInput:
    """Combined sensory input from multiple modalities."""

    visual: Optional[VisualUnderstanding] = None
    audio: Optional[AudioUnderstanding] = None
    proprioceptive_state: Optional[Dict[str, float]] = None
    timestamp: float = 0.0


class SensoryIntegration:
    """
    Multimodal sensory processing system.

    Combines neural (probabilistic) and symbolic (deterministic)
    reasoning to understand the world through integrated senses.

    Process:
    1. Capture multimodal input (visual, audio, proprioception)
    2. Process through neural network (embeddings, patterns)
    3. Process through symbolic system (facts, logic)
    4. Reconcile interpretations
    5. Update internal model
    """

    def __init__(
        self,
        enable_vision: bool = True,
        enable_audio: bool = True,
        enable_proprioception: bool = True,
    ):
        """Initialize sensory integration system."""
        self.enable_vision = enable_vision
        self.enable_audio = enable_audio
        self.enable_proprioception = enable_proprioception

        # Import neural/symbolic components
        try:
            from src.neurosymbolic import NeuralComponent, SymbolicComponent

            self.neural: Optional[NeuralComponent] = NeuralComponent()
            self.symbolic: Optional[SymbolicComponent] = SymbolicComponent()
        except ImportError:
            logger.warning("Neurosymbolic components not available (stub mode)")
            self.neural = None
            self.symbolic = None

        # Sensory state
        self.proprioceptive_state: Dict[str, float] = {}
        self.last_visual: Optional[VisualUnderstanding] = None
        self.last_audio: Optional[AudioUnderstanding] = None

        logger.info(
            f"SensoryIntegration initialized "
            f"(vision={enable_vision}, audio={enable_audio}, "
            f"proprioception={enable_proprioception})"
        )

    def process_visual_input(
        self,
        image_description: str,
        image_data: Optional[NDArray[Any]] = None,
    ) -> VisualUnderstanding:
        """
        Process visual input through neural + symbolic systems.

        Args:
            image_description: Text description of visual scene
            image_data: Optional raw image data

        Returns:
            VisualUnderstanding with embedding and facts
        """
        if not self.enable_vision:
            return VisualUnderstanding(description="Vision disabled")

        logger.debug(f"Processing visual input: {image_description[:50]}...")

        result = VisualUnderstanding(description=image_description)

        # Neural processing: generate embedding
        if self.neural is not None:
            try:
                result.embedding = self.neural.embed(image_description)
                result.confidence = 0.8
            except Exception as e:
                logger.error(f"Neural visual processing failed: {e}")

        # Symbolic processing: extract and store facts
        if self.symbolic is not None:
            try:
                # Extract objects from description (simple heuristic)
                words = image_description.lower().split()
                common_objects = {
                    "person",
                    "chair",
                    "table",
                    "door",
                    "window",
                    "tree",
                    "car",
                    "building",
                    "sky",
                    "ground",
                }
                detected = [w for w in words if w in common_objects]
                result.objects_detected = detected
                result.symbolic_facts = []

                # Add facts to knowledge graph
                for obj in detected:
                    self.symbolic.add_fact(obj, "is_visible", "true")
                    if result.symbolic_facts is not None:
                        result.symbolic_facts.append(
                            {
                                "subject": obj,
                                "predicate": "is_visible",
                                "object": "true",
                            }
                        )
            except Exception as e:
                logger.error(f"Symbolic visual processing failed: {e}")

        self.last_visual = result
        return result

    def process_audio_input(
        self,
        audio_description: str,
    ) -> AudioUnderstanding:
        """
        Process audio input through emotional + linguistic analysis.

        Args:
            audio_description: Transcription or description of audio

        Returns:
            AudioUnderstanding with transcription and emotion
        """
        if not self.enable_audio:
            return AudioUnderstanding(transcription="Audio disabled")

        logger.debug(f"Processing audio input: {audio_description[:50]}...")

        result = AudioUnderstanding(transcription=audio_description)

        # Simple emotion detection from keywords
        positive_words = {"good", "happy", "great", "excellent", "love"}
        negative_words = {"bad", "sad", "terrible", "hate", "angry"}

        words = audio_description.lower().split()
        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)

        if positive_count > negative_count:
            result.emotional_tone = "positive"
        elif negative_count > positive_count:
            result.emotional_tone = "negative"
        else:
            result.emotional_tone = "neutral"

        result.confidence = 0.75

        if self.symbolic is not None:
            try:
                self.symbolic.add_fact(
                    "audio_input",
                    "emotional_tone",
                    result.emotional_tone,
                )
            except Exception as e:
                logger.error(f"Symbolic audio processing failed: {e}")

        self.last_audio = result
        return result

    def update_proprioception(
        self,
        state: Dict[str, float],
    ) -> None:
        """
        Update proprioceptive state (internal awareness).

        Args:
            state: Dictionary of internal state values
                  (CPU%, memory%, emotional_valence, etc)
        """
        if not self.enable_proprioception:
            return

        self.proprioceptive_state = state.copy()

        logger.debug(f"Proprioception updated: {state}")

        # Add to knowledge graph
        if self.symbolic is not None:
            try:
                for key, value in state.items():
                    self.symbolic.add_fact(
                        "self",
                        f"state_{key}",
                        str(value),
                    )
            except Exception as e:
                logger.error(f"Proprioceptive state update failed: {e}")

    def integrate_multimodal(
        self,
        visual: Optional[VisualUnderstanding] = None,
        audio: Optional[AudioUnderstanding] = None,
        proprioceptive_state: Optional[Dict[str, float]] = None,
    ) -> MultimodalInput:
        """
        Integrate multiple sensory streams into unified input.

        Args:
            visual: Visual understanding
            audio: Audio understanding
            proprioceptive_state: Internal state

        Returns:
            MultimodalInput with all sensory streams
        """
        input_data = MultimodalInput(
            visual=visual or self.last_visual,
            audio=audio or self.last_audio,
            proprioceptive_state=proprioceptive_state or self.proprioceptive_state,
        )

        logger.info("Multimodal sensory input integrated")
        return input_data

    def get_sensory_summary(self) -> str:
        """Generate summary of current sensory state."""
        summary = "=== SENSORY STATE ===\n"

        if self.last_visual:
            summary += f"Visual: {self.last_visual.description[:50]}...\n"

        if self.last_audio:
            summary += f"Audio: {self.last_audio.transcription[:50]}...\n"

        if self.proprioceptive_state:
            summary += f"Internal state: {self.proprioceptive_state}\n"

        return summary
