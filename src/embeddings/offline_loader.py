"""
Offline Sentence Transformer Loader
Estratégia: Leve em CUDA (default), Multilíngue em CPU (sob demanda)
Modelos pré-salvos em /opt/models sem acessar internet
"""

import logging
import os
from pathlib import Path
from typing import Any, Literal, Optional

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Forçar modo offline
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HOME"] = "/opt/hf_cache"

MODELS_DIR = "/opt/models/sentence-transformers"

# Cache global de modelos carregados (evita recarregar)
_model_cache: dict[str, Any] = {}


class OfflineSentenceTransformer:
    """Carrega modelos de embeddings de forma segura e offline"""

    # Mapeamento de modelos disponíveis
    AVAILABLE_MODELS = {
        "default": {"name": "all-MiniLM-L6-v2", "device": "cuda", "size_mb": 87},
        "multilingual": {
            "name": "paraphrase-multilingual-MiniLM-L12-v2",
            "device": "cpu",
            "size_mb": 479,
        },
    }

    def __init__(self, model_name: str = "default", force_device: Optional[str] = None):
        """
        Args:
            model_name: "default" (CUDA) ou "multilingual" (CPU)
            force_device: Forçar "cuda" ou "cpu" (sobrescreve padrão)
        """
        if model_name not in self.AVAILABLE_MODELS:
            available = list(self.AVAILABLE_MODELS.keys())
            raise ValueError(f"Modelo desconhecido: {model_name}. Disponíveis: {available}")

        model_config = self.AVAILABLE_MODELS[model_name]
        self.device = force_device or model_config["device"]

        # Construir caminho
        self.model_path = str(Path(str(MODELS_DIR)) / str(model_config["name"]))

        logger.info(f"🔄 Carregando: {model_name} → {self.model_path}")
        logger.info(f"   Device: {self.device} (size: {model_config['size_mb']}MB)")

        # Verificar se modelo existe
        if not os.path.exists(self.model_path):
            avail_models = os.listdir(MODELS_DIR) if os.path.exists(MODELS_DIR) else "Nenhum"
            raise FileNotFoundError(
                f"❌ Modelo não encontrado: {self.model_path}\n"
                f"Modelos disponíveis: {avail_models}"
            )

        # Verificar cache
        cache_key = f"{model_name}_{self.device}"
        if cache_key in _model_cache:
            logger.info("   📦 Usando modelo em cache")
            self.model = _model_cache[cache_key]
            return

        # Carregar modelo OFFLINE
        try:
            self.model = SentenceTransformer(self.model_path, device=str(self.device))
            _model_cache[cache_key] = self.model
            logger.info(f"   ✅ Modelo carregado em {self.device}")
        except Exception as e:
            logger.error(f"   ❌ Erro ao carregar modelo: {e}")
            raise

    def encode(self, sentences, convert_to_tensor=False, **kwargs):
        """Encoda frases em embeddings"""
        return self.model.encode(sentences, convert_to_tensor=convert_to_tensor, **kwargs)

    def __call__(self, *args, **kwargs):
        """Permite usar como função"""
        return self.encode(*args, **kwargs)


def load_embedding_model(
    model_name: Literal["default", "multilingual"] = "default",
    force_device: Optional[Literal["cuda", "cpu"]] = None,
) -> OfflineSentenceTransformer:
    """
    Factory para carregar modelos de embeddings offline

    Args:
        model_name:
            - "default": Rápido em CUDA (default)
            - "multilingual": Suporta PT/EN/ES/FR/etc em CPU
        force_device: Forçar "cuda" ou "cpu" (sobrescreve padrão do modelo)

    Returns:
        OfflineSentenceTransformer carregado

    Examples:
        >>> # Default (rápido em CUDA)
        >>> embedder = load_embedding_model()
        >>> emb = embedder.encode(["Teste"])

        >>> # Multilíngue (CPU)
        >>> embedder = load_embedding_model("multilingual")
        >>> emb = embedder.encode(["Português", "English", "Español"])
    """
    return OfflineSentenceTransformer(model_name=model_name, force_device=force_device)


if __name__ == "__main__":
    # Teste
    print("🔍 Testando carregamento offline...")

    # Test 1: Default (CUDA)
    print("\n1️⃣ Modelo default (CUDA):")
    try:
        embedder = load_embedding_model("default")
        test_text = "Teste de embedding em português"
        emb = embedder.encode([test_text], convert_to_tensor=True)
        shape = emb[0].shape if isinstance(emb, list) and emb else emb.shape
        print(f"   ✅ OK: shape {shape}, device cpu")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Test 2: Multilingual (CPU)
    print("\n2️⃣ Modelo multilingual (CPU):")
    try:
        embedder = load_embedding_model("multilingual")
        test_texts = ["Português aqui", "English here", "Español aquí"]
        emb = embedder.encode(test_texts, convert_to_tensor=True)
        shape = emb[0].shape if isinstance(emb, list) and emb else emb.shape
        print(f"   ✅ OK: shape {shape}, device cpu")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        print(f"   ❌ Erro: {e}")
