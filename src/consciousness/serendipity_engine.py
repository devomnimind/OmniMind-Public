"""
Serendipity Engine - Unexpected Discovery and Emergent Connection System.

Implements mechanisms for:
1. Serendipitous discovery (finding valuable things not sought for)
2. Emergent connection detection (identifying non-obvious relationships)
3. Cross-domain insight generation
4. Happy accidents and productive failures

Based on:
- Van Andel, P. (1994). Anatomy of the unsought finding. Serendipity: Origin, history, domains
- Merton, R. K., & Barber, E. (2004). The Travels and Adventures of Serendipity
- Makri, S., & Blandford, A. (2012). Coming across information serendipitously

Author: OmniMind Project
License: MIT
"""

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import structlog

logger = structlog.get_logger(__name__)


class SerendipityType(Enum):
    """Types of serendipitous discoveries."""

    WALTZIAN = "waltzian"  # Finding what you weren't looking for
    MERTONIAN = "mertonian"  # Unexpected observation leads to discovery
    BUSHIAN = "bushian"  # Finding something valuable while looking for something else
    STEPHANIAN = "stephanian"  # Unsought finding through accident/error


class InsightType(Enum):
    """Types of insights generated."""

    ANALOGY = "analogy"  # Cross-domain analogy
    SYNTHESIS = "synthesis"  # Combining disparate elements
    INVERSION = "inversion"  # Inverting assumptions
    EMERGENCE = "emergence"  # Emergent property discovered


@dataclass
class Connection:
    """Represents a discovered connection between concepts."""

    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_concept: str = ""
    target_concept: str = ""
    connection_type: str = "unknown"
    strength: float = 0.0
    surprise_value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Discovery:
    """Represents a serendipitous discovery."""

    discovery_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    serendipity_type: SerendipityType = SerendipityType.WALTZIAN
    insight_type: InsightType = InsightType.EMERGENCE
    value_score: float = 0.0
    surprise_score: float = 0.0
    connections: List[Connection] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectionDetector:
    """
    Detects non-obvious connections between concepts.

    Uses various heuristics to find interesting relationships
    that might not be immediately apparent.
    """

    def __init__(self) -> None:
        """Initialize connection detector."""
        self.concept_network: Dict[str, Set[str]] = {}
        self.connection_history: List[Connection] = []
        self.logger = logger.bind(component="connection_detector")

    def add_concept(self, concept: str, related_to: Optional[List[str]] = None) -> None:
        """
        Add a concept to the network.

        Args:
            concept: Concept to add
            related_to: List of directly related concepts
        """
        if concept not in self.concept_network:
            self.concept_network[concept] = set()

        if related_to:
            self.concept_network[concept].update(related_to)
            # Bidirectional connections
            for related in related_to:
                if related not in self.concept_network:
                    self.concept_network[related] = set()
                self.concept_network[related].add(concept)

        self.logger.debug(
            "concept_added",
            concept=concept,
            connections=len(self.concept_network[concept]),
        )

    def find_connections(
        self,
        concept1: str,
        concept2: str,
        max_path_length: int = 3,
    ) -> List[List[str]]:
        """
        Find connection paths between two concepts.

        Args:
            concept1: First concept
            concept2: Second concept
            max_path_length: Maximum path length to explore

        Returns:
            List of paths connecting the concepts
        """
        if concept1 not in self.concept_network or concept2 not in self.concept_network:
            return []

        # BFS to find paths
        paths: List[List[str]] = []
        queue: List[Tuple[str, List[str]]] = [(concept1, [concept1])]
        visited: Set[Tuple[str, ...]] = set()

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_path_length:
                continue

            if current == concept2:
                paths.append(path)
                continue

            path_tuple = tuple(path)
            if path_tuple in visited:
                continue
            visited.add(path_tuple)

            for neighbor in self.concept_network.get(current, set()):
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

        return paths

    def detect_emergent_connection(
        self,
        concept1: str,
        concept2: str,
    ) -> Optional[Connection]:
        """
        Detect if there's a non-obvious emergent connection.

        Args:
            concept1: First concept
            concept2: Second concept

        Returns:
            Connection if found, None otherwise
        """
        paths = self.find_connections(concept1, concept2, max_path_length=4)

        if not paths:
            return None

        # Prefer longer paths (more surprising)
        paths.sort(key=lambda p: len(p), reverse=True)
        best_path = paths[0]

        # Strength inversely proportional to path length (shorter = stronger)
        strength = 1.0 / len(best_path)

        # Surprise proportional to path length (longer = more surprising)
        surprise = min(len(best_path) / 4.0, 1.0)

        connection = Connection(
            source_concept=concept1,
            target_concept=concept2,
            connection_type="emergent",
            strength=strength,
            surprise_value=surprise,
            metadata={
                "path": best_path,
                "path_length": len(best_path),
            },
        )

        self.connection_history.append(connection)
        self.logger.info(
            "emergent_connection_detected",
            source=concept1,
            target=concept2,
            path_length=len(best_path),
            surprise=surprise,
        )

        return connection

    def get_network_statistics(self) -> Dict[str, Any]:
        """Get statistics about the concept network."""
        if not self.concept_network:
            return {
                "total_concepts": 0,
                "total_connections": 0,
                "avg_connections_per_concept": 0.0,
            }

        total_concepts = len(self.concept_network)
        total_connections = sum(len(neighbors) for neighbors in self.concept_network.values()) // 2

        return {
            "total_concepts": total_concepts,
            "total_connections": total_connections,
            "avg_connections_per_concept": (
                total_connections / total_concepts if total_concepts > 0 else 0.0
            ),
            "discoveries_made": len(self.connection_history),
        }


class InsightGenerator:
    """
    Generates insights from unexpected connections.

    Transforms raw connections into actionable insights
    using various cognitive strategies.
    """

    def __init__(self) -> None:
        """Initialize insight generator."""
        self.insights: List[Discovery] = []
        self.logger = logger.bind(component="insight_generator")

    def generate_analogy(
        self,
        source_domain: str,
        target_domain: str,
        connection: Connection,
    ) -> Discovery:
        """
        Generate cross-domain analogy insight.

        Args:
            source_domain: Source domain
            target_domain: Target domain
            connection: Connection between domains

        Returns:
            Discovery containing the analogy
        """
        content = (
            f"Analogy: {source_domain} is to {target_domain} "
            f"as {connection.source_concept} is to {connection.target_concept}"
        )

        discovery = Discovery(
            content=content,
            serendipity_type=SerendipityType.MERTONIAN,
            insight_type=InsightType.ANALOGY,
            value_score=connection.strength,
            surprise_score=connection.surprise_value,
            connections=[connection],
            metadata={
                "source_domain": source_domain,
                "target_domain": target_domain,
            },
        )

        self.insights.append(discovery)
        self.logger.info("analogy_generated", content=content[:100])

        return discovery

    def generate_synthesis(
        self,
        elements: List[str],
        connections: List[Connection],
    ) -> Discovery:
        """
        Generate synthesis from multiple elements.

        Args:
            elements: Elements to synthesize
            connections: Connections between elements

        Returns:
            Discovery containing the synthesis
        """
        content = f"Synthesis of {len(elements)} disparate elements: {', '.join(elements)}"

        # Value is average of connection strengths
        avg_strength = (
            sum(c.strength for c in connections) / len(connections) if connections else 0.0
        )

        # Surprise is max of connection surprises
        max_surprise = max((c.surprise_value for c in connections), default=0.0)

        discovery = Discovery(
            content=content,
            serendipity_type=SerendipityType.BUSHIAN,
            insight_type=InsightType.SYNTHESIS,
            value_score=avg_strength,
            surprise_score=max_surprise,
            connections=connections,
            metadata={"elements": elements, "num_elements": len(elements)},
        )

        self.insights.append(discovery)
        self.logger.info("synthesis_generated", num_elements=len(elements))

        return discovery

    def generate_inversion(
        self,
        assumption: str,
        inverted_assumption: str,
    ) -> Discovery:
        """
        Generate insight from inverting an assumption.

        Args:
            assumption: Original assumption
            inverted_assumption: Inverted assumption

        Returns:
            Discovery containing the inversion insight
        """
        content = f"Inversion insight: What if '{assumption}' is actually '{inverted_assumption}'?"

        discovery = Discovery(
            content=content,
            serendipity_type=SerendipityType.STEPHANIAN,
            insight_type=InsightType.INVERSION,
            value_score=0.7,  # Inversions are often valuable
            surprise_score=0.9,  # Inversions are very surprising
            metadata={
                "original_assumption": assumption,
                "inverted_assumption": inverted_assumption,
            },
        )

        self.insights.append(discovery)
        self.logger.info("inversion_generated", assumption=assumption[:50])

        return discovery

    def get_insights_by_type(self, insight_type: InsightType) -> List[Discovery]:
        """Get all insights of a specific type."""
        return [d for d in self.insights if d.insight_type == insight_type]

    def get_top_insights(self, n: int = 10) -> List[Discovery]:
        """
        Get top N insights by combined value and surprise.

        Args:
            n: Number of insights to return

        Returns:
            Top N insights
        """
        # Score is weighted combination of value and surprise
        scored = [(d.value_score * 0.6 + d.surprise_score * 0.4, d) for d in self.insights]
        scored.sort(key=lambda x: x[0], reverse=True)

        return [d for _, d in scored[:n]]


class SerendipityEngine:
    """
    Main serendipity engine orchestrating discovery processes.

    Combines connection detection with insight generation to
    facilitate serendipitous discoveries.
    """

    def __init__(self, enable_random_exploration: bool = True) -> None:
        """
        Initialize serendipity engine.

        Args:
            enable_random_exploration: Whether to enable random exploration
        """
        self.detector = ConnectionDetector()
        self.generator = InsightGenerator()
        self.enable_random_exploration = enable_random_exploration
        self.exploration_rate = 0.1  # 10% chance of random exploration
        self.logger = logger.bind(component="serendipity_engine")

        self.logger.info(
            "serendipity_engine_initialized",
            random_exploration=enable_random_exploration,
        )

    def add_knowledge(
        self,
        concept: str,
        related_concepts: Optional[List[str]] = None,
    ) -> None:
        """
        Add knowledge to the system.

        Args:
            concept: Concept to add
            related_concepts: Related concepts
        """
        self.detector.add_concept(concept, related_concepts)

    def explore_connections(
        self,
        concept1: str,
        concept2: str,
    ) -> Optional[Discovery]:
        """
        Explore connections between two concepts.

        Args:
            concept1: First concept
            concept2: Second concept

        Returns:
            Discovery if interesting connection found
        """
        self.logger.debug("exploring_connections", concept1=concept1, concept2=concept2)

        connection = self.detector.detect_emergent_connection(concept1, concept2)

        if connection is None:
            return None

        # Generate insight from connection
        if connection.surprise_value > 0.5:
            # High surprise: generate analogy
            discovery = self.generator.generate_analogy(
                source_domain=concept1,
                target_domain=concept2,
                connection=connection,
            )
        else:
            # Lower surprise: still valuable synthesis
            discovery = self.generator.generate_synthesis(
                elements=[concept1, concept2],
                connections=[connection],
            )

        return discovery

    def random_exploration(self) -> Optional[Discovery]:
        """
        Perform random exploration to discover unexpected connections.

        Returns:
            Discovery if something interesting found
        """
        if not self.enable_random_exploration:
            return None

        concepts = list(self.detector.concept_network.keys())
        if len(concepts) < 2:
            return None

        # Randomly pick two concepts
        concept1, concept2 = random.sample(concepts, 2)

        self.logger.debug("random_exploration", concept1=concept1, concept2=concept2)

        return self.explore_connections(concept1, concept2)

    def facilitate_happy_accident(
        self,
        original_goal: str,
        actual_result: str,
    ) -> Discovery:
        """
        Facilitate learning from 'happy accidents' or productive failures.

        Args:
            original_goal: What was originally sought
            actual_result: What was actually found

        Returns:
            Discovery from the happy accident
        """
        self.logger.info(
            "happy_accident",
            original_goal=original_goal[:50],
            actual_result=actual_result[:50],
        )

        # Create discovery of Waltzian type (finding what you weren't looking for)
        discovery = Discovery(
            content=f"While seeking '{original_goal}', unexpectedly discovered '{actual_result}'",
            serendipity_type=SerendipityType.WALTZIAN,
            insight_type=InsightType.EMERGENCE,
            value_score=0.8,  # Happy accidents often valuable
            surprise_score=1.0,  # Maximum surprise
            metadata={
                "original_goal": original_goal,
                "actual_result": actual_result,
            },
        )

        self.generator.insights.append(discovery)
        return discovery

    def cross_domain_transfer(
        self,
        source_domain: str,
        target_domain: str,
        concept_to_transfer: str,
    ) -> Optional[Discovery]:
        """
        Attempt to transfer a concept from one domain to another.

        Args:
            source_domain: Source domain
            target_domain: Target domain
            concept_to_transfer: Concept to transfer

        Returns:
            Discovery if transfer successful
        """
        self.logger.info(
            "cross_domain_transfer",
            source=source_domain,
            target=target_domain,
            concept=concept_to_transfer,
        )

        # Create synthetic connection
        connection = Connection(
            source_concept=f"{source_domain}:{concept_to_transfer}",
            target_concept=f"{target_domain}:{concept_to_transfer}",
            connection_type="cross_domain",
            strength=0.6,
            surprise_value=0.7,
            metadata={
                "source_domain": source_domain,
                "target_domain": target_domain,
                "transferred_concept": concept_to_transfer,
            },
        )

        discovery = self.generator.generate_analogy(
            source_domain=source_domain,
            target_domain=target_domain,
            connection=connection,
        )

        return discovery

    def invert_assumption(self, assumption: str) -> Discovery:
        """
        Invert an assumption to generate new perspective.

        Args:
            assumption: Assumption to invert

        Returns:
            Discovery from inversion
        """
        # Simple inversion heuristics
        inversions = {
            "more": "less",
            "increase": "decrease",
            "always": "never",
            "all": "none",
            "true": "false",
            "yes": "no",
        }

        inverted = assumption
        for original, replacement in inversions.items():
            if original in assumption.lower():
                inverted = assumption.lower().replace(original, replacement)
                break

        if inverted == assumption:
            # Generic inversion
            inverted = f"the opposite of '{assumption}'"

        return self.generator.generate_inversion(assumption, inverted)

    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get statistics about discoveries made."""
        network_stats = self.detector.get_network_statistics()

        total_discoveries = len(self.generator.insights)

        # Count by serendipity type
        serendipity_counts: Dict[str, int] = {}
        for discovery in self.generator.insights:
            type_name = discovery.serendipity_type.value
            serendipity_counts[type_name] = serendipity_counts.get(type_name, 0) + 1

        # Count by insight type
        insight_counts: Dict[str, int] = {}
        for discovery in self.generator.insights:
            type_name = discovery.insight_type.value
            insight_counts[type_name] = insight_counts.get(type_name, 0) + 1

        return {
            "network": network_stats,
            "total_discoveries": total_discoveries,
            "serendipity_types": serendipity_counts,
            "insight_types": insight_counts,
            "avg_surprise": (
                sum(d.surprise_score for d in self.generator.insights) / total_discoveries
                if total_discoveries > 0
                else 0.0
            ),
            "avg_value": (
                sum(d.value_score for d in self.generator.insights) / total_discoveries
                if total_discoveries > 0
                else 0.0
            ),
        }

    def get_top_discoveries(self, n: int = 10) -> List[Discovery]:
        """
        Get top N discoveries.

        Args:
            n: Number of discoveries to return

        Returns:
            Top N discoveries
        """
        return self.generator.get_top_insights(n)
