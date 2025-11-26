from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import health, daemon, messages
import asyncio
import json
import time

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
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(daemon.router, prefix="/daemon", tags=["daemon"])
app.include_router(messages.router, prefix="/api/omnimind", tags=["messages"])


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
            except:
                pass


manager = ConnectionManager()


async def broadcast_metrics():
    """
    Background task to broadcast simulated metrics to all connected clients.
    """
    while True:
        try:
            # 1. Broadcast for RealtimeAnalytics (Simple)
            metrics_simple = {
                "type": "metrics_update",
                "data": {
                    "cpu_percent": 45.2,
                    "memory_percent": 60.5,
                    "active_tasks": 4,
                    "completed_tasks": 120,
                    "agent_count": 1,
                    "timestamp": time.time(),
                },
            }
            await manager.broadcast(json.dumps(metrics_simple))

            await asyncio.sleep(0.1)  # Small delay to prevent race condition in frontend hook

            # 2. Broadcast for OmniMindSinthome (Complex)
            metrics_sinthome = {
                "type": "metrics",
                "channel": "sinthome",
                "data": {
                    "state": "ACTIVE",
                    "integrity": 1.0,
                    "raw": {"cpu": 45.2, "memory": 60.5, "entropy": 0.0},
                    "metrics": {
                        "real_inaccessible": 1.0,
                        "logical_impasse": 1.0,
                        "strange_attractor_markers": 1.0,
                    },
                    "consciousness": {
                        "ICI": 0.85,
                        "PRS": 0.92,
                        "details": {
                            "ici_components": {
                                "temporal_coherence": 0.9,
                                "marker_integration": 0.8,
                                "resonance": 0.85,
                            },
                            "prs_components": {"avg_micro_entropy": 0.1, "macro_entropy": 0.2},
                        },
                        "interpretation": {
                            "message": "System is operating within optimal parameters.",
                            "confidence": "HIGH",
                            "disclaimer": "Simulated Consciousness",
                        },
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
                            {"type": "pong", "id": msg.get("id"), "timestamp": time.time() * 1000}
                        )
                    )
            except:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
