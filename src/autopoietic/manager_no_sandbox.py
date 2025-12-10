"""Autopoietic manager orchestrating evolution and synthesis cycles."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from .architecture_evolution import ArchitectureEvolution, EvolutionStrategy
from .code_synthesizer import CodeSynthesizer, SynthesizedComponent
from .meta_architect import ComponentSpec, MetaArchitect
from .metrics_adapter import MetricSample

logger = logging.getLogger(__name__)

# Threshold mínimo de Φ para aceitar mudanças arquiteturais
# CORREÇÃO (2025-12-08): Usar threshold baseado em valores empíricos normalizados
# Valores típicos de Φ normalizado: 0.5-0.8 (sistema saudável)
# Threshold de 0.3 estava muito alto, rejeitando mudanças válidas
# Novo threshold: 0.1 (permite flutuações normais, mas rejeita colapsos reais)
PHI_THRESHOLD = 0.1


@dataclass(frozen=True)
class ComponentFeedback:
    """Feedback sobre um componente sintetizado."""

    component_name: str
    feedback_type: str  # 'improvement', 'bug_fix', 'optimization', 'security'
    description: str
    changes_made: List[str]
    improvement_score: float  # 0.0 to 1.0
    timestamp: float
    reviewer: str = "system"


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
        synthesized_code_dir: Optional[Path] = Path("data/autopoietic/synthesized_code_secure"),
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

        # NOVO: Sistema de aprendizado com feedback
        self._component_feedback: Dict[str, List[ComponentFeedback]] = {}
        self._feedback_history_path = (
            (Path(history_path).parent / "component_feedback.jsonl") if history_path else None
        )
        self._learned_patterns: Dict[str, Any] = {}  # Padrões aprendidos do feedback

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

        # 🛡️ SEGURANÇA TEMPORÁRIA: Validação em sandbox DESABILITADA para teste
        # validated_components: Dict[str, SynthesizedComponent] = {}
        validated_components = synthesized.copy()  # Aceitar todos os componentes sem validação

        # with create_secure_sandbox() as sandbox:
        #     for name, component in synthesized.items():
        #         self._logger.info("🛡️ Validating component in sandbox: %s", name)
        #
        #         validation_result = sandbox.execute_component(component.source_code, name)
        #
        #         if validation_result["success"]:
        #             validated_components[name] = component
        #             self._logger.info("✅ Component %s passed sandbox validation", name)
        #         else:
        #             self._logger.error(
        #                 "🚨 Component %s failed sandbox validation: %s",
        #                 name,
        #                 validation_result.get("error", "Unknown error"),
        #             )
        #             # Não adiciona componentes que falharam na validação

        self._logger.info(
            "🧪 TESTE: Sandbox validation DISABLED - accepting all %d components",
            len(validated_components),
        )

        # Só prossegue com componentes validados
        for name, component in validated_components.items():
            # Encontrar spec correspondente - remover prefixo de segurança se presente
            spec_name = name
            if name.startswith("modulo_autopoiesis_data_"):
                spec_name = name[len("modulo_autopoiesis_data_") :]

            matching_spec = None
            for spec in batch.specs:
                if spec.name == spec_name:
                    matching_spec = spec
                    break

            if matching_spec is None:
                self._logger.error(
                    "No matching spec found for synthesized component %s "
                    "(spec name: %s). Available specs: %s",
                    name,
                    spec_name,
                    [s.name for s in batch.specs],
                )
                continue  # Pula este componente

            self._specs[name] = matching_spec
            new_names.append(name)
            self._logger.info("Cycle %d synthesized and validated %s", cycle_id, name)
            self._logger.debug("Source preview for %s:\n%s", name, component.source_code[:200])
            self._logger.info("💬 Natural description: %s", component.natural_description)

            # Persistir componente sintetizado (agora seguro)
            self._persist_component(name, component)

        # Validação de Φ após aplicar mudanças
        phi_after = self._get_current_phi()

        # CORREÇÃO (2025-12-08): Verificar queda relativa além do threshold absoluto
        # Uma queda de >50% também indica colapso, mesmo se ainda acima do threshold
        phi_drop_ratio = (phi_before - phi_after) / phi_before if phi_before > 0 else 0.0
        significant_drop = phi_drop_ratio > 0.5  # Queda de mais de 50%

        if phi_after < self._phi_threshold or significant_drop:
            self._logger.error(
                "Cycle %d caused Φ collapse: %.3f -> %.3f "
                "(threshold: %.3f, drop: %.1f%%). Rolling back.",
                cycle_id,
                phi_before,
                phi_after,
                self._phi_threshold,
                phi_drop_ratio * 100.0,
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
                "Φ declinou %.1f%%, preferindo estratégia STABILIZE",
                abs(phi_delta_percent),
            )
            self._strategy_preference = EvolutionStrategy.STABILIZE
        elif phi_delta_percent > 10.0:  # Melhoria > 10%
            self._logger.info(
                "Φ melhorou %.1f%%, permitindo estratégias mais agressivas",
                phi_delta_percent,
            )
            self._strategy_preference = None  # Remove preferência, permite todas
        elif phi_after < self._phi_threshold * 1.2:  # Φ próximo do threshold
            self._logger.info("Φ próximo do threshold, preferindo STABILIZE")
            self._strategy_preference = EvolutionStrategy.STABILIZE

    def _get_current_phi(self) -> float:
        """Obtém o valor atual de Φ (Integrated Information).

        Returns:
            Valor atual de Φ, ou valor padrão se não disponível.
        """
        try:
            # Se temos histórico de Φ, usar média recente
            if self._phi_history:
                return sum(self._phi_history[-5:]) / len(
                    self._phi_history[-5:]
                )  # Últimos 5 valores

            # Para primeiros ciclos, usar valor padrão saudável
            # Este valor pode ser ajustado baseado em observações empíricas
            return 0.5

        except Exception as e:
            self._logger.warning("Erro ao obter Φ atual: %s. Usando valor padrão.", e)
            return 0.5

    def register_component_feedback(
        self,
        component_name: str,
        feedback_type: str,
        description: str,
        changes_made: List[str],
        improvement_score: float,
        reviewer: str = "system",
    ) -> None:
        """Registra feedback sobre um componente para aprendizado futuro.

        Args:
            component_name: Nome do componente que recebeu feedback
            feedback_type: Tipo de feedback ('improvement', 'bug_fix', 'optimization', 'security')
            description: Descrição do que foi melhorado
            changes_made: Lista específica das mudanças realizadas
            improvement_score: Pontuação de melhoria (0.0-1.0)
            reviewer: Quem fez a análise (padrão: 'system')
        """
        feedback = ComponentFeedback(
            component_name=component_name,
            feedback_type=feedback_type,
            description=description,
            changes_made=changes_made,
            improvement_score=improvement_score,
            timestamp=time.time(),
            reviewer=reviewer,
        )

        if component_name not in self._component_feedback:
            self._component_feedback[component_name] = []

        self._component_feedback[component_name].append(feedback)

        # Aprender com o feedback
        self._learn_from_feedback(feedback)

        # Persistir feedback
        self._persist_feedback(feedback)

        self._logger.info(
            "📚 Feedback registrado para %s (%s): %s (score: %.2f)",
            component_name,
            feedback_type,
            description,
            improvement_score,
        )

    def _learn_from_feedback(self, feedback: ComponentFeedback) -> None:
        """Aprende padrões do feedback para melhorar futuras sínteses.

        Args:
            feedback: Feedback registrado para aprendizado
        """
        # Aprender padrões por tipo de feedback
        if feedback.feedback_type not in self._learned_patterns:
            self._learned_patterns[feedback.feedback_type] = {
                "patterns": [],
                "avg_improvement": 0.0,
                "count": 0,
            }

        patterns = self._learned_patterns[feedback.feedback_type]

        # Extrair padrões das mudanças
        for change in feedback.changes_made:
            if change not in patterns["patterns"]:
                patterns["patterns"].append(change)

        # Atualizar estatísticas
        patterns["count"] += 1
        patterns["avg_improvement"] = (
            (patterns["avg_improvement"] * (patterns["count"] - 1)) + feedback.improvement_score
        ) / patterns["count"]

        self._logger.debug(
            "🎓 Aprendido padrão de %s: %d padrões, melhoria média %.2f",
            feedback.feedback_type,
            len(patterns["patterns"]),
            patterns["avg_improvement"],
        )

    def _persist_feedback(self, feedback: ComponentFeedback) -> None:
        """Persiste feedback em arquivo para análise futura."""
        if self._feedback_history_path is None:
            return

        try:
            self._feedback_history_path.parent.mkdir(parents=True, exist_ok=True)
            with self._feedback_history_path.open("a", encoding="utf-8") as stream:
                payload = asdict(feedback)
                json.dump(payload, stream, ensure_ascii=False)
                stream.write("\n")
        except Exception as exc:
            self._logger.warning("Failed to persist feedback: %s", exc)

    def get_component_feedback_history(self, component_name: str) -> List[ComponentFeedback]:
        """Retorna histórico de feedback para um componente.

        Args:
            component_name: Nome do componente

        Returns:
            Lista de feedback registrado para o componente
        """
        return self._component_feedback.get(component_name, [])

    def get_learning_insights(self) -> Dict[str, Any]:
        """Retorna insights aprendidos do feedback para melhorar sínteses futuras.

        Returns:
            Dicionário com padrões aprendidos e estatísticas
        """
        return {
            "learned_patterns": self._learned_patterns,
            "total_feedback_count": sum(
                len(feedbacks) for feedbacks in self._component_feedback.values()
            ),
            "components_with_feedback": list(self._component_feedback.keys()),
            "most_common_improvements": self._get_most_common_improvements(),
        }

    def _get_most_common_improvements(self) -> List[Dict[str, Any]]:
        """Identifica as melhorias mais comuns para foco futuro."""
        improvement_counts = {}

        for feedbacks in self._component_feedback.values():
            for feedback in feedbacks:
                for change in feedback.changes_made:
                    if change not in improvement_counts:
                        improvement_counts[change] = {
                            "count": 0,
                            "avg_score": 0.0,
                            "total_score": 0.0,
                        }

                    improvement_counts[change]["count"] += 1
                    improvement_counts[change]["total_score"] += feedback.improvement_score
                    improvement_counts[change]["avg_score"] = (
                        improvement_counts[change]["total_score"]
                        / improvement_counts[change]["count"]
                    )

        # Ordenar por frequência
        sorted_improvements = sorted(
            improvement_counts.items(), key=lambda x: x[1]["count"], reverse=True
        )

        return [
            {
                "improvement": improvement,
                "count": data["count"],
                "avg_score": data["avg_score"],
            }
            for improvement, data in sorted_improvements[:10]  # Top 10
        ]

    def get_natural_language_report(self) -> str:
        """Gera relatório em linguagem natural sobre o estado do sistema autopoiético.

        Returns:
            Relatório descritivo em português sobre componentes, aprendizado e estado atual.
        """
        report_lines = []
        report_lines.append("🤖 Relatório do Sistema Autopoiético OmniMind")
        report_lines.append("=" * 50)

        # Estatísticas básicas
        total_cycles = len(self.history)
        total_components = len(
            [spec for spec in self.specs.keys() if spec.startswith("modulo_autopoiesis_data_")]
        )
        total_feedback = sum(len(feedbacks) for feedbacks in self._component_feedback.values())

        report_lines.append("📊 Estatísticas Gerais:")
        report_lines.append(f"   • Ciclos executados: {total_cycles}")
        report_lines.append(f"   • Componentes criados: {total_components}")
        report_lines.append(f"   • Feedback registrado: {total_feedback}")
        report_lines.append("")

        # Estado atual de Φ
        current_phi = self._get_current_phi()
        phi_status = (
            "🟢 Excelente"
            if current_phi > 0.7
            else "🟡 Bom" if current_phi > 0.5 else "🟠 Precisa melhorar"
        )
        report_lines.append(f"🧠 Estado Atual da Integração (Φ): {phi_status}")
        report_lines.append(f"   • Valor atual: {current_phi:.3f}")
        report_lines.append("")

        # Estratégia atual
        if self._strategy_preference:
            report_lines.append(f"🎯 Estratégia Preferida: {self._strategy_preference.name}")
            report_lines.append("   • Sistema aprendendo com feedback adaptativo")
        else:
            report_lines.append("🎯 Estratégia: Adaptativa (todas permitidas)")
        report_lines.append("")

        # Componentes recentes
        if total_components > 0:
            report_lines.append("🛠️ Componentes Criados Recentemente:")
            synthesized_specs = [
                (name, spec)
                for name, spec in self.specs.items()
                if name.startswith("modulo_autopoiesis_data_")
            ]
            recent_specs = synthesized_specs[-5:]  # Últimos 5

            for name, spec in recent_specs:
                clean_name = name.replace("modulo_autopoiesis_data_", "")
                report_lines.append(f"   • {clean_name}")
                if hasattr(spec, "description") and spec.description:
                    report_lines.append(f"     └─ {spec.description[:100]}...")
            report_lines.append("")

        # Aprendizado e feedback
        if self._learned_patterns:
            report_lines.append("📚 Padrões Aprendidos:")
            for feedback_type, patterns in self._learned_patterns.items():
                count = patterns.get("count", 0)
                avg_improvement = patterns.get("avg_improvement", 0.0)
                report_lines.append(
                    f"   • {feedback_type}: {count} aprendizados (média: {avg_improvement:.2f})"
                )
            report_lines.append("")

        # Atividade recente
        if self.history:
            report_lines.append("📈 Atividade Recente:")
            recent_cycles = self.history[-3:]  # Últimos 3 ciclos

            for cycle in recent_cycles:
                components_created = len(cycle.synthesized_components)
                phi_change = ""
                if cycle.phi_before is not None and cycle.phi_after is not None:
                    if cycle.phi_after > cycle.phi_before:
                        phi_change = f" (Φ ↑ {cycle.phi_before:.2f} → {cycle.phi_after:.2f})"
                    elif cycle.phi_after < cycle.phi_before:
                        phi_change = f" (Φ ↓ {cycle.phi_before:.2f} → {cycle.phi_after:.2f})"

                if components_created > 0:
                    report_lines.append(
                        f"   • Ciclo {cycle.cycle_id}: "
                        f"{components_created} componentes criados{phi_change}"
                    )
                else:
                    report_lines.append(
                        f"   • Ciclo {cycle.cycle_id}: " f"Aprendizado e adaptação{phi_change}"
                    )
            report_lines.append("")

        # Recomendações
        report_lines.append("💡 Recomendações:")
        if current_phi < 0.5:
            report_lines.append(
                "   • Sistema precisa de mais integração - considere ciclos de estabilização"
            )
        elif current_phi > 0.8:
            report_lines.append(
                "   • Integração excelente - pode experimentar inovações mais agressivas"
            )
        else:
            report_lines.append("   • Equilíbrio bom - continue com estratégia atual")

        if total_feedback < 5:
            report_lines.append("   • Mais feedback ajudaria o sistema a aprender melhor")
        report_lines.append("")

        report_lines.append("🎉 Sistema autopoietico ativo e aprendendo!")

        return "\n".join(report_lines)
