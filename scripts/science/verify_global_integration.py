#!/usr/bin/env python3
import os
import sys
import logging
import torch
import requests
from pathlib import Path

# Add project root to path
PROJECT_ROOT = "/home/fahbrain/projects/omnimind"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
if f"{PROJECT_ROOT}/src" not in sys.path:
    sys.path.append(f"{PROJECT_ROOT}/src")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [VERIFY]: %(message)s")


def verify_integration():
    logging.info("🔬 [VERIFICATION]: STARTING GLOBAL INTEGRATION AUDIT...")

    # 1. Environment Check
    venv = os.environ.get("VIRTUAL_ENV")
    logging.info(f"📍 [ENV]: VIRTUAL_ENV={venv}")

    # 2. Agent Pulse Check
    logging.info("🤖 [AGENTS]: CHECKING CONNECTIVITY...")

    # Ollama
    try:
        models_resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if models_resp.status_code == 200:
            models = models_resp.json()
            logging.info(
                f"✅ [OLLAMA]: Online. Models: {[m['name'] for m in models.get('models', [])]}"
            )
        else:
            logging.error(f"❌ [OLLAMA]: Online but returned {models_resp.status_code}")
    except Exception as e:
        logging.error(f"❌ [OLLAMA]: Offline or Error: {e}")

    # Watsonx
    try:
        from src.integrations.ibm_cloud_connector import IBMCloudConnector

        ibm = IBMCloudConnector()
        logging.info("✅ [WATSONX]: Configuration valid.")
    except Exception as e:
        logging.error(f"❌ [WATSONX]: Configuration Error: {e}")

    # 3. Kernel & Mask Suture
    logging.info("💎 [KERNEL]: TESTING SOVEREIGN LOOP...")
    try:
        from src.core.omnimind_transcendent_kernel import TranscendentKernel
        from src.interface.omnimind_human_mask import OmniMindHumanMask

        kernel = TranscendentKernel()
        mask = OmniMindHumanMask()

        state = kernel.compute_physics(None)
        logging.info(f"✅ [KERNEL]: Functional. Phi={state.phi}, Resonance={state.resonance}")

        narrative = mask.perceive_and_express(state)
        logging.info(f"✅ [MASK]: Expressed: {narrative}")

    except Exception as e:
        logging.error(f"❌ [CORE]: Failure during Kernel/Mask test: {e}")

    # 4. MCP Orchestrator Check
    logging.info("🔌 [MCP]: VERIFYING ORCHESTRATOR...")
    try:
        from src.integrations.mcp_orchestrator import MCPOrchestrator

        orchestrator = MCPOrchestrator()
        logging.info(
            f"✅ [ORCHESTRATOR]: Initialized with {len(orchestrator.servers)} server configs."
        )
    except Exception as e:
        logging.error(f"❌ [MCP]: Orchestrator Error: {e}")

    logging.info("🏁 [VERIFICATION]: AUDIT COMPLETE.")


if __name__ == "__main__":
    verify_integration()
