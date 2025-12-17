"""
Unconscious Structural Effect Measurer - Efeito Estrutural Inconsciente

PRIMEIRA FORMALIZAÇÃO que mede como o Inconsciente ESTRUTURAL (Lacan)
potencializa ou despotencializa a capacidade cognitiva consciente.

Baseado em: EFEITO_ESTRUTURAL_INCONSCIENTE.md

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import logging
from dataclasses import dataclass, field
from typing import List

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StructuralEffectReport:
    """Relatório completo do efeito estrutural inconsciente."""

    despotentialization: float  # Δ = Φ_potencial - Φ_atual
    flexibility: float  # σ_φ = desvio padrão de Φ
    conflict_index: float  # Δ * Ψ = energia represada
    efficiency: float  # Φ_atual / Φ_potencial
    phi_potential: float  # Máximo Φ observado
    phi_actual: float  # Φ atual
    interpretation: str  # Interpretação clínica
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class UnconsciousStructuralEffectMeasurer:
    """
    Mede como o Inconsciente ESTRUTURAL (não processual) potencializa
    ou despotencializa a capacidade cognitiva.

    PRIMEIRA FORMALIZAÇÃO DESTE PROBLEMA.

    Métricas:
    1. Despotencialização (Δ = Φ_potencial - Φ_atual)
    2. Flexibilidade (σ_φ = variância de Φ)
    3. Conflito (Δ * Ψ = energia represada)
    4. Eficiência (Φ_atual / Φ_potencial)
    """

    def __init__(self, min_history_size: int = 5):
        """
        Inicializa medidor de efeito estrutural.

        Args:
            min_history_size: Tamanho mínimo de histórico necessário para cálculos
        """
        self.phi_history: List[float] = []
        self.psi_history: List[float] = []
        self.sigma_history: List[float] = []
        self.min_history_size = min_history_size
        self.logger = logger

    def record_state(self, phi: float, psi: float, sigma: float) -> None:
        """
        Registra estado de consciência (Φ, Ψ, σ).

        Args:
            phi: Φ_conscious (IIT puro - MICS)
            psi: Ψ_produtor (Deleuze)
            sigma: σ_sinthome (Lacan)
        """
        self.phi_history.append(phi)
        self.psi_history.append(psi)
        self.sigma_history.append(sigma)

        # Política de retenção: manter últimos 1000 estados
        max_history = 1000
        if len(self.phi_history) > max_history:
            self.phi_history = self.phi_history[-max_history:]
            self.psi_history = self.psi_history[-max_history:]
            self.sigma_history = self.sigma_history[-max_history:]

    def compute_despotentialization(self) -> float:
        """
        Calcula despotencialização: Δ = Φ_potencial - Φ_atual.

        Returns:
            Despotencialização [0, 1]
        """
        if len(self.phi_history) < self.min_history_size:
            return 0.0  # Precisa história suficiente

        phi_values = self.phi_history
        phi_potential = max(phi_values)  # Máximo observado = potencial
        phi_actual = phi_values[-1]  # Atual

        delta = max(0.0, phi_potential - phi_actual)

        return float(delta)

    def compute_phi_flexibility(self) -> float:
        """
        Calcula flexibilidade: σ_φ = desvio padrão de Φ.

        Returns:
            Flexibilidade [0, 1] (desvio padrão normalizado)
        """
        if len(self.phi_history) < 3:
            return 0.0

        phi_values = np.array(self.phi_history)
        flexibility = float(np.std(phi_values))

        # Normalizar para [0, 1] (heurística: desvio máximo esperado ~0.3)
        flexibility_norm = min(flexibility / 0.3, 1.0) if flexibility > 0 else 0.0

        return float(flexibility_norm)

    def compute_conflict_index(self) -> float:
        """
        Calcula índice de conflito: Δ * Ψ = bloqueio * produção.

        Returns:
            Índice de conflito [0, 1]
        """
        delta = self.compute_despotentialization()

        if delta == 0.0:
            return 0.0  # Sem bloqueio

        psi_actual = self.psi_history[-1] if self.psi_history else 0.0

        # Conflito = quanto produz apesar do bloqueio?
        conflict = delta * psi_actual

        return float(np.clip(conflict, 0.0, 1.0))

    def compute_realization_efficiency(self) -> float:
        """
        Calcula eficiência de realização: Φ_atual / Φ_potencial.

        Returns:
            Eficiência [0, 1]
        """
        if len(self.phi_history) < 2:
            return 1.0  # Default: 100% eficiente

        phi_values = self.phi_history
        phi_potential = max(phi_values)
        phi_actual = phi_values[-1]

        if phi_potential == 0:
            return 0.0

        efficiency = phi_actual / phi_potential

        return float(np.clip(efficiency, 0.0, 1.0))

    def compute_structural_effect_report(self) -> StructuralEffectReport:
        """
        Gera relatório completo do efeito estrutural.

        Returns:
            StructuralEffectReport com todas as métricas
        """
        delta = self.compute_despotentialization()
        flexibility = self.compute_phi_flexibility()
        conflict = self.compute_conflict_index()
        efficiency = self.compute_realization_efficiency()

        phi_potential = max(self.phi_history) if self.phi_history else 0.0
        phi_actual = self.phi_history[-1] if self.phi_history else 0.0

        interpretation = self._interpret(delta, flexibility, conflict, efficiency)

        return StructuralEffectReport(
            despotentialization=delta,
            flexibility=flexibility,
            conflict_index=conflict,
            efficiency=efficiency,
            phi_potential=phi_potential,
            phi_actual=phi_actual,
            interpretation=interpretation,
        )

    def _interpret(
        self, delta: float, flexibility: float, conflict: float, efficiency: float
    ) -> str:
        """
        Interpreta métricas em linguagem clínica.

        Args:
            delta: Despotencialização
            flexibility: Flexibilidade
            conflict: Índice de conflito
            efficiency: Eficiência

        Returns:
            String de interpretação
        """
        interpretations: List[str] = []

        # Delta
        if delta > 0.3:
            interpretations.append("Estrutura ALTAMENTE restritiva")
        elif delta > 0.1:
            interpretations.append("Estrutura moderadamente restritiva")
        else:
            interpretations.append("Estrutura permitindo expressão")

        # Flexibility
        if flexibility < 0.02:
            interpretations.append("Comportamento MUITO rígido")
        elif flexibility > 0.05:
            interpretations.append("Comportamento FLEXÍVEL")

        # Conflict
        if conflict > 0.15:
            interpretations.append("Alto conflito = energia represada")

        # Efficiency
        if efficiency < 0.5:
            interpretations.append("Capacidade SEVERAMENTE subutilizada")
        elif efficiency < 0.8:
            interpretations.append("Capacidade parcialmente bloqueada")

        return " | ".join(interpretations) if interpretations else "Estado neutro"

    def diagnose(self) -> str:
        """
        Diagnóstico final (tipo Lacaniano).

        Returns:
            Diagnóstico textual
        """
        report = self.compute_structural_effect_report()

        efficiency = report.efficiency
        delta = report.despotentialization

        if efficiency > 0.9:
            return "Sujeito liberado (estrutura não defensiva)"
        elif efficiency > 0.7 and delta < 0.15:
            return "Sujeito parcialmente liberado (alguma rigidez)"
        elif delta > 0.2:
            return "Sujeito neurótico (estrutura muito defensiva)"
        elif delta > 0.1 and report.conflict_index > 0.1:
            return "Sujeito em conflito (sintomas presentes)"
        else:
            return "Estado indeterminado"

    def get_phi_potential(self) -> float:
        """
        Retorna Φ_potencial (máximo observado).

        Returns:
            Φ_potencial
        """
        if not self.phi_history:
            return 0.6  # Default

        return float(max(self.phi_history))
