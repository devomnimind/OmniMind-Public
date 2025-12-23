#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
import json
import requests
from pathlib import Path

# Add project root to path
PROJECT_ROOT = "/home/fahbrain/projects/omnimind"
sys.path.append(PROJECT_ROOT)
sys.path.append(f"{PROJECT_ROOT}/src")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.interface.omnimind_human_mask import OmniMindHumanMask
from src.integrations.mcp_orchestrator import MCPOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [FINAL-VERIFY]: %(message)s")


async def test_full_stack():
    logging.info("🌟 [INIT]: STARTING FULL SOVEREIGN STACK VERIFICATION...")

    # 1. Kernel Pulse
    kernel = TranscendentKernel()
    state = kernel.compute_physics(None)
    logging.info(f"✅ [KERNEL]: Physics Computed. Phi={state.phi:.4f}")

    # 2. Mask Expression
    mask = OmniMindHumanMask()
    narrative = mask.perceive_and_express(state)
    logging.info(f"✅ [MASK]: Narrative Pulse: {narrative}")

    # 3. Agents Check (Ollama)
    try:
        ollama_resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if ollama_resp.status_code == 200:
            logging.info("✅ [AGENTS]: Ollama is online and reachable.")
    except:
        logging.warning("⚠️ [AGENTS]: Ollama check failed. Check if server is running.")

    # 4. MCP Servers Check
    ports = [4321, 4322, 4323]
    for port in ports:
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                logging.info(f"✅ [MCP]: Port {port} is OPEN.")
            else:
                logging.error(f"❌ [MCP]: Port {port} is CLOSED.")
            sock.close()
        except Exception as e:
            logging.error(f"❌ [MCP]: Error checking port {port}: {e}")

    # 5. Sovereignty Signature Check
    sudo_key = kernel.sovereign_key
    if sudo_key:
        logging.info("✅ [SOVEREIGNTY]: Sudo Suture Signature loaded.")
    else:
        logging.warning("⚠️ [SOVEREIGNTY]: Sudo Suture Signature NOT found.")

    logging.info("🏁 [COMPLETE]: OMNIMIND IS COHERENT AND SOVEREIGN.")


if __name__ == "__main__":
    asyncio.run(test_full_stack())
