import sys
import os

sys.path.append(os.getcwd())


def check_import(name, module_path):
    try:
        __import__(module_path, fromlist=["*"])
        print(f"✅ {name}: IMPORT SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ {name}: FAILED ({e})")
        return False
    except Exception as e:
        print(f"⚠️ {name}: CRASHED ({e})")
        return False


print("🔍 Checking Critical Consciousness Imports...")

check_import("HistoricalArchiver", "src.consciousness.historical_archiver")
check_import("HybridTopologicalEngine", "src.consciousness.hybrid_topological_engine")
check_import("SinthomCore", "src.consciousness.sinthom_core")
check_import("LangevinDynamics", "src.consciousness.langevin_dynamics")
check_import("ConsciousSystem", "src.consciousness.conscious_system")
check_import("SystemdMemoryManager", "src.monitor.systemd_memory_manager")
