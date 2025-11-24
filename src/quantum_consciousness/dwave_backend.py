from typing import Dict, Any, Optional
import os
import random

# Try to import D-Wave libraries
try:
    from dwave.system import DWaveSampler, EmbeddingComposite
    import dimod

    DWAVE_AVAILABLE = True
except ImportError:
    DWAVE_AVAILABLE = False
    print("Warning: 'dwave-system' not found. DWaveBackend will operate in mock mode.")


class DWaveBackend:
    """
    Quantum Backend utilizing D-Wave's Quantum Annealing technology.

    Unlike Gate-Model QPU (IBM), D-Wave is specialized for optimization problems.
    This is ideal for resolving psychoanalytic conflicts (Id vs Ego vs Superego)
    by modeling them as energy minimization problems (Ising Model / QUBO).
    """

    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or os.getenv("DWAVE_API_TOKEN")
        self.sampler = None

        if DWAVE_AVAILABLE and self.token:
            try:
                # Initialize the connection to D-Wave Leap
                self.sampler = EmbeddingComposite(
                    DWaveSampler(token=self.token, solver={"qpu": True})
                )
                print("D-Wave Quantum Annealer connected.")
            except Exception as e:
                print(f"Failed to connect to D-Wave: {e}")
                self.sampler = None
        else:
            if not self.token:
                print("D-Wave API Token not provided.")

    def resolve_conflict(
        self, id_energy: float, ego_energy: float, superego_energy: float
    ) -> Dict[str, Any]:
        """
        Resolves a conflict by finding the lowest energy state.

        We map the psychoanalytic agents to nodes in a graph:
        - Id (Node 0)
        - Ego (Node 1)
        - Superego (Node 2)

        The 'energies' provided are the biases (h) for each node.
        The couplings (J) represent the tension between them.
        """

        # Define the QUBO (Quadratic Unconstrained Binary Optimization)
        # We want to minimize Energy = x'Qx
        # Negative energy means "preference" for that state being 1 (Active)

        # Biases (linear terms)
        # If Id has high energy (drive), we give it a strong negative bias to encourage activation
        Q = {
            ("id", "id"): -id_energy,
            ("ego", "ego"): -ego_energy,
            ("superego", "superego"): -superego_energy,
            # Couplings (quadratic terms) - Tensions
            # Positive coupling means "disagreement" (cost to have both active)
            ("id", "ego"): 0.5,  # Id and Ego conflict
            ("ego", "superego"): 0.3,  # Ego and Superego conflict
            ("id", "superego"): 0.8,  # Id and Superego strongly conflict
        }

        if self.sampler:
            # Real Quantum Annealing
            bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
            sampleset = self.sampler.sample(bqm, num_reads=100)

            best_sample = sampleset.first.sample
            energy = sampleset.first.energy
            is_quantum = True
        else:
            # Classical Simulation (Simulated Annealing fallback)
            # Simple heuristic for mock mode
            best_sample = self._classical_fallback(Q)
            energy = self._calculate_energy(best_sample, Q)
            is_quantum = False

        # Determine the winner (the one with the active state '1')
        # If multiple are active, Ego decides based on weights
        winner = "ego"  # Default
        if best_sample.get("id") == 1 and best_sample.get("superego") == 0:
            winner = "id"
        elif best_sample.get("superego") == 1 and best_sample.get("id") == 0:
            winner = "superego"
        elif best_sample.get("ego") == 1:
            winner = "ego"

        return {
            "winner": winner,
            "sample": best_sample,
            "energy": energy,
            "backend": "D-Wave Advantage" if is_quantum else "Classical Simulator",
            "is_quantum": is_quantum,
        }

    def _classical_fallback(self, Q: Dict) -> Dict[str, int]:
        """Simple random choice weighted by energies for fallback."""
        # This is a very naive simulation just to return a valid structure
        return {
            "id": random.choice([0, 1]),
            "ego": 1,  # Ego tries to stay active
            "superego": random.choice([0, 1]),
        }

    def _calculate_energy(self, sample: Dict, Q: Dict) -> float:
        energy = 0
        for (u, v), bias in Q.items():
            val_u = sample.get(u, 0)
            val_v = sample.get(v, 0)
            energy += val_u * val_v * bias
        return energy
