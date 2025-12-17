"""Tests for Episodic Knowledge Layer - Phase 26A

DEPRECATED: Módulo knowledge.episodic_layer não existe mais.

SUBSTITUIÇÃO:
- ✅ Substituído por: src.memory.narrative_history.NarrativeHistory (Lacanian approach)
- ✅ Arquivo: src/memory/narrative_history.py
- ✅ Funcionalidade: Memória episódica com abordagem Lacaniana (construção retroativa)
- ✅ Status: Implementado e operacional (2025-12-05)

MIGRAÇÃO:
```python
# ANTES (deprecated):
from knowledge.episodic_layer import Episode, EpisodicLayer
layer = EpisodicLayer()
episode = Episode(...)
layer.store_episode(episode)

# DEPOIS (atual - Lacanian):
from src.memory.narrative_history import NarrativeHistory
history = NarrativeHistory()
# Inscrição sem significado (Lacanian)
event_id = history.inscribe_event(
    {"task": "learn", "action": "read", "result": "understood"},
    without_meaning=True
)
# Ressignificação retroativa (Nachträglichkeit)
history.retroactive_signification(event_id, "This means understanding")
# Construção narrativa
narrative = history.construct_narrative("learning process")
```

NOTA: NarrativeHistory usa EpisodicMemory como backend, mas com semântica Lacaniana.
Este teste foi marcado como skip até que seja atualizado para usar NarrativeHistory.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(
    reason=(
        "Módulo knowledge.episodic_layer foi substituído por "
        "src.memory.narrative_history (Lacanian)"
    )
)

# Import removido - módulo não existe
# from knowledge.episodic_layer import Episode, EpisodicLayer
#
# SUBSTITUIÇÃO: Use src.memory.narrative_history.NarrativeHistory


class TestEpisodicLayer:
    """Test Episodic Knowledge Layer - DEPRECATED: Use NarrativeHistory instead"""

    def test_init(self):
        """Test initialization - DEPRECATED"""
        # Nota: EpisodicLayer foi substituído por NarrativeHistory (Lacanian)
        # layer = EpisodicLayer()  # DEPRECATED
        # assert layer is not None
        # assert len(layer.episodes) == 0
        pytest.skip("Use test_narrative_history.py instead")

    def test_store_episode(self):
        """Test storing an episode - DEPRECATED"""
        # Nota: EpisodicLayer foi substituído por NarrativeHistory (Lacanian)
        # layer = EpisodicLayer()  # DEPRECATED
        # episode = Episode(  # DEPRECATED
        #     id="ep_1",
        #     timestamp=datetime.now(timezone.utc),
        #     event="Memory issue detected and resolved",
        #     outcome="Memory usage reduced from 95% to 60%",
        #     learned="Reducing batch_size helps with memory",
        # )
        # episode_id = layer.store_episode(episode)
        # assert episode_id == "ep_1"
        # assert "ep_1" in layer.episodes
        # assert layer.episodes["ep_1"].event == "Memory issue detected and resolved"
        pytest.skip("Use test_narrative_history.py instead")

    def test_get_episode(self):
        """Test retrieving an episode - DEPRECATED"""
        # Nota: EpisodicLayer foi substituído por NarrativeHistory (Lacanian)
        # layer = EpisodicLayer()  # DEPRECATED
        # episode = Episode(  # DEPRECATED
        #     id="ep_2",
        #     timestamp=datetime.now(timezone.utc),
        #     event="CPU optimization applied",
        #     outcome="CPU usage reduced",
        # )
        # layer.store_episode(episode)
        # retrieved = layer.get_episode("ep_2")
        # assert retrieved is not None
        # assert retrieved.event == "CPU optimization applied"
        pytest.skip("Use test_narrative_history.py instead")

    def test_get_recent_episodes(self):
        """Test getting recent episodes - DEPRECATED"""
        # Nota: EpisodicLayer foi substituído por NarrativeHistory (Lacanian)
        # layer = EpisodicLayer()  # DEPRECATED
        # now = datetime.now(timezone.utc)
        # episode1 = Episode(  # DEPRECATED
        #     id="ep_3", timestamp=now - timedelta(hours=1), event="Event1"
        # )
        # episode2 = Episode(  # DEPRECATED
        #     id="ep_4", timestamp=now - timedelta(hours=2), event="Event2"
        # )
        # episode3 = Episode(id="ep_5", timestamp=now, event="Event3")  # DEPRECATED
        # layer.store_episode(episode1)
        # layer.store_episode(episode2)
        # layer.store_episode(episode3)
        # recent = layer.get_recent_episodes(limit=2)
        # assert len(recent) == 2
        # assert recent[0].id == "ep_5"
        # assert recent[1].id == "ep_3"
        pytest.skip("Use test_narrative_history.py instead")
