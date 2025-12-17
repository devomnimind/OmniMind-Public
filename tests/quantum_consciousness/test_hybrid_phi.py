import numpy as np
import pytest

from src.quantum_consciousness.amplitude_amplification import AmplitudeAmplification
from src.quantum_consciousness.entanglement_validator import EntanglementValidator
from src.quantum_consciousness.hybrid_phi_calculator import HybridPhiCalculator
from src.quantum_consciousness.phi_trajectory_transformer import QuantumInputFeatures


@pytest.mark.asyncio
async def test_hybrid_phi_simulator():
    calc = HybridPhiCalculator(use_ibm=False)
    states = np.random.randn(8, 8)
    result = await calc.calculate_phi_hybrid(states, use_real_hw=False)

    assert 0 <= result["phi_classical"] <= 1
    assert 0 <= result["phi_quantum"] <= 1
    assert 0 <= result["fidelity"] <= 1


@pytest.mark.asyncio
async def test_amplitude_amplification_simulation():
    aa = AmplitudeAmplification()
    res = await aa.run_amplitude_amplification(
        num_qubits=3, target_index=5, iterations=2, use_real_hw=False
    )
    assert res["probability_target"] >= 0
    assert "counts" in res


def test_entanglement_tools():
    validator = EntanglementValidator()
    bell = validator.bell_test(qubit_pairs=[(0, 1), (2, 3)])
    assert bell["entangled"]

    a = np.random.randint(0, 2, 100)
    b = np.random.randint(0, 2, 100)
    mi = validator.mutual_information(a, b)
    assert 0 <= mi <= 1

    rho = np.array([[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0], [0.5, 0, 0, 0.5]])
    c = validator.concurrence(rho)
    assert 0 <= c <= 1


class TestHybridPhiCalculatorTrajectory:
    """Tests for Phase 25 trajectory processing methods."""

    @pytest.fixture
    def calculator(self):
        """Create HybridPhiCalculator instance."""
        return HybridPhiCalculator(use_ibm=False)

    @pytest.fixture
    def mock_quantum_features(self):
        """Create mock QuantumInputFeatures for testing."""
        T = 10
        return QuantumInputFeatures(
            phi_sequence=np.array([0.3 + i * 0.05 for i in range(T)]),
            phi_mean=0.55,
            phi_std=0.15,
            phi_trend=0.05,
            coherence_sequence=np.array([0.5 + i * 0.03 for i in range(T)]),
            coherence_mean=0.635,
            integration_sequence=np.array([0.4 + i * 0.04 for i in range(T)]),
            integration_mean=0.58,
            timestamps=np.array([100.0 + i * 10.0 for i in range(T)]),
            episode_ids=[f"ep_{i:03d}" for i in range(T)],
            quantum_amplitudes=np.array(
                [
                    [0.7 + 0.3j, 0.3 + 0.7j] if i % 2 == 0 else [0.5 + 0.5j, 0.5 + 0.5j]
                    for i in range(T)
                ]
            ),
        )

    def test_blend_phi(self, calculator):
        """Test blending classical and quantum Φ values."""
        phi_c = np.array([0.3, 0.4, 0.5, 0.6, 0.7])
        phi_q = np.array([0.2, 0.3, 0.4, 0.5, 0.6])

        # Equal weight
        phi_hybrid = calculator.blend_phi(phi_c, phi_q, blend_weight=0.5)
        assert phi_hybrid.shape == phi_c.shape
        assert np.all(phi_hybrid >= 0.0)
        assert np.all(phi_hybrid <= 1.0)
        # Check blend: 0.5 * 0.3 + 0.5 * 0.2 = 0.25
        assert np.isclose(phi_hybrid[0], 0.25, atol=1e-6)

        # Pure classical
        phi_hybrid_c = calculator.blend_phi(phi_c, phi_q, blend_weight=1.0)
        assert np.allclose(phi_hybrid_c, phi_c)

        # Pure quantum
        phi_hybrid_q = calculator.blend_phi(phi_c, phi_q, blend_weight=0.0)
        assert np.allclose(phi_hybrid_q, phi_q)

    def test_blend_phi_shape_mismatch(self, calculator):
        """Test blend_phi raises error on shape mismatch."""
        phi_c = np.array([0.3, 0.4, 0.5])
        phi_q = np.array([0.2, 0.3])  # Different length

        with pytest.raises(ValueError, match="Shape mismatch"):
            calculator.blend_phi(phi_c, phi_q)

    def test_calculate_fidelity(self, calculator):
        """Test fidelity calculation between classical and quantum amplitudes."""
        T = 5
        amp_c = np.array([[0.7, 0.3], [0.6, 0.4], [0.5, 0.5], [0.4, 0.6], [0.3, 0.7]])
        amp_q = np.array(
            [
                [0.7 + 0.3j, 0.3 + 0.7j],
                [0.6 + 0.4j, 0.4 + 0.6j],
                [0.5 + 0.5j, 0.5 + 0.5j],
                [0.4 + 0.6j, 0.6 + 0.4j],
                [0.3 + 0.7j, 0.7 + 0.3j],
            ]
        )

        fidelity = calculator.calculate_fidelity(amp_c, amp_q)

        assert fidelity.shape == (T,)
        assert np.all(fidelity >= 0.0)
        assert np.all(fidelity <= 1.0)

    def test_calculate_fidelity_shape_mismatch(self, calculator):
        """Test calculate_fidelity raises error on shape mismatch."""
        amp_c = np.array([[0.7, 0.3], [0.6, 0.4]])
        amp_q = np.array([[0.7 + 0.3j, 0.3 + 0.7j]])  # Different length

        with pytest.raises(ValueError, match="Shape mismatch"):
            calculator.calculate_fidelity(amp_c, amp_q)

    @pytest.mark.asyncio
    async def test_process_trajectory(self, calculator, mock_quantum_features):
        """Test complete trajectory processing."""
        result = await calculator.process_trajectory(
            mock_quantum_features, blend_weight=0.5, use_real_hw=False
        )

        # Check structure
        assert "phi_classical_sequence" in result
        assert "phi_quantum_sequence" in result
        assert "phi_hybrid_sequence" in result
        assert "fidelity_sequence" in result

        # Check sequences
        T = mock_quantum_features.phi_sequence.shape[0]
        assert result["phi_classical_sequence"].shape == (T,)
        assert result["phi_quantum_sequence"].shape == (T,)
        assert result["phi_hybrid_sequence"].shape == (T,)
        assert result["fidelity_sequence"].shape == (T,)

        # Check ranges
        assert np.all(result["phi_classical_sequence"] >= 0.0)
        assert np.all(result["phi_classical_sequence"] <= 1.0)
        assert np.all(result["phi_quantum_sequence"] >= 0.0)
        assert np.all(result["phi_quantum_sequence"] <= 1.0)
        assert np.all(result["phi_hybrid_sequence"] >= 0.0)
        assert np.all(result["phi_hybrid_sequence"] <= 1.0)
        assert np.all(result["fidelity_sequence"] >= 0.0)
        assert np.all(result["fidelity_sequence"] <= 1.0)

        # Check statistics
        assert "phi_classical_mean" in result
        assert "phi_quantum_mean" in result
        assert "phi_hybrid_mean" in result
        assert "fidelity_mean" in result
        assert 0 <= result["phi_classical_mean"] <= 1
        assert 0 <= result["phi_quantum_mean"] <= 1
        assert 0 <= result["phi_hybrid_mean"] <= 1
        assert 0 <= result["fidelity_mean"] <= 1

        # Check Phase 24 metadata
        assert result["phase24_phi_mean"] == pytest.approx(0.55, abs=0.01)
        assert result["trajectory_length"] == T

    @pytest.mark.asyncio
    async def test_process_trajectory_different_blend_weights(
        self, calculator, mock_quantum_features
    ):
        """Test trajectory processing with different blend weights."""
        result_50 = await calculator.process_trajectory(
            mock_quantum_features, blend_weight=0.5, use_real_hw=False
        )
        result_80 = await calculator.process_trajectory(
            mock_quantum_features, blend_weight=0.8, use_real_hw=False
        )
        result_20 = await calculator.process_trajectory(
            mock_quantum_features, blend_weight=0.2, use_real_hw=False
        )

        # Higher blend_weight should produce hybrid closer to classical
        # Check that 0.8 blend is closer to classical than 0.2 blend
        phi_c_mean = result_50["phi_classical_mean"]

        # 0.8 blend should be closer to classical
        diff_80 = abs(result_80["phi_hybrid_mean"] - phi_c_mean)
        diff_20 = abs(result_20["phi_hybrid_mean"] - phi_c_mean)

        assert diff_80 < diff_20


class TestHybridPhiHybridTopological:
    """Testes de integração entre HybridPhiCalculator e HybridTopologicalEngine."""

    @pytest.mark.asyncio
    async def test_hybrid_phi_with_topological_metrics(self):
        """Testa que HybridPhiCalculator pode ser usado com métricas topológicas."""
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Calcular Φ híbrido (quantum + classical)
        calc = HybridPhiCalculator(use_ibm=False)
        states = np.random.randn(8, 8)
        result = await calc.calculate_phi_hybrid(states, use_real_hw=False)

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
        assert 0 <= result["phi_classical"] <= 1
        assert 0 <= result["phi_quantum"] <= 1
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # HybridPhi: Φ clássico + quântico
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa
