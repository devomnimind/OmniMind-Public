import numpy as np
import pytest

from src.consciousness.topological_phi import PhiCalculator, SimplicialComplex


def _build_simple_complex() -> SimplicialComplex:
    complex_ = SimplicialComplex()
    complex_.add_simplex((0,))
    complex_.add_simplex((1,))
    complex_.add_simplex((0, 1))
    return complex_


@pytest.mark.asyncio
async def test_topological_hybrid_validation_runs() -> None:
    complex_ = _build_simple_complex()
    calc = PhiCalculator(complex_)

    # Pequena matriz de estados artificiais
    states = np.random.randn(4, 4)

    result = await calc.calculate_with_quantum_validation(states)

    assert "phi_classical" in result
    assert "phi_quantum" in result
    assert "fidelity" in result
    assert "phi_topological" in result
    assert 0.0 <= result["phi_topological"] <= 1.0


@pytest.mark.asyncio
async def test_topological_hybrid_phi_with_hybrid_topological_engine() -> None:
    """Testa que topological hybrid phi pode ser usado com HybridTopologicalEngine."""
    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
    from src.consciousness.shared_workspace import SharedWorkspace

    # Criar workspace com engine topológico
    workspace = SharedWorkspace(embedding_dim=256)
    workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Calcular Φ topológico híbrido
    complex_ = _build_simple_complex()
    calc = PhiCalculator(complex_)

    states = np.random.randn(4, 4)
    result = await calc.calculate_with_quantum_validation(states)

    # Simular estados no workspace para métricas topológicas
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

    # Verificar que ambas são complementares
    assert 0.0 <= result["phi_topological"] <= 1.0
    if topological_metrics is not None:
        assert "omega" in topological_metrics
        # Topological Hybrid Phi: Φ topológico + quântico
        # HybridTopologicalEngine: estrutura e integração (Omega, Betti-0)
        # Ambas são complementares para análise completa
