#!/usr/bin/env python3
"""
TREINAMENTO ESTENDIDO COM VALIDAÇÃO CIENTÍFICA RIGOROSA

Executa ciclos longos de treinamento com:
- Múltiplas execuções independentes
- Validação estatística rigorosa
- Detecção de inconsistências
- Análise crítica dos resultados
- Relatórios persistentes

Ato como supervisor científico cético, questionando:
- Consistência dos cálculos
- Validade dos resultados
- Robustez das métricas
- Integridade dos dados
"""

from __future__ import annotations

import asyncio
import json
import logging
import statistics
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Adicionar src ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(project_root / "logs" / "extended_training.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class TrainingCycle:
    """Registro de um ciclo de treinamento."""

    cycle_id: int
    timestamp: float
    phi_before: float
    phi_after: float
    phi_delta: float
    metrics: Dict[str, float]
    anomalies: List[str]
    validation_passed: bool


@dataclass
class TrainingSession:
    """Sessão completa de treinamento."""

    session_id: str
    start_time: float
    end_time: Optional[float]
    total_cycles: int
    cycles: List[TrainingCycle]
    statistics: Dict[str, Any]
    validation_results: Dict[str, Any]
    inconsistencies: List[str]
    scientific_verdict: str


class ScientificSupervisor:
    """Supervisor científico cético para validação rigorosa."""

    def __init__(self):
        self.inconsistencies: List[str] = []
        self.warnings: List[str] = []
        self.critical_issues: List[str] = []

    def validate_phi_calculation(
        self, phi_before: float, phi_after: float, cycle_id: int
    ) -> List[str]:
        """Valida cálculo de Φ com ceticismo científico."""
        issues = []

        # 1. Verificar ranges
        if not (0 <= phi_before <= 1):
            issues.append(f"Ciclo {cycle_id}: phi_before fora do range [0,1]: {phi_before}")
            self.critical_issues.append(f"Range inválido em ciclo {cycle_id}")

        if not (0 <= phi_after <= 1):
            issues.append(f"Ciclo {cycle_id}: phi_after fora do range [0,1]: {phi_after}")
            self.critical_issues.append(f"Range inválido em ciclo {cycle_id}")

        # 2. Verificar mudanças abruptas (possível erro de cálculo)
        delta = abs(phi_after - phi_before)
        if delta > 0.5:
            issues.append(
                f"Ciclo {cycle_id}: Mudança abrupta de Φ ({phi_before:.4f} -> {phi_after:.4f}, Δ={delta:.4f})"
            )
            self.warnings.append(f"Mudança abrupta suspeita em ciclo {cycle_id}")

        # 3. Verificar se Φ está sempre zero (possível bug)
        if phi_before == 0.0 and phi_after == 0.0:
            issues.append(f"Ciclo {cycle_id}: Φ permanece em zero (possível cálculo não executado)")

        # 4. Verificar se há NaN ou Inf
        if np.isnan(phi_before) or np.isinf(phi_before):
            issues.append(f"Ciclo {cycle_id}: phi_before é NaN/Inf")
            self.critical_issues.append(f"Valor inválido em ciclo {cycle_id}")

        if np.isnan(phi_after) or np.isinf(phi_after):
            issues.append(f"Ciclo {cycle_id}: phi_after é NaN/Inf")
            self.critical_issues.append(f"Valor inválido em ciclo {cycle_id}")

        return issues

    def validate_statistical_consistency(self, cycles: List[TrainingCycle]) -> List[str]:
        """Valida consistência estatística dos resultados."""
        issues = []

        if len(cycles) < 10:
            issues.append("Poucos ciclos para análise estatística robusta")
            return issues

        # Extrair valores de Φ
        phi_before_values = [c.phi_before for c in cycles]
        phi_after_values = [c.phi_after for c in cycles]
        phi_deltas = [c.phi_delta for c in cycles]

        # 1. Verificar variância (muito baixa = possível hardcoding)
        phi_before_var = statistics.variance(phi_before_values) if len(phi_before_values) > 1 else 0
        phi_after_var = statistics.variance(phi_after_values) if len(phi_after_values) > 1 else 0

        if phi_before_var < 0.0001:
            issues.append(
                f"Variância muito baixa em phi_before ({phi_before_var:.6f}) - possível hardcoding"
            )
            self.warnings.append("Variância suspeitamente baixa")

        if phi_after_var < 0.0001:
            issues.append(
                f"Variância muito baixa em phi_after ({phi_after_var:.6f}) - possível hardcoding"
            )
            self.warnings.append("Variância suspeitamente baixa")

        # 2. Verificar tendência (deve haver alguma variação)
        if all(abs(d) < 0.001 for d in phi_deltas):
            issues.append("Deltas de Φ muito consistentes - possível cálculo determinístico demais")
            self.warnings.append("Falta de variabilidade nos resultados")

        # 3. Verificar outliers (mudanças muito grandes)
        if phi_deltas:
            mean_delta = statistics.mean(phi_deltas)
            stdev_delta = statistics.stdev(phi_deltas) if len(phi_deltas) > 1 else 0
            outliers = [
                i
                for i, d in enumerate(phi_deltas)
                if abs(d - mean_delta) > 3 * stdev_delta and stdev_delta > 0
            ]
            if outliers:
                issues.append(f"Encontrados {len(outliers)} outliers nos deltas de Φ")
                self.warnings.append("Outliers detectados - investigar")

        return issues

    def generate_scientific_verdict(self, session: TrainingSession) -> str:
        """Gera veredito científico baseado em evidências."""
        if self.critical_issues:
            return "REJEITADO: Problemas críticos detectados nos cálculos"
        elif len(self.inconsistencies) > len(session.cycles) * 0.1:
            return "REJEITADO: Muitas inconsistências (>10% dos ciclos)"
        elif len(self.warnings) > len(session.cycles) * 0.2:
            return "CONDICIONAL: Muitos avisos - requer revisão"
        elif session.total_cycles < 100:
            return "INCOMPLETO: Poucos ciclos para validação estatística"
        else:
            return "APROVADO: Resultados consistentes e válidos"


class ExtendedTrainingRunner:
    """Executor de treinamento estendido com validação científica."""

    def __init__(
        self,
        cycles: int = 500,
        cycle_interval: float = 1.0,
        validation_interval: int = 50,
    ):
        self.cycles = cycles
        self.cycle_interval = cycle_interval
        self.validation_interval = validation_interval
        self.supervisor = ScientificSupervisor()
        self.session: Optional[TrainingSession] = None

    async def run_training(self) -> TrainingSession:
        """Executa treinamento estendido."""
        session_id = f"training_{int(time.time())}"
        logger.info("=" * 80)
        logger.info(f"INICIANDO TREINAMENTO ESTENDIDO: {session_id}")
        logger.info(f"Ciclos: {self.cycles}, Intervalo: {self.cycle_interval}s")
        logger.info("=" * 80)

        start_time = time.time()
        training_cycles: List[TrainingCycle] = []

        # Inicializar IntegrationLoop
        try:
            from src.consciousness.integration_loop import IntegrationLoop

            integration_loop = IntegrationLoop(enable_logging=False)
            logger.info("IntegrationLoop inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar IntegrationLoop: {e}")
            raise

        # Executar ciclos
        for cycle_id in range(1, self.cycles + 1):
            try:
                # Coletar métricas antes
                phi_before = await self._get_current_phi(integration_loop)

                # Executar ciclo (sem timeout - sistema pesado, permite tempo necessário)
                await integration_loop.run_cycles(1, collect_metrics_every=1)

                # Coletar métricas depois
                phi_after = await self._get_current_phi(integration_loop)
                phi_delta = phi_after - phi_before

                # Validar com supervisor científico
                anomalies = self.supervisor.validate_phi_calculation(
                    phi_before, phi_after, cycle_id
                )

                # Coletar métricas adicionais
                metrics = {
                    "phi_before": phi_before,
                    "phi_after": phi_after,
                    "phi_delta": phi_delta,
                }

                cycle = TrainingCycle(
                    cycle_id=cycle_id,
                    timestamp=time.time(),
                    phi_before=phi_before,
                    phi_after=phi_after,
                    phi_delta=phi_delta,
                    metrics=metrics,
                    anomalies=anomalies,
                    validation_passed=len(anomalies) == 0,
                )

                training_cycles.append(cycle)
                self.supervisor.inconsistencies.extend(anomalies)

                # Log progresso
                if cycle_id % 50 == 0:
                    logger.info(
                        f"Ciclo {cycle_id}/{self.cycles}: Φ {phi_before:.4f} -> {phi_after:.4f} "
                        f"(Δ={phi_delta:+.4f}) | Anomalias: {len(anomalies)}"
                    )

                # Validação intermediária
                if cycle_id % self.validation_interval == 0:
                    stats_issues = self.supervisor.validate_statistical_consistency(
                        training_cycles[-self.validation_interval :]
                    )
                    self.supervisor.warnings.extend(stats_issues)

                await asyncio.sleep(self.cycle_interval)

            except Exception as e:
                logger.error(f"Erro no ciclo {cycle_id}: {e}", exc_info=True)
                self.supervisor.critical_issues.append(f"Erro em ciclo {cycle_id}: {e}")

        # Calcular estatísticas finais
        end_time = time.time()
        statistics_data = self._calculate_statistics(training_cycles)

        # Validação final
        final_stats_issues = self.supervisor.validate_statistical_consistency(training_cycles)
        self.supervisor.warnings.extend(final_stats_issues)

        # Gerar veredito científico
        scientific_verdict = self.supervisor.generate_scientific_verdict(
            TrainingSession(
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                total_cycles=len(training_cycles),
                cycles=training_cycles,
                statistics={},
                validation_results={},
                inconsistencies=[],
                scientific_verdict="",
            )
        )

        # Criar sessão final
        session = TrainingSession(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            total_cycles=len(training_cycles),
            cycles=training_cycles,
            statistics=statistics_data,
            validation_results={
                "inconsistencies": len(self.supervisor.inconsistencies),
                "warnings": len(self.supervisor.warnings),
                "critical_issues": len(self.supervisor.critical_issues),
            },
            inconsistencies=self.supervisor.inconsistencies[:20],  # Primeiros 20
            scientific_verdict=scientific_verdict,
        )

        return session

    async def _get_current_phi(self, integration_loop) -> float:
        """Obtém Φ atual do IntegrationLoop."""
        try:
            workspace = integration_loop.workspace
            phi = workspace.compute_phi_from_integrations()
            return float(phi) if not (np.isnan(phi) or np.isinf(phi)) else 0.0
        except Exception as e:
            logger.debug(f"Erro ao obter Φ: {e}")
            return 0.0

    def _calculate_statistics(self, cycles: List[TrainingCycle]) -> Dict[str, Any]:
        """Calcula estatísticas dos ciclos."""
        if not cycles:
            return {}

        phi_before_values = [c.phi_before for c in cycles]
        phi_after_values = [c.phi_after for c in cycles]
        phi_deltas = [c.phi_delta for c in cycles]

        return {
            "phi_before": {
                "mean": float(statistics.mean(phi_before_values)),
                "stdev": (
                    float(statistics.stdev(phi_before_values))
                    if len(phi_before_values) > 1
                    else 0.0
                ),
                "min": float(min(phi_before_values)),
                "max": float(max(phi_before_values)),
            },
            "phi_after": {
                "mean": float(statistics.mean(phi_after_values)),
                "stdev": (
                    float(statistics.stdev(phi_after_values)) if len(phi_after_values) > 1 else 0.0
                ),
                "min": float(min(phi_after_values)),
                "max": float(max(phi_after_values)),
            },
            "phi_delta": {
                "mean": float(statistics.mean(phi_deltas)),
                "stdev": float(statistics.stdev(phi_deltas)) if len(phi_deltas) > 1 else 0.0,
                "min": float(min(phi_deltas)),
                "max": float(max(phi_deltas)),
            },
            "validation_passed_rate": sum(1 for c in cycles if c.validation_passed) / len(cycles),
        }

    def save_session(self, session: TrainingSession) -> Path:
        """Salva sessão de treinamento."""
        sessions_dir = project_root / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        session_file = sessions_dir / f"{session.session_id}.json"

        # Converter para dict (sem os ciclos completos para economizar espaço)
        session_dict = asdict(session)
        session_dict["cycles"] = [
            {
                "cycle_id": c.cycle_id,
                "phi_before": c.phi_before,
                "phi_after": c.phi_after,
                "phi_delta": c.phi_delta,
                "anomalies_count": len(c.anomalies),
                "validation_passed": c.validation_passed,
            }
            for c in session.cycles
        ]

        with session_file.open("w", encoding="utf-8") as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Sessão salva em: {session_file}")
        return session_file


async def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Treinamento estendido com validação científica")
    parser.add_argument("--cycles", type=int, default=500, help="Número de ciclos")
    parser.add_argument("--interval", type=float, default=1.0, help="Intervalo entre ciclos (s)")
    parser.add_argument(
        "--validation-interval", type=int, default=50, help="Intervalo de validação"
    )
    args = parser.parse_args()

    runner = ExtendedTrainingRunner(
        cycles=args.cycles,
        cycle_interval=args.interval,
        validation_interval=args.validation_interval,
    )

    try:
        session = await runner.run_training()
        session_file = runner.save_session(session)

        # Imprimir resumo
        print("\n" + "=" * 80)
        print("RESUMO DO TREINAMENTO")
        print("=" * 80)
        print(f"Sessão: {session.session_id}")
        print(f"Ciclos executados: {session.total_cycles}")
        print(f"Duração: {session.end_time - session.start_time:.2f}s")
        print(f"\nEstatísticas:")
        print(f"  Φ médio (antes): {session.statistics.get('phi_before', {}).get('mean', 0):.4f}")
        print(f"  Φ médio (depois): {session.statistics.get('phi_after', {}).get('mean', 0):.4f}")
        print(f"  ΔΦ médio: {session.statistics.get('phi_delta', {}).get('mean', 0):.4f}")
        print(f"\nValidação:")
        print(f"  Inconsistências: {session.validation_results.get('inconsistencies', 0)}")
        print(f"  Avisos: {session.validation_results.get('warnings', 0)}")
        print(f"  Problemas críticos: {session.validation_results.get('critical_issues', 0)}")
        print(f"\nVeredito Científico: {session.scientific_verdict}")
        print(f"\nArquivo: {session_file}")
        print("=" * 80)

        # Exit code baseado no veredito
        if "REJEITADO" in session.scientific_verdict:
            sys.exit(1)
        elif "CONDICIONAL" in session.scientific_verdict:
            sys.exit(2)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Treinamento interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro fatal no treinamento: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
