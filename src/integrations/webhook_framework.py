from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4
import structlog


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

"""Webhook Framework Module.

Provides webhook receiver and sender functionality for external integrations.
Supports webhook validation, retry logic, and event handling.

Reference: Problem Statement - FRENTE 5: APIs Externas - Webhooks e callbacks
"""


logger = structlog.get_logger(__name__)


class WebhookEventType(Enum):
    """Standard webhook event types."""

    PING = "ping"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    CUSTOM = "custom"


@dataclass
class WebhookEvent:
    """Webhook event data.

    Attributes:
        id: Unique event ID
        type: Event type
        timestamp: Event timestamp
        payload: Event payload
        source: Event source identifier
        signature: Event signature for validation
    """

    id: str
    type: WebhookEventType
    timestamp: float
    payload: Dict[str, Any]
    source: str = "unknown"
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "source": self.source,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WebhookEvent:
        """Create from dictionary.

        Args:
            data: Event data

        Returns:
            WebhookEvent instance
        """
        return cls(
            id=data.get("id", str(uuid4())),
            type=WebhookEventType(data.get("type", "custom")),
            timestamp=data.get("timestamp", time.time()),
            payload=data.get("payload", {}),
            source=data.get("source", "unknown"),
            signature=data.get("signature"),
        )


@dataclass
class WebhookConfig:
    """Webhook configuration.

    Attributes:
        secret: Secret key for signature validation
        validate_signature: Whether to validate signatures
        allowed_sources: List of allowed source identifiers
        max_payload_size: Maximum payload size in bytes
        timeout_seconds: Request timeout
    """

    secret: str = ""
    validate_signature: bool = True
    allowed_sources: List[str] = field(default_factory=list)
    max_payload_size: int = 1024 * 1024  # 1MB
    timeout_seconds: float = 30.0


class WebhookReceiver:
    """Webhook receiver for incoming webhook events.

    Validates and processes incoming webhook events with signature verification
    and event handlers.

    Example:
        >>> config = WebhookConfig(secret="my-secret")
        >>> receiver = WebhookReceiver(config)
        >>>
        >>> @receiver.on_event(WebhookEventType.CREATE)
        >>> def handle_create(event: WebhookEvent) -> None:
        ...     print(f"Created: {event.payload}")
        >>>
        >>> # Process incoming webhook
        >>> receiver.process_webhook(request_body, headers)
    """

    def __init__(self, config: WebhookConfig) -> None:
        """Initialize webhook receiver.

        Args:
            config: Webhook configuration
        """
        self.config = config
        self._handlers: Dict[WebhookEventType, List[Callable[[WebhookEvent], None]]] = {}

        logger.info(
            "webhook_receiver_initialized",
            validate_signature=config.validate_signature,
        )

    def on_event(
        self, event_type: WebhookEventType
    ) -> Callable[[Callable[[WebhookEvent], None]], Callable[[WebhookEvent], None]]:
        """Decorator to register event handler.

        Args:
            event_type: Type of event to handle

        Returns:
            Decorator function
        """

        def decorator(
            func: Callable[[WebhookEvent], None],
        ) -> Callable[[WebhookEvent], None]:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            logger.debug("webhook_handler_registered", event_type=event_type.value)
            return func

        return decorator

    def process_webhook(
        self, body: str, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Process incoming webhook request.

        Args:
            body: Request body (JSON string)
            headers: Request headers

        Returns:
            Processing result

        Raises:
            WebhookError: If validation or processing fails
        """
        headers = headers or {}

        # Check payload size
        if len(body.encode("utf-8")) > self.config.max_payload_size:
            raise WebhookError("Payload too large")

        # Validate signature
        if self.config.validate_signature:
            signature = headers.get("X-Webhook-Signature")
            if not signature:
                raise WebhookError("Missing signature")

            if not self._validate_signature(body, signature):
                raise WebhookError("Invalid signature")

        # Parse event
        try:
            data = json.loads(body)
            event = WebhookEvent.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise WebhookError(f"Invalid webhook payload: {e}") from e

        # Check source
        if self.config.allowed_sources:
            if event.source not in self.config.allowed_sources:
                raise WebhookError(f"Source not allowed: {event.source}")

        # Process event
        self._dispatch_event(event)

        logger.info(
            "webhook_processed",
            event_id=event.id,
            event_type=event.type.value,
            source=event.source,
        )

        return {"success": True, "event_id": event.id}

    def _validate_signature(self, body: str, signature: str) -> bool:
        """Validate webhook signature.

        Args:
            body: Request body
            signature: Provided signature

        Returns:
            True if signature is valid
        """
        if not self.config.secret:
            logger.warning("no_secret_configured")
            return True

        expected_signature = self._generate_signature(body)
        return hmac.compare_digest(signature, expected_signature)

    def _generate_signature(self, body: str) -> str:
        """Generate HMAC signature for body.

        Args:
            body: Request body

        Returns:
            HMAC signature (hex)
        """
        return hmac.new(
            self.config.secret.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _dispatch_event(self, event: WebhookEvent) -> None:
        """Dispatch event to registered handlers.

        Args:
            event: Webhook event
        """
        handlers = self._handlers.get(event.type, [])

        if not handlers:
            logger.warning("no_handler_for_event", event_type=event.type.value)
            return

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    "webhook_handler_error",
                    event_type=event.type.value,
                    error=str(e),
                )


class WebhookSender:
    """Webhook sender for outgoing webhook events.

    Sends webhook events to external endpoints with retry logic and
    signature generation.

    Example:
        >>> config = WebhookConfig(secret="my-secret")
        >>> sender = WebhookSender(config)
        >>> event = WebhookEvent(
        ...     id=str(uuid4()),
        ...     type=WebhookEventType.CREATE,
        ...     timestamp=time.time(),
        ...     payload={"key": "value"}
        ... )
        >>> sender.send_webhook("https://example.com/webhook", event)
    """

    def __init__(self, config: WebhookConfig) -> None:
        """Initialize webhook sender.

        Args:
            config: Webhook configuration
        """
        self.config = config
        self._sent_count = 0
        self._error_count = 0

        logger.info("webhook_sender_initialized")

    def send_webhook(
        self,
        url: str,
        event: WebhookEvent,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ) -> Dict[str, Any]:
        """Send webhook to endpoint.

        Args:
            url: Webhook endpoint URL
            event: Event to send
            max_retries: Maximum retry attempts
            retry_backoff: Backoff multiplier for retries

        Returns:
            Send result

        Raises:
            WebhookError: If send fails after retries
        """
        body = json.dumps(event.to_dict())
        signature = self._generate_signature(body)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event-Type": event.type.value,
            "X-Webhook-Event-ID": event.id,
        }

        last_error: Optional[Exception] = None
        backoff = retry_backoff

        for attempt in range(max_retries + 1):
            try:
                response = self._make_request(url, body, headers)
                self._sent_count += 1

                logger.info(
                    "webhook_sent",
                    url=url,
                    event_id=event.id,
                    event_type=event.type.value,
                    attempt=attempt,
                )

                return {
                    "success": True,
                    "event_id": event.id,
                    "status_code": response.get("status_code", 200),
                }

            except Exception as e:
                last_error = e
                self._error_count += 1

                if attempt < max_retries:
                    logger.warning(
                        "webhook_send_retry",
                        url=url,
                        attempt=attempt,
                        error=str(e),
                        backoff=backoff,
                    )
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.error(
                        "webhook_send_failed",
                        url=url,
                        event_id=event.id,
                        error=str(e),
                    )

        raise WebhookError(f"Failed to send webhook after {max_retries} retries") from last_error

    def _make_request(self, url: str, body: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Make HTTP request to webhook endpoint.

        Args:
            url: Endpoint URL
            body: Request body
            headers: Request headers

        Returns:
            Response data

        Raises:
            WebhookError: If request fails
        """
        request = urllib.request.Request(
            url,
            data=body.encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                return {
                    "status_code": response.status,
                    "body": response.read().decode("utf-8"),
                }

        except urllib.error.HTTPError as e:
            raise WebhookError(f"HTTP {e.code}: {e.reason}") from e

        except urllib.error.URLError as e:
            raise WebhookError(f"Connection error: {e}") from e

    def _generate_signature(self, body: str) -> str:
        """Generate HMAC signature for body.

        Args:
            body: Request body

        Returns:
            HMAC signature (hex)
        """
        if not self.config.secret:
            return ""

        return hmac.new(
            self.config.secret.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """Get sender statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "sent_total": self._sent_count,
            "errors_total": self._error_count,
            "success_rate": (
                (self._sent_count - self._error_count) / self._sent_count
                if self._sent_count > 0
                else 0.0
            ),
        }


class WebhookError(Exception):
    """Webhook error."""
