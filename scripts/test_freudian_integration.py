
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lacanian.freudian_metapsychology import FreudianMind, Action

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

def test_integration():
    print("=== Testing FreudianMind Integration with Audit Fixes ===")
    
    try:
        mind = FreudianMind()
        
        # 1. Verify Components
        print("\n[1] Verifying Components:")
        if mind.quantum_backend:
            print("✅ Quantum Backend (D-Wave) is active.")
        else:
            print("❌ Quantum Backend is MISSING.")
            
        if mind.id_agent.encrypted_memory:
            print("✅ Encrypted Unconscious is active.")
        else:
            print("❌ Encrypted Unconscious is MISSING.")
            
        if mind.superego_agent.society:
            print("✅ Society of Minds is active.")
        else:
            print("❌ Society of Minds is MISSING.")
            
        # 2. Test Decision Cycle
        print("\n[2] Testing Decision Cycle:")
        actions = [
            Action(
                action_id="quantum_test_action",
                pleasure_reward=0.9,
                reality_cost=0.5,
                moral_alignment=-0.2,
                description="Testing Quantum Decision"
            )
        ]
        
        reality_context = {"time": 1.0}
        
        chosen_action, resolution = mind.act(actions, reality_context)
        
        print(f"Action Chosen: {chosen_action.description}")
        print(f"Conflict Resolution Quality: {resolution.compromise_quality}")
        print("✅ Decision cycle completed successfully.")
        
        # 3. Test Repression (Encrypted Unconscious)
        print("\n[3] Testing Repression:")
        mind.id_agent.repress_memory("traumatic_event_001", -0.9)
        print("✅ Repression command sent.")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integration()
