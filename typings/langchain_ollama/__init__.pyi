"""Type stubs for langchain_ollama."""

from typing import Any, Optional, Dict, List

class OllamaLLM:
    """Ollama language model."""

    model: str
    temperature: float

    def __init__(self, model: str, temperature: float = 0.7, **kwargs: Any) -> None: ...
    def __call__(self, prompt: str) -> str: ...
    def invoke(self, prompt: str) -> str: ...

__all__ = ["OllamaLLM"]
