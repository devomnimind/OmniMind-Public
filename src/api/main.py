import asyncio
import json
import time
from typing import List

import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware_auto_concurrency import add_auto_concurrency_middleware
from src.api.routes import daemon, health, messages, metrics

app = FastAPI(title="OmniMind API", version="1.0.0")

# Add Auto-Concurrency Detection Middleware (MUST be first for proper detection)
add_auto_concurrency_middleware(app, validation_mode_manager=None)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(daemon.router, prefix="/daemon", tags=["daemon"])
app.include_router(messages.router, prefix="/api/omnimind", tags=["messages"])
app.include_router(metrics.router, prefix="/api/omnimind/metrics", tags=["metrics"])


@app.get("/")
async def root():
    return {"message": "OmniMind API is running"}


# WebSocket Endpoint
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


manager = ConnectionManager()


def count_active_agents() -> int:
    """Count active OmniMind agents (Python processes)."""
    count = 0
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            if proc.info["name"] and "python" in proc.info["name"].lower():
                cmdline = proc.info.get("cmdline", [])
                if cmdline and any(
                    "omnimind" in str(arg).lower() or "tribunal" in str(arg).lower()
                    for arg in cmdline
                ):
                    count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return max(count, 1)


def get_task_counts() -> tuple:
    """Get real task counts from Tribunal."""
    tasks_info = daemon.get_tribunal_tasks_info()
    active = tasks_info["total_tasks"]
    completed = sum(t.get("success_count", 0) for t in tasks_info["tasks"])
    return active, completed


async def broadcast_metrics():
    """
    Background task to broadcast simulated metrics to all connected clients.
    """
    while True:
        try:
            # Get real metrics
            active_tasks, completed_tasks = get_task_counts()
            agent_count = count_active_agents()

            # Read Real Metrics from File
            real_metrics_data = {}
            try:
                with open("data/monitor/real_metrics.json", "r") as f:
                    real_metrics_data = json.load(f)
            except FileNotFoundError:
                pass  # File not created yet
            except Exception as e:
                print(f"Error reading metrics file: {e}")

            # 1. Broadcast for RealtimeAnalytics (Simple)
            metrics_simple = {
                "type": "metrics_update",
                "data": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "active_tasks": active_tasks,
                    "completed_tasks": completed_tasks,
                    "agent_count": agent_count,
                    "timestamp": time.time(),
                },
            }
            await manager.broadcast(json.dumps(metrics_simple))

            await asyncio.sleep(0.1)  # Small delay to prevent race condition in frontend hook

            # 2. Broadcast for OmniMindSinthome (Complex)
            # Use real data if available, otherwise fallback to defaults (0.0)
            metrics_sinthome = {
                "type": "metrics",
                "channel": "sinthome",
                "data": {
                    "state": "ACTIVE",
                    "integrity": 1.0,
                    "raw": {
                        "cpu": psutil.cpu_percent(),
                        "memory": psutil.virtual_memory().percent,
                        "entropy": real_metrics_data.get("entropy", 0.0),
                    },
                    "metrics": {
                        "real_inaccessible": 1.0,
                        "logical_impasse": 1.0,
                        "strange_attractor_markers": 1.0,
                    },
                    "consciousness": {
                        "ICI": real_metrics_data.get("ici", 0.0),
                        "PRS": real_metrics_data.get("prs", 0.0),
                        "details": {
                            "ici_components": real_metrics_data.get("ici_components", {}),
                            "prs_components": real_metrics_data.get("prs_components", {}),
                        },
                        "interpretation": real_metrics_data.get(
                            "interpretation",
                            {
                                "message": "Waiting for system metrics...",
                                "confidence": "Low",
                                "disclaimer": "System initializing...",
                            },
                        ),
                    },
                },
            }
            await manager.broadcast(json.dumps(metrics_sinthome))

            await asyncio.sleep(2)  # Update every 2 seconds
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(2)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_metrics())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial connection success message
        await websocket.send_text(
            json.dumps({"type": "connection_established", "timestamp": time.time() * 1000})
        )

        while True:
            # Receive message (keep connection open)
            data = await websocket.receive_text()

            # Simple echo or heartbeat response
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "pong",
                                "id": msg.get("id"),
                                "timestamp": time.time() * 1000,
                            }
                        )
                    )
            except Exception:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
