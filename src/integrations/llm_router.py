"""
LLM Fallback Architecture - OmniMind
====================================

Este módulo implementa uma arquitetura robusta de fallback para LLMs,
garantindo alta disponibilidade e performance otimizada.

Arquitetura:
1. Ollama (Local) - Prioridade máxima, menor latência
2. HuggingFace (Local Inference) - Fallback quando Ollama falha
3. OpenRouter (Cloud) - Fallback final com múltiplos modelos

Benefícios:
- Zero dependência de cloud para operações críticas
- Fallback automático e transparente
- Múltiplos modelos OpenRouter para diversidade
- Monitoramento e métricas de performance
- Recuperação automática de falhas

Autor: OmniMind Team
Data: 2025-11-27
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import os

# Carrega variáveis de ambiente do .env
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Provedores LLM suportados."""

    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENROUTER = "openrouter"


class LLMModelTier(Enum):
    """Níveis de qualidade/modelo para fallback."""

    FAST = "fast"  # Modelos rápidos, menor qualidade
    BALANCED = "balanced"  # Equilíbrio qualidade/performance
    HIGH_QUALITY = "high_quality"  # Melhor qualidade, mais lento


@dataclass
class LLMConfig:
    """Configuração para um provedor LLM."""

    provider: LLMProvider
    model_name: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    retry_attempts: int = 2
    tier: LLMModelTier = LLMModelTier.BALANCED


@dataclass
class LLMResponse:
    """Resposta padronizada de LLM."""

    success: bool
    text: str
    provider: LLMProvider
    model: str
    latency_ms: int
    tokens_used: Optional[int] = None
    error: Optional[str] = None


class LLMProviderInterface(ABC):
    """Interface abstrata para provedores LLM."""

    @abstractmethod
    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca o LLM com o prompt fornecido."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provedor está disponível."""
        pass

    @abstractmethod
    def get_latency_estimate(self) -> int:
        """Retorna estimativa de latência em ms."""
        pass


class OllamaProvider(LLMProviderInterface):
    """Provedor Ollama (local)."""

    def __init__(self):
        self._client = None
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Verifica disponibilidade do Ollama."""
        try:
            import ollama

            # Tenta listar modelos para verificar se Ollama está rodando
            ollama.list()
            self._available = True
            self._client = ollama
        except Exception as e:
            logger.warning(f"Ollama não disponível: {e}")
            self._available = False

    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca Ollama."""
        if not self.is_available():
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.OLLAMA,
                model=config.model_name,
                latency_ms=0,
                error="Ollama não disponível",
            )

        start_time = time.time()
        try:
            if self._client is None:
                return LLMResponse(
                    success=False,
                    text="",
                    provider=LLMProvider.OLLAMA,
                    model=config.model_name,
                    latency_ms=0,
                    error="Ollama client not initialized",
                )

            # Store client reference to avoid None check issues in lambda
            client = self._client
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.generate(
                    model=config.model_name,
                    prompt=prompt,
                    options={
                        "temperature": config.temperature,
                        "num_predict": config.max_tokens,
                    },
                ),
            )

            latency = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=True,
                text=response["response"],
                provider=LLMProvider.OLLAMA,
                model=config.model_name,
                latency_ms=latency,
                tokens_used=response.get("eval_count"),
            )

        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"Erro no Ollama: {e}")
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.OLLAMA,
                model=config.model_name,
                latency_ms=latency,
                error=str(e),
            )

    def is_available(self) -> bool:
        """Verifica se Ollama está disponível."""
        return self._available

    def get_latency_estimate(self) -> int:
        """Estimativa de latência Ollama (local)."""
        return 500  # ~500ms para modelos locais


class HuggingFaceProvider(LLMProviderInterface):
    """Provedor HuggingFace (inferência local)."""

    def __init__(self):
        self._pipeline = None
        self._available = False
        self._model_name = None
        self._check_availability()

    def _check_availability(self):
        """Verifica disponibilidade do HuggingFace."""
        try:
            # Verifica se temos token HF
            token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
            if not token:
                logger.warning("Token HuggingFace não encontrado")
                return

            # Verifica se transformers está disponível
            try:
                import transformers  # noqa: F401
            except ImportError:
                pass
            self._available = True

        except ImportError:
            logger.warning("transformers não disponível")
            self._available = False
        except Exception as e:
            logger.warning(f"Erro na verificação HuggingFace: {e}")
            self._available = False

    def _load_model(self, model_name: str):
        """Carrega modelo sob demanda."""
        if self._pipeline and self._model_name == model_name:
            return  # Já carregado

        try:
            from transformers import pipeline
            import torch

            # Configuração para GPU se disponível
            device = 0 if torch.cuda.is_available() else -1

            self._pipeline = pipeline(
                "text-generation",
                model=model_name,
                device=device,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                token=os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN"),
            )
            self._model_name = model_name
            logger.info(f"Modelo HF carregado: {model_name}")

        except Exception as e:
            logger.error(f"Erro carregando modelo HF {model_name}: {e}")
            self._available = False

    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca HuggingFace."""
        if not self.is_available():
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE,
                model=config.model_name,
                latency_ms=0,
                error="HuggingFace não disponível",
            )

        # Carrega modelo se necessário
        self._load_model(config.model_name)

        if not self._pipeline:
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE,
                model=config.model_name,
                latency_ms=0,
                error="Falha ao carregar modelo",
            )

        start_time = time.time()
        try:
            # Gera resposta
            pad_token_id = None
            if self._pipeline and hasattr(self._pipeline, "tokenizer") and self._pipeline.tokenizer:
                pad_token_id = getattr(self._pipeline.tokenizer, "eos_token_id", None)

            outputs = self._pipeline(
                prompt,
                max_new_tokens=config.max_tokens,
                temperature=config.temperature,
                do_sample=True,
                pad_token_id=pad_token_id,
            )

            # Extrai texto gerado
            generated_text = outputs[0]["generated_text"]
            # Remove o prompt do início se presente
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt) :].strip()

            latency = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=True,
                text=generated_text,
                provider=LLMProvider.HUGGINGFACE,
                model=config.model_name,
                latency_ms=latency,
            )

        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"Erro no HuggingFace: {e}")
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE,
                model=config.model_name,
                latency_ms=latency,
                error=str(e),
            )

    def is_available(self) -> bool:
        """Verifica se HuggingFace está disponível."""
        return self._available

    def get_latency_estimate(self) -> int:
        """Estimativa de latência HF (local com GPU)."""
        return 2000  # ~2s para modelos locais


class OpenRouterProvider(LLMProviderInterface):
    """Provedor OpenRouter (cloud com múltiplos modelos)."""

    def __init__(self):
        self._client = None
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Verifica disponibilidade do OpenRouter."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.warning("OPENROUTER_API_KEY não encontrada")
            return

        try:
            import openai

            self._client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
            self._available = True
        except ImportError:
            logger.warning("openai não disponível para OpenRouter")
            self._available = False
        except Exception as e:
            logger.warning(f"Erro na configuração OpenRouter: {e}")
            self._available = False

    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca OpenRouter."""
        if not self.is_available():
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.OPENROUTER,
                model=config.model_name,
                latency_ms=0,
                error="OpenRouter não disponível",
            )

        start_time = time.time()
        try:
            if self._client is None:
                return LLMResponse(
                    success=False,
                    text="",
                    provider=LLMProvider.OPENROUTER,
                    model=config.model_name,
                    latency_ms=0,
                    error="OpenRouter client not initialized",
                )

            # Store client reference to avoid None check issues in lambda
            client = self._client
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=config.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout,
                ),
            )

            latency = int((time.time() - start_time) * 1000)
            content = response.choices[0].message.content
            if content is None:
                content = ""

            return LLMResponse(
                success=True,
                text=content,
                provider=LLMProvider.OPENROUTER,
                model=config.model_name,
                latency_ms=latency,
                tokens_used=response.usage.total_tokens if response.usage else None,
            )

        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"Erro no OpenRouter: {e}")
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.OPENROUTER,
                model=config.model_name,
                latency_ms=latency,
                error=str(e),
            )

    def is_available(self) -> bool:
        """Verifica se OpenRouter está disponível."""
        return self._available

    def get_latency_estimate(self) -> int:
        """Estimativa de latência OpenRouter (cloud)."""
        return 3000  # ~3s para API cloud


class LLMRouter:
    """
    Router inteligente de LLMs com fallback automático.

    Estratégia de fallback:
    1. Ollama (local, mais rápido)
    2. HuggingFace (local inference)
    3. OpenRouter (cloud, múltiplos modelos)
    """

    def __init__(self):
        # Inicializa provedores
        self.providers = {
            LLMProvider.OLLAMA: OllamaProvider(),
            LLMProvider.HUGGINGFACE: HuggingFaceProvider(),
            LLMProvider.OPENROUTER: OpenRouterProvider(),
        }

        # Configurações por tier
        self.tier_configs = self._load_tier_configs()

        # Métricas
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "latency_by_provider": {},
            "fallback_used": 0,
        }

        logger.info("LLM Router inicializado com fallback automático")

    def _load_tier_configs(self) -> Dict[LLMModelTier, List[LLMConfig]]:
        """Carrega configurações de modelos por tier."""
        return {
            LLMModelTier.FAST: [
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2:7b-instruct",  # Modelo disponível localmente
                    temperature=0.7,
                    max_tokens=1024,
                    tier=LLMModelTier.FAST,
                ),
                LLMConfig(
                    provider=LLMProvider.HUGGINGFACE,
                    model_name="microsoft/DialoGPT-small",
                    temperature=0.7,
                    max_tokens=1024,
                    tier=LLMModelTier.FAST,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="microsoft/wizardlm-2-8x22b",
                    temperature=0.7,
                    max_tokens=1024,
                    tier=LLMModelTier.FAST,
                ),
            ],
            LLMModelTier.BALANCED: [
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2:7b-instruct",  # Modelo atual
                    temperature=0.7,
                    max_tokens=2048,
                    tier=LLMModelTier.BALANCED,
                ),
                LLMConfig(
                    provider=LLMProvider.HUGGINGFACE,
                    model_name="microsoft/DialoGPT-medium",
                    temperature=0.7,
                    max_tokens=2048,
                    tier=LLMModelTier.BALANCED,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="anthropic/claude-3-haiku",
                    temperature=0.7,
                    max_tokens=2048,
                    tier=LLMModelTier.BALANCED,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="openai/gpt-4o-mini",
                    temperature=0.7,
                    max_tokens=2048,
                    tier=LLMModelTier.BALANCED,
                ),
            ],
            LLMModelTier.HIGH_QUALITY: [
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2:72b-instruct",  # Modelo grande se disponível
                    temperature=0.7,
                    max_tokens=4096,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                LLMConfig(
                    provider=LLMProvider.HUGGINGFACE,
                    model_name="microsoft/DialoGPT-large",
                    temperature=0.7,
                    max_tokens=4096,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="anthropic/claude-3-5-sonnet",
                    temperature=0.7,
                    max_tokens=4096,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="openai/gpt-4o",
                    temperature=0.7,
                    max_tokens=4096,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="google/gemini-pro-1.5",
                    temperature=0.7,
                    max_tokens=4096,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
            ],
        }

    async def invoke(
        self,
        prompt: str,
        tier: LLMModelTier = LLMModelTier.BALANCED,
        preferred_provider: Optional[LLMProvider] = None,
    ) -> LLMResponse:
        """
        Invoca LLM com fallback automático.

        Args:
            prompt: Texto do prompt
            tier: Tier de qualidade desejada
            preferred_provider: Provedor preferido (opcional)

        Returns:
            LLMResponse com resultado
        """
        self.metrics["requests_total"] += 1

        configs = self.tier_configs[tier]

        # Se especificou provedor preferido, tenta primeiro
        if preferred_provider:
            preferred_configs = [c for c in configs if c.provider == preferred_provider]
            if preferred_configs:
                configs = preferred_configs + [
                    c for c in configs if c.provider != preferred_provider
                ]

        # Tenta cada configuração em ordem
        for config in configs:
            provider = self.providers[config.provider]

            # Pula se provedor não disponível
            if not provider.is_available():
                logger.debug(f"Provedor {config.provider.value} não disponível, tentando próximo")
                continue

            logger.debug(
                f"Tentando provedor {config.provider.value} com modelo {config.model_name}"
            )

            # Invoca provedor
            response = await provider.invoke(prompt, config)

            # Registra métricas
            provider_key = config.provider.value
            if provider_key not in self.metrics["latency_by_provider"]:
                self.metrics["latency_by_provider"][provider_key] = []
            self.metrics["latency_by_provider"][provider_key].append(response.latency_ms)

            if response.success:
                self.metrics["requests_success"] += 1
                if config.provider != configs[0].provider:
                    # Se não foi o primeiro (fallback usado)
                    self.metrics["fallback_used"] += 1
                logger.info(f"LLM request successful via {config.provider.value}")
                return response
            else:
                logger.warning(f"Falha no provedor {config.provider.value}: " f"{response.error}")

        # Todos os provedores falharam
        logger.error("Todos os provedores LLM falharam")
        return LLMResponse(
            success=False,
            text="",
            provider=LLMProvider.OLLAMA,  # Default
            model="unknown",
            latency_ms=0,
            error="Todos os provedores " "LLM falharam",
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de uso."""
        metrics = self.metrics.copy()

        # Calcula médias de latência
        for provider, latencies in metrics["latency_by_provider"].items():
            if latencies:
                metrics["latency_by_provider"][provider] = {
                    "avg_ms": sum(latencies) / len(latencies),
                    "min_ms": min(latencies),
                    "max_ms": max(latencies),
                    "count": len(latencies),
                }

        return metrics

    def get_provider_status(self) -> Dict[str, bool]:
        """Retorna status de disponibilidade de cada provedor."""
        return {provider.value: self.providers[provider].is_available() for provider in LLMProvider}


# Instância global do router
_llm_router = None


def get_llm_router() -> LLMRouter:
    """Factory function para obter instância do LLM Router."""
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router


# Função de compatibilidade para substituir chamadas diretas
async def invoke_llm(prompt: str, **kwargs) -> LLMResponse:
    """
    Função de compatibilidade para invocar LLM com fallback.

    Substitui chamadas diretas como ollama.generate() ou openai.chat.completions.create().
    """
    router = get_llm_router()
    return await router.invoke(prompt, **kwargs)


def invoke_llm_sync(prompt: str, **kwargs) -> LLMResponse:
    """
    Função síncrona de compatibilidade para invocar LLM com fallback.

    Para uso em contextos síncronos como LangGraph nodes.
    """
    try:
        # Verificar se estamos em um loop rodando
        asyncio.get_running_loop()
        # Se estamos em um loop, usar ThreadPoolExecutor
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _invoke_async(prompt, **kwargs))
            return future.result()
    except RuntimeError:
        # Não estamos em um loop, podemos usar asyncio.run()
        return asyncio.run(_invoke_async(prompt, **kwargs))


async def _invoke_async(prompt: str, **kwargs) -> LLMResponse:
    """Função auxiliar async para invoke_llm_sync."""
    router = get_llm_router()
    return await router.invoke(prompt, **kwargs)
