"""
OmniMind Service Management

Handles service updates, restarts, and system communication.
"""

from src.services.service_update_api import register_service_update_routes
from src.services.service_update_communicator import (
    ServiceChange,
    ServiceUpdateCommunicator,
    get_communicator,
)

__all__ = [
    "ServiceUpdateCommunicator",
    "ServiceChange",
    "get_communicator",
    "register_service_update_routes",
]
