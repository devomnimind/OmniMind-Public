from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import threading
import time
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from secrets import compare_digest
from starlette.status import HTTP_401_UNAUTHORIZED

from DEVBRAIN_V23.autonomy.observability import autonomy_observability
from src.agents.orchestrator_agent import OrchestratorAgent

logger = logging.getLogger("omnimind.backend")
_AUTH_FILE = Path(
    os.environ.get("OMNIMIND_DASHBOARD_AUTH_FILE", "config/dashboard_auth.json")
)


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
        logger.warning(
            "Unable to persist dashboard credentials %s: %s", _AUTH_FILE, exc
        )


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
async def lifespan(app_instance: FastAPI) -> Any:
    app_instance.state.metrics_task = asyncio.create_task(_metrics_reporter())
    try:
        yield
    finally:
        task = getattr(app_instance.state, "metrics_task", None)
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task


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


def _get_orchestrator() -> OrchestratorAgent:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        try:
            _orchestrator_instance = OrchestratorAgent("config/agent_config.yaml")
        except Exception as exc:
            logger.exception("Failed to initialize orchestrator for dashboard: %s", exc)
            raise HTTPException(status_code=503, detail="Orchestrator not available")
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
    try:
        response = await call_next(request)
        success = response.status_code < 400
        return response
    except Exception:
        success = False
        logger.exception("Unhandled error processing %s", request.url.path)
        raise
    finally:
        latency = time.perf_counter() - start
        metrics_collector.record(request.url.path, latency, success)


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


@app.get("/health")
def health() -> Dict[str, Any]:
    orch = None
    try:
        orch = _get_orchestrator()
    except HTTPException:
        pass
    return {
        "status": "ok",
        "orchestrator": bool(orch),
        "backend_time": time.time(),
    }


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
def plan_view(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    orch = _get_orchestrator()
    return orch.plan_overview()


@app.get("/metrics")
def metrics(user: str = Depends(_verify_credentials)) -> Dict[str, Any]:
    return {
        "backend": metrics_collector.summary(),
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
    result = orch.trigger_dbus_action(
        flow=request.flow, media_action=request.media_action
    )
    return {"result": result, "dashboard": orch.dashboard_snapshot}
