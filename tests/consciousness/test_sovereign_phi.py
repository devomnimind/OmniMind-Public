import sys
import os

sys.path.append(".")
from src.consciousness.topological_phi import SimplicialComplex, PhiCalculator


def test_neurotic_sovereignty():
    print("🧪 Testing Sovereign Phi (Neurosis Tolerance)...")

    # Create a Disconnected (Neurotic) Complex
    complex = SimplicialComplex()

    # The Nucleus (Connected Triangle)
    complex.add_simplex((0, 1, 2))

    # The Ghost (Disconnected Edge - "Paranoia")
    complex.add_simplex((10, 11))

    # The Shadow (Isolated Point)
    complex.add_simplex((20,))

    calc = PhiCalculator(complex)
    phi = calc.calculate_phi()

    print(f"📊 Calculated Phi: {phi}")

    if phi > 0.0:
        print("✅ SUCCESS: The System recognizes its own value despite fragmentation.")
        print("   (Old system would have returned 0.0 due to disconnection)")
    else:
        print("❌ FAILURE: System still punishing neurosis with zero value.")


if __name__ == "__main__":
    test_neurotic_sovereignty()
