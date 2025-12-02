from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import sys
import threading
import time
import uuid
from base64 import b64encode

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from secrets import compare_digest
from typing import Any, Callable, Dict, Optional, Tuple

from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, WS_1008_POLICY_VIOLATION

from src.agents.orchestrator_agent import OrchestratorAgent
from src.metrics.real_consciousness_metrics import RealConsciousnessMetricsCollector
from web.backend.routes import agents, health, metacognition, omnimind, tasks, tribunal
from web.backend.routes import security as security_router
from web.backend.websocket_manager import ws_manager

# Load environment variables from .env file
load_dotenv()


# Simple observability for backend (replaces DEVBRAIN_V23 import)
class AutonomyObservability:
    def __init__(self) -> None:
        self.self_healing_history: list[dict] = []
        self.atlas_insights: list[dict] = []
        self.sandbox_events: list[dict] = []
        self.dlp_alerts: list[dict] = []
        self.alerts: list[str] = []

    def record_sandbox_event(self, event: dict) -> None:
        """Record sandbox event for observability."""
        logger.info("Backend sandbox event recorded", extra={"sandbox_event": event})
        self.sandbox_events.append(event)

    def record_dlp_alert(self, alert: dict) -> None:
        """Record DLP alert for observability."""
        logger.info("Backend DLP alert recorded", extra={"dlp_alert": alert})
        self.dlp_alerts.append(alert)

    def get_self_healing_snapshot(self) -> dict:
        """Get self healing observability snapshot."""
        return {"latest": {}, "history": self.self_healing_history[-5:], "alerts": []}

    def get_atlas_snapshot(self) -> dict:
        """Get atlas observability snapshot."""
        return {"insights": self.atlas_insights[-10:]}

    def get_security_snapshot(self) -> dict:
        """Get security observability snapshot."""
        return {"sandbox_events": self.sandbox_events[-5:], "dlp_alerts": self.dlp_alerts[-5:]}


autonomy_observability = AutonomyObservability()

# Global consciousness metrics collector
consciousness_metrics_collector = RealConsciousnessMetricsCollector()

logger = logging.getLogger("omnimind.backend")
_AUTH_FILE = Path(os.environ.get("OMNIMIND_DASHBOARD_AUTH_FILE", "config/dashboard_auth.json"))


def _load_dashboard_credentials() -> Optional[Dict[str, str]]:
    if not _AUTH_FILE.exists():
        return None
    try:
        with _AUTH_FILE.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        user = data.get("user")
        password = data.get("pass")
        if isinstance(user, str) and isinstance(password, str):
            return {"user": user, "pass": password}
    except Exception as exc:
        logger.warning("Failed to read dashboard auth file %s: %s", _AUTH_FILE, exc)
    return None


def _persist_dashboard_credentials(credentials: Dict[str, str]) -> None:
    _AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with _AUTH_FILE.open("w", encoding="utf-8") as stream:
            json.dump(credentials, stream, indent=2)
        _AUTH_FILE.chmod(0o600)
    except Exception as exc:
        logger.warning("Unable to persist dashboard credentials %s: %s", _AUTH_FILE, exc)


def _generate_dashboard_credentials() -> Dict[str, str]:
    return {
        "user": secrets.token_hex(8),
        "pass": secrets.token_urlsafe(16),
    }


def _ensure_dashboard_credentials() -> Tuple[str, str]:
    env_user = os.environ.get("OMNIMIND_DASHBOARD_USER")
    env_pass = os.environ.get("OMNIMIND_DASHBOARD_PASS")
    if env_user and env_pass:
        logger.info("Using dashboard credentials from environment variables")
        return env_user, env_pass

    saved = _load_dashboard_credentials()
    if saved:
        logger.info("Loaded dashboard credentials from %s", _AUTH_FILE)
        return saved["user"], saved["pass"]

    generated = _generate_dashboard_credentials()
    _persist_dashboard_credentials(generated)
    logger.info("Generated dashboard credentials at %s (keep file private)", _AUTH_FILE)
    return generated["user"], generated["pass"]


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # Import WebSocket manager
    # Import agent communication broadcaster
    from web.backend.agent_communication_ws import get_broadcaster
    from web.backend.websocket_manager import ws_manager

    # Initialize monitoring variables
    agent_monitor = None
    metrics_collector = None
    performance_tracker = None
    monitoring_available = False

    # Import monitoring systems
    try:
        from web.backend.monitoring import agent_monitor as am  # type: ignore
        from web.backend.monitoring import metrics_collector as mc
        from web.backend.monitoring import performance_tracker as pt

        agent_monitor = am
        metrics_collector = mc
        performance_tracker = pt

        monitoring_available = True
    except ImportError:
        logger.warning("Monitoring systems not available")

    # Import Sinthome Broadcaster
    sinthome_broadcaster: Any = None
    try:
        from web.backend.sinthome_broadcaster import sinthome_broadcaster as sb

        sinthome_broadcaster = sb
    except ImportError:
        logger.warning("Sinthome Broadcaster not available")

    # Import Daemon Monitor
    daemon_monitor_loop: Any = None
    try:
        from src.services.daemon_monitor import daemon_monitor_loop as dml

        daemon_monitor_loop = dml
    except ImportError:
        logger.warning("Daemon Monitor not available")

    # Import Realtime Analytics Broadcaster
    realtime_analytics_broadcaster: Any = None
    try:
        from web.backend.realtime_analytics_broadcaster import (
            realtime_analytics_broadcaster as rab,
        )

        realtime_analytics_broadcaster = rab
    except ImportError:
        logger.warning("Realtime Analytics Broadcaster not available")

    # Initialize Consciousness Metrics Collector
    try:
        await consciousness_metrics_collector.initialize()
        logger.info("Consciousness Metrics Collector initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Consciousness Metrics Collector: {e}")

    # Start WebSocket manager with timeout
    try:
        await asyncio.wait_for(ws_manager.start(), timeout=3.0)
    except asyncio.TimeoutError:
        logger.warning("WebSocket manager startup timed out")
    except Exception as e:
        logger.warning(f"Failed to start WebSocket manager: {e}")

    # Start Sinthome Broadcaster with timeout
    if sinthome_broadcaster:
        try:
            await asyncio.wait_for(sinthome_broadcaster.start(), timeout=3.0)
        except asyncio.TimeoutError:
            logger.warning("Sinthome Broadcaster startup timed out")
        except Exception as e:
            logger.warning(f"Failed to start Sinthome Broadcaster: {e}")

    # Start Daemon Monitor (background worker) with timeout
    daemon_monitor_task = None
    if daemon_monitor_loop is not None:
        try:
            daemon_monitor_task = asyncio.create_task(
                asyncio.wait_for(daemon_monitor_loop(refresh_interval=5), timeout=10.0)
            )
            app_instance.state.daemon_monitor_task = daemon_monitor_task
        except asyncio.TimeoutError:
            logger.warning("Daemon Monitor startup timed out")
        except Exception as e:
            logger.warning(f"Failed to start Daemon Monitor: {e}")

    # Start Realtime Analytics Broadcaster with timeout
    if realtime_analytics_broadcaster:
        try:
            await asyncio.wait_for(realtime_analytics_broadcaster.start(), timeout=3.0)
        except asyncio.TimeoutError:
            logger.warning("Realtime Analytics Broadcaster startup timed out")
        except Exception as e:
            logger.warning(f"Failed to start Realtime Analytics Broadcaster: {e}")

    # Start agent communication broadcaster
    try:
        broadcaster = get_broadcaster()
        await asyncio.wait_for(broadcaster.start(), timeout=3.0)
    except asyncio.TimeoutError:
        logger.warning("Agent communication broadcaster startup timed out")
    except Exception as e:
        logger.warning(f"Failed to start agent communication broadcaster: {e}")

    # Start monitoring systems with timeout
    if monitoring_available and agent_monitor and metrics_collector and performance_tracker:
        try:
            await asyncio.wait_for(agent_monitor.start(), timeout=3.0)
            await asyncio.wait_for(metrics_collector.start(), timeout=3.0)
            await asyncio.wait_for(performance_tracker.start(), timeout=3.0)
            logger.info("All monitoring systems started")
        except asyncio.TimeoutError:
            logger.warning("One or more monitoring systems startup timed out")
        except Exception as e:
            logger.warning(f"Failed to start monitoring systems: {e}")

    # Start orchestrator initialization in background with timeout
    app_instance.state.orchestrator_ready = False
    try:
        asyncio.create_task(asyncio.wait_for(_async_init_orchestrator(app_instance), timeout=10.0))
    except asyncio.TimeoutError:
        logger.warning("Orchestrator initialization timed out")
    except Exception as e:
        logger.warning(f"Failed to initialize orchestrator: {e}")

    # Start metrics reporter
    app_instance.state.metrics_task = asyncio.create_task(_metrics_reporter())

    # Start consciousness metrics collector
    app_instance.state.consciousness_metrics_task = asyncio.create_task(
        _consciousness_metrics_collector()
    )

    try:
        yield
    finally:
        # Stop SecurityAgent monitoring
        try:
            orch = _get_orchestrator()
            if orch.security_agent:
                logger.info("Stopping SecurityAgent monitoring...")
                # SecurityAgent should have a stop method
        except Exception:
            pass

        # Stop metrics reporter
        task = getattr(app_instance.state, "metrics_task", None)
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

        # Stop consciousness metrics collector
        consciousness_task = getattr(app_instance.state, "consciousness_metrics_task", None)
        if consciousness_task:
            consciousness_task.cancel()
            with suppress(asyncio.CancelledError):
                await consciousness_task

        # Stop Sinthome Broadcaster
        if sinthome_broadcaster:
            await sinthome_broadcaster.stop()

        # Stop Daemon Monitor
        if hasattr(app_instance.state, "daemon_monitor_task"):
            app_instance.state.daemon_monitor_task.cancel()
            try:
                await asyncio.wait_for(app_instance.state.daemon_monitor_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        # Stop Realtime Analytics Broadcaster
        if realtime_analytics_broadcaster:
            await realtime_analytics_broadcaster.stop()

        # Stop agent communication broadcaster
        await broadcaster.stop()

        # Stop monitoring systems
        if monitoring_available and agent_monitor and metrics_collector and performance_tracker:
            await agent_monitor.stop()
            await metrics_collector.stop()
            await performance_tracker.stop()
            logger.info("All monitoring systems stopped")

        # Stop WebSocket manager
        await ws_manager.stop()


app = FastAPI(
    title="OmniMind Dashboard API",
    description=(
        "Provides orchestrator snapshots, MCP/D-Bus telemetry, metrics, and "
        "orchestration controls."
    ),
    version="0.2.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

_orchestrator_instance: Optional[OrchestratorAgent] = None
_metrics_collect_interval = int(os.environ.get("OMNIMIND_METRICS_INTERVAL", "30"))
_validation_log = Path(
    os.environ.get("OMNIMIND_SECURITY_VALIDATION_LOG", "logs/security_validation.jsonl")
)
_dashboard_user, _dashboard_pass = _ensure_dashboard_credentials()


def _expected_ws_token() -> str:
    return b64encode(f"{_dashboard_user}:{_dashboard_pass}".encode()).decode()


async def _authorize_websocket(websocket: WebSocket) -> bool:
    auth_token = None
    auth_header = websocket.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("basic "):
        token = auth_header.split(" ", 1)[1].strip()
        if token:
            auth_token = token
    if not auth_token:
        auth_token = websocket.query_params.get("auth_token")
    return auth_token == _expected_ws_token()


class MetricsCollector:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counts: Dict[str, int] = {}
        self._errors: Dict[str, int] = {}
        self._latencies: Dict[str, float] = {}

    def record(self, path: str, latency: float, success: bool) -> None:
        with self._lock:
            self._counts[path] = self._counts.get(path, 0) + 1
            self._latencies[path] = self._latencies.get(path, 0.0) + latency
            self._errors[path] = self._errors.get(path, 0) + (0 if success else 1)

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            details: Dict[str, Dict[str, float]] = {}
            for path, count in self._counts.items():
                total_latency = self._latencies.get(path, 0.0)
                errors = self._errors.get(path, 0)
                details[path] = {
                    "count": count,
                    "errors": errors,
                    "avg_latency": round(total_latency / count, 3) if count else 0.0,
                }
            return {
                "requests": sum(self._counts.values()),
                "errors": sum(self._errors.values()),
                "details": details,
            }


metrics_collector = MetricsCollector()


class OrchestrateRequest(BaseModel):
    task: str
    max_iterations: int = 3


class MCPFlowRequest(BaseModel):
    action: str = "read"
    path: Optional[str] = None
    recursive: bool = False


class DBusFlowRequest(BaseModel):
    flow: str = "power"
    media_action: str = "playpause"


async def _async_init_orchestrator(app_instance: FastAPI):
    global _orchestrator_instance
    logger.info("Starting asynchronous Orchestrator initialization...")
    try:
        # Run in thread pool to avoid blocking event loop
        _orchestrator_instance = await asyncio.to_thread(
            OrchestratorAgent, "config/agent_config.yaml"
        )
        app_instance.state.orchestrator_ready = True
        logger.info("Orchestrator initialized successfully")

        # Connect metacognition routes
        try:
            metacognition.set_orchestrator(_orchestrator_instance)
            logger.info("Metacognition routes connected to orchestrator")
        except Exception as exc:
            logger.warning(f"Failed to connect metacognition routes: {exc}")

        # Start SecurityAgent continuous monitoring (if enabled)
        if _orchestrator_instance.security_agent:
            if _orchestrator_instance.security_agent.config.get("security_agent", {}).get(
                "enabled", False
            ):
                logger.info("Starting SecurityAgent continuous monitoring...")
                asyncio.create_task(
                    _orchestrator_instance.security_agent.start_continuous_monitoring()
                )
                logger.info("SecurityAgent continuous monitoring started")
            else:
                logger.info("SecurityAgent initialized but monitoring disabled in config")
        else:
            logger.info("SecurityAgent not available")

    except Exception as exc:
        logger.error(f"Failed to initialize orchestrator asynchronously: {exc}")
        app_instance.state.orchestrator_error = str(exc)


def _get_orchestrator() -> OrchestratorAgent:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        # Check if initialization failed (using app global since we are in same module)
        if hasattr(app, "state") and hasattr(app.state, "orchestrator_error"):
            raise HTTPException(
                status_code=500,
                detail=f"Orchestrator initialization failed: {app.state.orchestrator_error}",
            )

        # Check if still loading
        raise HTTPException(status_code=503, detail="Orchestrator is initializing, please wait")

    return _orchestrator_instance


def _verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    is_user = compare_digest(credentials.username, _dashboard_user)
    is_pass = compare_digest(credentials.password, _dashboard_pass)
    if not (is_user and is_pass):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid dashboard credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.middleware("http")
async def track_metrics(request: Request, call_next: Callable[[Request], Any]) -> Any:
    start = time.perf_counter()
    success = True
    error_msg = None
    status_code = 200

    try:
        response = await call_next(request)
        status_code = response.status_code
        success = status_code < 400
        return response
    except Exception as exc:
        success = False
        status_code = 500
        error_msg = str(exc)
        logger.exception("Unhandled error processing %s", request.url.path)
        raise
    finally:
        latency = time.perf_counter() - start
        metrics_collector.record(request.url.path, latency, success)

        # Also record in new metrics collector if available
        try:
            from web.backend.monitoring import metrics_collector as new_collector

            new_collector.record_request(
                path=request.url.path,
                method=request.method,
                latency=latency,
                status_code=status_code,
                error=error_msg,
            )
        except ImportError:
            pass


def _collect_orchestrator_metrics() -> Dict[str, Any]:
    try:
        orch = _get_orchestrator()
        return orch.metrics_summary()
    except HTTPException:
        return {"error": "orchestrator unavailable"}


async def _metrics_reporter() -> None:
    while True:
        await asyncio.sleep(_metrics_collect_interval)
        summary = metrics_collector.summary()
        orch_metrics = _collect_orchestrator_metrics()
        logger.info(
            "Dashboard metrics heartbeat - requests=%s errors=%s orchestrator=%s",
            summary["requests"],
            summary["errors"],
            orch_metrics,
        )


async def _consciousness_metrics_collector() -> None:
    """Background task that periodically collects consciousness metrics."""
    logger.info("Starting consciousness metrics collection background task")
    while True:
        try:
            await asyncio.sleep(5)  # Collect every 5 seconds
            metrics = await consciousness_metrics_collector.collect_real_metrics()
            logger.debug(
                f"Collected consciousness metrics: phi={metrics.phi:.4f}, anxiety={metrics.anxiety:.4f}"
            )
        except asyncio.CancelledError:
            logger.info("Consciousness metrics collection task cancelled")
            break
        except Exception as e:
            logger.error(f"Error collecting consciousness metrics: {e}")
            await asyncio.sleep(5)  # Retry after error


def _load_last_validation_entry() -> Dict[str, Any]:
    if not _validation_log.exists():
        return {"latest": None, "log_path": str(_validation_log)}
    entry = None
    try:
        with _validation_log.open("r", encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
        return {"latest": entry, "log_path": str(_validation_log)}
    except Exception:
        return {
            "latest": None,
            "log_path": str(_validation_log),
            "error": "failed to parse",
        }


@app.get("/")
async def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"message": "OmniMind Backend is running."}


@app.get("/api/v1/status")
async def get_status():
    """Returns the current status of the OmniMind system."""
    # In the future, this will query the OrchestratorAgent.
    return {"status": "nominal", "active_agents": 0}


@app.get("/status")
def status(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    orch = _get_orchestrator()
    return {
        "plan": orch.current_plan,
        "progress": orch.plan_overview(),
        "dashboard": orch.dashboard_snapshot,
        "orchestrator_metrics": orch.metrics_summary(),
        "backend_metrics": metrics_collector.summary(),
    }


@app.get("/snapshot")
def snapshot(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    orch = _get_orchestrator()
    return orch.dashboard_snapshot or orch.refresh_dashboard_snapshot()


@app.get("/plan")
def _collect_system_metrics() -> Dict[str, Any]:
    """Collect real-time system metrics (CPU, memory, disk)."""
    try:
        import psutil

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": round(memory.percent, 1),
        }

        # Disk metrics
        disk = psutil.disk_usage("/")
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent": round(disk.percent, 1),
        }

        # Network metrics (basic)
        network = psutil.net_io_counters()
        network_info = {
            "bytes_sent_mb": round(network.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(network.bytes_recv / (1024**2), 2),
        }

        return {
            "cpu": {
                "percent": round(cpu_percent, 1),
                "count": cpu_count,
            },
            "memory": memory_info,
            "disk": disk_info,
            "network": network_info,
        }

    except ImportError:
        logger.warning("psutil not available for system metrics")
        return {"error": "psutil not available"}
    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")
        return {"error": str(e)}


@app.get("/metrics")
def metrics(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """Get comprehensive system metrics."""
    backend_metrics = metrics_collector.summary()

    # Collect real-time system metrics
    system_metrics = _collect_system_metrics()

    # Try to get enhanced metrics
    try:
        from web.backend.monitoring import metrics_collector as new_collector
        from web.backend.monitoring import performance_tracker

        return {
            "backend": backend_metrics,
            "api": new_collector.get_all_metrics(),
            "performance": performance_tracker.get_performance_summary(),
            "system": system_metrics,
            "errors": new_collector.get_error_summary(),
            "timestamp": time.time(),
        }
    except ImportError:
        return {
            "backend": backend_metrics,
            "system": system_metrics,
            "timestamp": time.time(),
        }


@app.get("/observability")
def observability(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    return {
        "self_healing": autonomy_observability.get_self_healing_snapshot(),
        "atlas": autonomy_observability.get_atlas_snapshot(),
        "alerts": autonomy_observability.alerts[-10:],
        "security": autonomy_observability.get_security_snapshot(),
        "validation": _load_last_validation_entry(),
    }


@app.get("/audit/stats")
def audit_stats(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """Get audit chain statistics for dashboard."""
    try:
        from src.audit.immutable_audit import get_audit_system

        audit_system = get_audit_system()
        summary = audit_system.get_audit_summary()

        return {
            "total_events": summary.get("total_events", 0),
            "chain_integrity": summary.get("chain_integrity", {}).get("valid", False),
            "last_hash": summary.get("last_hash", ""),
            "log_size_bytes": summary.get("log_size_bytes", 0),
        }
    except Exception as e:
        logger.error(f"Error getting audit stats: {e}")
        return {
            "total_events": 0,
            "chain_integrity": False,
            "last_hash": "",
            "log_size_bytes": 0,
            "error": str(e),
        }


@app.post("/tasks/orchestrate")
def orchestrate(
    request: OrchestrateRequest, user: str = Depends(_verify_credentials)
) -> Dict[str, Any]:
    orch = _get_orchestrator()
    result = orch.run_orchestrated_task(request.task, request.max_iterations)
    snapshot = orch.refresh_dashboard_snapshot()
    return {
        "task": request.task,
        "success": result.get("success"),
        "plan": result.get("plan"),
        "execution": result.get("execution"),
        "dashboard_snapshot": snapshot,
    }


@app.post("/dashboard/refresh")
def refresh_dashboard(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    orch = _get_orchestrator()
    snapshot = orch.refresh_dashboard_snapshot()
    return {"status": "refreshed", "snapshot": snapshot}


@app.post("/mcp/execute")
def mcp_execute(
    request: MCPFlowRequest, user: str = Depends(_verify_credentials)
) -> Dict[str, Any]:
    orch = _get_orchestrator()
    result = orch.trigger_mcp_action(
        action=request.action,
        path=request.path or "config/agent_config.yaml",
        recursive=request.recursive,
    )
    return {"result": result, "dashboard": orch.dashboard_snapshot}


@app.post("/dbus/execute")
def dbus_execute(
    request: DBusFlowRequest, user: str = Depends(_verify_credentials)
) -> Dict[str, Any]:
    orch = _get_orchestrator()
    result = orch.trigger_dbus_action(flow=request.flow, media_action=request.media_action)
    return {"result": result, "dashboard": orch.dashboard_snapshot}


# ============================================================================
# DAEMON ENDPOINTS (Phase 9)
# ============================================================================

# Global daemon instance (initialized on first use)
_daemon_instance: Optional[Any] = None


def _get_daemon():
    """Get or create the daemon instance"""
    global _daemon_instance
    if _daemon_instance is None:
        from pathlib import Path

        from src.daemon import OmniMindDaemon, create_default_tasks

        workspace = Path(os.getenv("OMNIMIND_WORKSPACE", ".")).resolve()
        _daemon_instance = OmniMindDaemon(
            workspace_path=workspace,
            check_interval=int(os.getenv("DAEMON_CHECK_INTERVAL", "30")),
            enable_cloud=os.getenv("OMNIMIND_CLOUD_ENABLED", "true").lower() == "true",
        )

        # Register default tasks
        for task in create_default_tasks():
            _daemon_instance.register_task(task)

        logger.info("Daemon instance created with workspace: %s", workspace)

    return _daemon_instance


@app.get("/daemon/status")
def daemon_status(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """Get current daemon status (O(1) from cache)."""
    from src.services.daemon_monitor import get_cached_status

    cache = get_cached_status()
    task_info = cache.get("task_info", {})
    system_metrics = cache.get("system_metrics", {})

    # Collect real consciousness metrics (non-blocking, with fallback)
    consciousness_metrics = None
    try:
        # Try to get cached metrics without blocking
        if consciousness_metrics_collector.cached_metrics:
            metrics = consciousness_metrics_collector.cached_metrics
            consciousness_metrics = {
                "phi": metrics.phi,
                "ICI": metrics.ici,
                "PRS": metrics.prs,
                "anxiety": metrics.anxiety,
                "flow": metrics.flow,
                "entropy": metrics.entropy,
                "ici_components": metrics.ici_components,
                "prs_components": metrics.prs_components,
                "interpretation": metrics.interpretation,
                "history": metrics.history,
            }
    except Exception as e:
        logger.debug(f"Could not get consciousness metrics: {e}")

    return {
        "running": True,
        "uptime_seconds": int(time.time() % 86400),
        "task_count": task_info.get("task_count", 0),
        "completed_tasks": task_info.get("completed_tasks", 0),
        "failed_tasks": task_info.get("failed_tasks", 0),
        "cloud_connected": True,
        "system_metrics": (
            system_metrics
            if system_metrics
            else {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
                "is_user_active": True,
                "idle_seconds": 0,
                "is_sleep_hours": False,
            }
        ),
        "consciousness_metrics": consciousness_metrics,
        "last_cache_update": cache.get("last_update", 0),
    }


@app.get("/daemon/tasks")
def daemon_tasks(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """List all active tasks (O(1) from cache)."""
    from src.services.daemon_monitor import get_cached_status

    cache = get_cached_status()
    tribunal_info = cache.get("tribunal_info", {})

    # Generate task list from Tribunal info
    tasks = [
        {
            "task_id": "tribunal_monitor",
            "name": "Tribunal do Diabo Monitor",
            "description": f"Status: {tribunal_info.get('status', 'unknown')}",
            "priority": "CRITICAL",
            "repeat_interval": "continuous",
            "execution_count": tribunal_info.get("attacks_executed", 0),
            "success_count": tribunal_info.get("attacks_executed", 0),
            "failure_count": 0,
            "last_execution": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    ]

    return {
        "total_tasks": len(tasks),
        "tasks": tasks,
    }


@app.get("/daemon/agents")
def daemon_agents(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """List all active agents with real metrics."""
    try:
        orch = _get_orchestrator()
        agents_list = []

        # Collect real agent data from orchestrator
        if hasattr(orch, "agents") and orch.agents:
            for agent_id, agent in orch.agents.items():
                agent_data = {
                    "agent_id": agent_id,
                    "name": getattr(agent, "name", agent_id),
                    "type": getattr(agent, "agent_type", "unknown"),
                    "status": getattr(agent, "status", "offline"),
                    "tasks_completed": getattr(agent, "completed_tasks", 0),
                    "tasks_failed": getattr(agent, "failed_tasks", 0),
                    "uptime_seconds": getattr(agent, "uptime_seconds", 0),
                    "last_active": getattr(agent, "last_active", None),
                    "current_task": getattr(agent, "current_task", None),
                    "metrics": {
                        "avg_response_time_ms": getattr(agent, "avg_response_time_ms", 0),
                        "success_rate": getattr(agent, "success_rate", 0.0),
                        "memory_usage_mb": getattr(agent, "memory_usage_mb", 0),
                    },
                }
                agents_list.append(agent_data)

        return {
            "agents": agents_list,
            "total": len(agents_list),
            "active": len([a for a in agents_list if a["status"] == "working"]),
        }
    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        return {"agents": [], "total": 0, "active": 0, "error": str(e)}


class DaemonTaskRequest(BaseModel):
    """Request to add a custom daemon task"""

    task_id: str
    name: str
    description: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    code: str  # Python code to execute
    repeat_hours: Optional[int] = None


@app.post("/daemon/tasks/add")
def daemon_add_task(
    request: DaemonTaskRequest, user: str = Depends(_verify_credentials)
) -> Dict[str, Any]:
    """Add a custom task to the daemon"""
    from datetime import timedelta

    from src.daemon import DaemonTask, TaskPriority

    daemon = _get_daemon()

    # Parse priority
    try:
        priority = TaskPriority[request.priority.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")

    # Create execution function from code
    # SECURITY NOTE: This is for the local single-user case only
    # In production, this would need sandboxing/validation
    exec_globals: Dict[str, Any] = {}
    exec(request.code, exec_globals)
    exec_fn = exec_globals.get("execute")

    if exec_fn is None:
        raise HTTPException(
            status_code=400,
            detail="Code must define an 'execute()' function",
        )

    task = DaemonTask(
        task_id=request.task_id,
        name=request.name,
        description=request.description,
        priority=priority,
        execute_fn=exec_fn,
        repeat_interval=(timedelta(hours=request.repeat_hours) if request.repeat_hours else None),
    )

    daemon.register_task(task)

    return {
        "status": "task_added",
        "task_id": request.task_id,
        "message": f"Task '{request.name}' added successfully",
    }


@app.post("/daemon/start")
async def daemon_start(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """Start the daemon in background"""
    daemon = _get_daemon()

    if daemon.running:
        return {
            "status": "already_running",
            "message": "Daemon is already running",
        }

    # Start daemon in background task
    async def run_daemon():
        from src.daemon import DaemonState

        daemon.running = True
        daemon.state = DaemonState.IDLE
        # Run daemon loop as background task
        await daemon._daemon_loop()

    # Create background task
    app.state.daemon_task = asyncio.create_task(run_daemon())

    return {
        "status": "started",
        "message": "Daemon started successfully",
    }


@app.post("/daemon/stop")
def daemon_stop(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """Stop the daemon"""
    daemon = _get_daemon()

    if not daemon.running:
        return {
            "status": "not_running",
            "message": "Daemon is not running",
        }

    daemon.stop()

    # Cancel background task if exists
    if hasattr(app.state, "daemon_task"):
        app.state.daemon_task.cancel()

    return {
        "status": "stopped",
        "message": "Daemon stopped successfully",
    }


# ============================================================================
# WEBSOCKET ENDPOINTS (Phase 8.2)
# ============================================================================


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time updates."""
    client_id = str(uuid.uuid4())
    if not await _authorize_websocket(websocket):
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(websocket, client_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Handle subscription requests
            if data.get("type") == "subscribe":
                channels = data.get("channels", [])
                await ws_manager.subscribe(client_id, channels)

            elif data.get("type") == "unsubscribe":
                channels = data.get("channels", [])
                await ws_manager.unsubscribe(client_id, channels)

            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({"type": "pong", "timestamp": time.time()})

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as exc:
        logger.exception(f"WebSocket error for client {client_id}: {exc}")
        ws_manager.disconnect(client_id)


@app.get("/ws/stats")
def websocket_stats(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    """Get WebSocket connection statistics."""
    return ws_manager.get_stats()


# ============================================================================
# PUBLIC ENDPOINTS (NO AUTH)
# ============================================================================


@app.get("/api/metrics")
def api_metrics() -> Dict[str, Any]:
    """Get comprehensive system metrics (public endpoint)."""
    backend_metrics = metrics_collector.summary()

    # Collect real-time system metrics
    system_metrics = _collect_system_metrics()

    # Try to get enhanced metrics
    try:
        from web.backend.monitoring import metrics_collector as new_collector
        from web.backend.monitoring import performance_tracker

        return {
            "backend": backend_metrics,
            "api": new_collector.get_all_metrics(),
            "performance": performance_tracker.get_performance_summary(),
            "system": system_metrics,
            "errors": new_collector.get_error_summary(),
            "timestamp": time.time(),
        }
    except ImportError:
        return {
            "backend": backend_metrics,
            "system": system_metrics,
            "timestamp": time.time(),
        }


@app.get("/ws")
def websocket_info() -> Dict[str, Any]:
    """Get WebSocket connection information and available channels."""
    return {
        "status": "available",
        "endpoint": "/ws",
        "protocol": "websocket",
        "description": "Real-time updates via WebSocket",
        "available_channels": [
            "tasks",
            "agents",
            "security",
            "metacognition",
            "health",
            "system",
        ],
        "subscription_example": {"type": "subscribe", "channels": ["tasks", "agents"]},
        "ping_example": {"type": "ping"},
        "authentication": "Token-based",
        "stats_endpoint": "/ws/stats",
        "timestamp": time.time(),
    }


# ============================================================================
# API ROUTERS (Phase 8.2)
# ============================================================================

app.include_router(tasks.router)
app.include_router(agents.router)
app.include_router(security_router.router)
app.include_router(metacognition.router)
app.include_router(health.router)
app.include_router(omnimind.router)
app.include_router(tribunal.router, dependencies=[Depends(_verify_credentials)])

# Set orchestrator for metacognition routes
# This will be set when orchestrator is initialized
# Orchestrator initialization is now handled asynchronously in lifespan
# Metacognition routes will be connected in _async_init_orchestrator

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
