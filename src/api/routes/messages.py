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

import time
from typing import Any, Dict, List

from fastapi import APIRouter, Request

router = APIRouter()

# In-memory message queue for polling simulation
message_queue: List[Dict[str, Any]] = []


@router.get("/messages")
async def get_messages() -> List[Dict[str, Any]]:
    """
    Get pending messages for polling clients.
    """
    global message_queue
    # Return pending messages and clear queue (simple polling)
    messages = message_queue[:]
    message_queue = []

    # Always return at least a heartbeat if empty to keep connection alive
    if not messages:
        return []

    return messages


@router.post("/messages")
async def post_message(request: Request):
    """
    Receive messages from clients via polling fallback.
    """
    await request.json()
    # Log or process message
    # For now, just acknowledge
    return {"status": "received", "timestamp": time.time()}
