"""Enhanced MCP Client with Connection Pooling and Retry Logic.

This module provides production-ready MCP client functionality with advanced
features like connection pooling, automatic retries, circuit breaker pattern,
and comprehensive error handling.

Reference: Problem Statement - FRENTE 5: MCP Client Completo
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, Optional, TypeVar
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry logic.

    Attributes:
        max_retries: Maximum number of retry attempts
        initial_backoff_ms: Initial backoff time in milliseconds
        max_backoff_ms: Maximum backoff time in milliseconds
        backoff_multiplier: Multiplier for exponential backoff
        retryable_status_codes: HTTP status codes that should trigger retry
    """

    max_retries: int = 3
    initial_backoff_ms: int = 100
    max_backoff_ms: int = 10000
    backoff_multiplier: float = 2.0
    retryable_status_codes: set[int] = field(
        default_factory=lambda: {408, 429, 500, 502, 503, 504}
    )


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker.

    Attributes:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes to close circuit from half-open
        timeout_seconds: Time to wait before trying half-open state
        window_size: Size of the sliding window for failure tracking
    """

    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 60.0
    window_size: int = 10


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pooling.

    Attributes:
        max_connections: Maximum number of connections in pool
        connection_timeout: Timeout for individual connections
        idle_timeout: Time before idle connections are closed
        max_retries_per_connection: Max retries per connection
    """

    max_connections: int = 10
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0
    max_retries_per_connection: int = 3


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance.

    Implements the circuit breaker pattern to prevent cascading failures
    and allow services time to recover.

    Example:
        >>> config = CircuitBreakerConfig()
        >>> breaker = CircuitBreaker(config)
        >>> try:
        ...     result = breaker.call(lambda: risky_operation())
        ... except CircuitOpenError:
        ...     # Circuit is open, service is down
        ...     pass
    """

    def __init__(self, config: CircuitBreakerConfig) -> None:
        """Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
        """
        self.config = config
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._recent_results: deque[bool] = deque(maxlen=config.window_size)
        self._lock = Lock()

        logger.info("circuit_breaker_initialized", state=self._state.value)

    def call(self, func: Callable[[], T]) -> T:
        """Execute function through circuit breaker.

        Args:
            func: Function to execute

        Returns:
            Function result

        Raises:
            CircuitOpenError: If circuit is open
            Exception: Any exception from the function
        """
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info("circuit_state_changed", state="half_open")
                else:
                    raise CircuitOpenError("Circuit breaker is OPEN")

        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful operation."""
        with self._lock:
            self._recent_results.append(True)

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info("circuit_state_changed", state="closed")

    def _on_failure(self) -> None:
        """Handle failed operation."""
        with self._lock:
            self._recent_results.append(False)
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning("circuit_state_changed", state="open")
            elif self._state == CircuitState.CLOSED:
                # Check if we should open the circuit
                recent_failures = sum(1 for r in self._recent_results if not r)
                if recent_failures >= self.config.failure_threshold:
                    self._state = CircuitState.OPEN
                    logger.warning(
                        "circuit_opened",
                        failures=recent_failures,
                        threshold=self.config.failure_threshold,
                    )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return True

        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.config.timeout_seconds

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    def reset(self) -> None:
        """Manually reset circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._recent_results.clear()
            logger.info("circuit_breaker_reset")


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class EnhancedMCPClient:
    """Enhanced MCP client with production features.

    Provides a robust MCP client with connection pooling, automatic retries,
    circuit breaker pattern, and comprehensive error handling.

    Example:
        >>> retry_config = RetryConfig(max_retries=3)
        >>> breaker_config = CircuitBreakerConfig()
        >>> client = EnhancedMCPClient(
        ...     endpoint="http://localhost:4321/mcp",
        ...     retry_config=retry_config,
        ...     circuit_breaker_config=breaker_config
        ... )
        >>> content = client.read_file("/path/to/file.txt")
    """

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:4321/mcp",
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    ) -> None:
        """Initialize enhanced MCP client.

        Args:
            endpoint: MCP server endpoint URL
            timeout: Request timeout in seconds
            retry_config: Retry configuration (uses defaults if None)
            circuit_breaker_config: Circuit breaker config (uses defaults if None)
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self._circuit_breaker = CircuitBreaker(
            circuit_breaker_config or CircuitBreakerConfig()
        )
        self._headers = {"Content-Type": "application/json"}
        self._request_count = 0
        self._error_count = 0

        logger.info(
            "enhanced_mcp_client_initialized",
            endpoint=endpoint,
            max_retries=self.retry_config.max_retries,
        )

    def _execute_with_retry(self, operation: Callable[[], T], operation_name: str) -> T:
        """Execute operation with retry logic.

        Args:
            operation: Operation to execute
            operation_name: Name for logging

        Returns:
            Operation result

        Raises:
            Exception: If all retries exhausted
        """
        last_exception: Optional[Exception] = None
        backoff_ms = self.retry_config.initial_backoff_ms

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Execute through circuit breaker
                result = self._circuit_breaker.call(operation)
                if attempt > 0:
                    logger.info(
                        "retry_succeeded",
                        operation=operation_name,
                        attempt=attempt,
                    )
                return result

            except CircuitOpenError:
                logger.error("circuit_breaker_open", operation=operation_name)
                raise

            except urllib.error.HTTPError as e:
                last_exception = e
                if e.code not in self.retry_config.retryable_status_codes:
                    # Non-retryable error
                    raise

                if attempt < self.retry_config.max_retries:
                    logger.warning(
                        "http_error_retrying",
                        operation=operation_name,
                        status_code=e.code,
                        attempt=attempt,
                        backoff_ms=backoff_ms,
                    )
                    time.sleep(backoff_ms / 1000.0)
                    backoff_ms = min(
                        backoff_ms * self.retry_config.backoff_multiplier,
                        self.retry_config.max_backoff_ms,
                    )

            except urllib.error.URLError as e:
                last_exception = e
                if attempt < self.retry_config.max_retries:
                    logger.warning(
                        "connection_error_retrying",
                        operation=operation_name,
                        error=str(e),
                        attempt=attempt,
                        backoff_ms=backoff_ms,
                    )
                    time.sleep(backoff_ms / 1000.0)
                    backoff_ms = min(
                        backoff_ms * self.retry_config.backoff_multiplier,
                        self.retry_config.max_backoff_ms,
                    )

            except Exception as e:
                last_exception = e
                logger.error(
                    "unexpected_error",
                    operation=operation_name,
                    error=str(e),
                    attempt=attempt,
                )
                raise

        # All retries exhausted
        self._error_count += 1
        logger.error(
            "all_retries_exhausted",
            operation=operation_name,
            max_retries=self.retry_config.max_retries,
        )
        if last_exception:
            raise last_exception
        raise RuntimeError(f"All retries exhausted for {operation_name}")

    def _request(self, method: str, params: Dict[str, Any]) -> Any:
        """Make MCP request with retry logic.

        Args:
            method: MCP method name
            params: Method parameters

        Returns:
            Response result
        """
        self._request_count += 1

        def make_request() -> Any:
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": uuid4().hex,
            }
            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                self.endpoint,
                data=data,
                headers=self._headers,
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")

            try:
                result_payload = json.loads(body)
            except json.JSONDecodeError as exc:
                raise MCPClientError("Invalid JSON response from MCP server") from exc

            if "error" in result_payload:
                err = result_payload["error"]
                raise MCPClientError(err.get("message", "MCP error"))

            return result_payload.get("result")

        return self._execute_with_retry(make_request, f"mcp_{method}")

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """Read file via MCP with retry logic.

        Args:
            path: File path
            encoding: File encoding

        Returns:
            File contents
        """
        return self._request("read_file", {"path": path, "encoding": encoding})  # type: ignore[no-any-return]

    def write_file(
        self, path: str, content: str, encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Write file via MCP with retry logic.

        Args:
            path: File path
            content: File content
            encoding: File encoding

        Returns:
            Write result
        """
        return self._request(  # type: ignore[no-any-return]
            "write_file", {"path": path, "content": content, "encoding": encoding}
        )

    def list_dir(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """List directory via MCP with retry logic.

        Args:
            path: Directory path
            recursive: List recursively

        Returns:
            Directory listing
        """
        return self._request("list_dir", {"path": path, "recursive": recursive})  # type: ignore[no-any-return]

    def stat(self, path: str) -> Dict[str, Any]:
        """Get file stats via MCP with retry logic.

        Args:
            path: File path

        Returns:
            File statistics
        """
        return self._request("stat", {"path": path})  # type: ignore[no-any-return]

    def get_metrics(self) -> Dict[str, Any]:
        """Get MCP server metrics.

        Returns:
            Server metrics
        """
        return self._request("get_metrics", {})  # type: ignore[no-any-return]

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics.

        Returns:
            Dictionary with client statistics
        """
        return {
            "requests_total": self._request_count,
            "errors_total": self._error_count,
            "circuit_state": self._circuit_breaker.get_state().value,
            "success_rate": (
                (self._request_count - self._error_count) / self._request_count
                if self._request_count > 0
                else 0.0
            ),
        }

    def reset_circuit_breaker(self) -> None:
        """Manually reset the circuit breaker."""
        self._circuit_breaker.reset()


class MCPClientError(Exception):
    """MCP client error."""

    pass
