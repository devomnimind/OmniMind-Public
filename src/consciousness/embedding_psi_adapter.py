"""
Embedding Psi Adapter - Adapta PsiProducer para trabalhar com embeddings.

Calcula Ψ (Deleuze) diretamente a partir de embeddings usando LZ complexity,
sem depender de texto reconstruído.

CORREÇÃO (2025-12-07): Adicionada dependência gaussiana de Φ conforme IIT clássico.
FASE 2 (2025-12-07): Integração de PrecisionWeighter para eliminar pesos hardcoded.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: VERIFICACAO_PHI_SISTEMA.md
"""

import logging
from typing import List, Optional

import numpy as np

from src.consciousness.adaptive_weights import PrecisionWeighter
from src.consciousness.biological_metrics import LempelZivComplexity
from src.consciousness.embedding_narrative import EmbeddingNarrative
from src.consciousness.phi_constants import calculate_psi_gaussian

logger = logging.getLogger(__name__)


class EmbeddingNoveltyAdapter:
    """
    Adaptador de novidade para embeddings.

    Mantém compatibilidade com NoveltyDetector (texto opcional) mas trabalha
    diretamente com embeddings para melhor desempenho científico.
    """

    def __init__(self):
        """Inicializa adapter."""
        self.logger = logger
        self.embedding_history: List[np.ndarray] = []

    def register_embedding(self, embedding: np.ndarray) -> None:
        """
        Registra embedding no histórico.

        Args:
            embedding: Embedding a registrar
        """
        self.embedding_history.append(embedding.copy())
        # Mantém apenas últimos 100 para eficiência
        if len(self.embedding_history) > 100:
            self.embedding_history.pop(0)

    def measure_novelty_from_embedding(
        self, embedding: np.ndarray, metric: str = "cosine_distance"
    ) -> float:
        """
        Mede novidade de um embedding em relação ao histórico.

        Args:
            embedding: Embedding a medir
            metric: Métrica a usar ("cosine_distance" ou "l2_distance")

        Returns:
            float [0, 1] representando novidade (1 = completamente novo)
        """
        if not self.embedding_history:
            return 1.0  # Primeiro embedding = completamente novo

        # Calcula distâncias para histórico
        distances = []
        for hist_emb in self.embedding_history:
            if metric == "cosine_distance":
                # Cosine distance = 1 - cosine similarity
                similarity = np.dot(embedding, hist_emb) / (
                    np.linalg.norm(embedding) * np.linalg.norm(hist_emb) + 1e-10
                )
                distance = 1.0 - similarity
            else:  # l2_distance
                distance = np.linalg.norm(embedding - hist_emb)

            distances.append(distance)

        # Novidade = distância mínima normalizada
        min_distance = min(distances) if distances else 1.0
        # Normaliza para [0, 1] (assumindo distância máxima ~2.0 para cosine)
        novelty = (
            min(1.0, min_distance / 2.0) if metric == "cosine_distance" else min(1.0, min_distance)
        )

        return float(novelty)


class PsiProducerAdapter:
    """
    Adapta PsiProducer para trabalhar com EmbeddingNarrative.

    Calcula Ψ diretamente a partir de embeddings usando LZ complexity,
    sem depender de texto reconstruído.
    """

    def __init__(self, use_precision_weights: bool = True):
        """
        Inicializa adapter.

        Args:
            use_precision_weights: Se True, usa PrecisionWeighter para pesos dinâmicos
        """
        self.logger = logger
        self.novelty_adapter = EmbeddingNoveltyAdapter()
        self.use_precision_weights = use_precision_weights
        self.precision_weighter: Optional[PrecisionWeighter] = (
            PrecisionWeighter(history_window=50) if use_precision_weights else None
        )

    async def calculate_psi_for_embedding(
        self, embedding_narrative: EmbeddingNarrative, phi_raw: Optional[float] = None
    ) -> float:
        """
        Calcula Ψ para EmbeddingNarrative.

        CORREÇÃO (2025-12-07): Agora inclui dependência gaussiana de Φ conforme IIT clássico.

        Args:
            embedding_narrative: Narrativa de embeddings
            phi_raw: Valor de Φ em nats (opcional, se fornecido será usado para gaussiana)

        Returns:
            float [0, 1] representando Ψ
        """
        # 1. Componente gaussiano de Φ (IIT clássico)
        if phi_raw is not None:
            psi_gaussian = calculate_psi_gaussian(phi_raw)
        else:
            # Fallback: valor neutro se Φ não fornecido
            psi_gaussian = 0.5

        # 2. Converte embedding_narrative → vetor numérico
        numeric_repr = embedding_narrative.to_numeric_representation()

        # 3. Calcula LZ complexity do vetor
        lz_result = LempelZivComplexity.from_signal(numeric_repr)
        lz_complexity = lz_result.complexity

        # 4. Registra embedding no histórico de novidade
        mean_embedding = np.mean(list(embedding_narrative.module_embeddings.values()), axis=0)
        self.novelty_adapter.register_embedding(mean_embedding)

        # 5. Calcula novidade (surpresa)
        novelty = self.novelty_adapter.measure_novelty_from_embedding(mean_embedding)

        # 6. Calcula relevância (baseada em goal_inference)
        goal = embedding_narrative.goal_inference
        relevance = goal.get("meaning_confidence", 0.5) if isinstance(goal, dict) else 0.5

        # 7. Componente de criatividade (com PrecisionWeighter ou fallback)
        components = {
            "lz_complexity": lz_complexity,
            "novelty": novelty,
            "relevance": relevance,
        }
        if self.use_precision_weights and self.precision_weighter:
            weights = self.precision_weighter.compute_weights(components)
            psi_from_creativity = sum(components[k] * weights[k] for k in components)
            self.logger.debug(f"EmbeddingPsiAdapter: Pesos dinâmicos calculados: {weights}")
        else:
            # Fallback para pesos hardcoded (compatibilidade)
            psi_from_creativity = 0.4 * lz_complexity + 0.3 * novelty + 0.3 * relevance

        # 8. COMBINAR: Alpha dinâmico baseado em Φ (FASE 3)
        # Se Φ é alto, confia mais na estrutura (Gaussian)
        # Se Φ é baixo, confia mais na criatividade bruta
        if phi_raw is not None:
            # Alpha dinâmico usando constantes empíricas
            # Range (0.3, 0.7) garante mínimo de cada componente
            from src.consciousness.phi_constants import (
                PSI_ALPHA_MAX,
                PSI_ALPHA_MIN,
                normalize_phi,
            )

            # Normalizar phi_raw para [0, 1] se necessário
            phi_norm = (
                normalize_phi(phi_raw) if phi_raw > 1.0 else float(np.clip(phi_raw, 0.0, 1.0))
            )
            # Phi alto (0.8) -> alpha = 0.7 (confia mais em Gaussian)
            # Phi baixo (0.1) -> alpha = 0.3 (confia mais em criatividade)
            alpha = float(np.clip(phi_norm * 10.0, PSI_ALPHA_MIN, PSI_ALPHA_MAX))
        else:
            # Fallback: usar 0.5 se phi_raw não disponível
            alpha = 0.5
            self.logger.debug(
                "EmbeddingPsiAdapter: phi_raw não disponível, usando alpha=0.5 (fallback)"
            )

        psi = alpha * psi_gaussian + (1.0 - alpha) * psi_from_creativity

        # 9. Normaliza para [0, 1]
        psi = float(np.clip(psi, 0.0, 1.0))

        return psi

    def calculate_psi_from_temporal_signature(self, temporal_signature: List[float]) -> float:
        """
        Calcula Ψ a partir de assinatura temporal.

        Útil quando apenas temporal_signature está disponível.

        Args:
            temporal_signature: Assinatura temporal (ativações + deltas + acelerações)

        Returns:
            float [0, 1] representando Ψ
        """
        if not temporal_signature:
            return 0.5  # Valor neutro

        # Converte para array
        signature_array = np.array(temporal_signature)

        # Calcula LZ complexity
        lz_result = LempelZivComplexity.from_signal(signature_array)
        lz_complexity = lz_result.complexity

        # Calcula entropia de Shannon
        normalized = (signature_array - signature_array.min()) / (
            signature_array.max() - signature_array.min() + 1e-10
        )
        normalized = np.clip(normalized, 1e-10, 1.0)
        entropy = -np.sum(normalized * np.log(normalized))
        entropy_normalized = min(1.0, entropy / 10.0)  # Normaliza

        # Ψ = combinação de LZ e entropia
        psi = 0.6 * lz_complexity + 0.4 * entropy_normalized

        return float(np.clip(psi, 0.0, 1.0))
