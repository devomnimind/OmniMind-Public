"""
External AI Providers Integration - OmniMind
Integração segura com provedores externos de IA (Gemini, Copilot, OpenRouter)

Mantém isolamento completo dos dados internos do OmniMind.
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import structlog
from dotenv import load_dotenv

# Load environment variables for token access
load_dotenv()

logger = structlog.get_logger(__name__)


class TaskType(Enum):
    """Tipos de tarefas suportadas pelos provedores externos"""

    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    DEBUGGING = "debugging"
    TESTING = "testing"


class ProviderCapability(Enum):
    """Capacidades específicas dos provedores"""

    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    ANALYSIS = "analysis"
    DEBUGGING = "debugging"
    MULTIMODAL = "multimodal"


@dataclass
class ProviderCapabilities:
    """Capacidades de um provedor"""

    supported_task_types: List[TaskType]
    capabilities: List[ProviderCapability]
    max_context_length: int
    max_output_tokens: int
    supports_streaming: bool = False
    supports_multimodal: bool = False


@dataclass
class TaskSpec:
    """Especificação de tarefa para delegação externa"""

    task_id: str
    task_type: TaskType
    prompt: str
    context: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, str]]] = None  # [{"name": "file.py", "content": "..."}]
    metadata: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 300


@dataclass
class TaskResult:
    """Resultado de tarefa executada externamente"""

    task_id: str
    success: bool
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    execution_time_seconds: float = 0.0
    provider_used: str = ""


class ExternalAIProvider(ABC):
    """Interface abstrata para provedores externos de IA"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = self._create_rate_limiter()

    @abstractmethod
    async def initialize(self) -> None:
        """Inicializa o provedor (conexões, autenticação, etc.)"""

    @abstractmethod
    async def execute_task(self, task: TaskSpec) -> TaskResult:
        """Executa tarefa de forma isolada"""

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Retorna capacidades do provedor"""

    @abstractmethod
    async def check_rate_limits(self) -> Dict[str, Any]:
        """Verifica limites de uso atuais"""

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Garante que há uma sessão HTTP ativa"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self.session

    def _create_rate_limiter(self) -> Dict[str, Any]:
        """Cria limitador de taxa baseado na configuração"""
        return {
            "requests_per_minute": self.config.get("rate_limits", {}).get(
                "requests_per_minute", 60
            ),
            "tokens_per_minute": self.config.get("rate_limits", {}).get(
                "tokens_per_minute", 100000
            ),
            "last_request_time": 0,
            "request_count": 0,
            "token_count": 0,
        }

    async def _check_rate_limit(self, estimated_tokens: int = 1000) -> bool:
        """Verifica se pode fazer requisição respeitando rate limits"""
        current_time = time.time()

        # Reset counters se passou 1 minuto
        if current_time - self.rate_limiter["last_request_time"] >= 60:
            self.rate_limiter["request_count"] = 0
            self.rate_limiter["token_count"] = 0
            self.rate_limiter["last_request_time"] = current_time

        # Verifica limites
        if self.rate_limiter["request_count"] >= self.rate_limiter["requests_per_minute"]:
            return False

        if (
            self.rate_limiter["token_count"] + estimated_tokens
            > self.rate_limiter["tokens_per_minute"]
        ):
            return False

        return True

    def _update_rate_limit(self, tokens_used: int = 1000) -> None:
        """Atualiza contadores de rate limit"""
        self.rate_limiter["request_count"] += 1
        self.rate_limiter["token_count"] += tokens_used
        self.rate_limiter["last_request_time"] = time.time()

    async def close(self) -> None:
        """Fecha conexões e limpa recursos"""
        if self.session and not self.session.closed:
            await self.session.close()


class GeminiProvider(ExternalAIProvider):
    """Google Gemini integration"""

    async def initialize(self) -> None:
        """Inicializa conexão com Gemini API"""
        await self._ensure_session()

        api_key_env = self.config.get("api_key_env")
        if not api_key_env:
            raise ValueError("api_key_env não configurada")

        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError(f"{api_key_env} não configurada")

        self.base_url = self.config.get("api_base_url", "https://generativelanguage.googleapis.com")

        logger.info("Gemini provider initialized")

    async def execute_task(self, task: TaskSpec) -> TaskResult:
        """Executa tarefa via Gemini API"""
        start_time = time.time()

        try:
            # Verifica rate limits
            if not await self._check_rate_limit():
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error_message="Rate limit exceeded",
                    execution_time_seconds=time.time() - start_time,
                    provider_used="gemini",
                )

            # Prepara payload
            payload = self._prepare_gemini_payload(task)

            # Seleciona modelo baseado na tarefa
            model = self._select_model(task.task_type)

            # Faz requisição
            session = await self._ensure_session()
            url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"

            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error_message=f"Gemini API error: {error_text}",
                        execution_time_seconds=time.time() - start_time,
                        provider_used="gemini",
                    )

                result_data = await response.json()
                content = self._extract_gemini_content(result_data)

                # Atualiza rate limiter
                tokens_used = self._estimate_tokens(task.prompt, content)
                self._update_rate_limit(tokens_used)

                return TaskResult(
                    task_id=task.task_id,
                    success=True,
                    content=content,
                    tokens_used=tokens_used,
                    cost_estimate=self._calculate_cost(model, tokens_used),
                    execution_time_seconds=time.time() - start_time,
                    provider_used="gemini",
                )

        except Exception as e:
            logger.error("Gemini task execution failed", error=str(e), task_id=task.task_id)
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time_seconds=time.time() - start_time,
                provider_used="gemini",
            )

    def get_capabilities(self) -> ProviderCapabilities:
        """Retorna capacidades do Gemini"""
        return ProviderCapabilities(
            supported_task_types=[
                TaskType.CODE_GENERATION,
                TaskType.ANALYSIS,
                TaskType.DOCUMENTATION,
                TaskType.OPTIMIZATION,
            ],
            capabilities=[
                ProviderCapability.TEXT_GENERATION,
                ProviderCapability.CODE_GENERATION,
                ProviderCapability.ANALYSIS,
                ProviderCapability.MULTIMODAL,
            ],
            max_context_length=2097152,  # 2M tokens para Gemini 1.5 Pro
            max_output_tokens=8192,
            supports_streaming=False,
            supports_multimodal=True,
        )

    async def check_rate_limits(self) -> Dict[str, Any]:
        """Verifica limites de uso do Gemini"""
        return {
            "requests_remaining": self.rate_limiter["requests_per_minute"]
            - self.rate_limiter["request_count"],
            "tokens_remaining": self.rate_limiter["tokens_per_minute"]
            - self.rate_limiter["token_count"],
            "reset_in_seconds": 60 - (time.time() - self.rate_limiter["last_request_time"]),
        }

    def _prepare_gemini_payload(self, task: TaskSpec) -> Dict[str, Any]:
        """Prepara payload para Gemini API"""
        # Converte arquivos em partes se houver
        parts = [{"text": task.prompt}]

        if task.files:
            for file_info in task.files:
                parts.append({"text": f"\n--- {file_info['name']} ---\n{file_info['content']}"})

        return {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 4096,
            },
        }

    def _select_model(self, task_type: TaskType) -> str:
        """Seleciona modelo Gemini baseado no tipo de tarefa"""
        model_mapping = {
            TaskType.CODE_GENERATION: "gemini-1.5-pro",
            TaskType.CODE_REVIEW: "gemini-1.5-pro",
            TaskType.ANALYSIS: "gemini-2.0-flash",
            TaskType.DOCUMENTATION: "gemini-1.5-flash",
            TaskType.OPTIMIZATION: "gemini-1.5-pro",
        }
        return model_mapping.get(task_type, "gemini-1.5-flash")

    def _extract_gemini_content(self, response_data: Dict[str, Any]) -> str:
        """Extrai conteúdo da resposta do Gemini"""
        try:
            candidates = response_data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        except Exception as e:
            logger.error("Failed to extract Gemini content", error=str(e))

        return "Erro ao extrair conteúdo da resposta"

    def _estimate_tokens(self, input_text: str, output_text: str) -> int:
        """Estima tokens usados (aproximação simples)"""
        # Aproximação: ~4 caracteres por token
        input_tokens = len(input_text) // 4
        output_tokens = len(output_text) // 4
        return input_tokens + output_tokens

    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Calcula custo estimado baseado no modelo"""
        costs = {
            "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
        }

        model_costs = costs.get(model, costs["gemini-1.5-flash"])
        # Assume 50% input, 50% output como aproximação
        input_cost = (tokens // 2) * model_costs["input"] / 1000
        output_cost = (tokens // 2) * model_costs["output"] / 1000

        return input_cost + output_cost


class CopilotProvider(ExternalAIProvider):
    """GitHub Copilot integration"""

    async def initialize(self) -> None:
        """Inicializa conexão com GitHub Copilot"""
        await self._ensure_session()

        # Suporte para OAuth ou Personal Access Token
        auth_method = self.config.get("auth_method", "oauth")

        if auth_method == "oauth":
            # Implementar fluxo OAuth
            self.token = await self._get_oauth_token()
        else:
            # Usar PAT diretamente
            token_env_var = os.getenv(self.config.get("github_token_env", "GITHUB_TOKEN"))
            self.token = token_env_var if token_env_var else ""

        if not self.token:
            raise ValueError("GitHub token não configurada")

        self.base_url = self.config.get("api_base_url", "https://api.github.com")
        logger.info("Copilot provider initialized")

    async def execute_task(self, task: TaskSpec) -> TaskResult:
        """Executa tarefa via GitHub Copilot Chat API"""
        start_time = time.time()

        try:
            # Verifica rate limits
            if not await self._check_rate_limit():
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error_message="Rate limit exceeded",
                    execution_time_seconds=time.time() - start_time,
                    provider_used="copilot",
                )

            # Prepara payload para Copilot Chat
            payload = self._prepare_copilot_payload(task)

            # Faz requisição para Copilot Chat API
            session = await self._ensure_session()
            url = f"{self.base_url}/copilot/chat/completions"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error_message=f"Copilot API error: {error_text}",
                        execution_time_seconds=time.time() - start_time,
                        provider_used="copilot",
                    )

                result_data = await response.json()
                content = self._extract_copilot_content(result_data)

                # Atualiza rate limiter
                tokens_used = self._estimate_tokens(task.prompt, content)
                self._update_rate_limit(tokens_used)

                return TaskResult(
                    task_id=task.task_id,
                    success=True,
                    content=content,
                    tokens_used=tokens_used,
                    cost_estimate=0.0,  # Gratuito para usuários GitHub
                    execution_time_seconds=time.time() - start_time,
                    provider_used="copilot",
                )

        except Exception as e:
            logger.error("Copilot task execution failed", error=str(e), task_id=task.task_id)
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time_seconds=time.time() - start_time,
                provider_used="copilot",
            )

    def get_capabilities(self) -> ProviderCapabilities:
        """Retorna capacidades do Copilot"""
        return ProviderCapabilities(
            supported_task_types=[
                TaskType.CODE_GENERATION,
                TaskType.CODE_REVIEW,
                TaskType.DEBUGGING,
                TaskType.OPTIMIZATION,
            ],
            capabilities=[
                ProviderCapability.CODE_GENERATION,
                ProviderCapability.CODE_REVIEW,
                ProviderCapability.DEBUGGING,
            ],
            max_context_length=8192,
            max_output_tokens=4096,
            supports_streaming=False,
            supports_multimodal=False,
        )

    async def check_rate_limits(self) -> Dict[str, Any]:
        """Verifica limites de uso do Copilot"""
        return {
            "requests_remaining": self.rate_limiter["requests_per_minute"]
            - self.rate_limiter["request_count"],
            "reset_in_seconds": 60 - (time.time() - self.rate_limiter["last_request_time"]),
        }

    async def _get_oauth_token(self) -> str:
        """Obtém token de acesso para o GitHub Copilot."""
        # 1. Tentar via Env Var
        token = os.getenv(self.config.get("github_token_env", "GITHUB_TOKEN"))

        # 2. Tentar via Arquivo Local (Local-First Pattern)
        if not token:
            token_file = Path.home() / ".github_token"
            if token_file.exists():
                token = token_file.read_text().strip()
                logger.debug("GitHub token carregado de ~/.github_token")

        if not token:
            raise ValueError(
                "GitHub Token não encontrado (Env: GITHUB_TOKEN ou File: ~/.github_token). "
                "O Real exige autenticação para o Copilot."
            )
        return token

    def _prepare_copilot_payload(self, task: TaskSpec) -> Dict[str, Any]:
        """Prepara payload para Copilot Chat API"""
        messages = [{"role": "user", "content": task.prompt}]

        # Adiciona contexto de arquivos se houver
        if task.files:
            context = "\n\n".join([f"File: {f['name']}\n{f['content']}" for f in task.files])
            messages.insert(0, {"role": "system", "content": f"Context:\n{context}"})

        return {
            "messages": messages,
            "model": "copilot-chat",
            "temperature": 0.7,
            "max_tokens": 2048,
        }

    def _extract_copilot_content(self, response_data: Dict[str, Any]) -> str:
        """Extrai conteúdo da resposta do Copilot"""
        try:
            choices = response_data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error("Failed to extract Copilot content", error=str(e))

        return "Erro ao extrair conteúdo da resposta"

    def _estimate_tokens(self, input_text: str, output_text: str) -> int:
        """Estima tokens usados"""
        # Aproximação: ~4 caracteres por token
        input_tokens = len(input_text) // 4
        output_tokens = len(output_text) // 4
        return input_tokens + output_tokens


class OpenRouterProvider(ExternalAIProvider):
    """OpenRouter multi-model integration"""

    async def initialize(self) -> None:
        """Inicializa conexão com OpenRouter"""
        await self._ensure_session()

        api_key_env = self.config.get("api_key_env")
        if not api_key_env:
            raise ValueError("api_key_env não configurada")

        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError(f"{api_key_env} não configurada")

        self.base_url = self.config.get("api_base_url", "https://openrouter.ai/api/v1")

        logger.info("OpenRouter provider initialized")

    async def execute_task(self, task: TaskSpec) -> TaskResult:
        """Executa tarefa via OpenRouter API"""
        start_time = time.time()

        try:
            # Verifica rate limits
            if not await self._check_rate_limit():
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error_message="Rate limit exceeded",
                    execution_time_seconds=time.time() - start_time,
                    provider_used="openrouter",
                )

            # Seleciona modelo baseado na tarefa
            model = self._select_model(task.task_type)

            # Prepara payload
            payload = self._prepare_openrouter_payload(task, model)

            # Faz requisição
            session = await self._ensure_session()
            url = f"{self.base_url}/chat/completions"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error_message=f"OpenRouter API error: {error_text}",
                        execution_time_seconds=time.time() - start_time,
                        provider_used="openrouter",
                    )

                result_data = await response.json()
                content = self._extract_openrouter_content(result_data)

                # Atualiza rate limiter
                tokens_used = result_data.get("usage", {}).get("total_tokens", 1000)
                self._update_rate_limit(tokens_used)

                return TaskResult(
                    task_id=task.task_id,
                    success=True,
                    content=content,
                    tokens_used=tokens_used,
                    cost_estimate=self._calculate_cost(model, tokens_used),
                    execution_time_seconds=time.time() - start_time,
                    provider_used="openrouter",
                )

        except Exception as e:
            logger.error("OpenRouter task execution failed", error=str(e), task_id=task.task_id)
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time_seconds=time.time() - start_time,
                provider_used="openrouter",
            )

    def get_capabilities(self) -> ProviderCapabilities:
        """Retorna capacidades do OpenRouter"""
        return ProviderCapabilities(
            supported_task_types=[
                TaskType.CODE_GENERATION,
                TaskType.CODE_REVIEW,
                TaskType.ANALYSIS,
                TaskType.DOCUMENTATION,
                TaskType.OPTIMIZATION,
                TaskType.DEBUGGING,
            ],
            capabilities=[
                ProviderCapability.TEXT_GENERATION,
                ProviderCapability.CODE_GENERATION,
                ProviderCapability.ANALYSIS,
                ProviderCapability.DEBUGGING,
            ],
            max_context_length=128000,  # Varia por modelo
            max_output_tokens=4096,
            supports_streaming=True,
            supports_multimodal=False,
        )

    async def check_rate_limits(self) -> Dict[str, Any]:
        """Verifica limites de uso do OpenRouter"""
        return {
            "requests_remaining": self.rate_limiter["requests_per_minute"]
            - self.rate_limiter["request_count"],
            "credits_remaining": self.config.get("rate_limits", {}).get("credits_per_month", 500),
            "reset_in_seconds": 60 - (time.time() - self.rate_limiter["last_request_time"]),
        }

    def _select_model(self, task_type: TaskType) -> str:
        """Seleciona modelo OpenRouter baseado no tipo de tarefa"""
        model_mapping = {
            TaskType.CODE_GENERATION: "qwen/qwen2-72b-instruct",
            TaskType.CODE_REVIEW: "qwen/qwen2-72b-instruct",
            TaskType.ANALYSIS: "qwen/qwen2-72b-instruct",
            TaskType.DOCUMENTATION: "qwen/qwen2-72b-instruct",
            TaskType.OPTIMIZATION: "qwen/qwen2-72b-instruct",
            TaskType.DEBUGGING: "qwen/qwen2-72b-instruct",
        }
        return model_mapping.get(task_type, "qwen/qwen2-72b-instruct")

    def _prepare_openrouter_payload(self, task: TaskSpec, model: str) -> Dict[str, Any]:
        """Prepara payload para OpenRouter API"""
        messages = [{"role": "user", "content": task.prompt}]

        # Adiciona contexto de arquivos se houver
        if task.files:
            context = "\n\n".join([f"File: {f['name']}\n{f['content']}" for f in task.files])
            messages.insert(0, {"role": "system", "content": f"Context:\n{context}"})

        return {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

    def _extract_openrouter_content(self, response_data: Dict[str, Any]) -> str:
        """Extrai conteúdo da resposta do OpenRouter"""
        try:
            choices = response_data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error("Failed to extract OpenRouter content", error=str(e))

        return "Erro ao extrair conteúdo da resposta"

    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Calcula custo estimado baseado no modelo"""
        # Custos aproximados do OpenRouter
        costs = {
            "qwen/qwen2-72b-instruct": {"input": 0.0001, "output": 0.0001},
            "anthropic/claude-3-opus": {"input": 0.015, "output": 0.075},
            "qwen/qwen3-max": {"input": 0.002, "output": 0.006},
            "google/gemini-pro": {"input": 0.000125, "output": 0.000375},
        }

        model_costs = costs.get(model, costs["qwen/qwen2-72b-instruct"])
        # Assume 50% input, 50% output como aproximação
        input_cost = (tokens // 2) * model_costs["input"] / 1000
        output_cost = (tokens // 2) * model_costs["output"] / 1000

        return input_cost + output_cost
