# tests/autopoietic/test_meta_architect.py
"""Tests for the MetaArchitect module.

Ensures that specifications are generated correctly and validated.
"""

from src.autopoietic.meta_architect import ComponentSpec, MetaArchitect


def test_generate_specifications() -> None:
    architect = MetaArchitect()
    requirements = {"synthesizer": ["code_synthesizer"], "repair": ["advanced_repair"]}
    specs = architect.generate_specifications(requirements)
    assert len(specs) == 2
    names = {spec.name for spec in specs}
    assert "code_synthesizer" in names
    assert "advanced_repair" in names
    for spec in specs:
        assert isinstance(spec, ComponentSpec)
        assert spec.config["generated_by"] == "MetaArchitect"


def test_validate_specifications_success() -> None:
    architect = MetaArchitect()
    specs = [
        ComponentSpec(name="comp1", type="type1", config={"a": "b"}),
        ComponentSpec(name="comp2", type="type2", config={"c": "d"}),
    ]
    assert architect.validate_specifications(specs) is True


def test_validate_specifications_failure() -> None:
    architect = MetaArchitect()
    specs = [ComponentSpec(name="", type="type", config={})]
    assert architect.validate_specifications(specs) is False
