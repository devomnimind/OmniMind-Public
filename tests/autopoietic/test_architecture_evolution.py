"""Testes para ArchitectureEvolution (architecture_evolution.py).

Cobertura de:
- Inicialização do sistema de evolução
- Proposta de evolução (propose_evolution)
- Validação de especificações evoluídas
- Integração com MetaArchitect
"""

from __future__ import annotations

import pytest
from typing import Dict, List

from src.autopoietic.architecture_evolution import ArchitectureEvolution
from src.autopoietic.meta_architect import ComponentSpec, MetaArchitect


class TestArchitectureEvolution:
    """Testes para o módulo de evolução de arquitetura."""

    @pytest.fixture
    def meta_architect(self) -> MetaArchitect:
        """Fixture que fornece uma instância de MetaArchitect."""
        return MetaArchitect()

    @pytest.fixture
    def evolution(self, meta_architect: MetaArchitect) -> ArchitectureEvolution:
        """Fixture que fornece uma instância de ArchitectureEvolution."""
        return ArchitectureEvolution(meta_architect)

    def test_initialization(self, meta_architect: MetaArchitect) -> None:
        """Testa inicialização do ArchitectureEvolution."""
        evolution = ArchitectureEvolution(meta_architect)
        assert evolution is not None
        assert evolution._meta_architect is meta_architect

    def test_propose_evolution_empty(self, evolution: ArchitectureEvolution) -> None:
        """Testa proposta de evolução com dicionário vazio."""
        evolved = evolution.propose_evolution({})
        assert isinstance(evolved, list)
        assert len(evolved) == 0

    def test_propose_evolution_single(self, evolution: ArchitectureEvolution) -> None:
        """Testa proposta de evolução para um único componente."""
        existing = {
            "component_a": ComponentSpec(
                name="component_a",
                type="synthesizer",
                config={"param": "value"}
            )
        }
        
        evolved = evolution.propose_evolution(existing)
        
        assert isinstance(evolved, list)
        assert len(evolved) == 1
        
        spec = evolved[0]
        assert isinstance(spec, ComponentSpec)
        assert spec.name == "evolved_component_a"
        assert spec.type == "synthesizer"
        assert spec.config["evolved"] == "true"
        assert spec.config["param"] == "value"

    def test_propose_evolution_multiple(self, evolution: ArchitectureEvolution) -> None:
        """Testa proposta de evolução para múltiplos componentes."""
        existing = {
            "comp_x": ComponentSpec(
                name="comp_x",
                type="type_x",
                config={"x": "1"}
            ),
            "comp_y": ComponentSpec(
                name="comp_y",
                type="type_y",
                config={"y": "2"}
            ),
            "comp_z": ComponentSpec(
                name="comp_z",
                type="type_z",
                config={"z": "3"}
            ),
        }
        
        evolved = evolution.propose_evolution(existing)
        
        assert len(evolved) == 3
        
        names = [spec.name for spec in evolved]
        assert "evolved_comp_x" in names
        assert "evolved_comp_y" in names
        assert "evolved_comp_z" in names
        
        # Verifica que todos mantiveram seus tipos
        for spec in evolved:
            original_name = spec.name.replace("evolved_", "")
            original_type = existing[original_name].type
            assert spec.type == original_type

    def test_propose_evolution_preserves_config(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa que a evolução preserva configurações originais."""
        existing = {
            "test_comp": ComponentSpec(
                name="test_comp",
                type="test_type",
                config={"key1": "value1", "key2": "value2", "key3": "value3"}
            )
        }
        
        evolved = evolution.propose_evolution(existing)
        
        assert len(evolved) == 1
        evolved_spec = evolved[0]
        
        # Verifica que as configurações originais foram preservadas
        assert evolved_spec.config["key1"] == "value1"
        assert evolved_spec.config["key2"] == "value2"
        assert evolved_spec.config["key3"] == "value3"
        # E que a flag evolved foi adicionada
        assert evolved_spec.config["evolved"] == "true"

    def test_propose_evolution_adds_evolved_flag(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa que a flag 'evolved' é adicionada à configuração."""
        existing = {
            "component": ComponentSpec(
                name="component",
                type="any_type",
                config={}
            )
        }
        
        evolved = evolution.propose_evolution(existing)
        
        assert evolved[0].config["evolved"] == "true"

    def test_propose_evolution_preserves_type(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa que os tipos dos componentes são preservados."""
        types_to_test = ["synthesizer", "repair", "boundary", "custom"]
        existing = {
            f"comp_{t}": ComponentSpec(
                name=f"comp_{t}",
                type=t,
                config={}
            )
            for t in types_to_test
        }
        
        evolved = evolution.propose_evolution(existing)
        
        for spec in evolved:
            original_name = spec.name.replace("evolved_", "")
            assert spec.type == existing[original_name].type

    def test_propose_evolution_validation_success(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa que a validação é bem-sucedida para specs válidos."""
        existing = {
            "valid_component": ComponentSpec(
                name="valid_component",
                type="synthesizer",
                config={"valid": "config"}
            )
        }
        
        # Não deve lançar exceção
        evolved = evolution.propose_evolution(existing)
        assert len(evolved) == 1

    def test_propose_evolution_creates_correct_names(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa que os nomes evoluídos são criados corretamente."""
        existing = {
            "simple": ComponentSpec("simple", "type1", {}),
            "with_underscore": ComponentSpec("with_underscore", "type2", {}),
            "multiple_words_here": ComponentSpec("multiple_words_here", "type3", {}),
        }
        
        evolved = evolution.propose_evolution(existing)
        
        names = {spec.name for spec in evolved}
        assert "evolved_simple" in names
        assert "evolved_with_underscore" in names
        assert "evolved_multiple_words_here" in names

    def test_propose_evolution_with_empty_config(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa evolução de componentes com config vazia."""
        existing = {
            "empty_config": ComponentSpec(
                name="empty_config",
                type="test",
                config={}
            )
        }
        
        evolved = evolution.propose_evolution(existing)
        
        assert len(evolved) == 1
        # Config deve ter apenas a flag evolved
        assert evolved[0].config["evolved"] == "true"
        assert len(evolved[0].config) == 1

    def test_propose_evolution_with_complex_config(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa evolução de componentes com config complexa."""
        existing = {
            "complex": ComponentSpec(
                name="complex",
                type="advanced",
                config={
                    "nested": "value",
                    "number": "42",
                    "flag": "true",
                    "list_like": "item1,item2,item3"
                }
            )
        }
        
        evolved = evolution.propose_evolution(existing)
        
        assert len(evolved) == 1
        spec = evolved[0]
        
        # Todas as configurações originais devem estar presentes
        assert spec.config["nested"] == "value"
        assert spec.config["number"] == "42"
        assert spec.config["flag"] == "true"
        assert spec.config["list_like"] == "item1,item2,item3"
        assert spec.config["evolved"] == "true"

    def test_propose_evolution_multiple_iterations(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa múltiplas iterações de evolução."""
        # Primeira evolução
        existing_v1 = {
            "base": ComponentSpec("base", "type", {"version": "1"})
        }
        evolved_v1 = evolution.propose_evolution(existing_v1)
        
        # Segunda evolução
        existing_v2 = {
            evolved_v1[0].name: evolved_v1[0]
        }
        evolved_v2 = evolution.propose_evolution(existing_v2)
        
        assert len(evolved_v2) == 1
        assert evolved_v2[0].name == "evolved_evolved_base"
        assert evolved_v2[0].config["version"] == "1"
        assert evolved_v2[0].config["evolved"] == "true"

    def test_integration_with_meta_architect(
        self, meta_architect: MetaArchitect
    ) -> None:
        """Testa integração completa com MetaArchitect."""
        # Usa MetaArchitect para gerar specs
        requirements = {"capabilities": ["feature1", "feature2"]}
        original_specs = meta_architect.generate_specifications(requirements)
        
        # Cria dicionário de specs
        existing = {spec.name: spec for spec in original_specs}
        
        # Evolui
        evolution = ArchitectureEvolution(meta_architect)
        evolved = evolution.propose_evolution(existing)
        
        # Verifica resultado
        assert len(evolved) == len(original_specs)
        for spec in evolved:
            assert spec.name.startswith("evolved_")
            assert spec.config["evolved"] == "true"

    def test_propose_evolution_maintains_immutability(
        self, evolution: ArchitectureEvolution
    ) -> None:
        """Testa que os specs originais não são modificados."""
        original_config = {"original": "value"}
        existing = {
            "component": ComponentSpec(
                name="component",
                type="test",
                config=original_config
            )
        }
        
        evolved = evolution.propose_evolution(existing)
        
        # Config original não deve ter a flag evolved
        assert "evolved" not in existing["component"].config
        # Config evoluída deve ter a flag
        assert evolved[0].config["evolved"] == "true"
