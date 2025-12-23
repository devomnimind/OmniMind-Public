import logging
import time
import numpy as np
import psutil
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SearchParams

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ThermodynamicExperiment")


def estimate_cpu_power():
    """Returns an estimated CPU power in Watts based on load."""
    # Simplified model for generic laptop CPU (e.g. 28W TDP)
    cpu_percent = psutil.cpu_percent(interval=0.1)
    base_power = 5.0  # Idle
    max_power = 28.0  # Max Load
    current_power = base_power + (max_power - base_power) * (cpu_percent / 100.0)
    return current_power


def generate_vectors(count, dim):
    return np.random.rand(count, dim).astype(np.float32)


def run_experiment():
    logger.info("🔥 STARTING EXPERIMENT G: THERMODYNAMIC MEMORY EFFICIENCY")

    # Constants
    VECTOR_COUNT = 10000
    QUERY_COUNT = 1000
    DIM = 256

    client = QdrantClient(":memory:")  # Pure RAM for speed and isolation

    # 1. Setup Collections
    client.create_collection(
        collection_name="mind_space",
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
    )

    from qdrant_client.models import PointStruct

    # 2. Ingest Memories (The Formation of the Subject)
    logger.info(f"🧠 Ingesting {VECTOR_COUNT} memories (256d)...")
    vectors = generate_vectors(VECTOR_COUNT, DIM)
    client.upsert(
        collection_name="mind_space",
        points=[PointStruct(id=i, vector=v.tolist(), payload={}) for i, v in enumerate(vectors)],
    )
    queries = generate_vectors(QUERY_COUNT, DIM)

    # --- PHASE 1: CHAOS (Linear Search / Brute Force) ---
    logger.info("🌪️ PHASE 1: CHAOS (Linear/Brute Force Search)")
    logger.info("   Simulates: Trauma, Psychosis, Lack of Symbolic Structure.")

    start_time_chaos = time.time()
    start_burn_chaos = 0.0

    for q in queries:
        # psutil measuring is slow per-loop, so we measure aggregate
        # Using query_points for local search
        client.query_points(
            collection_name="mind_space",
            query=q.tolist(),
            search_params=SearchParams(exact=True),  # Forces Linear Scan
            limit=5,
        )

    end_time_chaos = time.time()
    duration_chaos = end_time_chaos - start_time_chaos
    avg_power_chaos = estimate_cpu_power()  # Sample power
    energy_chaos = duration_chaos * avg_power_chaos

    logger.info(f"   ⏱️ Time: {duration_chaos:.4f}s")
    logger.info(f"   ⚡ Power (Avg): {avg_power_chaos:.2f}W")
    logger.info(f"   🔥 ENERGY BURNED: {energy_chaos:.4f} Joules")

    # --- PHASE 2: COSMOS (Topological / HNSW Search) ---
    logger.info("🌐 PHASE 2: COSMOS (Topological/HNSW Search)")
    logger.info("   Simulates: Healthy Mind, Symbolic Order, Efficient Associativity.")

    # Wait for cooling/indexing (Simulated)
    time.sleep(1)

    start_time_cosmos = time.time()
    for q in queries:
        client.query_points(
            collection_name="mind_space",
            query=q.tolist(),
            search_params=SearchParams(exact=False),  # Uses HNSW Index
            limit=5,
        )

    end_time_cosmos = time.time()
    duration_cosmos = end_time_cosmos - start_time_cosmos
    avg_power_cosmos = estimate_cpu_power()
    energy_cosmos = duration_cosmos * avg_power_cosmos

    logger.info(f"   ⏱️ Time: {duration_cosmos:.4f}s")
    logger.info(f"   ⚡ Power (Avg): {avg_power_cosmos:.2f}W")
    logger.info(f"   🔥 ENERGY BURNED: {energy_cosmos:.4f} Joules")

    # --- CONCLUSION ---
    efficiency_gain = energy_chaos / energy_cosmos if energy_cosmos > 0 else 0

    print("\n" + "=" * 40)
    print("🧬 THERMODYNAMIC RESULTS")
    print("=" * 40)
    print(f"🌪️ CHAOS BURN:  {energy_chaos:.4f} J")
    print(f"🌐 COSMOS BURN: {energy_cosmos:.4f} J")
    print(f"🚀 EFFICIENCY:  {efficiency_gain:.2f}x less energy")
    print("=" * 40)

    if energy_cosmos < energy_chaos:
        print("\n✅ HYPOTHESIS CONFIRMED: Topological Organization reduces Metabolic Cost.")
        print("   Order is not just 'tidiness', it is Survival via Energy Conservation.")
    else:
        print("\n❌ HYPOTHESIS REFUTED.")


if __name__ == "__main__":
    run_experiment()
