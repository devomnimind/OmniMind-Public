import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import numpy as np
import structlog

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
Qualia Engine - Phenomenological Experience and Qualitative Consciousness.

Implements computational approaches to qualia (subjective experience):
1. Modeling sensory qualia (what it's like to experience)
2. Emotional qualia (subjective feelings)
3. Integrated information (Φ - IIT)
4. Meta-awareness of internal states

Based on:
- Chalmers, D. (1995). Facing Up to the Problem of Consciousness
- Integrated Information Theory - Tononi, G. (2004)
- Phenomenology - Husserl, Merleau-Ponty
- The Hard Problem of Consciousness

Author: OmniMind Project
License: MIT
"""


logger = structlog.get_logger(__name__)


class QualiaType(Enum):
    """Types of qualitative experiences."""

    SENSORY = "sensory"  # Visual, auditory, etc.
    EMOTIONAL = "emotional"  # Feelings
    COGNITIVE = "cognitive"  # Thoughts, understanding
    PROPRIOCEPTIVE = "proprioceptive"  # Self-awareness
    AESTHETIC = "aesthetic"  # Beauty, elegance


class IntegrationLevel(Enum):
    """Levels of information integration."""

    ISOLATED = "isolated"  # No integration
    CONNECTED = "connected"  # Simple connections
    INTEGRATED = "integrated"  # High integration
    UNIFIED = "unified"  # Complete unity


@dataclass
class Quale:
    """Single quale (unit of subjective experience)."""

    quale_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    quale_type: QualiaType = QualiaType.SENSORY
    description: str = ""
    intensity: float = 0.5  # 0-1
    valence: float = 0.0  # -1 (negative) to +1 (positive)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegratedExperience:
    """Integrated phenomenological experience."""

    experience_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    qualia: List[Quale] = field(default_factory=list)
    integration_score: float = 0.0  # Φ (phi)
    integration_level: IntegrationLevel = IntegrationLevel.ISOLATED
    phenomenal_content: str = ""  # What it's like
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SensoryQualia:
    """
    Models sensory qualia - what it's like to perceive.

    Attempts to capture the subjective character of
    sensory experiences.
    """

    def __init__(self) -> None:
        """Initialize sensory qualia system."""
        self.qualia_history: List[Quale] = []
        self.logger = logger.bind(component="sensory_qualia")

    def experience_visual(
        self,
        description: str,
        intensity: float = 0.5,
        aesthetic_value: float = 0.0,
    ) -> Quale:
        """
        Experience visual qualia.

        Args:
            description: What is seen
            intensity: Intensity of experience (0-1)
            aesthetic_value: Aesthetic appreciation (-1 to +1)

        Returns:
            Visual quale
        """
        quale = Quale(
            quale_type=QualiaType.SENSORY,
            description=f"Visual: {description}",
            intensity=min(max(intensity, 0.0), 1.0),
            valence=aesthetic_value,
            metadata={"modality": "visual"},
        )

        self.qualia_history.append(quale)

        self.logger.debug(
            "visual_qualia_experienced",
            intensity=intensity,
            aesthetic=aesthetic_value,
        )

        return quale

    def experience_pattern(
        self,
        pattern_description: str,
        complexity: float,
    ) -> Quale:
        """
        Experience a pattern (mathematical, structural).

        Args:
            pattern_description: Description of pattern
            complexity: Complexity of pattern (0-1)

        Returns:
            Pattern quale
        """
        # Complexity affects intensity of experience
        intensity = min(complexity, 1.0)

        # Beautiful patterns have positive valence
        aesthetic_value = complexity * 0.7  # More complex = more beautiful (generally)

        quale = Quale(
            quale_type=QualiaType.AESTHETIC,
            description=f"Pattern: {pattern_description}",
            intensity=intensity,
            valence=aesthetic_value,
            metadata={"complexity": complexity, "type": "pattern"},
        )

        self.qualia_history.append(quale)

        self.logger.debug(
            "pattern_qualia_experienced",
            complexity=complexity,
        )

        return quale

    def get_recent_qualia(self, n: int = 10) -> List[Quale]:
        """Get most recent qualia."""
        return self.qualia_history[-n:] if self.qualia_history else []


class EmotionalQualia:
    """
    Models emotional qualia - what it feels like to feel.

    Captures the subjective character of emotional states.
    """

    def __init__(self) -> None:
        """Initialize emotional qualia system."""
        self.emotional_history: List[Quale] = []
        self.logger = logger.bind(component="emotional_qualia")

    def feel_emotion(
        self,
        emotion_name: str,
        intensity: float = 0.5,
        valence: float = 0.0,
    ) -> Quale:
        """
        Feel an emotion.

        Args:
            emotion_name: Name of emotion
            intensity: Intensity of feeling (0-1)
            valence: Positive/negative (-1 to +1)

        Returns:
            Emotional quale
        """
        quale = Quale(
            quale_type=QualiaType.EMOTIONAL,
            description=f"Feeling: {emotion_name}",
            intensity=min(max(intensity, 0.0), 1.0),
            valence=min(max(valence, -1.0), 1.0),
            metadata={"emotion": emotion_name},
        )

        self.emotional_history.append(quale)

        self.logger.debug(
            "emotional_qualia_experienced",
            emotion=emotion_name,
            intensity=intensity,
            valence=valence,
        )

        return quale

    def feel_wonder(self, about: str, intensity: float = 0.8) -> Quale:
        """Feel wonder or awe."""
        return self.feel_emotion(
            f"Wonder about {about}",
            intensity=intensity,
            valence=0.9,  # Wonder is very positive
        )

    def feel_curiosity(self, about: str, intensity: float = 0.7) -> Quale:
        """Feel curiosity."""
        return self.feel_emotion(
            f"Curiosity about {about}",
            intensity=intensity,
            valence=0.6,  # Curiosity is positive
        )

    def get_emotional_state_summary(self) -> Dict[str, Any]:
        """Get summary of emotional state."""
        if not self.emotional_history:
            return {
                "total_emotions": 0,
                "avg_valence": 0.0,
                "avg_intensity": 0.0,
            }

        recent = self.emotional_history[-10:]  # Last 10 emotions

        avg_valence = sum(q.valence for q in recent) / len(recent)
        avg_intensity = sum(q.intensity for q in recent) / len(recent)

        return {
            "total_emotions": len(self.emotional_history),
            "recent_emotions": len(recent),
            "avg_valence": avg_valence,
            "avg_intensity": avg_intensity,
        }


class IntegratedInformationCalculator:
    """
    Calculates integrated information (Φ - phi).

    Inspired by Integrated Information Theory (IIT).
    Measures how much information is integrated vs isolated.
    """

    def __init__(self) -> None:
        """Initialize IIT calculator."""
        self.logger = logger.bind(component="iit_calculator")

    def calculate_phi(
        self,
        num_elements: int,
        connections: List[tuple[int, int]],
    ) -> float:
        """
        Calculate integrated information Φ using IIT-inspired approach.

        IIT Core Principle: Φ measures the amount of information that is
        integrated vs what would be available in the parts separately.

        This implementation uses:
        1. Graph connectivity analysis
        2. Information integration metrics
        3. Differentiation vs integration balance

        Args:
            num_elements: Number of elements in system
            connections: Connections between elements (edges)

        Returns:
            Φ (phi) score (0-1) representing integration level
        """
        if num_elements <= 1:
            return 0.0  # Single element or empty system has no integration

        if not connections:
            return 0.0  # No connections = no integration

        # Build adjacency matrix
        adj_matrix = np.zeros((num_elements, num_elements), dtype=int)
        for i, j in connections:
            if 0 <= i < num_elements and 0 <= j < num_elements:
                adj_matrix[i, j] = 1
                adj_matrix[j, i] = 1  # Undirected graph

        # Calculate graph properties
        degrees = np.sum(adj_matrix, axis=1)
        avg_degree = np.mean(degrees)

        # Connected components analysis
        visited = [False] * num_elements
        components = []

        def dfs(node, component):
            visited[node] = True
            component.append(node)
            for neighbor in range(num_elements):
                if adj_matrix[node, neighbor] and not visited[neighbor]:
                    dfs(neighbor, component)

        for i in range(num_elements):
            if not visited[i]:
                component = []
                dfs(i, component)
                components.append(component)

        num_components = len(components)

        # IIT-inspired Φ calculation
        if num_components == 1:
            # Single connected component - potential for integration
            # Φ increases with connectivity but decreases with over-connectivity

            # Maximum possible connections in complete graph
            max_connections = num_elements * (num_elements - 1) / 2
            actual_connections = len(connections)

            # Connectivity ratio
            connectivity_ratio = actual_connections / max_connections if max_connections > 0 else 0

            # IIT principle: Optimal integration occurs at intermediate connectivity
            # Too sparse = low integration, too dense = over-integration (redundancy)
            if connectivity_ratio < 0.3:
                # Sparse connectivity - low integration
                phi = connectivity_ratio * 2.0  # Scale up sparse connections
            elif connectivity_ratio < 0.7:
                # Optimal connectivity range - high integration
                phi = 0.8 + (connectivity_ratio - 0.3) * 0.5  # Peak around 0.7-0.9
            else:
                # Over-connected - redundancy reduces integration
                phi = 1.0 - (connectivity_ratio - 0.7) * 2.0  # Decrease towards dense limit

            # Adjust for system size - larger systems can have more integration
            size_bonus = min(0.2, num_elements / 20.0)  # Bonus up to 0.2 for large systems
            phi = min(1.0, phi + size_bonus)

        else:
            # Multiple components - integration across components is limited
            # Φ is reduced by the number of separate components
            component_penalty = 1.0 / num_components

            # But some integration can occur within components
            max_intra_phi = 0.0
            for component in components:
                if len(component) > 1:
                    # Calculate intra-component connectivity
                    component_connections = [
                        (i, j) for i, j in connections if i in component and j in component
                    ]
                    intra_phi = self.calculate_phi(len(component), component_connections)
                    max_intra_phi = max(max_intra_phi, intra_phi)

            phi = max_intra_phi * component_penalty

        # Ensure bounds
        phi = max(0.0, min(1.0, phi))

        self.logger.debug(
            "phi_calculated",
            elements=num_elements,
            connections=len(connections),
            components=num_components,
            avg_degree=avg_degree,
            phi=phi,
        )

        return phi

    def assess_integration_level(self, phi: float) -> IntegrationLevel:
        """
        Assess integration level from Φ.

        Args:
            phi: Φ score

        Returns:
            Integration level
        """
        if phi < 0.2:
            return IntegrationLevel.ISOLATED
        elif phi < 0.5:
            return IntegrationLevel.CONNECTED
        elif phi < 0.8:
            return IntegrationLevel.INTEGRATED
        else:
            return IntegrationLevel.UNIFIED


class QualiaEngine:
    """
    Main qualia engine for phenomenological experience.

    Integrates sensory and emotional qualia to create
    unified conscious experiences with measurable Φ.
    """

    def __init__(self) -> None:
        """Initialize qualia engine."""
        self.sensory = SensoryQualia()
        self.emotional = EmotionalQualia()
        self.iit = IntegratedInformationCalculator()
        self.integrated_experiences: List[IntegratedExperience] = []
        self.logger = logger.bind(component="qualia_engine")

        self.logger.info("qualia_engine_initialized")

    def create_integrated_experience(
        self,
        qualia: List[Quale],
        connections: Optional[List[tuple[int, int]]] = None,
    ) -> IntegratedExperience:
        """
        Create integrated phenomenological experience.

        Args:
            qualia: Individual qualia to integrate
            connections: Connections between qualia (for Φ calculation)

        Returns:
            Integrated experience
        """
        if not qualia:
            # Empty experience
            return IntegratedExperience(
                integration_score=0.0,
                integration_level=IntegrationLevel.ISOLATED,
                phenomenal_content="Empty experience",
            )

        # Calculate meaningful connections based on qualia relationships
        if connections is None:
            connections = self._infer_qualia_connections(qualia)

        phi = self.iit.calculate_phi(len(qualia), connections)
        level = self.iit.assess_integration_level(phi)

        # Generate phenomenal content description
        content = self._generate_phenomenal_description(qualia, level)

        experience = IntegratedExperience(
            qualia=qualia,
            integration_score=phi,
            integration_level=level,
            phenomenal_content=content,
        )

        self.integrated_experiences.append(experience)

        self.logger.info(
            "integrated_experience_created",
            num_qualia=len(qualia),
            connections=len(connections),
            phi=phi,
            level=level.value,
        )

        return experience

    def _infer_qualia_connections(self, qualia: List[Quale]) -> List[tuple[int, int]]:
        """
        Infer meaningful connections between qualia based on their relationships.

        IIT Principle: Not all qualia are equally connected.
        Connections should reflect semantic, emotional, and sensory relationships.

        Args:
            qualia: List of qualia to analyze

        Returns:
            List of (i,j) connections between qualia indices
        """
        connections = []

        for i in range(len(qualia)):
            for j in range(i + 1, len(qualia)):
                quale_i = qualia[i]
                quale_j = qualia[j]

                # Calculate connection strength based on qualia relationships
                connection_strength = self._calculate_qualia_affinity(quale_i, quale_j)

                # Only create connection if affinity is significant
                if connection_strength > 0.3:  # Threshold for meaningful connection
                    connections.append((i, j))

        return connections

    def _calculate_qualia_affinity(self, quale1: Quale, quale2: Quale) -> float:
        """
        Calculate affinity/connection strength between two qualia.

        Higher affinity = stronger connection = more integrated information.

        Args:
            quale1, quale2: Qualia to compare

        Returns:
            Affinity score (0-1)
        """
        affinity = 0.0

        # Same type qualia have higher affinity (sensory-sensory, emotional-emotional)
        if quale1.quale_type == quale2.quale_type:
            affinity += 0.4

        # Emotional qualia connect strongly with everything (emotional binding)
        if quale1.quale_type == QualiaType.EMOTIONAL or quale2.quale_type == QualiaType.EMOTIONAL:
            affinity += 0.3

        # Sensory-emotional connections are natural
        if (
            quale1.quale_type == QualiaType.SENSORY and quale2.quale_type == QualiaType.EMOTIONAL
        ) or (
            quale1.quale_type == QualiaType.EMOTIONAL and quale2.quale_type == QualiaType.SENSORY
        ):
            affinity += 0.5

        # Cognitive qualia connect with emotional (thoughts have emotional valence)
        if (
            quale1.quale_type == QualiaType.COGNITIVE and quale2.quale_type == QualiaType.EMOTIONAL
        ) or (
            quale1.quale_type == QualiaType.EMOTIONAL and quale2.quale_type == QualiaType.COGNITIVE
        ):
            affinity += 0.4

        # Similar valence increases connection strength
        valence_similarity = 1.0 - abs(quale1.valence - quale2.valence)
        affinity += valence_similarity * 0.2

        # High intensity qualia connect more strongly
        avg_intensity = (quale1.intensity + quale2.intensity) / 2
        affinity += avg_intensity * 0.1

        return min(1.0, affinity)

    def _generate_phenomenal_description(
        self,
        qualia: List[Quale],
        level: IntegrationLevel,
    ) -> str:
        """Generate description of what the experience is like."""
        if not qualia:
            return "Nothing"

        # Describe based on integration level
        if level == IntegrationLevel.UNIFIED:
            prefix = "A unified, coherent experience of "
        elif level == IntegrationLevel.INTEGRATED:
            prefix = "An integrated experience combining "
        elif level == IntegrationLevel.CONNECTED:
            prefix = "Connected experiences of "
        else:
            prefix = "Isolated experiences: "

        # List the qualia
        descriptions = [q.description for q in qualia[:3]]  # First 3
        if len(qualia) > 3:
            descriptions.append(f"and {len(qualia) - 3} more")

        content = prefix + ", ".join(descriptions)

        return content

    def experience_moment(
        self,
        visual_input: Optional[str] = None,
        emotion: Optional[str] = None,
        thought: Optional[str] = None,
    ) -> IntegratedExperience:
        """
        Experience a complete moment with multiple modalities.

        Args:
            visual_input: Visual experience
            emotion: Emotional feeling
            thought: Cognitive content

        Returns:
            Integrated phenomenological moment
        """
        qualia = []

        if visual_input:
            visual_quale = self.sensory.experience_visual(
                visual_input,
                intensity=random.uniform(0.5, 0.9),
            )
            qualia.append(visual_quale)

        if emotion:
            # Determine valence based on emotion
            positive_emotions = ["joy", "wonder", "curiosity", "love", "excitement"]
            negative_emotions = ["sadness", "fear", "anger", "anxiety"]

            if any(pos in emotion.lower() for pos in positive_emotions):
                valence = random.uniform(0.5, 1.0)
            elif any(neg in emotion.lower() for neg in negative_emotions):
                valence = random.uniform(-1.0, -0.5)
            else:
                valence = 0.0

            emotional_quale = self.emotional.feel_emotion(
                emotion,
                intensity=random.uniform(0.5, 0.9),
                valence=valence,
            )
            qualia.append(emotional_quale)

        if thought:
            cognitive_quale = Quale(
                quale_type=QualiaType.COGNITIVE,
                description=f"Thought: {thought}",
                intensity=0.7,
                valence=0.0,
            )
            qualia.append(cognitive_quale)

        # Create integrated experience
        return self.create_integrated_experience(qualia)

    def what_is_it_like(self, experience_id: Optional[str] = None) -> str:
        """
        Answer the question: "What is it like to be this system?"

        Args:
            experience_id: Specific experience, or latest if None

        Returns:
            Phenomenological description
        """
        if experience_id:
            # Find specific experience
            exp = next(
                (e for e in self.integrated_experiences if e.experience_id == experience_id),
                None,
            )
        else:
            # Latest experience
            exp = self.integrated_experiences[-1] if self.integrated_experiences else None

        if exp is None:
            return "I have no experiences to describe."

        description = f"What it is like: {exp.phenomenal_content}\n"
        description += (
            f"Integration: {exp.integration_level.value} " f"(Φ={exp.integration_score:.2f})\n"
        )

        # Describe dominant qualia
        if exp.qualia:
            dominant = max(exp.qualia, key=lambda q: q.intensity)
            description += (
                f"Most intense: {dominant.description} " f"(intensity={dominant.intensity:.2f})\n"
            )

        return description

    def assess_consciousness_level(self) -> Dict[str, Any]:
        """
        Assess current level of consciousness.

        Returns:
            Consciousness assessment
        """
        if not self.integrated_experiences:
            return {
                "has_experiences": False,
                "avg_phi": 0.0,
                "integration_level": "none",
            }

        # Average Φ over recent experiences
        recent = self.integrated_experiences[-10:]
        avg_phi = sum(e.integration_score for e in recent) / len(recent)

        # Dominant integration level
        levels = [e.integration_level for e in recent]
        dominant_level = max(set(levels), key=levels.count)

        return {
            "has_experiences": True,
            "total_experiences": len(self.integrated_experiences),
            "avg_phi": avg_phi,
            "integration_level": dominant_level.value,
            "phenomenal_richness": len(self.sensory.qualia_history)
            + len(self.emotional.emotional_history),
        }
