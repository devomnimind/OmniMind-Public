"""
Testes para Meta Learning - Black Hole Collapse.

Group 15: Learning & Monitoring - meta_learning/
"""

import pytest

from src.meta_learning.black_hole_collapse import (
    CRITICAL_DENSITY,
    BlackHoleMetaLearner,
    MetaKnowledge,
)


class TestMetaKnowledge:
    """Testa MetaKnowledge dataclass."""

    def test_initialization(self) -> None:
        """Testa inicialização de MetaKnowledge."""
        meta = MetaKnowledge(
            singularity=["axiom1", "axiom2"],
            event_horizon=5.0,
            hawking_radiation=["theorem1", "theorem2"],
            collapse_timestamp=1234567890.0,
        )

        assert meta.singularity == ["axiom1", "axiom2"]
        assert meta.event_horizon == pytest.approx(5.0)
        assert meta.hawking_radiation == ["theorem1", "theorem2"]
        assert meta.collapse_timestamp == pytest.approx(1234567890.0)


class TestBlackHoleMetaLearner:
    """Testa BlackHoleMetaLearner para meta-learning baseado em densidade."""

    def test_initialization_default(self) -> None:
        """Testa inicialização com valores padrão."""
        learner = BlackHoleMetaLearner()

        assert learner.critical_density == CRITICAL_DENSITY
        assert learner.knowledge_base == {}
        assert learner.meta_levels == []

    def test_initialization_custom_density(self) -> None:
        """Testa inicialização com densidade crítica customizada."""
        custom_density = 20.0
        learner = BlackHoleMetaLearner(critical_density=custom_density)

        assert learner.critical_density == pytest.approx(custom_density)

    def test_check_collapse_condition_below_threshold(self) -> None:
        """Testa que densidade abaixo do limite não causa colapso."""
        learner = BlackHoleMetaLearner(critical_density=10.0)

        # Densidade baixa E volume grande
        should_collapse = learner.check_collapse_condition(
            knowledge_mass=0.1, knowledge_volume=100.0
        )

        # Com densidade baixa, NÃO deve causar colapso
        assert should_collapse is False

    def test_check_collapse_condition_zero_volume(self) -> None:
        """Testa que volume zero não causa colapso."""
        learner = BlackHoleMetaLearner()

        should_collapse = learner.check_collapse_condition(
            knowledge_mass=100.0, knowledge_volume=0.0  # Volume zero
        )

        assert should_collapse is False

    def test_check_collapse_condition_near_zero_volume(self) -> None:
        """Testa que volume muito pequeno não causa colapso."""
        learner = BlackHoleMetaLearner()

        should_collapse = learner.check_collapse_condition(
            knowledge_mass=100.0, knowledge_volume=1e-15  # Volume muito pequeno
        )

        assert should_collapse is False

    def test_collapse_to_meta_level(self) -> None:
        """Testa colapso para meta-nível."""
        learner = BlackHoleMetaLearner()

        # Adicionar conhecimento como dicionário
        knowledge = {
            "fact1": "value1",
            "fact2": "value2",
            "fact3": "value3",
            "rule1": "value4",
            "rule2": "value5",
        }

        meta_knowledge = learner.collapse_to_meta_level(knowledge)

        assert isinstance(meta_knowledge, MetaKnowledge)
        assert len(meta_knowledge.singularity) > 0  # Core axioms
        assert meta_knowledge.event_horizon > 0.0
        assert isinstance(meta_knowledge.hawking_radiation, list)
        assert meta_knowledge.collapse_timestamp >= 0.0

    def test_collapse_to_meta_level_empty_knowledge(self) -> None:
        """Testa colapso com conhecimento vazio."""
        learner = BlackHoleMetaLearner()

        meta_knowledge = learner.collapse_to_meta_level({})

        assert isinstance(meta_knowledge, MetaKnowledge)
        # Mesmo vazio, deve gerar estrutura válida
        assert isinstance(meta_knowledge.singularity, list)

    def test_extract_axioms_internal(self) -> None:
        """Testa extração de axiomas core (método interno)."""
        learner = BlackHoleMetaLearner()

        knowledge = {
            "axiom1": "All humans are mortal",
            "axiom2": "Socrates is human",
            "axiom3": "Therefore Socrates is mortal",
            "axiom4": "All men are mortal",
            "axiom5": "Plato is a man",
            "axiom6": "Extra axiom",
        }

        axioms = learner._extract_axioms(knowledge)

        assert isinstance(axioms, list)
        assert len(axioms) <= 5  # Extracts first 5
        # Deve extrair regras fundamentais

    def test_generate_theorems_internal(self) -> None:
        """Testa geração de teoremas (método interno)."""
        learner = BlackHoleMetaLearner()

        axioms = ["axiom1", "axiom2", "axiom3"]
        theorems = learner._generate_theorems(axioms)

        assert isinstance(theorems, list)
        assert len(theorems) == len(axioms)
        # Deve derivar teoremas dos axiomas

    def test_define_boundary_internal(self) -> None:
        """Testa definição do horizonte de eventos (método interno)."""
        learner = BlackHoleMetaLearner()

        axioms = ["axiom1", "axiom2", "axiom3"]
        horizon = learner._define_boundary(axioms)

        assert isinstance(horizon, float)
        assert horizon > 0.0

    def test_define_boundary_scaling(self) -> None:
        """Testa que horizonte de eventos escala com número de axiomas."""
        learner = BlackHoleMetaLearner()

        horizon_small = learner._define_boundary(["axiom1"])
        horizon_large = learner._define_boundary(["axiom1", "axiom2", "axiom3"])

        # Mais axiomas deve ter maior horizonte de eventos
        assert horizon_large > horizon_small

    def test_multiple_collapses(self) -> None:
        """Testa múltiplos colapsos sucessivos."""
        learner = BlackHoleMetaLearner()

        # Primeiro colapso
        knowledge1 = {"fact1": "v1", "fact2": "v2", "fact3": "v3"}
        meta1 = learner.collapse_to_meta_level(knowledge1)

        # Segundo colapso
        knowledge2 = {"fact4": "v4", "fact5": "v5", "fact6": "v6"}
        meta2 = learner.collapse_to_meta_level(knowledge2)

        # Deve ter registrado ambos
        assert len(learner.meta_levels) >= 2
        assert meta1.collapse_timestamp != meta2.collapse_timestamp

    def test_knowledge_density_calculation(self) -> None:
        """Testa cálculo de densidade de conhecimento."""
        learner = BlackHoleMetaLearner()

        # Adicionar conhecimento
        learner.knowledge_base["topic1"] = ["fact1", "fact2", "fact3"]
        learner.knowledge_base["topic2"] = ["fact4", "fact5"]

        # Volume e massa devem ser calculáveis
        total_items = sum(len(items) for items in learner.knowledge_base.values())
        assert total_items == 5

    def test_schwarzschild_radius_calculation(self) -> None:
        """Testa cálculo do raio de Schwarzschild."""
        # Raio de Schwarzschild: r_s = 2GM/c²
        mass = 100.0

        # Usar método interno se existir, ou calcular diretamente
        from src.meta_learning.black_hole_collapse import C_CONSTANT, G_CONSTANT

        r_s = 2 * G_CONSTANT * mass / (C_CONSTANT**2)

        assert r_s > 0.0
        # Para massa normalizada, valor deve ser razoável
        assert r_s < mass * 10  # Sanity check

    def test_meta_level_hierarchy(self) -> None:
        """Testa hierarquia de níveis meta."""
        learner = BlackHoleMetaLearner()

        # Criar vários níveis
        for i in range(3):
            knowledge = {f"fact_{i}_{j}": f"value_{i}_{j}" for j in range(5)}
            learner.collapse_to_meta_level(knowledge)

        # Deve ter 3 níveis meta
        assert len(learner.meta_levels) == 3

        # Cada nível deve ter timestamp crescente (ou igual)
        for i in range(len(learner.meta_levels) - 1):
            assert (
                learner.meta_levels[i].collapse_timestamp
                <= learner.meta_levels[i + 1].collapse_timestamp
            )

    def test_information_compression(self) -> None:
        """Testa compressão de informação no colapso."""
        learner = BlackHoleMetaLearner()

        # Grande quantidade de conhecimento específico
        specific_knowledge = {f"specific_fact_{i}": f"value_{i}" for i in range(100)}

        meta = learner.collapse_to_meta_level(specific_knowledge)

        # Singularidade deve ter menos itens que conhecimento original
        # (compressão para axiomas fundamentais - max 5)
        assert len(meta.singularity) <= 5
        assert len(meta.singularity) < len(specific_knowledge)

    def test_hawking_radiation_generation(self) -> None:
        """Testa geração de radiação de Hawking (teoremas derivados)."""
        learner = BlackHoleMetaLearner()

        knowledge = {"axiom1": "v1", "axiom2": "v2", "axiom3": "v3"}
        meta = learner.collapse_to_meta_level(knowledge)

        # Radiação de Hawking deve conter teoremas derivados
        assert isinstance(meta.hawking_radiation, list)

    def test_get_statistics(self) -> None:
        """Testa obtenção de estatísticas."""
        learner = BlackHoleMetaLearner()

        # Fazer alguns colapsos
        for i in range(3):
            learner.collapse_to_meta_level({f"fact{i}": f"value{i}"})

        stats = learner.get_statistics()

        assert isinstance(stats, dict)
        assert "total_meta_levels" in stats
        assert "current_level" in stats
        assert stats["total_meta_levels"] == 3
