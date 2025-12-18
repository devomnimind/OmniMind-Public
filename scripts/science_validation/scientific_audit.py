#!/usr/bin/env python3
"""
AUDITORIA CIENTÍFICA RIGOROSA - SUPERVISÃO CETÍCA

Como supervisor científico, questiona:
1. Consistência matemática dos cálculos
2. Validade estatística dos resultados
3. Robustez das implementações
4. Integridade dos dados
5. Possíveis hardcodings ou valores fixos

Detecta:
- Cálculos suspeitos (variância zero, valores fixos)
- Inconsistências entre implementações
- Falhas de validação
- Dados corrompidos ou inválidos
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ScientificAuditor:
    """Auditor científico cético."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.critical_findings: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []

    def audit_phi_implementations(self) -> Dict[str, Any]:
        """Audita todas as implementações de Φ."""
        logger.info("=" * 80)
        logger.info("AUDITORIA: IMPLEMENTAÇÕES DE Φ")
        logger.info("=" * 80)

        findings = {
            "implementations": [],
            "inconsistencies": [],
            "hardcoding_suspected": [],
        }

        # 1. Verificar topological_phi
        try:
            import sys

            if str(self.project_root / "src") not in sys.path:
                sys.path.insert(0, str(self.project_root / "src"))
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))
            from src.consciousness.topological_phi import PhiCalculator, SimplicialComplex

            # Teste com diferentes configurações
            test_cases = [
                ([(0,), (1,), (0, 1)], "2 vértices, 1 aresta"),
                ([(0,), (1,), (2,), (0, 1), (1, 2)], "3 vértices, 2 arestas"),
            ]

            phi_values = []
            for simplices, desc in test_cases:
                complex = SimplicialComplex()
                for s in simplices:
                    complex.add_simplex(s)
                calc = PhiCalculator(complex)
                phi = calc.calculate_phi()
                phi_values.append(phi)
                logger.info(f"  Topological Φ ({desc}): {phi:.6f}")

            # Verificar se há variação (não hardcoded)
            if len(set(phi_values)) == 1 and phi_values[0] > 0:
                self.warnings.append("Topological Φ pode estar hardcoded (valores idênticos)")
                findings["hardcoding_suspected"].append("topological_phi")

        except Exception as e:
            self.critical_findings.append(f"Erro ao auditar topological_phi: {e}")
            findings["inconsistencies"].append(f"topological_phi: {e}")

        # 2. Verificar integration_loop
        try:
            import sys

            if str(self.project_root / "src") not in sys.path:
                sys.path.insert(0, str(self.project_root / "src"))
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))
            from src.consciousness.integration_loop import IntegrationLoop

            loop = IntegrationLoop(enable_logging=False)
            # Verificar se workspace existe
            if hasattr(loop, "workspace"):
                logger.info("  IntegrationLoop: workspace presente")
            else:
                self.critical_findings.append("IntegrationLoop sem workspace")

        except Exception as e:
            self.critical_findings.append(f"Erro ao auditar integration_loop: {e}")

        # 3. Verificar shared_workspace compute_phi
        try:
            import sys

            if str(self.project_root / "src") not in sys.path:
                sys.path.insert(0, str(self.project_root / "src"))
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))
            from src.consciousness.shared_workspace import SharedWorkspace

            workspace = SharedWorkspace()
            # Testar com workspace vazio
            phi_empty = workspace.compute_phi_from_integrations()
            logger.info(f"  SharedWorkspace Φ (vazio): {phi_empty:.6f}")

            if phi_empty != 0.0:
                self.warnings.append(
                    f"SharedWorkspace retorna Φ={phi_empty:.6f} para workspace vazio (esperado 0.0)"
                )

        except Exception as e:
            self.critical_findings.append(f"Erro ao auditar shared_workspace: {e}")

        return findings

    def audit_training_data(self) -> Dict[str, Any]:
        """Audita dados de treinamento e sessões."""
        logger.info("=" * 80)
        logger.info("AUDITORIA: DADOS DE TREINAMENTO")
        logger.info("=" * 80)

        findings = {
            "sessions_found": 0,
            "sessions_valid": 0,
            "anomalies": [],
        }

        sessions_dir = self.project_root / "data" / "sessions"
        if not sessions_dir.exists():
            self.warnings.append("Diretório de sessões não existe - criando")
            sessions_dir.mkdir(parents=True, exist_ok=True)
            return findings

        session_files = list(sessions_dir.glob("*.json"))
        findings["sessions_found"] = len(session_files)

        for session_file in session_files:
            try:
                with session_file.open("r", encoding="utf-8") as f:
                    session = json.load(f)

                # Validar estrutura
                required_fields = ["session_id", "total_cycles", "statistics"]
                missing = [f for f in required_fields if f not in session]
                if missing:
                    findings["anomalies"].append(f"{session_file.name}: campos faltando {missing}")
                    continue

                # Validar estatísticas
                stats = session.get("statistics", {})
                phi_stats = stats.get("phi_after", {})
                if phi_stats:
                    mean = phi_stats.get("mean", 0)
                    stdev = phi_stats.get("stdev", 0)

                    # Verificar se variância é suspeitamente baixa
                    if stdev < 0.0001 and mean > 0:
                        findings["anomalies"].append(
                            f"{session_file.name}: variância muito baixa (possível hardcoding)"
                        )

                findings["sessions_valid"] += 1

            except Exception as e:
                findings["anomalies"].append(f"{session_file.name}: erro {e}")

        logger.info(f"  Sessões encontradas: {findings['sessions_found']}")
        logger.info(f"  Sessões válidas: {findings['sessions_valid']}")
        if findings["anomalies"]:
            logger.warning(f"  Anomalias: {len(findings['anomalies'])}")

        return findings

    def audit_real_metrics(self) -> Dict[str, Any]:
        """Audita métricas reais com ceticismo."""
        logger.info("=" * 80)
        logger.info("AUDITORIA: MÉTRICAS REAIS")
        logger.info("=" * 80)

        findings = {
            "metrics_file_exists": False,
            "all_zero": False,
            "suspicious_values": [],
        }

        metrics_path = self.project_root / "data" / "monitor" / "real_metrics.json"
        if not metrics_path.exists():
            self.warnings.append("Arquivo de métricas reais não encontrado")
            return findings

        findings["metrics_file_exists"] = True

        try:
            with metrics_path.open("r", encoding="utf-8") as f:
                metrics = json.load(f)

            # Verificar se todas as métricas são zero (sistema não executado)
            all_values = [
                float(metrics.get("phi", 0)),
                float(metrics.get("anxiety", 0)),
                float(metrics.get("flow", 0)),
                float(metrics.get("entropy", 0)),
                float(metrics.get("ici", 0)),
                float(metrics.get("prs", 0)),
            ]

            if all(v == 0.0 for v in all_values):
                findings["all_zero"] = True
                self.warnings.append(
                    "Todas as métricas estão em zero - sistema pode não estar executando"
                )

            # Verificar valores suspeitos
            phi = float(metrics.get("phi", 0))
            if phi < 0 or phi > 1:
                findings["suspicious_values"].append(f"phi fora do range: {phi}")
                self.critical_findings.append(f"Φ inválido: {phi}")

            # Verificar se há NaN ou Inf
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        findings["suspicious_values"].append(f"{key} é NaN/Inf")
                        self.critical_findings.append(f"{key} inválido: {value}")

        except Exception as e:
            self.critical_findings.append(f"Erro ao auditar métricas: {e}")

        return findings

    def generate_audit_report(self) -> Dict[str, Any]:
        """Gera relatório completo de auditoria."""
        report = {
            "timestamp": str(datetime.now()),
            "auditor": "ScientificSupervisor",
            "critical_findings": self.critical_findings,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "phi_audit": self.audit_phi_implementations(),
            "training_audit": self.audit_training_data(),
            "metrics_audit": self.audit_real_metrics(),
        }

        # Gerar recomendações
        if self.critical_findings:
            self.recommendations.append("Corrigir problemas críticos antes de prosseguir")
        metrics_audit = self.audit_real_metrics()
        if metrics_audit.get("all_zero"):
            self.recommendations.append("Executar sistema para coletar métricas reais")
        phi_audit = self.audit_phi_implementations()
        if phi_audit.get("hardcoding_suspected"):
            self.recommendations.append("Investigar possíveis hardcodings em cálculos de Φ")

        report["recommendations"] = self.recommendations

        return report


def main():
    """Função principal."""

    project_root = Path(__file__).parent.parent.parent
    auditor = ScientificAuditor(project_root)

    logger.info("🔬 INICIANDO AUDITORIA CIENTÍFICA RIGOROSA")
    logger.info("=" * 80)

    report = auditor.generate_audit_report()

    # Salvar relatório
    reports_dir = project_root / "data" / "validation"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / f"scientific_audit_{int(time.time())}.json"

    with report_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Imprimir resumo
    logger.info("=" * 80)
    logger.info("RESUMO DA AUDITORIA")
    logger.info("=" * 80)
    logger.info(f"Problemas críticos: {len(auditor.critical_findings)}")
    logger.info(f"Avisos: {len(auditor.warnings)}")
    logger.info(f"Recomendações: {len(auditor.recommendations)}")
    logger.info(f"\nRelatório: {report_file}")

    if auditor.critical_findings:
        logger.error("\nPROBLEMAS CRÍTICOS ENCONTRADOS:")
        for finding in auditor.critical_findings:
            logger.error(f"  - {finding}")

    if auditor.warnings:
        logger.warning("\nAVISOS:")
        for warning in auditor.warnings:
            logger.warning(f"  - {warning}")

    # Exit code
    sys.exit(1 if auditor.critical_findings else 0)


if __name__ == "__main__":
    import time
    from datetime import datetime

    main()
