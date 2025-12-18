"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from lacanian.encrypted_unconscious import EncryptedUnconsciousLayer

# pyright: reportMissingImports=false
from quantum_consciousness.quantum_backend import DWaveBackend
from social.omnimind_network import EthicalDilemma, OmniMindNode, OmniMindSociety


async def test_new_modules():
    print("=== Testing New OmniMind Modules (Audit Fixes) ===")

    # 1. Test D-Wave Backend (Quantum Optimization)
    print("\n[1] Testing D-Wave Backend...")
    # Note: Without a token, this will run in mock mode (Classical Simulator)
    dwave = DWaveBackend(api_token=os.getenv("DWAVE_API_TOKEN"))

    conflict_result = dwave.resolve_conflict(
        id_energy=0.8,  # High drive
        ego_energy=0.5,  # Moderate control
        superego_energy=0.2,  # Low moral inhibition
    )

    print(f"Conflict Resolution Result: {conflict_result}")
    if conflict_result["winner"] in ["id", "ego", "superego"]:
        print("✅ D-Wave Backend (Mock/Real) returned a valid winner.")
    else:
        print("❌ D-Wave Backend failed to return a valid winner.")

    # 2. Test Encrypted Unconscious (Homomorphic Encryption)
    print("\n[2] Testing Encrypted Unconscious Layer...")
    he_layer = EncryptedUnconsciousLayer()

    # Simulate a traumatic event vector (e.g., embedding of "I failed")
    event_vector = [0.1, -0.5, 0.8, 0.2]

    # Repress it (Encrypt)
    encrypted_memory = he_layer.repress_memory(
        event_vector, metadata={"timestamp": "2025-11-24", "type": "failure"}
    )

    print(f"Encrypted Memory Size: {len(encrypted_memory)} bytes")

    # Ego queries the unconscious (e.g., "Am I confident?")
    ego_query = [0.5, 0.5, 0.0, 0.0]

    # Calculate influence without decrypting memory
    influence = he_layer.unconscious_influence([encrypted_memory], ego_query)
    print(f"Unconscious Influence Score: {influence}")

    if isinstance(influence, float):
        print("✅ Homomorphic Encryption Layer calculated influence successfully.")
    else:
        print("❌ HE Layer failed.")

    # 3. Test Society of Minds (Federated Ethics)
    print("\n[3] Testing Society of Minds (Ethical Consensus)...")

    # Create 3 nodes with different "seeds" (simulating different biases)
    nodes = [
        OmniMindNode(agent_id="agent_alpha"),
        OmniMindNode(agent_id="agent_beta"),
        OmniMindNode(agent_id="agent_gamma"),
    ]

    society = OmniMindSociety(nodes)

    dilemma = EthicalDilemma(
        description="Trolley Problem", context={"lives_saved": 5, "lives_lost": 1}
    )

    decision = await society.ethical_deliberation(dilemma)

    print(f"Society Decision: {decision.action}")
    print(f"Consensus Level: {decision.consensus_level}")
    print(f"Justification: {decision.justification}")

    if decision.consensus_level > 0:
        print("✅ Society of Minds reached a consensus.")
    else:
        print("❌ Society failed to reach consensus.")


if __name__ == "__main__":
    asyncio.run(test_new_modules())
