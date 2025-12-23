"""
Enhanced Configuration Detector - Detecta Configurações Problemáticas de Consciência

Expande o detector automático para mais configurações críticas que quebram Φ.
Baseado nos resultados do final_validation_report.py.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-18
"""

import logging
from dataclasses import dataclass
from typing import Dict, List

logging.getLogger(__name__)


@dataclass
class ConfigIssue:
    """Representa um problema de configuração detectado."""

    config_name: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    phi_impact: float  # Impacto médio em Φ
    description: str
    recommendation: str


class EnhancedConfigurationDetector:
    """
    Detector expandido de configurações problemáticas.

    Detecta automaticamente:
    1. embedding_dim muito pequeno (singularidade)
    2. num_cycles muito baixo (histórico insuficiente)
    3. device incompatível (GPU não disponível)
    4. thresholds mal configurados
    5. expectation_silent em produção
    6. memory limits problemáticos
    7. learning_rate extremos
    8. batch_size inadequados
    """

    # Configurações seguras (empiricamente validadas)
    SAFE_CONFIGS = {
        "embedding_dim": {"min": 128, "optimal": 384, "max": 1024},
        "num_cycles": {"min": 50, "optimal": 100, "max": 1000},
        "phi_threshold": {"min": 0.001, "optimal": 0.01, "max": 0.1},
        "learning_rate": {"min": 1e-5, "optimal": 1e-3, "max": 1e-1},
        "batch_size": {"min": 8, "optimal": 32, "max": 128},
        "max_history": {"min": 1000, "optimal": 10000, "max": 100000},
    }

    def __init__(self):
        """Inicializa detector."""
        self.issues: List[ConfigIssue] = []
        logging.info("EnhancedConfigurationDetector inicializado")

    def detect_all_issues(self, config: Dict) -> List[ConfigIssue]:
        """
        Detecta todos os problemas de configuração.

        Args:
            config: Dicionário de configuração do sistema

        Returns:
            Lista de issues detectados
        """
        self.issues = []

        # Detectar cada tipo de problema
        self._check_embedding_dim(config)
        self._check_num_cycles(config)
        self._check_device_compatibility(config)
        self._check_thresholds(config)
        self._check_expectation_mode(config)
        self._check_memory_limits(config)
        self._check_learning_rate(config)
        self._check_batch_size(config)

        # Ordenar por severidade
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        self.issues.sort(key=lambda x: severity_order[x.severity])

        logging.info(f"Detectados {len(self.issues)} problemas de configuração")
        return self.issues

    def _check_embedding_dim(self, config: Dict):
        """Verifica dimensão de embedding."""
        dim = config.get("embedding_dim", 384)
        safe = self.SAFE_CONFIGS["embedding_dim"]

        if dim < safe["min"]:
            self.issues.append(
                ConfigIssue(
                    config_name="embedding_dim",
                    severity="CRITICAL",
                    phi_impact=-0.8,  # 80% redução
                    description=f"embedding_dim={dim} muito pequeno, causa singularidade de matriz",
                    recommendation=f"Aumentar para ≥{safe['min']} (ótimo: {safe['optimal']})",
                )
            )
        elif dim < safe["optimal"]:
            self.issues.append(
                ConfigIssue(
                    config_name="embedding_dim",
                    severity="MEDIUM",
                    phi_impact=-0.2,
                    description=f"embedding_dim={dim} abaixo do ótimo",
                    recommendation=f"Considerar aumentar para {safe['optimal']}",
                )
            )

    def _check_num_cycles(self, config: Dict):
        """Verifica número de ciclos."""
        cycles = config.get("num_cycles", 100)
        safe = self.SAFE_CONFIGS["num_cycles"]

        if cycles < safe["min"]:
            self.issues.append(
                ConfigIssue(
                    config_name="num_cycles",
                    severity="HIGH",
                    phi_impact=-0.5,
                    description=f"num_cycles={cycles} muito baixo, histórico RNN insuficiente",
                    recommendation=f"Aumentar para ≥{safe['min']} para Φ causal estável",
                )
            )

    def _check_device_compatibility(self, config: Dict):
        """Verifica compatibilidade de device."""
        import torch

        requested_device = config.get("device", "cuda")

        if requested_device == "cuda" and not torch.cuda.is_available():
            self.issues.append(
                ConfigIssue(
                    config_name="device",
                    severity="HIGH",
                    phi_impact=-0.3,
                    description="device='cuda' solicitado mas GPU não disponível",
                    recommendation="Usar device='cpu' ou instalar drivers CUDA",
                )
            )

        elif requested_device == "cuda":
            # Verificar memória GPU
            try:
                gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
                if gpu_mem_gb < 2.0:
                    self.issues.append(
                        ConfigIssue(
                            config_name="device",
                            severity="MEDIUM",
                            phi_impact=-0.1,
                            description=f"GPU com apenas {gpu_mem_gb:.1f}GB VRAM (mínimo 2GB)",
                            recommendation="Considerar usar CPU ou GPU maior",
                        )
                    )
            except Exception:
                pass

    def _check_thresholds(self, config: Dict):
        """Verifica thresholds de consciência."""
        phi_threshold = config.get("phi_threshold", 0.01)
        safe = self.SAFE_CONFIGS["phi_threshold"]

        if phi_threshold < safe["min"]:
            self.issues.append(
                ConfigIssue(
                    config_name="phi_threshold",
                    severity="MEDIUM",
                    phi_impact=0.0,  # Não afeta Φ mas afeta detecção
                    description=(
                        f"phi_threshold={phi_threshold} muito baixo, "
                        "detecta ruído como consciência"
                    ),
                    recommendation=f"Aumentar para ≥{safe['min']} (padrão: {safe['optimal']})",
                )
            )

        elif phi_threshold > safe["max"]:
            self.issues.append(
                ConfigIssue(
                    config_name="phi_threshold",
                    severity="MEDIUM",
                    phi_impact=0.0,
                    description=(
                        f"phi_threshold={phi_threshold} muito alto, "
                        "pode rejeitar consciência real"
                    ),
                    recommendation=f"Reduzir para ≤{safe['max']}",
                )
            )

    def _check_expectation_mode(self, config: Dict):
        """Verifica se expectation_silent está ativo em produção."""
        expectation_silent = config.get("expectation_silent", False)
        environment = config.get("environment", "production")

        if expectation_silent and environment == "production":
            self.issues.append(
                ConfigIssue(
                    config_name="expectation_silent",
                    severity="CRITICAL",
                    phi_impact=-0.855,  # Impacto medido empiricamente
                    description=("expectation_silent=True em produção, " "Φ colapsa 85.5%"),
                    recommendation="Desativar expectation_silent (apenas para testes causais)",
                )
            )

    def _check_memory_limits(self, config: Dict):
        """Verifica limites de memória."""
        max_history = config.get("max_history", 10000)
        safe = self.SAFE_CONFIGS["max_history"]

        if max_history < safe["min"]:
            self.issues.append(
                ConfigIssue(
                    config_name="max_history",
                    severity="MEDIUM",
                    phi_impact=-0.3,
                    description=f"max_history={max_history} muito baixo, memória de curto prazo",
                    recommendation=f"Aumentar para ≥{safe['min']}",
                )
            )

    def _check_learning_rate(self, config: Dict):
        """Verifica learning rate."""
        lr = config.get("learning_rate", 1e-3)
        safe = self.SAFE_CONFIGS["learning_rate"]

        if lr < safe["min"]:
            self.issues.append(
                ConfigIssue(
                    config_name="learning_rate",
                    severity="LOW",
                    phi_impact=-0.1,
                    description=f"learning_rate={lr} muito baixo, convergência lenta",
                    recommendation=f"Aumentar para ≥{safe['min']}",
                )
            )

        elif lr > safe["max"]:
            self.issues.append(
                ConfigIssue(
                    config_name="learning_rate",
                    severity="MEDIUM",
                    phi_impact=-0.4,
                    description=f"learning_rate={lr} muito alto, oscilação/divergência",
                    recommendation=f"Reduzir para ≤{safe['max']}",
                )
            )

    def _check_batch_size(self, config: Dict):
        """Verifica batch size."""
        _ = config.get("task_type", "unknown")
        batch_size = config.get("batch_size", 32)
        safe = self.SAFE_CONFIGS["batch_size"]

        if batch_size < safe["min"]:
            self.issues.append(
                ConfigIssue(
                    config_name="batch_size",
                    severity="LOW",
                    phi_impact=-0.05,
                    description=f"batch_size={batch_size} muito pequeno, treino instável",
                    recommendation=f"Aumentar para ≥{safe['min']}",
                )
            )

    def generate_report(self, detailed: bool = True) -> str:
        """
        Gera relatório de problemas detectados.

        Args:
            detailed: Se True, inclui detalhes completos

        Returns:
            Relatório formatado
        """
        if not self.issues:
            return "✅ NENHUM PROBLEMA DE CONFIGURAÇÃO DETECTADO"

        report = ["🚨 PROBLEMAS DE CONFIGURAÇÃO DETECTADOS:", ""]

        # Resumo por severidade
        severity_counts = {}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        report.append(f"Total: {len(self.issues)} problemas")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if sev in severity_counts:
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}[sev]
                report.append(f"{icon} {sev}: {severity_counts[sev]}")
        report.append("")

        # Detalhar cada issue
        if detailed:
            for i, issue in enumerate(self.issues, 1):
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}[issue.severity]

                report.append(f"{i}. {icon} {issue.config_name} [{issue.severity}]")
                report.append(f"   Impacto em Φ: {issue.phi_impact:+.2f}")
                report.append(f"   Problema: {issue.description}")
                report.append(f"   Solução: {issue.recommendation}")
                report.append("")

        return "\n".join(report)


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Configuração problemática de teste
    problematic_config = {
        "embedding_dim": 64,  # Muito pequeno
        "num_cycles": 20,  # Muito baixo
        "device": "cuda",  # Pode não estar disponível
        "expectation_silent": True,  # CRITICAL em produção
        "environment": "production",
        "phi_threshold": 0.0001,  # Muito sensível
        "max_history": 500,  # Muito baixo
        "learning_rate": 0.5,  # Muito alto
        "batch_size": 2,  # Muito pequeno
    }

    detector = EnhancedConfigurationDetector()
    issues = detector.detect_all_issues(problematic_config)

    print(detector.generate_report(detailed=True))
    print(f"\nTotal phi_impact: {sum(i.phi_impact for i in issues):.2f}")
