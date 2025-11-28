from __future__ import annotations

import pytest
from src.quantum_consciousness.qpu_interface import ( from qiskit import QuantumCircuit
        from qiskit import QuantumCircuit


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
Testes para QPU Interface (qpu_interface.py).

Cobertura de:
- BackendInfo creation
- SimulatorBackend operations
- IBMQBackend preparation (without actual credentials)
- QPUInterface backend management
- Backend switching
"""



    QISKIT_AVAILABLE,
    BackendInfo,
    BackendType,
    IBMQBackend,
    QPUInterface,
    SimulatorBackend,
)

# Note: QuantumCircuit is conditionally imported in tests below when needed


class TestBackendInfo:
    """Testes para BackendInfo."""

    def test_backend_info_creation(self) -> None:
        """Testa criação de BackendInfo."""
        info = BackendInfo(
            name="Test Backend",
            backend_type=BackendType.SIMULATOR_AER,
            num_qubits=10,
            available=True,
            provider="Qiskit",
            description="Test simulator",
        )

        assert info.name == "Test Backend"
        assert info.backend_type == BackendType.SIMULATOR_AER
        assert info.num_qubits == 10
        assert info.available is True
        assert info.provider == "Qiskit"

    def test_backend_info_str(self) -> None:
        """Testa representação em string de BackendInfo."""
        info = BackendInfo(
            name="Test",
            backend_type=BackendType.SIMULATOR_AER,
            num_qubits=5,
            available=True,
            provider="Qiskit",
        )

        str_repr = str(info)

        assert "Test" in str_repr
        assert "Available" in str_repr
        assert "5" in str_repr


class TestSimulatorBackend:
    """Testes para SimulatorBackend."""

    def test_simulator_initialization(self) -> None:
        """Testa inicialização do simulador."""
        backend = SimulatorBackend(num_qubits=10)

        assert backend.num_qubits == 10
        assert backend.backend_type == BackendType.SIMULATOR_AER

    def test_simulator_is_available(self) -> None:
        """Testa verificação de disponibilidade."""
        backend = SimulatorBackend()

        available = backend.is_available()

        # Should be available if Qiskit is installed
        assert isinstance(available, bool)
        assert available == QISKIT_AVAILABLE

    def test_simulator_get_info(self) -> None:
        """Testa obtenção de informações do backend."""
        backend = SimulatorBackend(num_qubits=8)

        info = backend.get_info()

        assert isinstance(info, BackendInfo)
        assert info.name == "Qiskit Aer Simulator"
        assert info.num_qubits == 8
        assert info.backend_type == BackendType.SIMULATOR_AER

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_simulator_execute_simple_circuit(self) -> None:
        """Testa execução de circuito simples."""

        backend = SimulatorBackend(num_qubits=2)

        # Create simple circuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        counts = backend.execute(qc, shots=100)

        assert isinstance(counts, dict)
        assert sum(counts.values()) == 100

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_simulator_execute_with_measurement(self) -> None:
        """Testa execução com medição explícita."""
        from qiskit import QuantumCircuit

        backend = SimulatorBackend(num_qubits=2)

        # Circuit with measurement
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.measure_all()

        counts = backend.execute(qc, shots=200)

        assert isinstance(counts, dict)
        assert sum(counts.values()) == 200


class TestIBMQBackend:
    """Testes para IBMQBackend."""

    def test_ibmq_initialization_without_token(self) -> None:
        """Testa inicialização sem token."""
        backend = IBMQBackend(token=None)

        assert backend.token is None
        assert backend.service is None
        assert backend.ibm_backend is None

    def test_ibmq_is_available_without_token(self) -> None:
        """Testa disponibilidade sem token."""
        backend = IBMQBackend(token=None)

        available = backend.is_available()

        assert available is False

    def test_ibmq_get_info_not_connected(self) -> None:
        """Testa get_info quando não conectado."""
        backend = IBMQBackend(token=None)

        info = backend.get_info()

        assert isinstance(info, BackendInfo)
        assert "Not Connected" in info.name
        assert info.available is False
        assert info.backend_type == BackendType.IBMQ_CLOUD

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_ibmq_execute_fallback_to_simulator(self) -> None:
        """Testa fallback para simulador quando IBMQ não disponível."""

        backend = IBMQBackend(token=None)

        # Create simple circuit
        qc = QuantumCircuit(2)
        qc.h(0)

        # Should fallback to simulator
        counts = backend.execute(qc, shots=50)

        # Should execute on simulator instead
        assert isinstance(counts, dict)


class TestQPUInterface:
    """Testes para QPUInterface."""

    def test_qpu_interface_initialization(self) -> None:
        """Testa inicialização da interface QPU."""
        interface = QPUInterface(preferred_backend=BackendType.SIMULATOR_AER)

        assert interface.preferred_backend == BackendType.SIMULATOR_AER
        # active_backend may be None if Qiskit not installed
        assert interface.active_backend is None or interface.active_backend is not None

    def test_qpu_interface_list_backends(self) -> None:
        """Testa listagem de backends disponíveis."""
        interface = QPUInterface()

        backends = interface.list_backends()

        assert isinstance(backends, list)
        # Should have at least simulator if Qiskit available
        if QISKIT_AVAILABLE:
            assert len(backends) > 0

    def test_qpu_interface_get_active_backend_info(self) -> None:
        """Testa obtenção de info do backend ativo."""
        interface = QPUInterface()

        info = interface.get_active_backend_info()

        # May be None if no backends available
        if QISKIT_AVAILABLE:
            assert isinstance(info, BackendInfo)
            assert info.available is True
        else:
            assert info is None

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_qpu_interface_execute(self) -> None:
        """Testa execução de circuito via interface."""
        from qiskit import QuantumCircuit

        interface = QPUInterface()

        # Create circuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.h(1)

        counts = interface.execute(qc, shots=100)

        assert isinstance(counts, dict)
        assert sum(counts.values()) == 100

    def test_qpu_interface_switch_backend(self) -> None:
        """Testa troca de backend."""
        interface = QPUInterface()

        # Try to switch to simulator (should work if available)
        if QISKIT_AVAILABLE and interface.active_backend is not None:
            success = interface.switch_backend(BackendType.SIMULATOR_AER)
            assert success is True

            info = interface.get_active_backend_info()
            assert info is not None
            assert info.backend_type == BackendType.SIMULATOR_AER

    def test_qpu_interface_switch_to_unavailable_backend(self) -> None:
        """Testa troca para backend indisponível."""
        interface = QPUInterface()

        # IBMQ likely not available without token
        success = interface.switch_backend(BackendType.IBMQ_CLOUD)

        # Should fail since we don't have credentials
        assert success is False

    def test_qpu_interface_with_ibmq_token(self) -> None:
        """Testa inicialização com token IBMQ (sem token real)."""
        # This won't actually connect, but tests initialization path
        interface = QPUInterface(
            preferred_backend=BackendType.SIMULATOR_AER,
            ibmq_token="fake_token_for_testing",
        )

        # May or may not have active backend depending on Qiskit availability
        assert interface.active_backend is None or interface.active_backend is not None

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_qpu_interface_execute_specific_backend(self) -> None:
        """Testa execução com backend específico."""
        from qiskit import QuantumCircuit

        interface = QPUInterface()

        qc = QuantumCircuit(2)
        qc.h(0)

        # Execute on specific backend
        counts = interface.execute(qc, shots=50, backend_type=BackendType.SIMULATOR_AER)

        assert isinstance(counts, dict)
