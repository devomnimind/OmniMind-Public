"""API routes for OmniMind specific functionality."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Body

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/omnimind", tags=["omnimind"])


@router.get("/messages", response_model=List[Dict[str, Any]])
async def get_messages() -> List[Dict[str, Any]]:
    """
    Get recent system messages.

    Returns a list of messages from the system.
    """
    # TODO: Connect to actual message bus or log storage
    # For now, return an empty list to satisfy the API contract
    return []


@router.post("/messages")
async def post_message(message: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Receive a message from the client (polling mode fallback).
    """
    logger.info(f"Received message via HTTP POST: {message}")
    # In a real implementation, this would push to the message bus
    return {"status": "received", "message_id": message.get("id")}
