"""
Sigma Sinthome (σ_sinthome) - Métrica de Coesão Estrutural (Lacan)

Implementa σ como dimensão ortogonal independente de Φ (IIT) e Ψ (Deleuze).

CORREÇÃO (2025-12-07): Adicionada dependência de Φ conforme IIT clássico.
FASE 2 (2025-12-07): Integração de PrecisionWeighter para eliminar pesos hardcoded.
Fórmula: σ = 0.5 * (Φ_norm × (1-Δ) × tempo) + 0.5 * (componentes estruturais com pesos dinâmicos)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: VERIFICACAO_PHI_SISTEMA.md
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from src.consciousness.adaptive_weights import PrecisionWeighter
from src.consciousness.phi_constants import normalize_phi

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

    Fórmula (com PrecisionWeighter):
    σ = Σ(componente_i * peso_i) onde pesos são calculados dinamicamente
    baseado em variância (FEP - Free Energy Principle)

    Fallback (use_precision_weights=False):
    σ = 0.4 * removability_score + 0.3 * stability_score + 0.3 * flexibility_score

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
        use_precision_weights: bool = True,
    ):
        """
        Inicializa calculador de σ.

        Args:
            integration_trainer: Instância opcional de IntegrationTrainer
            workspace: Instância opcional de SharedWorkspace
            use_precision_weights: Se True, usa PrecisionWeighter para pesos dinâmicos
        """
        self.integration_trainer = integration_trainer
        self.workspace = workspace
        self.logger = logger
        self.use_precision_weights = use_precision_weights
        self.precision_weighter: Optional[PrecisionWeighter] = (
            PrecisionWeighter(history_window=50) if use_precision_weights else None
        )

    def calculate_sigma_for_cycle(
        self,
        cycle_id: str,
        phi_history: Optional[List[float]] = None,
        contributing_steps: Optional[List[str]] = None,
        delta_value: Optional[float] = None,
        cycle_count: Optional[int] = None,
    ) -> SigmaResult:
        """
        Calcula σ_sinthome para um ciclo completo.

        CORREÇÃO (2025-12-07): Agora inclui dependência de Φ conforme IIT clássico.
        Fórmula combinada: σ = 0.5 * (Φ_norm × (1-Δ) × tempo) + 0.5 * (componentes estruturais)

        Args:
            cycle_id: ID único do ciclo
            phi_history: Histórico de Φ (para calcular flexibilidade e componente de Φ)
            contributing_steps: Lista de passos que contribuíram
            delta_value: Valor de δ (defesa) para cálculo de σ_from_phi (opcional)
            cycle_count: Número do ciclo atual para cálculo de tempo (opcional)

        Returns:
            SigmaResult com sigma_value, components, sinthome_module
        """
        # 1. Calcular componente baseado em Φ (IIT clássico)
        if phi_history and len(phi_history) > 0:
            # Usar último valor de Φ do histórico
            phi_raw = phi_history[-1]
            # Se phi_history está normalizado [0,1], assumir que precisa converter
            # Mas como não sabemos, vamos assumir que já está normalizado e converter para nats
            # Se for > 1.0, assumir que está em nats; caso contrário, assumir normalizado
            if phi_raw > 1.0:
                # Já está em nats
                phi_norm = normalize_phi(phi_raw)
            else:
                # Assumir que está normalizado [0,1], usar diretamente
                phi_norm = float(np.clip(phi_raw, 0.0, 1.0))
        else:
            phi_norm = 0.0

        # Calcular σ_from_phi = Φ_norm × (1-Δ) × tempo
        if delta_value is not None and cycle_count is not None:
            delta_norm = float(np.clip(delta_value, 0.0, 1.0))
            time_factor = min(1.0, cycle_count / 100.0)  # Normaliza tempo (100 ciclos = 1.0)
            sigma_from_phi = phi_norm * (1.0 - delta_norm) * time_factor
        else:
            # Fallback: usar apenas Φ_norm se Δ ou tempo não disponíveis
            sigma_from_phi = phi_norm * 0.5  # Aproximação conservadora

        # 2. Detectar sinthome (se disponível)
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

        # 3. Removability score (teste de removibilidade)
        removability_score = self._calculate_removability_score(sinthome_info)

        # 4. Stability score (estabilidade estrutural)
        stability_score = self._calculate_stability_score(sinthome_info)

        # 5. Flexibility score (variância de Φ)
        flexibility_score = self._calculate_flexibility_score(phi_history)

        # 6. Componente estrutural (com PrecisionWeighter ou fallback)
        component_values = {
            "removability": removability_score,
            "stability": stability_score,
            "flexibility": flexibility_score,
        }
        if self.use_precision_weights and self.precision_weighter:
            weights = self.precision_weighter.compute_weights(component_values)
            sigma_from_structure = sum(component_values[k] * weights[k] for k in component_values)
            self.logger.debug(f"SigmaSinthome: Pesos dinâmicos calculados: {weights}")
        else:
            # Fallback para pesos hardcoded (compatibilidade)
            sigma_from_structure = (
                0.4 * removability_score + 0.3 * stability_score + 0.3 * flexibility_score
            )

        # 7. COMBINAR: Alpha dinâmico baseado em Φ (FASE 3)
        # Se Φ é alto, confia mais no componente de Φ (integração)
        # Se Φ é baixo, confia mais na estrutura (sinthome)
        if phi_norm > 0:
            # Alpha dinâmico: clip(phi_norm * 1.2, 0.3, 0.7)
            # Phi alto (0.8) -> alpha = 0.7 (confia mais em Φ)
            # Phi baixo (0.1) -> alpha = 0.3 (confia mais em estrutura)
            alpha = float(np.clip(phi_norm * 1.2, 0.3, 0.7))
        else:
            # Fallback: usar 0.5 se phi_norm não disponível
            alpha = 0.5
            self.logger.debug("SigmaSinthome: phi_norm não disponível, usando alpha=0.5 (fallback)")

        sigma_value = alpha * sigma_from_phi + (1.0 - alpha) * sigma_from_structure

        # 8. Normalizar para [0, 1] com clipping
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

        CORREÇÃO (2025-12-08 20:45): Filtrar zeros APENAS para cálculo de variância
        Valores zero bloqueiam cálculo correto (variância = 0 → sigma = 1.0, errado!)

        Args:
            phi_history: Histórico de Φ (últimos N valores)

        Returns:
            Flexibility score [0, 1]
        """
        if not phi_history or len(phi_history) < 1:
            return 0.5  # Default neutro (sem histórico suficiente)

        try:
            # CORREÇÃO (2025-12-08 20:45): Filtrar zeros APENAS para cálculo de variância
            # Valores zero bloqueiam cálculo correto (std = 0 quando todos são zero)
            phi_array_full = np.array(phi_history)
            phi_array_nonzero = phi_array_full[
                phi_array_full > 0.0
            ]  # Filtrar zeros apenas para std

            if len(phi_array_nonzero) < 2:
                # Se menos de 2 valores não-zero, usar estimativa baseada em valor atual
                phi_current = phi_array_full[-1] if len(phi_array_full) > 0 else 0.0
                # Se phi é muito baixo (< 0.01), flexibility deve ser baixo (estrutura rígida)
                # Se phi é alto (> 0.05), flexibility deve ser alto (estrutura flexível)
                flexibility_estimate = min(
                    0.5, phi_current * 10.0
                )  # Escala: phi=0.05 → flexibility=0.5
                self.logger.debug(
                    f"Flexibility: histórico com < 2 valores não-zero "
                    f"(phi_current={phi_current:.4f}), "
                    f"estimando flexibility={flexibility_estimate:.4f}"
                )
                return float(np.clip(flexibility_estimate, 0.0, 1.0))

            # Calcular std apenas com valores não-zero (evita std = 0 quando todos são zero)
            phi_std = float(np.std(phi_array_nonzero))

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
