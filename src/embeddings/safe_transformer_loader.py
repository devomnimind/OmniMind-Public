"""
Safe loader para SentenceTransformer que evita torch._dynamo instability.

Objetivo: Carregar modelo com mínima surface para problemas de import.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def load_sentence_transformer_safe(
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu",
    cache_path: Optional[str] = None,
) -> tuple:
    """
    Carrega SentenceTransformer de forma segura, evitando torch._dynamo.

    Args:
        model_name: Nome do modelo no HF hub
        device: "cpu" ou "cuda"
        cache_path: Caminho local para cache do modelo

    Returns:
        (model, embedding_dim) ou None, embedding_dim em caso de erro
    """
    model = None
    embedding_dim = 384  # default para all-MiniLM-L6-v2

    try:
        # Desabilitar torch.compile e outras otimizações que causam problemas
        os.environ["TORCH_DISABLE_COMPILE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"

        # Import lazy - apenas quando necessário
        from sentence_transformers import SentenceTransformer

        logger.info(f"Carregando SentenceTransformer: {model_name} (device={device})")

        if cache_path and os.path.exists(cache_path):
            logger.info(f"Usando cache local: {cache_path}")
            model = SentenceTransformer(cache_path, device=device)
        else:
            # Tentar carregar com local_files_only primeiro
            try:
                logger.info("Tentando carregar com local_files_only=True...")
                model = SentenceTransformer(
                    model_name,
                    device=device,
                    local_files_only=True,
                    trust_remote_code=False,
                )
            except Exception as e:
                logger.warning(f"local_files_only falhou: {e}. Tentando download...")
                model = SentenceTransformer(
                    model_name,
                    device=device,
                    trust_remote_code=False,
                )

        if model:
            embedding_dim: int = model.get_sentence_embedding_dimension()  # type: ignore
            logger.info(
                f"✅ SentenceTransformer carregado com sucesso. "
                f"Dimensões: {embedding_dim}, Device: {device}"
            )
        else:
            logger.error("Modelo carregou como None")
            embedding_dim = 384

    except ImportError as e:
        logger.error(f"❌ Erro de import (SentenceTransformer): {e}")
        logger.warning("Usando fallback: embeddings via sklearn/numpy (384 dims aleatório)")
        embedding_dim = 384
        model = None

    except Exception as e:
        logger.error(f"❌ Erro ao carregar SentenceTransformer: {type(e).__name__}: {e}")
        logger.warning("Fallback: embeddings aleatório de dimensão 384")
        embedding_dim = 384
        model = None

    return model, embedding_dim


def create_fallback_embedding(text: str, dimension: int = 384) -> list:
    """
    Cria embedding fallback quando SentenceTransformer falha.
    Usa hash do texto para gerar vetor pseudo-aleatório determinístico.

    Args:
        text: Texto para embedir
        dimension: Dimensão do vetor

    Returns:
        Vetor de embedding (normalizando ~entre -1 e 1)
    """
    import hashlib

    # Hash determinístico do texto
    h = hashlib.sha256(text.encode()).digest()

    # Converter bytes para valores float entre -1 e 1
    embedding = []
    for i in range(dimension):
        byte_val = h[i % len(h)]
        # Normalizar para range [-1, 1]
        val = (byte_val / 128.0) - 1.0
        embedding.append(val)

    return embedding
