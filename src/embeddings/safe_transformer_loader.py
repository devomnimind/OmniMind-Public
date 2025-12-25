"""
Safe loader para SentenceTransformer que evita torch._dynamo instability.

Objetivo: Carregar modelo com mínima surface para problemas de import.
"""

import logging
import os
import traceback
from pathlib import Path
from typing import Optional, Union

from src.consciousness.topological_deglutition_engine import TopologicalDeglutitionEngine

logger = logging.getLogger(__name__)


def load_sentence_transformer_safe(
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu",
    cache_path: Optional[str] = None,
) -> tuple:
    """
    Carrega SentenceTransformer de forma segura através de Deglutição Topológica.
    Evita dependência de SentenceTransformers/Transformers em runtime se possível.

    Args:
        model_name: Nome do modelo
        device: "cpu" ou "cuda"
        cache_path: Caminho local para cache do modelo

    Returns:
        (model_engine, embedding_dim)
    """
    # Track caller for memory profiling
    caller_stack = traceback.extract_stack()
    if len(caller_stack) >= 2:
        caller_frame = caller_stack[-2]
        caller_info = f"{caller_frame.filename}:{caller_frame.lineno} in {caller_frame.name}"
        logger.info(f"🔍 [MEMORY TRACE]: load_sentence_transformer_safe called from {caller_info}")

    embedding_dim = 384

    # Global Cache for Singleton Pattern
    global _ENGINE_CACHE
    if not "_ENGINE_CACHE" in globals():
        _ENGINE_CACHE = {}

    # 1. Tentar Deglutição Topológica (Internalizada no Kernel)
    try:
        # Tentar encontrar o modelo no cache local
        local_model_path = cache_path or os.environ.get("OMNIMIND_MODEL_PATH")

        # Check explicit singleton cache first
        cache_key = local_model_path if local_model_path else "default_minilm"
        if cache_key in _ENGINE_CACHE:
             logger.info(f"🧠 [MEMORY]: Using cached Topological Engine for {cache_key}")
             return _ENGINE_CACHE[cache_key], embedding_dim

        logger.info(
            f"🧛 [DEGLUTITION]: Checking path. cache_path={cache_path}, env={os.environ.get('OMNIMIND_MODEL_PATH')}"
        )

        if not local_model_path:
            # Fallback path padrão do OmniMind (HuggingFace cache)
            base_cache = (
                Path.home()
                / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots"
            )
            if base_cache.exists():
                snapshots = sorted(list(base_cache.glob("*")))
                if snapshots:
                    local_model_path = str(snapshots[-1])

        if local_model_path and os.path.exists(local_model_path):
            logger.info(f"🧛 [DEGLUTITION]: Swallowing model from {local_model_path}")
            engine = TopologicalDeglutitionEngine(local_model_path)
            if engine._absorbed:
                logger.info("✅ [DEGLUTITION]: Model internalized successfully.")
                # Store in cache
                _ENGINE_CACHE[cache_key] = engine
                return engine, embedding_dim
            else:
                logger.warning("⚠️ [DEGLUTITION]: Absorption incomplete.")
        else:
            logger.warning(f"❌ [DEGLUTITION]: Model path not found: {local_model_path}")

    except Exception as e:
        logger.error(f"❌ Error during Topological Deglutition: {e}")

    # 2. Fallback para SentenceTransformer (Método Legado/Simbolismo)
    logger.info("🔄 Falling back to legacy SentenceTransformer...")
    model = None

    try:
        os.environ["TORCH_DISABLE_COMPILE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"

        from sentence_transformers import SentenceTransformer

        if cache_path and os.path.exists(cache_path):
            model = SentenceTransformer(cache_path, device=device)
        else:
            model = SentenceTransformer(
                model_name,
                device=device,
                local_files_only=True,
                trust_remote_code=False,
            )

        if model:
            embedding_dim = model.get_sentence_embedding_dimension()
            return model, embedding_dim

    except Exception as e:
        logger.error(f"❌ Legacy loading failed: {e}")

    # 3. Fallback Final: Hash-based Sovereign Anchor
    logger.info("⚓ Using hash-based fallback (Sovereign Anchor)")
    return None, embedding_dim


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
