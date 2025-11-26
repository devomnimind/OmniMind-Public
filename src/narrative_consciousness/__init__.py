"""
Phase 16.2: Narrative Consciousness

Integrates personal narrative, dialogue, and identity construction
to create genuine autobiographical self.

References:
- Damasio (2010): "Self Comes to Mind"
- McAdams (2008): "The Life Story Model"
- Buber (1923): "I and Thou"
"""

from .dialogue_engine import DialogueEngine, MutualUnderstanding, Relationship
from .identity_construction import (
    Belief,
    IdentityConstruction,
    IdentitySnapshot,
    Value,
)
from .life_story_model import IdentityModel, LifeChapter, LifeStory, NarrativeArc

__all__ = [
    "LifeStory",
    "LifeChapter",
    "NarrativeArc",
    "IdentityModel",
    "DialogueEngine",
    "MutualUnderstanding",
    "Relationship",
    "IdentityConstruction",
    "IdentitySnapshot",
    "Value",
    "Belief",
]
