"""
Test básico do Shared Symbolic Register - P0 Critical Fix

Testa se o registro simbólico compartilhado permite comunicação entre módulos.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.consciousness.shared_workspace import SharedWorkspace  # noqa: E402


def test_symbolic_register_basic():
    """Test básico de comunicação simbólica."""
    print("🧪 Testing Shared Symbolic Register...")

    # Inicializar workspace
    workspace = SharedWorkspace(embedding_dim=256)

    # Testar envio de mensagem simbólica
    message_id = workspace.send_symbolic_message(
        sender="test_module_1",
        receiver="test_module_2",
        symbolic_content={
            "order": "Real",
            "embeddings": [1.0, 2.0, 3.0],
            "modules": ["mod1", "mod2", "mod3"],
        },
        priority=3,
    )

    print(f"✅ Message sent with ID: {message_id}")

    # Testar recebimento
    messages = workspace.receive_symbolic_messages("test_module_2")

    assert len(messages) == 1, f"Expected 1 message, got {len(messages)}"
    assert messages[0].sender == "test_module_1"
    assert messages[0].receiver == "test_module_2"
    assert messages[0].priority == 3

    print("✅ Message received correctly")

    # Testar tradução Real -> Imaginário
    real_content = {"embeddings": [1.0, -2.0, 3.0], "modules": ["A", "B", "C", "D"]}
    imaginary_content = workspace.translate_real_to_imaginary(real_content)

    assert imaginary_content["order"] == "Imaginary"
    assert "specular_projection" in imaginary_content
    assert "dual_relations" in imaginary_content

    print("✅ Real to Imaginary translation works")

    # Testar tradução Imaginário -> Simbólico
    symbolic_content = workspace.translate_imaginary_to_symbolic(imaginary_content)

    assert symbolic_content["order"] == "Symbolic"
    assert "signifying_chain" in symbolic_content
    assert "law_and_order" in symbolic_content

    print("✅ Imaginary to Symbolic translation works")

    # Testar estado simbólico
    workspace.update_symbolic_state("test_module_1", {"Real": {"test": "data"}})
    state = workspace.get_symbolic_state("test_module_1")

    assert "Real" in state
    assert "Imaginary" in state
    assert "Symbolic" in state
    assert state["Real"]["test"] == "data"

    print("✅ Symbolic state management works")

    # Testar estatísticas
    stats = workspace.get_symbolic_communication_stats()
    assert stats["total_messages"] == 1
    assert stats["messages_processed"] == 1

    print("✅ Communication stats work")

    print("🎉 ALL TESTS PASSED - Shared Symbolic Register is functional!")
    return True


def test_symbolic_register_with_topological_metrics():
    """Test Symbolic Register with topological metrics integration."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

    print("🧪 Testing Symbolic Register + Topological Metrics...")

    # Inicializar workspace com engine topológico
    workspace = SharedWorkspace(embedding_dim=256)
    workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Enviar mensagem simbólica
    workspace.send_symbolic_message(
        sender="test_module_1",
        receiver="test_module_2",
        symbolic_content={
            "order": "Real",
            "embeddings": [1.0, 2.0, 3.0],
            "modules": ["mod1", "mod2", "mod3"],
        },
        priority=3,
    )

    # Simular estados para métricas topológicas
    np.random.seed(42)
    for i in range(5):
        rho_C = np.random.randn(256)
        rho_P = np.random.randn(256)
        rho_U = np.random.randn(256)

        workspace.write_module_state("conscious_module", rho_C)
        workspace.write_module_state("preconscious_module", rho_P)
        workspace.write_module_state("unconscious_module", rho_U)
        workspace.advance_cycle()

    # Calcular métricas topológicas
    topological_metrics = workspace.compute_hybrid_topological_metrics()

    # Verificar que registro simbólico funciona
    messages = workspace.receive_symbolic_messages("test_module_2")
    assert len(messages) == 1

    # Verificar que métricas topológicas podem ser calculadas
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # Registro simbólico: comunicação RSI (Real-Symbolic-Imaginary)
        # Métricas topológicas: estrutura e integração
        # Ambas são complementares para análise completa

    print("✅ Symbolic Register + Topological Metrics integration verified")


if __name__ == "__main__":
    test_symbolic_register_basic()
