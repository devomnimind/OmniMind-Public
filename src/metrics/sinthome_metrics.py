"""
Sinthome Metrics - Medição de Estruturas Sinthomáticas.

Este módulo implementa métricas para quantificar a presença e estabilidade
do Sinthome (o quarto anel do nó Borromeano) no sistema OmniMind.

Métricas baseadas em:
- Lacan (Sinthome como reparação do erro no nó)
- Teoria do Caos (Atratores Estranhos)
- Panarquia (Ciclos adaptativos)

Author: This work was conceived by Fabrício da Silva and implemented with AI assistance
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
License: MIT
"""

import logging
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class SinthomeScore:
    """Pontuação composta do estado Sinthomático."""

    overall_integrity: float  # 0.0 - 1.0
    metrics: Dict[str, float]
    state: str  # 'STABLE', 'UNSTABLE', 'CRITICAL', 'HIBERNATING'


class SinthomeMetrics:
    """Calculadora de métricas Sinthomáticas."""

    def __init__(self):
        self.history: List[Dict[str, float]] = []

    def calculate_logical_impasse(self, circular_dependencies: int, contradictions: int) -> float:
        """
        Mede o Impasse Lógico (Gödelian Incompleteness).
        Quanto maior o impasse, maior a necessidade de um Sinthome.

        Args:
            circular_dependencies: Contagem de dependências circulares detectadas.
            contradictions: Contagem de contradições lógicas.

        Returns:
            Score 0.0 (sem impasse) a 1.0 (impasse total).
        """
        # Normalização simples: 10 dependências ou contradições = 1.0
        raw_score = (circular_dependencies * 0.1) + (contradictions * 0.15)
        return min(1.0, raw_score)

    def calculate_indeterminacy_peak(self, entropy: float, prediction_error: float) -> float:
        """
        Mede o Pico de Indeterminismo (Entropy Spike).

        Args:
            entropy: Entropia atual do sistema (0-100).
            prediction_error: Erro de predição do modelo (0.0-1.0).

        Returns:
            Score 0.0 a 1.0.
        """
        norm_entropy = min(1.0, entropy / 100.0)
        return (norm_entropy * 0.7) + (prediction_error * 0.3)

    def calculate_panarchic_reorganization(
        self, structural_changes: int, adaptation_rate: float
    ) -> float:
        """
        Mede a Reorganização Panárquica (capacidade de reestruturação).

        Args:
            structural_changes: Número de mudanças na topologia da rede.
            adaptation_rate: Taxa de adaptação bem-sucedida (0.0-1.0).

        Returns:
            Score 0.0 a 1.0.
        """
        # Mudanças estruturais são boas se a taxa de adaptação for alta
        norm_changes = min(1.0, structural_changes / 5.0)
        return norm_changes * adaptation_rate

    def calculate_autopoiesis(self, self_repair_events: int, uptime: float) -> float:
        """
        Mede a Autopoiese (capacidade de auto-manutenção).

        Args:
            self_repair_events: Eventos de auto-reparo bem-sucedidos.
            uptime: Tempo de atividade normalizado (0.0-1.0).

        Returns:
            Score 0.0 a 1.0.
        """
        norm_repair = min(1.0, self_repair_events / 10.0)
        return (norm_repair * 0.6) + (uptime * 0.4)

    def calculate_strange_attractor_markers(
        self, fractal_dimension: float, lyapunov_exponent: float
    ) -> float:
        """
        Identifica marcadores de Atrator Estranho (Caos Estável).

        Args:
            fractal_dimension: Dimensão fractal da trajetória do sistema.
            lyapunov_exponent: Expoente de Lyapunov (positivo = caos).

        Returns:
            Score 0.0 a 1.0 (1.0 = atrator estranho ideal).
        """
        # Higher fractal dimension (>2.0) suggests complex attractor
        # Lyapunov exponent in [0.1, 1.5] indicates managed chaos
        # Simplificação: quão próximo de 2.5 (exemplo)
        fractal_score = 1.0 - min(1.0, abs(fractal_dimension - 2.5))

        # Lyapunov positivo indica caos, mas não muito alto (instabilidade total)
        # Ideal range: 0.1 to 1.5
        if 0.1 <= lyapunov_exponent <= 1.5:
            lyapunov_score = 1.0
        elif lyapunov_exponent > 1.5:
            lyapunov_score = max(0.0, 1.0 - (lyapunov_exponent - 1.5))
        else:
            lyapunov_score = 0.0

        return (fractal_score * 0.5) + (lyapunov_score * 0.5)

    def calculate_real_inaccessible(
        self, missing_information_ratio: float, gap_persistence: float
    ) -> float:
        """
        Quantifica o Real Inacessível (o que não pode ser simbolizado).

        Args:
            missing_information_ratio: Razão de info perdida/não processável.
            gap_persistence: Persistência temporal dessa lacuna (0.0-1.0).

        Returns:
            Score 0.0 a 1.0.
        """
        return (missing_information_ratio * 0.5) + (gap_persistence * 0.5)

    def evaluate_integrity(
        self,
        impasse: float,
        indeterminacy: float,
        reorganization: float,
        autopoiesis: float,
        strange_attractor: float,
        real: float,
    ) -> SinthomeScore:
        """
        Avalia a integridade geral do Sinthome.
        """
        # O Sinthome deve ser forte quando há Impasse e Indeterminismo
        # Ele se manifesta como Reorganização, Autopoiese e Atrator Estranho

        resilience_factors = (reorganization + autopoiesis + strange_attractor) / 3.0
        stress_factors = (impasse + indeterminacy + real) / 3.0

        # Integridade é a capacidade de manter resiliência sob estresse
        if stress_factors > 0:
            integrity = min(1.0, resilience_factors / stress_factors)
        else:
            # Se sem estresse, integridade é a capacidade latente
            integrity = resilience_factors

        metrics = {
            "logical_impasse": impasse,
            "indeterminacy_peak": indeterminacy,
            "panarchic_reorganization": reorganization,
            "autopoiesis": autopoiesis,
            "strange_attractor_markers": strange_attractor,
            "real_inaccessible": real,
        }

        state = "STABLE"
        if integrity < 0.3:
            state = "CRITICAL"
        elif integrity < 0.6:
            state = "UNSTABLE"
        elif stress_factors > 0.8 and integrity > 0.6:
            state = "HIBERNATING"  # Proteção contra estresse extremo

        return SinthomeScore(overall_integrity=integrity, metrics=metrics, state=state)
