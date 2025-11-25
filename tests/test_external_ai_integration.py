"""
Testes para Integração de Provedores Externos de IA - OmniMind
Testa isolamento, delegação e execução segura de tarefas externas
"""

import asyncio
import pytest
import os
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

from src.integrations.external_ai_providers import (
    GeminiProvider,
    CopilotProvider,
    OpenRouterProvider,
    TaskSpec,
    TaskType,
    ProviderCapabilities,
)
from src.integrations.task_isolation import TaskIsolationEngine, IsolatedTask
from src.integrations.task_delegation import TaskDelegationManager, DelegationResult


class TestTaskIsolationEngine:
    """Testes para o engine de isolamento de tarefas"""

    def setup_method(self):
        """Configura testes"""
        self.isolation_engine = TaskIsolationEngine()

    def test_sanitize_text_removes_sensitive_data(self):
        """Testa remoção de dados sensíveis"""
        prompt_with_secrets = """
        Conecte ao banco com password=secret123 e token=sk-1234567890
        Use o email admin@example.com e IP 192.168.1.100
        """

        sanitized = self.isolation_engine._sanitize_text(prompt_with_secrets)

        assert "[REDACTED]" in sanitized
        assert "secret123" not in sanitized
        assert "sk-1234567890" not in sanitized
        assert "[EMAIL]" in sanitized
        assert "[IP_ADDRESS]" in sanitized

    def test_limit_prompt_length(self):
        """Testa limitação de tamanho do prompt"""
        long_prompt = "a" * 15000
        limited = self.isolation_engine._limit_prompt_length(long_prompt)

        assert len(limited) <= 10000
        assert limited.endswith("...")

    def test_isolate_context_creates_isolated_task(self):
        """Testa criação de tarefa isolada"""
        task_spec = TaskSpec(
            task_id="test_001",
            task_type=TaskType.CODE_GENERATION,
            prompt="Crie uma função Python",
            context={"language": "python", "password": "secret123"},
            metadata={"user_id": "123"},
        )

        async def run_test():
            isolated = await self.isolation_engine.isolate_context(task_spec)

            assert isinstance(isolated, IsolatedTask)
            assert isolated.task_id == "test_001"
            assert "secret123" not in str(isolated.context)  # Valor sensível removido
            assert "[REDACTED]" in str(isolated.context)  # Substituído por marcador
            assert isolated.isolation_hash

        asyncio.run(run_test())

    def test_validate_isolation_integrity(self):
        """Testa validação de integridade do isolamento"""

        async def run_test():
            task_spec = TaskSpec(task_id="test", task_type=TaskType.ANALYSIS, prompt="test")
            isolated = await self.isolation_engine.isolate_context(task_spec)

            # Integridade deve ser válida
            assert self.isolation_engine.validate_isolation_integrity(isolated)

            # Modificar hash deve invalidar
            isolated.isolation_hash = "modified"
            assert not self.isolation_engine.validate_isolation_integrity(isolated)

        asyncio.run(run_test())


class TestGeminiProvider:
    """Testes para provedor Gemini"""

    def setup_method(self):
        """Configura testes"""
        self.config = {
            "api_key_env": "GOOGLE_AI_API_KEY",
            "api_base_url": "https://generativelanguage.googleapis.com",
            "rate_limits": {"requests_per_minute": 60},
        }
        self.provider = GeminiProvider(self.config)

    @patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test_key"})
    def test_initialize_success(self):
        """Testa inicialização bem-sucedida"""

        async def run_test():
            await self.provider.initialize()
            assert self.provider.api_key == "test_key"
            assert self.provider.base_url == "https://generativelanguage.googleapis.com"

        asyncio.run(run_test())

    def test_initialize_without_api_key_fails(self):
        """Testa falha de inicialização sem chave API"""

        async def run_test():
            with pytest.raises(ValueError, match="GOOGLE_AI_API_KEY não configurada"):
                await self.provider.initialize()

        asyncio.run(run_test())

    def test_get_capabilities(self):
        """Testa obtenção de capacidades"""
        capabilities = self.provider.get_capabilities()

        assert isinstance(capabilities, ProviderCapabilities)
        assert TaskType.CODE_GENERATION in capabilities.supported_task_types
        assert capabilities.max_context_length == 2097152
        assert capabilities.supports_multimodal

    @patch("aiohttp.ClientSession.post")
    @patch.dict(os.environ, {"GOOGLE_AI_API_KEY": "test_key"})
    def test_execute_task_success(self, mock_post):
        """Testa execução bem-sucedida de tarefa"""
        # Mock da resposta
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "candidates": [
                    {"content": {"parts": [{"text": "def hello():\n    return 'Hello, World!'"}]}}
                ],
                "usage": {"total_tokens": 100},
            }
        )
        mock_post.return_value.__aenter__.return_value = mock_response

        async def run_test():
            await self.provider.initialize()

            task = TaskSpec(
                task_id="test_001",
                task_type=TaskType.CODE_GENERATION,
                prompt="Crie uma função hello world",
            )

            result = await self.provider.execute_task(task)

            assert result.success
            assert result.task_id == "test_001"
            assert result.content is not None and "def hello():" in result.content
            assert result.provider_used == "gemini"
            assert result.cost_estimate is not None and result.cost_estimate > 0

        asyncio.run(run_test())

    def test_select_model_based_on_task_type(self):
        """Testa seleção de modelo baseada no tipo de tarefa"""
        assert self.provider._select_model(TaskType.CODE_GENERATION) == "gemini-1.5-pro"
        assert self.provider._select_model(TaskType.ANALYSIS) == "gemini-1.5-flash"


class TestCopilotProvider:
    """Testes para provedor Copilot"""

    def setup_method(self):
        """Configura testes"""
        self.config = {
            "github_token_env": "GITHUB_TOKEN",
            "api_base_url": "https://api.github.com",
            "rate_limits": {"requests_per_minute": 60},
        }
        self.provider = CopilotProvider(self.config)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_initialize_success(self):
        """Testa inicialização bem-sucedida"""

        async def run_test():
            await self.provider.initialize()
            assert self.provider.token == "test_token"

        asyncio.run(run_test())

    def test_get_capabilities(self):
        """Testa obtenção de capacidades"""
        capabilities = self.provider.get_capabilities()

        assert isinstance(capabilities, ProviderCapabilities)
        assert TaskType.CODE_GENERATION in capabilities.supported_task_types
        assert not capabilities.supports_multimodal
        assert capabilities.max_context_length == 8192


class TestOpenRouterProvider:
    """Testes para provedor OpenRouter"""

    def setup_method(self):
        """Configura testes"""
        self.config = {
            "api_key_env": "OPENROUTER_API_KEY",
            "api_base_url": "https://openrouter.ai/api/v1",
            "rate_limits": {"requests_per_minute": 100},
        }
        self.provider = OpenRouterProvider(self.config)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"})
    def test_initialize_success(self):
        """Testa inicialização bem-sucedida"""

        async def run_test():
            await self.provider.initialize()
            assert self.provider.api_key == "test_key"

        asyncio.run(run_test())

    def test_select_model_uses_free_model_for_code(self):
        """Testa que usa modelo gratuito para tarefas de código"""
        assert self.provider._select_model(TaskType.CODE_GENERATION) == "qwen/qwen3-coder:free"
        assert self.provider._select_model(TaskType.CODE_REVIEW) == "qwen/qwen3-coder:free"
        assert self.provider._select_model(TaskType.ANALYSIS) == "openai/gpt-4-turbo"

    def test_calculate_cost_free_model(self):
        """Testa cálculo de custo para modelo gratuito"""
        cost = self.provider._calculate_cost("qwen/qwen3-coder:free", 1000)
        assert cost == 0.0

    def test_calculate_cost_paid_model(self):
        """Testa cálculo de custo para modelo pago"""
        cost = self.provider._calculate_cost("openai/gpt-4-turbo", 1000)
        assert cost > 0


class TestTaskDelegationManager:
    """Testes para gerenciador de delegação"""

    def setup_method(self):
        """Configura testes"""
        self.config_path = "/home/fahbrain/projects/omnimind/config/external_ai_providers.yaml"
        self.manager = TaskDelegationManager(self.config_path)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"})
    def test_initialize_providers(self):
        """Testa inicialização de provedores"""

        async def run_test():
            await self.manager.initialize_providers()

            # Deve ter inicializado OpenRouter (já que tem chave)
            assert "openrouter" in self.manager.providers

            # Fecha conexões
            await self.manager.close()

        asyncio.run(run_test())

    def test_select_provider_based_on_task_type(self):
        """Testa seleção de provedor baseada no tipo de tarefa"""

        async def run_test():
            await self.manager.initialize_providers()

            # Cria tarefa isolada mock
            isolated_task = IsolatedTask(task_id="test_001", prompt="Crie uma função", context={})

            # Para tarefas de código, deve priorizar OpenRouter
            selection = await self.manager._select_provider(isolated_task)

            if selection:  # Só se houver provedores disponíveis
                assert selection.provider_name in ["openrouter", "copilot", "gemini"]

            await self.manager.close()

        asyncio.run(run_test())

    def test_get_delegation_stats(self):
        """Testa obtenção de estatísticas de delegação"""

        async def run_test():
            stats = await self.manager.get_delegation_stats()

            assert "total_delegations" in stats
            assert "success_rate" in stats
            assert "provider_usage" in stats
            assert "total_cost" in stats

        asyncio.run(run_test())


class TestIntegration:
    """Testes de integração"""

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"})
    def test_full_delegation_flow(self):
        """Testa fluxo completo de delegação"""

        async def run_test():
            manager = TaskDelegationManager()

            # Inicializa provedores
            await manager.initialize_providers()

            # Cria tarefa
            task_spec = TaskSpec(
                task_id="integration_test_001",
                task_type=TaskType.CODE_GENERATION,
                prompt="Crie uma função simples em Python",
                context={"language": "python"},
            )

            # Delega tarefa (vai falhar porque é mock, mas testa o fluxo)
            result = await manager.delegate_task(task_spec)

            # Verifica estrutura do resultado
            assert isinstance(result, DelegationResult)
            assert result.task_id == "integration_test_001"
            assert "success" in result.__dict__
            assert "provider_used" in result.__dict__

            # Fecha conexões
            await manager.close()

        asyncio.run(run_test())


# Testes de configuração
def test_external_ai_config_loading():
    """Testa carregamento da configuração externa"""
    manager = TaskDelegationManager()

    # Verifica se configuração foi carregada
    assert manager.config is not None
    assert "providers" in manager.config
    assert "task_delegation" in manager.config


def test_provider_config_validation():
    """Testa validação da configuração de provedores"""
    manager = TaskDelegationManager()

    # Verifica estrutura da configuração
    providers_config = manager.config.get("providers", {})

    for provider_name, provider_config in providers_config.items():
        assert "enabled" in provider_config
        assert "name" in provider_config

        if provider_config.get("enabled"):
            assert "api_key_env" in provider_config or "github_token_env" in provider_config


if __name__ == "__main__":
    # Executa testes
    pytest.main([__file__, "-v"])
