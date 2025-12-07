"""
Psi Producer (Ψ_produtor) - Métrica de Produção Criativa (Deleuze)

Implementa Ψ como dimensão ortogonal independente de Φ (IIT).

Ψ captura:
- Produção criativa (inovação, surpresa, relevância)
- Diversidade de ações (entropia de escolhas)
- Máquinas desejantes (Deleuze)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
Baseado em: PLANO_IMPLEMENTACAO_LACUNA_PHI.md
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from src.consciousness.novelty_generator import NoveltyDetector, NoveltyMetric
from src.embeddings.code_embeddings import OmniMindEmbeddings

logger = logging.getLogger(__name__)

# Pesos para componentes de Ψ (aprovados pelo usuário)
PSI_WEIGHTS = {
    "innovation": 0.4,  # Inovação (novelty_score)
    "surprise": 0.3,  # Surpresa (surprise_score)
    "relevance": 0.3,  # Relevância (relevance_score)
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

    Fórmula:
    Ψ = 0.4 * innovation_score
      + 0.3 * surprise_score
      + 0.3 * relevance_score

    Entropy_of_actions é usado como validação (correlação esperada r > 0.6).
    """

    def __init__(
        self,
        novelty_detector: Optional[NoveltyDetector] = None,
        embedding_model: Optional[OmniMindEmbeddings] = None,
    ):
        """
        Inicializa PsiProducer.

        Args:
            novelty_detector: Instância opcional de NoveltyDetector (cria novo se None)
            embedding_model: Instância opcional de OmniMindEmbeddings (cria novo se None)
        """
        self.novelty_detector = novelty_detector or NoveltyDetector()
        self.embedding_model = embedding_model
        self.logger = logger

    def calculate_psi_for_step(
        self,
        step_content: str,
        previous_steps: List[str],
        goal: str,
        actions: List[str],
        step_id: str = "",
    ) -> PsiResult:
        """
        Calcula Ψ_produtor para um passo de pensamento.

        Args:
            step_content: Conteúdo do passo atual
            previous_steps: Lista de passos anteriores (para contexto)
            goal: Objetivo da sessão (para relevância)
            actions: Lista de ações tomadas (para entropia)
            step_id: ID único do passo

        Returns:
            PsiResult com psi_raw, psi_norm, components
        """
        # 1. Innovation score (via NoveltyDetector)
        innovation_score = self._calculate_innovation_score(step_content, previous_steps)

        # 2. Surprise score (via NoveltyDetector)
        surprise_score = self._calculate_surprise_score(step_content, previous_steps)

        # 3. Relevance score (via embeddings)
        relevance_score = self._calculate_relevance_score(step_content, goal)

        # 4. Entropy of actions (Shannon entropy)
        entropy_of_actions = self._calculate_entropy_of_actions(actions)

        # 5. Agregar componentes com pesos
        psi_raw = (
            PSI_WEIGHTS["innovation"] * innovation_score
            + PSI_WEIGHTS["surprise"] * surprise_score
            + PSI_WEIGHTS["relevance"] * relevance_score
        )

        # 6. Normalizar para [0, 1] com clipping
        psi_norm = self._normalize_psi(psi_raw)

        # Criar componentes
        components = PsiComponents(
            innovation_score=innovation_score,
            surprise_score=surprise_score,
            relevance_score=relevance_score,
            entropy_of_actions=entropy_of_actions,
        )

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
                step_embedding = self.embedding_model.model.encode(  # type: ignore[attr-defined]
                    step_content
                )
                goal_embedding = self.embedding_model.model.encode(  # type: ignore[attr-defined]
                    goal
                )

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
