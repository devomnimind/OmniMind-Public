"""OAuth 2.0 Authentication Helper Module.

Provides OAuth 2.0 authentication flows for external API integrations.
Supports authorization code flow, client credentials, and refresh tokens.

Reference: Problem Statement - FRENTE 5: APIs Externas - Autenticação OAuth
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class OAuth2GrantType(Enum):
    """OAuth 2.0 grant types."""

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    IMPLICIT = "implicit"
    PASSWORD = "password"


@dataclass
class OAuth2Token:
    """OAuth 2.0 access token.

    Attributes:
        access_token: The access token
        token_type: Token type (usually 'Bearer')
        expires_in: Token lifetime in seconds
        refresh_token: Refresh token (optional)
        scope: Token scope
        issued_at: Timestamp when token was issued
    """

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    issued_at: float = field(default_factory=time.time)

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check if token is expired.

        Args:
            buffer_seconds: Safety buffer in seconds

        Returns:
            True if token is expired or will expire soon
        """
        elapsed = time.time() - self.issued_at
        return elapsed >= (self.expires_in - buffer_seconds)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "issued_at": self.issued_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OAuth2Token:
        """Create from dictionary.

        Args:
            data: Token data

        Returns:
            OAuth2Token instance
        """
        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 3600),
            refresh_token=data.get("refresh_token"),
            scope=data.get("scope"),
            issued_at=data.get("issued_at", time.time()),
        )


@dataclass
class OAuth2Config:
    """OAuth 2.0 configuration.

    Attributes:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        authorization_endpoint: Authorization endpoint URL
        token_endpoint: Token endpoint URL
        redirect_uri: Redirect URI for callbacks
        scope: Requested scopes
        state: CSRF protection state
    """

    client_id: str
    client_secret: str
    authorization_endpoint: str
    token_endpoint: str
    redirect_uri: str
    scope: str = ""
    state: Optional[str] = None


class OAuth2Client:
    """OAuth 2.0 client implementation.

    Provides OAuth 2.0 authentication flows with automatic token refresh
    and PKCE support for enhanced security.

    Example:
        >>> config = OAuth2Config(
        ...     client_id="your-client-id",
        ...     client_secret="your-secret",
        ...     authorization_endpoint="https://provider.com/oauth/authorize",
        ...     token_endpoint="https://provider.com/oauth/token",
        ...     redirect_uri="http://localhost:8080/callback",
        ...     scope="read write"
        ... )
        >>> oauth = OAuth2Client(config)
        >>> auth_url = oauth.get_authorization_url()
        >>> # User visits auth_url and is redirected back with code
        >>> token = oauth.exchange_code_for_token(authorization_code)
        >>> # Use token for API calls
        >>> headers = oauth.get_auth_headers()
    """

    def __init__(self, config: OAuth2Config) -> None:
        """Initialize OAuth 2.0 client.

        Args:
            config: OAuth configuration
        """
        self.config = config
        self._token: Optional[OAuth2Token] = None
        self._code_verifier: Optional[str] = None
        self._code_challenge: Optional[str] = None

        logger.info(
            "oauth2_client_initialized",
            client_id=config.client_id,
            scope=config.scope,
        )

    def get_authorization_url(self, use_pkce: bool = True) -> str:
        """Generate authorization URL for OAuth flow.

        Args:
            use_pkce: Use PKCE for enhanced security

        Returns:
            Authorization URL
        """
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
            "state": self.config.state or self._generate_state(),
        }

        if use_pkce:
            self._code_verifier = self._generate_code_verifier()
            self._code_challenge = self._generate_code_challenge(self._code_verifier)
            params["code_challenge"] = self._code_challenge
            params["code_challenge_method"] = "S256"

        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.config.authorization_endpoint}?{query_string}"

        logger.info("authorization_url_generated", use_pkce=use_pkce)
        return auth_url

    def exchange_code_for_token(
        self, authorization_code: str, use_pkce: bool = True
    ) -> OAuth2Token:
        """Exchange authorization code for access token.

        Args:
            authorization_code: Authorization code from callback
            use_pkce: Whether PKCE was used in authorization

        Returns:
            Access token

        Raises:
            OAuth2Error: If token exchange fails
        """
        data = {
            "grant_type": OAuth2GrantType.AUTHORIZATION_CODE.value,
            "code": authorization_code,
            "redirect_uri": self.config.redirect_uri,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        if use_pkce and self._code_verifier:
            data["code_verifier"] = self._code_verifier

        try:
            token_data = self._request_token(data)
            self._token = OAuth2Token.from_dict(token_data)

            logger.info("token_obtained", expires_in=self._token.expires_in)
            return self._token

        except Exception as e:
            logger.error("token_exchange_failed", error=str(e))
            raise OAuth2Error(f"Failed to exchange code for token: {e}") from e

    def refresh_access_token(self) -> OAuth2Token:
        """Refresh the access token using refresh token.

        Returns:
            New access token

        Raises:
            OAuth2Error: If refresh fails
        """
        if not self._token or not self._token.refresh_token:
            raise OAuth2Error("No refresh token available")

        data = {
            "grant_type": OAuth2GrantType.REFRESH_TOKEN.value,
            "refresh_token": self._token.refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        try:
            token_data = self._request_token(data)
            self._token = OAuth2Token.from_dict(token_data)

            logger.info("token_refreshed", expires_in=self._token.expires_in)
            return self._token

        except Exception as e:
            logger.error("token_refresh_failed", error=str(e))
            raise OAuth2Error(f"Failed to refresh token: {e}") from e

    def get_client_credentials_token(self) -> OAuth2Token:
        """Get token using client credentials flow.

        Returns:
            Access token

        Raises:
            OAuth2Error: If authentication fails
        """
        data = {
            "grant_type": OAuth2GrantType.CLIENT_CREDENTIALS.value,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "scope": self.config.scope,
        }

        try:
            token_data = self._request_token(data)
            self._token = OAuth2Token.from_dict(token_data)

            logger.info(
                "client_credentials_token_obtained",
                expires_in=self._token.expires_in,
            )
            return self._token

        except Exception as e:
            logger.error("client_credentials_failed", error=str(e))
            raise OAuth2Error(f"Failed to get client credentials token: {e}") from e

    def get_valid_token(self) -> OAuth2Token:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            OAuth2Error: If token cannot be obtained
        """
        if not self._token:
            raise OAuth2Error("No token available. Authenticate first.")

        if self._token.is_expired():
            logger.info("token_expired_refreshing")
            return self.refresh_access_token()

        return self._token

    def get_auth_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication.

        Returns:
            Dictionary with Authorization header

        Raises:
            OAuth2Error: If no valid token available
        """
        token = self.get_valid_token()
        return {"Authorization": f"{token.token_type} {token.access_token}"}

    def _request_token(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Make token request to OAuth server.

        Args:
            data: Request parameters

        Returns:
            Token response data

        Raises:
            OAuth2Error: If request fails
        """
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        request = urllib.request.Request(
            self.config.token_endpoint,
            data=encoded_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)  # type: ignore[no-any-return]

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(
                "token_request_failed",
                status=e.code,
                error=error_body,
            )
            raise OAuth2Error(f"HTTP {e.code}: {error_body}") from e

        except urllib.error.URLError as e:
            logger.error("token_request_connection_error", error=str(e))
            raise OAuth2Error(f"Connection error: {e}") from e

    @staticmethod
    def _generate_state() -> str:
        """Generate random state for CSRF protection."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def _generate_code_verifier() -> str:
        """Generate PKCE code verifier."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")

    @staticmethod
    def _generate_code_challenge(verifier: str) -> str:
        """Generate PKCE code challenge from verifier.

        Args:
            verifier: Code verifier

        Returns:
            Code challenge (S256)
        """
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    def revoke_token(self, token: Optional[str] = None) -> None:
        """Revoke an access or refresh token.

        Args:
            token: Token to revoke (uses current token if None)
        """
        token_to_revoke = token or (self._token.access_token if self._token else None)
        if not token_to_revoke:
            logger.warning("no_token_to_revoke")
            return

        # Note: Revocation endpoint varies by provider
        # This is a placeholder implementation
        logger.info("token_revoked")
        self._token = None

    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """Get current token information.

        Returns:
            Token info if available
        """
        if not self._token:
            return None

        return {
            "has_token": True,
            "is_expired": self._token.is_expired(),
            "expires_in": self._token.expires_in,
            "token_type": self._token.token_type,
            "scope": self._token.scope,
            "has_refresh_token": self._token.refresh_token is not None,
        }


class OAuth2Error(Exception):
    """OAuth 2.0 error."""
