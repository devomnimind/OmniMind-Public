#!/usr/bin/env python3
"""
Minimal FastAPI backend for OmniMind - focused startup
Removes optional dependencies to ensure clean startup
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest
from starlette.status import WS_1008_POLICY_VIOLATION

# Load environment
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omnimind.backend.minimal")

# Auth config
_AUTH_FILE = Path("config/dashboard_auth.json")
security = HTTPBasic()


def _load_dashboard_credentials() -> Optional[Dict[str, str]]:
    if not _AUTH_FILE.exists():
        return None
    try:
        with _AUTH_FILE.open("r") as f:
            data = json.load(f)
        user = data.get("user")
        password = data.get("pass")
        if user and password:
            return {"user": user, "pass": password}
    except Exception as e:
        logger.warning(f"Failed to read auth file: {e}")
    return None


def _ensure_dashboard_credentials() -> tuple[str, str]:
    env_user = os.environ.get("OMNIMIND_DASHBOARD_USER")
    env_pass = os.environ.get("OMNIMIND_DASHBOARD_PASS")
    if env_user and env_pass:
        return env_user, env_pass
    
    saved = _load_dashboard_credentials()
    if saved:
        return saved["user"], saved["pass"]
    
    # Generate new
    user = "admin"
    password = "omnimind2025!"
    _AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _AUTH_FILE.open("w") as f:
        json.dump({"user": user, "pass": password}, f, indent=2)
    return user, password


DASHBOARD_USER, DASHBOARD_PASS = _ensure_dashboard_credentials()
logger.info(f"Dashboard auth: user={DASHBOARD_USER}")


def _verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    correct_user = compare_digest(credentials.username, DASHBOARD_USER)
    correct_pass = compare_digest(credentials.password, DASHBOARD_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username


async def _authorize_websocket(websocket: WebSocket) -> bool:
    """Authorize WebSocket connection via query param token."""
    auth_token = websocket.query_params.get("auth_token")
    if not auth_token:
        return False
    
    # Decode base64 token
    try:
        import base64
        decoded = base64.b64decode(auth_token).decode('utf-8')
        user, password = decoded.split(":", 1)
        return compare_digest(user, DASHBOARD_USER) and compare_digest(password, DASHBOARD_PASS)
    except Exception:
        return False


# Minimal WebSocket Manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, set] = {}
    
    async def start(self):
        logger.info("WebSocket manager started")
    
    async def stop(self):
        logger.info("WebSocket manager stopped")
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)
        logger.info(f"Client {client_id} disconnected")
    
    async def subscribe(self, client_id: str, channels: list):
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(channels)
            logger.info(f"Client {client_id} subscribed to {channels}")
    
    async def unsubscribe(self, client_id: str, channels: list):
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(channels)
            logger.info(f"Client {client_id} unsubscribed from {channels}")
    
    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all clients subscribed to channel."""
        for client_id, channels in self.subscriptions.items():
            if channel in channels:
                websocket = self.active_connections.get(client_id)
                if websocket:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Failed to send to {client_id}: {e}")


ws_manager = WebSocketManager()


# Minimal Sinthome Broadcaster
class SinthomeBroadcaster:
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start(self):
        logger.info("Sinthome broadcaster starting...")
        self.running = True
        self.task = asyncio.create_task(self._broadcast_loop())
        logger.info("Sinthome broadcaster started")
    
    async def stop(self):
        logger.info("Sinthome broadcaster stopping...")
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Sinthome broadcaster stopped")
    
    async def _broadcast_loop(self):
        """Broadcast minimal sinthome metrics every 1s."""
        import psutil
        
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory().percent
                
                # Simple integrity calculation
                integrity = max(0.0, min(1.0, 1.0 - (cpu/200 + mem/200)))
                
                message = {
                    "type": "metrics",
                    "channel": "sinthome",
                    "data": {
                        "integrity": integrity,
                        "state": "ACTIVE",
                        "raw": {
                            "cpu": cpu,
                            "memory": mem,
                            "entropy": (cpu + mem) / 2
                        },
                        "metrics": {
                            "logical_impasse": 0.9,
                            "strange_attractor_markers": 0.95,
                            "real_inaccessible": 0.85
                        }
                    },
                    "timestamp": time.time()
                }
                
                await ws_manager.broadcast("sinthome", message)
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                await asyncio.sleep(1.0)


sinthome_broadcaster = SinthomeBroadcaster()


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    # Start minimal services
    await ws_manager.start()
    await sinthome_broadcaster.start()
    
    logger.info("Application started successfully")
    
    try:
        yield
    finally:
        logger.info("Shutting down application...")
        await sinthome_broadcaster.stop()
        await ws_manager.stop()
        logger.info("Application shutdown complete")


# FastAPI app
app = FastAPI(title="OmniMind Backend (Minimal)", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "backend_time": time.time()
    }


@app.get("/")
def root():
    return {"message": "OmniMind Backend (Minimal)", "status": "running"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint."""
    client_id = str(uuid.uuid4())
    
    if not await _authorize_websocket(websocket):
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
        return
    
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "subscribe":
                channels = data.get("channels", [])
                await ws_manager.subscribe(client_id, channels)
            
            elif data.get("type") == "unsubscribe":
                channels = data.get("channels", [])
                await ws_manager.unsubscribe(client_id, channels)
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
    
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        ws_manager.disconnect(client_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
