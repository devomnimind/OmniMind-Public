"""Tests for Knowledge Integrator - Phase 26A

DEPRECATED: Módulos knowledge.* não existem mais.

SUBSTITUIÇÃO:
- ✅ Substituído por: Integração via src.memory.* (módulos unificados)
- ✅ Declarative: src.memory.semantic_memory.SemanticMemory
- ✅ Episodic: src.memory.narrative_history.NarrativeHistory (Lacanian)
- ✅ Procedural: src.memory.procedural_memory.ProceduralMemory
- ✅ Integração: Uso combinado dos módulos acima
- ✅ Status: Implementado e operacional

MIGRAÇÃO:
```python
# ANTES (deprecated):
from knowledge.knowledge_integrator import KnowledgeIntegrator
from knowledge.declarative_layer import Concept
from knowledge.episodic_layer import Episode
from knowledge.procedural_layer import Rule
integrator = KnowledgeIntegrator()
integrated = integrator.integrate(concept, episode, rule)

# DEPOIS (atual):
from src.memory.semantic_memory import SemanticMemory
from src.memory.narrative_history import NarrativeHistory
from src.memory.procedural_memory import ProceduralMemory

# Integração manual ou via IntegrationLoop
semantic = SemanticMemory()
narrative = NarrativeHistory()
procedural = ProceduralMemory()
# Uso combinado dos três sistemas de memória
```

Este teste foi marcado como skip até que seja atualizado para usar os módulos de memória unificados.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(
    reason=(
        "Módulos knowledge.* foram substituídos por "
        "src.memory.* (semantic, narrative, procedural)"
    )
)

# Imports removidos - módulos não existem
# from knowledge.declarative_layer import Concept
# from knowledge.episodic_layer import Episode
# from knowledge.knowledge_integrator import KnowledgeIntegrator
# from knowledge.procedural_layer import Rule
#
# SUBSTITUIÇÃO: Use src.memory.semantic_memory,
#                src.memory.narrative_history,
#                src.memory.procedural_memory


class TestKnowledgeIntegrator:
    """Test Knowledge Integrator - DEPRECATED: Use memory modules directly"""

    def test_init(self):
        """Test initialization - DEPRECATED"""
        # Nota: KnowledgeIntegrator foi substituído por uso direto dos módulos de memória
        # integrator = KnowledgeIntegrator()  # DEPRECATED
        # assert integrator is not None
        # assert integrator.declarative is not None
        # assert integrator.procedural is not None
        # assert integrator.episodic is not None
        pytest.skip(
            "Use test_semantic_memory.py, test_narrative_history.py, "
            "test_procedural_memory.py instead"
        )

    def test_query_all_layers(self):
        """Test querying all layers - DEPRECATED"""
        # Nota: KnowledgeIntegrator foi substituído por uso direto dos módulos de memória
        # integrator = KnowledgeIntegrator()  # DEPRECATED
        # concept = Concept(...)  # DEPRECATED
        # integrator.declarative.store_concept(concept)
        # rule = Rule(...)  # DEPRECATED
        # integrator.procedural.store_rule(rule)
        # episode = Episode(...)  # DEPRECATED
        # integrator.episodic.store_episode(episode)
        # results = integrator.query("memory")
        # assert "concepts" in results
        # assert "rules" in results
        # assert "episodes" in results
        pytest.skip(
            "Use test_semantic_memory.py, test_narrative_history.py, "
            "test_procedural_memory.py instead"
        )

    def test_get_statistics(self):
        """Test getting statistics - DEPRECATED"""
        # Nota: KnowledgeIntegrator foi substituído por uso direto dos módulos de memória
        # integrator = KnowledgeIntegrator()  # DEPRECATED
        # concept = Concept(id="c1", name="Test", definition="Test")  # DEPRECATED
        # integrator.declarative.store_concept(concept)
        # rule = Rule(id="r1", name="Test", description="Test", rule_type="rule")  # DEPRECATED
        # integrator.procedural.store_rule(rule)
        # episode = Episode(  # DEPRECATED
        #     id="e1", timestamp=datetime.now(timezone.utc), event="Test"
        # )
        # integrator.episodic.store_episode(episode)
        # stats = integrator.get_statistics()
        # assert stats["concepts"] == 1
        # assert stats["rules"] == 1
        # assert stats["episodes"] == 1
        pytest.skip(
            "Use test_semantic_memory.py, test_narrative_history.py, "
            "test_procedural_memory.py instead"
        )
