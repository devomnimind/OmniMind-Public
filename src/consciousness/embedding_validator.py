"""
Embedding Narrative Validator - Valida qualidade da análise de embeddings.

Não valida "reconstrução de texto" (não há texto!).
Valida bem-formação de embeddings e consistência da análise.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: REDESENHO_RADICAL_EMBEDDINGS.py
"""

import logging
from typing import Any, Dict, List

import numpy as np

from src.consciousness.embedding_narrative import EmbeddingNarrative

logger = logging.getLogger(__name__)


class EmbeddingNarrativeValidator:
    """
    Valida qualidade da análise de embeddings.

    Validações:
    1. Embeddings estão bem-formados? (NaN, zero vectors, magnitude)
    2. Análise é consistente? (ranges numéricos)
    3. Métricas estão em ranges razoáveis?
    """

    def __init__(self):
        """Inicializa validator."""
        self.logger = logger

    async def validate(self, embedding_narrative: EmbeddingNarrative) -> Dict[str, Any]:
        """
        Valida EmbeddingNarrative.

        Args:
            embedding_narrative: Narrativa a validar

        Returns:
            Dict com validação (is_valid, issues, confidence, recommendation)
        """
        issues: List[str] = []
        confidence = 1.0

        # 1. Verificação de embeddings
        for name, emb in embedding_narrative.module_embeddings.items():
            # Converte para array se necessário
            if not isinstance(emb, np.ndarray):
                emb = np.array(emb)

            # Há NaNs?
            if np.any(np.isnan(emb)):
                issues.append(f"NaNs em {name}")
                confidence -= 0.3

            # Não está vazio?
            if np.allclose(emb, 0):
                issues.append(f"{name} é zero vector")
                confidence -= 0.2

            # Magnitude é razoável?
            norm = float(np.linalg.norm(emb))
            if norm > 100.0 or norm < 0.01:
                issues.append(f"{name} magnitude extrema: {norm:.3f}")
                confidence -= 0.1

        # 2. Verificação de análise
        goal = embedding_narrative.goal_inference
        if isinstance(goal, dict):
            divergence = goal.get("divergence", 0)
            if not (0 <= divergence <= 1):
                issues.append(f"Divergence fora de [0, 1]: {divergence}")
                confidence -= 0.2

        # 3. Verificação de ações
        action = embedding_narrative.action_pattern
        if isinstance(action, dict):
            sync = action.get("module_synchronization", 0.5)
            if not (0 <= sync <= 1):
                issues.append(f"Sincronização fora de [0, 1]: {sync}")
                confidence -= 0.1

        # 4. Verificação de signature semântica
        signature = embedding_narrative.semantic_signature
        if signature:
            for key, value in signature.items():
                if not isinstance(value, (int, float)):
                    issues.append(f"Signature {key} não é numérico: {type(value)}")
                    confidence -= 0.05
                elif np.isnan(value) or np.isinf(value):
                    issues.append(f"Signature {key} é NaN ou Inf: {value}")
                    confidence -= 0.1

        # 5. Verificação de representação numérica
        try:
            numeric_repr = embedding_narrative.to_numeric_representation()
            if len(numeric_repr) == 0:
                issues.append("Representação numérica vazia")
                confidence -= 0.3
            elif np.any(np.isnan(numeric_repr)) or np.any(np.isinf(numeric_repr)):
                issues.append("Representação numérica contém NaN ou Inf")
                confidence -= 0.2
        except Exception as e:
            issues.append(f"Erro ao gerar representação numérica: {e}")
            confidence -= 0.3

        # Garante confidence em [0, 1]
        confidence = max(0.0, min(1.0, confidence))

        # Recomendação
        if confidence > 0.8:
            recommendation = "Use com confiança"
        elif confidence > 0.5:
            recommendation = "Verifique issues antes de usar"
        else:
            recommendation = "NÃO USE - problemas críticos detectados"

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "confidence": float(confidence),
            "recommendation": recommendation,
        }
