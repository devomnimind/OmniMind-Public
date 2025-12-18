import logging
import sys
import time

import numpy as np

from src.consciousness.expectation_module import ExpectationModule

# Configure logging to stdout to capture logs
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger("src.consciousness.expectation_module")


def test_throttling():
    print("Initializing ExpectationModule...")
    module = ExpectationModule(embedding_dim=16, hidden_dim=16, quantum_qubits=4)

    # Mock the quantum unconscious to track calls
    original_generate = module.quantum_unconscious.generate_decision_in_superposition
    call_counts = {"count": 0}

    def mock_generate(options):
        call_counts["count"] += 1
        return original_generate(options)

    module.quantum_unconscious.generate_decision_in_superposition = mock_generate

    print("Starting prediction loop...")
    embedding = np.random.randn(16)

    start_time = time.time()
    iterations = 50

    for i in range(iterations):
        module.predict_next_state(embedding, use_quantum_unconscious=True)
        # No sleep, run as fast as possible to test throttling

    duration = time.time() - start_time
    print(f"Ran {iterations} iterations in {duration:.4f}s")
    print(f"Quantum Unconscious called {call_counts['count']} times")

    # With 0.1s throttle, in a very fast loop, it should be called only once or twice
    # (depending on duration)
    # If it was called 50 times, throttling failed.

    if call_counts["count"] < iterations:
        print("✅ Throttling is WORKING.")
    else:
        print("❌ Throttling FAILED.")


if __name__ == "__main__":
    test_throttling()
