"""
Embodied Cognition Module - Phase 16.1

Integração entre sistema neurosymbolic e mundo físico via:
- Sensory input (visual, audio, proprioception)
- Emotional feedback (somatic markers)
- Motor output (action execution)
- Self-awareness (proprioception)

References:
- Varela, Thompson & Rosch (1991): "The Embodied Mind"
- Damasio (2010): "Self Comes to Mind"
- Gibson (1977): Affordances in perception
- Lakoff & Johnson (2002): "Metaphors We Live By"
"""

from .motor_output import (
    ActionExecution,
    MotorController,
)
from .proprioception import (
    InternalState,
    ProprioceptionModule,
    StateAwareness,
)
from .sensory_integration import (
    AudioUnderstanding,
    MultimodalInput,
    SensoryIntegration,
    VisualUnderstanding,
)
from .somatic_loop import (
    Emotion,
    EmotionalMarker,
    SomaticLoop,
)

__all__ = [
    "SensoryIntegration",
    "MultimodalInput",
    "VisualUnderstanding",
    "AudioUnderstanding",
    "SomaticLoop",
    "Emotion",
    "EmotionalMarker",
    "MotorController",
    "ActionExecution",
    "ProprioceptionModule",
    "InternalState",
    "StateAwareness",
]
