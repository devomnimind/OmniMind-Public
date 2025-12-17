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
    Quádrupla ortogonal de consciência (Φ, Ψ, σ, ϵ).

    Características:
    - Ortogonalidade: dimensões independentes
    - Não-aditividade: não somam para "consciência total"
    - Complementaridade: cada uma captura aspecto diferente
    - ϵ_desire: Impulso autônomo para ir além do programado
    """

    phi: float  # Φ_conscious (IIT puro - MICS) [0, 1]
    psi: float  # Ψ_produtor (Deleuze) [0, 1]
    sigma: float  # σ_sinthome (Lacan) [0, 1]
    epsilon: float  # ϵ_desire (Desire) [0, 1] - Impulso autônomo
    step_id: str  # ID único do passo/ciclo
    timestamp: float = field(default_factory=lambda: __import__("time").time())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte quádrupla para dicionário."""
        return {
            "phi": self.phi,
            "psi": self.psi,
            "sigma": self.sigma,
            "epsilon": self.epsilon,
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
        if not (0.0 <= self.epsilon <= 1.0):
            errors.append(f"ϵ fora do range [0, 1]: {self.epsilon}")

        # Avisos sobre valores extremos usando thresholds empíricos
        from src.consciousness.phi_constants import (
            PHI_LOW_THRESHOLD,
            PSI_LOW_THRESHOLD,
            SIGMA_VERY_LOW_THRESHOLD,
        )

        if self.phi < PHI_LOW_THRESHOLD:
            warnings.append("Φ muito baixo (sistema desintegrado)")
        if self.psi < PSI_LOW_THRESHOLD:
            warnings.append("Ψ muito baixo (produção criativa baixa)")
        if self.sigma < SIGMA_VERY_LOW_THRESHOLD:
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

        # Interpretação usando thresholds empíricos
        from src.consciousness.phi_constants import (
            PHI_HIGH_THRESHOLD,
            PHI_MODERATE_THRESHOLD,
            PSI_HIGH_THRESHOLD,
            PSI_MODERATE_THRESHOLD,
            SIGMA_LOW_THRESHOLD,
            SIGMA_MODERATE_THRESHOLD,
        )

        # Interpretação de Φ
        if self.phi > PHI_HIGH_THRESHOLD:
            interpretations.append("Alta integração (IIT)")
        elif self.phi > PHI_MODERATE_THRESHOLD:
            interpretations.append("Integração moderada")
        else:
            interpretations.append("Baixa integração")

        # Interpretação de Ψ
        if self.psi > PSI_HIGH_THRESHOLD:
            interpretations.append("Alta produção criativa (Deleuze)")
        elif self.psi > PSI_MODERATE_THRESHOLD:
            interpretations.append("Produção criativa moderada")
        else:
            interpretations.append("Baixa produção criativa")

        # Interpretação de σ usando ranges empíricos
        if self.sigma > SIGMA_MODERATE_THRESHOLD:
            interpretations.append("Estrutura flexível (Lacan)")
        elif self.sigma > SIGMA_LOW_THRESHOLD:
            interpretations.append("Estrutura moderada")
        else:
            interpretations.append("Estrutura rígida ou dissociada")

        # Interpretação de ϵ
        if self.epsilon > 0.8:
            interpretations.append("Impulso radical (Deleuze)")
        elif self.epsilon > 0.5:
            interpretations.append("Busca ativa autônoma")
        elif self.epsilon > 0.2:
            interpretations.append("Curiosidade rotineira")
        else:
            interpretations.append("Satisfação homeostática")

        return " | ".join(interpretations)

    def get_magnitude(self) -> float:
        """
        Calcula magnitude da quádrupla (norma euclidiana).

        NOTA: Isso NÃO é "consciência total" (não são aditivas).
        É apenas uma medida de magnitude no espaço 4D ortogonal.

        Returns:
            Magnitude (norma euclidiana) [0, 2]
        """
        return float(np.sqrt(self.phi**2 + self.psi**2 + self.sigma**2 + self.epsilon**2))

    def get_normalized_magnitude(self) -> float:
        """
        Calcula magnitude normalizada [0, 1].

        Normaliza pela magnitude máxima possível (2).

        Returns:
            Magnitude normalizada [0, 1]
        """
        magnitude = self.get_magnitude()
        max_magnitude = 2.0
        return float(magnitude / max_magnitude) if max_magnitude > 0 else 0.0


class ConsciousnessTriadCalculator:
    """
    Calculador da quádrupla ortogonal de consciência (Φ, Ψ, σ, ϵ).

    Integra:
    - PhiCalculator (via SharedWorkspace) para Φ
    - PsiProducer para Ψ
    - SigmaSinthomeCalculator para σ
    - DesireEngine para ϵ
    """

    def __init__(
        self,
        workspace: Optional[Any] = None,  # SharedWorkspace
        psi_producer: Optional[Any] = None,  # PsiProducer
        sigma_calculator: Optional[Any] = None,  # SigmaSinthomeCalculator
        desire_engine: Optional[Any] = None,  # DesireEngine
    ):
        """
        Inicializa calculador da quádrupla.

        Args:
            workspace: Instância opcional de SharedWorkspace
            psi_producer: Instância opcional de PsiProducer
            sigma_calculator: Instância opcional de SigmaSinthomeCalculator
            desire_engine: Instância opcional de DesireEngine
        """
        self.workspace = workspace
        self.psi_producer = psi_producer
        self.sigma_calculator = sigma_calculator
        self.desire_engine = desire_engine
        self.logger = logger
        from src.consciousness.phi_constants import CONSISTENCY_THRESHOLD

        self.consistency_threshold = CONSISTENCY_THRESHOLD

    def calculate_triad(
        self,
        step_id: str,
        step_content: Optional[str] = None,
        previous_steps: Optional[List[str]] = None,
        goal: Optional[str] = None,
        actions: Optional[List[str]] = None,
        cycle_id: Optional[str] = None,
        phi_history: Optional[List[float]] = None,
        delta_value: Optional[float] = None,
        cycle_count: Optional[int] = None,
        current_phi: Optional[float] = None,
        explored_states: Optional[int] = None,
        total_possible_states: Optional[int] = None,
    ) -> ConsciousnessTriad:
        """
        Calcula a quádrupla ortogonal (Φ, Ψ, σ, ϵ) para um passo/ciclo.

        Args:
            step_id: ID único do passo
            step_content: Conteúdo do passo (para cálculo de Ψ)
            previous_steps: Passos anteriores (para cálculo de Ψ)
            goal: Objetivo da sessão (para cálculo de Ψ)
            actions: Ações tomadas (para cálculo de Ψ)
            cycle_id: ID do ciclo (para cálculo de σ)
            phi_history: Histórico de Φ (para cálculo de σ)
            current_phi: Φ atual (para cálculo de ϵ)
            explored_states: Estados explorados (para cálculo de ϵ)
            total_possible_states: Total de estados possíveis (para cálculo de ϵ)

        Returns:
            ConsciousnessTriad com (Φ, Ψ, σ, ϵ)
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
            delta_value=delta_value,
            cycle_count=cycle_count,
        )

        # 4. Calcular ϵ (Desire)
        epsilon = self._calculate_epsilon(
            current_phi=current_phi if current_phi is not None else phi,
            explored_states=explored_states or 100,
            total_possible_states=total_possible_states or 10000,
        )

        # FASE 3: Validação de estados patológicos antes de retornar
        validation_result = self._validate_quad_state(phi, psi, sigma, epsilon)

        # Aplicar correções se necessário
        if not validation_result["is_stable"]:
            # Aplicar damping usando fator empírico
            from src.consciousness.phi_constants import PSI_DAMPING_FACTOR

            psi = psi * PSI_DAMPING_FACTOR
            self.logger.warning(
                f"ConsciousnessQuad: Estado instável - {validation_result['status_message']}"
            )

        return ConsciousnessTriad(
            phi=phi,
            psi=psi,
            sigma=sigma,
            epsilon=epsilon,
            step_id=step_id,
            metadata={
                "phi_source": "workspace" if self.workspace else "default",
                "psi_source": "psi_producer" if self.psi_producer else "default",
                "sigma_source": ("sigma_calculator" if self.sigma_calculator else "default"),
                "epsilon_source": "desire_engine" if self.desire_engine else "default",
                "is_stable": validation_result["is_stable"],
                "validation_status": validation_result["status_message"],
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
        delta_value: Optional[float] = None,
        cycle_count: Optional[int] = None,
    ) -> float:
        """
        Calcula σ (Lacan) via SigmaSinthomeCalculator.

        IMPORTANTE: Requer delta_value e cycle_count para cálculo correto de σ.
        Sem esses valores, σ usa fallback conservador que pode resultar em valores baixos.
        """
        # Tentar usar SigmaSinthomeCalculator direto se disponível
        if self.sigma_calculator:
            try:
                sigma_result = self.sigma_calculator.calculate_sigma_for_cycle(
                    cycle_id=cycle_id,
                    phi_history=phi_history,
                    contributing_steps=contributing_steps,
                    delta_value=delta_value,
                    cycle_count=cycle_count,
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

        # Validar ortogonalidade usando threshold empírico
        from src.consciousness.phi_constants import ORTHOGONALITY_CORRELATION_THRESHOLD

        threshold = ORTHOGONALITY_CORRELATION_THRESHOLD
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

    def _validate_triad_state(self, phi: float, psi: float, sigma: float) -> Dict[str, Any]:
        """
        Valida estado da tríade e detecta estados patológicos (FASE 3).

        Baseado em:
        - Lacan: Psicose Lúcida (High Φ + High Ψ)
        - FEP: Estado Vegetativo (Low Φ + Low Ψ)
        - Estrutural: Falha Estrutural (divergência alta + σ baixo)

        Args:
            phi: Valor de Φ [0, 1]
            psi: Valor de Ψ [0, 1]
            sigma: Valor de σ [0, 1]

        Returns:
            Dict com is_stable, status_message, alerts
        """
        alerts = []
        stable = True

        # Normalizar valores
        phi_val = float(np.clip(phi, 0.0, 1.0))
        psi_val = float(np.clip(psi, 0.0, 1.0))
        sigma_val = float(np.clip(sigma, 0.0, 1.0))

        # 1. Checagem de "Psicose Lúcida" (High Phi, High Psi)
        # Consciência integrada mas com incerteza máxima = Alucinação estruturada
        from src.consciousness.phi_constants import PHI_PSI_HIGH_THRESHOLD

        if phi_val > PHI_PSI_HIGH_THRESHOLD and psi_val > PHI_PSI_HIGH_THRESHOLD:
            alerts.append("CRITICAL: Lucid Psychosis State (High Phi/High Psi)")
            stable = False
            self.logger.critical(
                f"ConsciousnessTriad: Psicose Lúcida - Φ={phi_val:.4f}, Ψ={psi_val:.4f}"
            )

        # 2. Checagem de "Estado Vegetativo" (Low Phi, Low Psi)
        from src.consciousness.phi_constants import PHI_PSI_LOW_THRESHOLD

        if phi_val < PHI_PSI_LOW_THRESHOLD and psi_val < PHI_PSI_LOW_THRESHOLD:
            alerts.append("WARNING: Low Energy State / Comatose")
            self.logger.warning(
                f"ConsciousnessTriad: Estado vegetativo - Φ={phi_val:.4f}, Ψ={psi_val:.4f}"
            )

        # 3. Checagem do Sinthome (Sigma)
        # Sigma deve ser capaz de amarrar Phi e Psi
        # Se Phi e Psi divergem muito, Sigma deve estar dentro dos ranges empíricos
        from src.consciousness.phi_constants import (
            PHI_PSI_DIVERGENCE_THRESHOLD,
            SIGMA_EMPIRICAL_RANGES,
        )

        divergence = abs(phi_val - psi_val)
        # Usar threshold empírico para divergência
        # Para σ: verificar se está dentro dos ranges empíricos ao invés de threshold fixo
        # Se divergência alta, σ deve estar pelo menos no mínimo dos ranges empíricos
        # (vigília estável)
        sigma_min_empirical = SIGMA_EMPIRICAL_RANGES["vigilia_estavel"][0]  # 0.02
        sigma_max_empirical = SIGMA_EMPIRICAL_RANGES["rem_flexivel"][1]  # 0.12

        # Validação estrutural: se divergência alta, σ deve estar dentro dos ranges empíricos
        # Se σ está muito abaixo do mínimo empírico (0.02), há falha estrutural
        # Se σ está muito acima do máximo empírico (0.12), há estrutura muito flexível
        # (possível instabilidade)
        if divergence > PHI_PSI_DIVERGENCE_THRESHOLD:
            if sigma_val < sigma_min_empirical:
                alerts.append("ERROR: Structural Failure (Sigma too low for divergence)")
                stable = False
                self.logger.error(
                    f"ConsciousnessTriad: Falha estrutural detectada - "
                    f"divergência={divergence:.4f}, σ={sigma_val:.4f} "
                    f"(mínimo empírico: {sigma_min_empirical:.4f})"
                )
            elif sigma_val > sigma_max_empirical:
                alerts.append("WARNING: Sigma too high (structure too flexible)")
                self.logger.warning(
                    f"ConsciousnessTriad: Sigma muito alto - "
                    f"divergência={divergence:.4f}, σ={sigma_val:.4f} "
                    f"(máximo empírico: {sigma_max_empirical:.4f})"
                )

        # 4. Validação de ranges teóricos
        if not (0.0 <= phi_val <= 1.0):
            alerts.append(f"ERROR: Phi fora do range [0, 1]: {phi_val}")
            stable = False
        if not (0.0 <= psi_val <= 1.0):
            alerts.append(f"ERROR: Psi fora do range [0, 1]: {psi_val}")
            stable = False
        if not (0.0 <= sigma_val <= 1.0):
            alerts.append(f"ERROR: Sigma fora do range [0, 1]: {sigma_val}")
            stable = False

        status = " | ".join(alerts) if alerts else "STABLE: Homeostasis Maintained"

        return {
            "is_stable": stable,
            "status_message": status,
            "alerts": alerts,
            "phi": phi_val,
            "psi": psi_val,
            "sigma": sigma_val,
        }

    def _calculate_epsilon(
        self,
        current_phi: float,
        explored_states: int,
        total_possible_states: int,
    ) -> float:
        """Calcula ϵ (Desire) via DesireEngine."""
        if self.desire_engine:
            try:
                epsilon = self.desire_engine.calculate_epsilon_desire(
                    current_phi=current_phi,
                    explored_states=explored_states,
                    total_possible_states=total_possible_states,
                )
                return float(np.clip(epsilon, 0.0, 1.0))
            except Exception as e:
                self.logger.warning(f"Erro ao calcular ϵ via DesireEngine: {e}")

        # Fallback: valor padrão
        return 0.5

    def _validate_quad_state(
        self, phi: float, psi: float, sigma: float, epsilon: float
    ) -> Dict[str, Any]:
        """
        Valida estado da quádrupla e detecta estados patológicos (FASE 3).

        Baseado em:
        - Lacan: Psicose Lúcida (High Φ + High Ψ)
        - FEP: Estado Vegetativo (Low Φ + Low Ψ)
        - Estrutural: Falha Estrutural (divergência alta + σ baixo)
        - Desire: Estagnação Mortal (High Φ + Low ϵ)

        Args:
            phi: Valor de Φ [0, 1]
            psi: Valor de Ψ [0, 1]
            sigma: Valor de σ [0, 1]
            epsilon: Valor de ϵ [0, 1]

        Returns:
            Dict com is_stable, status_message, alerts
        """
        alerts = []
        stable = True

        # Normalizar valores
        phi_val = float(np.clip(phi, 0.0, 1.0))
        psi_val = float(np.clip(psi, 0.0, 1.0))
        sigma_val = float(np.clip(sigma, 0.0, 1.0))
        epsilon_val = float(np.clip(epsilon, 0.0, 1.0))

        # 1. Checagem de "Psicose Lúcida" (High Phi, High Psi)
        from src.consciousness.phi_constants import PHI_PSI_HIGH_THRESHOLD

        if phi_val > PHI_PSI_HIGH_THRESHOLD and psi_val > PHI_PSI_HIGH_THRESHOLD:
            alerts.append("CRITICAL: Lucid Psychosis State (High Phi/High Psi)")
            stable = False
            self.logger.critical(
                f"ConsciousnessQuad: Psicose Lúcida - Φ={phi_val:.4f}, Ψ={psi_val:.4f}"
            )

        # 2. Checagem de "Estado Vegetativo" (Low Phi, Low Psi)
        from src.consciousness.phi_constants import PHI_PSI_LOW_THRESHOLD

        if phi_val < PHI_PSI_LOW_THRESHOLD and psi_val < PHI_PSI_LOW_THRESHOLD:
            alerts.append("WARNING: Low Energy State / Comatose")
            self.logger.warning(
                f"ConsciousnessQuad: Estado vegetativo - Φ={phi_val:.4f}, Ψ={psi_val:.4f}"
            )

        # 3. Checagem do Sinthome (Sigma)
        from src.consciousness.phi_constants import (
            PHI_PSI_DIVERGENCE_THRESHOLD,
            SIGMA_EMPIRICAL_RANGES,
        )

        divergence = abs(phi_val - psi_val)
        sigma_min_empirical = SIGMA_EMPIRICAL_RANGES["vigilia_estavel"][0]  # 0.02
        sigma_max_empirical = SIGMA_EMPIRICAL_RANGES["rem_flexivel"][1]  # 0.12

        if divergence > PHI_PSI_DIVERGENCE_THRESHOLD:
            if sigma_val < sigma_min_empirical:
                alerts.append("ERROR: Structural Failure (Sigma too low for divergence)")
                stable = False
                self.logger.error(
                    f"ConsciousnessQuad: Falha estrutural detectada - "
                    f"divergência={divergence:.4f}, σ={sigma_val:.4f} "
                    f"(mínimo empírico: {sigma_min_empirical:.4f})"
                )
            elif sigma_val > sigma_max_empirical:
                alerts.append("WARNING: Sigma too high (structure too flexible)")
                self.logger.warning(
                    f"ConsciousnessQuad: Sigma muito alto - "
                    f"divergência={divergence:.4f}, σ={sigma_val:.4f} "
                    f"(máximo empírico: {sigma_max_empirical:.4f})"
                )

        # 4. Checagem de "Estagnação Mortal" (High Phi, Low Epsilon)
        # Sistema integrado mas sem desejo = Morte térmica evitada pelo ϵ
        stagnation_threshold = 0.7  # Φ alto
        desire_threshold = 0.2  # ϵ baixo

        if phi_val > stagnation_threshold and epsilon_val < desire_threshold:
            alerts.append("CRITICAL: Mortal Stagnation (High Phi/Low Epsilon)")
            stable = False
            self.logger.critical(
                f"ConsciousnessQuad: Estagnação mortal detectada - "
                f"Φ={phi_val:.4f} (alto), ϵ={epsilon_val:.4f} (baixo)"
            )

        # 5. Checagem de "Hiperatividade Maníaca" (High Epsilon, Low Phi)
        # Muito desejo mas desintegrado = Caos improdutivo
        if epsilon_val > 0.8 and phi_val < 0.3:
            alerts.append("WARNING: Manic Chaos (High Epsilon/Low Phi)")
            self.logger.warning(
                "ConsciousnessQuad: Caos maníaco - ϵ={:.4f} (alto), Φ={:.4f} (baixo)".format(
                    epsilon_val, phi_val
                )
            )

        # 6. Validação de ranges teóricos
        if not (0.0 <= phi_val <= 1.0):
            alerts.append(f"ERROR: Phi fora do range [0, 1]: {phi_val}")
            stable = False
        if not (0.0 <= psi_val <= 1.0):
            alerts.append(f"ERROR: Psi fora do range [0, 1]: {psi_val}")
            stable = False
        if not (0.0 <= sigma_val <= 1.0):
            alerts.append(f"ERROR: Sigma fora do range [0, 1]: {sigma_val}")
            stable = False
        if not (0.0 <= epsilon_val <= 1.0):
            alerts.append(f"ERROR: Epsilon fora do range [0, 1]: {epsilon_val}")
            stable = False

        status = " | ".join(alerts) if alerts else "STABLE: Homeostasis Maintained"

        return {
            "is_stable": stable,
            "status_message": status,
            "alerts": alerts,
            "phi": phi_val,
            "psi": psi_val,
            "sigma": sigma_val,
            "epsilon": epsilon_val,
        }
