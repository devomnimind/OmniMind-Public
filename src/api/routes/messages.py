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
