#!/usr/bin/env python3
"""
Teste de integração Tier 3: Dashboard de Status
Validação: endpoints, métrica de saúde, HTML rendering
"""
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.integrations.mcp_dashboard_server import (  # noqa: E402
    MCPS,
    MCPHealthMonitor,
    handle_dashboard,
    handle_metrics,
    handle_status,
)


class TestDashboardImports:
    """Testa imports do Dashboard."""

    def test_imports_successfully(self):
        """Verifica se todos imports funcionam."""
        assert MCPHealthMonitor is not None
        assert MCPS is not None
        assert handle_status is not None
        assert handle_metrics is not None
        assert handle_dashboard is not None


class TestMCPHealthMonitor:
    """Testa Monitor de Saúde dos MCPs."""

    def test_monitor_instantiation(self):
        """Testa criação de instância do Monitor."""
        monitor = MCPHealthMonitor()
        assert monitor is not None
        assert monitor.start_time is not None
        assert len(monitor.metrics) == 0

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Async timeout measurement by system monitor")
    async def test_check_mcp_health_offline(self):
        """Testa check quando MCP está offline (timeouts são normais em testes)."""
        monitor = MCPHealthMonitor()
        # Testa com timeout esperado
        result = await monitor.check_mcp_health("test_mcp", 9999)

        assert result is not None
        assert "status" in result
        assert result["port"] == 9999
        # Status esperado pode ser offline, timeout, ou error
        assert result["status"] in ["offline", "error", "timeout"]

    @pytest.mark.asyncio
    async def test_check_all_mcps(self):
        """Testa check de todos MCPs."""
        monitor = MCPHealthMonitor()
        result = await monitor.check_all_mcps()

        assert isinstance(result, dict)
        assert len(result) == len(MCPS)
        for name in MCPS.keys():
            assert name in result

    def test_get_summary(self):
        """Testa geração de sumário."""
        monitor = MCPHealthMonitor()
        health_status = {
            "memory": {"status": "healthy"},
            "thinking": {"status": "degraded"},
            "context": {"status": "offline"},
        }

        summary = monitor.get_summary(health_status)

        assert summary["total_mcps"] == 3
        assert summary["healthy"] == 1
        assert summary["degraded"] == 1
        assert summary["offline"] == 1
        assert isinstance(summary["uptime_percent"], float)


class TestDashboardEndpoints:
    """Testa endpoints do Dashboard."""

    @pytest.mark.asyncio
    async def test_handle_status_returns_json(self):
        """Testa se /status retorna JSON válido."""
        mock_request = MagicMock()

        with patch("src.integrations.mcp_dashboard_server.monitor") as mock_monitor:
            mock_monitor.check_all_mcps = AsyncMock(
                return_value={
                    "memory": {"status": "healthy", "port": 4321},
                }
            )
            mock_monitor.get_summary = MagicMock(
                return_value={
                    "total_mcps": 1,
                    "healthy": 1,
                    "degraded": 0,
                    "offline": 0,
                    "uptime_percent": 100.0,
                }
            )

            response = await handle_status(mock_request)

            assert response.status == 200
            body = response.body
            assert body is not None
            data = json.loads(body.decode())
            assert isinstance(data, dict)
            assert data.get("status") == "ok"
            assert "summary" in data
            assert "mcps" in data

    @pytest.mark.asyncio
    async def test_handle_metrics_returns_by_tier(self):
        """Testa se /metrics retorna dados por tier."""
        mock_request = MagicMock()

        with patch("src.integrations.mcp_dashboard_server.monitor") as mock_monitor:
            mock_monitor.check_all_mcps = AsyncMock(
                return_value={
                    "memory": {"status": "healthy", "port": 4321},
                    "thinking": {"status": "healthy", "port": 4322},
                }
            )

            response = await handle_metrics(mock_request)

            assert response.status == 200
            body = response.body
            assert body is not None
            data = json.loads(body.decode())
            assert "by_tier" in data
            assert "by_type" in data
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_handle_dashboard_returns_html(self):
        """Testa se /dashboard retorna HTML."""
        mock_request = MagicMock()

        with patch("src.integrations.mcp_dashboard_server.monitor") as mock_monitor:
            mock_monitor.check_all_mcps = AsyncMock(
                return_value={
                    "memory": {"status": "healthy", "port": 4321},
                }
            )
            mock_monitor.get_summary = MagicMock(
                return_value={
                    "total_mcps": 1,
                    "healthy": 1,
                    "degraded": 0,
                    "offline": 0,
                    "uptime_percent": 100.0,
                    "system_uptime": "00:05:00",
                }
            )

            response = await handle_dashboard(mock_request)

            assert response.status == 200
            assert "text/html" in str(response.content_type)
            html = response.text
            assert html is not None
            assert "OmniMind MCP Dashboard" in str(html)
            assert "MCPs Status" in str(html)


class TestMCPConfiguration:
    """Testa configuração de MCPs."""

    def test_mcps_configuration_complete(self):
        """Verifica se todos MCPs têm configuração."""
        required_keys = {"port", "tier", "type"}

        for name, info in MCPS.items():
            assert all(key in info for key in required_keys), f"Missing keys in {name}"
            assert isinstance(info["port"], int)
            assert isinstance(info["tier"], int)
            assert info["type"] in ["consciousness", "tool", "system", "external"]

    def test_mcps_ports_unique(self):
        """Verifica se portas são únicas."""
        ports = [info["port"] for info in MCPS.values()]
        assert len(ports) == len(set(ports)), "Duplicate ports found"

    def test_mcps_tiers_valid(self):
        """Verifica se tiers são válidos."""
        for name, info in MCPS.items():
            assert info["tier"] in [1, 2, 3], f"Invalid tier for {name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
