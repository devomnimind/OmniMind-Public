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
import concurrent.futures
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

# Carrega variáveis de ambiente do .env
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Provedores LLM suportados."""

    OLLAMA = "ollama"
    HUGGINGFACE_LOCAL = "huggingface_local"
    HUGGINGFACE = "huggingface"
    HUGGINGFACE_SPACE = "huggingface_space"
    OPENROUTER = "openrouter"
    GEMINI = "gemini"


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
    timeout: int = 120  # 2 minutos para modelos locais
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
                tokens_used=(response.get("eval_count") if isinstance(response, dict) else None),
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
        """Estimativa de latência Ollama (local) - ajustada para produção."""
        return 800  # ~800ms para modelos locais (otimizado)


class HuggingFaceLocalProvider(LLMProviderInterface):
    """Provedor HuggingFace Local (inferência local com transformers)."""

    def __init__(self):
        self._pipeline = None
        self._current_model = None
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Verifica disponibilidade do HuggingFace Local."""
        try:
            # Verifica se torch está disponível (transformers será importado quando necessário)
            import torch

            # Verifica se há GPU disponível
            if torch.cuda.is_available():
                logger.info("HuggingFace Local: GPU disponível para inferência")
            else:
                logger.info("HuggingFace Local: Usando CPU para inferência")

            self._available = True
        except ImportError as e:
            logger.warning(f"HuggingFace Local não disponível: {e}")
            self._available = False
        except Exception as e:
            logger.warning(f"Erro na configuração HuggingFace Local: {e}")
            self._available = False

    def _load_model(self, model_name: str):
        """Carrega modelo se necessário."""
        if self._current_model != model_name or self._pipeline is None:
            try:
                import torch
                from transformers import pipeline

                logger.info(f"Carregando modelo HuggingFace Local: {model_name}")

                # Verificar VRAM disponível antes de tentar GPU
                device = None
                use_gpu = False

                if torch.cuda.is_available():
                    try:
                        # Verificar VRAM livre
                        total_mem = torch.cuda.get_device_properties(0).total_memory
                        # noqa: F841 - não usado, mantido para referência
                        _ = torch.cuda.memory_allocated(0)
                        reserved = torch.cuda.memory_reserved(0)
                        free_mem = total_mem - reserved
                        free_mem_mb = free_mem / (1024**2)

                        # Se VRAM livre < 500MB, usar CPU
                        if free_mem_mb < 500:
                            logger.warning(
                                f"VRAM insuficiente ({free_mem_mb:.0f}MB livre). "
                                "Usando CPU como fallback."
                            )
                            device = -1  # CPU
                            use_gpu = False
                        else:
                            device = 0  # GPU
                            use_gpu = True
                    except Exception as vram_check_error:
                        logger.warning(
                            f"Erro ao verificar VRAM: {vram_check_error}. Tentando GPU..."
                        )
                        device = 0
                        use_gpu = True
                else:
                    logger.info("GPU não disponível, usando CPU")
                    device = -1  # CPU
                    use_gpu = False

                # Carrega pipeline de text-generation
                if use_gpu:
                    self._pipeline = pipeline(
                        "text-generation",
                        model=model_name,
                        device=device,
                        torch_dtype=torch.float16,
                        trust_remote_code=True,  # Permite código remoto para alguns modelos
                    )
                else:
                    self._pipeline = pipeline(
                        "text-generation",
                        model=model_name,
                        device=device,
                        trust_remote_code=True,  # Permite código remoto para alguns modelos
                    )

                self._current_model = model_name
                device_str = "GPU" if use_gpu else "CPU"
                logger.info(f"Modelo {model_name} carregado com sucesso em {device_str}")
            except Exception as e:
                logger.warning(f"Erro ao carregar modelo {model_name}: {e}")
                # Tentar fallback CPU se GPU falhou
                if device != -1:  # type: ignore[name-defined]  # Se não estava já tentando CPU
                    try:
                        logger.info("Tentando fallback para CPU...")
                        from transformers import pipeline

                        self._pipeline = pipeline(
                            "text-generation",
                            model=model_name,
                            device=-1,  # CPU
                            trust_remote_code=True,
                        )
                        self._current_model = model_name
                        logger.info(f"Modelo {model_name} carregado com sucesso em CPU (fallback)")
                    except Exception as cpu_error:
                        logger.error(f"Fallback CPU também falhou: {cpu_error}")
                        self._pipeline = None
                        raise e
                else:
                    self._pipeline = None
                    raise e

    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca HuggingFace Local."""
        if not self.is_available():
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE_LOCAL,
                model=config.model_name,
                latency_ms=0,
                error="HuggingFace Local não disponível",
            )

        start_time = time.time()
        try:
            # Carrega modelo se necessário
            self._load_model(config.model_name)

            if self._pipeline is None:
                return LLMResponse(
                    success=False,
                    text="",
                    provider=LLMProvider.HUGGINGFACE_LOCAL,
                    model=config.model_name,
                    latency_ms=0,
                    error="Modelo não pôde ser carregado",
                )

            # Função síncrona para gerar texto
            def _generate_text():
                try:
                    pipeline = self._pipeline
                    if pipeline is None:
                        raise RuntimeError("Pipeline is None")

                    logger.debug(f"Gerando texto com prompt: {prompt[:100]}...")
                    logger.debug(
                        f"Config: max_new_tokens={config.max_tokens}, "
                        f"temperature={config.temperature}"
                    )

                    # Gera texto
                    outputs = pipeline(
                        prompt,
                        max_new_tokens=config.max_tokens,
                        temperature=config.temperature,
                        do_sample=True,
                        top_p=0.9,
                        pad_token_id=getattr(pipeline.tokenizer, "eos_token_id", None),
                        return_full_text=False,  # Não retorna o prompt
                    )

                    logger.debug(f"Pipeline output type: {type(outputs)}")
                    logger.debug(f"Pipeline output: {outputs}")

                    # Extrai texto gerado
                    if isinstance(outputs, list) and outputs:
                        generated_text = outputs[0].get("generated_text", "")
                        logger.debug(f"Texto extraído da lista: {generated_text[:100]}...")
                    else:
                        generated_text = str(outputs)
                        logger.debug(f"Texto convertido para string: {generated_text[:100]}...")

                    return generated_text.strip()
                except Exception as e:
                    logger.error(f"Erro durante geração de texto: {e}")
                    logger.error(f"Tipo do erro: {type(e)}")
                    import traceback

                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise e

            # Executa em thread separada para não bloquear
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_generate_text)
                response = future.result(timeout=config.timeout)

            latency = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=True,
                text=response,
                provider=LLMProvider.HUGGINGFACE_LOCAL,
                model=config.model_name,
                latency_ms=latency,
            )

        except concurrent.futures.TimeoutError:
            latency = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE_LOCAL,
                model=config.model_name,
                latency_ms=latency,
                error=f"Timeout após {config.timeout}s",
            )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"Erro no HuggingFace Local: {e}")
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE_LOCAL,
                model=config.model_name,
                latency_ms=latency,
                error=str(e),
            )

    def is_available(self) -> bool:
        """Verifica se HuggingFace Local está disponível."""
        return self._available

    def get_latency_estimate(self) -> int:
        """Estimativa de latência HF Local - ajustada para produção."""
        return 3000  # ~3s para inferência local (depende do modelo/HW)


class HuggingFaceProvider(LLMProviderInterface):
    """Provedor HuggingFace (Inference API)."""

    def __init__(self):
        self._client = None
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Verifica disponibilidade do HuggingFace Inference API."""
        try:
            # Verifica se temos token HF
            token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
            if not token:
                logger.warning("Token HuggingFace não encontrado")
                return

            # Verifica se huggingface_hub está disponível
            try:
                from huggingface_hub import InferenceClient

                self._client = InferenceClient(token=token)
                # Testa conectividade com um modelo simples
                try:
                    # Teste rápido de conectividade
                    self._client.text_generation("test", model="gpt2", max_new_tokens=1)
                    self._available = True
                except Exception:
                    # Se falhar o teste, ainda marca como disponível pois pode ser temporário
                    self._available = True
            except ImportError:
                logger.warning("huggingface_hub não disponível para HF Inference API")
                self._available = False

        except Exception as e:
            logger.warning(f"Erro na verificação HuggingFace: {e}")
            self._available = False

    def _load_model(self, model_name: str):
        """Não necessário para Inference API."""
        pass

    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca HuggingFace Inference API."""
        if not self.is_available():
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE,
                model=config.model_name,
                latency_ms=0,
                error="HuggingFace não disponível",
            )

        start_time = time.time()
        try:
            if self._client is None:
                return LLMResponse(
                    success=False,
                    text="",
                    provider=LLMProvider.HUGGINGFACE,
                    model=config.model_name,
                    latency_ms=0,
                    error="HF Inference API client not initialized",
                )

            # Função síncrona para gerar texto
            def _generate_text():
                try:
                    client = self._client
                    if client is None:
                        raise RuntimeError("Client is None")
                    return client.text_generation(
                        prompt=prompt,
                        model=config.model_name,
                        max_new_tokens=config.max_tokens,
                        temperature=config.temperature,
                        do_sample=True,
                        top_p=0.9,
                    )
                except Exception as e:
                    raise e

            # Executa em thread separada para não bloquear
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_generate_text)
                response = future.result(timeout=config.timeout)

            latency = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=True,
                text=response,
                provider=LLMProvider.HUGGINGFACE,
                model=config.model_name,
                latency_ms=latency,
            )

        except concurrent.futures.TimeoutError:
            latency = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE,
                model=config.model_name,
                latency_ms=latency,
                error=f"Timeout após {config.timeout}s",
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
        """Estimativa de latência HF Inference API (cloud) - ajustada para produção."""
        return 2000  # ~2s para Inference API (otimizado)


class HuggingFaceSpaceProvider(LLMProviderInterface):
    """Provedor HuggingFace Space (inferência via API)."""

    def __init__(self):
        self._client = None
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Verifica disponibilidade do HuggingFace Space."""
        space_url = os.getenv("HF_SPACE_URL")
        if not space_url:
            logger.warning("HF_SPACE_URL não encontrada")
            return

        try:
            import requests

            self._client = requests.Session()
            # Testa conectividade via endpoint /health
            response = self._client.get(f"{space_url}/health", timeout=5)
            if response.status_code == 200:
                self._available = True
            else:
                logger.warning(f"Space health check falhou: {response.status_code}")
        except ImportError:
            logger.warning("requests não disponível para HF Space")
            self._available = False
        except Exception as e:
            logger.warning(f"Erro na configuração HF Space: {e}")
            self._available = False

    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca HuggingFace Space."""
        if not self.is_available():
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE_SPACE,
                model=config.model_name,
                latency_ms=0,
                error="HuggingFace Space não disponível",
            )

        space_url = os.getenv("HF_SPACE_URL")
        if not space_url:
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE_SPACE,
                model=config.model_name,
                latency_ms=0,
                error="HF_SPACE_URL não configurada",
            )

        start_time = time.time()
        try:
            if self._client is None:
                return LLMResponse(
                    success=False,
                    text="",
                    provider=LLMProvider.HUGGINGFACE_SPACE,
                    model=config.model_name,
                    latency_ms=0,
                    error="HF Space client not initialized",
                )

            # Payload para inferência (ajuste conforme o Space)
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": config.max_tokens,
                    "temperature": config.temperature,
                    "do_sample": True,
                },
            }

            # Faz request async
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{space_url}/generate",  # Ajuste endpoint conforme Space
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Extrai texto (ajuste conforme resposta do Space)
                        generated_text = result.get("generated_text", "")
                        if isinstance(generated_text, list) and generated_text:
                            generated_text = generated_text[0].get("generated_text", "")

                        # Garante que é string
                        if generated_text is None:
                            generated_text = ""
                        if not isinstance(generated_text, str):
                            generated_text = str(generated_text)

                        # Remove prompt se presente
                        if generated_text.startswith(prompt):
                            generated_text = generated_text[len(prompt) :].strip()

                        latency = int((time.time() - start_time) * 1000)
                        return LLMResponse(
                            success=True,
                            text=generated_text,
                            provider=LLMProvider.HUGGINGFACE_SPACE,
                            model=config.model_name,
                            latency_ms=latency,
                        )
                    else:
                        error_text = await response.text()
                        latency = int((time.time() - start_time) * 1000)
                        return LLMResponse(
                            success=False,
                            text="",
                            provider=LLMProvider.HUGGINGFACE_SPACE,
                            model=config.model_name,
                            latency_ms=latency,
                            error=f"HTTP {response.status}: {error_text}",
                        )

        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"Erro no HF Space: {e}")
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.HUGGINGFACE_SPACE,
                model=config.model_name,
                latency_ms=latency,
                error=str(e),
            )

    def is_available(self) -> bool:
        """Verifica se HuggingFace Space está disponível."""
        return self._available

    def get_latency_estimate(self) -> int:
        """Estimativa de latência HF Space (cloud) - ajustada para produção."""
        return 1500  # ~1.5s para Spaces (otimizado)


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
        """Estimativa de latência OpenRouter (cloud) - ajustada para produção."""
        return 2000  # ~2s para API cloud (otimizado)


class GeminiProvider(LLMProviderInterface):
    """Provedor Google Gemini."""

    def __init__(self):
        self._client = None
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Verifica disponibilidade do Gemini."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY não encontrada")
            return

        try:
            import google.generativeai as genai  # type: ignore[import-not-found]

            genai.configure(api_key=api_key)
            self._client = genai
            self._available = True
        except ImportError:
            logger.warning("google-generativeai não disponível para Gemini")
            self._available = False
        except Exception as e:
            logger.warning(f"Erro na configuração Gemini: {e}")
            self._available = False

    async def invoke(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Invoca Gemini."""
        if not self.is_available():
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.GEMINI,
                model=config.model_name,
                latency_ms=0,
                error="Gemini não disponível",
            )

        start_time = time.time()
        try:
            if self._client is None:
                return LLMResponse(
                    success=False,
                    text="",
                    provider=LLMProvider.GEMINI,
                    model=config.model_name,
                    latency_ms=0,
                    error="Gemini client not initialized",
                )

            # Store client reference to avoid None check issues in lambda
            client = self._client
            model = client.GenerativeModel(config.model_name)

            # Configurar geração
            generation_config = client.types.GenerationConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.generate_content(
                    prompt,
                    generation_config=generation_config,
                ),
            )

            latency = int((time.time() - start_time) * 1000)
            content = response.text if response.text else ""

            return LLMResponse(
                success=True,
                text=content,
                provider=LLMProvider.GEMINI,
                model=config.model_name,
                latency_ms=latency,
            )

        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"Erro no Gemini: {e}")
            return LLMResponse(
                success=False,
                text="",
                provider=LLMProvider.GEMINI,
                model=config.model_name,
                latency_ms=latency,
                error=str(e),
            )

    def is_available(self) -> bool:
        """Verifica se Gemini está disponível."""
        return self._available

    def get_latency_estimate(self) -> int:
        """Estimativa de latência Gemini (cloud) - ajustada para produção."""
        return 1500  # ~1.5s para Gemini API (otimizado)


class LLMRouter:
    """
    Router inteligente de LLMs com fallback automático.

    Estratégia de fallback:
    1. Ollama (local, mais rápido)
    2. HuggingFace Local (inferência local com transformers)
    3. HuggingFace Space (cloud inference)
    4. HuggingFace (Inference API cloud)
    5. OpenRouter (cloud, múltiplos modelos)
    """

    def __init__(self):
        # Inicializa provedores
        self.providers = {
            LLMProvider.OLLAMA: OllamaProvider(),
            LLMProvider.HUGGINGFACE_LOCAL: HuggingFaceLocalProvider(),
            LLMProvider.HUGGINGFACE: HuggingFaceProvider(),
            LLMProvider.HUGGINGFACE_SPACE: HuggingFaceSpaceProvider(),
            LLMProvider.OPENROUTER: OpenRouterProvider(),
            LLMProvider.GEMINI: GeminiProvider(),
        }

        # Configurações por tier
        self.tier_configs = self._load_tier_configs()

        # Métricas
        self.metrics: Dict[str, Any] = {
            "requests_total": 0,
            "requests_success": 0,
            "latency_by_provider": {},
            "fallback_used": 0,
        }

        logger.info("LLM Router inicializado com fallback automático")

    def _load_tier_configs(self) -> Dict[LLMModelTier, List[LLMConfig]]:
        """Carrega configurações de modelos por tier com modelos offline prioritários."""
        return {
            LLMModelTier.FAST: [
                # 🔥 PRIORIDADE: Modelos Offline Locais (Ollama)
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="phi:latest",  # Modelo Phi-3 baixado localmente
                    temperature=0.7,
                    max_tokens=1024,
                    timeout=60,
                    tier=LLMModelTier.FAST,
                ),
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="llama3.2:1b",  # Modelo Llama 3.2 1B baixado localmente
                    temperature=0.7,
                    max_tokens=1024,
                    timeout=45,
                    tier=LLMModelTier.FAST,
                ),
                # 🔄 FALLBACK: HuggingFace Local (inferência local)
                LLMConfig(
                    provider=LLMProvider.HUGGINGFACE_LOCAL,
                    model_name="microsoft/Phi-3.5-mini-instruct",  # Modelo baixado localmente
                    temperature=0.7,
                    max_tokens=1024,
                    timeout=120,
                    tier=LLMModelTier.FAST,
                ),
                # ☁️ ÚLTIMO FALLBACK: Cloud APIs (OpenRouter)
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="microsoft/wizardlm-2-8x22b",  # Modelo gratuito similar ao Phi
                    temperature=0.7,
                    max_tokens=1024,
                    timeout=60,
                    tier=LLMModelTier.FAST,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="z-ai/glm-4.5-air:free",  # GLM-4.5 Air gratuito
                    temperature=0.7,
                    max_tokens=1024,
                    timeout=60,
                    tier=LLMModelTier.FAST,
                ),
            ],
            LLMModelTier.BALANCED: [
                # 🔥 PRIORIDADE: Modelos Offline Locais (Ollama)
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="phi:latest",  # Modelo Phi-3 principal
                    temperature=0.7,
                    max_tokens=2048,
                    timeout=90,
                    tier=LLMModelTier.BALANCED,
                ),
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="llama3.2:1b",  # Llama 3.2 como backup
                    temperature=0.7,
                    max_tokens=2048,
                    timeout=75,
                    tier=LLMModelTier.BALANCED,
                ),
                # 🔄 FALLBACK: HuggingFace Local
                LLMConfig(
                    provider=LLMProvider.HUGGINGFACE_LOCAL,
                    model_name="microsoft/Phi-3.5-mini-instruct",  # Phi-3.5 local
                    temperature=0.7,
                    max_tokens=2048,
                    timeout=180,
                    tier=LLMModelTier.BALANCED,
                ),
                # ☁️ ÚLTIMO FALLBACK: Cloud APIs
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="microsoft/wizardlm-2-8x22b",  # WizardLM gratuito
                    temperature=0.7,
                    max_tokens=2048,
                    timeout=90,
                    tier=LLMModelTier.BALANCED,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="z-ai/glm-4.5-air:free",  # GLM-4.5 Air
                    temperature=0.7,
                    max_tokens=2048,
                    timeout=90,
                    tier=LLMModelTier.BALANCED,
                ),
            ],
            LLMModelTier.HIGH_QUALITY: [
                # 🔥 PRIORIDADE: Modelos Offline Locais (Ollama)
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="phi:latest",  # Phi-3 para alta qualidade
                    temperature=0.7,
                    max_tokens=4096,
                    timeout=180,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="llama3.2:1b",  # Llama 3.2 como backup
                    temperature=0.7,
                    max_tokens=4096,
                    timeout=150,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                # 🔄 FALLBACK: HuggingFace Local
                LLMConfig(
                    provider=LLMProvider.HUGGINGFACE_LOCAL,
                    model_name="microsoft/Phi-3.5-mini-instruct",  # Phi-3.5 local
                    temperature=0.7,
                    max_tokens=4096,
                    timeout=300,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                # ☁️ ÚLTIMO FALLBACK: Cloud APIs (modelos premium)
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="anthropic/claude-3.5-sonnet",  # Claude 3.5 Sonnet (pago)
                    temperature=0.7,
                    max_tokens=4096,
                    timeout=180,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="openai/gpt-4o-mini",  # GPT-4o Mini (pago)
                    temperature=0.7,
                    max_tokens=4096,
                    timeout=180,
                    tier=LLMModelTier.HIGH_QUALITY,
                ),
                LLMConfig(
                    provider=LLMProvider.OPENROUTER,
                    model_name="google/gemini-pro-1.5",  # Gemini Pro 1.5 (pago)
                    temperature=0.7,
                    max_tokens=4096,
                    timeout=180,
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
        Invoca LLM com fallback automático e retry com exponential backoff.

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

        fallback_count = 0

        # Tenta cada configuração em ordem com retry
        for attempt, config in enumerate(configs):
            provider = self.providers[config.provider]

            # Pula se provedor não disponível
            if not provider.is_available():
                logger.debug(
                    f"[Attempt {attempt + 1}/{len(configs)}] Provedor {config.provider.value} "
                    f"não disponível, tentando próximo"
                )
                continue

            logger.debug(
                f"[Attempt {attempt + 1}/{len(configs)}] Tentando {config.provider.value} "
                f"com modelo {config.model_name}"
            )

            # Invoca provedor com retry
            for retry_attempt in range(1, config.retry_attempts + 1):
                try:
                    response = await asyncio.wait_for(
                        provider.invoke(prompt, config),
                        timeout=config.timeout,
                    )

                    # Registra métricas
                    provider_key = config.provider.value
                    if provider_key not in self.metrics["latency_by_provider"]:
                        self.metrics["latency_by_provider"][provider_key] = []
                    self.metrics["latency_by_provider"][provider_key].append(response.latency_ms)

                    if response.success:
                        self.metrics["requests_success"] += 1
                        if fallback_count > 0:
                            self.metrics["fallback_used"] += 1
                            logger.info(
                                f"[Fallback #{fallback_count}] LLM request successful via "
                                f"{config.provider.value} ({response.model}) - "
                                f"Latency: {response.latency_ms}ms"
                            )
                        else:
                            logger.info(
                                f"LLM request successful via {config.provider.value} "
                                f"({response.model}) - Latency: {response.latency_ms}ms"
                            )
                        return response
                    else:
                        logger.warning(
                            f"[Attempt {retry_attempt}/{config.retry_attempts}] "
                            f"Falha no {config.provider.value}: {response.error}"
                        )

                except asyncio.TimeoutError:
                    logger.warning(
                        f"[Attempt {retry_attempt}/{config.retry_attempts}] "
                        f"Timeout no {config.provider.value} (>{config.timeout}s)"
                    )
                except Exception as e:
                    logger.error(
                        f"[Attempt {retry_attempt}/{config.retry_attempts}] "
                        f"Erro no {config.provider.value}: {str(e)}"
                    )

                # Exponential backoff entre retries
                if retry_attempt < config.retry_attempts:
                    backoff_delay = 2 ** (retry_attempt - 1)
                    logger.debug(f"Aguardando {backoff_delay}s antes de retry...")
                    await asyncio.sleep(backoff_delay)

            fallback_count += 1

        # Todos os provedores falharam
        logger.error(
            f"❌ Todos os {len(configs)} provedores LLM falharam após "
            f"{fallback_count} fallbacks"
        )
        return LLMResponse(
            success=False,
            text="",
            provider=LLMProvider.OLLAMA,
            model="unknown",
            latency_ms=0,
            error="Todos os provedores LLM falharam após múltiplas tentativas",
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
    Evita deadlock com asyncio.run() dentro de loops já rodando.
    """
    try:
        # Verificar se estamos em um loop rodando
        asyncio.get_running_loop()
        # Se estamos em um loop, usar thread com novo event loop
        import threading

        result_container = []
        exception_container = []

        def run_in_new_loop():
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(_invoke_async(prompt, **kwargs))
                    result_container.append(result)
                finally:
                    new_loop.close()
            except Exception as e:
                exception_container.append(e)

        thread = threading.Thread(target=run_in_new_loop, daemon=False)
        thread.start()
        thread.join(timeout=120)  # 2 minutos de timeout

        if exception_container:
            raise exception_container[0]
        if not result_container:
            raise TimeoutError("LLM invocation timed out after 120s")
        return result_container[0]

    except RuntimeError:
        # Não estamos em um loop, podemos usar asyncio.run() diretamente
        return asyncio.run(_invoke_async(prompt, **kwargs))


async def _invoke_async(prompt: str, **kwargs) -> LLMResponse:
    """Função auxiliar async para invoke_llm_sync."""
    router = get_llm_router()
    return await router.invoke(prompt, **kwargs)
