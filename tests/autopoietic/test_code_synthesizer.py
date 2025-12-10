# tests/autopoietic/test_code_synthesizer.py
"""Tests for the CodeSynthesizer module.

Validates that component specifications are turned into valid Python source
strings and that the generated class contains expected attributes.
"""

from src.autopoietic.code_synthesizer import CodeSynthesizer, ComponentSpec


def test_synthesize_single_spec() -> None:
    spec = ComponentSpec(name="example_component", type="synthesizer", config={"key": "value"})
    synthesizer = CodeSynthesizer()
    result = synthesizer.synthesize([spec])
    # 🔒 Security signatures are now added to component names
    expected_key = "modulo_autopoiesis_data_example_component"
    assert expected_key in result
    synthesized = result[expected_key]
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
    # 🔒 Security signatures are now added to component names
    expected_keys = {"modulo_autopoiesis_data_comp_one", "modulo_autopoiesis_data_comp_two"}
    assert set(result.keys()) == expected_keys
    for name, synthesized in result.items():
        # Verify the signed name contains the original name
        assert "comp_one" in name or "comp_two" in name
        # The class name in the source code is based on the original spec name, not the signed name
        original_name = name.replace("modulo_autopoiesis_data_", "")
        expected_class_name = original_name.title().replace("_", "")
        assert f"class {expected_class_name}" in synthesized.source_code
