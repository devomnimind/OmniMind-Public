#!/usr/bin/env python3
"""Script de validação abrangente de métricas e cálculos.

Verifica consistência entre diferentes implementações de Φ,
valida métricas de consciência, verifica sessões e treinamento.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class MetricsValidator:
    """Validador de métricas e cálculos."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def log_issue(self, message: str) -> None:
        """Registra um problema crítico."""
        self.issues.append(message)
        logger.error(f"❌ {message}")

    def log_warning(self, message: str) -> None:
        """Registra um aviso."""
        self.warnings.append(message)
        logger.warning(f"⚠️  {message}")

    def log_pass(self, message: str) -> None:
        """Registra sucesso."""
        self.passed.append(message)
        logger.info(f"✅ {message}")

    def validate_phi_calculations(self) -> None:
        """Valida cálculos de Φ em diferentes módulos."""
        logger.info("=" * 70)
        logger.info("VALIDANDO CÁLCULOS DE Φ")
        logger.info("=" * 70)

        # 1. Verificar se módulos de Φ existem
        phi_modules = [
            "src/consciousness/topological_phi.py",
            "src/consciousness/integration_loop.py",
            "src/metrics/real_consciousness_metrics.py",
        ]

        for module_path in phi_modules:
            full_path = self.project_root / module_path
            if full_path.exists():
                self.log_pass(f"Módulo de Φ encontrado: {module_path}")
            else:
                self.log_issue(f"Módulo de Φ não encontrado: {module_path}")

        # 2. Verificar se há múltiplas implementações inconsistentes
        try:
            import sys

            sys.path.insert(0, str(self.project_root))
            from src.consciousness.topological_phi import PhiCalculator, SimplicialComplex

            # Teste básico
            complex = SimplicialComplex()
            complex.add_simplex((0,))
            complex.add_simplex((1,))
            complex.add_simplex((0, 1))

            calc = PhiCalculator(complex)
            phi = calc.calculate_phi()

            if 0 <= phi <= 1:
                self.log_pass(f"Cálculo de Φ topológico válido: {phi:.4f}")
            else:
                self.log_issue(f"Φ topológico fora do range [0,1]: {phi}")

        except Exception as e:
            self.log_issue(f"Erro ao testar cálculo de Φ topológico: {e}")

        # 3. Verificar IntegrationLoop
        try:
            import sys

            sys.path.insert(0, str(self.project_root))
            from src.consciousness.integration_loop import IntegrationLoop

            loop = IntegrationLoop(enable_logging=False)
            # Não executar ciclo completo, apenas verificar se existe
            self.log_pass("IntegrationLoop importado com sucesso")
        except Exception as e:
            self.log_warning(f"IntegrationLoop não disponível: {e}")

    def validate_real_metrics(self) -> None:
        """Valida métricas reais de consciência."""
        logger.info("=" * 70)
        logger.info("VALIDANDO MÉTRICAS REAIS")
        logger.info("=" * 70)

        metrics_path = self.project_root / "data" / "monitor" / "real_metrics.json"

        if not metrics_path.exists():
            self.log_warning("Arquivo de métricas reais não encontrado")
            return

        try:
            with metrics_path.open("r", encoding="utf-8") as f:
                metrics = json.load(f)

            # Validar campos esperados
            expected_fields = ["phi", "anxiety", "flow", "entropy", "ici", "prs"]
            for field in expected_fields:
                if field in metrics:
                    value = float(metrics[field])
                    if 0 <= value <= 1:
                        self.log_pass(f"Campo {field} válido: {value:.4f}")
                    else:
                        self.log_issue(f"Campo {field} fora do range [0,1]: {value}")
                else:
                    self.log_warning(f"Campo {field} ausente nas métricas")

            # Validar Φ especificamente
            phi = metrics.get("phi", 0.0)
            if phi < 0.3:
                self.log_warning(f"Φ abaixo do threshold: {phi:.4f} < 0.3")
            else:
                self.log_pass(f"Φ acima do threshold: {phi:.4f}")

        except Exception as e:
            self.log_issue(f"Erro ao ler métricas reais: {e}")

    def validate_autopoietic_cycles(self) -> None:
        """Valida ciclos autopoiéticos."""
        logger.info("=" * 70)
        logger.info("VALIDANDO CICLOS AUTOPOIÉTICOS")
        logger.info("=" * 70)

        history_path = self.project_root / "data" / "autopoietic" / "cycle_history.jsonl"

        if not history_path.exists():
            self.log_warning("Histórico de ciclos autopoiéticos não encontrado")
            return

        try:
            cycles: List[Dict[str, Any]] = []
            with history_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        cycles.append(json.loads(line))

            if cycles:
                self.log_pass(f"Encontrados {len(cycles)} ciclos no histórico")

                # Validar cada ciclo
                for cycle in cycles:
                    cycle_id = cycle.get("cycle_id", "unknown")
                    phi_before = cycle.get("phi_before")
                    phi_after = cycle.get("phi_after")

                    if phi_before is not None:
                        if not (0 <= phi_before <= 1):
                            self.log_issue(
                                f"Ciclo {cycle_id}: phi_before fora do range: {phi_before}"
                            )
                    if phi_after is not None:
                        if not (0 <= phi_after <= 1):
                            self.log_issue(
                                f"Ciclo {cycle_id}: phi_after fora do range: {phi_after}"
                            )

                    # Verificar se rollback foi necessário
                    if (
                        phi_before is not None
                        and phi_after is not None
                        and phi_after < 0.3
                        and len(cycle.get("synthesized_components", [])) > 0
                    ):
                        self.log_warning(
                            f"Ciclo {cycle_id}: Rollback necessário (Φ {phi_before:.3f} -> {phi_after:.3f})"
                        )
            else:
                self.log_warning("Nenhum ciclo encontrado no histórico")

        except Exception as e:
            self.log_issue(f"Erro ao validar ciclos autopoiéticos: {e}")

    def validate_training_sessions(self) -> None:
        """Valida sessões de treinamento."""
        logger.info("=" * 70)
        logger.info("VALIDANDO SESSÕES DE TREINAMENTO")
        logger.info("=" * 70)

        # Verificar se há dados de treinamento
        training_dirs = [
            "data/training",
            "data/sessions",
            "real_evidence",
        ]

        for dir_path in training_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                files = list(full_path.glob("*.json"))
                if files:
                    self.log_pass(f"Encontrados {len(files)} arquivos em {dir_path}")
                else:
                    self.log_warning(f"Diretório {dir_path} existe mas está vazio")
            else:
                self.log_warning(f"Diretório de treinamento não encontrado: {dir_path}")

        # Verificar scripts de validação científica
        validation_scripts = list(
            (self.project_root / "scripts" / "science_validation").glob("*.py")
        )
        if validation_scripts:
            self.log_pass(f"Encontrados {len(validation_scripts)} scripts de validação")
        else:
            self.log_warning("Nenhum script de validação científica encontrado")

    def validate_consistency(self) -> None:
        """Valida consistência entre diferentes implementações."""
        logger.info("=" * 70)
        logger.info("VALIDANDO CONSISTÊNCIA")
        logger.info("=" * 70)

        # Verificar se há valores de Φ inconsistentes
        metrics_path = self.project_root / "data" / "monitor" / "real_metrics.json"
        history_path = self.project_root / "data" / "autopoietic" / "cycle_history.jsonl"

        if metrics_path.exists() and history_path.exists():
            try:
                with metrics_path.open("r", encoding="utf-8") as f:
                    current_metrics = json.load(f)
                    current_phi = current_metrics.get("phi", 0.0)

                with history_path.open("r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                    if lines:
                        last_cycle = json.loads(lines[-1])
                        last_phi_after = last_cycle.get("phi_after")

                        if last_phi_after is not None:
                            diff = abs(float(current_phi) - float(last_phi_after))
                            if diff > 0.5:
                                self.log_warning(
                                    f"Grande diferença entre Φ atual ({current_phi:.4f}) "
                                    f"e último ciclo ({last_phi_after:.4f}): {diff:.4f}"
                                )
                            else:
                                self.log_pass(
                                    f"Φ consistente: atual={current_phi:.4f}, "
                                    f"último={last_phi_after:.4f}"
                                )
            except Exception as e:
                self.log_warning(f"Erro ao verificar consistência: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório final."""
        total_checks = len(self.passed) + len(self.warnings) + len(self.issues)
        success_rate = (len(self.passed) / total_checks * 100) if total_checks > 0 else 0

        report = {
            "summary": {
                "total_checks": total_checks,
                "passed": len(self.passed),
                "warnings": len(self.warnings),
                "issues": len(self.issues),
                "success_rate": success_rate,
            },
            "passed": self.passed,
            "warnings": self.warnings,
            "issues": self.issues,
        }

        return report

    def print_summary(self) -> None:
        """Imprime resumo final."""
        logger.info("=" * 70)
        logger.info("RESUMO DA VALIDAÇÃO")
        logger.info("=" * 70)
        logger.info(f"✅ Passou: {len(self.passed)}")
        logger.info(f"⚠️  Avisos: {len(self.warnings)}")
        logger.info(f"❌ Problemas: {len(self.issues)}")

        if self.issues:
            logger.info("\nPROBLEMAS CRÍTICOS:")
            for issue in self.issues:
                logger.info(f"  - {issue}")

        if self.warnings:
            logger.info("\nAVISOS:")
            for warning in self.warnings:
                logger.info(f"  - {warning}")


def main():
    """Função principal."""
    project_root = Path(__file__).parent.parent

    validator = MetricsValidator(project_root)

    # Executar todas as validações
    validator.validate_phi_calculations()
    validator.validate_real_metrics()
    validator.validate_autopoietic_cycles()
    validator.validate_training_sessions()
    validator.validate_consistency()

    # Gerar relatório
    report = validator.generate_report()
    validator.print_summary()

    # Salvar relatório
    report_path = project_root / "data" / "validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"\nRelatório salvo em: {report_path}")

    # Exit code baseado em problemas críticos
    if validator.issues:
        sys.exit(1)
    elif validator.warnings:
        sys.exit(0)  # Warnings não são fatais
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
