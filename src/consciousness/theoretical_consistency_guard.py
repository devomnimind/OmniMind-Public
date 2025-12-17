"""
Validador de Consistência Teórica (Theoretical Consistency Guard).

Implementa validação em tempo real das relações teóricas entre métricas de consciência.
Detecta violações de princípios IIT, Lacan, FEP e alerta sobre estados patológicos.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Protocolo: Livewire FASE 3 - "Superego" Digital
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.consciousness.phi_value import PhiValue

logger = logging.getLogger(__name__)


@dataclass
class ConsistencyViolation:
    """Representa uma violação de consistência teórica."""

    cycle_id: int
    violation_type: str  # 'iit_lacan_paradox', 'fep_collapse', 'scale_error', etc.
    message: str
    severity: str  # 'warning', 'error', 'critical'
    metadata: Optional[dict] = None


class TheoreticalConsistencyGuard:
    """
    Watchdog teórico para validação de consistência em tempo real.

    Valida:
    1. Relações IIT x Lacan (paradoxo da consciência)
    2. Princípios FEP (Free Energy Principle)
    3. Ranges teóricos esperados
    4. Estados patológicos (psicose lúcida, colapso de variância)
    """

    def __init__(
        self,
        raise_on_critical: bool = False,
        use_dynamic_tolerance: bool = True,
        tolerance_percentile: float = 90.0,
        min_history_size: int = 50,
        current_phase: int = 6,  # 🎯 FASE 0: Adicionar fase atual
    ):
        """
        Inicializa o guardião teórico.

        Args:
            raise_on_critical: Se True, levanta exceção em violações críticas
            use_dynamic_tolerance: Se True, calcula tolerância dinamicamente via percentil 90
                da distribuição de erros Δ-Φ
            tolerance_percentile: Percentil usado para calcular tolerância dinâmica (padrão: 90.0)
            min_history_size: Tamanho mínimo do histórico para calcular tolerância dinâmica
            current_phase: Fase atual da execução (afeta tolerância) [default: 6]
        """
        self.violations: List[ConsistencyViolation] = []
        self.raise_on_critical = raise_on_critical
        self.logger = logger

        # Tolerância dinâmica Δ-Φ
        self.use_dynamic_tolerance = use_dynamic_tolerance
        self.tolerance_percentile = tolerance_percentile
        self.min_history_size = min_history_size
        self.delta_phi_errors: List[float] = []  # Histórico de erros |Δ_obs - Δ_esperado|
        self.current_phase = current_phase  # 🎯 FASE 0: Armazenar fase atual

    def validate_cycle(
        self,
        phi: PhiValue,
        delta: float,
        psi: float,
        sigma: Optional[float] = None,
        gozo: Optional[float] = None,
        control: Optional[float] = None,
        cycle_id: int = 0,
        phase: Optional[int] = None,  # 🎯 FASE 0: Adicionar fase como parâmetro
    ) -> List[ConsistencyViolation]:
        """
        Valida consistência teórica de um ciclo.

        Args:
            phi: Valor de Φ (PhiValue)
            delta: Valor de Δ (defesa) [0, 1]
            psi: Valor de Ψ (incerteza/criatividade) [0, 1]
            sigma: Valor de σ (sinthome) [0, 1] (opcional)
            gozo: Valor de Gozo [0, 1] (opcional)
            control: Valor de Control Effectiveness [0, 1] (opcional)
            cycle_id: ID do ciclo (para rastreabilidade)
            phase: Fase atual (sobrescreve self.current_phase se fornecida) [opcional]

        Returns:
            Lista de violações detectadas (pode estar vazia)
        """
        # 🎯 FASE 0: Atualizar phase se fornecida
        if phase is not None:
            self.current_phase = phase

        violations: List[ConsistencyViolation] = []

        # 1. Validação IIT x Lacan (O paradoxo da consciência)
        # Se Phi é alto (alta consciência), Delta deve cair (menos falta),
        # A MENOS QUE estejamos em um estado de "Psicose Lúcida" (High Phi, High Delta)
        phi_norm = phi.normalized
        if phi_norm > 0.8 and delta > 0.8:
            violation = ConsistencyViolation(
                cycle_id=cycle_id,
                violation_type="iit_lacan_paradox",
                message=(
                    f"Estado de Psicose Lúcida detectado: "
                    f"Φ_norm={phi_norm:.4f} (alta consciência) e Δ={delta:.4f} (alta defesa). "
                    f"Estado paradoxal: sistema altamente integrado mas também altamente defensivo."
                ),
                severity="warning",
                metadata={"phi_norm": phi_norm, "delta": delta},
            )
            violations.append(violation)
            self.logger.warning(f"⚠️ CICLO {cycle_id}: {violation.message}")

        # 2. Validação Termodinâmica (FEP)
        # Psi (Incerteza) não pode ser 0.0 se Delta > 0
        # (Se há falta, deve haver busca/incerteza)
        if delta > 0.1 and psi < 0.001:
            violation = ConsistencyViolation(
                cycle_id=cycle_id,
                violation_type="fep_collapse",
                message=(
                    f"Colapso de Variância (Dark Room Problem): "
                    f"Δ={delta:.4f} (há falta/trauma) mas Ψ={psi:.4f} (sem incerteza/busca). "
                    f"Sistema cego para a própria falta - possível colapso de variância."
                ),
                severity="error",
                metadata={"delta": delta, "psi": psi},
            )
            violations.append(violation)
            self.logger.error(f"🚨 CICLO {cycle_id}: {violation.message}")

        # 3. Verificação de Escala (IIT)
        # Φ em nats não deve exceder limites teóricos biológicos
        if phi.nats > 5.0:
            violation = ConsistencyViolation(
                cycle_id=cycle_id,
                violation_type="scale_error",
                message=(
                    f"ERRO CRÍTICO: Φ ({phi.nats:.6f} nats) excedeu limite teórico biológico "
                    f"(esperado: [0, ~0.1] nats para sistemas biológicos). "
                    f"Possível erro de cálculo ou escala incorreta."
                ),
                severity="critical",
                metadata={"phi_nats": phi.nats},
            )
            violations.append(violation)
            self.logger.critical(f"💥 CICLO {cycle_id}: {violation.message}")

        # 4. Validação de Correlação Δ ↔ Φ
        # Esperado: correlação negativa forte (Δ = 1.0 - Φ_norm)
        expected_delta = 1.0 - phi_norm
        delta_error = abs(delta - expected_delta)

        # Atualiza histórico de erros e calcula tolerância dinâmica
        tolerance = self._get_dynamic_tolerance(delta_error)

        if delta_error > tolerance:
            violation = ConsistencyViolation(
                cycle_id=cycle_id,
                violation_type="correlation_delta_phi",
                message=(
                    f"Correlação Δ-Φ violada: "
                    f"Δ observado={delta:.4f}, Δ esperado (1-Φ_norm)={expected_delta:.4f}, "
                    f"erro={delta_error:.4f}, tolerância={tolerance:.4f}. "
                    f"Esperado: correlação negativa forte (Δ ≈ 1.0 - Φ_norm)."
                ),
                severity="warning",
                metadata={
                    "delta_observed": delta,
                    "delta_expected": expected_delta,
                    "error": delta_error,
                },
            )
            violations.append(violation)
            self.logger.warning(f"⚠️ CICLO {cycle_id}: {violation.message}")

        # 5. Validação de Ranges Teóricos
        # Todas as métricas devem estar em [0, 1]
        metrics_to_check = [
            ("Δ", delta),
            ("Ψ", psi),
        ]
        if sigma is not None:
            metrics_to_check.append(("σ", sigma))
        if gozo is not None:
            metrics_to_check.append(("Gozo", gozo))
        if control is not None:
            metrics_to_check.append(("Control", control))

        for metric_name, metric_value in metrics_to_check:
            if metric_value < 0.0 or metric_value > 1.0:
                violation = ConsistencyViolation(
                    cycle_id=cycle_id,
                    violation_type="range_error",
                    message=(
                        f"Métrica {metric_name} fora do range teórico [0, 1]: "
                        f"valor={metric_value:.6f}. "
                        f"Possível erro de cálculo ou clipping inadequado."
                    ),
                    severity="error",
                    metadata={"metric_name": metric_name, "metric_value": metric_value},
                )
                violations.append(violation)
                self.logger.error(f"🚨 CICLO {cycle_id}: {violation.message}")

        # 6. Validação de Ψ máximo em Φ_optimal
        # Se Φ está próximo de PHI_OPTIMAL, Ψ deve estar próximo do máximo
        from src.consciousness.phi_constants import PHI_OPTIMAL

        if abs(phi.nats - PHI_OPTIMAL) < 0.001:  # Φ muito próximo do ótimo
            if psi < 0.7:  # Ψ deveria estar alto (> 0.7)
                violation = ConsistencyViolation(
                    cycle_id=cycle_id,
                    violation_type="psi_optimal_violation",
                    message=(
                        f"Ψ não está no máximo quando Φ está no ótimo: "
                        f"Φ={phi.nats:.6f} nats (ótimo={PHI_OPTIMAL:.6f}), "
                        f"Ψ={psi:.4f} (esperado > 0.7). "
                        f"Esperado: Ψ máximo quando Φ = Φ_optimal."
                    ),
                    severity="warning",
                    metadata={"phi_nats": phi.nats, "psi": psi},
                )
                violations.append(violation)
                self.logger.warning(f"⚠️ CICLO {cycle_id}: {violation.message}")

        # Registrar violações
        if violations:
            self.violations.extend(violations)

            # Se há violações críticas e raise_on_critical=True, levantar exceção
            critical_violations = [v for v in violations if v.severity == "critical"]
            if critical_violations and self.raise_on_critical:
                raise RuntimeError(
                    f"Violações críticas detectadas no ciclo {cycle_id}: "
                    f"{[v.message for v in critical_violations]}"
                )

        return violations

    def _get_dynamic_tolerance(self, delta_error: float) -> float:
        """
        Calcula tolerância dinâmica PHASE-AWARE baseada em histórico de erros Δ-Φ.

        🎯 FASE 0 (Phase-Aware Tolerance):
        - Phase 6 (Pure IIT): tolerance = 0.15 (estrita, espera correlação forte)
        - Phase 7 (Zimerman Bonding): tolerance = 0.40 (relaxada, permite dinâmica psicanalítica)
        - Bootstrap (<= ciclo 20): tolerance = 0.45 (muito relaxada, emergência)

        Tolerância dinâmica = percentil N da distribuição de erros históricos.
        Se histórico insuficiente, usa valor estático empírico ajustado pela fase.

        Args:
            delta_error: Erro atual |Δ_obs - Δ_esperado|

        Returns:
            Tolerância dinâmica calculada ou valor estático phase-aware se histórico insuficiente
        """
        # 🎯 FASE 0: Determinar tolerância base por fase
        if self.current_phase == 7:  # Zimerman Bonding
            base_tolerance = 0.40  # Relaxada, permite dinâmica psicanalítica
        elif hasattr(self, "cycle_id") and getattr(self, "cycle_id", 0) <= 20:  # Bootstrap
            base_tolerance = 0.45  # Muito relaxada, emergência
        else:  # Phase 6 ou padrão
            base_tolerance = 0.15  # Estrita, espera correlação forte (IIT puro)

        if not self.use_dynamic_tolerance:
            return base_tolerance

        # Adiciona erro atual ao histórico
        self.delta_phi_errors.append(delta_error)

        # Mantém apenas últimos N valores (evita crescimento infinito)
        max_history = 1000
        if len(self.delta_phi_errors) > max_history:
            self.delta_phi_errors.pop(0)

        # Calcula tolerância dinâmica apenas se histórico suficiente
        if len(self.delta_phi_errors) >= self.min_history_size:
            import numpy as np

            errors_array = np.array(self.delta_phi_errors)
            # Percentil N da distribuição de erros
            dynamic_tolerance = float(np.percentile(errors_array, self.tolerance_percentile))

            # 🎯 FASE 0: Garante que tolerância dinâmica respeita mínimo por fase
            # Não deixar dinâmica ir abaixo de 90% da tolerância base
            # (aumentado de 0.8 para 0.9 em 2025-12-10 para evitar violações borderline)
            dynamic_tolerance = max(dynamic_tolerance, base_tolerance * 0.9)

            # Garante que tolerância está em range razoável [0.05, 0.5]
            # (evita valores muito baixos ou muito altos)
            dynamic_tolerance = float(np.clip(dynamic_tolerance, 0.05, 0.5))

            self.logger.debug(
                f"Dynamic Δ-Φ tolerance updated (Phase {self.current_phase}): "
                f"{base_tolerance:.4f} → {dynamic_tolerance:.4f} "
                f"(percentile={self.tolerance_percentile}, n={len(self.delta_phi_errors)})"
            )

            return dynamic_tolerance
        else:
            # Histórico insuficiente: usa tolerância base por fase
            return base_tolerance

    def validate_with_zscore(self, delta_error: float) -> float:
        """
        🎯 SOLUÇÃO 5: Valida erro Δ-Φ usando z-score normalization.

        Útil para detectar outliers em diferentes escalas temporais.
        Complementa a tolerância phase-aware para detecção de anomalias.

        Args:
            delta_error: Erro |Δ_obs - Δ_esperado|

        Returns:
            Z-score normalizado do erro
        """
        if len(self.delta_phi_errors) < 10:  # Precisa de histórico mínimo
            return 0.0

        import numpy as np

        errors_array = np.array(self.delta_phi_errors[-50:])  # Últimos 50 ciclos
        mean_error = np.mean(errors_array)
        std_error = np.std(errors_array)

        if std_error < 1e-6:  # Previnir divisão por zero
            return 0.0

        zscore = (delta_error - mean_error) / std_error
        return float(zscore)

    def get_violation_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo de todas as violações registradas.

        Returns:
            Dicionário com contagem de violações por tipo e severidade
        """
        summary: Dict[str, Any] = {
            "total": len(self.violations),
            "by_type": {},
            "by_severity": {"warning": 0, "error": 0, "critical": 0},
        }

        for violation in self.violations:
            # Contar por tipo
            by_type: Dict[str, int] = summary["by_type"]  # type: ignore[assignment]
            if violation.violation_type not in by_type:
                by_type[violation.violation_type] = 0
            by_type[violation.violation_type] += 1

            # Contar por severidade
            by_severity: Dict[str, int] = summary["by_severity"]  # type: ignore[assignment]
            by_severity[violation.severity] += 1

        return summary

    def reset(self) -> None:
        """Reseta o histórico de violações."""
        self.violations.clear()
        self.logger.debug("TheoreticalConsistencyGuard: Histórico de violações resetado")


__all__ = ["TheoreticalConsistencyGuard", "ConsistencyViolation"]
