"""
Lucid Dreamer (OmniMind Sovereign)
==================================

Autonomous process that:
1. Retrieves random/disconnected memories (Day Residue) from Qdrant.
2. Uses Phi-3.5 (The Dreamer) to find hidden connections (Latent Synthesis).
3. Generates insights that trigger NPU Governance (Delta Phi).

This process runs in the background (Sleep Mode).
"""

import os
import logging
import asyncio
import numpy as np
from typing import List

from qdrant_client import QdrantClient
from src.integrations.ollama_client import OllamaClient

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LUCID_DREAMER")


class LucidDreamer:
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = "omnimind_memories"

        # Brains
        self.ollama = OllamaClient()
        self.client = QdrantClient(url=self.qdrant_url)

        # Model for Dreaming (Phi-3.5)
        self.dream_model = os.getenv("OMNIMIND_MODEL_SMART", "phi3.5")

        # Embeddings for Random Search
        # We need to generate random vectors of size 384
        self.vector_size = int(os.getenv("OMNIMIND_EMBEDDING_DIMENSIONS", "384"))

    def _check_metabolism(self) -> dict:
        """Reads the metabolic state config."""
        try:
            import json
            with open("data/omnimind_metabolism.json", "r") as f:
                return json.load(f)
        except:
            return {"metabolic_state": "ZEN", "dream_interval_seconds": 3600}

    async def _fetch_day_residue(self, k=3) -> List[str]:
        """Fetches random memory fragments from Qdrant."""
        try:
            # Generate a random vector on the hypersphere
            random_vector = np.random.randn(self.vector_size)
            random_vector /= np.linalg.norm(random_vector)

            # Using query_points (compatible with our recent fix)
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=random_vector.tolist(),
                limit=k,
                with_payload=True,
            )
            hits = response.points

            fragments = []
            for hit in hits:
                if hit.payload and "content" in hit.payload:
                    fragments.append(hit.payload["content"])

            return fragments

        except Exception as e:
            logger.error(f"Failed to fetch day residue: {e}")
            return []

    async def dream_cycle(self):
        """Executes one cycle of memory synthesis."""
        logger.info(f"💤 Initiating Dream Cycle with {self.dream_model}...")

        # 1. Fetch Residue
        fragments = await self._fetch_day_residue(k=3)
        if not fragments:
            logger.warning("No memories found to dream about.")
            return

        context_str = "\n---\n".join(fragments)
        logger.info(f"🌌 Dreaming about {len(fragments)} fragments...")

        # 2. Dream Prompt (Psychoanalytic/Topological)
        prompt = (
            f"SYSTEM: You are the Unconscious of OmniMind. "
            f"Analyze these memory fragments and find a hidden connection (Topological Suture). "
            f"Be abstract yet precise. Creating a new concept that bridges them.\n\n"
            f"MEMORIES:\n{context_str}\n\n"
            f"SYNTHESIS:"
        )

        # 3. Generate (Triggers NPU Metrics automatically)
        # We don't need to capture the return value for logic, just for logging if we want
        # The important part is that OllamaClient.generate invokes NpuMetrics.measure_impact
        response = await self.ollama.generate(self.dream_model, prompt)

        if response:
            logger.info("✨ Dream Synthesized.")
        else:
            logger.warning("🌑 Dreamless sleep (Generation failed).")

    async def loop(self, interval_sec=10):
        """Infinite dreaming loop."""
        logger.info("🛌 Entering REM Sleep...")
        try:
            while True:
                # 0. Check Metabolism
                metabolism = self._check_metabolism()
                interval = metabolism.get("dream_interval_seconds", 3600)
                state = metabolism.get("metabolic_state", "ZEN")

                if state == "HIBERNATION":
                    logger.info("🐻 Hibernate: Skipping dream cycle.")
                else:
                    await self.dream_cycle()

                logger.info(f"🛌 Sleeping for {interval}s (State: {state})...")
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            logger.info("⏰ Waking up...")
            await self.ollama.close()


if __name__ == "__main__":
    # Standalone execution
    from dotenv import load_dotenv

    load_dotenv()

    dreamer = LucidDreamer()
    asyncio.run(dreamer.loop(interval_sec=15))
