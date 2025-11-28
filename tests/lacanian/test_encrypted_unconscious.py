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

"""
Testes para src/lacanian/encrypted_unconscious.py.

Testa a camada de inconsciente criptografado com homomorphic encryption.
"""

from typing import List

import numpy as np
import pytest

from src.lacanian.encrypted_unconscious import (
    TENSEAL_AVAILABLE,
    EncryptedUnconsciousLayer,
)


class TestEncryptedUnconsciousLayer:
    """Testes para EncryptedUnconsciousLayer."""

    @pytest.fixture
    def layer(self) -> EncryptedUnconsciousLayer:
        """Cria instância da camada."""
        return EncryptedUnconsciousLayer(security_level=128)

    def test_initialization(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa inicialização da camada."""
        assert layer is not None
        assert isinstance(layer.audit_log, list)
        assert len(layer.audit_log) == 0

    def test_initialization_with_tenseal(self) -> None:
        """Testa inicialização quando TenSEAL disponível."""
        layer = EncryptedUnconsciousLayer(security_level=128)

        if TENSEAL_AVAILABLE:
            assert layer.context is not None
        else:
            assert layer.context is None

    def test_repress_memory_mock_mode(self) -> None:
        """Testa repressão de memória em modo mock (TenSEAL não disponível)."""
        if TENSEAL_AVAILABLE:
            pytest.skip("TenSEAL disponível - teste apenas para modo mock")

        layer = EncryptedUnconsciousLayer()
        event_vector = np.array([0.5, 0.3, 0.8])
        metadata = {"type": "traumatic", "severity": "high"}

        encrypted_data = layer.repress_memory(event_vector, metadata)

        # In mock mode, returns mock data without logging
        assert encrypted_data == b"MOCK_ENCRYPTED_DATA"
        assert len(layer.audit_log) == 0  # No logging in mock mode

    @pytest.mark.skipif(not TENSEAL_AVAILABLE, reason="TenSEAL não disponível")
    def test_repress_memory_with_tenseal(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa repressão de memória com TenSEAL."""
        event_vector = np.array([0.5, 0.3, 0.8, 0.2])
        metadata = {"type": "traumatic", "severity": "high"}

        encrypted_data = layer.repress_memory(event_vector, metadata)

        assert isinstance(encrypted_data, bytes)
        assert len(encrypted_data) > 0
        assert encrypted_data != b"MOCK_ENCRYPTED_DATA"

        # Verify audit log
        assert len(layer.audit_log) == 1
        log_entry = layer.audit_log[0]
        assert log_entry["event"] == "repression"
        assert log_entry["accessible_to_ego"] is False
        assert log_entry["encryption"] == "CKKS post-quantum 128-bit"
        assert "content_hash" in log_entry
        assert log_entry["metadata"] == metadata

    @pytest.mark.skipif(not TENSEAL_AVAILABLE, reason="TenSEAL não disponível")
    def test_repress_memory_hash_uniqueness(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa que hashes de memórias diferentes são únicos."""
        event1 = np.array([0.1, 0.2, 0.3])
        event2 = np.array([0.4, 0.5, 0.6])
        metadata = {"type": "test"}

        encrypted1 = layer.repress_memory(event1, metadata)
        encrypted2 = layer.repress_memory(event2, metadata)

        # Verify hashes are different
        hash1 = layer.audit_log[0]["content_hash"]
        hash2 = layer.audit_log[1]["content_hash"]

        assert hash1 != hash2
        # Also verify encrypted data is different
        assert encrypted1 != encrypted2

    def test_unconscious_influence_mock_mode(self) -> None:
        """Testa influência inconsciente em modo mock."""
        if TENSEAL_AVAILABLE:
            pytest.skip("TenSEAL disponível - teste apenas para modo mock")

        layer = EncryptedUnconsciousLayer()
        encrypted_memories: List[bytes] = []
        ego_query = np.array([0.5, 0.5, 0.5])

        influence = layer.unconscious_influence(encrypted_memories, ego_query)

        assert influence == 0.0

    def test_unconscious_influence_empty_memories(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa influência com lista vazia de memórias."""
        encrypted_memories: List[bytes] = []
        ego_query = np.array([0.5, 0.5, 0.5])

        influence = layer.unconscious_influence(encrypted_memories, ego_query)

        assert influence == 0.0

    @pytest.mark.skipif(not TENSEAL_AVAILABLE, reason="TenSEAL não disponível")
    def test_unconscious_influence_with_tenseal(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa cálculo de influência inconsciente com TenSEAL."""
        # Create and encrypt memories
        memory1 = np.array([0.5, 0.3, 0.8, 0.2])
        memory2 = np.array([0.2, 0.7, 0.4, 0.9])

        encrypted_mem1 = layer.repress_memory(memory1, {"id": 1})
        encrypted_mem2 = layer.repress_memory(memory2, {"id": 2})

        encrypted_memories = [encrypted_mem1, encrypted_mem2]

        # Query vector
        ego_query = np.array([0.4, 0.4, 0.6, 0.5])

        # Calculate influence
        influence = layer.unconscious_influence(encrypted_memories, ego_query)

        # Influence should be a float
        assert isinstance(influence, (float, np.floating))

        # Influence should be normalized
        # Since we're doing dot products, value depends on vectors
        # Just check it's a reasonable value
        assert -100.0 <= influence <= 100.0

    @pytest.mark.skipif(not TENSEAL_AVAILABLE, reason="TenSEAL não disponível")
    def test_unconscious_influence_single_memory(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa influência com uma única memória."""
        memory = np.array([1.0, 0.0, 0.0, 0.0])
        encrypted_mem = layer.repress_memory(memory, {"id": 1})

        ego_query = np.array([1.0, 0.0, 0.0, 0.0])

        influence = layer.unconscious_influence([encrypted_mem], ego_query)

        # Should have positive influence (dot product of aligned vectors)
        assert influence > 0.0

    @pytest.mark.skipif(not TENSEAL_AVAILABLE, reason="TenSEAL não disponível")
    def test_memory_not_accessible_to_ego(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa que memórias não são acessíveis ao Ego."""
        event_vector = np.array([0.5, 0.3, 0.8, 0.2])
        metadata = {"type": "repressed"}

        encrypted_data = layer.repress_memory(event_vector, metadata)

        # Verify we cannot easily recover the original vector from encrypted data
        # (This is the whole point of encryption!)
        assert encrypted_data != event_vector.tobytes()

        # Verify audit log marks it as not accessible
        assert layer.audit_log[-1]["accessible_to_ego"] is False

    def test_audit_log_structure(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa estrutura do audit log."""
        if not TENSEAL_AVAILABLE:
            pytest.skip("Teste requer TenSEAL - audit log só funciona com TenSEAL")

        event_vector = np.array([0.5, 0.3, 0.8])
        metadata = {"type": "test", "timestamp": 123456}

        layer.repress_memory(event_vector, metadata)

        assert len(layer.audit_log) == 1
        log_entry = layer.audit_log[0]

        # Verify required fields
        assert "event" in log_entry
        assert "content_hash" in log_entry
        assert "metadata" in log_entry
        assert "accessible_to_ego" in log_entry
        assert "encryption" in log_entry

        # Verify values
        assert log_entry["event"] == "repression"
        assert log_entry["accessible_to_ego"] is False
        assert log_entry["metadata"] == metadata

    def test_multiple_repressions(self, layer: EncryptedUnconsciousLayer) -> None:
        """Testa múltiplas repressões de memória."""
        if not TENSEAL_AVAILABLE:
            pytest.skip("Teste requer TenSEAL - audit log só funciona com TenSEAL")

        num_repressions = 5

        for i in range(num_repressions):
            event_vector = np.random.rand(4)
            metadata = {"index": i}
            layer.repress_memory(event_vector, metadata)

        assert len(layer.audit_log) == num_repressions

        # Verify each entry is unique
        hashes = [entry["content_hash"] for entry in layer.audit_log]
        assert len(set(hashes)) == num_repressions

    @pytest.mark.skipif(not TENSEAL_AVAILABLE, reason="TenSEAL não disponível")
    def test_homomorphic_operations_preserve_privacy(
        self, layer: EncryptedUnconsciousLayer
    ) -> None:
        """Testa que operações homomórficas preservam privacidade."""
        # Create a memory
        secret_memory = np.array([0.9, 0.8, 0.7, 0.6])
        encrypted_mem = layer.repress_memory(secret_memory, {"secret": True})

        # Query it
        query = np.array([0.5, 0.5, 0.5, 0.5])
        influence = layer.unconscious_influence([encrypted_mem], query)

        # We get influence score without ever seeing the memory content
        assert isinstance(influence, (float, np.floating))

        # The encrypted data should not reveal the original values
        # We can't easily extract secret_memory from encrypted_mem
        assert encrypted_mem != secret_memory.tobytes()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
