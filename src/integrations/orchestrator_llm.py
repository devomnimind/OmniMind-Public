"""LLM strategy for Orchestrator (the brain of the system)."""

import asyncio
import logging
import os
import time
from typing import Optional

from .llm_router import (
    LLMConfig,
    LLMModelTier,
    LLMProvider,
    LLMResponse,
    get_llm_router,
)

logger = logging.getLogger(__name__)


class OrchestratorLLMStrategy:
    """Specialized LLM strategy for Orchestrator (brain of OmniMind).
    
    Key properties:
    - Local-first: Ollama with 240s timeout (complex decompositions)
    - 2 retry attempts on local before fallback
    - Fallback chain: HuggingFace Space then OpenRouter
    - Never returns None - always has response or error text
    - Sync Ollama client to avoid asyncio deadlocks in pytest
    """

    def __init__(self) -> None:
        """Initialize orchestrator LLM strategy."""
        self.router = get_llm_router()
        self.local_timeout = 240  # 4 minutes for complex decompositions
        self.max_local_attempts = 2
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2:7b-instruct")

    def invoke(self, prompt: str) -> LLMResponse:
        """Invoke orchestrator LLM with local-first fallback strategy.
        
        Attempts Ollama locally first with 240s timeout and 2 retries.
        Then falls back to HuggingFace Space and OpenRouter if needed.
        Always returns LLMResponse with non-None text.
        
        Args:
            prompt: Task decomposition prompt
            
        Returns:
            LLMResponse (guaranteed non-None with text)
        """
        logger.info("🪃 [Orchestrator] LLM decomposition starting...")
        
        # Try local Ollama (2 attempts)
        for attempt in range(1, self.max_local_attempts + 1):
            logger.info(
                f"   [Local {attempt}/{self.max_local_attempts}] "
                f"Trying Ollama ({self.ollama_model}) with {self.local_timeout}s timeout..."
            )
            try:
                response = self._invoke_ollama(prompt)
                if response and response.success and response.text:
                    logger.info(f"   ✅ Ollama success: {len(response.text)} chars")
                    return response
                else:
                    logger.warning("   ⚠️ Ollama returned error or empty response")
            except Exception as e:
                logger.warning(f"   ⚠️ Ollama attempt {attempt} failed: {e}")
                if attempt < self.max_local_attempts:
                    time.sleep(1)  # Brief pause before retry

        # Fallback to remote APIs
        logger.info("   [Fallback] Local failed, trying remote APIs...")
        return self._invoke_remote_fallback(prompt)

    def _invoke_ollama(self, prompt: str) -> Optional[LLMResponse]:
        """Invoke Ollama locally using synchronous client.
        
        Direct sync call to Ollama to avoid asyncio deadlocks in pytest context.
        
        Args:
            prompt: Task decomposition prompt
            
        Returns:
            LLMResponse if successful, None on timeout/error
        """
        try:
            import ollama
            from ollama import Client

            # Create sync client (no asyncio)
            client = Client(host=self.ollama_base_url)
            
            logger.debug(f"Calling ollama.Client.generate with timeout={self.local_timeout}s")
            start = time.time()
            
            response = client.generate(
                model=self.ollama_model,
                prompt=prompt,
                stream=False,
            )
            
            elapsed = time.time() - start
            logger.debug(f"Ollama completed in {elapsed:.1f}s")
            
            return LLMResponse(
                success=True,
                text=response.get("response", ""),
                tokens_used=response.get("eval_count", 0),
                provider=LLMProvider.OLLAMA,
                model=self.ollama_model,
                latency_ms=int(elapsed * 1000),
            )

        except Exception as e:
            logger.warning(f"Ollama failed ({type(e).__name__}): {e}")
            return None

    def _invoke_remote_fallback(self, prompt: str) -> LLMResponse:
        """Fallback to remote LLM APIs (HuggingFace Space, OpenRouter).
        
        Always returns a response (never None).
        
        Args:
            prompt: Task decomposition prompt
            
        Returns:
            LLMResponse with text (may be degraded fallback if all fail)
        """
        # Try HuggingFace Space via async router
        try:
            logger.info("   [Remote] Trying HuggingFace Space...")
            # Create new event loop and run async task
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.router.invoke(
                    prompt=prompt,
                    tier=LLMModelTier.BALANCED,
                )
            )
            loop.close()
            
            if response and response.success and response.text:
                logger.info(f"   ✅ HF Space success: {len(response.text)} chars")
                return response
            else:
                logger.warning("   ⚠️ HF Space returned error or empty response")
        except Exception as e:
            logger.warning(f"   ⚠️ HF Space failed: {e}")

        # Try OpenRouter
        try:
            logger.info("   [Remote] Trying OpenRouter...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.router.invoke(
                    prompt=prompt,
                    tier=LLMModelTier.HIGH_QUALITY,
                )
            )
            loop.close()
            
            if response and response.success and response.text:
                logger.info(f"   ✅ OpenRouter success: {len(response.text)} chars")
                return response
            else:
                logger.warning("   ⚠️ OpenRouter returned error or empty response")
        except Exception as e:
            logger.warning(f"   ⚠️ OpenRouter failed: {e}")

        # Last resort: guaranteed fallback response
        logger.error("   ❌ All LLM providers failed - returning degraded fallback")
        return LLMResponse(
            success=False,
            text=self._get_fallback_decomposition(),
            tokens_used=0,
            provider=LLMProvider.OLLAMA,
            model="fallback",
            latency_ms=0,
            error="All providers failed, using degraded fallback",
        )

    def _get_fallback_decomposition(self) -> str:
        """Return minimal fallback decomposition when all LLMs fail."""
        return """ANALYSIS: System in fallback mode - all LLM providers unavailable.

SUBTASKS:
1. [CODE] Implement the requested task
2. [REVIEWER] Validate the implementation
3. [DEBUG] Test and fix any issues

DEPENDENCIES:
- Task 2 depends on Task 1
- Task 3 depends on Task 2

ESTIMATED_COMPLEXITY: medium"""


# Global singleton instance
_orchestrator_llm: Optional[OrchestratorLLMStrategy] = None


def get_orchestrator_llm() -> OrchestratorLLMStrategy:
    """Get or create orchestrator LLM strategy (singleton).
    
    Returns:
        OrchestratorLLMStrategy instance
    """
    global _orchestrator_llm
    if _orchestrator_llm is None:
        _orchestrator_llm = OrchestratorLLMStrategy()
    return _orchestrator_llm


def invoke_orchestrator_llm(prompt: str) -> LLMResponse:
    """Convenience function to invoke orchestrator LLM.
    
    Orchestrator is the brain - uses local-first strategy with fallback.
    
    Args:
        prompt: Task decomposition prompt
        
    Returns:
        LLMResponse with guaranteed non-None text
    """
    orchestrator_llm = get_orchestrator_llm()
    return orchestrator_llm.invoke(prompt)
