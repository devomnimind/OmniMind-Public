import os
import sys
from qiskit_ibm_runtime import QiskitRuntimeService
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv()


def test_direct_connection():
    # Load keys directly from known env vars or hardcoded fallback for testing
    api_key = os.getenv("IBM_CLOUD_API_KEY") or os.getenv("IBM_QUANTUM_NEW_KEY")
    crn = os.getenv("IBM_QUANTUM_NEW_CRN")

    print(f"🔑 Testing Connection with Key Prefix: {api_key[:5] if api_key else 'None'}...")

    if not api_key:
        print("❌ No API Key found in environment.")
        return False

    try:
        # Try initializing service
        print("📡 Initializing QiskitRuntimeService (channel='ibm_cloud')...")
        service = QiskitRuntimeService(channel="ibm_cloud", token=api_key, instance=crn)

        print("✅ Service Initialized!")

        # List backends
        print("📋 Listing Backends...")
        backends = service.backends()
        for b in backends:
            try:
                # Different SDK versions have different status attributes
                status_val = (
                    b.status().operational if hasattr(b.status(), "operational") else "Unknown"
                )
                print(f"   - {b.name} (Operational: {status_val})")
            except Exception as e:
                print(f"   - {b.name} (Status Read Error: {e})")

        return True

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

        # Fallback attempt
        print("\n🔄 Retrying with channel='ibm_quantum'...")
        try:
            service = QiskitRuntimeService(channel="ibm_quantum", token=api_key)
            print("✅ Service Initialized (Legacy Channel)!")
            return True
        except Exception as e2:
            print(f"❌ Legacy Connection Failed: {e2}")
            return False


if __name__ == "__main__":
    if test_direct_connection():
        sys.exit(0)
    else:
        sys.exit(1)
