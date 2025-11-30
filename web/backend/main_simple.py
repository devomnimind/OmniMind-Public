"""OmniMind FastAPI Backend - Simplified version for immediate responsiveness."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Set up paths BEFORE any imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src_path = os.path.join(project_root, 'src')
web_path = os.path.join(project_root, 'web')

sys.path.insert(0, src_path)
sys.path.insert(0, web_path)

os.environ['PYTHONPATH'] = f"{src_path}:{web_path}"

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest
from starlette.status import HTTP_401_UNAUTHORIZED
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="OmniMind Dashboard API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

# Dashboard credentials
_dashboard_user = os.getenv("OMNIMIND_DASHBOARD_USER", "admin")
_dashboard_pass = os.getenv("OMNIMIND_DASHBOARD_PASS", "omnimind2025!")


def _verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify HTTP Basic auth credentials."""
    is_user = compare_digest(credentials.username, _dashboard_user)
    is_pass = compare_digest(credentials.password, _dashboard_pass)
    if not (is_user and is_pass):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def read_root():
    """Root endpoint - confirm API is running."""
    return {"message": "OmniMind Backend is running."}


@app.get("/api/v1/status")
async def get_status():
    """Simple status endpoint."""
    return {"status": "nominal", "active_agents": 0}


@app.get("/daemon/status")
async def daemon_status(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """Get current daemon status with real metrics from actual system operations."""
    try:
        # Lazy import to avoid freezing
        from src.api.routes.daemon import get_daemon_status as get_real_daemon_status

        # Get real metrics
        result = await get_real_daemon_status()
        logger.info("Daemon status retrieved successfully")
        return result
    except Exception as e:
        logger.error(f"Error getting daemon status: {e}")
        return {
            "error": str(e),
            "running": False,
            "uptime_seconds": 0,
            "task_count": 0,
        }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
