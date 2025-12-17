# src/autopoietic/architecture_evolution.py
"""Architecture Evolution module.

Provides a lightweight *architecture evolution* engine that analyses existing
component specifications and proposes evolved components. The implementation is
deterministic and does not rely on external AI services, satisfying OmniMind’s
production constraints.

All functions include full type hints and Google‑style docstrings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Mapping, Optional

from .meta_architect import ComponentSpec, MetaArchitect

logger = logging.getLogger(__name__)


class EvolutionStrategy(Enum):
    """Strategies for architectural evolution."""

    STABILIZE = auto()  # Fix errors, reduce load
    OPTIMIZE = auto()  # Improve performance/efficiency
    EXPAND = auto()  # Add new capabilities
    EXPLORE = auto()  # Random variations (mutation)


@dataclass(frozen=True)
class EvolutionBatch:
    """Result of an evolution proposal."""

    strategy: EvolutionStrategy
    specs: List[ComponentSpec]


class ArchitectureEvolution:
    """Propose evolved component specifications based on existing ones.

    The evolution strategy analyzes system metrics (metrics_snapshot) to decide
    whether to Stabilize, Optimize, or Expand the architecture.
    """

    def __init__(self, meta_architect: MetaArchitect) -> None:
        """Create an ``ArchitectureEvolution`` instance.

        Args:
            meta_architect: Instance of ``MetaArchitect`` used to validate the
                generated specifications.
        """
        self._meta_architect = meta_architect
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.debug("ArchitectureEvolution initialized")

    def determine_strategy(self, metrics: Dict[str, Any]) -> EvolutionStrategy:
        """Determine the best evolution strategy based on metrics.

        Args:
            metrics: Dictionary containing system metrics.
                Expected keys: 'error_rate', 'cpu_usage', 'latency_ms'.

        Returns:
            Selected EvolutionStrategy.
        """
        error_rate = metrics.get("error_rate", 0.0)
        cpu_usage = metrics.get("cpu_usage", 0.0)
        latency = metrics.get("latency_ms", 0.0)

        if error_rate > 0.10:  # > 10% errors (antes era 5%)
            self._logger.info("High error rate (%.2f), strategy: STABILIZE", error_rate)
            return EvolutionStrategy.STABILIZE

        if cpu_usage > 90.0 or latency > 1000.0:  # Aumentado os limites
            self._logger.info("High load/latency, strategy: OPTIMIZE")
            return EvolutionStrategy.OPTIMIZE

        # If healthy, try to expand or explore - AJUSTE (2025-12-10): Mais agressivo
        self._logger.info("System healthy, strategy: EXPAND")
        return EvolutionStrategy.EXPAND

    def propose_evolution(
        self,
        existing_specs: Mapping[str, ComponentSpec],
        metrics: Optional[Dict[str, Any]] = None,
    ) -> EvolutionBatch:
        """Generate evolved specifications from existing ones.

        Args:
            existing_specs: Mapping from component name to its ``ComponentSpec``.
            metrics: Optional dictionary of system metrics to guide evolution.

        Returns:
            List of new ``ComponentSpec`` objects representing evolved
            components.
        """
        metrics = metrics or {}
        strategy = self.determine_strategy(metrics)
        return self.propose_evolution_with_strategy(existing_specs, metrics, strategy)

    def propose_evolution_with_strategy(
        self,
        existing_specs: Mapping[str, ComponentSpec],
        metrics: Optional[Dict[str, Any]],
        strategy: EvolutionStrategy,
    ) -> EvolutionBatch:
        """Phase 22: Generate evolved specifications with explicit strategy.

        Args:
            existing_specs: Mapping from component name to its ``ComponentSpec``.
            metrics: Optional dictionary of system metrics.
            strategy: Explicit evolution strategy to use.

        Returns:
            EvolutionBatch with specified strategy.
        """
        metrics = metrics or {}

        evolved: List[ComponentSpec] = []

        for name, spec in existing_specs.items():
            # Skip if component is already evolved (simple heuristic to prevent infinite names)
            if name.startswith("evolved_") and "generation" in spec.config:
                generation = int(spec.config.get("generation", 1))
                if generation > 3:  # Max 3 generations
                    self._logger.debug("Component %s reached max evolution generation", name)
                    continue

            new_config = dict(spec.config)
            new_config["parent"] = name
            new_config["strategy"] = strategy.name
            new_config["generation"] = str(int(spec.config.get("generation", 0)) + 1)
            new_config["evolved"] = "true"

            # Apply strategy-specific mutations - AJUSTE (2025-12-10): Nomeação mais inteligente
            if strategy == EvolutionStrategy.STABILIZE:
                # Evitar prefixos repetitivos
                if not name.startswith("stabilized_"):
                    new_config["robustness"] = "high"
                    new_config["monitoring"] = "verbose"
                    evolved_name = f"stabilized_{name}"
                else:
                    # Já estabilizado, tentar otimizar
                    new_config["caching"] = "enabled"
                    new_config["optimization_level"] = "O2"
                    evolved_name = name.replace("stabilized_", "optimized_")

            elif strategy == EvolutionStrategy.OPTIMIZE:
                if not name.startswith("optimized_"):
                    new_config["caching"] = "enabled"
                    new_config["optimization_level"] = "O2"
                    evolved_name = f"optimized_{name}"
                else:
                    # Já otimizado, tentar expandir
                    new_config["features"] = "extended"
                    new_config["capacity"] = "2x"
                    evolved_name = name.replace("optimized_", "expanded_")

            elif strategy == EvolutionStrategy.EXPAND:
                if not name.startswith("expanded_"):
                    new_config["features"] = "extended"
                    new_config["capacity"] = "2x"
                    evolved_name = f"expanded_{name}"
                else:
                    # Já expandido, voltar para estabilizar
                    new_config["robustness"] = "high"
                    new_config["monitoring"] = "verbose"
                    evolved_name = name.replace("expanded_", "stabilized_")

            else:  # Fallback/Legacy behavior
                evolved_name = f"evolved_{name}"

            # Ensure unique name if multiple evolutions happen (timestamp/random could be added)

            new_spec = ComponentSpec(name=evolved_name, type=spec.type, config=new_config)
            evolved.append(new_spec)

            self._logger.info(
                "Evolved spec created: %s from %s (Strategy: %s)",
                evolved_name,
                name,
                strategy.name,
            )

        # Validate before returning
        if not self._meta_architect.validate_specifications(evolved):
            self._logger.error("Validation of evolved specs failed")
            raise ValueError("Evolved specifications validation failed")

        return EvolutionBatch(strategy=strategy, specs=evolved)
