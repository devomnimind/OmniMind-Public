# tests/autopoietic/test_code_synthesizer.py
"""Tests for the CodeSynthesizer module.

Validates that component specifications are turned into valid Python source
strings and that the generated class contains expected attributes.
"""

from src.autopoietic.code_synthesizer import CodeSynthesizer, ComponentSpec


def test_synthesize_single_spec() -> None:
    spec = ComponentSpec(
        name="example_component", type="synthesizer", config={"key": "value"}
    )
    synthesizer = CodeSynthesizer()
    result = synthesizer.synthesize([spec])
    assert "example_component" in result
    synthesized = result["example_component"]
    assert isinstance(synthesized.source_code, str)
    # Verify that class name is correctly PascalCased
    assert "class ExampleComponent" in synthesized.source_code
    # Verify config assignment appears
    assert "self.key = 'value'" in synthesized.source_code


def test_generate_multiple_specs() -> None:
    specs = [
        ComponentSpec(name="comp_one", type="type1", config={"a": "1"}),
        ComponentSpec(name="comp_two", type="type2", config={"b": "2"}),
    ]
    synthesizer = CodeSynthesizer()
    result = synthesizer.synthesize(specs)
    assert set(result.keys()) == {"comp_one", "comp_two"}
    for name, synthesized in result.items():
        assert f"class {name.title().replace('_', '')}" in synthesized.source_code
