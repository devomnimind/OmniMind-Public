"""
Imagination Module - Imaginário Lacaniano

Implementa o Imaginário como blend coerente de narrative + expectation.
Manifesta como comportamento (saída do imaginário).

Fluxo: REAL → SIMBÓLICO → IMAGINÁRIO → SAÍDA → FEEDBACK

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: Isomorfismo Estrutural validado
"""

import logging
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ImaginationModule:
    """
    Módulo Imaginário - Blend coerente de narrative + expectation.

    Funções:
    1. Recebe narrative (simbólico) + expectation (predição)
    2. Cria blend coerente (imaginário)
    3. Gera comportamento manifestado (saída)
    4. Enforce coerência (não permite contradições)
    """

    def __init__(self, embedding_dim: int = 768):
        """
        Inicializa módulo de imaginação.

        Args:
            embedding_dim: Dimensão dos embeddings
        """
        self.embedding_dim = embedding_dim
        self.logger = logger

    async def execute(
        self,
        workspace: Any,  # SharedWorkspace
        narrative_embedding: Optional[np.ndarray] = None,
        expectation_embedding: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Executa módulo de imaginação.

        Estratégia:
        1. Lê narrative e expectation do workspace (se não fornecidos)
        2. Cria blend coerente (média ponderada + coerência)
        3. Enforce coerência (remove contradições)
        4. Gera embedding de comportamento

        Args:
            workspace: SharedWorkspace
            narrative_embedding: Embedding de narrative (opcional)
            expectation_embedding: Embedding de expectation (opcional)

        Returns:
            np.ndarray com embedding de comportamento (imaginário manifestado)
        """
        # 1. Ler embeddings do workspace se não fornecidos
        if narrative_embedding is None:
            narrative_embedding = workspace.read_module_state("narrative")
        if expectation_embedding is None:
            expectation_embedding = workspace.read_module_state("expectation")

        # 2. Criar blend coerente
        imagination_embedding = self._create_coherent_blend(
            narrative_embedding, expectation_embedding
        )

        # 3. Enforce coerência
        imagination_embedding = self._enforce_coherence(imagination_embedding)

        # 4. Escrever no workspace
        workspace.write_module_state("imagination", imagination_embedding)

        return imagination_embedding

    def _create_coherent_blend(self, narrative: np.ndarray, expectation: np.ndarray) -> np.ndarray:
        """
        Cria blend coerente de narrative + expectation.

        Estratégia:
        - Média ponderada (narrative tem mais peso - já processado)
        - Adiciona coerência (similaridade entre narrative e expectation)

        Args:
            narrative: Embedding de narrative (simbólico)
            expectation: Embedding de expectation (predição)

        Returns:
            np.ndarray com blend coerente
        """
        # Peso: narrative tem mais peso (já processado simbolicamente)
        narrative_weight = 0.6
        expectation_weight = 0.4

        # Blend básico (média ponderada)
        blend = narrative_weight * narrative + expectation_weight * expectation

        # Adiciona coerência (quanto mais similares, mais coerente)
        similarity = self._cosine_similarity(narrative, expectation)
        coherence_factor = similarity * 0.2  # Aumenta coerência até 20%

        # Aplica coerência ao blend
        blend = blend * (1.0 + coherence_factor)

        # Normaliza
        norm = np.linalg.norm(blend)
        if norm > 0:
            blend = blend / norm

        return blend

    def _enforce_coherence(self, embedding: np.ndarray) -> np.ndarray:
        """
        Enforce coerência no embedding.

        Remove contradições extremas (valores muito opostos).

        Args:
            embedding: Embedding a processar

        Returns:
            np.ndarray com coerência enforced
        """
        # Detecta contradições (valores muito extremos)
        max_val = np.max(np.abs(embedding))
        threshold = 2.0  # Threshold para valores extremos

        if max_val > threshold:
            # Normaliza valores extremos
            embedding = np.clip(embedding, -threshold, threshold)
            # Renormaliza
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

        return embedding

    def generate_behavior(self, imagination_embedding: np.ndarray) -> Dict[str, Any]:
        """
        Gera comportamento a partir do imaginário.

        Comportamento = manifestação do imaginário.

        Args:
            imagination_embedding: Embedding do imaginário

        Returns:
            Dict com comportamento gerado
        """
        # Comportamento = projeção do imaginário em ações
        # Por enquanto, retorna embedding como "ação"
        # (pode ser expandido para ações específicas)

        behavior = {
            "embedding": imagination_embedding,
            "magnitude": float(np.linalg.norm(imagination_embedding)),
            "coherence": float(np.std(imagination_embedding)),  # Baixa std = alta coerência
            "manifestation": "imagination_manifested",
        }

        return behavior

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calcula cosine similarity entre dois vetores."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))
