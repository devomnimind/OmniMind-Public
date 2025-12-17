"""
Offline mode configuration for LLM models and embeddings.

Garante que modelos locais sejam usados com fallback para API quando necessário.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def setup_offline_mode() -> None:
    """
    Configure environment for offline mode with local model caching.

    Prioridades:
    1. Usar modelos do cache local (~/.cache/huggingface)
    2. Usar modelos do diretório local do projeto (models/)
    3. Fallback para API remota se configurado
    """
    # Configurar HuggingFace para modo offline por padrão
    # HF_HUB_OFFLINE=1 força uso de modelos em cache local
    # Se modelo não existir, erro será capturado e fallback para API acontecerá
    os.environ["HF_HUB_OFFLINE"] = os.environ.get("HF_HUB_OFFLINE", "1")
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    logger.info("✅ Offline mode configured: HF_HUB_OFFLINE=1 (priority to local models)")

    # Verificar se modelos estão no cache local
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
    local_models_dir = Path("models")

    cache_models = []
    if hf_cache.exists():
        cache_models = [d.name for d in hf_cache.iterdir() if d.is_dir()]

    local_models = []
    if local_models_dir.exists():
        local_models = [d.name for d in local_models_dir.iterdir() if d.is_dir()]

    logger.info("🔍 Modelo Cache Status:")
    logger.info(f"  HuggingFace cache ({hf_cache}): {len(cache_models)} modelos")
    if cache_models:
        for model in sorted(cache_models)[:5]:  # Mostrar primeiros 5
            logger.info(f"    • {model}")
        if len(cache_models) > 5:
            logger.info(f"    ... e {len(cache_models) - 5} mais")

    logger.info(f"  Local models ({local_models_dir}): {len(local_models)} modelos")
    if local_models:
        for model in sorted(local_models)[:5]:
            logger.info(f"    • {model}")

    # Buscar modelos críticos com normalização de caminho
    critical_models: dict[str, Optional[str]] = {
        "phi": None,
        "all-MiniLM-L6-v2": None,  # Normalized name
    }

    # Normalizar nomes de modelo para busca
    def normalize_model_name(name: str) -> str:
        """Normalizar nome do modelo removendo prefixos."""
        # Remove 'sentence-transformers/' prefix
        return name.split("/")[-1].lower()

    for model_name in critical_models.keys():
        normalized_search = normalize_model_name(model_name)
        found = False

        # Buscar no cache com matching flexível
        for cached_model in cache_models:
            if normalized_search in normalize_model_name(cached_model):
                critical_models[model_name] = "cache"
                found = True
                break

        # Se não encontrou no cache, buscar localmente
        if not found:
            for local_model in local_models:
                if normalized_search in normalize_model_name(local_model):
                    critical_models[model_name] = "local"
                    break

    logger.info("📦 Modelos Críticos:")
    for model, location in critical_models.items():
        status = f"✅ {location}" if location else "❌ Não encontrado"
        logger.info(f"  {model}: {status}")

    return


def get_model_path(model_name: str) -> Optional[str]:
    """
    Get local path for a model if it exists.

    Args:
        model_name: Nome do modelo (ex: 'all-MiniLM-L6-v2', 'phi',
                'sentence-transformers/all-MiniLM-L6-v2')

    Returns:
        Path to model if found locally, None otherwise
    """
    # Normalizar nome do modelo (remover prefixos)
    normalized_name = model_name.split("/")[-1].lower()

    # Procurar no cache do HuggingFace
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
    if hf_cache.exists():
        for model_dir in hf_cache.iterdir():
            if normalized_name in model_dir.name.lower():
                return str(model_dir)

    # Procurar no diretório local do projeto
    local_models_dir = Path("models")
    if local_models_dir.exists():
        for model_dir in local_models_dir.iterdir():
            if normalized_name in model_dir.name.lower():
                return str(model_dir)

    return None


def load_model_offline(
    model_name: str, fallback_enabled: bool = True, device: str = "cpu"
) -> tuple[bool, Optional[str]]:
    """
    Try to load model in offline mode with API fallback.

    Args:
        model_name: Nome do modelo
        fallback_enabled: Se True, permite fallback para API remota
        device: Device (cpu, cuda, etc)

    Returns:
        (success: bool, error_msg: Optional[str])
    """
    logger.info(f"🔄 Tentando carregar modelo: {model_name}")

    # Passo 1: Verificar cache local
    model_path = get_model_path(model_name)
    if model_path:
        logger.info(f"✅ Modelo encontrado localmente: {model_path}")
        os.environ["HF_HUB_OFFLINE"] = "1"
        return True, None

    logger.warning(f"⚠️  Modelo não encontrado no cache local: {model_name}")

    # Passo 2: Se fallback habilitado, permitir download remoto
    if fallback_enabled:
        logger.info(f"🔗 Fallback habilitado - permitindo download remoto de {model_name}")
        os.environ["HF_HUB_OFFLINE"] = "0"
        return True, None

    # Passo 3: Modo offline obrigatório - erro
    error_msg = (
        f"Modelo {model_name} não encontrado localmente e HF_HUB_OFFLINE=1. "
        f"Para usar modelo remoto, desabilite offline mode ou execute: "
        f"HF_HUB_OFFLINE=0 python -m uvicorn web.backend.main:app"
    )
    logger.error(f"❌ {error_msg}")
    return False, error_msg


def resolve_sentence_transformer_name(short_name: str) -> str:
    """
    Resolve short model name to full HuggingFace path or absolute path for SentenceTransformer.

    This handles offline mode where cache directory names don't automatically
    resolve short names like 'all-MiniLM-L6-v2' to 'sentence-transformers/all-MiniLM-L6-v2'.

    If model is found in HF cache, returns absolute path to snapshot for direct loading.
    Otherwise returns full HuggingFace model name.

    Args:
        short_name: Short name like 'all-MiniLM-L6-v2' or full name like
            'sentence-transformers/all-MiniLM-L6-v2'

    Returns:
        Absolute path to model snapshot (if found locally) or full model name
        for HuggingFace
    """
    # If already has prefix, use as provided
    if "/" in short_name and not short_name.startswith("/"):
        model_to_search = short_name.split("/")[-1]  # Extract model name from path
    else:
        model_to_search = short_name

    # Check cache to see if model exists locally
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
    if hf_cache.exists():
        for model_dir in hf_cache.iterdir():
            # Look for model directories matching the model name
            if model_dir.is_dir() and model_to_search in model_dir.name:
                # Check if it has snapshots
                snapshots_dir = model_dir / "snapshots"
                if snapshots_dir.exists():
                    # Get the first (usually only) snapshot
                    for snapshot in snapshots_dir.iterdir():
                        if snapshot.is_dir():
                            logger.debug(f"🔍 Found model {short_name} at: {snapshot}")
                            return str(snapshot)

    # Mapping of short names to full paths if not found
    name_mapping = {
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
        "multi-qa-mpnet-base-dot-v1": "sentence-transformers/multi-qa-mpnet-base-dot-v1",
    }

    # Return mapped name if available, otherwise return original
    result = name_mapping.get(short_name, short_name)
    logger.debug(f"🔍 Model name: {short_name} → {result} (not found in local cache)")
    return result
