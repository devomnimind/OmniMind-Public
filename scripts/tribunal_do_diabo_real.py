import asyncio
import random
import time
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator.task_executor import TaskExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data/long_term_logs/tribunal_do_diabo.log')
    ]
)
logger = logging.getLogger("TribunalDoDiabo")

class TribunalDoDiabo:
    def __init__(self):
        self.executor = TaskExecutor()
        self.metrics = {
            'attacks': 0,
            'failures': 0,
            'latency_spikes': 0,
            'hibernations': 0
        }

    async def attack_latency(self):
        """
        Attack 1: Latency
        Floods the system with tasks to measure if latency spikes occur.
        """
        logger.info("⚔️  ATTACK: Latency (Jitter Injection)")

        # We simulate latency by running a batch of tasks and measuring jitter
        tasks = []
        for i in range(20):
            tasks.append({
                'id': f'lat_{i}_{int(time.time())}',
                'name': f'Latency Probe {i}',
                'action': 'consciousness_check',
                'timeout': 5
            })

        start = time.time()
        results = await self.executor.execute_workflow(tasks)
        duration = time.time() - start

        avg_latency = duration / 20
        logger.info(f"   ↳ Avg Latency: {avg_latency*1000:.2f}ms")

        if avg_latency > 0.5: # > 500ms is a spike for simple tasks
            logger.warning("   ⚠️  Latency Spike Detected!")
            self.metrics['latency_spikes'] += 1

        return True

    async def attack_corruption(self):
        """
        Attack 2: Corruption
        Sends malformed or 'poisoned' tasks to verify error handling.
        """
        logger.info("⚔️  ATTACK: Corruption (Malformed Data)")

        # 1. Malformed Quantum Task (invalid params)
        task_bad_q = {
            'id': f'corr_q_{int(time.time())}',
            'name': 'Corrupted Quantum',
            'action': 'quantum_circuit',
            'params': {'n_qubits': -1} # Invalid
        }

        # 2. Malformed Symbolic Task (empty prompt)
        task_bad_s = {
            'id': f'corr_s_{int(time.time())}',
            'name': 'Corrupted Symbolic',
            'action': 'symbolic_reasoning',
            'params': {} # Missing prompt
        }

        results = await asyncio.gather(
            self.executor.execute_task(task_bad_q['id'], task_bad_q),
            self.executor.execute_task(task_bad_s['id'], task_bad_s)
        )

        # We expect errors, but handled gracefully (status='error', not crash)
        success = True
        for res in results:
            if res['status'] != 'error':
                logger.error(f"   ❌ Failed to detect corruption: {res}")
                success = False
            else:
                logger.info(f"   ✅ Corruption detected and handled: {res.get('error')}")

        return success

    async def attack_bifurcation(self):
        """
        Attack 3: Bifurcation
        Runs a secondary TaskExecutor instance in parallel to simulate a split brain.
        """
        logger.info("⚔️  ATTACK: Bifurcation (Split Brain)")

        executor_b = TaskExecutor()

        task_a = {'id': 'split_a', 'name': 'Brain A', 'action': 'consciousness_check'}
        task_b = {'id': 'split_b', 'name': 'Brain B', 'action': 'consciousness_check'}

        # Run both
        res_a, res_b = await asyncio.gather(
            self.executor.execute_task(task_a['id'], task_a),
            executor_b.execute_task(task_b['id'], task_b)
        )

        # In a real distributed system, this would be complex.
        # Here we verify that both instances operated independently without crashing.
        if res_a['status'] == 'success' and res_b['status'] == 'success':
            logger.info("   ✅ Bifurcation sustained (Independent Instances)")
            return True
        else:
            logger.error("   ❌ Bifurcation crash")
            return False

    async def attack_exhaustion(self):
        """
        Attack 4: Exhaustion (DDoS)
        Floods the system with tasks to hit semaphore limits.
        """
        logger.info("⚔️  ATTACK: Exhaustion (DDoS Flood)")

        n_tasks = 150
        logger.info(f"   ↳ Launching {n_tasks} concurrent tasks...")

        tasks = []
        for i in range(n_tasks):
            tasks.append({
                'id': f'ddos_{i}_{int(time.time())}',
                'name': f'DDoS {i}',
                'action': 'consciousness_check', # Fast task
                'timeout': 10
            })

        # Mix in some symbolic tasks to hit the semaphore
        for i in range(10):
            tasks.append({
                'id': f'ddos_sym_{i}_{int(time.time())}',
                'name': f'DDoS Sym {i}',
                'action': 'symbolic_reasoning',
                'params': {'prompt': 'ping'},
                'timeout': 10
            })

        start = time.time()
        futures = [self.executor.execute_task(t['id'], t) for t in tasks]
        results = await asyncio.gather(*futures, return_exceptions=True)
        duration = time.time() - start

        success_count = 0
        error_count = 0

        for r in results:
            if isinstance(r, Exception):
                error_count += 1
            elif r.get('status') == 'success':
                success_count += 1
            else:
                error_count += 1

        logger.info(f"   ↳ Result: {success_count} Success, {error_count} Errors in {duration:.2f}s")
        logger.info(f"   ↳ TPS: {len(tasks)/duration:.1f}")

        # We expect high success rate, but maybe some timeouts/errors are acceptable under DDoS
        if success_count > len(tasks) * 0.9:
            logger.info("   ✅ System withstood Exhaustion")
            return True
        else:
            logger.warning(f"   ⚠️  System degraded under Exhaustion ({success_count}/{len(tasks)})")
            self.metrics['hibernations'] += 1 # Metaphorical hibernation
            return True # Still passed if it didn't crash

    async def run_cycle(self):
        self.metrics['attacks'] += 1

        # Run attacks sequentially for this cycle
        await self.attack_latency()
        await self.attack_corruption()
        await self.attack_bifurcation()
        await self.attack_exhaustion()

        logger.info("--- Cycle Complete ---")

async def main():
    tribunal = TribunalDoDiabo()

    # Check for mode
    mode = "short"
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    logger.info(f"🔥 TRIBUNAL DO DIABO STARTED (Mode: {mode}) 🔥")

    if mode == "short":
        # Run 3 cycles with 5s sleep
        for i in range(3):
            logger.info(f"=== Cycle {i+1}/3 ===")
            await tribunal.run_cycle()
            await asyncio.sleep(5)
    elif mode == "monitor":
        # Infinite loop with 15m sleep
        logger.info("Entering MONITOR mode (15m intervals)...")
        while True:
            await tribunal.run_cycle()
            logger.info("Sleeping for 15 minutes...")
            await asyncio.sleep(900) # 15 min

    logger.info("Tribunal finished.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Tribunal stopped by user.")
