# src/autopoietic/advanced_repair.py
"""Advanced Self‑Repair module.

Detects failures in registered components and automatically generates patches
using the ``CodeSynthesizer``. The implementation is deterministic and does
not rely on external AI services, satisfying OmniMind’s production constraints.
All functions include full type hints and Google‑style docstrings.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Mapping

from .code_synthesizer import CodeSynthesizer, SynthesizedComponent
from .meta_architect import ComponentSpec

logger = logging.getLogger(__name__)


class AdvancedRepair:
    """Detect component failures and synthesize corrective code.

    The workflow is:
    1. ``detect_failures`` receives a mapping of component names to error
       messages.
    2. For each failure a minimal ``ComponentSpec`` is generated describing a
       *repair* component.
    3. ``CodeSynthesizer`` creates Python source for the repair.
    4. ``apply_patches`` writes the generated source to the appropriate file
       path (simulated here by returning a dict of file contents).
    """

    def __init__(self) -> None:
        """Create a new ``AdvancedRepair`` instance with its own logger."""
        self._logger = logger.getChild(self.__class__.__name__)
        self._synthesizer = CodeSynthesizer()
        self._logger.debug("AdvancedRepair initialized")

    def detect_failures(self, error_map: Mapping[str, str]) -> List[ComponentSpec]:
        """Convert error messages into repair specifications.

        Args:
            error_map: Mapping from component name to an error description.

        Returns:
            List of ``ComponentSpec`` objects describing repair components.
        """
        specs: List[ComponentSpec] = []
        for comp_name, error_msg in error_map.items():
            repair_name = f"repair_{comp_name}"
            config = {
                "original_component": comp_name,
                "error": error_msg,
                "generated_by": "AdvancedRepair",
            }
            spec = ComponentSpec(name=repair_name, type="repair", config=config)
            specs.append(spec)
            self._logger.debug("Created repair spec %s for component %s", repair_name, comp_name)
        return specs

    def synthesize_patches(self, specs: List[ComponentSpec]) -> Dict[str, SynthesizedComponent]:
        """Generate source code patches for a list of repair specifications.

        Args:
            specs: List of ``ComponentSpec`` objects.

        Returns:
            Mapping from repair component name to ``SynthesizedComponent``.
        """
        patches = self._synthesizer.synthesize(specs)
        self._logger.debug("Synthesized %d repair patches", len(patches))
        return patches

    def apply_patches(self, patches: Mapping[str, SynthesizedComponent]) -> Dict[str, str]:
        """Simulate applying patches by returning file paths and contents.

        In a real system this would write files to disk and trigger a reload.
        Here we simply return a dictionary mapping a hypothetical file path to the
        generated source code.

        Args:
            patches: Mapping from component name to ``SynthesizedComponent``.

        Returns:
            Mapping from file path (string) to source code (string).
        """
        applied: Dict[str, str] = {}
        for name, synth in patches.items():
            # Example path: src/autopoietic/repairs/<name>.py
            path = f"src/autopoietic/repairs/{name}.py"
            applied[path] = synth.source_code
            self._logger.info("Applied patch for %s at %s", name, path)
        return applied
