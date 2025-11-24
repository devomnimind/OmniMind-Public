# src/autopoietic/meta_architect.py
"""Meta‑Architect module.

This module provides a simple *meta‑architect* that analyses high‑level system
requirements and produces concrete component specifications. The implementation
is intentionally lightweight for the prototype phase – it demonstrates the
workflow without relying on external AI services.

The class `MetaArchitect` exposes a single public method
`generate_specifications` which receives a dictionary describing desired
capabilities and returns a list of `ComponentSpec` dataclasses.

All functions include full type hints and Google‑style docstrings to satisfy
OmniMind’s strict quality rules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Mapping, Sequence

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ComponentSpec:
    """Specification for a generated component.

    Attributes:
        name: Human‑readable identifier of the component.
        type: Logical type (e.g. "synthesizer", "repair", "boundary").
        config: Arbitrary configuration dictionary required for the component.
    """

    name: str
    type: str
    config: Mapping[str, str]


class MetaArchitect:
    """Generate component specifications from high‑level requirements.

    The meta‑architect does not create code directly; it only produces
    specifications that other parts of the autopoietic pipeline (e.g. the
    `CodeSynthesizer`) can consume.
    """

    def __init__(self) -> None:
        """Create a new ``MetaArchitect`` instance.

        The constructor sets up a logger; no heavy resources are allocated.
        """
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.debug("MetaArchitect initialized")

    def generate_specifications(
        self, requirements: Mapping[str, Sequence[str]]
    ) -> List[ComponentSpec]:
        """Generate a list of ``ComponentSpec`` objects.

        Args:
            requirements: Mapping where keys are capability names (e.g.
                ``"synthesizer"``) and values are lists of component names that
                should fulfil the capability.

        Returns:
            A list of ``ComponentSpec`` instances ready for consumption by the
            code synthesizer.
        """
        specs: List[ComponentSpec] = []
        for comp_type, names in requirements.items():
            for name in names:
                config = {"generated_by": "MetaArchitect", "version": "1.0"}
                spec = ComponentSpec(name=name, type=comp_type, config=config)
                specs.append(spec)
                self._logger.debug("Generated spec: %s (type=%s)", name, comp_type)
        return specs

    def validate_specifications(self, specs: Sequence[ComponentSpec]) -> bool:
        """Validate a list of specifications.

        The current validation is minimal – it checks that each spec has a non‑
        empty name and type. In a full implementation additional checks (e.g.
        schema validation) would be performed.

        Args:
            specs: Sequence of ``ComponentSpec`` objects.

        Returns:
            ``True`` if all specifications appear valid, ``False`` otherwise.
        """
        for spec in specs:
            if not spec.name or not spec.type:
                self._logger.error("Invalid spec detected: %s", spec)
                return False
        self._logger.debug("All %d specs validated successfully", len(specs))
        return True
