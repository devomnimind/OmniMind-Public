"""
Delta Calculator (δ) - Defesa Psicanalítica

Delta mede bloqueios defensivos contra trauma.
É diferente de σ (sinthome):
- σ = estrutura que amarra (estabilidade)
- δ = defesa contra trauma (proteção)

Controle tem 3 componentes:
1. Sinthome (σ) = estrutura que amarra
2. Defesa (δ) = bloqueios contra trauma
3. Regulação = ajuste fino contínuo

CORREÇÃO (2025-12-07 - Protocolo Livewire):
- Uso de PrecisionWeighter para componentes de trauma (elimina pesos hardcoded)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: Isomorfismo Estrutural validado + Protocolo Livewire
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from src.consciousness.adaptive_weights import PrecisionWeighter
from src.consciousness.dynamic_trauma import DynamicTraumaCalculator
from src.consciousness.phi_constants import normalize_phi

logger = logging.getLogger(__name__)


@dataclass
class DeltaComponents:
    """Componentes individuais de δ (defesa)."""

    trauma_detection: float = 0.0  # Detecção de trauma (divergência extrema)
    blocking_strength: float = 0.0  # Força de bloqueio
    defensive_activation: float = 0.0  # Ativação defensiva


@dataclass
class DeltaResult:
    """Resultado do cálculo de δ."""

    delta_value: float  # δ (defesa) [0, 1]
    components: DeltaComponents
    blocked_modules: List[str]  # Módulos bloqueados
    timestamp: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Inicializa metadata se None."""
        if self.metadata is None:
            self.metadata = {}


class DeltaCalculator:
    """
    Calcula δ (defesa psicanalítica).

    δ é diferente de σ:
    - σ (sinthome) = estrutura que amarra (estabilidade)
    - δ (defesa) = bloqueios contra trauma (proteção)

    Fórmula:
    δ = 0.4 * trauma_detection
      + 0.3 * blocking_strength
      + 0.3 * defensive_activation

    Valores:
    - δ baixo (0.0-0.3): Sistema aberto, sem defesas
    - δ médio (0.3-0.6): Defesas moderadas, proteção ativa
    - δ alto (0.6-1.0): Defesas rígidas, bloqueios fortes
    """

    def __init__(
        self,
        trauma_threshold: Optional[float] = None,
        use_dynamic_trauma: bool = True,
        use_precision_weights: bool = True,
        use_dynamic_threshold: bool = True,
        dynamic_threshold_k: float = 2.0,
        min_history_size: int = 30,
    ):
        """
        Inicializa calculador de δ.

        Args:
            trauma_threshold: Threshold para detecção de trauma (divergência extrema).
                Se None, usa valor empírico estático (0.7) ou cálculo dinâmico se habilitado.
            use_dynamic_trauma: Se True, usa DynamicTraumaCalculator (Protocolo Livewire)
            use_precision_weights: Se True, usa PrecisionWeighter para componentes
                de trauma (elimina pesos hardcoded 0.4/0.3/0.3)
            use_dynamic_threshold: Se True, calcula threshold dinamicamente como μ+kσ
                da Δ_norm histórica (onde k = dynamic_threshold_k)
            dynamic_threshold_k: Multiplicador do desvio padrão para threshold dinâmico
                (padrão: 2.0 = μ+2σ, pode usar 3.0 = μ+3σ para eventos mais extremos)
            min_history_size: Tamanho mínimo do histórico para calcular threshold dinâmico
        """
        from src.consciousness.phi_constants import TRAUMA_THRESHOLD_STATIC

        self.use_dynamic_threshold = use_dynamic_threshold
        self.dynamic_threshold_k = dynamic_threshold_k
        self.min_history_size = min_history_size
        self.delta_norm_history: List[float] = []  # Histórico de Δ_norm para cálculo dinâmico

        # Threshold inicial: estático ou fornecido
        self.trauma_threshold_static = (
            trauma_threshold if trauma_threshold is not None else TRAUMA_THRESHOLD_STATIC
        )
        self.trauma_threshold = self.trauma_threshold_static  # Será atualizado dinamicamente

        self.logger = logger
        self.blocked_modules_history: List[str] = []

        # PROTOCOLO LIVEWIRE FASE 2.2: Trauma dinâmico com memória
        self.use_dynamic_trauma = use_dynamic_trauma
        self.dynamic_trauma_calc: Optional[DynamicTraumaCalculator] = (
            DynamicTraumaCalculator() if use_dynamic_trauma else None
        )

        # PROTOCOLO LIVEWIRE: Ponderação dinâmica
        self.use_precision_weights = use_precision_weights
        self.precision_weighter: Optional[PrecisionWeighter] = (
            PrecisionWeighter(history_window=50) if use_precision_weights else None
        )

    def calculate_delta(
        self,
        expectation_embedding: np.ndarray,
        reality_embedding: np.ndarray,
        module_outputs: Dict[str, np.ndarray],
        integration_strength: Optional[float] = None,
        phi_raw: Optional[float] = None,
    ) -> DeltaResult:
        """
        Calcula δ (defesa) para um ciclo.

        CORREÇÃO (2025-12-07): Agora inclui dependência de Φ conforme IIT clássico.
        Fórmula combinada: Δ = 0.5 * (1.0 - Φ_norm) + 0.5 * (componentes de trauma)

        Args:
            expectation_embedding: Embedding de expectation
            reality_embedding: Embedding de reality
            module_outputs: Outputs de todos os módulos
            integration_strength: Força de integração (opcional, usado como proxy
                de Φ se phi_raw não fornecido)
            phi_raw: Valor de Φ em nats (opcional, se fornecido será normalizado)

        Returns:
            DeltaResult com delta_value e components
        """
        # 1. Calcular componente baseado em Φ (IIT clássico)
        if phi_raw is not None:
            # Se phi_raw fornecido, normalizar explicitamente
            phi_norm = normalize_phi(phi_raw)
        elif integration_strength is not None:
            # Se integration_strength fornecido, assumir que já está normalizado [0, 1]
            phi_norm = float(np.clip(integration_strength, 0.0, 1.0))
        else:
            # Fallback: assumir Φ baixo (alta defesa)
            phi_norm = 0.0

        # Componente de Φ: inversão perfeita (IIT clássico)
        delta_from_phi = 1.0 - phi_norm

        # 2. Detecção de trauma (divergência extrema)
        trauma_detection = self._detect_trauma(expectation_embedding, reality_embedding)

        # 3. Força de bloqueio
        blocking_strength = self._calculate_blocking_strength(
            trauma_detection, integration_strength
        )

        # 4. Ativação defensiva
        defensive_activation = self._calculate_defensive_activation(
            module_outputs, trauma_detection
        )

        # 5. Identificar módulos bloqueados
        blocked_modules = self._identify_blocked_modules(module_outputs, trauma_detection)

        # 6. Componente de trauma (usando PrecisionWeighter se habilitado)
        if self.use_precision_weights and self.precision_weighter:
            # Usar ponderação dinâmica baseada em variância
            trauma_components = {
                "trauma_detection": trauma_detection,
                "blocking_strength": blocking_strength,
                "defensive_activation": defensive_activation,
            }
            weights = self.precision_weighter.compute_weights(trauma_components)
            delta_from_trauma = sum(trauma_components[k] * weights[k] for k in trauma_components)
            self.logger.debug(
                f"Delta trauma weights: {weights}, " f"delta_from_trauma={delta_from_trauma:.4f}"
            )
        else:
            # Fallback: pesos hardcoded (compatibilidade)
            delta_from_trauma = (
                0.4 * trauma_detection + 0.3 * blocking_strength + 0.3 * defensive_activation
            )

        # 7. COMBINAR: 50% de Φ (IIT) + 50% de trauma (Lacan)
        delta_value = 0.5 * delta_from_phi + 0.5 * delta_from_trauma

        # 8. Normalizar para [0, 1]
        delta_value = float(np.clip(delta_value, 0.0, 1.0))

        # 9. Atualizar histórico e threshold dinâmico
        self._update_dynamic_threshold(delta_value)

        components = DeltaComponents(
            trauma_detection=trauma_detection,
            blocking_strength=blocking_strength,
            defensive_activation=defensive_activation,
        )

        return DeltaResult(
            delta_value=delta_value,
            components=components,
            blocked_modules=blocked_modules,
            timestamp=float(__import__("time").time()),
            metadata={},
        )

    def _detect_trauma(self, expectation: np.ndarray, reality: np.ndarray) -> float:
        """
        Detecta trauma (divergência extrema).

        Trauma = quando expectation diverge muito de reality.

        Args:
            expectation: Embedding de expectation
            reality: Embedding de reality

        Returns:
            float [0, 1] representando detecção de trauma
        """
        # Divergência L2
        divergence = float(np.linalg.norm(expectation - reality))

        # Normaliza (garantindo [0, 1])
        # CORREÇÃO: A divergência pode ser maior que max_norm devido à desigualdade
        # triangular reversa. Usar min para garantir que não exceda 1.0
        max_norm = max(np.linalg.norm(expectation), np.linalg.norm(reality))
        max_norm_float = float(max_norm)  # Garantir type float
        normalized_divergence = float(min(1.0, divergence / (max_norm_float + 1e-10)))

        # Trauma = divergência acima do threshold
        trauma_threshold_float = float(self.trauma_threshold)  # type: ignore[arg-type]
        if normalized_divergence > trauma_threshold_float:
            threshold = trauma_threshold_float
            trauma_level = min(
                1.0,
                (normalized_divergence - threshold) / (1.0 - threshold),
            )
        else:
            trauma_level = 0.0

        return float(trauma_level)

    def _calculate_blocking_strength(
        self, trauma_detection: float, integration_strength: Optional[float]
    ) -> float:
        """
        Calcula força de bloqueio.

        Bloqueio = resposta defensiva ao trauma.
        Quanto mais trauma, mais bloqueio necessário.

        Args:
            trauma_detection: Nível de trauma detectado
            integration_strength: Força de integração (opcional)

        Returns:
            float [0, 1] representando força de bloqueio
        """
        # Bloqueio baseado em trauma
        base_blocking = trauma_detection

        # Se integração está baixa, bloqueio aumenta (sistema vulnerável)
        if integration_strength is not None:
            vulnerability_factor = 1.0 - integration_strength
            blocking = base_blocking + 0.3 * vulnerability_factor
        else:
            blocking = base_blocking

        return float(np.clip(blocking, 0.0, 1.0))

    def _calculate_defensive_activation(
        self, module_outputs: Dict[str, np.ndarray], trauma_detection: float
    ) -> float:
        """
        Calcula ativação defensiva.

        Ativação = quanto os módulos estão "defendendo" (bloqueando fluxo).

        Args:
            module_outputs: Outputs de todos os módulos
            trauma_detection: Nível de trauma

        Returns:
            float [0, 1] representando ativação defensiva
        """
        if not module_outputs:
            return 0.0

        # Ativação = variância dos módulos (quanto estão "nervosos")
        activations = [np.linalg.norm(emb) for emb in module_outputs.values()]
        variance = float(np.var(activations))

        # Normaliza
        activation_level = min(1.0, variance / 10.0)

        # Combina com trauma
        defensive_activation = 0.6 * activation_level + 0.4 * trauma_detection

        return float(np.clip(defensive_activation, 0.0, 1.0))

    def _identify_blocked_modules(
        self, module_outputs: Dict[str, np.ndarray], trauma_detection: float
    ) -> List[str]:
        """
        Identifica módulos bloqueados.

        Módulos bloqueados = módulos com ativação muito baixa (defesa).

        Args:
            module_outputs: Outputs de todos os módulos
            trauma_detection: Nível de trauma

        Returns:
            List[str] com nomes dos módulos bloqueados
        """
        if trauma_detection < 0.3:
            return []  # Sem trauma suficiente para bloqueios

        blocked = []
        for module_name, embedding in module_outputs.items():
            activation = np.linalg.norm(embedding)
            # Se ativação muito baixa, está bloqueado
            if activation < 0.1:
                blocked.append(module_name)

        return blocked

    def _update_dynamic_threshold(self, delta_norm: float) -> None:
        """
        Atualiza threshold dinâmico baseado em histórico de Δ_norm.

        Threshold dinâmico = μ + kσ, onde:
        - μ = média do histórico de Δ_norm
        - σ = desvio padrão do histórico
        - k = multiplicador (padrão: 2.0 para μ+2σ, ou 3.0 para μ+3σ)

        Um evento de 3 desvios padrão é estatisticamente extremo (≈0.3% dos casos),
        o que se alinha com a ideia de trauma (evento raro e impactante).

        Args:
            delta_norm: Valor de Δ normalizado [0, 1] do ciclo atual
        """
        if not self.use_dynamic_threshold:
            return

        # Adiciona ao histórico
        self.delta_norm_history.append(delta_norm)

        # Mantém apenas últimos N valores (evita crescimento infinito)
        max_history = 1000
        if len(self.delta_norm_history) > max_history:
            self.delta_norm_history.pop(0)

        # Calcula threshold dinâmico apenas se histórico suficiente
        if len(self.delta_norm_history) >= self.min_history_size:
            history_array = np.array(self.delta_norm_history)
            mean_delta = float(np.mean(history_array))
            std_delta = float(np.std(history_array))

            # Threshold dinâmico = μ + kσ
            dynamic_threshold = mean_delta + (self.dynamic_threshold_k * std_delta)

            # Garante que threshold está em range razoável [0.3, 0.95]
            # (evita valores muito baixos ou muito altos)
            dynamic_threshold = float(np.clip(dynamic_threshold, 0.3, 0.95))

            # Atualiza threshold
            old_threshold = self.trauma_threshold
            self.trauma_threshold = dynamic_threshold

            self.logger.debug(
                f"Dynamic trauma threshold updated: {old_threshold:.4f} → "
                f"{self.trauma_threshold:.4f} (μ={mean_delta:.4f}, σ={std_delta:.4f}, "
                f"k={self.dynamic_threshold_k}, n={len(self.delta_norm_history)})"
            )
        else:
            # Histórico insuficiente: usa threshold estático
            self.trauma_threshold = self.trauma_threshold_static
