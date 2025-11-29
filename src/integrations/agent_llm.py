"""
Agent LLM Strategy - Remote-Only with Security Filters

Agents usam apenas APIs remotas (HuggingFace, OpenRouter) com filtros de segurança.
Ao contrário do Orchestrator que é local-first, Agents são sempre remotos para:
1. Distribuir carga
2. Garantir isolamento (security sandbox)
3. Falhar graciosamente sem bloquear orquestrador

Estratégia:
- PRIMARY: OpenRouter (HIGH_QUALITY para tarefas críticas)
- FALLBACK: HuggingFace Space (BALANCED para tarefas normais)
- SECURITY: Filtros para bloquear system context, environment vars, etc.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

import aiohttp

logger = logging.getLogger(__name__)


class AgentTier(Enum):
    """Tiers de qualidade para agents."""

    BALANCED = "balanced"  # HuggingFace Space
    HIGH_QUALITY = "high_quality"  # OpenRouter


@dataclass
class AgentLLMResponse:
    """Resposta de LLM para agents."""

    success: bool
    text: str
    provider: str  # "openrouter", "huggingface"
    model: str
    latency_ms: float
    tokens_used: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converter para dict para serialização."""
        return {
            "success": self.success,
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "error": self.error,
        }


class SecurityFilter:
    """Filtros de segurança para agents."""

    # Padrões proibidos (regex-like strings)
    FORBIDDEN_PATTERNS = [
        "os.environ",
        "os.system",
        "subprocess",
        "exec(",
        "eval(",
        "__import__",
        "open(",
        "import os",
        "import sys",
        "getenv",
        "pwd",
        "whoami",
        "/etc/",
        "/root/",
        "SECRET_",
        "API_KEY",
        "PASSWORD",
    ]

    @staticmethod
    def validate_prompt(prompt: str) -> tuple[bool, Optional[str]]:
        """
        Validar prompt contra padrões proibidos.

        Args:
            prompt: String do prompt

        Returns:
            (is_valid, error_message)
        """
        for pattern in SecurityFilter.FORBIDDEN_PATTERNS:
            if pattern.lower() in prompt.lower():
                error = f"Forbidden pattern detected: {pattern}"
                logger.warning(f"Security filter blocked: {error} in prompt")
                return False, error

        return True, None

    @staticmethod
    def sanitize_response(response: str) -> str:
        """
        Sanitizar resposta para remover dados sensíveis.

        Args:
            response: Resposta bruta do LLM

        Returns:
            Resposta sanitizada
        """
        sanitized = response

        # Remover paths suspeitos
        for path in ["/root/", "/home/", "/etc/"]:
            sanitized = sanitized.replace(path, "[PATH]")

        # Remover env vars
        lines = sanitized.split("\n")
        filtered_lines = []
        for line in lines:
            if any(
                forbidden in line.upper()
                for forbidden in ["SECRET", "API_KEY", "PASSWORD", "TOKEN"]
            ):
                filtered_lines.append("[REDACTED]")
            else:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)


class AgentLLMStrategy:
    """
    Estratégia de LLM para Agents.

    Remote-only com fallback chain:
    1. OpenRouter (HIGH_QUALITY - GPT-4 equivalent)
    2. HuggingFace Space (BALANCED - Free alternative)
    3. Fallback local (se disponível, mas não garantido)
    """

    def __init__(self):
        """Inicializar estratégia de agent LLM."""
        self.openrouter_url = "https://openrouter.io/api/v1/chat/completions"
        self.openrouter_key = self._get_env("OPENROUTER_API_KEY", None)

        self.hf_space_url = self._get_env(
            "HF_SPACE_URL", "https://fahbrain-omnimind-inference.hf.space/predict"
        )

        # aiohttp timeouts (need ClientTimeout object)
        self.timeout_openrouter = aiohttp.ClientTimeout(total=60)
        self.timeout_hf = aiohttp.ClientTimeout(total=45)
        self.max_retries = 2

        logger.info(
            f"AgentLLMStrategy initialized: "
            f"OpenRouter={self.openrouter_key is not None}, HF={self.hf_space_url}"
        )

    def _get_env(self, key: str, default: Any = None) -> Any:
        """Get environment variable safely."""
        import os

        return os.getenv(key, default)

    async def invoke(
        self, prompt: str, tier: AgentTier = AgentTier.BALANCED, agent_name: str = "agent"
    ) -> AgentLLMResponse:
        """
        Invocar LLM para agent de forma segura.

        Args:
            prompt: Prompt para o LLM
            tier: Tier de qualidade (BALANCED ou HIGH_QUALITY)
            agent_name: Nome do agent (para logging)

        Returns:
            AgentLLMResponse
        """
        # Validar prompt contra patterns suspeitos
        is_valid, error_msg = SecurityFilter.validate_prompt(prompt)
        if not is_valid:
            return AgentLLMResponse(
                success=False,
                text="",
                provider="security_filter",
                model="N/A",
                latency_ms=0.0,
                error=error_msg,
            )

        logger.info(f"Agent {agent_name} invoking LLM: tier={tier.value}")

        # Strategy: PRIMARY OpenRouter, FALLBACK HuggingFace
        if tier == AgentTier.HIGH_QUALITY and self.openrouter_key:
            response = await self._invoke_openrouter(prompt, agent_name)
            if response.success:
                return response
            logger.warning(f"OpenRouter failed: {response.error}, falling back to HF")

        # Try HuggingFace
        response = await self._invoke_huggingface(prompt, agent_name)
        if response.success:
            return response

        # Fallback degradado (síntese simples)
        logger.warning(f"All LLM providers failed for {agent_name}, returning degraded response")
        return AgentLLMResponse(
            success=False,
            text="Agent encountered all LLM providers being unavailable. Please retry.",
            provider="fallback_degraded",
            model="N/A",
            latency_ms=0.0,
            error="All providers exhausted",
        )

    async def _invoke_openrouter(self, prompt: str, agent_name: str) -> AgentLLMResponse:
        """
        Invocar OpenRouter com HIGH_QUALITY models.

        Args:
            prompt: Prompt
            agent_name: Agent name

        Returns:
            AgentLLMResponse
        """
        if not self.openrouter_key:
            return AgentLLMResponse(
                success=False,
                text="",
                provider="openrouter",
                model="N/A",
                latency_ms=0.0,
                error="OpenRouter API key not configured",
            )

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://omnimind.ai",
                    "X-Title": "OmniMind",
                }

                payload = {
                    "model": "openai/gpt-4-turbo-preview",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                }

                async with session.post(
                    self.openrouter_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout_openrouter,
                ) as resp:
                    latency_ms = (time.time() - start_time) * 1000

                    if resp.status == 200:
                        data = await resp.json()
                        text = data["choices"][0]["message"]["content"]

                        # Sanitizar resposta
                        text = SecurityFilter.sanitize_response(text)

                        return AgentLLMResponse(
                            success=True,
                            text=text,
                            provider="openrouter",
                            model="gpt-4-turbo-preview",
                            latency_ms=latency_ms,
                            tokens_used=data.get("usage", {}).get("total_tokens"),
                        )
                    else:
                        error = f"HTTP {resp.status}"
                        return AgentLLMResponse(
                            success=False,
                            text="",
                            provider="openrouter",
                            model="gpt-4-turbo-preview",
                            latency_ms=latency_ms,
                            error=error,
                        )

        except asyncio.TimeoutError:
            latency_ms = (time.time() - start_time) * 1000
            return AgentLLMResponse(
                success=False,
                text="",
                provider="openrouter",
                model="gpt-4-turbo-preview",
                latency_ms=latency_ms,
                error="Timeout (60s exceeded)",
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"OpenRouter error: {e}")
            return AgentLLMResponse(
                success=False,
                text="",
                provider="openrouter",
                model="gpt-4-turbo-preview",
                latency_ms=latency_ms,
                error=str(e),
            )

    async def _invoke_huggingface(self, prompt: str, agent_name: str) -> AgentLLMResponse:
        """
        Invocar HuggingFace Space com fallback.

        Args:
            prompt: Prompt
            agent_name: Agent name

        Returns:
            AgentLLMResponse
        """
        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"data": [prompt]}

                async with session.post(
                    self.hf_space_url, json=payload, timeout=self.timeout_hf
                ) as resp:
                    latency_ms = (time.time() - start_time) * 1000

                    if resp.status == 200:
                        data = await resp.json()
                        text = data.get("data", [prompt])[0]

                        # Sanitizar resposta
                        text = SecurityFilter.sanitize_response(text)

                        return AgentLLMResponse(
                            success=True,
                            text=text,
                            provider="huggingface",
                            model="qwen2:7b-instruct",
                            latency_ms=latency_ms,
                        )
                    else:
                        error = f"HTTP {resp.status}"
                        return AgentLLMResponse(
                            success=False,
                            text="",
                            provider="huggingface",
                            model="qwen2:7b-instruct",
                            latency_ms=latency_ms,
                            error=error,
                        )

        except asyncio.TimeoutError:
            latency_ms = (time.time() - start_time) * 1000
            return AgentLLMResponse(
                success=False,
                text="",
                provider="huggingface",
                model="qwen2:7b-instruct",
                latency_ms=latency_ms,
                error="Timeout (45s exceeded)",
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"HuggingFace error: {e}")
            return AgentLLMResponse(
                success=False,
                text="",
                provider="huggingface",
                model="qwen2:7b-instruct",
                latency_ms=latency_ms,
                error=str(e),
            )


# Factory function
_agent_llm_strategy_instance: Optional[AgentLLMStrategy] = None


def get_agent_llm_strategy() -> AgentLLMStrategy:
    """Get singleton instance of AgentLLMStrategy."""
    global _agent_llm_strategy_instance
    if _agent_llm_strategy_instance is None:
        _agent_llm_strategy_instance = AgentLLMStrategy()
    return _agent_llm_strategy_instance


async def invoke_agent_llm(
    prompt: str, tier: AgentTier = AgentTier.BALANCED, agent_name: str = "agent"
) -> AgentLLMResponse:
    """
    Invocar LLM para um agent com strategy padrão.

    Args:
        prompt: Prompt
        tier: BALANCED (HF Space) ou HIGH_QUALITY (OpenRouter)
        agent_name: Nome do agent

    Returns:
        AgentLLMResponse com resultado
    """
    strategy = get_agent_llm_strategy()
    return await strategy.invoke(prompt, tier, agent_name)
