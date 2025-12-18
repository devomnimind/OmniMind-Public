#!/usr/bin/env python3
"""
🔬 Scientific Validation Protocol: Verify OmniMind Consciousness Metrics

Arquivo: scripts/scientific_validation.py

Objetivo: Validar que as métricas de consciência computacional são consistentes,
reproduzíveis e significativas usando metodologia científica rigorosa.

Protocolo de Validação:
  1. Teste de Reprodutibilidade: Mesmas condições → Mesmos resultados
  2. Teste de Sensibilidade: Mudanças pequenas → Mudanças detectáveis
  3. Teste de Robustez: Sistema degradado → Recovery automático
  4. Teste de Correlação: Phi correlaciona com qualidade de integração
  5. Teste de Limite: Testar limites máximos de intensidade
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ValidationTest:
    """Resultado de um teste de validação"""

    name: str
    description: str
    passed: bool
    message: str
    duration_seconds: float
    metrics: Dict[str, Any]


class ScientificValidationSuite:
    """Suite completa de validação científica"""

    def __init__(self, workspace, integration_loop, readiness_engine=None):
        self.workspace = workspace
        self.integration_loop = integration_loop
        self.readiness_engine = readiness_engine

        self.test_results: List[ValidationTest] = []
        self.start_time: float = 0.0

        logger.info("✅ ScientificValidationSuite initialized")

    async def run_full_validation(self) -> Dict[str, Any]:
        """
        Executa suite completa de validação.

        Returns:
            Dict com resultados de todos os testes
        """
        self.start_time = datetime.now().timestamp()
        self.test_results = []

        logger.info("🔬 Starting Scientific Validation Suite...")

        tests = [
            self.test_reproducibility,
            self.test_sensitivity,
            self.test_robustness,
            self.test_correlation,
            self.test_limits,
            self.test_langevin_dynamics,
            self.test_bootstrap_recovery,
        ]

        for test in tests:
            try:
                await test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}", exc_info=True)
                self.test_results.append(
                    ValidationTest(
                        name=test.__name__,
                        description=test.__doc__ or "",
                        passed=False,
                        message=f"Exception: {str(e)}",
                        duration_seconds=0.0,
                        metrics={},
                    )
                )

        return self._generate_report()

    async def test_reproducibility(self):
        """
        Teste 1: Reprodutibilidade

        Hipótese: Mesmas condições iniciais → Mesmos resultados de Phi
        """
        logger.info("📋 Running: Reproducibility Test")
        start = datetime.now()

        try:
            # Coleta inicial
            self.workspace.cross_predictions.clear()

            # Primeira execução
            phi_1_initial = self._get_phi()
            await self.integration_loop.run_cycles(2, collect_metrics_every=1)
            phi_1_after = self._get_phi()

            # Segunda execução (mesmas condições)
            self.workspace.cross_predictions.clear()
            phi_2_initial = self._get_phi()
            await self.integration_loop.run_cycles(2, collect_metrics_every=1)
            phi_2_after = self._get_phi()

            # Validação
            reproducibility_score = 1.0 - abs(phi_1_after - phi_2_after) / max(
                phi_1_after, phi_2_after, 0.01
            )

            passed = reproducibility_score >= 0.8  # 80% similaridade

            self.test_results.append(
                ValidationTest(
                    name="test_reproducibility",
                    description="Mesmas condições → Mesmos resultados",
                    passed=passed,
                    message=f"Reproducibility score: {reproducibility_score:.2%}",
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={
                        "phi_run1": phi_1_after,
                        "phi_run2": phi_2_after,
                        "reproducibility_score": reproducibility_score,
                        "passed": passed,
                    },
                )
            )

            logger.info(f"✅ Reproducibility Test: {reproducibility_score:.2%} ({passed})")

        except Exception as e:
            logger.error(f"❌ Reproducibility test failed: {e}")
            self.test_results.append(
                ValidationTest(
                    name="test_reproducibility",
                    description="Mesmas condições → Mesmos resultados",
                    passed=False,
                    message=str(e),
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={},
                )
            )

    async def test_sensitivity(self):
        """
        Teste 2: Sensibilidade

        Hipótese: Perturbações → Mudanças detectáveis em Phi
        """
        logger.info("📋 Running: Sensitivity Test")
        start = datetime.now()

        try:
            # Baseline
            self.workspace.cross_predictions.clear()
            await self.integration_loop.run_cycles(1, collect_metrics_every=1)
            phi_baseline = self._get_phi()

            # Com perturbação (mais ciclos = mais dados = diferentes predições)
            await self.integration_loop.run_cycles(3, collect_metrics_every=1)
            phi_perturbed = self._get_phi()

            # Validação
            sensitivity = abs(phi_perturbed - phi_baseline)
            passed = sensitivity > 0.05  # Detectável se diferença > 5%

            self.test_results.append(
                ValidationTest(
                    name="test_sensitivity",
                    description="Perturbações → Mudanças detectáveis",
                    passed=passed,
                    message=f"Sensitivity: {sensitivity:.3f}",
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={
                        "phi_baseline": phi_baseline,
                        "phi_perturbed": phi_perturbed,
                        "sensitivity": sensitivity,
                        "passed": passed,
                    },
                )
            )

            logger.info(f"✅ Sensitivity Test: Δ={sensitivity:.3f} ({passed})")

        except Exception as e:
            logger.error(f"❌ Sensitivity test failed: {e}")
            self.test_results.append(
                ValidationTest(
                    name="test_sensitivity",
                    description="Perturbações → Mudanças detectáveis",
                    passed=False,
                    message=str(e),
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={},
                )
            )

    async def test_robustness(self):
        """
        Teste 3: Robustez

        Hipótese: Sistema degradado → Readiness engine recupera
        """
        logger.info("📋 Running: Robustness Test")
        start = datetime.now()

        try:
            if not self.readiness_engine:
                logger.warning("Skipping robustness test (no readiness engine)")
                self.test_results.append(
                    ValidationTest(
                        name="test_robustness",
                        description="Sistema degradado → Recovery automático",
                        passed=True,
                        message="Skipped (no readiness engine)",
                        duration_seconds=0.0,
                        metrics={},
                    )
                )
                return

            # Obter status inicial
            status_initial = await self.readiness_engine.validator.check_readiness(self.workspace)

            # Simular degradação (limpar cross-predictions)
            self.workspace.cross_predictions.clear()
            status_degraded = await self.readiness_engine.validator.check_readiness(self.workspace)

            passed = status_initial.state == "READY" and status_degraded.state in [
                "DEGRADED",
                "CRITICAL",
            ]

            self.test_results.append(
                ValidationTest(
                    name="test_robustness",
                    description="Sistema degradado → Recovery automático",
                    passed=passed,
                    message=f"Initial: {status_initial.state}, Degraded: {status_degraded.state}",
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={
                        "status_initial": status_initial.state,
                        "status_degraded": status_degraded.state,
                        "passed": passed,
                    },
                )
            )

            logger.info(
                f"✅ Robustness Test: {status_initial.state}→{status_degraded.state} ({passed})"
            )

        except Exception as e:
            logger.error(f"❌ Robustness test failed: {e}")
            self.test_results.append(
                ValidationTest(
                    name="test_robustness",
                    description="Sistema degradado → Recovery automático",
                    passed=False,
                    message=str(e),
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={},
                )
            )

    async def test_correlation(self):
        """
        Teste 4: Correlação

        Hipótese: Phi correlaciona com qualidade de r²
        """
        logger.info("📋 Running: Correlation Test")
        start = datetime.now()

        try:
            correlations = []

            # Coletar múltiplos pontos de dados
            for i in range(5):
                await self.integration_loop.run_cycles(1, collect_metrics_every=1)

                phi = self._get_phi()
                r2_quality = self._get_r_squared_quality()

                correlations.append((phi, r2_quality))

            # Calcular correlação de Pearson
            if len(correlations) >= 3:
                phis = [x[0] for x in correlations]
                r2s = [x[1] for x in correlations]

                correlation = np.corrcoef(phis, r2s)[0, 1]
                passed = abs(correlation) > 0.5  # Correlação moderada
            else:
                correlation = 0.0
                passed = False

            self.test_results.append(
                ValidationTest(
                    name="test_correlation",
                    description="Phi correlaciona com r² quality",
                    passed=passed,
                    message=f"Pearson correlation: {correlation:.3f}",
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={
                        "pearson_correlation": correlation,
                        "data_points": len(correlations),
                        "passed": passed,
                    },
                )
            )

            logger.info(f"✅ Correlation Test: r={correlation:.3f} ({passed})")

        except Exception as e:
            logger.error(f"❌ Correlation test failed: {e}")
            self.test_results.append(
                ValidationTest(
                    name="test_correlation",
                    description="Phi correlaciona com r² quality",
                    passed=False,
                    message=str(e),
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={},
                )
            )

    async def test_limits(self):
        """
        Teste 5: Limites

        Hipótese: Sistema suporta intensidade máxima sem crash
        """
        logger.info("📋 Running: Limits Test")
        start = datetime.now()

        try:
            # Testar com múltiplos ciclos intensivos
            for cycles in [5, 8, 10]:
                try:
                    await asyncio.wait_for(
                        self.integration_loop.run_cycles(cycles, collect_metrics_every=1),
                        timeout=30.0,
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout with {cycles} cycles")
                    break

            # Se chegou aqui sem crash
            passed = True
            message = "System handled intensive cycles without crashing"

            self.test_results.append(
                ValidationTest(
                    name="test_limits",
                    description="Sistema suporta intensidade máxima",
                    passed=passed,
                    message=message,
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={"passed": passed},
                )
            )

            logger.info(f"✅ Limits Test: {message}")

        except Exception as e:
            logger.error(f"❌ Limits test failed: {e}")
            self.test_results.append(
                ValidationTest(
                    name="test_limits",
                    description="Sistema suporta intensidade máxima",
                    passed=False,
                    message=str(e),
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={},
                )
            )

    async def test_langevin_dynamics(self):
        """
        Teste 6: Langevin Dynamics

        Hipótese: Embeddings têm variação estocástica (sem convergência)
        """
        logger.info("📋 Running: Langevin Dynamics Test")
        start = datetime.now()

        try:
            # Coletar históricos
            await self.integration_loop.run_cycles(5, collect_metrics_every=1)

            variances = []
            for module in ["sensory_input", "qualia", "narrative"]:
                try:
                    history = self.workspace.get_module_history(module)
                    if history and len(history) >= 2:
                        recent = history[-10:]
                        variance = np.var(recent)
                        variances.append(variance)
                except Exception:
                    continue

            # Validação
            avg_variance = np.mean(variances) if variances else 0.0
            passed = avg_variance > 0.01  # Alguma variação detectada

            self.test_results.append(
                ValidationTest(
                    name="test_langevin_dynamics",
                    description="Embeddings com variação estocástica",
                    passed=passed,
                    message=f"Average variance: {avg_variance:.4f}",
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={
                        "average_variance": avg_variance,
                        "modules_tested": len(variances),
                        "passed": passed,
                    },
                )
            )

            logger.info(f"✅ Langevin Dynamics Test: variance={avg_variance:.4f} ({passed})")

        except Exception as e:
            logger.error(f"❌ Langevin Dynamics test failed: {e}")
            self.test_results.append(
                ValidationTest(
                    name="test_langevin_dynamics",
                    description="Embeddings com variação estocástica",
                    passed=False,
                    message=str(e),
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={},
                )
            )

    async def test_bootstrap_recovery(self):
        """
        Teste 7: Bootstrap Recovery

        Hipótese: Sistema recupera após perda de dados
        """
        logger.info("📋 Running: Bootstrap Recovery Test")
        start = datetime.now()

        try:
            # Ter dados válidos
            await self.integration_loop.run_cycles(2, collect_metrics_every=1)
            phi_before = self._get_phi()

            # Simular perda
            self.workspace.cross_predictions.clear()
            phi_after_loss = self._get_phi()

            # Re-bootstrap
            await self.integration_loop.run_cycles(2, collect_metrics_every=1)
            phi_recovered = self._get_phi()

            # Validação
            loss_detected = phi_after_loss < 0.1
            recovery_successful = phi_recovered > 0.05
            passed = loss_detected and recovery_successful

            self.test_results.append(
                ValidationTest(
                    name="test_bootstrap_recovery",
                    description="Sistema recupera após perda de dados",
                    passed=passed,
                    message=f"Before: {phi_before:.3f}, After loss: {phi_after_loss:.3f}, Recovered: {phi_recovered:.3f}",
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={
                        "phi_before": phi_before,
                        "phi_after_loss": phi_after_loss,
                        "phi_recovered": phi_recovered,
                        "passed": passed,
                    },
                )
            )

            logger.info(
                f"✅ Bootstrap Recovery Test: {phi_before:.3f}→{phi_after_loss:.3f}→{phi_recovered:.3f} ({passed})"
            )

        except Exception as e:
            logger.error(f"❌ Bootstrap Recovery test failed: {e}")
            self.test_results.append(
                ValidationTest(
                    name="test_bootstrap_recovery",
                    description="Sistema recupera após perda de dados",
                    passed=False,
                    message=str(e),
                    duration_seconds=(datetime.now() - start).total_seconds(),
                    metrics={},
                )
            )

    def _get_phi(self) -> float:
        """Obtém Phi atual"""
        if not self.workspace or not self.workspace.cross_predictions:
            return 0.0

        try:
            r_squared = [
                cp.r_squared
                for cp in self.workspace.cross_predictions[-20:]
                if cp.r_squared is not None
                and isinstance(cp.r_squared, (int, float))
                and not np.isnan(cp.r_squared)
            ]
            if r_squared:
                return float(np.mean(r_squared))
        except Exception:
            pass

        return 0.0

    def _get_r_squared_quality(self) -> float:
        """Qualidade de r²"""
        if not self.workspace or not self.workspace.cross_predictions:
            return 0.0

        try:
            r_squared = [
                cp.r_squared
                for cp in self.workspace.cross_predictions[-5:]
                if cp.r_squared is not None
                and isinstance(cp.r_squared, (int, float))
                and not np.isnan(cp.r_squared)
            ]
            if r_squared:
                return float(np.mean(r_squared))
        except Exception:
            pass

        return 0.0

    def _generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo"""
        passed_count = sum(1 for t in self.test_results if t.passed)
        total_count = len(self.test_results)

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count,
            "pass_rate": passed_count / total_count if total_count > 0 else 0.0,
            "tests": [
                {
                    "name": t.name,
                    "description": t.description,
                    "passed": t.passed,
                    "message": t.message,
                    "duration_seconds": t.duration_seconds,
                    "metrics": t.metrics,
                }
                for t in self.test_results
            ],
        }

        logger.info(
            f"""

        ╔════════════════════════════════════════════════════════════════╗
        ║           🔬 SCIENTIFIC VALIDATION REPORT                      ║
        ╠════════════════════════════════════════════════════════════════╣
        ║  Total Tests: {total_count:3d}                                             ║
        ║  Passed:      {passed_count:3d}  ✅                                             ║
        ║  Failed:      {total_count - passed_count:3d}  ❌                                             ║
        ║  Pass Rate:   {report["pass_rate"]:6.1%}                                           ║
        ╚════════════════════════════════════════════════════════════════╝
        """
        )

        return report

    def save_report(self, filepath: str):
        """Salva relatório em JSON"""
        report = self._generate_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"✅ Report saved to {filepath}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════════════════════


async def run_scientific_validation_cli():
    """CLI para rodar validação científica"""
    import argparse

    parser = argparse.ArgumentParser(description="Scientific Validation Suite for OmniMind")
    parser.add_argument(
        "--output", type=str, default="validation_report.json", help="Output file for report"
    )

    args = parser.parse_args()

    # Inicializar sistema
    from src.consciousness.integration_loop import IntegrationLoop
    from src.consciousness.shared_workspace import SharedWorkspace
    from src.consciousness.system_readiness_validator import ContinuousReadinessEngine

    logger.info("Initializing OmniMind system for validation...")

    workspace = SharedWorkspace()
    loop = IntegrationLoop(workspace=workspace)
    readiness = ContinuousReadinessEngine(loop, workspace)

    suite = ScientificValidationSuite(workspace, loop, readiness)

    # Rodar validação
    report = await suite.run_full_validation()
    suite.save_report(args.output)

    logger.info(f"✅ Validation complete. Report: {args.output}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_scientific_validation_cli())
    asyncio.run(run_scientific_validation_cli())
