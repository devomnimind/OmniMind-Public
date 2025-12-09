"""
Device Utilities - Detecção automática de GPU para cálculos.

Centraliza detecção de device para garantir consistência em todos os módulos.
"""

import logging
import os
from typing import Literal

logger = logging.getLogger(__name__)

# Cache do device para evitar múltiplas verificações
_cached_device: Literal["cuda", "cpu"] | None = None


def get_compute_device() -> Literal["cuda", "cpu"]:
    """
    Detecta device ótimo para cálculos (GPU se disponível).

    Returns:
        "cuda" se GPU disponível, "cpu" caso contrário
    """
    global _cached_device

    if _cached_device is not None:
        return _cached_device

    try:
        import torch

        # Verificar CUDA disponível
        if torch.cuda.is_available():
            _cached_device = "cuda"
            logger.info(f"✅ GPU disponível: {torch.cuda.get_device_name(0)}")
        else:
            # Verificar se há device mesmo que is_available() falhe
            try:
                device_count = torch.cuda.device_count()
                if device_count > 0:
                    # GPU hardware existe mas PyTorch init pode ter falhado
                    # Verificar variáveis de ambiente
                    force_gpu = os.getenv("OMNIMIND_FORCE_GPU", "").lower() in ("true", "1", "yes")
                    if force_gpu:
                        _cached_device = "cuda"
                        logger.warning(
                            f"⚠️ GPU hardware detectado (device_count={device_count}) mas "
                            f"torch.cuda.is_available()=False. Usando GPU forçado via env."
                        )
                    else:
                        _cached_device = "cpu"
                        logger.warning(
                            "GPU hardware detectado mas não disponível. "
                            "Defina OMNIMIND_FORCE_GPU=true para forçar uso."
                        )
                else:
                    _cached_device = "cpu"
            except Exception:
                _cached_device = "cpu"
    except ImportError:
        _cached_device = "cpu"
        logger.warning("PyTorch não disponível, usando CPU")

    return _cached_device


def check_gpu_memory_available(min_memory_mb: float = 100.0) -> bool:
    """
    Verifica se há memória GPU disponível suficiente antes de carregar modelos.

    Args:
        min_memory_mb: Memória mínima necessária em MB (padrão: 100MB)

    Returns:
        True se há memória suficiente, False caso contrário
    """
    try:
        import torch

        if not torch.cuda.is_available():
            return False

        # Verificar memória GPU disponível
        total_mem = torch.cuda.get_device_properties(0).total_memory
        allocated = torch.cuda.memory_allocated(0)
        reserved = torch.cuda.memory_reserved(0)
        free_mem = total_mem - reserved  # Memória realmente livre

        free_mem_mb = free_mem / (1024 * 1024)
        allocated_mb = allocated / (1024 * 1024)
        reserved_mb = reserved / (1024 * 1024)

        if free_mem_mb < min_memory_mb:
            logger.warning(
                f"GPU memória insuficiente: {free_mem_mb:.1f}MB livre "
                f"(alocado: {allocated_mb:.1f}MB, reservado: {reserved_mb:.1f}MB, "
                f"necessário: {min_memory_mb:.1f}MB). Usando CPU."
            )
            return False

        return True
    except Exception as e:
        logger.debug(f"Erro ao verificar memória GPU: {e}. Usando CPU.")
        return False


def get_sentence_transformer_device(min_memory_mb: float = 100.0) -> str:
    """
    Retorna device para SentenceTransformer verificando memória disponível.

    Verifica se há memória GPU suficiente antes de retornar "cuda".
    Se não houver memória suficiente, retorna "cpu" automaticamente.

    Args:
        min_memory_mb: Memória mínima necessária em MB (padrão: 100MB)

    Returns:
        "cuda" se GPU disponível e com memória suficiente, "cpu" caso contrário
    """
    preferred_device = get_compute_device()

    # Se preferência é CPU, retornar diretamente
    if preferred_device == "cpu":
        return "cpu"

    # Se preferência é CUDA, verificar memória disponível
    if preferred_device == "cuda":
        if check_gpu_memory_available(min_memory_mb):
            return "cuda"
        else:
            logger.info(
                "GPU disponível mas sem memória suficiente. " "Usando CPU como fallback automático."
            )
            return "cpu"

    return "cpu"


def get_torch_device():
    """
    Retorna torch.device para cálculos PyTorch.

    Returns:
        torch.device("cuda") ou torch.device("cpu")
    """
    import torch

    device_str = get_compute_device()
    return torch.device(device_str)


def ensure_tensor_on_real_device(tensor_or_model) -> None:
    """
    Garante que tensor ou modelo não está em meta device.

    Detecta se model/tensor está em meta device e migra para device real (cuda/cpu).
    Meta device é um device virtual usado durante inicialização, não pode ter dados reais.

    Args:
        tensor_or_model: torch.Tensor, nn.Module, ou SentenceTransformer
    """
    try:
        import torch

        # Se for um módulo ou modelo
        if hasattr(tensor_or_model, "device"):
            # SentenceTransformer ou nn.Module
            current_device = (
                next(tensor_or_model.parameters()).device
                if hasattr(tensor_or_model, "parameters")
                else tensor_or_model.device
            )
        elif isinstance(tensor_or_model, torch.Tensor):
            current_device = tensor_or_model.device
        else:
            return  # Não é tensor/modelo

        # Verificar se está em meta device
        if current_device.type == "meta":
            logger.warning(f"⚠️ Detectado meta device! Migrando para device real...")
            real_device = get_torch_device()

            # Migrar para device real
            if hasattr(tensor_or_model, "to"):
                tensor_or_model.to(real_device)
                logger.info(f"✅ Modelo migrado para {real_device}")
            else:
                raise RuntimeError(f"Não consigo migrar {type(tensor_or_model)} de meta device")

    except Exception as e:
        logger.debug(f"Erro ao checar/migrar meta device: {e}")


def reset_device_cache() -> None:
    """Reseta cache de device (útil para testes)."""
    global _cached_device
    _cached_device = None
