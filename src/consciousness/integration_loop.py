import asyncio
import json
import logging
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
from src.consciousness.shared_workspace import SharedWorkspace, ModuleState

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

"""
Integration Loop: Orchestrates closed-loop feedback between consciousness modules.

Phase 2 of Φ elevation refactoring plan. The IntegrationLoop creates the feedback cycle:
    sensory_input → qualia → narrative → meaning → expectation → sensory_feedback

This enables real causal coupling measured by SharedWorkspace cross-prediction metrics.
"""


logger = logging.getLogger(__name__)


@dataclass
class ModuleInterfaceSpec:
    """Specification for how a module integrates into the loop."""

    module_name: str
    embedding_dim: int
    required_inputs: List[str] = field(default_factory=list)
    produces_output: bool = True
    latency_ms: float = 10.0

    def __post_init__(self):
        if self.embedding_dim <= 0:
            raise ValueError(f"embedding_dim must be positive, got {self.embedding_dim}")
        if not isinstance(self.module_name, str):
            raise ValueError(f"module_name must be str, got {type(self.module_name)}")


@dataclass
class LoopCycleResult:
    """Result of one full integration loop cycle."""

    cycle_number: int
    cycle_duration_ms: float
    modules_executed: List[str]
    errors_occurred: List[Tuple[str, str]] = field(default_factory=list)
    cross_prediction_scores: Dict[str, Any] = field(default_factory=dict)
    phi_estimate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success(self) -> bool:
        """Cycle succeeded if no errors and Φ computed."""
        return len(self.errors_occurred) == 0 and self.phi_estimate > 0.0

    @property
    def execution_order(self) -> str:
        """Human-readable execution sequence."""
        return " → ".join(self.modules_executed)


class ModuleExecutor:
    """Executes a consciousness module with error handling and state management."""

    def __init__(self, module_name: str, spec: ModuleInterfaceSpec):
        self.module_name = module_name
        self.spec = spec
        self.call_count = 0
        self.error_count = 0
        self.total_execution_time_ms = 0.0

    async def execute(
        self, workspace: SharedWorkspace, input_module: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, np.ndarray]:
        """Execute module with inputs from workspace."""
        start_time = datetime.now()
        self.call_count += 1

        try:
            # Read inputs from workspace with proper dimension handling
            inputs = {}
            if input_module:
                state = workspace.read_module_state(input_module)
                if isinstance(state, ModuleState):
                    inputs[input_module] = state.embedding
                elif isinstance(state, np.ndarray):
                    inputs[input_module] = state
            else:
                for req_input in self.spec.required_inputs:
                    state = workspace.read_module_state(req_input)
                    if isinstance(state, ModuleState):
                        inputs[req_input] = state.embedding
                    elif isinstance(state, np.ndarray):
                        inputs[req_input] = state

            # Generate output
            output_embedding = self._compute_output(inputs, **kwargs)

            # Write output to workspace
            if self.spec.produces_output:
                workspace.write_module_state(
                    module_name=self.module_name,
                    embedding=output_embedding,
                    metadata={
                        "inputs": list(inputs.keys()),
                        "executor_call": self.call_count,
                    },
                )

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.total_execution_time_ms += elapsed_ms

            logger.debug(f"Module {self.module_name} executed in {elapsed_ms:.2f}ms")

            return {"output": output_embedding}

        except Exception as e:
            self.error_count += 1
            logger.error(f"Module {self.module_name} failed: {e}")
            raise

    def _compute_output(self, inputs: Dict[str, np.ndarray], **kwargs: Any) -> np.ndarray:
        """Compute module output from inputs."""
        # Special handling for expectation module
        if self.module_name == "expectation":
            from .expectation_module import predict_next_state

            if inputs:
                # Use first input as current state for prediction
                current_state = next(iter(inputs.values()))
                return predict_next_state(current_state)
            else:
                # No inputs - return zero embedding
                return np.zeros(self.spec.embedding_dim)

        # Check if required inputs are available and non-zero
        missing_required = []
        zero_required = []

        for req_input in self.spec.required_inputs:
            if req_input not in inputs:
                missing_required.append(req_input)
            elif np.allclose(inputs[req_input], 0.0):
                zero_required.append(req_input)

        # If required inputs are missing or zero, module cannot function properly
        if missing_required or zero_required:
            logger.warning(
                f"Module {self.module_name} missing/zero required inputs: "
                f"missing={missing_required}, zero={zero_required}. "
                f"Cannot compute meaningful output."
            )
            # Return zeros to indicate module failure
            return np.zeros(self.spec.embedding_dim)

        # Default behavior for other modules
        if inputs:
            # Blend inputs via averaging
            stacked = np.array(list(inputs.values()))
            base_output = np.mean(stacked, axis=0)
        else:
            # No inputs - initialize with random embedding
            base_output = np.random.randn(self.spec.embedding_dim) * 0.1

        # Ensure correct dimensionality
        if len(base_output) != self.spec.embedding_dim:
            if len(base_output) < self.spec.embedding_dim:
                pad_size = self.spec.embedding_dim - len(base_output)
                base_output = np.concatenate([base_output, np.random.randn(pad_size) * 0.01])
            else:
                base_output = base_output[: self.spec.embedding_dim]

        # Add stochastic component
        noise = np.random.randn(self.spec.embedding_dim) * 0.05
        output = base_output + noise

        # L2 normalize
        norm = np.linalg.norm(output)
        if norm > 0:
            output = output / norm

        return output

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "module_name": self.module_name,
            "call_count": self.call_count,
            "error_count": self.error_count,
            "avg_execution_time_ms": (
                self.total_execution_time_ms / self.call_count if self.call_count > 0 else 0.0
            ),
        }


class IntegrationLoop:
    """Orchestrates closed-loop feedback between consciousness modules."""

    STANDARD_SPECS = {
        "sensory_input": ModuleInterfaceSpec(
            module_name="sensory_input",
            embedding_dim=256,
            required_inputs=[],
            produces_output=True,
        ),
        "qualia": ModuleInterfaceSpec(
            module_name="qualia",
            embedding_dim=256,
            required_inputs=["sensory_input"],
            produces_output=True,
        ),
        "narrative": ModuleInterfaceSpec(
            module_name="narrative",
            embedding_dim=256,
            required_inputs=["qualia"],
            produces_output=True,
        ),
        "meaning_maker": ModuleInterfaceSpec(
            module_name="meaning_maker",
            embedding_dim=256,
            required_inputs=["narrative"],
            produces_output=True,
        ),
        "expectation": ModuleInterfaceSpec(
            module_name="expectation",
            embedding_dim=256,
            required_inputs=["meaning_maker"],
            produces_output=True,
        ),
    }

    def __init__(
        self,
        workspace: Optional[SharedWorkspace] = None,
        module_specs: Optional[Dict[str, ModuleInterfaceSpec]] = None,
        loop_sequence: Optional[List[str]] = None,
        enable_logging: bool = True,
    ):
        """Initialize integration loop."""
        self.module_specs = module_specs or self.STANDARD_SPECS
        self.loop_sequence = loop_sequence or list(self.STANDARD_SPECS.keys())

        # Use maximum dimension from all modules
        max_dim = max(spec.embedding_dim for spec in self.module_specs.values())
        self.workspace = workspace or SharedWorkspace(embedding_dim=max_dim)
        self.enable_logging = enable_logging

        # Initialize module executors
        self.executors = {
            name: ModuleExecutor(name, self.module_specs[name]) for name in self.loop_sequence
        }

        # Cycle tracking
        self.cycle_count = 0
        self.total_cycles_executed = 0
        self.cycle_history: List[LoopCycleResult] = []

    async def execute_cycle(self, collect_metrics: bool = True) -> LoopCycleResult:
        """Execute one complete integration loop cycle."""
        start_time = datetime.now()
        self.cycle_count += 1
        self.total_cycles_executed += 1

        result = LoopCycleResult(
            cycle_number=self.cycle_count,
            cycle_duration_ms=0.0,
            modules_executed=[],
            errors_occurred=[],
            cross_prediction_scores={},
            phi_estimate=0.0,
        )

        # Advance workspace cycle
        self.workspace.advance_cycle()

        # Execute modules in sequence
        for module_name in self.loop_sequence:
            try:
                executor = self.executors[module_name]
                await executor.execute(self.workspace)
                result.modules_executed.append(module_name)

                if self.enable_logging:
                    logger.debug(f"Cycle {self.cycle_count}: {module_name} completed")

            except Exception as e:
                result.errors_occurred.append((module_name, str(e)))
                logger.error(f"Cycle {self.cycle_count}: {module_name} failed - {e}")

        # Collect metrics if requested
        if collect_metrics and len(result.modules_executed) > 1:
            try:
                # Compute cross-predictions first
                for source_module in result.modules_executed:
                    for target_module in result.modules_executed:
                        if source_module != target_module:
                            try:
                                cross_pred = self.workspace.compute_cross_prediction(
                                    source_module=source_module,
                                    target_module=target_module,
                                )
                                if source_module not in result.cross_prediction_scores:
                                    result.cross_prediction_scores[source_module] = {}
                                result.cross_prediction_scores[source_module][
                                    target_module
                                ] = cross_pred.to_dict()
                            except Exception:
                                pass

                # Compute Φ from workspace state (which already has cross-predictions)
                result.phi_estimate = self.workspace.compute_phi_from_integrations()

                if self.enable_logging:
                    logger.info(f"Cycle {self.cycle_count}: Φ={result.phi_estimate:.4f}")

            except Exception as e:
                logger.error(f"Cycle {self.cycle_count}: Metrics failed - {e}")

        # Finalize timing
        result.cycle_duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.cycle_history.append(result)

        return result

    def _compute_all_cross_predictions(self) -> Dict[str, Dict[str, float]]:
        """Compute cross-prediction scores between all module pairs."""
        scores = {}
        modules_with_history = [
            m for m in self.loop_sequence if len(self.workspace.get_module_history(m)) > 1
        ]

        for source_module in modules_with_history:
            scores[source_module] = {}
            for target_module in modules_with_history:
                if source_module == target_module:
                    continue

                try:
                    cross_pred = self.workspace.compute_cross_prediction(
                        source_module=source_module,
                        target_module=target_module,
                    )
                    scores[source_module][target_module] = cross_pred.to_dict()

                except Exception as e:
                    logger.warning(f"Cross-prediction failed {source_module}->{target_module}: {e}")

        return scores

    async def run_cycles(
        self,
        num_cycles: int,
        collect_metrics_every: int = 1,
        progress_callback: Optional[Callable] = None,
    ) -> List[LoopCycleResult]:
        """Run multiple integration cycles."""
        results = []

        for i in range(num_cycles):
            collect_metrics = collect_metrics_every > 0 and (i + 1) % collect_metrics_every == 0

            result = await self.execute_cycle(collect_metrics=collect_metrics)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, num_cycles, result)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall integration loop statistics."""
        cycle_results = self.cycle_history
        successful_cycles = [c for c in cycle_results if c.success]

        phi_values = [c.phi_estimate for c in cycle_results if c.phi_estimate > 0.0]
        phi_mean = np.mean(phi_values) if phi_values else 0.0
        phi_max = np.max(phi_values) if phi_values else 0.0
        phi_min = np.min(phi_values) if phi_values else 0.0

        return {
            "total_cycles": self.total_cycles_executed,
            "successful_cycles": len(successful_cycles),
            "success_rate": (len(successful_cycles) / len(cycle_results) if cycle_results else 0.0),
            "avg_cycle_duration_ms": (
                np.mean([c.cycle_duration_ms for c in cycle_results]) if cycle_results else 0.0
            ),
            "phi_statistics": {
                "mean": phi_mean,
                "max": phi_max,
                "min": phi_min,
                "values_count": len(phi_values),
            },
            "module_statistics": {
                name: self.executors[name].get_statistics() for name in self.loop_sequence
            },
        }

    def get_phi_progression(self) -> List[float]:
        """Get Φ values over cycle history."""
        return [c.phi_estimate for c in self.cycle_history]

    def save_state(self, filepath: Path) -> None:
        """Save integration loop state and history."""
        state = {
            "cycle_count": self.cycle_count,
            "total_cycles_executed": self.total_cycles_executed,
            "statistics": self.get_statistics(),
            "phi_progression": self.get_phi_progression(),
            "recent_cycles": [
                {
                    "cycle": c.cycle_number,
                    "success": c.success,
                    "phi": c.phi_estimate,
                    "modules_executed": c.modules_executed,
                }
                for c in self.cycle_history[-100:]
            ],
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2, default=str)

        logger.info(f"Integration loop state saved to {filepath}")


async def main_example():
    """Example usage of IntegrationLoop."""
    loop = IntegrationLoop(enable_logging=True)

    print("🔄 Running 10 integration cycles...")

    def progress(i, total, result):
        phi = result.phi_estimate
        status = "✅" if result.success else "❌"
        print(f"  Cycle {i:2d}/{total}: Φ={phi:.4f} {status}")

    results = await loop.run_cycles(10, collect_metrics_every=1, progress_callback=progress)

    stats = loop.get_statistics()
    print("\n📊 Statistics:")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Φ mean: {stats['phi_statistics']['mean']:.4f}")
    print(f"  Φ max:  {stats['phi_statistics']['max']:.4f}")

    return loop, results


if __name__ == "__main__":
    asyncio.run(main_example())
