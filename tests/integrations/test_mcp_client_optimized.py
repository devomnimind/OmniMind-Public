"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Testes completos para o Enhanced MCP Client (mcp_client_optimized.py).

Cobertura de:
- Cache de contexto com TTL e LRU eviction
- Rate limiting (por minuto e por hora)
- Proteção de dados
- Compressão de contexto
- Auditoria de chamadas
- Métodos convenientes (read_file, write_file, list_dir)
- Tratamento de exceções e edge cases
"""

from __future__ import annotations

import time
from unittest.mock import Mock, patch

import pytest

from src.integrations.mcp_client_optimized import (
    CallMetrics,
    ContextEntry,
    EnhancedMCPClient,
    RateLimitConfig,
    RateLimitExceeded,
)


class TestContextEntry:
    """Testes para ContextEntry."""

    def test_context_entry_initialization(self) -> None:
        """Testa inicialização de ContextEntry."""
        entry = ContextEntry(
            key="test_key",
            value={"data": "test"},
            timestamp=time.time(),
        )

        assert entry.key == "test_key"
        assert entry.value == {"data": "test"}
        assert entry.access_count == 0
        assert entry.size_bytes > 0

    def test_context_entry_size_calculation(self) -> None:
        """Testa cálculo automático de tamanho."""
        small_entry = ContextEntry(key="small", value="x", timestamp=time.time())
        large_entry = ContextEntry(key="large", value="x" * 1000, timestamp=time.time())

        assert large_entry.size_bytes > small_entry.size_bytes


class TestRateLimitConfig:
    """Testes para RateLimitConfig."""

    def test_default_rate_limit_config(self) -> None:
        """Testa valores padrão de configuração."""
        config = RateLimitConfig()

        assert config.max_requests_per_minute == 60
        assert config.max_requests_per_hour == 1000
        assert config.max_concurrent_requests == 10
        assert config.cooldown_seconds == 60

    def test_custom_rate_limit_config(self) -> None:
        """Testa configuração customizada."""
        config = RateLimitConfig(
            max_requests_per_minute=30,
            max_requests_per_hour=500,
            max_concurrent_requests=5,
            cooldown_seconds=120,
        )

        assert config.max_requests_per_minute == 30
        assert config.max_requests_per_hour == 500
        assert config.max_concurrent_requests == 5
        assert config.cooldown_seconds == 120


class TestCallMetrics:
    """Testes para CallMetrics."""

    def test_call_metrics_initialization(self) -> None:
        """Testa inicialização de métricas."""
        metrics = CallMetrics()

        assert metrics.total_calls == 0
        assert metrics.cached_calls == 0
        assert metrics.failed_calls == 0
        assert metrics.total_tokens_sent == 0
        assert metrics.total_tokens_saved == 0
        assert metrics.avg_response_time_ms == 0.0
        assert metrics.last_call_timestamp == 0.0


class TestEnhancedMCPClient:
    """Testes para EnhancedMCPClient."""

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_client_initialization(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa inicialização do cliente."""
        mock_audit.return_value = Mock()
        mock_protection.return_value = Mock()

        client = EnhancedMCPClient(
            endpoint="http://test:8080",
            timeout=10.0,
            enable_cache=True,
            cache_ttl_seconds=1800,
            max_cache_size_mb=50,
        )

        assert client.enable_cache is True
        assert client.cache_ttl == 1800
        assert client.max_cache_size_bytes == 50 * 1024 * 1024
        assert client._cache_hits == 0
        assert client._cache_misses == 0
        assert len(client._context_cache) == 0

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_cache_key_generation(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa geração de chaves de cache."""
        client = EnhancedMCPClient()

        # Mesmos parâmetros = mesma chave
        key1 = client._get_cache_key("read_file", {"path": "/test"})
        key2 = client._get_cache_key("read_file", {"path": "/test"})
        assert key1 == key2

        # Parâmetros diferentes = chaves diferentes
        key3 = client._get_cache_key("read_file", {"path": "/other"})
        assert key1 != key3

        # Ordem dos parâmetros não importa (JSON sorted)
        key4 = client._get_cache_key("test", {"b": 2, "a": 1})
        key5 = client._get_cache_key("test", {"a": 1, "b": 2})
        assert key4 == key5

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_cache_get_miss(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa cache miss."""
        client = EnhancedMCPClient(enable_cache=True)

        result = client._get_from_cache("nonexistent_key")

        assert result is None
        assert client._cache_misses == 1
        assert client._cache_hits == 0

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_cache_get_hit(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa cache hit."""
        client = EnhancedMCPClient(enable_cache=True)

        # Adiciona ao cache
        client._add_to_cache("test_key", {"result": "data"})

        # Recupera do cache
        result = client._get_from_cache("test_key")

        assert result == {"result": "data"}
        assert client._cache_hits == 1
        assert client._cache_misses == 0

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_cache_ttl_expiration(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa expiração de cache por TTL."""
        client = EnhancedMCPClient(
            enable_cache=True,
            cache_ttl_seconds=1,  # 1 segundo
        )

        # Adiciona ao cache
        client._add_to_cache("test_key", {"result": "data"})

        # Cache hit imediato
        result = client._get_from_cache("test_key")
        assert result == {"result": "data"}

        # Aguarda expiração
        time.sleep(1.1)

        # Cache miss após expiração
        result = client._get_from_cache("test_key")
        assert result is None
        assert "test_key" not in client._context_cache

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_cache_disabled(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa comportamento com cache desabilitado."""
        client = EnhancedMCPClient(enable_cache=False)

        # Tenta adicionar ao cache
        client._add_to_cache("test_key", {"result": "data"})

        # Cache não deve ser populado
        assert len(client._context_cache) == 0

        # Get sempre retorna None
        result = client._get_from_cache("test_key")
        assert result is None

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_lru_eviction(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa eviction LRU quando cache está cheio."""
        # Cache muito pequeno (1 byte)
        client = EnhancedMCPClient(
            enable_cache=True,
            max_cache_size_mb=0.000001,  # ~1 byte
        )

        # Adiciona várias entradas
        for i in range(10):
            client._add_to_cache(f"key_{i}", f"value_{i}")

        # Cache deve ter menos de 10 entradas devido a eviction
        assert len(client._context_cache) < 10

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_rate_limit_per_minute(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa rate limit por minuto."""
        config = RateLimitConfig(max_requests_per_minute=3)
        client = EnhancedMCPClient(rate_limit=config)

        # Primeiras 3 chamadas OK
        for _ in range(3):
            client._check_rate_limit()

        # Quarta chamada deve falhar
        with pytest.raises(RateLimitExceeded) as exc_info:
            client._check_rate_limit()

        assert "req/min" in str(exc_info.value)

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_rate_limit_per_hour(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa rate limit por hora."""
        config = RateLimitConfig(
            max_requests_per_minute=1000,  # Alto
            max_requests_per_hour=5,
        )
        client = EnhancedMCPClient(rate_limit=config)

        # Primeiras 5 chamadas OK
        for _ in range(5):
            client._check_rate_limit()

        # Sexta chamada deve falhar
        with pytest.raises(RateLimitExceeded) as exc_info:
            client._check_rate_limit()

        assert "req/hora" in str(exc_info.value)

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_rate_limit_reset(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa reset de rate limit por minuto."""
        config = RateLimitConfig(max_requests_per_minute=2)
        client = EnhancedMCPClient(rate_limit=config)

        # Usa limite
        client._check_rate_limit()
        client._check_rate_limit()

        # Aguarda limpeza (timestamp > 60s)
        client._request_timestamps = []

        # Nova chamada deve funcionar
        client._check_rate_limit()

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_compress_context_short_text(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa compressão de texto curto (não comprime)."""
        client = EnhancedMCPClient()

        short_text = "Short text"
        compressed = client._compress_context(short_text, max_tokens=1000)

        assert compressed == short_text

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_compress_context_long_text(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa compressão de texto longo."""
        client = EnhancedMCPClient()

        # Texto com muitas linhas
        long_text = "\n".join([f"Line {i}" for i in range(1000)])
        compressed = client._compress_context(long_text, max_tokens=100)

        # Deve ser comprimido
        assert len(compressed) < len(long_text)
        assert "[Comprimido:" in compressed or "[Truncado]" in compressed

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_protect_data_disabled(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa proteção de dados desabilitada."""
        client = EnhancedMCPClient(enable_data_protection=False)

        data = {"sensitive": "password123"}
        protected, result = client._protect_data(data)

        assert protected == data
        assert result is None

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_protect_data_enabled(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa proteção de dados habilitada."""
        mock_protection_obj = Mock()
        mock_protection_obj.sanitize_for_mcp.return_value = (
            {"sensitive": "***REDACTED***"},
            Mock(safe=False, violations=["password_found"]),
        )
        mock_protection.return_value = mock_protection_obj

        client = EnhancedMCPClient(enable_data_protection=True)

        data = {"sensitive": "password123"}
        protected, result = client._protect_data(data)

        assert protected["sensitive"] == "***REDACTED***"
        assert result is not None
        assert not result.safe

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_audit_call_disabled(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa auditoria desabilitada."""
        client = EnhancedMCPClient(enable_audit=False)

        # Não deve lançar exceção
        client._audit_call("test_method", {}, {}, cached=False)

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_audit_call_enabled(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa auditoria habilitada."""
        mock_audit_obj = Mock()
        mock_audit.return_value = mock_audit_obj

        client = EnhancedMCPClient(enable_audit=True)

        client._audit_call("test_method", {"key": "value"}, {"result": "ok"}, cached=True)

        # Verifica se log_action foi chamado
        mock_audit_obj.log_action.assert_called_once()
        call_args = mock_audit_obj.log_action.call_args
        assert call_args[1]["action"] == "mcp_call_test_method"

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_call_with_context_optimization_cached(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa chamada MCP com resultado em cache."""
        mock_mcp_instance = Mock()
        mock_mcp.return_value = mock_mcp_instance

        client = EnhancedMCPClient(enable_cache=True)

        # Popula cache manualmente
        cache_key = client._get_cache_key("test_method", {"param": "value"})
        client._add_to_cache(cache_key, {"cached": "result"})

        # Chamada deve usar cache
        result = client.call_with_context_optimization("test_method", {"param": "value"})

        assert result == {"cached": "result"}
        # Cliente MCP não deve ser chamado
        mock_mcp_instance._request.assert_not_called()

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_call_with_context_optimization_uncached(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa chamada MCP sem cache."""
        mock_mcp_instance = Mock()
        mock_mcp_instance._request.return_value = {"real": "result"}
        mock_mcp.return_value = mock_mcp_instance

        client = EnhancedMCPClient(enable_cache=True, enable_data_protection=False)

        result = client.call_with_context_optimization("test_method", {"param": "value"})

        assert result == {"real": "result"}
        mock_mcp_instance._request.assert_called_once_with("test_method", {"param": "value"})
        # Resultado deve estar no cache agora
        cache_key = client._get_cache_key("test_method", {"param": "value"})
        assert cache_key in client._context_cache

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_call_with_rate_limit_exceeded(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa exceção de rate limit."""
        config = RateLimitConfig(max_requests_per_minute=1)
        client = EnhancedMCPClient(
            enable_cache=False,  # Desabilita cache para forçar chamadas
            enable_data_protection=False,  # Desabilita proteção para simplificar teste
            rate_limit=config,
        )

        mock_mcp_instance = Mock()
        mock_mcp_instance._request.return_value = {"result": "ok"}
        mock_mcp.return_value = mock_mcp_instance

        # Primeira chamada OK
        client.call_with_context_optimization("test", {})

        # Segunda chamada deve falhar
        with pytest.raises(RateLimitExceeded):
            client.call_with_context_optimization("test", {})

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_call_with_mcp_client_error(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa tratamento de erro do MCP Client."""
        from src.integrations.mcp_client import MCPClientError

        mock_mcp_instance = Mock()
        mock_mcp_instance._request.side_effect = MCPClientError("Test error")
        mock_mcp.return_value = mock_mcp_instance

        client = EnhancedMCPClient(enable_cache=False, enable_data_protection=False)

        with pytest.raises(MCPClientError):
            client.call_with_context_optimization("test", {})

        # Métricas devem registrar falha
        assert client.metrics.failed_calls == 1

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_read_file(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa método read_file."""
        mock_mcp_instance = Mock()
        mock_mcp_instance._request.return_value = "file content"
        mock_mcp.return_value = mock_mcp_instance

        client = EnhancedMCPClient(enable_cache=False, enable_data_protection=False)

        content = client.read_file("/test/file.txt")

        assert content == "file content"
        mock_mcp_instance._request.assert_called_once()

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_write_file(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa método write_file."""
        mock_mcp_instance = Mock()
        mock_mcp_instance.write_file.return_value = {
            "size": 100,
            "path": "/test/file.txt",
        }
        mock_mcp.return_value = mock_mcp_instance

        client = EnhancedMCPClient(enable_data_protection=False)

        result = client.write_file("/test/file.txt", "content")

        assert result["size"] == 100
        mock_mcp_instance.write_file.assert_called_once_with("/test/file.txt", "content", "utf-8")

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_list_dir(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa método list_dir."""
        mock_mcp_instance = Mock()
        mock_mcp_instance._request.return_value = {"entries": [{"name": "file.txt"}]}
        mock_mcp.return_value = mock_mcp_instance

        client = EnhancedMCPClient(enable_cache=False, enable_data_protection=False)

        result = client.list_dir("/test")

        assert "entries" in result
        assert result["entries"][0]["name"] == "file.txt"

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_get_metrics(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa obtenção de métricas."""
        client = EnhancedMCPClient()

        # Popula algumas métricas
        client.metrics.total_calls = 10
        client.metrics.cached_calls = 3
        client.metrics.failed_calls = 1
        client._cache_hits = 5
        client._cache_misses = 5

        metrics = client.get_metrics()

        assert metrics["calls"]["total"] == 10
        assert metrics["calls"]["cached"] == 3
        assert metrics["calls"]["failed"] == 1
        assert metrics["cache"]["hit_rate"] == 0.5
        assert metrics["cache"]["hits"] == 5
        assert metrics["cache"]["misses"] == 5

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_clear_cache(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa limpeza de cache."""
        client = EnhancedMCPClient(enable_cache=True)

        # Adiciona entradas ao cache
        client._add_to_cache("key1", "value1")
        client._add_to_cache("key2", "value2")
        client._cache_hits = 10
        client._cache_misses = 5

        client.clear_cache()

        assert len(client._context_cache) == 0
        assert client._cache_hits == 0
        assert client._cache_misses == 0

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_get_data_protection_stats(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa obtenção de estatísticas de proteção."""
        mock_protection_obj = Mock()
        mock_protection_obj.get_statistics.return_value = {"violations": 5}
        mock_protection.return_value = mock_protection_obj

        client = EnhancedMCPClient(enable_data_protection=True)

        stats = client.get_data_protection_stats()

        assert stats["violations"] == 5

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_get_data_protection_stats_disabled(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa estatísticas com proteção desabilitada."""
        client = EnhancedMCPClient(enable_data_protection=False)

        stats = client.get_data_protection_stats()

        assert stats == {}

    @patch("src.integrations.mcp_client_optimized.MCPClient")
    @patch("src.integrations.mcp_client_optimized.get_data_protection")
    @patch("src.integrations.mcp_client_optimized.get_audit_system")
    def test_context_compression_with_content_param(
        self,
        mock_audit: Mock,
        mock_protection: Mock,
        mock_mcp: Mock,
    ) -> None:
        """Testa compressão de contexto quando habilitada."""
        mock_mcp_instance = Mock()
        mock_mcp_instance._request.return_value = {"result": "ok"}
        mock_mcp.return_value = mock_mcp_instance

        client = EnhancedMCPClient(enable_cache=False, enable_data_protection=False)

        # Texto longo no campo "content"
        long_content = "\n".join([f"Line {i}" for i in range(1000)])

        client.call_with_context_optimization(
            "test",
            {"content": long_content},
            enable_compression=True,
            max_context_tokens=100,
        )

        # Verifica que o conteúdo foi comprimido
        call_args = mock_mcp_instance._request.call_args[0][1]
        assert len(call_args["content"]) < len(long_content)
