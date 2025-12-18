#!/usr/bin/env python3
"""
Health Check Endpoint para OmniMind MCPs
Verifica status de todos serviços e retorna JSON
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import aiohttp
from aiohttp import web

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# MCPs para verificar
MCPS_HEALTH_CHECK = {
    4321: "memory",
    4322: "thinking",
    4323: "context",
    4331: "filesystem",
    4332: "git",
    4333: "python",
    4334: "sqlite",
    4335: "system_info",
    4336: "logging",
    4337: "supabase",
}

START_TIME = time.time()


async def check_single_mcp(port: int) -> Dict[str, Any]:
    """Verifica status de um único MCP."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://127.0.0.1:{port}/health",
                timeout=aiohttp.ClientTimeout(total=2),
            ) as resp:
                return {
                    "status": "up" if resp.status == 200 else "degraded",
                    "code": resp.status,
                    "timestamp": datetime.now().isoformat(),
                }
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "code": 0,
            "error": "Health check timeout",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "down",
            "code": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def handle_health(request: web.Request) -> web.Response:
    """Endpoint: GET /health - Health check do sistema."""
    tasks = [check_single_mcp(port) for port in MCPS_HEALTH_CHECK.keys()]
    results = await asyncio.gather(*tasks)

    health_status = {}
    for (port, name), result in zip(MCPS_HEALTH_CHECK.items(), results):
        health_status[f"{name}_{port}"] = result

    # Calcular status geral
    up_count = sum(1 for r in results if r["status"] == "up")
    total_count = len(results)

    overall_status = "healthy" if up_count == total_count else "degraded"

    return web.json_response(
        {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(time.time() - START_TIME),
            "mcps_up": up_count,
            "mcps_total": total_count,
            "mcps": health_status,
        }
    )


async def handle_ready(request: web.Request) -> web.Response:
    """Endpoint: GET /ready - Readiness check (Kubernetes)."""
    tasks = [check_single_mcp(port) for port in MCPS_HEALTH_CHECK.keys()]
    results = await asyncio.gather(*tasks)

    up_count = sum(1 for r in results if r["status"] == "up")
    total_count = len(results)

    # Pronto se pelo menos 80% dos MCPs estão up
    is_ready = up_count / total_count >= 0.80

    if is_ready:
        return web.json_response({"ready": True}, status=200)
    else:
        return web.json_response(
            {"ready": False, "reason": f"Only {up_count}/{total_count} MCPs up"},
            status=503,
        )


async def init_app():
    """Inicializa aplicação aiohttp."""
    app = web.Application()
    app.router.add_get("/health", handle_health)
    app.router.add_get("/ready", handle_ready)
    return app


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 4360)
    await site.start()

    logger.info("✅ OmniMind Health Check Server running on http://127.0.0.1:4360")
    logger.info("   GET /health  - Full health status")
    logger.info("   GET /ready   - Readiness check (K8s compatible)")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
