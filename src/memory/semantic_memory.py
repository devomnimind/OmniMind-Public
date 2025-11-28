import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

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
Semantic Memory Module.

Stores abstract knowledge, concepts, and their relationships.
Acts as the long-term store for factual information, independent of specific episodes.
"""


logger = logging.getLogger(__name__)


@dataclass
class Concept:
    """Represents a semantic concept."""

    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    creation_time: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    strength: float = 0.5  # 0.0 to 1.0


class SemanticMemory:
    """
    Semantic Memory System.

    Manages a network of concepts and relationships.
    """

    def __init__(self) -> None:
        """Initialize semantic memory."""
        self.concepts: Dict[str, Concept] = {}
        # Adjacency list for graph: source -> {target -> relation_type}
        self.relationships: Dict[str, Dict[str, str]] = {}
        logger.info("Semantic Memory initialized")

    def store_concept(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> Concept:
        """
        Store a new concept or update an existing one.

        Args:
            name: Name of the concept (unique identifier).
            attributes: Dictionary of attributes.
            overwrite: If True, replaces existing attributes. If False, merges.

        Returns:
            The stored Concept object.
        """
        name = name.lower().strip()

        if name in self.concepts:
            concept = self.concepts[name]
            if attributes:
                if overwrite:
                    concept.attributes = attributes
                else:
                    concept.attributes.update(attributes)
            concept.strength = min(concept.strength + 0.1, 1.0)
            logger.debug(f"Updated concept: {name}")
        else:
            concept = Concept(name=name, attributes=attributes or {})
            self.concepts[name] = concept
            self.relationships[name] = {}
            logger.debug(f"Created new concept: {name}")

        return concept

    def associate_concepts(
        self,
        concept1: str,
        concept2: str,
        relation: str = "related_to",
        bidirectional: bool = False,
    ) -> bool:
        """
        Create a relationship between two concepts.

        Args:
            concept1: Source concept name.
            concept2: Target concept name.
            relation: Type of relationship (e.g., "is_a", "has_part").
            bidirectional: If True, creates the inverse relationship as well.

        Returns:
            True if successful, False if concepts don't exist.
        """
        c1 = concept1.lower().strip()
        c2 = concept2.lower().strip()

        if c1 not in self.concepts or c2 not in self.concepts:
            logger.warning(f"Cannot associate {c1} and {c2}: one or both do not exist.")
            return False

        if c1 not in self.relationships:
            self.relationships[c1] = {}

        self.relationships[c1][c2] = relation
        logger.debug(f"Associated {c1} -> {relation} -> {c2}")

        if bidirectional:
            if c2 not in self.relationships:
                self.relationships[c2] = {}
            self.relationships[c2][c1] = relation
            logger.debug(f"Associated {c2} -> {relation} -> {c1}")

        return True

    def retrieve_concept(self, name: str) -> Optional[Concept]:
        """
        Retrieve a concept by name.

        Args:
            name: Concept name.

        Returns:
            Concept object or None if not found.
        """
        name = name.lower().strip()
        if name in self.concepts:
            concept = self.concepts[name]
            concept.access_count += 1
            concept.last_accessed = datetime.now()
            return concept
        return None

    def get_related_concepts(
        self, name: str, relation_filter: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """
        Get all concepts related to the given concept.

        Args:
            name: Source concept name.
            relation_filter: If provided, only returns relationships of this type.

        Returns:
            List of (related_concept_name, relation_type) tuples.
        """
        name = name.lower().strip()
        if name not in self.relationships:
            return []

        related = []
        for target, rel in self.relationships[name].items():
            if relation_filter is None or rel == relation_filter:
                related.append((target, rel))

        return related

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about semantic memory."""
        total_concepts = len(self.concepts)
        total_relations = sum(len(rels) for rels in self.relationships.values())

        return {
            "total_concepts": total_concepts,
            "total_relations": total_relations,
            "avg_relations_per_concept": (
                total_relations / total_concepts if total_concepts > 0 else 0.0
            ),
        }
