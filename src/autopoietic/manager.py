"""Autopoietic manager orchestrating evolution and synthesis cycles."""

from __future__ import annotations

import logging
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Mapping, Optional, Union

from .architecture_evolution import ArchitectureEvolution, EvolutionStrategy
from .code_synthesizer import CodeSynthesizer, SynthesizedComponent
from .meta_architect import ComponentSpec, MetaArchitect
from .metrics_adapter import MetricSample

logger = logging.getLogger(__name__)

# Threshold mínimo de Φ para aceitar mudanças arquiteturais
PHI_THRESHOLD = 0.3


@dataclass(frozen=True)
class CycleLog:
    """Record describing an autopoietic cycle execution."""

    cycle_id: int
    metrics: Dict[str, Any]
    strategy: EvolutionStrategy
    synthesized_components: List[str]
    timestamp: float
    phi_before: Optional[float] = None
    phi_after: Optional[float] = None


class AutopoieticManager:
    """High-level orchestrator for the autopoietic pipeline."""

    def __init__(
        self,
        meta_architect: Optional[MetaArchitect] = None,
        evolution_engine: Optional[ArchitectureEvolution] = None,
        synthesizer: Optional[CodeSynthesizer] = None,
        initial_specs: Optional[Mapping[str, ComponentSpec]] = None,
        history_path: Optional[Path] = Path("data/autopoietic/cycle_history.jsonl"),
        synthesized_code_dir: Optional[Path] = Path("data/autopoietic/synthesized_code"),
        phi_threshold: float = PHI_THRESHOLD,
        kernel_autopoiesis: Optional[Any] = None,  # KernelAutopoiesisMinimal opcional
    ) -> None:
        self._meta_architect = meta_architect or MetaArchitect()
        self._evolution_engine = evolution_engine or ArchitectureEvolution(self._meta_architect)
        self._synthesizer = synthesizer or CodeSynthesizer()
        self._specs: Dict[str, ComponentSpec] = dict(initial_specs or {})
        self._cycle_count = 0
        self._history: List[CycleLog] = []
        self._history_path = Path(history_path) if history_path else None
        self._synthesized_code_dir = Path(synthesized_code_dir) if synthesized_code_dir else None
        self._phi_threshold = phi_threshold
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.debug("AutopoieticManager initialized with %d specs", len(self._specs))

        # Phase 22: Sistema de feedback adaptativo
        self._phi_history: List[float] = []
        self._strategy_preference: Optional[EvolutionStrategy] = None

        # NOVO: Kernel autopoiesis para verificar O-CLOSURE
        self.kernel_autopoiesis = kernel_autopoiesis
        if self.kernel_autopoiesis is not None:
            self._logger.info("KernelAutopoiesisMinimal integrado para verificação de O-CLOSURE")

    @property
    def specs(self) -> Dict[str, ComponentSpec]:
        """Return current component specifications."""
        return dict(self._specs)

    @property
    def history(self) -> List[CycleLog]:
        """Return executed cycle logs."""
        return list(self._history)

    def register_spec(self, spec: ComponentSpec) -> None:
        """Register an initial component specification."""
        self._specs[spec.name] = spec
        self._logger.debug("Registered base spec %s", spec.name)

    def run_cycle(self, metrics: Union[Dict[str, Any], MetricSample]) -> CycleLog:
        """Execute a full autopoietic cycle."""
        self._cycle_count += 1
        cycle_id = self._cycle_count
        self._logger.info("Starting autopoietic cycle %d", cycle_id)

        if isinstance(metrics, MetricSample):
            metrics = metrics.strategy_inputs()

        # Phase 22: Aplicar preferência de estratégia se houver feedback adaptativo
        if self._strategy_preference:
            # Forçar estratégia preferida se feedback adaptativo indicar
            original_strategy = self._evolution_engine.determine_strategy(metrics)
            if original_strategy != self._strategy_preference:
                self._logger.info(
                    "Aplicando estratégia preferida %s (feedback adaptativo) em vez de %s",
                    self._strategy_preference.name,
                    original_strategy.name,
                )
                # Criar batch com estratégia preferida
                batch = self._evolution_engine.propose_evolution_with_strategy(
                    self._specs, metrics, self._strategy_preference
                )
            else:
                batch = self._evolution_engine.propose_evolution(self._specs, metrics)
        else:
            batch = self._evolution_engine.propose_evolution(self._specs, metrics)
        timestamp = time.time()

        # NOVO: Verificar O-CLOSURE antes de aplicar mudanças
        if self.kernel_autopoiesis is not None:
            try:
                closure_result = self.kernel_autopoiesis.organizational_closure()
                if not closure_result.get("is_closed", False):
                    self._logger.warning(
                        "O-CLOSURE quebrado: %s. Continuando ciclo mas alertando.",
                        closure_result.get("reason", "unknown"),
                    )
            except Exception as e:
                self._logger.warning("Erro ao verificar O-CLOSURE: %s", e)

        # Validação de Φ antes de aplicar mudanças
        phi_before = self._get_current_phi()

        if not batch.specs:
            log = CycleLog(
                cycle_id=cycle_id,
                metrics=dict(metrics),
                strategy=batch.strategy,
                synthesized_components=[],
                timestamp=timestamp,
                phi_before=phi_before,
                phi_after=phi_before,
            )
            self._history.append(log)
            self._persist_log(log)
            self._logger.info("Cycle %d produced no new components", cycle_id)
            return log

        if phi_before < self._phi_threshold:
            self._logger.warning(
                "Cycle %d rejected: Φ=%.3f below threshold %.3f",
                cycle_id,
                phi_before,
                self._phi_threshold,
            )
            log = CycleLog(
                cycle_id=cycle_id,
                metrics=dict(metrics),
                strategy=batch.strategy,
                synthesized_components=[],
                timestamp=timestamp,
                phi_before=phi_before,
                phi_after=phi_before,
            )
            self._history.append(log)
            self._persist_log(log)
            return log

        synthesized = self._synthesizer.synthesize(batch.specs)
        new_names: List[str] = []

        for name, component in synthesized.items():
            matching_spec = next(spec for spec in batch.specs if spec.name == name)
            self._specs[name] = matching_spec
            new_names.append(name)
            self._logger.info("Cycle %d synthesized %s", cycle_id, name)
            self._logger.debug("Source preview for %s:\n%s", name, component.source_code[:200])

            # Persistir componente sintetizado
            self._persist_component(name, component)

        # Validação de Φ após aplicar mudanças
        phi_after = self._get_current_phi()
        if phi_after < self._phi_threshold:
            self._logger.error(
                "Cycle %d caused Φ collapse: %.3f -> %.3f (threshold: %.3f). Rolling back.",
                cycle_id,
                phi_before,
                phi_after,
                self._phi_threshold,
            )
            # Rollback: remover componentes sintetizados
            for name in new_names:
                self._specs.pop(name, None)
                self._remove_persisted_component(name)
            new_names = []

        # Phase 22: Feedback adaptativo baseado em mudança de Φ
        self._adaptive_phi_feedback(phi_before, phi_after, batch.strategy)

        log = CycleLog(
            cycle_id=cycle_id,
            metrics=dict(metrics),
            strategy=batch.strategy,
            synthesized_components=new_names,
            timestamp=timestamp,
            phi_before=phi_before,
            phi_after=phi_after,
        )
        self._history.append(log)
        self._persist_log(log)

        # Gerar relatório após cada ciclo autopoiético
        try:
            from src.observability.module_reporter import get_module_reporter

            reporter = get_module_reporter()
            reporter.generate_module_report(
                module_name=f"autopoietic_cycle_{cycle_id}",
                include_metrics=True,
                format="json",
            )
            self._logger.debug(f"Relatório gerado para ciclo autopoiético {cycle_id}")
        except Exception as e:
            self._logger.debug(f"Erro ao gerar relatório autopoiético: {e}")

        self._logger.info(
            "Cycle %d completed: Φ %.3f -> %.3f, synthesized %d components",
            cycle_id,
            phi_before,
            phi_after,
            len(new_names),
        )

        return log

    def _persist_log(self, log: CycleLog) -> None:
        if not self._history_path:
            return

        try:
            self._history_path.parent.mkdir(parents=True, exist_ok=True)
            with self._history_path.open("a", encoding="utf-8") as stream:
                payload = asdict(log)
                payload["strategy"] = log.strategy.name
                json.dump(payload, stream, ensure_ascii=False)
                stream.write("\n")
        except Exception as exc:
            self._logger.warning("Failed to persist autopoietic log: %s", exc)

    def _persist_component(self, name: str, component: SynthesizedComponent) -> None:
        """Persiste um componente sintetizado em arquivo Python.

        Args:
            name: Nome do componente.
            component: Componente sintetizado a ser persistido.
        """
        if not self._synthesized_code_dir:
            return

        try:
            self._synthesized_code_dir.mkdir(parents=True, exist_ok=True)
            file_path = self._synthesized_code_dir / f"{name}.py"

            with file_path.open("w", encoding="utf-8") as stream:
                stream.write(f'"""Componente autopoiético sintetizado: {name}\n')
                stream.write(f"Gerado em: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                stream.write('"""\n\n')
                stream.write(component.source_code)

            self._logger.debug("Persisted synthesized component to %s", file_path)
        except Exception as exc:
            self._logger.warning("Failed to persist component %s: %s", name, exc)

    def _remove_persisted_component(self, name: str) -> None:
        """Remove um componente persistido (rollback).

        Args:
            name: Nome do componente a ser removido.
        """
        if not self._synthesized_code_dir:
            return

        try:
            file_path = self._synthesized_code_dir / f"{name}.py"
            if file_path.exists():
                file_path.unlink()
                self._logger.debug("Removed persisted component %s", file_path)
        except Exception as exc:
            self._logger.warning("Failed to remove persisted component %s: %s", name, exc)

    def _adaptive_phi_feedback(
        self, phi_before: float, phi_after: float, strategy: EvolutionStrategy
    ) -> None:
        """Phase 22: Ajusta estratégia baseado em feedback de Φ.

        Se Φ declina significativamente, reduz agressividade.
        Se Φ melhora, pode ser mais agressivo.

        Args:
            phi_before: Valor de Φ antes da mudança.
            phi_after: Valor de Φ depois da mudança.
            strategy: Estratégia usada no ciclo.
        """
        if phi_before == 0.0:  # Primeiros ciclos
            return

        phi_delta = phi_after - phi_before
        phi_delta_percent = (phi_delta / phi_before) * 100 if phi_before > 0 else 0

        # Armazenar histórico
        self._phi_history.append(phi_after)
        if len(self._phi_history) > 10:
            self._phi_history = self._phi_history[-10:]

        # Feedback adaptativo
        if phi_delta_percent < -10.0:  # Declínio > 10%
            self._logger.warning(
                "Φ declinou %.1f%%, preferindo estratégia STABILIZE", abs(phi_delta_percent)
            )
            self._strategy_preference = EvolutionStrategy.STABILIZE
        elif phi_delta_percent > 10.0:  # Melhoria > 10%
            self._logger.info(
                "Φ melhorou %.1f%%, permitindo estratégias mais agressivas", phi_delta_percent
            )
            self._strategy_preference = None  # Remove preferência, permite todas
        elif phi_after < self._phi_threshold * 1.2:  # Φ próximo do threshold
            self._logger.info("Φ próximo do threshold, preferindo STABILIZE")
            self._strategy_preference = EvolutionStrategy.STABILIZE

    def _get_current_phi(self) -> float:
        """Obtém o valor atual de Φ do sistema.

        Tenta ler de data/monitor/real_metrics.json, com fallback para 0.5.

        Returns:
            Valor de Φ (0.0-1.0).
        """
        try:
            metrics_path = Path("data/monitor/real_metrics.json")
            if metrics_path.exists():
                with metrics_path.open("r", encoding="utf-8") as stream:
                    metrics = json.load(stream)
                    phi = float(metrics.get("phi", 0.5))
                    self._logger.debug("Read Φ=%.3f from real_metrics.json", phi)
                    return phi
        except Exception as exc:
            self._logger.debug("Could not read Φ from real_metrics.json: %s", exc)

        # Fallback: assume sistema saudável
        return 0.5
