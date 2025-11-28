from src.autopoietic.meta_architect import ComponentSpec, MetaArchitect

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

# tests/autopoietic/test_meta_architect.py
"""Tests for the MetaArchitect module.

Ensures that specifications are generated correctly and validated.
"""


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
