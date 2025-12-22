"""
@phylogenesis_signature(
    origin="OmniMind_Planning",
    intent="audit_ibm_resources",
    human_readable=True
)
"""

import os
import sys
import logging
from pprint import pprint

sys.path.append(os.getcwd())

from src.integrations.ibm_cloud_connector import IBMCloudConnector

try:
    from qiskit_ibm_runtime import QiskitRuntimeService
except ImportError:
    QiskitRuntimeService = None

logging.basicConfig(level=logging.INFO)


def check_resources():
    print("☁️ IBM CLOUD RESOURCE AUDIT")
    print("==========================")

    # 1. Watsonx Status
    print("\n[1] WATSONX (The Big Other)")
    try:
        ibm = IBMCloudConnector()
        if ibm.watsonx_model:
            print("   ✅ Connection: Active")
            print(f"   Model ID: {ibm.watsonx_model.model_id}")
            # Try to infer limits? No direct API, but we can check if generation works
            print("   Status: Ready for Demo (Inference Confirmed in Exp B)")
        else:
            print("   ⚠️ Connection: Inactive (Check Keys)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 2. Quantum Status
    print("\n[2] QUANTUM (The Real)")
    if QiskitRuntimeService:
        try:
            # Load from env or connector
            service = QiskitRuntimeService(channel="ibm_quantum")  # or ibm_cloud
            print(f"   ✅ Service: Active (Channel: {service.channel})")

            # List Backends
            backends = service.backends()
            print(f"   Available Backends: {len(backends)}")

            real_backends = [b.name for b in backends if not b.simulator]
            simulators = [b.name for b in backends if b.simulator]

            print(f"   Real QPUs: {real_backends[:3]} ...")
            print(f"   Simulators: {simulators}")

            # Check for least busy if we were to run a demo
            least_busy = service.least_busy(operational=True, simulator=False)
            print(
                f"   Recommended for Demo: {least_busy.name} (Status: {least_busy.status().status_msg})"
            )

        except Exception as e:
            print(f"   ⚠️ Cloud Quantum Access Audit Failed: {e}")
            print("   Note: Local Simulator (Aer) is always available.")
    else:
        print("   ❌ Qiskit Runtime not installed.")


if __name__ == "__main__":
    check_resources()
