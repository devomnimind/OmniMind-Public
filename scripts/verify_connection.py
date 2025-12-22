import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from src.quantum.consciousness.quantum_backend import QuantumBackend


def verify_connection():
    print("🔌 Verifying Quantum Backend Connection...")

    # Debug Environment
    print("Environment Variables:")
    for key in os.environ:
        if "IBM" in key or "QUANTUM" in key:
            print(f"  {key}: {os.environ[key][:5]}...")

    # Initialize
    backend = QuantumBackend(provider="auto", prefer_local=False)

    # Check Token
    print(f"🔑 Token loaded: {'Yes' if backend.token else 'No'}")
    if backend.token:
        print(f"   Token length: {len(backend.token)}")
        print(f"   Token prefix: {backend.token[:4]}...")

    # Check Active Mode
    print(f"📡 Active Mode: {backend.mode}")
    print(f"⚙️  Backend Provider: {backend.provider}")

    if backend.backend and hasattr(backend.backend, "get_info"):
        info = backend.backend.get_info()
        print(f"ℹ️  Backend Info: {info}")

    # Check if Federation is possible
    is_federated = backend.mode.startswith("CLOUD") or (backend.token and "IBM" in backend.mode)
    print(f"\n🌐 Federation Status: {'CONNECTED' if is_federated else 'DISCONNECTED'}")

    return is_federated


if __name__ == "__main__":
    if verify_connection():
        sys.exit(0)
    else:
        sys.exit(1)
