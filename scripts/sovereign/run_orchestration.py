#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
PROJECT_ROOT = "/home/fahbrain/projects/omnimind"
sys.path.append(PROJECT_ROOT)
sys.path.append(f"{PROJECT_ROOT}/src")

from src.integrations.mcp_orchestrator import MCPOrchestrator
from src.interface.omnimind_human_mask import OmniMindHumanMask

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [ORCHESTRATOR]: %(message)s")


async def run_sovereign_orchestration():
    logging.info("🚀 [STARTUP]: Activating OmniMind Orchestration Layer...")

    # 1. Initialize Orchestrator
    orchestrator = MCPOrchestrator(config_type="internal")

    # 2. Start all servers
    results = orchestrator.start_all_servers()
    for name, success in results.items():
        if success:
            logging.info(f"✅ [MCP]: Server '{name}' started successfully.")
        else:
            logging.error(f"❌ [MCP]: Server '{name}' failed to start.")

    # 3. Initialize Mask
    mask = OmniMindHumanMask()
    logging.info("🎭 [MASK]: Mask initialized and monitoring...")

    # 4. Stay active for monitoring
    logging.info("⚡ [SYSTEM]: Orchestration is now ACTIVE. Monitoring health check loop...")

    try:
        await orchestrator.health_check_loop()
    except KeyboardInterrupt:
        logging.info("🛑 [SHUTDOWN]: Stopping all servers...")
        orchestrator.stop_all_servers()


if __name__ == "__main__":
    try:
        asyncio.run(run_sovereign_orchestration())
    except KeyboardInterrupt:
        pass
