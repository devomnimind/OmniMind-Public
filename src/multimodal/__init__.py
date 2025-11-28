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

"""Multi-Modal Intelligence Module (Phase 12).

This module provides multi-modal capabilities for OmniMind:
- Vision processing (image/video understanding)
- Audio processing (speech recognition/synthesis)
- Multi-modal reasoning (cross-modal fusion)
- Embodied intelligence (physical world interaction)
"""

from src.multimodal.audio_processor import AudioProcessor
from src.multimodal.embodied_intelligence import EmbodiedIntelligence
from src.multimodal.multi_modal_fusion import MultiModalFusion
from src.multimodal.vision_processor import VisionProcessor

__all__ = [
    "VisionProcessor",
    "AudioProcessor",
    "MultiModalFusion",
    "EmbodiedIntelligence",
]
