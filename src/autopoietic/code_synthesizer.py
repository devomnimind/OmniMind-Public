from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Sequence
from .meta_architect import ComponentSpec


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

"""Code Synthesizer module.

Provides a lightweight code synthesizer that turns a ComponentSpec into a minimal
Python implementation. No external LLMs are used; the synthesizer builds
deterministic stub code based on the component type.

All functions include full type hints and Google‑style docstrings to satisfy
OmniMind’s strict quality rules.
"""


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SynthesizedComponent:
    """Result of code synthesis.

    Attributes:
        name: Component name.
        source_code: Generated Python source as a string.
    """

    name: str
    source_code: str


class CodeSynthesizer:
    """Generate Python source code from ComponentSpec objects.

    The synthesizer creates a minimal, syntactically correct Python class for
    each specification. The generated class defines an ``__init__`` that stores
    the configuration and a ``run`` method that logs a placeholder action.
    """

    def __init__(self) -> None:
        """Create a new CodeSynthesizer instance."""
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.debug("CodeSynthesizer initialized")

    def synthesize(self, specs: Sequence[ComponentSpec]) -> Dict[str, SynthesizedComponent]:
        """Synthesize source code for a sequence of component specifications.

        Args:
            specs: Iterable of ComponentSpec objects.

        Returns:
            Mapping from component name to SynthesizedComponent containing the
            generated source code.
        """
        result: Dict[str, SynthesizedComponent] = {}
        for spec in specs:
            source = self._generate_class_source(spec)
            result[spec.name] = SynthesizedComponent(name=spec.name, source_code=source)
            self._logger.debug("Synthesized component %s", spec.name)
        return result

    def _generate_class_source(self, spec: ComponentSpec) -> str:
        """Generate a Python class source string for a single ComponentSpec.

        The class name is derived from spec.name (converted to PascalCase). The
        run method simply logs that the component was invoked.
        """
        class_name = self._to_pascal_case(spec.name)
        config_items = "\n        ".join(
            f"self.{key} = '{value}'" for key, value in spec.config.items()
        )
        source = f"""class {class_name}:
    \"\"\"Auto‑generated component of type '{spec.type}'.\"\"\"
    def __init__(self):
        # Configuration injected by MetaArchitect
        {config_items}
        self._logger = logging.getLogger(__name__)

    def run(self) -> None:
        \"\"\"Placeholder execution method.

        In a real system this would contain the component's logic.
        \"\"\"
        self._logger.info(f\"Running {class_name} component\")
"""
        return source

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """Convert a snake_case name to PascalCase.

        Args:
            name: Original component name.

        Returns:
            PascalCase version suitable for a Python class name.
        """
        return "".join(part.capitalize() for part in name.split("_"))
