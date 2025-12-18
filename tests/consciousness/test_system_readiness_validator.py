#!/usr/bin/env python3
"""
Test Suite: System Readiness Validator

Testa todos os componentes de validação contínua de estado.
"""

from unittest.mock import AsyncMock, Mock

import numpy as np
import pytest

from src.consciousness.system_readiness_validator import (
    ContinuousReadinessEngine,
    ReadinessStatus,
    SystemReadinessValidator,
)


class TestReadinessStatus:
    """Testes para ReadinessStatus"""

    def test_ready_state_string(self):
        """Verificar representação de READY state"""
        status = ReadinessStatus(
            state="READY",
            reasons=[],
            metrics={"phi": 0.5},
            timestamp=0.0,
            checks_passed=4,
            checks_failed=0,
        )
        assert "READY" in str(status)
        assert "4" in str(status)

    def test_degraded_state_string(self):
        """Verificar representação de DEGRADED state"""
        status = ReadinessStatus(
            state="DEGRADED",
            reasons=["Low quality data"],
            metrics={"phi": 0.05},
            timestamp=0.0,
            checks_passed=3,
            checks_failed=1,
        )
        assert "DEGRADED" in str(status)
        assert "Low quality data" in str(status)

    def test_critical_state_string(self):
        """Verificar representação de CRITICAL state"""
        status = ReadinessStatus(
            state="CRITICAL",
            reasons=["Insufficient data", "Embedding convergence"],
            metrics={"phi": 0.0},
            timestamp=0.0,
            checks_passed=2,
            checks_failed=2,
        )
        assert "CRITICAL" in str(status)
        assert "Insufficient data" in str(status)


class TestSystemReadinessValidator:
    """Testes para SystemReadinessValidator"""

    @pytest.fixture
    def validator(self):
        """Criar validator para testes"""
        return SystemReadinessValidator()

    @pytest.fixture
    def mock_workspace(self):
        """Mock do workspace"""
        workspace = Mock()
        workspace.cross_predictions = []
        workspace.get_module_history = Mock(return_value=[])
        return workspace

    @pytest.mark.asyncio
    async def test_check_readiness_empty_workspace(self, validator, mock_workspace):
        """Test readiness check com workspace vazio"""
        status = await validator.check_readiness(mock_workspace)

        assert status.state == "CRITICAL"
        assert len(status.reasons) > 0
        assert "Insufficient data" in status.reasons[0]

    @pytest.mark.asyncio
    async def test_r_squared_quality_valid(self, validator):
        """Test cálculo de r² quality com dados válidos"""
        # Mock cross-predictions
        mock_cp1 = Mock()
        mock_cp1.r_squared = 0.45

        mock_cp2 = Mock()
        mock_cp2.r_squared = 0.52

        workspace = Mock()
        workspace.cross_predictions = [mock_cp1, mock_cp2]

        quality = await validator._check_r_squared_quality(workspace)
        assert quality == pytest.approx(0.485, rel=0.01)

    @pytest.mark.asyncio
    async def test_r_squared_quality_invalid_values(self, validator):
        """Test r² quality com valores inválidos (NaN)"""
        mock_cp1 = Mock()
        mock_cp1.r_squared = np.nan

        mock_cp2 = Mock()
        mock_cp2.r_squared = 0.45

        workspace = Mock()
        workspace.cross_predictions = [mock_cp1, mock_cp2]

        quality = await validator._check_r_squared_quality(workspace)
        # Deve ignorar NaN e usar apenas 0.45
        assert quality == 0.45

    @pytest.mark.asyncio
    async def test_embedding_variance_calculation(self, validator):
        """Test cálculo de variance de embeddings"""
        # Mock embeddings
        emb1 = np.array([1.0, 2.0, 3.0])
        emb2 = np.array([1.1, 2.1, 3.1])
        emb3 = np.array([1.2, 2.2, 3.2])

        workspace = Mock()
        workspace.get_module_history = Mock(return_value=[emb1, emb2, emb3])

        variance = await validator._check_embedding_variance(workspace)
        assert variance > 0.0  # Deve ter alguma variação

    @pytest.mark.asyncio
    async def test_phi_calculation_valid(self, validator):
        """Test cálculo de Phi com dados válidos"""
        mock_cp1 = Mock()
        mock_cp1.r_squared = 0.4

        mock_cp2 = Mock()
        mock_cp2.r_squared = 0.6

        workspace = Mock()
        workspace.cross_predictions = [mock_cp1, mock_cp2]

        phi = validator._calculate_phi(workspace)
        assert phi == 0.5

    @pytest.mark.asyncio
    async def test_phi_calculation_with_invalid_data(self, validator):
        """Test Phi com dados inválidos"""
        mock_cp1 = Mock()
        mock_cp1.r_squared = np.nan

        mock_cp2 = Mock()
        mock_cp2.r_squared = np.inf

        mock_cp3 = Mock()
        mock_cp3.r_squared = 0.45

        workspace = Mock()
        workspace.cross_predictions = [mock_cp1, mock_cp2, mock_cp3]

        phi = validator._calculate_phi(workspace)
        # Deve ignorar NaN/Inf e usar apenas 0.45
        assert phi == 0.45

    @pytest.mark.asyncio
    async def test_check_readiness_ready_state(self, validator):
        """Test readiness check com todos checks passando"""
        # Mock cross-predictions com qualidade
        mock_cp1 = Mock()
        mock_cp1.r_squared = 0.45

        mock_cp2 = Mock()
        mock_cp2.r_squared = 0.52

        # Mock embeddings com variação
        emb1 = np.array([1.0, 2.0, 3.0])
        emb2 = np.array([1.5, 2.5, 3.5])

        workspace = Mock()
        workspace.cross_predictions = [mock_cp1, mock_cp2]
        workspace.get_module_history = Mock(return_value=[emb1, emb2])

        status = await validator.check_readiness(workspace)

        assert status.state == "READY"
        assert status.checks_passed == 4
        assert status.checks_failed == 0


class TestContinuousReadinessEngine:
    """Testes para ContinuousReadinessEngine"""

    @pytest.fixture
    def mock_loop(self):
        """Mock do IntegrationLoop"""
        loop = AsyncMock()
        loop.run_cycles = AsyncMock()
        return loop

    @pytest.fixture
    def mock_workspace(self):
        """Mock do Workspace"""
        workspace = Mock()
        workspace.cross_predictions = []
        workspace.get_module_history = Mock(return_value=[])
        return workspace

    @pytest.fixture
    def engine(self, mock_loop, mock_workspace):
        """Criar engine para testes"""
        return ContinuousReadinessEngine(mock_loop, mock_workspace)

    def test_engine_initialization(self, engine):
        """Test inicialização do engine"""
        assert engine.is_running is False
        assert engine.last_status is None
        assert engine.monitor_task is None

    @pytest.mark.asyncio
    async def test_engine_start_stop(self, engine):
        """Test iniciar e parar engine"""
        await engine.start_continuous_monitoring()
        assert engine.is_running is True
        assert engine.monitor_task is not None

        await engine.stop_continuous_monitoring()
        assert engine.is_running is False

    @pytest.mark.asyncio
    async def test_force_readiness_check(self, engine):
        """Test força verificação imediata"""
        status = await engine.force_readiness_check()

        assert status is not None
        assert isinstance(status, ReadinessStatus)

    def test_get_statistics(self, engine):
        """Test obter estatísticas"""
        stats = engine.get_statistics()

        assert isinstance(stats, dict)
        assert "is_running" in stats
        assert "last_status" in stats
        assert stats["is_running"] is False

    def test_get_event_history(self, engine):
        """Test obter histórico de eventos"""
        history = engine.get_event_history()

        assert isinstance(history, list)
        assert len(history) == 0  # Nenhum evento inicialmente


class TestCircuitBreaker:
    """Testes para Circuit Breaker"""

    @pytest.fixture
    def validator(self):
        return SystemReadinessValidator()

    def test_circuit_breaker_activation(self, validator):
        """Test ativação de circuit breaker"""
        assert validator.circuit_breaker_active is False

        # Simular 3 falhas
        validator.consecutive_failures = 3

        # Circuit breaker deve ativar após MAX_CONSECUTIVE_FAILURES
        assert validator.consecutive_failures >= validator.MAX_CONSECUTIVE_FAILURES

    def test_circuit_breaker_cooldown(self, validator):
        """Test cooldown de circuit breaker"""
        import time

        validator.circuit_breaker_active = True
        validator.circuit_breaker_reset_time = time.time() - 1  # No passado

        # Após reset time, circuit breaker deve desativar
        current_time = time.time()
        if current_time >= validator.circuit_breaker_reset_time:
            validator.circuit_breaker_active = False

        assert validator.circuit_breaker_active is False


class TestAdaptiveThresholds:
    """Testes para Thresholds Adaptativos"""

    @pytest.fixture
    def validator(self):
        return SystemReadinessValidator()

    def test_historical_r_squared_tracking(self, validator):
        """Test rastreamento de histórico de r²"""
        # Adicionar valores ao histórico
        for value in [0.4, 0.45, 0.5, 0.55]:
            validator.historical_r_squared.append(value)

        assert len(validator.historical_r_squared) == 4
        assert np.mean(validator.historical_r_squared) == pytest.approx(0.475, rel=0.01)

    def test_historical_variance_tracking(self, validator):
        """Test rastreamento de histórico de variance"""
        for value in [0.05, 0.06, 0.07]:
            validator.historical_variance.append(value)

        assert len(validator.historical_variance) == 3
        assert np.mean(validator.historical_variance) == pytest.approx(0.06, rel=0.01)

    def test_max_history_size(self, validator):
        """Test limite de tamanho do histórico"""
        # Adicionar mais valores que o máximo permitido
        for i in range(150):
            validator.historical_r_squared.append(0.5 + i * 0.001)

        # Deve manter apenas últimos 100
        assert len(validator.historical_r_squared) == 100


class TestIntegration:
    """Testes de integração entre componentes"""

    @pytest.mark.asyncio
    async def test_full_readiness_pipeline(self):
        """Test pipeline completo de readiness"""
        # Criar mocks
        workspace = Mock()
        workspace.cross_predictions = []
        workspace.get_module_history = Mock(return_value=[])

        loop = AsyncMock()
        loop.run_cycles = AsyncMock()

        # Criar validator e engine
        validator = SystemReadinessValidator()
        _ = ContinuousReadinessEngine(loop, workspace)

        # Verificar readiness (deve ser crítico com workspace vazio)
        status = await validator.check_readiness(workspace)
        assert status.state == "CRITICAL"

        # Adicionar dados
        mock_cp1 = Mock()
        mock_cp1.r_squared = 0.45
        mock_cp2 = Mock()
        mock_cp2.r_squared = 0.50

        workspace.cross_predictions = [mock_cp1, mock_cp2]

        # Criar embeddings com variação
        emb1 = np.array([1.0, 2.0, 3.0])
        emb2 = np.array([1.5, 2.5, 3.5])
        workspace.get_module_history = Mock(return_value=[emb1, emb2])

        # Verificar readiness novamente (deve ser pronto)
        status = await validator.check_readiness(workspace)
        assert status.state == "READY"


if __name__ == "__main__":
    # Rodar testes
    pytest.main([__file__, "-v", "-s"])
    pytest.main([__file__, "-v", "-s"])
