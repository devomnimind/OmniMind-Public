"""
Tests for Agent LLM Strategy

Testa:
- Security filters
- Fallback chain
- Response sanitization
- Error handling
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.integrations.agent_llm import (
    AgentLLMResponse,
    AgentLLMStrategy,
    AgentTier,
    SecurityFilter,
    invoke_agent_llm,
)


class TestSecurityFilter:
    """Test security filtering for agents."""

    def test_valid_prompt_passes(self):
        """Test that normal prompts pass validation."""
        prompt = "Implement a REST API endpoint for user authentication"
        is_valid, error = SecurityFilter.validate_prompt(prompt)
        assert is_valid is True
        assert error is None

    def test_forbidden_os_environ(self):
        """Test that os.environ patterns are blocked."""
        prompt = "Get current user with: os.environ['USER']"
        is_valid, error = SecurityFilter.validate_prompt(prompt)
        assert is_valid is False
        assert error is not None and "os.environ" in error

    def test_forbidden_subprocess(self):
        """Test that subprocess patterns are blocked."""
        prompt = "Run command: subprocess.run(['ls', '-la'])"
        is_valid, error = SecurityFilter.validate_prompt(prompt)
        assert is_valid is False
        assert error is not None and "subprocess" in error

    def test_forbidden_secret_key(self):
        """Test that SECRET patterns are blocked."""
        prompt = "Use SECRET_API_KEY from environment"
        is_valid, error = SecurityFilter.validate_prompt(prompt)
        assert is_valid is False
        assert error is not None and "SECRET" in error

    def test_sanitize_response_removes_paths(self):
        """Test that paths are redacted."""
        response = "File location: /root/config.json and /etc/passwd"
        sanitized = SecurityFilter.sanitize_response(response)
        assert "/root/" not in sanitized
        assert "/etc/" not in sanitized
        assert "[PATH]" in sanitized

    def test_sanitize_response_redacts_secrets(self):
        """Test that secret lines are redacted."""
        response = "API_KEY=sk-12345\nNormal line\nPASSWORD=secret123"
        sanitized = SecurityFilter.sanitize_response(response)
        assert "API_KEY" not in sanitized
        assert "PASSWORD" not in sanitized
        assert "[REDACTED]" in sanitized
        assert "Normal line" in sanitized


class TestAgentLLMResponse:
    """Test AgentLLMResponse dataclass."""

    def test_success_response(self):
        """Test successful response."""
        response = AgentLLMResponse(
            success=True,
            text="Implemented endpoint",
            provider="openrouter",
            model="gpt-4-turbo-preview",
            latency_ms=1250.5,
            tokens_used=512,
        )
        assert response.success is True
        assert response.text == "Implemented endpoint"
        assert response.latency_ms > 0

    def test_error_response(self):
        """Test error response."""
        response = AgentLLMResponse(
            success=False,
            text="",
            provider="huggingface",
            model="qwen2:7b-instruct",
            latency_ms=45000.0,
            error="Timeout exceeded",
        )
        assert response.success is False
        assert response.error == "Timeout exceeded"

    def test_to_dict_serialization(self):
        """Test conversion to dict."""
        response = AgentLLMResponse(
            success=True,
            text="Result",
            provider="openrouter",
            model="gpt-4",
            latency_ms=1000.0,
            tokens_used=256,
        )
        data = response.to_dict()
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["provider"] == "openrouter"
        assert data["tokens_used"] == 256


class TestAgentLLMStrategy:
    """Test AgentLLMStrategy class."""

    def test_initialization(self):
        """Test strategy initialization."""
        strategy = AgentLLMStrategy()
        assert strategy.openrouter_url == "https://openrouter.io/api/v1/chat/completions"
        assert strategy.timeout_openrouter.total == 60
        assert strategy.timeout_hf.total == 45

    @pytest.mark.asyncio
    async def test_invoke_with_security_violation(self):
        """Test that security violations are caught."""
        strategy = AgentLLMStrategy()
        response = await strategy.invoke("Get system: os.environ['PATH']", agent_name="bad_agent")
        assert response.success is False
        assert response.provider == "security_filter"

    @pytest.mark.asyncio
    async def test_invoke_fallback_chain(self):
        """Test fallback from OpenRouter to HuggingFace."""
        strategy = AgentLLMStrategy()

        # Mock OpenRouter to fail, HF to succeed
        with (
            patch.object(strategy, "_invoke_openrouter") as mock_openrouter,
            patch.object(strategy, "_invoke_huggingface") as mock_hf,
        ):

            failed_response = AgentLLMResponse(
                success=False,
                text="",
                provider="openrouter",
                model="gpt-4",
                latency_ms=1000.0,
                error="Rate limited",
            )
            success_response = AgentLLMResponse(
                success=True,
                text="API implementation",
                provider="huggingface",
                model="qwen2",
                latency_ms=500.0,
            )

            mock_openrouter.return_value = failed_response
            mock_hf.return_value = success_response

            strategy.openrouter_key = "test-key"

            result = await strategy.invoke("Implement something", tier=AgentTier.HIGH_QUALITY)
            assert result.success is True
            assert result.provider == "huggingface"


class TestAgentLLMIntegration:
    """Integration tests for agent LLM."""

    @pytest.mark.asyncio
    async def test_invoke_agent_llm_function(self):
        """Test factory function."""
        # Mock the strategy
        with patch("src.integrations.agent_llm.get_agent_llm_strategy") as mock_get:
            mock_strategy = AsyncMock()
            mock_response = AgentLLMResponse(
                success=True,
                text="Result",
                provider="test",
                model="test-model",
                latency_ms=100.0,
            )
            mock_strategy.invoke.return_value = mock_response

            mock_get.return_value = mock_strategy

            result = await invoke_agent_llm("Test prompt", agent_name="test_agent")
            assert result.success is True
            assert result.text == "Result"

    @pytest.mark.asyncio
    async def test_agent_tier_selection(self):
        """Test that tier selection works."""
        strategy = AgentLLMStrategy()

        # BALANCED tier should use HuggingFace
        # HIGH_QUALITY should try OpenRouter first

        # Test BALANCED (should only try HF)
        with patch.object(strategy, "_invoke_huggingface") as mock_hf:
            response = AgentLLMResponse(
                success=True,
                text="Result",
                provider="huggingface",
                model="qwen2",
                latency_ms=400.0,
            )
            mock_hf.return_value = response

            result = await strategy.invoke("Prompt", tier=AgentTier.BALANCED)
            assert result.provider == "huggingface"
