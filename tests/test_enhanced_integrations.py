"""Tests for enhanced integration modules.

Tests MCP client enhancements, OAuth 2.0, and webhook framework.
"""

import json
import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from src.integrations.mcp_client_enhanced import (
    EnhancedMCPClient,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitOpenError,
    RetryConfig,
)
from src.integrations.oauth2_client import (
    OAuth2Client,
    OAuth2Config,
    OAuth2Token,
    OAuth2Error,
)
from src.integrations.webhook_framework import (
    WebhookReceiver,
    WebhookSender,
    WebhookEvent,
    WebhookConfig,
    WebhookEventType,
    WebhookError,
)


class TestCircuitBreaker:
    """Tests for circuit breaker implementation."""

    def test_circuit_breaker_initialization(self) -> None:
        """Test circuit breaker initialization."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker(config)
        assert breaker.get_state() == CircuitState.CLOSED

    def test_circuit_opens_on_failures(self) -> None:
        """Test circuit opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3, window_size=5)
        breaker = CircuitBreaker(config)

        # Simulate failures - catch the exception properly
        failure_count = 0
        for _ in range(5):
            try:
                breaker.call(lambda: 1 / 0)  # Will raise exception
            except (ZeroDivisionError, CircuitOpenError):
                failure_count += 1

        assert breaker.get_state() == CircuitState.OPEN
        assert failure_count == 5

    def test_circuit_open_rejects_calls(self) -> None:
        """Test circuit breaker rejects calls when open."""
        config = CircuitBreakerConfig(failure_threshold=2, window_size=3)
        breaker = CircuitBreaker(config)

        # Open the circuit - catch both exception types
        for _ in range(3):
            try:
                breaker.call(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitOpenError):
                pass

        # Should reject calls
        with pytest.raises(CircuitOpenError):
            breaker.call(lambda: "test")

    def test_circuit_half_open_after_timeout(self) -> None:
        """Test circuit transitions to half-open after timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,  # Need 2 successes to close
            timeout_seconds=0.1,
            window_size=3,
        )
        breaker = CircuitBreaker(config)

        # Open the circuit - catch both exception types
        for _ in range(3):
            try:
                breaker.call(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitOpenError):
                pass

        assert breaker.get_state() == CircuitState.OPEN

        # Wait for timeout
        time.sleep(0.15)

        # Should attempt half-open (need 2 successful calls to close)
        result1 = breaker.call(lambda: "success1")
        assert result1 == "success1"
        assert breaker.get_state() == CircuitState.HALF_OPEN

        result2 = breaker.call(lambda: "success2")
        assert result2 == "success2"

        # State should be CLOSED after enough successful calls
        assert breaker.get_state() == CircuitState.CLOSED

    def test_circuit_reset(self) -> None:
        """Test manual circuit reset."""
        config = CircuitBreakerConfig(failure_threshold=2, window_size=3)
        breaker = CircuitBreaker(config)

        # Open the circuit - catch both exception types
        for _ in range(3):
            try:
                breaker.call(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitOpenError):
                pass

        assert breaker.get_state() == CircuitState.OPEN

        # Reset
        breaker.reset()
        assert breaker.get_state() == CircuitState.CLOSED


class TestEnhancedMCPClient:
    """Tests for enhanced MCP client."""

    def test_client_initialization(self) -> None:
        """Test enhanced MCP client initialization."""
        retry_config = RetryConfig(max_retries=3)
        client = EnhancedMCPClient(retry_config=retry_config)
        assert client.retry_config.max_retries == 3

    @patch("urllib.request.urlopen")
    def test_successful_request(self, mock_urlopen: Mock) -> None:
        """Test successful MCP request."""
        # Mock response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(
            {"jsonrpc": "2.0", "result": {"content": "test"}, "id": "123"}
        ).encode("utf-8")
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = EnhancedMCPClient()
        result = client.read_file("/test/file.txt")
        assert result is not None

    def test_get_stats(self) -> None:
        """Test client statistics."""
        client = EnhancedMCPClient()
        stats = client.get_stats()
        assert "requests_total" in stats
        assert "errors_total" in stats
        assert "circuit_state" in stats
        assert "success_rate" in stats

    def test_reset_circuit_breaker(self) -> None:
        """Test manual circuit breaker reset."""
        client = EnhancedMCPClient()
        client.reset_circuit_breaker()
        stats = client.get_stats()
        assert stats["circuit_state"] == "closed"


class TestOAuth2Client:
    """Tests for OAuth 2.0 client."""

    def test_config_creation(self) -> None:
        """Test OAuth2 configuration creation."""
        config = OAuth2Config(
            client_id="test-client",
            client_secret="test-secret",
            authorization_endpoint="https://auth.example.com/oauth/authorize",
            token_endpoint="https://auth.example.com/oauth/token",
            redirect_uri="http://localhost:8080/callback",
            scope="read write",
        )
        assert config.client_id == "test-client"
        assert config.scope == "read write"

    def test_token_creation(self) -> None:
        """Test OAuth2 token creation."""
        token = OAuth2Token(
            access_token="test-token",
            expires_in=3600,
        )
        assert token.access_token == "test-token"
        assert not token.is_expired()

    def test_token_expiration(self) -> None:
        """Test token expiration check."""
        token = OAuth2Token(
            access_token="test-token",
            expires_in=60,
            issued_at=time.time() - 120,  # Issued 2 minutes ago
        )
        assert token.is_expired()

    def test_token_serialization(self) -> None:
        """Test token to/from dict."""
        original = OAuth2Token(
            access_token="test-token",
            refresh_token="refresh-token",
            expires_in=3600,
        )
        token_dict = original.to_dict()
        restored = OAuth2Token.from_dict(token_dict)

        assert restored.access_token == original.access_token
        assert restored.refresh_token == original.refresh_token

    def test_get_authorization_url(self) -> None:
        """Test authorization URL generation."""
        config = OAuth2Config(
            client_id="test-client",
            client_secret="test-secret",
            authorization_endpoint="https://auth.example.com/oauth/authorize",
            token_endpoint="https://auth.example.com/oauth/token",
            redirect_uri="http://localhost:8080/callback",
            scope="read write",
        )
        oauth = OAuth2Client(config)
        url = oauth.get_authorization_url(use_pkce=True)

        assert "https://auth.example.com/oauth/authorize" in url
        assert "client_id=test-client" in url
        assert "redirect_uri=" in url
        assert "scope=read+write" in url
        assert "code_challenge=" in url

    def test_get_authorization_url_without_pkce(self) -> None:
        """Test authorization URL generation without PKCE."""
        config = OAuth2Config(
            client_id="test-client",
            client_secret="test-secret",
            authorization_endpoint="https://auth.example.com/oauth/authorize",
            token_endpoint="https://auth.example.com/oauth/token",
            redirect_uri="http://localhost:8080/callback",
        )
        oauth = OAuth2Client(config)
        url = oauth.get_authorization_url(use_pkce=False)

        assert "https://auth.example.com/oauth/authorize" in url
        assert "code_challenge=" not in url

    def test_get_token_info_no_token(self) -> None:
        """Test token info when no token exists."""
        config = OAuth2Config(
            client_id="test",
            client_secret="secret",
            authorization_endpoint="https://auth.example.com/oauth/authorize",
            token_endpoint="https://auth.example.com/oauth/token",
            redirect_uri="http://localhost/callback",
        )
        oauth = OAuth2Client(config)
        info = oauth.get_token_info()
        assert info is None


class TestWebhookFramework:
    """Tests for webhook framework."""

    def test_webhook_config_creation(self) -> None:
        """Test webhook configuration creation."""
        config = WebhookConfig(
            secret="my-secret",
            validate_signature=True,
        )
        assert config.secret == "my-secret"
        assert config.validate_signature is True

    def test_webhook_event_creation(self) -> None:
        """Test webhook event creation."""
        event = WebhookEvent(
            id="test-123",
            type=WebhookEventType.CREATE,
            timestamp=time.time(),
            payload={"key": "value"},
            source="test-source",
        )
        assert event.id == "test-123"
        assert event.type == WebhookEventType.CREATE
        assert event.payload["key"] == "value"

    def test_webhook_event_serialization(self) -> None:
        """Test event to/from dict."""
        original = WebhookEvent(
            id="test-123",
            type=WebhookEventType.UPDATE,
            timestamp=time.time(),
            payload={"data": "test"},
        )
        event_dict = original.to_dict()
        restored = WebhookEvent.from_dict(event_dict)

        assert restored.id == original.id
        assert restored.type == original.type
        assert restored.payload == original.payload

    def test_webhook_receiver_initialization(self) -> None:
        """Test webhook receiver initialization."""
        config = WebhookConfig(secret="test-secret")
        receiver = WebhookReceiver(config)
        assert receiver.config.secret == "test-secret"

    def test_webhook_receiver_event_handler(self) -> None:
        """Test event handler registration."""
        config = WebhookConfig(secret="test-secret", validate_signature=False)
        receiver = WebhookReceiver(config)

        handler_called = False

        @receiver.on_event(WebhookEventType.CREATE)
        def handle_create(event: WebhookEvent) -> None:
            nonlocal handler_called
            handler_called = True

        # Process a webhook
        event_data = {
            "id": "test-123",
            "type": "create",
            "timestamp": time.time(),
            "payload": {"test": "data"},
        }
        body = json.dumps(event_data)
        receiver.process_webhook(body)

        assert handler_called

    def test_webhook_receiver_missing_signature(self) -> None:
        """Test webhook processing fails without signature."""
        config = WebhookConfig(secret="test-secret", validate_signature=True)
        receiver = WebhookReceiver(config)

        event_data = {
            "id": "test-123",
            "type": "create",
            "timestamp": time.time(),
            "payload": {},
        }
        body = json.dumps(event_data)

        with pytest.raises(WebhookError, match="Missing signature"):
            receiver.process_webhook(body, {})

    def test_webhook_sender_initialization(self) -> None:
        """Test webhook sender initialization."""
        config = WebhookConfig(secret="test-secret")
        sender = WebhookSender(config)
        assert sender.config.secret == "test-secret"

    def test_webhook_sender_stats(self) -> None:
        """Test sender statistics."""
        config = WebhookConfig()
        sender = WebhookSender(config)
        stats = sender.get_stats()

        assert "sent_total" in stats
        assert "errors_total" in stats
        assert "success_rate" in stats

    def test_webhook_event_type_enum(self) -> None:
        """Test webhook event types."""
        assert WebhookEventType.PING.value == "ping"
        assert WebhookEventType.CREATE.value == "create"
        assert WebhookEventType.UPDATE.value == "update"
        assert WebhookEventType.DELETE.value == "delete"
        assert WebhookEventType.CUSTOM.value == "custom"
