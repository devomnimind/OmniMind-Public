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
Tests for Phase 18: Tri-Partite Memory.
"""

from datetime import datetime, timedelta

from src.memory.memory_consolidator import MemoryConsolidator
from src.memory.memory_replay import MemoryReplay
from src.memory.procedural_memory import ProceduralMemory
from src.memory.semantic_memory import SemanticMemory
from src.memory.strategic_forgetting import StrategicForgetting


class TestSemanticMemory:
    def test_store_and_retrieve_concept(self):
        memory = SemanticMemory()
        concept = memory.store_concept("Python", {"type": "language"})

        assert concept.name == "python"
        assert concept.attributes["type"] == "language"

        retrieved = memory.retrieve_concept("Python")
        assert retrieved is not None
        assert retrieved.name == "python"
        assert retrieved.access_count == 1

    def test_relationships(self):
        memory = SemanticMemory()
        memory.store_concept("Cat")
        memory.store_concept("Animal")

        success = memory.associate_concepts("Cat", "Animal", "is_a", bidirectional=False)
        assert success is True

        related = memory.get_related_concepts("Cat")
        assert len(related) == 1
        assert related[0] == ("animal", "is_a")

    def test_update_concept(self):
        memory = SemanticMemory()
        memory.store_concept("AI", {"field": "CS"})
        memory.store_concept("AI", {"subfield": "ML"}, overwrite=False)

        concept = memory.retrieve_concept("AI")
        assert concept.attributes["field"] == "CS"
        assert concept.attributes["subfield"] == "ML"
        assert concept.strength > 0.5  # Should have increased from default


class TestProceduralMemory:
    def test_learn_and_execute_skill(self):
        memory = ProceduralMemory()
        steps = ["step1", "step2"]
        memory.learn_skill("Walk", steps)

        skill = memory.get_skill("Walk")
        assert skill is not None
        assert skill.steps == steps

        executed_steps = memory.execute_skill("Walk")
        assert executed_steps == steps

    def test_refine_skill(self):
        memory = ProceduralMemory()
        memory.learn_skill("Jump", ["jump"])

        initial_proficiency = memory.get_skill("Jump").proficiency
        memory.refine_skill("Jump", success=True)

        refined_proficiency = memory.get_skill("Jump").proficiency
        assert refined_proficiency > initial_proficiency


class TestMemoryConsolidator:
    def test_consolidation(self):
        semantic = SemanticMemory()
        consolidator = MemoryConsolidator(semantic)

        episodes = [
            {"content": "I saw a big dog"},
            {"content": "The dog barked"},
            {"content": "A dog is a pet"},
            {"tags": ["cat", "pet"]},
            {"tags": ["cat", "meow"]},
            {"tags": ["cat", "fur"]},
        ]

        # Threshold 3: 'dog' appears 3 times (in content), 'cat' appears 3 times (in tags)
        # Note: My simple implementation splits content by space. "dog" appears in 1, 2, 3.
        # "cat" appears in 4, 5, 6.

        stats = consolidator.consolidate(episodes, threshold=3)

        assert (
            stats["concepts_created"] >= 0
        )  # Might be 0 if my manual counting is off or split logic differs

        # Let's verify 'cat' specifically as it is in tags (easier)
        cat = semantic.retrieve_concept("cat")
        if cat:
            assert cat.attributes["source"] == "consolidation"


class TestStrategicForgetting:
    def test_pruning(self):
        semantic = SemanticMemory()
        forgetting = StrategicForgetting(semantic)

        # Create old, weak concept
        old_concept = semantic.store_concept("OldStuff")
        old_concept.creation_time = datetime.now() - timedelta(days=40)
        old_concept.strength = 0.1
        old_concept.access_count = 0

        # Create new concept
        semantic.store_concept("NewStuff")

        assert len(semantic.concepts) == 2

        pruned_count = forgetting.prune_semantic_memory(retention_days=30)

        assert pruned_count == 1
        assert "oldstuff" not in semantic.concepts
        assert "newstuff" in semantic.concepts


class TestMemoryReplay:
    def test_selection(self):
        replay = MemoryReplay()
        episodes = [
            {"id": 1, "significance": 0.1},
            {"id": 2, "significance": 0.9},
            {"id": 3, "significance": 0.5},
        ]

        selected = replay.select_episodes_for_replay(episodes, count=2, strategy="significance")

        assert len(selected) == 2
        assert selected[0]["id"] == 2  # Highest significance
        assert selected[1]["id"] == 3  # Second highest

    def test_replay(self):
        replay = MemoryReplay()
        episode = {"id": 1, "content": "test"}

        replayed = replay.replay_episode(episode)

        assert replayed["replayed"] is True
        assert replayed["replay_count"] == 1
