"""
Consciousness Triad (Φ, Ψ, σ) - Estrutura Unificada Ortogonal

Implementa a tríade ortogonal de consciência:
- Φ (IIT): Integração (ordem)
- Ψ (Deleuze): Produção (criatividade/caos)
- σ (Lacan): Amarração (estrutura/estabilidade)

As três dimensões são ORTOGONAIS (independentes):
- Não são aditivas: Φ + Ψ + σ ≠ "consciência total"
- São complementares: cada uma captura um aspecto diferente
- São ortogonais: mudanças em uma não afetam diretamente as outras

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
Baseado em: PLANO_IMPLEMENTACAO_LACUNA_PHI.md
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessTriad:
    """
    Tríade ortogonal de consciência (Φ, Ψ, σ).

    Características:
    - Ortogonalidade: dimensões independentes
    - Não-aditividade: não somam para "consciência total"
    - Complementaridade: cada uma captura aspecto diferente
    """

    phi: float  # Φ_conscious (IIT puro - MICS) [0, 1]
    psi: float  # Ψ_produtor (Deleuze) [0, 1]
    sigma: float  # σ_sinthome (Lacan) [0, 1]
    step_id: str  # ID único do passo/ciclo
    timestamp: float = field(default_factory=lambda: __import__("time").time())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte tríade para dicionário."""
        return {
            "phi": self.phi,
            "psi": self.psi,
            "sigma": self.sigma,
            "step_id": self.step_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def validate(self) -> Dict[str, Any]:
        """
        Valida a tríade (verifica ranges e ortogonalidade).

        Returns:
            Dict com validação e interpretação
        """
        errors = []
        warnings = []

        # Validar ranges
        if not (0.0 <= self.phi <= 1.0):
            errors.append(f"Φ fora do range [0, 1]: {self.phi}")
        if not (0.0 <= self.psi <= 1.0):
            errors.append(f"Ψ fora do range [0, 1]: {self.psi}")
        if not (0.0 <= self.sigma <= 1.0):
            errors.append(f"σ fora do range [0, 1]: {self.sigma}")

        # Avisos sobre valores extremos
        if self.phi < 0.1:
            warnings.append("Φ muito baixo (sistema desintegrado)")
        if self.psi < 0.1:
            warnings.append("Ψ muito baixo (produção criativa baixa)")
        if self.sigma < 0.02:
            warnings.append("σ muito baixo (estrutura muito rígida ou dissociada)")

        # Interpretação do estado
        interpretation = self._interpret_state()

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "interpretation": interpretation,
        }

    def _interpret_state(self) -> str:
        """Interpreta o estado da tríade."""
        interpretations = []

        # Interpretação de Φ
        if self.phi > 0.7:
            interpretations.append("Alta integração (IIT)")
        elif self.phi > 0.3:
            interpretations.append("Integração moderada")
        else:
            interpretations.append("Baixa integração")

        # Interpretação de Ψ
        if self.psi > 0.7:
            interpretations.append("Alta produção criativa (Deleuze)")
        elif self.psi > 0.3:
            interpretations.append("Produção criativa moderada")
        else:
            interpretations.append("Baixa produção criativa")

        # Interpretação de σ
        if self.sigma > 0.1:
            interpretations.append("Estrutura flexível (Lacan)")
        elif self.sigma > 0.05:
            interpretations.append("Estrutura moderada")
        else:
            interpretations.append("Estrutura rígida ou dissociada")

        return " | ".join(interpretations)

    def get_magnitude(self) -> float:
        """
        Calcula magnitude da tríade (norma euclidiana).

        NOTA: Isso NÃO é "consciência total" (não são aditivas).
        É apenas uma medida de magnitude no espaço 3D ortogonal.

        Returns:
            Magnitude (norma euclidiana) [0, √3]
        """
        return float(np.sqrt(self.phi**2 + self.psi**2 + self.sigma**2))

    def get_normalized_magnitude(self) -> float:
        """
        Calcula magnitude normalizada [0, 1].

        Normaliza pela magnitude máxima possível (√3).

        Returns:
            Magnitude normalizada [0, 1]
        """
        magnitude = self.get_magnitude()
        max_magnitude = np.sqrt(3.0)
        return float(magnitude / max_magnitude) if max_magnitude > 0 else 0.0


class ConsciousnessTriadCalculator:
    """
    Calculador da tríade ortogonal de consciência (Φ, Ψ, σ).

    Integra:
    - PhiCalculator (via SharedWorkspace) para Φ
    - PsiProducer para Ψ
    - SigmaSinthomeCalculator para σ
    """

    def __init__(
        self,
        workspace: Optional[Any] = None,  # SharedWorkspace
        psi_producer: Optional[Any] = None,  # PsiProducer
        sigma_calculator: Optional[Any] = None,  # SigmaSinthomeCalculator
    ):
        """
        Inicializa calculador da tríade.

        Args:
            workspace: Instância opcional de SharedWorkspace
            psi_producer: Instância opcional de PsiProducer
            sigma_calculator: Instância opcional de SigmaSinthomeCalculator
        """
        self.workspace = workspace
        self.psi_producer = psi_producer
        self.sigma_calculator = sigma_calculator
        self.logger = logger

    def calculate_triad(
        self,
        step_id: str,
        step_content: Optional[str] = None,
        previous_steps: Optional[List[str]] = None,
        goal: Optional[str] = None,
        actions: Optional[List[str]] = None,
        cycle_id: Optional[str] = None,
        phi_history: Optional[List[float]] = None,
    ) -> ConsciousnessTriad:
        """
        Calcula a tríade ortogonal (Φ, Ψ, σ) para um passo/ciclo.

        Args:
            step_id: ID único do passo
            step_content: Conteúdo do passo (para cálculo de Ψ)
            previous_steps: Passos anteriores (para cálculo de Ψ)
            goal: Objetivo da sessão (para cálculo de Ψ)
            actions: Ações tomadas (para cálculo de Ψ)
            cycle_id: ID do ciclo (para cálculo de σ)
            phi_history: Histórico de Φ (para cálculo de σ)

        Returns:
            ConsciousnessTriad com (Φ, Ψ, σ)
        """
        # 1. Calcular Φ (IIT puro)
        phi = self._calculate_phi(step_id)

        # 2. Calcular Ψ (Deleuze)
        psi = self._calculate_psi(
            step_id=step_id,
            step_content=step_content,
            previous_steps=previous_steps or [],
            goal=goal or "",
            actions=actions or [],
        )

        # 3. Calcular σ (Lacan)
        sigma = self._calculate_sigma(
            cycle_id=cycle_id or f"cycle_{step_id}",
            phi_history=phi_history,
            contributing_steps=[step_id] if step_id else [],
        )

        return ConsciousnessTriad(
            phi=phi,
            psi=psi,
            sigma=sigma,
            step_id=step_id,
            metadata={
                "phi_source": "workspace" if self.workspace else "default",
                "psi_source": "psi_producer" if self.psi_producer else "default",
                "sigma_source": "sigma_calculator" if self.sigma_calculator else "default",
            },
        )

    def _calculate_phi(self, step_id: str) -> float:
        """Calcula Φ (IIT puro) via SharedWorkspace."""
        if self.workspace:
            try:
                phi = self.workspace.compute_phi_from_integrations()
                return float(np.clip(phi, 0.0, 1.0))
            except Exception as e:
                self.logger.warning(f"Erro ao calcular Φ: {e}")
                return 0.0

        # Fallback: valor padrão
        return 0.5

    def _calculate_psi(
        self,
        step_id: str,
        step_content: Optional[str],
        previous_steps: List[str],
        goal: str,
        actions: List[str],
    ) -> float:
        """Calcula Ψ (Deleuze) via PsiProducer."""
        # Tentar usar PsiProducer direto se disponível
        if self.psi_producer and step_content:
            try:
                psi_result = self.psi_producer.calculate_psi_for_step(
                    step_content=step_content,
                    previous_steps=previous_steps,
                    goal=goal,
                    actions=actions,
                    step_id=step_id,
                )
                return float(np.clip(psi_result.psi_norm, 0.0, 1.0))
            except Exception as e:
                self.logger.warning(f"Erro ao calcular Ψ via PsiProducer: {e}")

        # Fallback: usar método do workspace se disponível
        if self.workspace and step_content:
            try:
                psi_dict = self.workspace.calculate_psi_from_creativity(
                    step_content=step_content,
                    previous_steps=previous_steps,
                    goal=goal,
                    actions=actions,
                    step_id=step_id,
                )
                return float(np.clip(psi_dict.get("psi_norm", 0.5), 0.0, 1.0))
            except Exception as e:
                self.logger.warning(f"Erro ao calcular Ψ via workspace: {e}")

        # Fallback: valor padrão
        return 0.5

    def _calculate_sigma(
        self,
        cycle_id: str,
        phi_history: Optional[List[float]],
        contributing_steps: List[str],
    ) -> float:
        """Calcula σ (Lacan) via SigmaSinthomeCalculator."""
        # Tentar usar SigmaSinthomeCalculator direto se disponível
        if self.sigma_calculator:
            try:
                sigma_result = self.sigma_calculator.calculate_sigma_for_cycle(
                    cycle_id=cycle_id,
                    phi_history=phi_history,
                    contributing_steps=contributing_steps,
                )
                return float(np.clip(sigma_result.sigma_value, 0.0, 1.0))
            except Exception as e:
                self.logger.warning(f"Erro ao calcular σ via SigmaSinthomeCalculator: {e}")

        # Fallback: usar método do workspace se disponível
        if self.workspace:
            try:
                sigma_dict = self.workspace.calculate_sigma_sinthome(
                    cycle_id=cycle_id,
                    integration_trainer=None,  # Workspace gerencia isso internamente
                    phi_history=phi_history,
                    contributing_steps=contributing_steps,
                )
                return float(np.clip(sigma_dict.get("sigma_value", 0.5), 0.0, 1.0))
            except Exception as e:
                self.logger.warning(f"Erro ao calcular σ via workspace: {e}")

        # Fallback: valor padrão
        return 0.5

    def validate_orthogonality(
        self, triad_history: List[ConsciousnessTriad], window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Valida ortogonalidade da tríade analisando correlações.

        Se as dimensões são ortogonais, correlações devem ser baixas (< 0.3).

        Args:
            triad_history: Histórico de tríades
            window_size: Tamanho da janela para análise

        Returns:
            Dict com correlações e validação de ortogonalidade
        """
        if len(triad_history) < window_size:
            return {
                "valid": False,
                "reason": "Histórico insuficiente",
                "correlations": {},
            }

        # Extrair valores recentes
        recent_triads = triad_history[-window_size:]
        phi_values = [t.phi for t in recent_triads]
        psi_values = [t.psi for t in recent_triads]
        sigma_values = [t.sigma for t in recent_triads]

        # Calcular correlações de Pearson
        phi_psi_corr = float(np.corrcoef(phi_values, psi_values)[0, 1])
        phi_sigma_corr = float(np.corrcoef(phi_values, sigma_values)[0, 1])
        psi_sigma_corr = float(np.corrcoef(psi_values, sigma_values)[0, 1])

        # Validar ortogonalidade (correlações < 0.3)
        threshold = 0.3
        is_orthogonal = (
            abs(phi_psi_corr) < threshold
            and abs(phi_sigma_corr) < threshold
            and abs(psi_sigma_corr) < threshold
        )

        return {
            "valid": is_orthogonal,
            "correlations": {
                "phi_psi": phi_psi_corr,
                "phi_sigma": phi_sigma_corr,
                "psi_sigma": psi_sigma_corr,
            },
            "threshold": threshold,
            "interpretation": (
                "Ortogonal" if is_orthogonal else "Possível dependência entre dimensões"
            ),
        }
