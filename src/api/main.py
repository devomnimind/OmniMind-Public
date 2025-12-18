import asyncio
import json
import time
from typing import List

import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, daemon, health, messages, metrics
from src.services.daemon_monitor import daemon_monitor_loop, STATUS_CACHE

app = FastAPI(title="OmniMind API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(daemon.router, prefix="/api/daemon", tags=["daemon"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])


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


async def broadcast_pulse():
    """
    Background task to broadcast unified metrics (Pulse) to all connected clients.
    Unifies hardware, tasks, and consciousness correlates into a single stream.
    """
    while True:
        try:
            # 1. Hardware & Process Metrics (Realtime)
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent

            # 2. Daemon Status & Tasks (Aggregated by DaemonMonitor)
            daemon_status = STATUS_CACHE

            # 3. Consciousness Metrics (Real-time from file)
            real_metrics_data = {}
            try:
                with open("data/monitor/real_metrics.json", "r") as f:
                    real_metrics_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass

            # UNIFIED PULSE
            pulse_msg = {
                "type": "omnimind_pulse",
                "timestamp": time.time(),
                "data": {
                    "hardware": {"cpu": cpu, "memory": mem, "agent_count": count_active_agents()},
                    "daemon": {
                        "status": daemon_status.get("system_metrics", {}).get(
                            "is_user_active", True
                        ),
                        "tasks": daemon_status.get("task_info", {}),
                        "tribunal": daemon_status.get("tribunal_info", {}),
                    },
                    "consciousness": {
                        "phi": real_metrics_data.get("phi", 0.0),
                        "anxiety": real_metrics_data.get("anxiety", 0.0),
                        "flow": real_metrics_data.get("flow", 0.0),
                        "entropy": real_metrics_data.get("entropy", 0.0),
                        "ici": real_metrics_data.get("ici", 0.0),
                        "prs": real_metrics_data.get("prs", 0.0),
                        "interpretation": real_metrics_data.get(
                            "interpretation",
                            {"message": "OmniMind Core Pulsing...", "confidence": "Stable"},
                        ),
                    },
                },
            }

            await manager.broadcast(json.dumps(pulse_msg))

            # Legacy support (deprecated but keeping for intermediate stability)
            metrics_simple = {
                "type": "metrics_update",
                "data": {
                    "cpu_percent": cpu,
                    "memory_percent": mem,
                    "timestamp": time.time(),
                },
            }
            await manager.broadcast(json.dumps(metrics_simple))

            await asyncio.sleep(2)  # Healthy 2s heartbeat
        except Exception as e:
            print(f"Pulse broadcast error: {e}")
            await asyncio.sleep(2)


@app.on_event("startup")
async def startup_event():
    # Start Daemon Monitor and Pulse Broadcast
    asyncio.create_task(daemon_monitor_loop(refresh_interval=5))
    asyncio.create_task(broadcast_pulse())


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
