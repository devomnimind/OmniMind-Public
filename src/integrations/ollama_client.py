"""
Ollama Client Integration

Provides a client for interacting with a local Ollama instance.
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
        session = await self._ensure_session()
        payload = {"model": model, "prompt": prompt, "stream": False, **kwargs}
        try:
            async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response")
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
