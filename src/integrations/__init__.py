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
