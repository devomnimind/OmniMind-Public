"""Tests for Procedural Knowledge Layer - Phase 26A

DEPRECATED: Módulo knowledge.procedural_layer não existe mais.

SUBSTITUIÇÃO:
- ✅ Substituído por: src.memory.procedural_memory.ProceduralMemory
- ✅ Arquivo: src/memory/procedural_memory.py
- ✅ Funcionalidade: Armazenamento de habilidades e procedimentos ("knowing how")
- ✅ Status: Implementado e operacional

MIGRAÇÃO:
```python
# ANTES (deprecated):
from knowledge.procedural_layer import ProceduralLayer, Rule
layer = ProceduralLayer()
rule = Rule(id="rule1", name="rule1", ...)
layer.store_rule(rule)

# DEPOIS (atual):
from src.memory.procedural_memory import ProceduralMemory, Skill
memory = ProceduralMemory()
skill = memory.learn_skill(
    name="problem_solving",
    steps=["analyze", "plan", "execute", "validate"],
    parameters={"timeout": 30}
)
# Execução de habilidade
result = memory.execute_skill("problem_solving", context={...})
```

Este teste foi marcado como skip até que seja atualizado para usar ProceduralMemory.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(
    reason="Módulo knowledge.procedural_layer foi substituído por src.memory.procedural_memory"
)

# Import removido - módulo não existe
# from knowledge.procedural_layer import ProceduralLayer, Rule
#
# SUBSTITUIÇÃO: Use src.memory.procedural_memory.ProceduralMemory


class TestProceduralLayer:
    """Test Procedural Knowledge Layer - DEPRECATED: Use ProceduralMemory instead"""

    def test_init(self):
        """Test initialization - DEPRECATED"""
        # Nota: ProceduralLayer foi substituído por ProceduralMemory
        # layer = ProceduralLayer()  # DEPRECATED
        # assert layer is not None
        # assert len(layer.rules) == 0
        pytest.skip("Use test_procedural_memory.py instead")

    def test_store_rule(self):
        """Test storing a rule - DEPRECATED"""
        # Nota: ProceduralLayer foi substituído por ProceduralMemory
        # layer = ProceduralLayer()  # DEPRECATED
        # rule = Rule(  # DEPRECATED
        #     id="rule_1",
        #     name="Memory Optimization",
        #     description="Reduce batch size when memory is high",
        #     rule_type="process",
        #     conditions=["memory > 90%"],
        #     actions=["reduce batch_size", "disable cache"],
        # )
        # rule_id = layer.store_rule(rule)
        # assert rule_id == "rule_1"
        # assert "rule_1" in layer.rules
        # assert layer.rules["rule_1"].name == "Memory Optimization"
        pytest.skip("Use test_procedural_memory.py instead")

    def test_get_rule(self):
        """Test retrieving a rule - DEPRECATED"""
        # Nota: ProceduralLayer foi substituído por ProceduralMemory
        # layer = ProceduralLayer()  # DEPRECATED
        # rule = Rule(  # DEPRECATED
        #     id="rule_2",
        #     name="CPU Optimization",
        #     description="Enable GPU when CPU is high",
        #     rule_type="rule",
        # )
        # layer.store_rule(rule)
        # retrieved = layer.get_rule("rule_2")
        # assert retrieved is not None
        # assert retrieved.name == "CPU Optimization"
        pytest.skip("Use test_procedural_memory.py instead")

    def test_get_rules_by_type(self):
        """Test getting rules by type - DEPRECATED"""
        # Nota: ProceduralLayer foi substituído por ProceduralMemory
        # layer = ProceduralLayer()  # DEPRECATED
        # rule1 = Rule(  # DEPRECATED
        #     id="rule_3", name="Rule1", description="Description1", rule_type="process"
        # )
        # rule2 = Rule(  # DEPRECATED
        #     id="rule_4", name="Rule2", description="Description2", rule_type="process"
        # )
        # rule3 = Rule(  # DEPRECATED
        #     id="rule_5", name="Rule3", description="Description3", rule_type="rule"
        # )
        # layer.store_rule(rule1)
        # layer.store_rule(rule2)
        # layer.store_rule(rule3)
        # process_rules = layer.get_rules_by_type("process")
        # assert len(process_rules) == 2
        # assert all(r.rule_type == "process" for r in process_rules)
        pytest.skip("Use test_procedural_memory.py instead")
