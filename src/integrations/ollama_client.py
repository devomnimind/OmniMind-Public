"""
Ollama Client Integration

Provides a client for interacting with a local Ollama instance.
Uses OllamaProcessManager for on-demand lifecycle management.
"""

import logging
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None

        # On-demand process manager (spawns Ollama when needed)
        try:
            from src.integrations.ollama_process_manager import get_ollama_manager

            self.process_manager = get_ollama_manager()
            logger.info("🦙 [Ollama] ProcessManager attached (on-demand mode)")
        except ImportError:
            logger.warning("ProcessManager not found. Assuming Ollama runs externally.")
            self.process_manager = None

        # SOBERANO GOVERNANCE
        try:
            from src.social.governance.npu_metrics import NpuMetrics

            self.governance = NpuMetrics()
            logger.info("🛡️ [SOVEREIGN]: NPU Governance Active (Phi/Entropy)")
        except ImportError:
            logger.warning("Governance module not found. Skipping NPU metrics.")
            self.governance = None
        except Exception as e:
            logger.warning(f"Governance init failed: {e}")
            self.governance = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure an active aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        session = await self._ensure_session()
        try:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                else:
                    logger.error(f"Failed to list models: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise

    async def generate(self, model: str, prompt: str, **kwargs) -> Optional[str]:
        """Generate text using a model."""
        # Ensure Ollama is running (on-demand spawn)
        if self.process_manager is not None:
            if not self.process_manager.ensure_running():
                logger.error("Failed to start Ollama process")
                return None

        session = await self._ensure_session()
        payload = {"model": model, "prompt": prompt, "stream": False, **kwargs}

        import time

        start_time = time.time()

        try:
            timeout = aiohttp.ClientTimeout(total=300)  # 300 second timeout for Deep Thought
            async with session.post(
                f"{self.base_url}/api/generate", json=payload, timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    text_response = data.get("response")

                    # GOVERNANCE AUDIT
                    if self.governance and text_response:
                        try:
                            latency = (time.time() - start_time) * 1000
                            report = self.governance.measure_impact(
                                generated_text=text_response,
                                prompt_context=prompt,
                                latency_ms=latency,
                                model_name=model,
                            )
                            # Log Critical Ontology Event
                            logger.info(report.synthesis_log)
                        except Exception as gov_err:
                            logger.warning(f"Governance Audit Failed: {gov_err}")

                    return text_response
                else:
                    logger.error(f"Failed to generate text: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return None

    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
