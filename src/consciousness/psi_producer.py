"""
Psi Producer (Ψ_produtor) - Métrica de Produção Criativa (Deleuze)

Implementa Ψ como dimensão ortogonal independente de Φ (IIT).

CORREÇÃO (2025-12-07): Adicionada dependência gaussiana de Φ conforme IIT clássico.
FASE 3 (2025-12-07): Integração de PrecisionWeighter e alpha dinâmico baseado em Φ.
Fórmula: Ψ = alpha(Φ) * gaussiana(Φ - Φ_optimal) + (1-alpha(Φ)) * (componentes de criatividade)
Onde alpha(Φ) = clip(Φ * 10.0, 0.3, 0.7) - Se Φ alto, confia mais na estrutura (Gaussian)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: VERIFICACAO_PHI_SISTEMA.md
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from src.consciousness.adaptive_weights import PrecisionWeighter
from src.consciousness.novelty_generator import NoveltyDetector, NoveltyMetric
from src.consciousness.phi_constants import calculate_psi_gaussian, normalize_phi
from src.embeddings.code_embeddings import OmniMindEmbeddings

logger = logging.getLogger(__name__)

# DEPRECATED: PSI_WEIGHTS removido (FASE 3 - Protocolo Livewire)
# Substituído por PrecisionWeighter para pesos dinâmicos baseados em variância (FEP)
# Mantido apenas para compatibilidade retroativa
PSI_WEIGHTS = {
    "innovation": 0.4,  # Inovação (novelty_score) - DEPRECATED
    "surprise": 0.3,  # Surpresa (surprise_score) - DEPRECATED
    "relevance": 0.3,  # Relevância (relevance_score) - DEPRECATED
}


@dataclass
class PsiComponents:
    """Componentes individuais de Ψ."""

    innovation_score: float = 0.0  # Novelty (via NoveltyDetector)
    surprise_score: float = 0.0  # Surprise (via NoveltyDetector)
    relevance_score: float = 0.0  # Relevância semântica (via embeddings)
    entropy_of_actions: float = 0.0  # Diversidade de ações (Shannon entropy)


@dataclass
class PsiResult:
    """Resultado do cálculo de Ψ."""

    psi_raw: float  # Ψ não normalizado
    psi_norm: float  # Ψ normalizado [0, 1]
    components: PsiComponents
    step_id: str
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class PsiProducer:
    """
    Calcula Ψ_produtor (produção criativa - Deleuze).

    Ψ é ortogonal a Φ (IIT):
    - Φ mede integração (ordem)
    - Ψ mede produção (criatividade/caos)
    - São dimensões independentes

    Fórmula (FASE 3 - com PrecisionWeighter):
    Ψ = alpha(Φ) * psi_gaussian + (1-alpha(Φ)) * psi_from_creativity
    Onde psi_from_creativity usa pesos dinâmicos baseados em variância (FEP)

    Fallback (use_precision_weights=False):
    Ψ = 0.4 * innovation_score + 0.3 * surprise_score + 0.3 * relevance_score

    Entropy_of_actions é usado como validação (correlação esperada r > 0.6).
    """

    def __init__(
        self,
        novelty_detector: Optional[NoveltyDetector] = None,
        embedding_model: Optional[OmniMindEmbeddings] = None,
        use_precision_weights: bool = True,
        use_dynamic_alpha: bool = True,
        min_history_size: int = 30,
        performance_window: int = 100,
    ):
        """
        Inicializa PsiProducer.

        Args:
            novelty_detector: Instância opcional de NoveltyDetector (cria novo se None)
            embedding_model: Instância opcional de OmniMindEmbeddings (cria novo se None)
            use_precision_weights: Se True, usa PrecisionWeighter para pesos dinâmicos (FASE 3)
            use_dynamic_alpha: Se True, ajusta alpha dinamicamente baseado em desempenho
            min_history_size: Tamanho mínimo do histórico para calcular alpha dinâmico
            performance_window: Janela de histórico usada para análise de desempenho
        """
        self.novelty_detector = novelty_detector or NoveltyDetector()
        self.embedding_model = embedding_model
        self.logger = logger
        self.use_precision_weights = use_precision_weights
        self.precision_weighter: Optional[PrecisionWeighter] = (
            PrecisionWeighter(history_window=30) if use_precision_weights else None
        )

        # Alpha dinâmico baseado em desempenho
        self.use_dynamic_alpha = use_dynamic_alpha
        self.min_history_size = min_history_size
        self.performance_window = performance_window
        self.performance_history: List[Dict[str, float]] = []  # Histórico de desempenho
        self.alpha_min: float = 0.3  # Mínimo de estrutura (será atualizado dinamicamente)
        self.alpha_max: float = 0.7  # Máximo de estrutura (será atualizado dinamicamente)

    def calculate_psi_for_step(
        self,
        step_content: str,
        previous_steps: List[str],
        goal: str,
        actions: List[str],
        step_id: str = "",
        phi_raw: Optional[float] = None,
    ) -> PsiResult:
        """
        Calcula Ψ_produtor para um passo de pensamento.

        CORREÇÃO (2025-12-07): Agora inclui dependência gaussiana de Φ conforme IIT clássico.
        Fórmula combinada: Ψ = 0.5 * gaussiana(Φ - Φ_optimal) + 0.5 * (componentes de criatividade)

        Args:
            step_content: Conteúdo do passo atual
            previous_steps: Lista de passos anteriores (para contexto)
            goal: Objetivo da sessão (para relevância)
            actions: Lista de ações tomadas (para entropia)
            step_id: ID único do passo
            phi_raw: Valor de Φ em nats (opcional, se fornecido será usado para gaussiana)

        Returns:
            PsiResult com psi_raw, psi_norm, components
        """
        # 1. Componente gaussiano de Φ (IIT clássico)
        if phi_raw is not None:
            psi_gaussian = calculate_psi_gaussian(phi_raw)
        else:
            # Fallback: valor neutro se Φ não fornecido
            psi_gaussian = 0.5

        # 2. Innovation score (via NoveltyDetector)
        innovation_score = self._calculate_innovation_score(step_content, previous_steps)

        # 3. Surprise score (via NoveltyDetector)
        surprise_score = self._calculate_surprise_score(step_content, previous_steps)

        # 4. Relevance score (via embeddings)
        relevance_score = self._calculate_relevance_score(step_content, goal)

        # 5. Entropy of actions (Shannon entropy)
        entropy_of_actions = self._calculate_entropy_of_actions(actions)

        # 6. Componente de criatividade (com PrecisionWeighter ou fallback)
        component_values = {
            "innovation": innovation_score,
            "surprise": surprise_score,
            "relevance": relevance_score,
        }
        if self.use_precision_weights and self.precision_weighter:
            weights = self.precision_weighter.compute_weights(component_values)
            psi_from_creativity = sum(component_values[k] * weights[k] for k in component_values)
            self.logger.debug(f"PsiProducer: Pesos dinâmicos calculados: {weights}")
        else:
            # Fallback para pesos hardcoded (compatibilidade)
            psi_from_creativity = (
                PSI_WEIGHTS["innovation"] * innovation_score
                + PSI_WEIGHTS["surprise"] * surprise_score
                + PSI_WEIGHTS["relevance"] * relevance_score
            )

        # 7. COMBINAR: Alpha dinâmico baseado em Φ (FASE 3)
        # Se Phi (integração) é alto, o sistema confia mais na estrutura (Gaussian)
        # Se Phi é baixo, confia mais na criatividade bruta
        if phi_raw is not None:
            # Normalizar phi_raw para [0, 1] se necessário
            phi_norm = (
                normalize_phi(phi_raw) if phi_raw > 1.0 else float(np.clip(phi_raw, 0.0, 1.0))
            )
            # Alpha dinâmico usando constantes empíricas
            # Range (0.3, 0.7) garante mínimo de cada componente (estrutura e criatividade)
            from src.consciousness.phi_constants import PSI_ALPHA_MAX, PSI_ALPHA_MIN

            # Phi alto (0.8) -> alpha = 0.7 (confia mais em Gaussian)
            # Phi baixo (0.1) -> alpha = 0.3 (confia mais em criatividade)
            alpha = float(np.clip(phi_norm * 10.0, PSI_ALPHA_MIN, PSI_ALPHA_MAX))
        else:
            # Fallback: usar 0.5 se phi_raw não fornecido
            alpha = 0.5
            self.logger.debug("PsiProducer: phi_raw não fornecido, usando alpha=0.5 (fallback)")

        psi_raw = alpha * psi_gaussian + (1.0 - alpha) * psi_from_creativity

        # 8. Normalizar para [0, 1] com clipping
        psi_norm = self._normalize_psi(psi_raw)

        # Criar componentes
        components = PsiComponents(
            innovation_score=innovation_score,
            surprise_score=surprise_score,
            relevance_score=relevance_score,
            entropy_of_actions=entropy_of_actions,
        )

        # Registra desempenho para ajuste dinâmico de alpha
        self._record_performance(psi_norm, psi_from_creativity, psi_gaussian, alpha)

        return PsiResult(
            psi_raw=psi_raw,
            psi_norm=psi_norm,
            components=components,
            step_id=step_id,
        )

    def _calculate_innovation_score(self, step_content: str, previous_steps: List[str]) -> float:
        """
        Calcula innovation_score usando NoveltyDetector.

        Args:
            step_content: Conteúdo do passo atual
            previous_steps: Passos anteriores (para contexto)

        Returns:
            Innovation score [0, 1]
        """
        # Registrar passos anteriores como conceitos conhecidos
        for prev_step in previous_steps:
            self.novelty_detector.register_concept(prev_step)

        # Medir novidade do passo atual
        innovation = self.novelty_detector.measure_novelty(
            step_content, metric=NoveltyMetric.STATISTICAL_RARITY
        )

        return float(np.clip(innovation, 0.0, 1.0))

    def _calculate_surprise_score(self, step_content: str, previous_steps: List[str]) -> float:
        """
        Calcula surprise_score usando NoveltyDetector.

        Args:
            step_content: Conteúdo do passo atual
            previous_steps: Passos anteriores (para contexto)

        Returns:
            Surprise score [0, 1]
        """
        # Registrar passos anteriores
        for prev_step in previous_steps:
            self.novelty_detector.register_concept(prev_step)

        # Medir surpresa do passo atual
        surprise = self.novelty_detector.measure_novelty(
            step_content, metric=NoveltyMetric.SURPRISE_VALUE
        )

        return float(np.clip(surprise, 0.0, 1.0))

    def _calculate_relevance_score(self, step_content: str, goal: str) -> float:
        """
        Calcula relevance_score usando similaridade semântica.

        Args:
            step_content: Conteúdo do passo atual
            goal: Objetivo da sessão

        Returns:
            Relevance score [0, 1] (similaridade cosseno)
        """
        if not goal or not step_content:
            return 0.5  # Default neutro

        # Usar embedding model se disponível
        if self.embedding_model is not None:
            try:
                # Gerar embeddings
                model = self.embedding_model.model
                if model is not None:
                    step_embedding = model.encode(step_content)  # type: ignore[union-attr]
                    goal_embedding = model.encode(goal)  # type: ignore[union-attr]

                # Calcular similaridade cosseno
                step_norm = np.linalg.norm(step_embedding)
                goal_norm = np.linalg.norm(goal_embedding)

                if step_norm > 0 and goal_norm > 0:
                    cosine_sim = np.dot(step_embedding, goal_embedding) / (step_norm * goal_norm)
                    relevance = float(np.clip(cosine_sim, 0.0, 1.0))
                else:
                    relevance = 0.5
            except Exception as e:
                self.logger.warning(f"Erro ao calcular relevance_score: {e}")
                relevance = 0.5
        else:
            # Fallback: similaridade simples baseada em palavras
            step_words = set(step_content.lower().split())
            goal_words = set(goal.lower().split())
            if goal_words:
                overlap = len(step_words & goal_words) / len(goal_words)
                relevance = float(np.clip(overlap, 0.0, 1.0))
            else:
                relevance = 0.5

        return relevance

    def _calculate_entropy_of_actions(self, actions: List[str]) -> float:
        """
        Calcula entropia de Shannon para diversidade de ações.

        Args:
            actions: Lista de ações (tipos de ação, tool calls, etc.)

        Returns:
            Entropia normalizada [0, 1]
        """
        if not actions or len(actions) < 2:
            return 0.0

        # Contar frequências de cada tipo de ação
        action_counts: Dict[str, int] = {}
        for action in actions:
            # Normalizar ação (pegar tipo base)
            action_type = action.split("(")[0].strip() if "(" in action else action.strip()
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        # Calcular probabilidades
        total = len(actions)
        probabilities = [count / total for count in action_counts.values()]

        # Shannon entropy: H = -Σ(p * log2(p))
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)

        # Normalizar para [0, 1]
        # Máxima entropia = log2(n_unique_actions)
        max_entropy = math.log2(len(action_counts)) if len(action_counts) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return float(np.clip(normalized_entropy, 0.0, 1.0))

    def _normalize_psi(self, psi_raw: float) -> float:
        """
        Normaliza Ψ para [0, 1] com clipping.

        Args:
            psi_raw: Ψ não normalizado

        Returns:
            Ψ normalizado [0, 1]
        """
        # Clipping direto (já está na faixa esperada devido aos pesos)
        psi_norm = float(np.clip(psi_raw, 0.0, 1.0))

        return psi_norm

    def _get_dynamic_alpha(
        self, alpha_base: float, psi_from_creativity: float, psi_gaussian: float
    ) -> float:
        """
        Calcula alpha dinâmico baseado em desempenho histórico.

        Alpha é ajustado adaptativamente:
        - Se sistema produz muitas respostas "chatas"/repetitivas → alpha_max diminui
          (forçando mais criatividade)
        - Se produz muitas respostas incoerentes → alpha_min aumenta
          (forçando mais estrutura)

        Args:
            alpha_base: Alpha base calculado a partir de Φ (range empírico)
            psi_from_creativity: Componente de criatividade
            psi_gaussian: Componente gaussiano (estrutura)

        Returns:
            Alpha ajustado dinamicamente [alpha_min, alpha_max]
        """
        if not self.use_dynamic_alpha:
            from src.consciousness.phi_constants import PSI_ALPHA_MAX, PSI_ALPHA_MIN

            return float(np.clip(alpha_base, PSI_ALPHA_MIN, PSI_ALPHA_MAX))

        # Se histórico insuficiente, usa valores estáticos
        if len(self.performance_history) < self.min_history_size:
            from src.consciousness.phi_constants import PSI_ALPHA_MAX, PSI_ALPHA_MIN

            self.alpha_min = PSI_ALPHA_MIN
            self.alpha_max = PSI_ALPHA_MAX
            return float(np.clip(alpha_base, PSI_ALPHA_MIN, PSI_ALPHA_MAX))

        # Analisa desempenho histórico para ajustar alpha
        try:
            # Calcula métricas de desempenho
            recent_performance = self.performance_history[-self.performance_window :]
            creativity_scores = [p["psi_from_creativity"] for p in recent_performance]
            gaussian_scores = [p["psi_gaussian"] for p in recent_performance]

            # Taxa de "colapso" em soluções redundantes (pouca novidade)
            # Se criatividade está muito baixa, sistema está "chato"
            avg_creativity = float(np.mean(creativity_scores))
            redundancy_rate = 1.0 - avg_creativity

            # Taxa de respostas incoerentes (estrutura muito baixa)
            # Se gaussian está muito baixo, sistema está incoerente
            avg_gaussian = float(np.mean(gaussian_scores))
            incoherence_rate = 1.0 - avg_gaussian

            # Ajuste adaptativo de alpha_min e alpha_max
            # Se muitas respostas chatas → reduzir alpha_max (forçar mais criatividade)
            if redundancy_rate > 0.6:  # Mais de 60% de redundância
                self.alpha_max = max(0.3, self.alpha_max - 0.01)  # Reduzir lentamente
                self.logger.debug(
                    f"Alpha max reduced due to redundancy: {self.alpha_max:.4f} "
                    f"(redundancy_rate={redundancy_rate:.4f})"
                )

            # Se muitas respostas incoerentes → aumentar alpha_min (forçar mais estrutura)
            if incoherence_rate > 0.6:  # Mais de 60% de incoerência
                self.alpha_min = min(0.7, self.alpha_min + 0.01)  # Aumentar lentamente
                self.logger.debug(
                    f"Alpha min increased due to incoherence: {self.alpha_min:.4f} "
                    f"(incoherence_rate={incoherence_rate:.4f})"
                )

            # Garante que alpha_min < alpha_max
            if self.alpha_min >= self.alpha_max:
                self.alpha_min = max(0.2, self.alpha_max - 0.1)

            # Aplica clipping com ranges dinâmicos
            alpha_adjusted = float(np.clip(alpha_base, self.alpha_min, self.alpha_max))

            self.logger.debug(
                f"Dynamic alpha: base={alpha_base:.4f}, adjusted={alpha_adjusted:.4f} "
                f"(min={self.alpha_min:.4f}, max={self.alpha_max:.4f})"
            )

            return alpha_adjusted

        except Exception as e:
            # Se análise falhar, usa alpha_base com clipping estático
            self.logger.warning(f"Failed to calculate dynamic alpha: {e}. Using base alpha.")
            from src.consciousness.phi_constants import PSI_ALPHA_MAX, PSI_ALPHA_MIN

            return float(np.clip(alpha_base, PSI_ALPHA_MIN, PSI_ALPHA_MAX))

    def _record_performance(
        self,
        psi_norm: float,
        psi_from_creativity: float,
        psi_gaussian: float,
        alpha: float,
    ) -> None:
        """
        Registra desempenho para ajuste dinâmico de alpha.

        Args:
            psi_norm: Valor normalizado de Ψ
            psi_from_creativity: Componente de criatividade
            psi_gaussian: Componente gaussiano (estrutura)
            alpha: Alpha usado no cálculo
        """
        if not self.use_dynamic_alpha:
            return

        # Adiciona ao histórico
        self.performance_history.append(
            {
                "psi_norm": psi_norm,
                "psi_from_creativity": psi_from_creativity,
                "psi_gaussian": psi_gaussian,
                "alpha": alpha,
            }
        )

        # Mantém apenas últimos N valores
        if len(self.performance_history) > self.performance_window:
            self.performance_history.pop(0)
