"""Autonomous Loop - Phase 26C

The main autonomous loop that runs 24/7.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict

from autonomous.auto_documentation_engine import AutoDocumentationEngine
from autonomous.auto_validation_engine import AutoValidationEngine
from autonomous.dynamic_framework_adapter import DynamicFrameworkAdapter
from autonomous.problem_detection_engine import ProblemDetectionEngine, SystemState
from autonomous.solution_lookup_engine import SolutionLookupEngine

logger = logging.getLogger(__name__)


class OmniMindAutonomousLoop:
    """O loop que roda 24/7 sem humano"""

    def __init__(self):
        """Initialize autonomous loop"""
        self.detector = ProblemDetectionEngine()
        self.solver = SolutionLookupEngine()
        self.adapter = DynamicFrameworkAdapter()
        self.validator = AutoValidationEngine()
        self.documenter = AutoDocumentationEngine()

        logger.info("OmniMindAutonomousLoop initialized")

    def get_system_state(self) -> SystemState:
        """Get current system state

        Returns:
            SystemState snapshot
        """
        return self.detector.get_system_state()

    async def autonomous_run(self, check_interval: float = 10.0):
        """O verdadeiro OmniMind autônomo

        Args:
            check_interval: Seconds between checks (default: 10)
        """
        logger.info("🧠 OmniMind Autonomous Loop started")
        logger.info(f"   Check interval: {check_interval}s")

        while True:
            try:
                # 1. DETECT
                system_state = self.get_system_state()
                issues = self.detector.detect_issues(system_state)

                if not issues:
                    # Tudo ok, continuar
                    await asyncio.sleep(check_interval)
                    continue

                # Tem problema
                issue = issues[0]  # Mais crítico primeiro
                logger.info(
                    "\n[OMNIMIND] 🔍 Detectei problema: %s (%s)",
                    issue.type,
                    issue.severity,
                )

                # 2. CLASSIFY
                classification = self.detector.classify_issue(issue)

                if not classification.get("auto_fixable", False):
                    # Logging para humano revisar
                    logger.warning(f"[OMNIMIND] ⚠️ Problema não auto-fixable: {issue.type}")
                    logger.warning(f"   Requer revisão humana: {issue.description}")
                    await asyncio.sleep(check_interval)
                    continue

                # 3. SEARCH SOLUTION
                logger.info("[OMNIMIND] 🔎 Buscando solução...")
                issue_dict = {
                    "type": issue.type,
                    "description": issue.description,
                    "severity": issue.severity,
                    "metric": issue.metric,
                    "value": issue.value,
                }
                solution = self.solver.find_solution(issue_dict)

                if solution.get("source") == "MANUAL_REQUIRED":
                    # Impossível resolver automaticamente
                    logger.warning("[OMNIMIND] ⚠️ Solução requer intervenção manual")
                    logger.warning(f"   Sugestões: {solution.get('suggestions', [])}")
                    await asyncio.sleep(check_interval)
                    continue

                # 4. ADAPT TO MACHINE
                logger.info("[OMNIMIND] 🔧 Adaptando solução ao hardware...")
                adapted = self.adapter.adapt_to_environment(solution)

                # 5. VALIDATE
                logger.info("[OMNIMIND] ✓ Validando solução...")
                if not self.validator.validate_solution(adapted, issue_dict):
                    # Falhou validação
                    logger.warning("[OMNIMIND] ❌ Validação falhou")
                    await asyncio.sleep(check_interval)
                    continue

                # 6. APPLY
                logger.info("[OMNIMIND] ⚙️ Aplicando adaptação...")
                metrics_before = {
                    "cpu": system_state.cpu_percent,
                    "memory": system_state.memory_percent,
                }
                self.adapter.apply_adaptation(adapted)

                # Get new state
                await asyncio.sleep(2)  # Wait for changes to take effect
                new_state = self.get_system_state()
                metrics_after = {
                    "cpu": new_state.cpu_percent,
                    "memory": new_state.memory_percent,
                }

                # Calculate improvement
                improvement = self._calculate_improvement(metrics_before, metrics_after, issue.type)

                # 7. DOCUMENT
                logger.info("[OMNIMIND] 📝 Documentando...")
                self.documenter.document_adaptation(
                    issue_dict,
                    solution,
                    {
                        "success": True,
                        "metrics_before": metrics_before,
                        "metrics_after": metrics_after,
                        "improvement_percent": improvement,
                        "machine_specs": {
                            "memory_gb": self.adapter.machine_config.memory_gb,
                            "gpu_count": self.adapter.machine_config.gpu_count,
                        },
                        "framework_version": "Phase 26C",
                    },
                )

                # 8. LOG
                logger.info("[OMNIMIND] ✅ Problema resolvido!")
                logger.info("   Tipo: %s", issue.type)
                logger.info("   Fonte: %s", solution.get("source"))
                logger.info("   Melhoria: %.1f%%", improvement)

                # Aguardar antes de próxima verificação
                await asyncio.sleep(check_interval)

            except Exception as e:
                # Erro ao tentar resolver
                logger.error(f"[OMNIMIND] ❌ Erro durante auto-adapt: {e}", exc_info=True)
                await asyncio.sleep(60)  # Aguardar mais em caso de erro

    def _calculate_improvement(
        self,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float],
        issue_type: str,
    ) -> float:
        """Calculate improvement percentage

        Args:
            metrics_before: Metrics before adaptation
            metrics_after: Metrics after adaptation
            issue_type: Type of issue

        Returns:
            Improvement percentage
        """
        if issue_type == "MEMORY":
            before = metrics_before.get("memory", 100)
            after = metrics_after.get("memory", 100)
            if before > 0:
                return ((before - after) / before) * 100
        elif issue_type == "PERFORMANCE":
            before = metrics_before.get("cpu", 100)
            after = metrics_after.get("cpu", 100)
            if before > 0:
                return ((before - after) / before) * 100

        return 0.0


async def main():
    """Main entry point"""
    omnimind = OmniMindAutonomousLoop()

    print(
        """
    🧠 ═══════════════════════════════════════════════════════════
    🧠  OMNIMIND AUTONOMOUS ADAPTATION ENGINE
    🧠  Phase 26C: Self-Healing + Self-Optimizing
    🧠
    🧠  Rodando 24/7 sem humano
    🧠  Detectando problemas → Buscando soluções → Adaptando → Validando
    🧠
    🧠  Supervisão: Todos os passos logados e reversíveis
    🧠 ═══════════════════════════════════════════════════════════
    """
    )

    await omnimind.autonomous_run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
