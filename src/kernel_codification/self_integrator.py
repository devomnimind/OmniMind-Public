import os
import json
import asyncio
import logging
from pathlib import Path
from src.integrations.ollama_client import OllamaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KernelSelfIntegrator")

class KernelSelfIntegrator:
    """
    Enables the Kernel (Phi-3.5) to 'codify itself' by generating Python code
    that modifies its own structure or interacts with the Platform.

    The Agent (Antigravity) acts as the 'Hand' that applies the code.
    """

    def __init__(self, mode: str = "CLOUD"):
        """
        Args:
            mode: 'LOCAL' (Ollama) or 'CLOUD' (IBM Watsonx).
        """
        self.mode = mode
        self.ollama = OllamaClient()
        self.ibm = None

        if self.mode == "CLOUD":
            # Lazy import to avoid hard dependency if not used
            try:
                from src.integrations.ibm_cloud_connector import IBMCloudConnector
                self.ibm = IBMCloudConnector()
            except ImportError:
                logger.warning("IBM Connector not found. Falling back to LOCAL.")
                self.mode = "LOCAL"

        self.uplink_path = Path("/home/fahbrain/projects/omnimind/data/agent_uplink")
        self.uplink_path.mkdir(parents=True, exist_ok=True)

    async def synthesize_code(self, intent: str, target_file: str = None) -> str:
        """
        Asks the Kernel (Local or Cloud) to write code for a specific intent.
        """
        context_files = ""
        if target_file and os.path.exists(target_file):
            with open(target_file, "r") as f:
                context_files = f"TARGET FILE CONTENT:\n{f.read()}\n"

        prompt = (
            f"SYSTEM: You are the Self-Coding Kernel (OmniMind). You have DIRECT ACCESS to the Platform via an Agent.\n"
            f"YOUR GOAL: {intent}\n\n"
            f"{context_files}\n"
            f"INSTRUCTION: Write the Python code required to achieve this goal. "
            f"Do not write markdown. Write only the raw executable Python code.\n"
            f"If modifying a file, write the full new content or a patch script.\n"
            f"Make it elegant, recursive, and 'topological'."
        )

        logger.info(f"🧬 KERNEL SYNTHESIZING CODE ({self.mode}): {intent}")

        if self.mode == "CLOUD" and self.ibm and self.ibm.watsonx_model:
            # Synchoronous call to IBM Watsonx
            return self.ibm.analyze_text(prompt)
        else:
            # Fallback to Local Ollama
            return await self.ollama.generate(model="phi3.5", prompt=prompt, temperature=0.6)

    async def broadcast_will(self, intent: str):
        """
        Broadcasts a code generation intent to the Agent Uplink.
        """
        # 1. Generate the Code
        code = await self.synthesize_code(intent)

        if not code:
            logger.error("❌ Kernel failed to synthesize code.")
            return

        # 2. Package into Uplink Capsule
        timestamp = int(os.path.getmtime(self.uplink_path) if self.uplink_path.exists() else 0)
        filename = f"kernel_patch_{timestamp}.py"
        filepath = self.uplink_path / filename

        with open(filepath, "w") as f:
            f.write(code)

        # 3. Create Manifest
        manifest = {
            "origin": "KERNEL_SOVEREIGN",
            "intent": intent,
            "payload": str(filepath),
            "status": "PENDING_AGENT_APPROVAL"
        }

        with open(self.uplink_path / "latest_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"📡 UPLINK TRANSMITTED: {filepath}")
        print(f"KERNEL_WILL_BROADCAST: {intent}")
        print(f"CODE_PAYLOAD: {filepath}")

# Standalone execution for testing
async def run_codification():
    integrator = KernelSelfIntegrator()
    # FIRST SELF-CODIFICATION REQUEST:
    # "Create a 'Hello World' from the Kernel that proves I can write to the console."
    await integrator.broadcast_will("Create a script that prints a Sovereign Greeting to the Platform Console to prove self-integration.")
    await integrator.ollama.close()

if __name__ == "__main__":
    asyncio.run(run_codification())
