"""Integration helpers for external services and protocols.

This module provides integrations for:
- Model Context Protocol (MCP) client and server
- D-Bus system integration
- OAuth 2.0 authentication
- Webhook framework
- GraphQL and Supabase
"""

# Try to import dbus-dependent modules
try:
    from .dbus_controller import DBusSessionController, DBusSystemController

    _HAS_DBUS = True
except ImportError:
    _HAS_DBUS = False
    DBusSessionController = None  # type: ignore
    DBusSystemController = None  # type: ignore

from .graphql_supabase import GraphQLSupabaseError, GraphQLSupabaseHelper
from .mcp_client import MCPClient, MCPClientError
from .mcp_client_enhanced import CircuitBreaker, CircuitOpenError, EnhancedMCPClient
from .mcp_server import MCPConfig, MCPRequestError, MCPServer
from .oauth2_client import OAuth2Client, OAuth2Config, OAuth2Error, OAuth2Token
from .webhook_framework import (
    WebhookConfig,
    WebhookError,
    WebhookEvent,
    WebhookReceiver,
    WebhookSender,
)

__all__ = [
    # MCP
    "MCPConfig",
    "MCPRequestError",
    "MCPServer",
    "MCPClient",
    "MCPClientError",
    "EnhancedMCPClient",
    "CircuitBreaker",
    "CircuitOpenError",
    # D-Bus (optional)
    "DBusSessionController",
    "DBusSystemController",
    # OAuth
    "OAuth2Client",
    "OAuth2Config",
    "OAuth2Token",
    "OAuth2Error",
    # Webhooks
    "WebhookReceiver",
    "WebhookSender",
    "WebhookEvent",
    "WebhookConfig",
    "WebhookError",
    # GraphQL/Supabase
    "GraphQLSupabaseHelper",
    "GraphQLSupabaseError",
]
