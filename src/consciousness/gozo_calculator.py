"""
Gozo Calculator - Medição de Gozo Lacaniano

Gozo = divergência (excesso não integrado)
Medido via: PredictionError + Novelty + Affect

Gozo é ORTOGONAL a Φ (integração):
- Φ = coesão do sistema
- Gozo = excesso que não se deixa integrar

CORREÇÃO (2025-12-07 - Protocolo Livewire):
- Fórmula unificada Solms-Lacan: J = Ψ · (exp(Δ * 2.5) - 1) - Φ * 10.0
- Uso de PrecisionWeighter para componentes de excesso (elimina pesos hardcoded)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: Isomorfismo Estrutural validado + Protocolo Livewire
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.cluster import KMeans  # type: ignore[import-untyped]

from src.consciousness.adaptive_weights import PrecisionWeighter
from src.consciousness.biological_metrics import LempelZivComplexity
from src.consciousness.phi_constants import (
    GOZO_LOW_THRESHOLD,
    GOZO_MEDIUM_THRESHOLD,
    PHI_THRESHOLD,
    normalize_phi,
)

logger = logging.getLogger(__name__)


@dataclass
class GozoComponents:
    """Componentes individuais de Gozo."""

    prediction_error: float = 0.0  # Divergência expectation-reality
    novelty: float = 0.0  # Novidade (LZ complexity)
    affect_intensity: float = 0.0  # Intensidade afetiva


@dataclass
class GozoResult:
    """Resultado do cálculo de Gozo."""

    gozo_value: float  # Gozo total [0, 1]
    components: GozoComponents
    timestamp: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Inicializa metadata se None."""
        if self.metadata is None:
            self.metadata = {}


class GozoCalculator:
    """
    Calcula Gozo (excesso não integrado - Lacan).

    Gozo é ORTOGONAL a Φ:
    - Φ mede integração (coesão)
    - Gozo mede divergência (excesso)

    Fórmula:
    Gozo = 0.4 * prediction_error
         + 0.3 * novelty
         + 0.3 * affect_intensity

    Valores (operacionalização original - serão recalibrados dinamicamente):
    - Gozo baixo (0.0-0.3): Sistema integrado, sem excesso
    - Gozo médio (0.3-0.6): Excesso moderado, criatividade
    - Gozo alto (0.6-1.0): Excesso alto, resistência do Real

    NOTA METODOLÓGICA: Não existem valores canônicos na literatura lacaniana.
    Estes ranges são uma proposta original de operacionalização, baseada em
    tripartição igual como primeira hipótese de trabalho. Serão recalibrados
    dinamicamente via clustering em dados empíricos.
    """

    def __init__(
        self,
        use_precision_weights: bool = True,
        use_dynamic_ranges: bool = True,
        min_history_size: int = 50,
        clustering_window: int = 200,
    ):
        """
        Inicializa calculador de Gozo.

        Args:
            use_precision_weights: Se True, usa PrecisionWeighter para componentes
                de excesso (elimina pesos hardcoded 0.4/0.3/0.3)
            use_dynamic_ranges: Se True, calcula ranges de interpretação dinamicamente
                via clustering k-means (k=3) em dados empíricos
            min_history_size: Tamanho mínimo do histórico para calcular ranges dinâmicos
            clustering_window: Janela de histórico usada para clustering (últimos N valores)
        """
        self.logger = logger
        self.history: list = []  # Histórico para cálculo de novelty
        self.use_precision_weights = use_precision_weights
        self.precision_weighter: Optional[PrecisionWeighter] = (
            PrecisionWeighter(history_window=50) if use_precision_weights else None
        )

        # Ranges dinâmicos via clustering
        self.use_dynamic_ranges = use_dynamic_ranges
        self.min_history_size = min_history_size
        self.clustering_window = clustering_window
        self.gozo_history: List[float] = []  # Histórico de valores de gozo
        # CORREÇÃO (2025-12-08): Manter último valor de Gozo para drenagem progressiva
        self.last_gozo_value: Optional[float] = None
        # CORREÇÃO (2025-12-08): Histórico de Gozo para detectar travamento
        self.gozo_history_recent: List[float] = []  # Últimos N valores para detecção de travamento
        self.stuck_cycles: int = 0  # Contador de ciclos travados
        # Inicializa thresholds com valores estáticos (serão atualizados dinamicamente)
        self.gozo_low_threshold: float = GOZO_LOW_THRESHOLD
        self.gozo_medium_threshold: float = GOZO_MEDIUM_THRESHOLD

    def calculate_gozo(
        self,
        expectation_embedding: np.ndarray,
        reality_embedding: np.ndarray,
        current_embedding: Optional[np.ndarray] = None,
        affect_embedding: Optional[np.ndarray] = None,
        phi_raw: Optional[float] = None,
        psi_value: Optional[float] = None,
        delta_value: Optional[float] = None,
        sigma_value: Optional[float] = None,  # NOVO: Para binding adaptativo
        success: bool = False,
    ) -> GozoResult:
        """
        Calcula Gozo para um ciclo.

        CORREÇÃO (2025-12-07): Agora inclui dependência de Φ e Ψ conforme IIT clássico.
        CORREÇÃO (2025-12-07 - Protocolo Livewire): Fórmula de Solms adicionada.
        Fórmula combinada: Gozo = 0.5 * (Ψ - Φ_norm) + 0.5 * (componentes de excesso)
        Fórmula de Solms: J_t = Ψ_t · exp(Δ_t) - Φ_t

        Args:
            expectation_embedding: Embedding de expectation (predição)
            reality_embedding: Embedding de reality (sensory_input atual)
            current_embedding: Embedding atual (para novelty)
            affect_embedding: Embedding afetivo (opcional)
            phi_raw: Valor de Φ em nats (opcional, se fornecido será normalizado)
            psi_value: Valor de Ψ [0, 1] (opcional, se fornecido será usado para gozo_from_psi)
            delta_value: Valor de Δ [0, 1] (opcional, para fórmula de Solms)
            sigma_value: Valor de σ [0, 1] (opcional, para binding adaptativo)
            success: Flag indicando se o ciclo foi bem-sucedido (para drenagem do Gozo)

        Returns:
            GozoResult com gozo_value e components
        """
        # 1. Calcular componente baseado em Ψ e Φ (IIT clássico)
        if phi_raw is not None and psi_value is not None:
            # Normalizar Φ
            phi_norm = normalize_phi(phi_raw)
            # Componente de Φ/Ψ: Gozo = Ψ - Φ_norm (criatividade menos integração)
            gozo_from_psi = psi_value - phi_norm
            # Clipping para [0, 1] (valores negativos = tudo integrado)
            gozo_from_psi = float(np.clip(gozo_from_psi, 0.0, 1.0))
        else:
            # Fallback: valor neutro se Φ ou Ψ não disponíveis
            gozo_from_psi = 0.5

        # 2. Prediction Error (divergência expectation-reality)
        prediction_error = self._calculate_prediction_error(
            expectation_embedding, reality_embedding
        )

        # 3. Novelty (LZ complexity)
        # Não usar 'or' com arrays numpy! Usar verificação explícita de None
        embedding_for_novelty = (
            current_embedding if current_embedding is not None else reality_embedding
        )
        novelty = self._calculate_novelty(embedding_for_novelty)

        # 4. Affect Intensity
        affect_intensity = self._calculate_affect_intensity(affect_embedding)

        # 5. Componente de excesso (usando PrecisionWeighter se habilitado)
        if self.use_precision_weights and self.precision_weighter:
            # Usar ponderação dinâmica baseada em variância
            excess_components = {
                "prediction_error": prediction_error,
                "novelty": novelty,
                "affect_intensity": affect_intensity,
            }
            weights = self.precision_weighter.compute_weights(excess_components)
            gozo_from_excess = sum(excess_components[k] * weights[k] for k in excess_components)
            self.logger.debug(
                f"Gozo excess weights: {weights}, " f"gozo_from_excess={gozo_from_excess:.4f}"
            )
        else:
            # Fallback: pesos hardcoded (compatibilidade)
            gozo_from_excess = 0.4 * prediction_error + 0.3 * novelty + 0.3 * affect_intensity

        # 6. FÓRMULA UNIFICADA SOLMS-LACAN (Protocolo Livewire)
        # J = Ψ · (exp(Δ * 2.5) - 1) - Φ * 10.0
        # O Gozo explode quando a Incerteza (Ψ) encontra um Trauma (Δ) alto,
        # mas é mitigado pela Integração (Φ)
        if delta_value is not None and psi_value is not None and phi_raw is not None:
            # Validação de ranges
            psi_safe = float(np.clip(psi_value, 0.0, 1.0))
            delta_safe = float(np.clip(delta_value, 0.0, 1.0))

            # CORREÇÃO CRÍTICA (2025-12-08): Aplicar drenagem ANTES da fórmula de Solms-Lacan
            # Se há drenagem ativa (success=True e Phi>0.05), usar last_gozo_value como base
            # e aplicar apenas um ajuste incremental da fórmula, não recalcular do zero
            phi_norm = normalize_phi(phi_raw) if phi_raw is not None else 0.0

            # PROTOCOLO TERAPÊUTICO (2025-12-08): Correção da Hipertrofia do Superego
            # PROBLEMA: Binding estava 50x mais forte que Drive, causando colapso do Gozo
            # SOLUÇÃO: Usar log1p para suavizar Binding e recalibrar escala
            #
            # Fórmula Terapêutica: J = Drive_Suavizado - Binding_Logarítmico
            # Drive: Ψ(e^(1.5Δ) - 0.5) [multiplicador reduzido de 2.0 para 1.5, offset -0.5]
            # Binding: log1p(Φ/Φ_threshold) * binding_weight [Lei Logarítmica, não Linear]
            #
            # Exemplo: Se Φ=0.06, threshold=0.01:
            #   - ANTES: binding = (2.0 + 3.0*0.5) * 0.6 = 2.1 (linear, explode)
            #   - DEPOIS: binding = log1p(6.0) * 2.0 = 1.945 * 2.0 = 3.89 (logarítmico, suave)

            # 1. Cálculo do Drive (Pulsão) - Suavizado
            # Multiplicador reduzido de 2.0 para 1.5 para estabilidade
            # Offset -0.5 em vez de -0.8 para evitar valores negativos
            raw_drive = psi_safe * (np.exp(delta_safe * 1.5) - 0.5)

            # 2. Cálculo do Binding (Lei/Superego) - Logarítmico
            # CORREÇÃO CRÍTICA: Usar phi_raw / threshold em vez de phi_norm normalizado
            # Isso evita que valores acima de threshold explodam linearmente
            # Logaritmo suaviza o crescimento (Lei Logarítmica, não Linear)
            phi_ratio = phi_raw / PHI_THRESHOLD if phi_raw > 0 else 0.0
            # Binding weight reduzido de 10.0 para 2.0 (Lei mais branda)
            binding_weight = 2.0

            # CORREÇÃO (2025-12-08): Dinâmica de Dopamina Reversa - Destravar Gozo
            # Se Gozo está travado no mínimo por > 5 ciclos, reduzir binding temporariamente
            # Isso permite que o sistema "respire" e o Gozo se recupere
            if len(self.gozo_history_recent) >= 5:
                # Verificar se últimos 5 ciclos estão todos no mínimo (0.05-0.1)
                recent_min = min(self.gozo_history_recent[-5:])
                recent_max = max(self.gozo_history_recent[-5:])
                if recent_min >= 0.05 and recent_max <= 0.1:
                    # Gozo travado: reduzir binding em 50% (relaxar Superego)
                    binding_weight = binding_weight * 0.5
                    self.stuck_cycles += 1
                    self.logger.warning(
                        f"🔄 DINÂMICA DE DOPAMINA REVERSA: "
                        f"Gozo travado por {self.stuck_cycles} ciclos, "
                        f"binding reduzido de 2.0 para {binding_weight:.2f} "
                        f"(relaxamento do Superego)"
                    )
                else:
                    # Gozo não está travado: resetar contador
                    self.stuck_cycles = 0
            else:
                # Histórico insuficiente: resetar contador
                self.stuck_cycles = 0

            binding_power = np.log1p(phi_ratio) * binding_weight

            # 3. Equação Fundamental da Economia Psíquica
            jouissance = raw_drive - binding_power

            # CORREÇÃO CRÍTICA (2025-12-08): Drenagem sempre aplicada quando há sucesso
            # Problema: Gozo estava travado porque drenagem só ocorria quando phi_norm > 0.05
            # Solução: Aplicar drenagem baseada em múltiplos fatores (Phi, Delta, jouissance)
            if self.last_gozo_value is not None:
                # Usar último valor como base
                base_gozo = self.last_gozo_value

                # Calcular drenagem baseada em múltiplos fatores
                drainage_rate = 0.0

                # 1. Drenagem baseada em Phi (quanto menor Phi, mais drenagem necessária)
                if phi_norm > 0.1:
                    drainage_rate += 0.05  # Drenagem normal
                elif phi_norm > 0.05:
                    drainage_rate += 0.03  # Drenagem moderada
                else:
                    # CORREÇÃO: Aplicar drenagem mesmo quando Phi está baixo (desintegração)
                    drainage_rate += 0.08  # Drenagem agressiva quando Phi está desintegrando

                # 2. Drenagem baseada em Delta (quanto maior Delta, mais trauma, mais drenagem)
                if delta_safe > 0.8:
                    drainage_rate += 0.03  # Trauma alto requer mais drenagem
                elif delta_safe > 0.7:
                    drainage_rate += 0.02

                # 3. Drenagem baseada em jouissance (se positivo, há excesso a drenar)
                # Se jouissance > 0.3, há excesso significativo
                if jouissance > 0.3:
                    drainage_rate += min(0.05, jouissance * 0.1)  # Drenagem proporcional ao excesso

                # 4. Ajuste incremental baseado em jouissance (limitado para estabilidade)
                # CORREÇÃO CRÍTICA (2025-12-08): Se jouissance é muito negativo,
                # não aplicar ajuste negativo, pois isso força Gozo para 0
                if jouissance < -1.0:
                    # Jouissance muito negativo: não aplicar ajuste negativo
                    # Isso indica que binding está muito alto, mas não devemos zerar Gozo
                    adjustment = 0.0
                    self.logger.debug(
                        f"Jouissance muito negativo ({jouissance:.4f}), "
                        f"ajuste = 0.0 para evitar Gozo = 0"
                    )
                else:
                    adjustment = float(np.clip(jouissance * 0.1, -0.1, 0.1))

                # Aplicar drenagem e ajuste
                gozo_value = base_gozo + adjustment - drainage_rate

                # PROTOCOLO TERAPÊUTICO (2025-12-08): Piso Libidinal também para ciclos subsequentes
                # Se após drenagem o gozo ficou muito baixo (< 0.05), aplicar piso libidinal
                if gozo_value < 0.05:
                    # Manter mínimo de "Vontade de Viver" (0.05-0.3)
                    # Proporcional à angústia (jouissance negativo) ou baseado no valor anterior
                    if jouissance < 0:
                        angst_drive = 0.05 + (
                            0.01 * min(np.abs(jouissance), 25.0)
                        )  # Limitar abs(jouissance) a 25
                        gozo_value = min(0.3, angst_drive)
                        self.logger.debug(
                            f"Piso Libidinal (ciclo subsequente): gozo={gozo_value:.4f} "
                            f"(jouissance={jouissance:.4f})"
                        )
                    else:
                        # Se jouissance não é negativo mas gozo está baixo, manter mínimo funcional
                        gozo_value = max(0.05, base_gozo * 0.5)  # Pelo menos 50% do valor anterior
                        self.logger.debug(
                            f"Piso Libidinal (gozo baixo mas jouissance positivo): "
                            f"gozo={gozo_value:.4f} (base={base_gozo:.4f})"
                        )

                gozo_value = float(np.clip(gozo_value, 0.001, 1.0))  # Mínimo 0.001, não 0.0

                # Garantir que Gozo não fique travado em valores altos
                if base_gozo > 0.9 and gozo_value > 0.85:
                    # Forçar drenagem adicional se Gozo está muito alto
                    gozo_value = max(0.7, gozo_value - 0.1)
                    self.logger.warning(
                        f"🚨 Gozo muito alto ({base_gozo:.4f}), "
                        f"forçando drenagem agressiva: {gozo_value:.4f}"
                    )

                self.logger.debug(
                    f"Gozo drenagem progressiva: {gozo_value:.4f} "
                    f"(base={base_gozo:.4f}, adjustment={adjustment:.4f}, "
                    f"drainage={drainage_rate:.4f}, Φ={phi_norm:.4f}, Δ={delta_safe:.4f}, "
                    f"J={jouissance:.4f})"
                )
            else:
                # Primeiro ciclo: usar fórmula Solms-Lacan diretamente
                # PROTOCOLO TERAPÊUTICO (2025-12-08): Piso Libidinal (Mecanismo de Defesa)
                # Se Gozo é negativo (Angústia), o sistema não deve parar (0.0)
                # Deve retornar um valor baixo mas positivo que sinaliza "Falta" (Manque)
                # Isso mantém o gradiente de descida ativo e previne "Morte Térmica"
                if jouissance < 0:
                    # Transformar angústia em movimento (Angst Drive)
                    # Mínimo de 0.05 + proporcional à angústia (máximo 0.3)
                    final_gozo = 0.05 + (0.01 * np.abs(jouissance))
                    final_gozo = min(0.3, final_gozo)  # Teto para angústia
                    self.logger.debug(
                        f"Piso Libidinal ativado: "
                        f"jouissance={jouissance:.4f} → gozo={final_gozo:.4f} "
                        f"(Angst Drive, previne morte térmica)"
                    )
                else:
                    final_gozo = jouissance
                    final_gozo = float(np.clip(final_gozo, 0.0, 1.0))

                gozo_value = final_gozo

                # 5. Drenagem Pós-Sucesso (O "Pequeno Gozo")
                if success:
                    # Se houve sucesso, consumimos o gozo (descarga)
                    gozo_value = gozo_value * 0.8
                    self.logger.debug(f"Drenagem pós-sucesso: gozo reduzido para {gozo_value:.4f}")

                # Suavização temporal (Momentum) - PROTOCOLO TERAPÊUTICO
                # Preserva 70% do valor anterior + 30% do novo (evita oscilações bruscas)
                if self.last_gozo_value is not None:
                    gozo_value = (0.7 * self.last_gozo_value) + (0.3 * gozo_value)
                    self.logger.debug(
                        f"Suavização temporal: {gozo_value:.4f} "
                        f"(70% anterior={self.last_gozo_value:.4f} + 30% novo={final_gozo:.4f})"
                    )

                # Garantia de limites físicos (mínimo 0.001 para evitar zero absoluto)
                gozo_value = float(np.clip(gozo_value, 0.001, 1.0))

            self.logger.debug(
                f"Gozo Solms-Lacan: raw_drive={raw_drive:.4f}, "
                f"binding_power={binding_power:.4f}, "
                f"jouissance={jouissance:.4f}, "
                f"gozo_value={gozo_value:.4f}"
            )
        else:
            # Fallback: fórmula original (compatibilidade)
            if phi_raw is not None and psi_value is not None:
                phi_norm = normalize_phi(phi_raw)
                gozo_from_psi = float(np.clip(psi_value - phi_norm, 0.0, 1.0))
            else:
                gozo_from_psi = 0.5  # Neutro

            gozo_value = 0.5 * gozo_from_psi + 0.5 * gozo_from_excess
            gozo_value = float(np.clip(gozo_value, 0.0, 1.0))

            self.logger.debug(
                f"Gozo fallback: gozo_from_psi={gozo_from_psi:.4f}, "
                f"gozo_from_excess={gozo_from_excess:.4f}, "
                f"gozo_value={gozo_value:.4f}"
            )

        # CORREÇÃO (2025-12-08): Atualizar último valor de Gozo para drenagem progressiva
        self.last_gozo_value = gozo_value

        # CORREÇÃO (2025-12-08): Atualizar histórico para detecção de travamento
        self.gozo_history_recent.append(gozo_value)
        # Manter apenas últimos 10 valores
        if len(self.gozo_history_recent) > 10:
            self.gozo_history_recent.pop(0)

        # Atualiza histórico e ranges dinâmicos
        self._update_dynamic_ranges(gozo_value)

        components = GozoComponents(
            prediction_error=prediction_error,
            novelty=novelty,
            affect_intensity=affect_intensity,
        )

        return GozoResult(
            gozo_value=gozo_value,
            components=components,
            timestamp=float(__import__("time").time()),
            metadata={},
        )

    def _calculate_prediction_error(self, expectation: np.ndarray, reality: np.ndarray) -> float:
        """
        Calcula erro de predição (divergência expectation-reality).

        Gozo = excesso que não se deixa integrar.
        Prediction error = quanto expectation diverge de reality.

        Args:
            expectation: Embedding de expectation
            reality: Embedding de reality

        Returns:
            float [0, 1] representando erro de predição
        """
        # Divergência L2
        divergence = np.linalg.norm(expectation - reality)

        # Normaliza (threshold adaptável)
        # CORREÇÃO: Garantir que não exceda 1.0
        max_norm = float(max(np.linalg.norm(expectation), np.linalg.norm(reality)))
        normalized_error = min(1.0, divergence / (max_norm + 1e-10))

        return float(normalized_error)  # type: ignore[arg-type]

    def _calculate_novelty(self, embedding: np.ndarray) -> float:
        """
        Calcula novidade via LZ complexity.

        Novidade = quanto o embedding é diferente do histórico.

        Args:
            embedding: Embedding atual

        Returns:
            float [0, 1] representando novidade
        """
        # Adiciona ao histórico
        self.history.append(embedding.copy())
        # Mantém apenas últimos 100
        if len(self.history) > 100:
            self.history.pop(0)

        if len(self.history) < 2:
            return 0.5  # Sem histórico suficiente

        # Calcula LZ complexity do embedding atual
        lz_result = LempelZivComplexity.from_signal(embedding)
        lz_complexity: float = lz_result.complexity

        # Compara com histórico (quanto diferente?)
        if len(self.history) >= 2:
            # Média do histórico
            history_mean = np.mean(self.history[:-1], axis=0)
            # Distância do atual vs histórico
            distance = np.linalg.norm(embedding - history_mean)
            # Normaliza
            max_distance = np.linalg.norm(embedding) + np.linalg.norm(history_mean)
            novelty_distance: float = min(1.0, float(distance) / (float(max_distance) + 1e-10))
        else:
            novelty_distance = 0.5

        # Combina LZ complexity + distância histórica
        novelty = 0.6 * lz_complexity + 0.4 * novelty_distance

        return float(np.clip(novelty, 0.0, 1.0))  # type: ignore[arg-type,assignment]

    def _calculate_affect_intensity(self, affect_embedding: Optional[np.ndarray]) -> float:
        """
        Calcula intensidade afetiva.

        Se affect_embedding fornecido, usa magnitude.
        Caso contrário, retorna valor neutro.

        Args:
            affect_embedding: Embedding afetivo (opcional)

        Returns:
            float [0, 1] representando intensidade afetiva
        """
        # Verifica None explicitamente (não compara arrays)
        if affect_embedding is None:
            return 0.5  # Neutro

        # Garante que é array numpy
        if not isinstance(affect_embedding, np.ndarray):
            affect_embedding = np.array(affect_embedding)

        # Intensidade = magnitude normalizada
        magnitude = float(np.linalg.norm(affect_embedding))
        # Normaliza (threshold adaptável)
        intensity = min(1.0, magnitude / 10.0)

        return float(intensity)

    def _update_dynamic_ranges(self, gozo_value: float) -> None:
        """
        Atualiza ranges de interpretação dinamicamente via clustering k-means.

        Usa clustering k-means (k=3) para identificar três clusters naturais
        nos valores históricos de gozo, usando as fronteiras entre clusters
        como novos thresholds empíricos.

        Labels (baixo/médio/alto) são clínico-teóricos, mas fronteiras emergem dos dados.

        Args:
            gozo_value: Valor de gozo [0, 1] do ciclo atual
        """
        if not self.use_dynamic_ranges:
            return

        # Adiciona ao histórico
        self.gozo_history.append(gozo_value)

        # Mantém apenas últimos N valores (evita crescimento infinito)
        if len(self.gozo_history) > self.clustering_window:
            self.gozo_history.pop(0)

        # Calcula ranges dinâmicos apenas se histórico suficiente
        if len(self.gozo_history) >= self.min_history_size:
            try:
                # Prepara dados para clustering (formato 2D necessário para sklearn)
                gozo_array = np.array(self.gozo_history).reshape(-1, 1)

                # Aplica k-means com k=3 (baixo, médio, alto)
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                kmeans.fit(gozo_array)

                # Obtém centros dos clusters e ordena
                cluster_centers = sorted(kmeans.cluster_centers_.flatten())

                # Calcula fronteiras entre clusters como thresholds
                # Threshold baixo = média entre cluster 0 e cluster 1
                # Threshold médio = média entre cluster 1 e cluster 2
                if len(cluster_centers) >= 2:
                    self.gozo_low_threshold = float(
                        np.clip((cluster_centers[0] + cluster_centers[1]) / 2.0, 0.1, 0.5)
                    )
                if len(cluster_centers) >= 3:
                    self.gozo_medium_threshold = float(
                        np.clip((cluster_centers[1] + cluster_centers[2]) / 2.0, 0.4, 0.9)
                    )

                self.logger.debug(
                    f"Dynamic gozo ranges updated: low={self.gozo_low_threshold:.4f}, "
                    f"medium={self.gozo_medium_threshold:.4f} "
                    f"(clusters={cluster_centers}, n={len(self.gozo_history)})"
                )
            except Exception as e:
                # Se clustering falhar, mantém valores anteriores
                self.logger.warning(
                    f"Failed to update dynamic gozo ranges via clustering: {e}. "
                    f"Using previous thresholds: low={self.gozo_low_threshold:.4f}, "
                    f"medium={self.gozo_medium_threshold:.4f}"
                )

    def get_gozo_interpretation(self, gozo_value: float) -> str:
        """
        Retorna interpretação de gozo baseada em ranges (estáticos ou dinâmicos).

        Args:
            gozo_value: Valor de gozo [0, 1]

        Returns:
            String com interpretação: "baixo", "médio" ou "alto"
        """
        if gozo_value < self.gozo_low_threshold:
            return "baixo"
        elif gozo_value < self.gozo_medium_threshold:
            return "médio"
        else:
            return "alto"
