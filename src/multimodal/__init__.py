"""Multi-Modal Intelligence Module (Phase 12).

This module provides multi-modal capabilities for OmniMind:
- Vision processing (image/video understanding)
- Audio processing (speech recognition/synthesis)
- Multi-modal reasoning (cross-modal fusion)
- Embodied intelligence (physical world interaction)
"""

from src.multimodal.audio_processor import AudioProcessor
from src.multimodal.vision_processor import VisionProcessor

__all__ = [
    "VisionProcessor",
    "AudioProcessor",
]
