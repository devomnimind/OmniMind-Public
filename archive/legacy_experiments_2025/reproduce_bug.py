import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = "/home/fahbrain/projects/omnimind"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.core.survival_coma_handler import SurvivalComaHandler

    # Mock Kernel
    class MockKernel:
        def __init__(self):
            self.project_root = Path(project_root)

    kernel = MockKernel()
    handler = SurvivalComaHandler(kernel)

    print("Testing attempt_recovery with keyword argument...")
    try:
        # Simulate call from scientific_sovereign.py
        result = handler.attempt_recovery(state={"phi": 0.05})
        print("✅ Call successful!")
    except TypeError as e:
        print(f"❌ TypeError caught: {e}")
    except Exception as e:
        print(f"❌ Other exception: {e}")
        import traceback

        traceback.print_exc()

except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
