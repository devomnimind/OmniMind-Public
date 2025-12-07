"""
Model Optimizer - Otimização de Modelos para Inferência Eficiente

Implementa:
- Quantização INT8 para reduzir memória e acelerar inferência
- KV Cache optimization para reduzir recomputação
- Model routing inteligente (fast path vs slow path)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import torch
    from torch import nn

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch não disponível. Funcionalidades de quantização limitadas.")


class ModelPrecision(Enum):
    """Precisão do modelo."""

    FP32 = "fp32"  # Full precision
    FP16 = "fp16"  # Half precision
    INT8 = "int8"  # Quantized
    INT4 = "int4"  # Ultra quantized (futuro)


@dataclass
class ModelConfig:
    """Configuração de um modelo otimizado."""

    model_name: str
    precision: ModelPrecision
    use_kv_cache: bool
    cache_size: int  # Tamanho do KV cache
    device: str  # "cpu", "cuda", etc.
    max_length: int  # Comprimento máximo de sequência


class ModelOptimizer:
    """
    Otimizador de modelos para inferência eficiente.

    Características:
    - Quantização INT8 para reduzir memória
    - KV Cache para evitar recomputação
    - Routing inteligente entre modelos
    """

    def __init__(
        self,
        default_precision: ModelPrecision = ModelPrecision.FP32,
        enable_kv_cache: bool = True,
        kv_cache_size: int = 512,
    ):
        """
        Inicializa ModelOptimizer.

        Args:
            default_precision: Precisão padrão para novos modelos
            enable_kv_cache: Se True, habilita KV cache
            kv_cache_size: Tamanho do KV cache
        """
        self.default_precision = default_precision
        self.enable_kv_cache = enable_kv_cache
        self.kv_cache_size = kv_cache_size

        # Cache de modelos otimizados
        self.optimized_models: Dict[str, Any] = {}
        self.model_configs: Dict[str, ModelConfig] = {}

        # KV Cache storage
        self.kv_caches: Dict[str, Dict[str, Any]] = {}

        logger.info(
            f"ModelOptimizer inicializado: precision={default_precision.value}, "
            f"kv_cache={'enabled' if enable_kv_cache else 'disabled'}"
        )

    def quantize_model_int8(
        self, model: Any, model_name: str, calibration_data: Optional[List[str]] = None
    ) -> Optional[Any]:
        """
        Quantiza modelo para INT8.

        Args:
            model: Modelo PyTorch ou SentenceTransformer
            model_name: Nome do modelo
            calibration_data: Dados para calibração (opcional)

        Returns:
            Modelo quantizado ou None se falhar
        """
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch não disponível. Quantização não suportada.")
            return None

        try:
            # Se for SentenceTransformer, pegar o modelo interno
            if hasattr(model, "auto_model"):
                torch_model = model.auto_model
            elif hasattr(model, "model"):
                torch_model = model.model
            elif isinstance(model, nn.Module):
                torch_model = model
            else:
                logger.error(f"Tipo de modelo não suportado para quantização: {type(model)}")
                return None

            # Quantização dinâmica (mais simples, não requer calibração)
            quantized_model = torch.quantization.quantize_dynamic(
                torch_model, {nn.Linear}, dtype=torch.qint8
            )

            logger.info(f"Modelo {model_name} quantizado para INT8")
            return quantized_model

        except Exception as e:
            logger.error(f"Erro ao quantizar modelo {model_name}: {e}")
            return None

    def optimize_embedding_model(
        self,
        model_name: str,
        model: Any,
        precision: Optional[ModelPrecision] = None,
        use_kv_cache: Optional[bool] = None,
    ) -> Optional[Any]:
        """
        Otimiza modelo de embeddings.

        Args:
            model_name: Nome do modelo
            model: Modelo SentenceTransformer ou similar
            precision: Precisão desejada (default: self.default_precision)
            use_kv_cache: Se True, habilita KV cache (default: self.enable_kv_cache)

        Returns:
            Modelo otimizado ou None se falhar
        """
        precision = precision or self.default_precision
        use_kv_cache = use_kv_cache if use_kv_cache is not None else self.enable_kv_cache

        # Se já está otimizado, retornar do cache
        cache_key = f"{model_name}_{precision.value}_{use_kv_cache}"
        if cache_key in self.optimized_models:
            logger.debug(f"Modelo {cache_key} já otimizado, retornando do cache")
            return self.optimized_models[cache_key]

        optimized_model = model

        # Aplicar quantização se necessário
        if precision == ModelPrecision.INT8:
            optimized_model = self.quantize_model_int8(model, model_name)
            if optimized_model is None:
                logger.warning("Falha na quantização, usando modelo original")
                optimized_model = model

        # Configurar KV cache se habilitado
        if use_kv_cache:
            self.kv_caches[model_name] = {}

        # Armazenar configuração
        self.model_configs[model_name] = ModelConfig(
            model_name=model_name,
            precision=precision,
            use_kv_cache=use_kv_cache,
            cache_size=self.kv_cache_size,
            device="cpu",  # TODO: detectar device automaticamente
            max_length=512,
        )

        # Cache do modelo otimizado
        self.optimized_models[cache_key] = optimized_model

        logger.info(
            f"Modelo {model_name} otimizado: precision={precision.value}, "
            f"kv_cache={'enabled' if use_kv_cache else 'disabled'}"
        )

        return optimized_model

    def get_kv_cache(self, model_name: str, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera KV cache para um modelo e chave específicos.

        Args:
            model_name: Nome do modelo
            cache_key: Chave do cache (ex: hash do prompt)

        Returns:
            Cache KV ou None se não existir
        """
        if model_name not in self.kv_caches:
            return None
        return self.kv_caches[model_name].get(cache_key)

    def set_kv_cache(self, model_name: str, cache_key: str, cache_value: Dict[str, Any]) -> None:
        """
        Armazena KV cache para um modelo e chave específicos.

        Args:
            model_name: Nome do modelo
            cache_key: Chave do cache
            cache_value: Valor do cache (keys/values do modelo)
        """
        if model_name not in self.kv_caches:
            self.kv_caches[model_name] = {}

        # Limitar tamanho do cache (LRU simples)
        if len(self.kv_caches[model_name]) >= self.kv_cache_size:
            # Remover entrada mais antiga (simplificado)
            oldest_key = next(iter(self.kv_caches[model_name]))
            del self.kv_caches[model_name][oldest_key]

        self.kv_caches[model_name][cache_key] = cache_value

    def clear_kv_cache(self, model_name: Optional[str] = None) -> None:
        """
        Limpa KV cache.

        Args:
            model_name: Nome do modelo (None para limpar todos)
        """
        if model_name is None:
            self.kv_caches.clear()
            logger.info("Todos os KV caches limpos")
        elif model_name in self.kv_caches:
            self.kv_caches[model_name].clear()
            logger.info(f"KV cache de {model_name} limpo")
        else:
            logger.warning(f"Modelo {model_name} não encontrado no cache")

    def get_model_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos modelos otimizados."""
        stats: Dict[str, Any] = {
            "total_models": len(self.optimized_models),
            "total_caches": sum(len(cache) for cache in self.kv_caches.values()),
            "models": {},
        }

        for name, config in self.model_configs.items():
            cache_size = len(self.kv_caches.get(name, {}))
            stats["models"][name] = {
                "precision": config.precision.value,
                "kv_cache_enabled": config.use_kv_cache,
                "kv_cache_size": cache_size,
                "max_cache_size": config.cache_size,
            }

        return stats


class ModelRouter:
    """
    Router inteligente para direcionar tarefas a modelos otimizados.

    Fast path: modelos quantizados (INT8) para tarefas simples
    Slow path: modelos full precision (FP32) para tarefas complexas
    """

    def __init__(self, optimizer: ModelOptimizer):
        """
        Inicializa ModelRouter.

        Args:
            optimizer: Instância de ModelOptimizer
        """
        self.optimizer = optimizer
        self.routing_stats: Dict[str, int] = {"fast_path": 0, "slow_path": 0}

        logger.info("ModelRouter inicializado")

    def should_use_fast_path(
        self, task_complexity: str, query_length: int, requires_high_precision: bool = False
    ) -> bool:
        """
        Decide se deve usar fast path (quantizado) ou slow path (full precision).

        Args:
            task_complexity: "simple", "medium", "complex"
            query_length: Comprimento da query
            requires_high_precision: Se True, força slow path

        Returns:
            True se deve usar fast path, False para slow path
        """
        if requires_high_precision:
            return False

        # Heurísticas simples
        if task_complexity == "simple" and query_length < 100:
            return True
        elif task_complexity == "medium" and query_length < 200:
            return True
        else:
            return False

    def route_embedding(
        self,
        model_name: str,
        fast_model: Any,
        slow_model: Any,
        text: str,
        task_complexity: str = "medium",
    ) -> Any:
        """
        Roteia geração de embedding para modelo apropriado.

        Args:
            model_name: Nome do modelo
            fast_model: Modelo quantizado (fast path)
            slow_model: Modelo full precision (slow path)
            text: Texto para gerar embedding
            task_complexity: Complexidade da tarefa

        Returns:
            Embedding gerado
        """
        use_fast = self.should_use_fast_path(
            task_complexity=task_complexity,
            query_length=len(text),
            requires_high_precision=False,
        )

        if use_fast:
            self.routing_stats["fast_path"] += 1
            logger.debug(f"Fast path usado para {model_name}")
            return fast_model.encode(text, normalize_embeddings=True)
        else:
            self.routing_stats["slow_path"] += 1
            logger.debug(f"Slow path usado para {model_name}")
            return slow_model.encode(text, normalize_embeddings=True)

    def get_routing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de roteamento."""
        total = sum(self.routing_stats.values())
        fast_pct = (self.routing_stats["fast_path"] / total * 100) if total > 0 else 0
        slow_pct = (self.routing_stats["slow_path"] / total * 100) if total > 0 else 0

        return {
            "fast_path_count": self.routing_stats["fast_path"],
            "slow_path_count": self.routing_stats["slow_path"],
            "fast_path_percentage": fast_pct,
            "slow_path_percentage": slow_pct,
            "total_requests": total,
        }
