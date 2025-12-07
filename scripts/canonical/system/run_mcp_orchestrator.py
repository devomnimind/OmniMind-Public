"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Add project root to python path
# Script está em scripts/canonical/system/, então project_root é 3 níveis acima
script_path = Path(__file__).resolve()
project_root = script_path.parents[3]  # scripts -> canonical -> system -> project_root
if not (project_root / "src").exists():
    # Fallback: tentar 2 níveis (se estiver em scripts/)
    project_root = script_path.parents[2]
if not (project_root / "src").exists():
    # Fallback final: usar diretório atual
    project_root = Path.cwd()
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from src.integrations.mcp_orchestrator import MCPOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp_runner")


async def main():
    orchestrator = MCPOrchestrator()

    # Start servers
    orchestrator.start_all_servers()

    # Handle shutdown signals
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Received shutdown signal")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    # Run health check loop in background
    health_task = asyncio.create_task(orchestrator.health_check_loop())

    # Wait for stop signal
    await stop_event.wait()

    # Cleanup
    health_task.cancel()
    orchestrator.stop_all_servers()
    logger.info("MCP Orchestrator stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
