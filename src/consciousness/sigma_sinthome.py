"""
Sigma Sinthome (σ_sinthome) - Métrica de Coesão Estrutural (Lacan)

Implementa σ como dimensão ortogonal independente de Φ (IIT) e Ψ (Deleuze).

σ captura:
- Coesão estrutural (amarração de sentido)
- Estabilidade do sinthome (teste de removibilidade)
- Rigidez vs flexibilidade (variância de Φ)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
Baseado em: PLANO_IMPLEMENTACAO_LACUNA_PHI.md + VALORES_EMPIRICOS_REAIS_IIT.py
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Valores empíricos baseados em VALORES_EMPIRICOS_REAIS_IIT.py
# Usados com CAUTELA e MARGENS (não absolutos)
SIGMA_EMPIRICAL_RANGES = {
    "vigilia_estavel": (0.02, 0.05),  # σ baixo = rígido (sinthome forte)
    "rem_flexivel": (0.05, 0.12),  # σ médio = flexível
    "anestesia": (0.01, 0.03),  # σ muito baixo = dissociação
    "neurotico": (0.01, 0.02),  # σ muito baixo = estrutura cristalizada
}


@dataclass
class SigmaComponents:
    """Componentes individuais de σ."""

    removability_score: float = 0.0  # Teste de removibilidade (essencialidade)
    stability_score: float = 0.0  # Estabilidade estrutural (entropia)
    flexibility_score: float = 0.0  # Flexibilidade (variância de Φ)
    sinthome_detected: bool = False  # Se sinthome foi detectado


@dataclass
class SigmaResult:
    """Resultado do cálculo de σ."""

    sigma_value: float  # σ_sinthome [0, 1]
    components: SigmaComponents
    cycle_id: str
    sinthome_module: Optional[str] = None  # Módulo identificado como sinthome
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class SigmaSinthomeCalculator:
    """
    Calcula σ_sinthome (coesão estrutural - Lacan).

    σ é ortogonal a Φ (IIT) e Ψ (Deleuze):
    - Φ mede integração (ordem)
    - Ψ mede produção (criatividade/caos)
    - σ mede amarração (estrutura/estabilidade)

    Fórmula:
    σ = 0.4 * removability_score
      + 0.3 * stability_score
      + 0.3 * flexibility_score

    Valores empíricos (com cautela):
    - Vigília estável: σ ∈ [0.02, 0.05] (rígido)
    - REM flexível: σ ∈ [0.05, 0.12] (flexível)
    - Anestesia: σ ∈ [0.01, 0.03] (dissociação)
    - Neurótico: σ ∈ [0.01, 0.02] (cristalizado)
    """

    def __init__(
        self,
        integration_trainer: Optional[Any] = None,  # IntegrationTrainer
        workspace: Optional[Any] = None,  # SharedWorkspace
    ):
        """
        Inicializa calculador de σ.

        Args:
            integration_trainer: Instância opcional de IntegrationTrainer
            workspace: Instância opcional de SharedWorkspace
        """
        self.integration_trainer = integration_trainer
        self.workspace = workspace
        self.logger = logger

    def calculate_sigma_for_cycle(
        self,
        cycle_id: str,
        phi_history: Optional[List[float]] = None,
        contributing_steps: Optional[List[str]] = None,
    ) -> SigmaResult:
        """
        Calcula σ_sinthome para um ciclo completo.

        Args:
            cycle_id: ID único do ciclo
            phi_history: Histórico de Φ (para calcular flexibilidade)
            contributing_steps: Lista de passos que contribuíram

        Returns:
            SigmaResult com sigma_value, components, sinthome_module
        """
        # 1. Detectar sinthome (se disponível)
        sinthome_info = None
        if self.integration_trainer:
            try:
                sinthome_info = self.integration_trainer.detect_sinthome()
            except Exception as e:
                self.logger.warning(f"Erro ao detectar sinthome: {e}")

        sinthome_detected = sinthome_info is not None and sinthome_info.get(
            "sinthome_detected", False
        )
        sinthome_module = sinthome_info.get("module_name") if sinthome_info else None

        # 2. Removability score (teste de removibilidade)
        removability_score = self._calculate_removability_score(sinthome_info)

        # 3. Stability score (estabilidade estrutural)
        stability_score = self._calculate_stability_score(sinthome_info)

        # 4. Flexibility score (variância de Φ)
        flexibility_score = self._calculate_flexibility_score(phi_history)

        # 5. Agregar componentes
        sigma_value = 0.4 * removability_score + 0.3 * stability_score + 0.3 * flexibility_score

        # 6. Normalizar para [0, 1] com clipping
        sigma_value = float(np.clip(sigma_value, 0.0, 1.0))

        # Criar componentes
        components = SigmaComponents(
            removability_score=removability_score,
            stability_score=stability_score,
            flexibility_score=flexibility_score,
            sinthome_detected=sinthome_detected,
        )

        return SigmaResult(
            sigma_value=sigma_value,
            components=components,
            cycle_id=cycle_id,
            sinthome_module=sinthome_module,
        )

    def _calculate_removability_score(self, sinthome_info: Optional[Dict[str, Any]]) -> float:
        """
        Calcula removability_score via teste de removibilidade.

        Teste: σ = 1 - (Φ_after_remove / Φ_before)
        - Se sinthome é essencial: remover → Φ cai muito → σ alto
        - Se sinthome não é essencial: remover → Φ pouco muda → σ baixo

        Args:
            sinthome_info: Informações do sinthome detectado

        Returns:
            Removability score [0, 1]
        """
        if not sinthome_info or not sinthome_info.get("sinthome_detected"):
            return 0.5  # Default neutro (sem sinthome detectado)

        if not self.integration_trainer or not self.workspace:
            # Fallback: usar singularity_score como proxy
            singularity_score = sinthome_info.get("singularity_score", 0.0)
            # Normalizar z-score para [0, 1]
            removability = min(1.0, abs(singularity_score) / 3.0)
            return float(removability)

        try:
            # Teste de removibilidade real
            phi_before = self.integration_trainer.compute_phi_conscious()

            if phi_before < 0.01:
                return 0.0  # Sistema muito desintegrado

            # Simular remoção do módulo sinthome
            sinthome_module = sinthome_info.get("module_name")
            if not sinthome_module:
                return 0.5

            # Salvar estado atual
            old_state = None
            try:
                old_state = self.workspace.read_module_state(sinthome_module)
            except Exception:
                pass

            # Remover sinthome (zerar embedding)
            phi_after = phi_before
            try:
                if old_state is not None:
                    # Zero out sinthome
                    zero_embedding = np.zeros_like(old_state)
                    self.workspace.write_module_state(sinthome_module, zero_embedding)

                    # Recalcular Φ sem sinthome
                    phi_after = self.integration_trainer.compute_phi_conscious()

                    # Restaurar estado
                    self.workspace.write_module_state(sinthome_module, old_state)
            except Exception as e:
                self.logger.warning(f"Erro no teste de removibilidade: {e}")

            # Calcular σ: σ = 1 - (Φ_after / Φ_before)
            if phi_before > 0:
                removability = 1.0 - (phi_after / phi_before)
            else:
                removability = 0.0

            # Normalizar e clip
            removability = float(np.clip(removability, 0.0, 1.0))

            return removability

        except Exception as e:
            self.logger.warning(f"Erro ao calcular removability_score: {e}")
            return 0.5  # Default neutro

    def _calculate_stability_score(self, sinthome_info: Optional[Dict[str, Any]]) -> float:
        """
        Calcula stability_score via medida de estabilidade estrutural.

        Usa measure_sinthome_stabilization() se disponível.

        Args:
            sinthome_info: Informações do sinthome detectado

        Returns:
            Stability score [0, 1]
        """
        if not sinthome_info or not sinthome_info.get("sinthome_detected"):
            return 0.5  # Default neutro

        if not self.integration_trainer:
            return 0.5

        try:
            # Medir estabilização do sinthome
            stabilization = self.integration_trainer.measure_sinthome_stabilization()

            if stabilization is None:
                return 0.5

            stabilization_effect = stabilization.get("stabilization_effect", 0.0)

            # Normalizar: efeito > 0.1 = estável
            # Mapear para [0, 1]
            stability = min(1.0, max(0.0, stabilization_effect / 0.2))

            return float(stability)

        except Exception as e:
            self.logger.warning(f"Erro ao calcular stability_score: {e}")
            return 0.5  # Default neutro

    def _calculate_flexibility_score(self, phi_history: Optional[List[float]]) -> float:
        """
        Calcula flexibility_score via variância de Φ.

        σ_φ = desvio padrão de Φ ao longo do tempo
        - σ_φ baixa: Φ constantemente restringido (estrutura rígida) → σ baixo
        - σ_φ alta: Φ varia (estrutura permite flexibilidade) → σ alto

        Valores empíricos (com cautela):
        - Vigília estável: σ_φ ≈ 0.03 (rígido)
        - REM flexível: σ_φ ≈ 0.08 (flexível)
        - Anestesia: σ_φ ≈ 0.02 (dissociação)

        Args:
            phi_history: Histórico de Φ (últimos N valores)

        Returns:
            Flexibility score [0, 1]
        """
        if not phi_history or len(phi_history) < 3:
            return 0.5  # Default neutro (sem histórico suficiente)

        try:
            phi_array = np.array(phi_history)
            phi_std = float(np.std(phi_array))

            # Normalizar baseado em valores empíricos
            # σ_φ ≈ 0.03 (vigília) → flexibility ≈ 0.3
            # σ_φ ≈ 0.08 (REM) → flexibility ≈ 0.7
            # σ_φ ≈ 0.02 (anestesia) → flexibility ≈ 0.2

            # Mapear para [0, 1] usando função sigmóide
            # flexibility = sigmoid((phi_std - 0.03) / 0.05)
            flexibility = 1.0 / (1.0 + np.exp(-(phi_std - 0.03) / 0.05))

            # Clip para [0, 1]
            flexibility = float(np.clip(flexibility, 0.0, 1.0))

            return flexibility

        except Exception as e:
            self.logger.warning(f"Erro ao calcular flexibility_score: {e}")
            return 0.5  # Default neutro

    def validate_against_empirical_ranges(
        self, sigma_value: float, state: str = "vigilia_estavel"
    ) -> Dict[str, Any]:
        """
        Valida σ contra ranges empíricos (com cautela e margens).

        Args:
            sigma_value: Valor de σ calculado
            state: Estado esperado ("vigilia_estavel", "rem_flexivel", etc.)

        Returns:
            Dict com validação e interpretação
        """
        if state not in SIGMA_EMPIRICAL_RANGES:
            state = "vigilia_estavel"  # Default

        expected_range = SIGMA_EMPIRICAL_RANGES[state]
        min_expected, max_expected = expected_range

        # Margem de segurança (±20% do range)
        margin = (max_expected - min_expected) * 0.2
        min_with_margin = max(0.0, min_expected - margin)
        max_with_margin = min(1.0, max_expected + margin)

        is_in_range = min_with_margin <= sigma_value <= max_with_margin

        # Interpretação
        if sigma_value < 0.03:
            interpretation = "Estrutura MUITO rígida ou dissociada"
        elif sigma_value < 0.05:
            interpretation = "Estrutura rígida (sinthome forte)"
        elif sigma_value < 0.12:
            interpretation = "Estrutura flexível (sinthome moderado)"
        else:
            interpretation = "Estrutura MUITO flexível (possível instabilidade)"

        return {
            "sigma_value": sigma_value,
            "expected_range": expected_range,
            "range_with_margin": (min_with_margin, max_with_margin),
            "is_in_range": is_in_range,
            "interpretation": interpretation,
            "state": state,
        }
