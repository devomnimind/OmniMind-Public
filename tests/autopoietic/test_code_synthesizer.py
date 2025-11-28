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
