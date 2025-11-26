"""
Enhanced MCP Client com otimização de contexto e proteção de dados.

Implementa:
- Compreensão contextual otimizada com cache local
- Redução lógica de chamadas MCP e uso de tokens
- Rate limiting configurável
- Autenticação e segurança (TLS/SSL futuro)
- Monitoramento e logs detalhados
- Proteção de dados integrada
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, cast

from src.audit.immutable_audit import get_audit_system
from src.integrations.mcp_client import MCPClient, MCPClientError
from src.integrations.mcp_data_protection import get_data_protection, ProtectionResult

logger = logging.getLogger(__name__)


@dataclass
class ContextEntry:
    """Entrada de contexto cacheado."""

    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    size_bytes: int = 0

    def __post_init__(self) -> None:
        """Calcula tamanho em bytes."""
        self.size_bytes = len(str(self.value).encode())


@dataclass
class RateLimitConfig:
    """Configuração de rate limiting."""

    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_concurrent_requests: int = 10
    cooldown_seconds: int = 60


@dataclass
class CallMetrics:
    """Métricas de chamadas MCP."""

    total_calls: int = 0
    cached_calls: int = 0
    failed_calls: int = 0
    total_tokens_sent: int = 0
    total_tokens_saved: int = 0
    avg_response_time_ms: float = 0.0
    last_call_timestamp: float = 0.0


class RateLimitExceeded(Exception):
    """Exceção quando rate limit é excedido."""


class EnhancedMCPClient:
    """
    Cliente MCP aprimorado com cache, rate limiting e proteção de dados.

    Features:
    - Cache inteligente de resultados frequentes
    - Compressão e sanitização de contexto
    - Rate limiting configurável
    - Proteção de dados automática
    - Métricas detalhadas
    """

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:4321/mcp",
        timeout: float = 15.0,
        enable_cache: bool = True,
        cache_ttl_seconds: int = 3600,
        max_cache_size_mb: int = 100,
        rate_limit: Optional[RateLimitConfig] = None,
        enable_data_protection: bool = True,
        enable_audit: bool = True,
    ) -> None:
        """
        Inicializa cliente MCP aprimorado.

        Args:
            endpoint: Endpoint do servidor MCP.
            timeout: Timeout para requests.
            enable_cache: Habilita cache de resultados.
            cache_ttl_seconds: TTL do cache em segundos.
            max_cache_size_mb: Tamanho máximo do cache em MB.
            rate_limit: Configuração de rate limiting.
            enable_data_protection: Habilita proteção de dados.
            enable_audit: Habilita auditoria.
        """
        self.client = MCPClient(endpoint=endpoint, timeout=timeout)
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl_seconds
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.enable_data_protection = enable_data_protection
        self.enable_audit = enable_audit

        # Cache de contexto
        self._context_cache: Dict[str, ContextEntry] = {}
        self._cache_hits = 0
        self._cache_misses = 0

        # Rate limiting
        self.rate_limit = rate_limit or RateLimitConfig()
        self._request_timestamps: List[float] = []
        self._hourly_request_count = 0
        self._last_hour_reset = time.time()

        # Métricas
        self.metrics = CallMetrics()

        # Proteção de dados
        self.data_protection = get_data_protection() if enable_data_protection else None

        # Auditoria
        self.audit_system = get_audit_system() if enable_audit else None

        logger.info(
            "EnhancedMCPClient inicializado (cache=%s, protection=%s)",
            enable_cache,
            enable_data_protection,
        )

    def _check_rate_limit(self) -> None:
        """Verifica se rate limit foi excedido."""
        now = time.time()

        # Reset contador horário se necessário
        if now - self._last_hour_reset > 3600:
            self._hourly_request_count = 0
            self._last_hour_reset = now

        # Limpar requests antigos (>1 minuto)
        self._request_timestamps = [ts for ts in self._request_timestamps if now - ts < 60]

        # Verificar limite por minuto
        if len(self._request_timestamps) >= self.rate_limit.max_requests_per_minute:
            raise RateLimitExceeded(
                f"Rate limit excedido: {self.rate_limit.max_requests_per_minute} req/min"
            )

        # Verificar limite por hora
        if self._hourly_request_count >= self.rate_limit.max_requests_per_hour:
            raise RateLimitExceeded(
                f"Rate limit horário excedido: {self.rate_limit.max_requests_per_hour} req/hora"
            )

        # Registrar request
        self._request_timestamps.append(now)
        self._hourly_request_count += 1

    def _get_cache_key(self, method: str, params: Dict[str, Any]) -> str:
        """Gera chave de cache baseada no método e parâmetros."""
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.sha256(f"{method}:{params_str}".encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Obtém valor do cache se válido."""
        if not self.enable_cache:
            return None

        entry = self._context_cache.get(cache_key)
        if entry is None:
            self._cache_misses += 1
            return None

        # Verificar TTL
        if time.time() - entry.timestamp > self.cache_ttl:
            del self._context_cache[cache_key]
            self._cache_misses += 1
            return None

        # Cache hit
        entry.access_count += 1
        self._cache_hits += 1
        self.metrics.cached_calls += 1
        self.metrics.total_tokens_saved += entry.size_bytes // 4  # Estimativa

        logger.debug("Cache hit para %s (acessos=%d)", cache_key[:8], entry.access_count)
        return entry.value

    def _add_to_cache(self, cache_key: str, value: Any) -> None:
        """Adiciona valor ao cache."""
        if not self.enable_cache:
            return

        # Verificar tamanho do cache
        current_size = sum(entry.size_bytes for entry in self._context_cache.values())

        if current_size > self.max_cache_size_bytes:
            # Evict least recently used (LRU)
            self._evict_lru()

        entry = ContextEntry(key=cache_key, value=value, timestamp=time.time(), access_count=1)

        self._context_cache[cache_key] = entry
        logger.debug("Cache adicionado: %s (%d bytes)", cache_key[:8], entry.size_bytes)

    def _evict_lru(self) -> None:
        """Remove entradas menos recentemente usadas do cache."""
        # Ordenar por timestamp (mais antigos primeiro)
        sorted_entries = sorted(self._context_cache.items(), key=lambda x: x[1].timestamp)

        # Remover 20% mais antigos
        to_remove = int(len(sorted_entries) * 0.2)
        for key, _ in sorted_entries[:to_remove]:
            del self._context_cache[key]

        logger.info("Cache LRU eviction: %d entradas removidas", to_remove)

    def _protect_data(self, data: Any) -> Tuple[Any, Optional[ProtectionResult]]:
        """Protege dados antes de enviar."""
        if not self.enable_data_protection or self.data_protection is None:
            return data, None

        protected, result = self.data_protection.sanitize_for_mcp(data)

        if not result.safe:
            logger.warning("Dados protegidos contêm %d violações DLP", len(result.violations))

        return protected, result

    def _audit_call(
        self,
        method: str,
        params: Dict[str, Any],
        result: Any,
        cached: bool,
        protection_result: Optional[ProtectionResult] = None,
    ) -> None:
        """Audita chamada MCP."""
        if not self.enable_audit or self.audit_system is None:
            return

        self.audit_system.log_action(
            action=f"mcp_call_{method}",
            details={
                "method": method,
                "params_size": len(str(params)),
                "result_size": len(str(result)),
                "cached": cached,
                "protected": protection_result is not None,
                "safe": protection_result.safe if protection_result else True,
            },
            category="enhanced_mcp_client",
        )

    def _compress_context(self, data: str, max_tokens: int = 4000) -> str:
        """
        Comprime contexto mantendo informações mais relevantes.

        Args:
            data: Contexto a comprimir.
            max_tokens: Máximo de tokens (aproximado por caracteres/4).

        Returns:
            Contexto comprimido.
        """
        max_chars = max_tokens * 4

        if len(data) <= max_chars:
            return data

        # Estratégia de compressão:
        # 1. Dividir em linhas
        # 2. Priorizar início e fim
        # 3. Sumarizar meio

        lines = data.split("\n")
        total_lines = len(lines)

        # Manter primeiras 30% e últimas 30%
        keep_start = int(total_lines * 0.3)
        keep_end = int(total_lines * 0.3)

        compressed_lines = (
            lines[:keep_start]
            + [f"... [Comprimido: {total_lines - keep_start - keep_end} linhas] ..."]
            + lines[-keep_end:]
        )

        compressed = "\n".join(compressed_lines)

        # Se ainda muito grande, truncar
        if len(compressed) > max_chars:
            compressed = compressed[:max_chars] + "\n... [Truncado]"

        logger.debug("Contexto comprimido: %d -> %d chars", len(data), len(compressed))

        return compressed

    def call_with_context_optimization(
        self,
        method: str,
        params: Dict[str, Any],
        enable_compression: bool = True,
        max_context_tokens: int = 4000,
    ) -> Any:
        """
        Chama MCP com otimização de contexto.

        Args:
            method: Método MCP a chamar.
            params: Parâmetros do método.
            enable_compression: Habilita compressão de contexto.
            max_context_tokens: Máximo de tokens de contexto.

        Returns:
            Resultado da chamada MCP.
        """
        start_time = time.time()

        try:
            # Verificar rate limit
            self._check_rate_limit()

            # Gerar chave de cache
            cache_key = self._get_cache_key(method, params)

            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                self._audit_call(method, params, cached_result, cached=True)
                return cached_result

            # Proteger dados nos parâmetros
            protected_params, protection_result = self._protect_data(params)

            # Comprimir contexto se habilitado
            if enable_compression and "content" in protected_params:
                protected_params["content"] = self._compress_context(
                    str(protected_params["content"]), max_context_tokens
                )

            # Estimar tokens enviados
            tokens_sent = len(str(protected_params)) // 4

            # Fazer chamada real
            result = self.client._request(method, protected_params)

            # Adicionar ao cache
            self._add_to_cache(cache_key, result)

            # Atualizar métricas
            self.metrics.total_calls += 1
            self.metrics.total_tokens_sent += tokens_sent
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.avg_response_time_ms = (
                self.metrics.avg_response_time_ms * 0.9 + elapsed_ms * 0.1
            )
            self.metrics.last_call_timestamp = time.time()

            # Auditar
            self._audit_call(
                method,
                params,
                result,
                cached=False,
                protection_result=protection_result,
            )

            return result

        except RateLimitExceeded:
            logger.warning("Rate limit excedido para método %s", method)
            raise
        except MCPClientError as e:
            self.metrics.failed_calls += 1
            logger.error("Erro na chamada MCP %s: %s", method, e)
            raise
        except Exception as e:
            self.metrics.failed_calls += 1
            logger.error("Erro inesperado na chamada MCP %s: %s", method, e)
            raise

    # Métodos convenientes que usam otimização

    def read_file(self, path: str, encoding: str = "utf-8", enable_compression: bool = True) -> str:
        """Lê arquivo com proteção de dados e cache."""
        return cast(
            str,
            self.call_with_context_optimization(
                "read_file",
                {"path": path, "encoding": encoding},
                enable_compression=enable_compression,
            ),
        )

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Escreve arquivo com proteção de dados."""
        # Write não usa cache
        protected_content, _ = self._protect_data(content)

        return self.client.write_file(path, protected_content, encoding)

    def list_dir(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """Lista diretório com cache."""
        result = self.call_with_context_optimization(
            "list_dir", {"path": path, "recursive": recursive}
        )
        normalized = result if isinstance(result, dict) else dict(result)
        return cast(Dict[str, Any], normalized)

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do cliente."""
        cache_hit_rate = 0.0
        total_cache_attempts = self._cache_hits + self._cache_misses
        if total_cache_attempts > 0:
            cache_hit_rate = self._cache_hits / total_cache_attempts

        return {
            "calls": {
                "total": self.metrics.total_calls,
                "cached": self.metrics.cached_calls,
                "failed": self.metrics.failed_calls,
            },
            "cache": {
                "hit_rate": cache_hit_rate,
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "size": len(self._context_cache),
                "size_bytes": sum(e.size_bytes for e in self._context_cache.values()),
            },
            "tokens": {
                "sent": self.metrics.total_tokens_sent,
                "saved": self.metrics.total_tokens_saved,
            },
            "performance": {
                "avg_response_time_ms": self.metrics.avg_response_time_ms,
            },
            "rate_limit": {
                "requests_last_minute": len(self._request_timestamps),
                "requests_this_hour": self._hourly_request_count,
            },
        }

    def clear_cache(self) -> None:
        """Limpa cache de contexto."""
        self._context_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Cache limpo")

    def get_data_protection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de proteção de dados."""
        if self.data_protection is None:
            return {}
        return self.data_protection.get_statistics()
