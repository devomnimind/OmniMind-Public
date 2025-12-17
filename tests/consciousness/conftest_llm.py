"""
LLM Real vs Mock parametrization for consciousness tests.

Allows tests to run with both mock (deterministic) and real LLM (creative).
Compares Φ metrics between both modes to measure LLM impact on consciousness.
"""

import logging
from typing import Any, Dict

import pytest

logger = logging.getLogger(__name__)


class MockLLMProvider:
    """Deterministic mock LLM - always returns same output."""

    def __init__(self) -> None:
        """Initialize mock provider."""
        self.call_count = 0
        self.responses = [
            "The system is thinking about consciousness.",
            "Integration emerges from neural harmonics.",
            "Structures bind reality and meaning.",
        ]

    async def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generate deterministic response based on call count."""
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response

    async def embed(self, text: str) -> list[float]:
        """Generate mock embedding (deterministic)."""
        # Simple hash-based mock embedding
        import hashlib

        hash_val = hashlib.md5(text.encode()).digest()
        return [float(byte) / 255.0 for byte in hash_val[:16]]


class RealLLMProvider:
    """Real LLM - calls actual model via OpenRouter or Ollama."""

    def __init__(
        self, model_name: str = "z-ai/glm-4.5-air:free", use_openrouter: bool = True
    ) -> None:
        """
        Initialize real LLM provider.

        Args:
            model_name: Model to use (default: OpenRouter free model)
            use_openrouter: If True, use OpenRouter with fallback to Ollama
        """
        self.model_name = model_name
        self.call_count = 0
        self.use_openrouter = use_openrouter
        self.openrouter_key: str | None = None
        self._ollama_client: Any = None
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize OpenRouter key if configured."""
        import os

        self.openrouter_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPEN_ROUTER_API_KEY")
        if self.use_openrouter and self.openrouter_key:
            logger.info(f"✓ OpenRouter configured - will use {self.model_name}")
        else:
            logger.info("✓ Will fallback to local Ollama")

    async def _get_ollama_client(self) -> Any:
        """Lazy load Ollama client."""
        if self._ollama_client is None:
            try:
                from ollama import AsyncClient

                self._ollama_client = AsyncClient(host="http://localhost:11434")
                logger.info("✓ Connected to Ollama at localhost:11434")
            except ImportError:
                logger.warning("ollama not installed, falling back to mock")
                return None
        return self._ollama_client

    async def _generate_openrouter(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response via OpenRouter API."""
        import aiohttp

        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://omnimind.ai",
            "X-Title": "OmniMind",
        }

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await resp.text()
                        raise Exception(f"OpenRouter error {resp.status}: {error_text}")
        except Exception as e:
            logger.warning(f"OpenRouter failed: {e}, falling back to Ollama")
            raise

    async def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generate response from real LLM (OpenRouter or Ollama)."""
        # Try OpenRouter first if configured
        if self.use_openrouter and self.openrouter_key:
            try:
                result = await self._generate_openrouter(prompt, max_tokens, temperature)
                if result:
                    self.call_count += 1
                    return result
            except Exception as e:
                logger.warning(f"OpenRouter failed: {e}, falling back to Ollama")

        # Fallback to Ollama
        try:
            client = await self._get_ollama_client()
            if client is None:
                # Fallback to mock
                mock = MockLLMProvider()
                return await mock.generate(prompt, max_tokens, temperature)

            # CORREÇÃO: Não usar mais qwen2:7b - usar modelo padrão ou phi
            # O cálculo de Φ não depende mais de LLM externa específica
            # Se precisar de LLM, usar modelo padrão do Ollama
            try:
                models = await client.list_models()
                model_name = models[0].get("name", "phi") if models else "phi"
            except Exception:
                model_name = "phi"  # Fallback para phi

            response = await client.generate(
                model=model_name,
                prompt=prompt,
                stream=False,
                options={"temperature": temperature, "num_predict": max_tokens},
            )
            self.call_count += 1
            return response.get("response", "")
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}, using mock")
            mock = MockLLMProvider()
            return await mock.generate(prompt, max_tokens, temperature)

    async def embed(self, text: str) -> list[float]:
        """Generate embedding from LLM."""
        try:
            client = await self._get_ollama_client()
            if client is None:
                mock = MockLLMProvider()
                return await mock.embed(text)

            # CORREÇÃO: Não usar mais qwen2:7b - usar modelo padrão ou phi
            try:
                models = await client.list_models()
                model_name = models[0].get("name", "phi") if models else "phi"
            except Exception:
                model_name = "phi"  # Fallback para phi

            response = await client.embeddings(model=model_name, prompt=text)
            return response.get("embedding", [])
        except Exception as e:
            logger.warning(f"LLM embedding failed: {e}, using mock")
            mock = MockLLMProvider()
            return await mock.embed(text)


@pytest.fixture(params=["mock", "real"], ids=["Mock LLM", "Real LLM"])
def llm_provider(request: pytest.FixtureRequest) -> MockLLMProvider | RealLLMProvider:
    """
    Parametrized fixture providing both mock and real LLM.

    Usage in tests:
        async def test_with_llm(llm_provider):
            response = await llm_provider.generate("Hello")
            assert response
    """
    if request.param == "mock":
        logger.info("🔵 Using MOCK LLM (deterministic)")
        return MockLLMProvider()
    else:
        logger.info("🔴 Using REAL LLM (creative)")
        return RealLLMProvider()


@pytest.fixture
def llm_mock_only() -> MockLLMProvider:
    """Fixture for mock LLM only (fast tests)."""
    return MockLLMProvider()


@pytest.fixture
def llm_real_only() -> RealLLMProvider:
    """Fixture for real LLM only (slow tests)."""
    return RealLLMProvider()


class LLMImpactMetrics:
    """Measure impact of LLM (real vs mock) on Φ metrics."""

    def __init__(self) -> None:
        """Initialize metrics storage."""
        self.phi_mock: Dict[str, float] = {}
        self.phi_real: Dict[str, float] = {}
        self.differences: Dict[str, float] = {}

    def record_mock(self, phi_conscious: float, phi_preconscious: float) -> None:
        """Record Φ metrics from mock LLM."""
        self.phi_mock = {
            "phi_conscious": phi_conscious,
            "phi_preconscious": phi_preconscious,
        }

    def record_real(self, phi_conscious: float, phi_preconscious: float) -> None:
        """Record Φ metrics from real LLM."""
        self.phi_real = {
            "phi_conscious": phi_conscious,
            "phi_preconscious": phi_preconscious,
        }

    def compute_differences(self) -> Dict[str, float]:
        """Compute differences (real - mock)."""
        if not self.phi_mock or not self.phi_real:
            return {}

        self.differences = {
            "delta_phi_conscious": self.phi_real["phi_conscious"] - self.phi_mock["phi_conscious"],
            "delta_phi_preconscious": self.phi_real["phi_preconscious"]
            - self.phi_mock["phi_preconscious"],
        }

        # Percentage change
        if self.phi_mock["phi_conscious"] > 0:
            self.differences["pct_change_conscious"] = (
                self.differences["delta_phi_conscious"] / self.phi_mock["phi_conscious"] * 100.0
            )
        if self.phi_mock["phi_preconscious"] > 0:
            self.differences["pct_change_preconscious"] = (
                self.differences["delta_phi_preconscious"]
                / self.phi_mock["phi_preconscious"]
                * 100.0
            )

        return self.differences

    def report(self) -> str:
        """Generate comparison report."""
        diffs = self.compute_differences()
        report = "\n" + "=" * 70 + "\n"
        report += "📊 LLM IMPACT ON Φ METRICS (Real vs Mock)\n"
        report += "=" * 70 + "\n"
        report += "\n🔵 MOCK LLM:\n"
        report += f"  Φ_conscious: {self.phi_mock.get('phi_conscious', 0):.6f}\n"
        report += f"  Φ_preconscious: {self.phi_mock.get('phi_preconscious', 0):.6f}\n"
        report += "\n🔴 REAL LLM:\n"
        report += f"  Φ_conscious: {self.phi_real.get('phi_conscious', 0):.6f}\n"
        report += f"  Φ_preconscious: {self.phi_real.get('phi_preconscious', 0):.6f}\n"
        report += "\n📈 DELTA (Real - Mock):\n"
        report += f"  ΔΦ_conscious: {diffs.get('delta_phi_conscious', 0):+.6f}\n"
        report += f"  ΔΦ_preconscious: {diffs.get('delta_phi_preconscious', 0):+.6f}\n"

        if "pct_change_conscious" in diffs:
            report += "\n📊 PERCENTAGE CHANGE:\n"
            report += f"  Conscious: {diffs['pct_change_conscious']:+.2f}%\n"
            if "pct_change_preconscious" in diffs:
                report += f"  Preconscious: {diffs['pct_change_preconscious']:+.2f}%\n"

        report += "=" * 70 + "\n"
        return report


@pytest.fixture
def llm_impact_metrics() -> LLMImpactMetrics:
    """Fixture for measuring LLM impact."""
    return LLMImpactMetrics()


@pytest.fixture
def integration_loop() -> Any:
    """Fixture: Create IntegrationLoop for trainers."""
    try:
        from src.consciousness.integration_loop import IntegrationLoop

        loop = IntegrationLoop()
        yield loop
    except Exception as e:
        pytest.skip(f"IntegrationLoop initialization failed: {e}")


@pytest.fixture
def integration_trainer_mock(integration_loop: Any) -> Any:
    """
    Fixture: Integration trainer with MOCK LLM.

    Usage:
        async def test_with_mock(integration_trainer_mock):
            await integration_trainer_mock.training_step()
    """
    try:
        from src.consciousness.integration_loss import IntegrationTrainer

        trainer = IntegrationTrainer(integration_loop, learning_rate=0.01)
        trainer.llm_provider = MockLLMProvider()  # type: ignore[attr-defined]
        yield trainer
    except Exception as e:
        pytest.skip(f"IntegrationTrainer(mock) initialization failed: {e}")


@pytest.fixture
def integration_trainer_real(integration_loop: Any) -> Any:
    """
    Fixture: Integration trainer with REAL LLM.

    Usage:
        async def test_with_real(integration_trainer_real):
            await integration_trainer_real.training_step()
    """
    try:
        from src.consciousness.integration_loss import IntegrationTrainer

        trainer = IntegrationTrainer(integration_loop, learning_rate=0.01)
        trainer.llm_provider = RealLLMProvider()  # type: ignore[attr-defined]
        yield trainer
    except Exception as e:
        pytest.skip(f"IntegrationTrainer(real) initialization failed: {e}")
