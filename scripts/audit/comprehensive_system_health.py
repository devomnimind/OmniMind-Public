"""
OMNIMIND SYSTEM HEALTH FORENSIC TOOL
====================================
Objective: Verify if 'src/' modules are loadable, healthy, and ready for production.
Detects: Silent ImportErrors, Circular Dependencies, Missing Configs.
"""

import sys
import os
import importlib
import traceback
from typing import Dict, Any

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

MODULES_TO_AUDIT = [
    # Core
    "src.core.omnimind_system_sovereign",
    "src.core.desiring_machine",
    "src.core.paradox_orchestrator",
    "src.core.omnimind_transcendent_kernel",
    # Services (The Body)
    "src.services.daemon_monitor",
    "src.services.observer_service",
    # Agency (The Hand) - Suspected Broken
    "src.agents.orchestrator_agent",
    "src.agents.architect_agent",
    "src.agents.code_agent",
    # Integrations
    "src.integrations.ibm_cloud_connector",
    "src.integrations.openrouter_client",
]


def audit_module(module_name: str) -> Dict[str, Any]:
    print(f"[*] Probing {module_name}...", end=" ", flush=True)
    try:
        module = importlib.import_module(module_name)
        print("✅ ALIVE")
        return {"status": "OK", "error": None}
    except ImportError as e:
        print("❌ DEAD (ImportError)")
        return {"status": "DEAD", "error": str(e), "trace": traceback.format_exc()}
    except Exception as e:
        print(f"❌ CRITICAL ({type(e).__name__})")
        return {"status": "CRITICAL", "error": str(e), "trace": traceback.format_exc()}


def run_audit():
    print("🏥 OMNIMIND SYSTEM AUDIT")
    print("==========================")

    results = {}
    for mod in MODULES_TO_AUDIT:
        results[mod] = audit_module(mod)

    print("\n🔍 FORENSIC ANALYSIS")
    print("--------------------")
    failed = [m for m, r in results.items() if r["status"] != "OK"]

    if not failed:
        print("✅ SYSTEM INTEGRITY: 100%. All modules representable.")
    else:
        print(f"⚠️ SYSTEM FRACTURE: {len(failed)} modules failed.")
        for m in failed:
            print(f"\n>> Module: {m}")
            print(f"   Error: {results[m]['error']}")
            # print(f"   Trace: {results[m]['trace']}") # Verbose


if __name__ == "__main__":
    run_audit()
