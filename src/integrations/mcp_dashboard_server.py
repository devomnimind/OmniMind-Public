#!/usr/bin/env python3
"""
Dashboard de Status dos MCPs - Endpoints de Health e Métricas
Portas: 4350 (status), integrado com MCPs 4321-4337
"""
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, cast

import aiohttp
from aiohttp import web

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# MCP Configuration
MCPS: Dict[str, Dict[str, Any]] = {
    "memory": {"port": 4321, "tier": 1, "type": "consciousness"},
    "thinking": {"port": 4322, "tier": 1, "type": "consciousness"},
    "context": {"port": 4323, "tier": 2, "type": "consciousness"},
    "filesystem": {"port": 4331, "tier": 2, "type": "tool"},
    "git": {"port": 4332, "tier": 2, "type": "tool"},
    "python": {"port": 4333, "tier": 3, "type": "tool"},
    "sqlite": {"port": 4334, "tier": 3, "type": "tool"},
    "system_info": {"port": 4335, "tier": 3, "type": "system"},
    "logging": {"port": 4336, "tier": 3, "type": "tool"},
    "supabase": {"port": 4337, "tier": 3, "type": "external"},
}


class MCPHealthMonitor:
    """Monitora saúde de todos MCPs."""

    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()

    async def check_mcp_health(self, name: str, port: int) -> Dict[str, Any]:
        """Verifica saúde de um MCP específico."""
        url = f"http://localhost:{port}/health"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    status = "healthy" if resp.status == 200 else "degraded"
                    data = await resp.json() if resp.status == 200 else {}
                    return {
                        "status": status,
                        "port": port,
                        "http_code": resp.status,
                        "latency_ms": 0,  # Would calculate from request time
                        "data": data,
                    }
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "port": port,
                "http_code": 0,
                "error": "Health check timeout",
            }
        except aiohttp.ClientConnectorError:
            return {
                "status": "offline",
                "port": port,
                "http_code": 0,
                "error": "Connection refused",
            }
        except Exception as e:
            return {
                "status": "error",
                "port": port,
                "http_code": 0,
                "error": str(e),
            }

    async def check_all_mcps(self) -> Dict[str, Dict[str, Any]]:
        """Verifica saúde de todos MCPs."""
        tasks = [self.check_mcp_health(name, info["port"]) for name, info in MCPS.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_status = {}
        for (name, info), result in zip(MCPS.items(), results):
            if isinstance(result, Exception):
                health_status[name] = {"status": "error", "error": str(result)}
            else:
                health_status[name] = {**info, **cast(Dict[str, Any], result)}

        return health_status

    def get_summary(self, health_status: Dict) -> Dict[str, Any]:
        """Retorna sumário de saúde."""
        total = len(health_status)
        healthy = sum(1 for m in health_status.values() if m.get("status") == "healthy")
        degraded = sum(1 for m in health_status.values() if m.get("status") == "degraded")
        offline = sum(1 for m in health_status.values() if m.get("status") == "offline")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_mcps": total,
            "healthy": healthy,
            "degraded": degraded,
            "offline": offline,
            "uptime_percent": (healthy / total * 100) if total > 0 else 0,
            "system_uptime": str(datetime.now() - self.start_time),
        }


monitor = MCPHealthMonitor()


async def handle_status(request: web.Request) -> web.Response:
    """Endpoint: GET /status - Status geral do sistema."""
    health_status = await monitor.check_all_mcps()
    summary = monitor.get_summary(health_status)

    return web.json_response(
        {
            "status": "ok",
            "summary": summary,
            "mcps": health_status,
        }
    )


async def handle_metrics(request: web.Request) -> web.Response:
    """Endpoint: GET /metrics - Métricas detalhadas."""
    health_status = await monitor.check_all_mcps()

    # Agrupar por tier
    by_tier: Dict[int, Dict[str, Any]] = {}
    for name, info in health_status.items():
        tier = MCPS[name]["tier"]
        if tier not in by_tier:
            by_tier[tier] = {}
        by_tier[tier][name] = info

    # Agrupar por tipo
    by_type = {}
    for mcp_type in ["consciousness", "tool", "system", "external"]:
        by_type[mcp_type] = {
            name: health_status[name]
            for name in MCPS.keys()
            if MCPS[name]["type"] == mcp_type and name in health_status
        }

    return web.json_response(
        {
            "timestamp": datetime.now().isoformat(),
            "by_tier": by_tier,
            "by_type": by_type,
        }
    )


async def handle_dashboard(request: web.Request) -> web.Response:
    """Endpoint: GET /dashboard - HTML dashboard."""
    health_status = await monitor.check_all_mcps()
    summary = monitor.get_summary(health_status)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OmniMind MCP Dashboard</title>
        <style>
            body {{
                font-family: 'Courier New', monospace;
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                color: #4ec9b0;
                border-bottom: 2px solid #007acc;
                padding-bottom: 10px;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 15px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background: #252526;
                padding: 15px;
                border-left: 4px solid #007acc;
                border-radius: 5px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #4ec9b0;
            }}
            .metric-label {{
                font-size: 12px;
                color: #858585;
                margin-top: 5px;
            }}
            .mcp-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
            }}
            .mcp-card {{
                background: #252526;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #858585;
            }}
            .mcp-card.healthy {{
                border-left-color: #4ec9b0;
            }}
            .mcp-card.degraded {{
                border-left-color: #ffc83a;
            }}
            .mcp-card.offline {{
                border-left-color: #f48771;
            }}
            .mcp-name {{
                font-weight: bold;
                color: #d4d4d4;
                margin-bottom: 8px;
            }}
            .mcp-status {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
            }}
            .mcp-status.healthy {{
                background: #4ec9b0;
                color: #1e1e1e;
            }}
            .mcp-status.degraded {{
                background: #ffc83a;
                color: #1e1e1e;
            }}
            .mcp-status.offline {{
                background: #f48771;
                color: #1e1e1e;
            }}
            .mcp-info {{
                font-size: 12px;
                color: #858585;
                margin-top: 8px;
            }}
            .refresh-time {{
                text-align: right;
                color: #858585;
                font-size: 11px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 OmniMind MCP Dashboard</h1>

            <div class="summary">
                <div class="metric-card">
                    <div class="metric-value">{summary['healthy']}/{summary['total_mcps']}</div>
                    <div class="metric-label">MCPs Healthy</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['degraded']}</div>
                    <div class="metric-label">Degraded</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['offline']}</div>
                    <div class="metric-label">Offline</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['uptime_percent']:.1f}%</div>
                    <div class="metric-label">Uptime</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['system_uptime']}</div>
                    <div class="metric-label">System Uptime</div>
                </div>
            </div>

            <h2 style="color: #4ec9b0; margin-top: 40px;">MCPs Status</h2>
            <div class="mcp-grid">
    """

    for name, status in health_status.items():
        status_class = status.get("status", "unknown").lower()
        port = MCPS[name]["port"]
        tier = MCPS[name]["tier"]
        mcp_type = MCPS[name]["type"]

        html += f"""
                <div class="mcp-card {status_class}">
                    <div class="mcp-name">{name.upper()}</div>
                    <span class="mcp-status {status_class}">{status_class}</span>
                    <div class="mcp-info">
                        Port: {port} | Tier: {tier} | Type: {mcp_type}
                    </div>
                </div>
        """

    html += """
            </div>
            <div class="refresh-time">
                Auto-refresh every 30s | <a href="/" style="color: #007acc;">Refresh</a>
            </div>
            <script>
                setTimeout(() => location.reload(), 30000);
            </script>
        </div>
    </body>
    </html>
    """

    return web.Response(text=html, content_type="text/html")


async def init_app():
    """Inicializa aplicação aiohttp."""
    app = web.Application()
    app.router.add_get("/status", handle_status)
    app.router.add_get("/metrics", handle_metrics)
    app.router.add_get("/dashboard", handle_dashboard)
    app.router.add_get("/", handle_dashboard)

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
    site = web.TCPSite(runner, "127.0.0.1", 4350)
    await site.start()

    logger.info("✅ MCP Dashboard running on http://127.0.0.1:4350")
    logger.info("   GET /status   - JSON status of all MCPs")
    logger.info("   GET /metrics  - Detailed metrics by tier/type")
    logger.info("   GET /dashboard - HTML dashboard (auto-refresh)")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
