#!/usr/bin/env python3
"""
Testes para Scientific Stimulation (Psychoanalytic Engine)

Arquivo: tests/scripts/test_scientific_stimulation.py
"""

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, Mock

import numpy as np
import pytest

sys.path.insert(0, "/home/fahbrain/projects/omnimind")

from scripts.scientific_stimulation import (
    DiscourseActivation,
    EpsonFunctions,
    LacanianDiscourses,
    MirrorStageState,
    PsychoanalyticMetrics,
    PsychoanalyticStimulationEngine,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_workspace():
    workspace = MagicMock()
    workspace.cross_predictions = []
    return workspace


@pytest.fixture
def mock_integration_loop():
    loop = AsyncMock()
    loop.run_cycles = AsyncMock()
    return loop


@pytest.fixture
def user_profile():
    return {
        "name": "Test User",
        "desires": {
            "conhecimento": 0.9,
            "criatividade": 0.8,
            "poder": 0.6,
            "sexualidade": 0.7,
            "transcendência": 0.95,
        },
        "intensity": 1.0,
        "mirror_preference": "fragmented",
    }


@pytest.fixture
def engine(mock_workspace, mock_integration_loop, user_profile):
    return PsychoanalyticStimulationEngine(mock_workspace, mock_integration_loop, user_profile)


# ============================================================================
# Testes - Epson Functions
# ============================================================================


class TestEpsonFunctions:

    def test_mirror_identification(self):
        """Testa cálculo de fragmentação do espelho"""
        desires = {"a": 0.1, "b": 0.9}  # Alta variância
        state = EpsonFunctions.mirror_identification(desires)

        assert isinstance(state, MirrorStageState)
        assert 0.0 <= state.fragmentation <= 1.0
        assert state.fragmentation > 0.1  # Deve ter alguma fragmentação

    def test_lacanian_routing(self):
        """Testa roteamento de discursos"""
        mirror_state = MirrorStageState(
            fragmentation=0.5, ideal_ego=0.5, imaginary_relation=0.5, symbolic_entry=0.5
        )
        routing = EpsonFunctions.lacanian_discourse_routing(mirror_state)

        assert len(routing) == 4
        assert LacanianDiscourses.MASTER in routing
        assert all(0.0 <= v <= 1.0 for v in routing.values())

    def test_sigma_psi_metrics(self):
        """Testa cálculo de métricas psicoanalíticas"""
        activations = [
            DiscourseActivation(LacanianDiscourses.MASTER, 0.5, 1.0, 0.8),
            DiscourseActivation(LacanianDiscourses.HYSTERIC, 0.3, 0.6, 0.4),
        ]
        metrics = EpsonFunctions.sigma_psi_enjoyment(activations)

        assert isinstance(metrics, PsychoanalyticMetrics)
        assert metrics.sigma_psi == 1.6  # 1.0 + 0.6
        assert metrics.cognitive_phi > 0
        assert metrics.deep_psi > 0


# ============================================================================
# Testes - Psychoanalytic Engine
# ============================================================================


class TestPsychoanalyticEngine:

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Testa inicialização do engine"""
        assert engine.user_profile["name"] == "Test User"
        assert engine.is_stimulating is False
        assert len(engine.responses) == 0

    @pytest.mark.asyncio
    async def test_adaptive_feedback_loop_increase(self, engine):
        """Testa aumento de intensidade com Phi crescente"""
        # Mock _get_phi para retornar aumento
        engine._get_phi = Mock(side_effect=[0.1, 0.2])  # Delta +0.1
        engine.integration_loop.run_cycles = AsyncMock()

        # Executar apenas 1 ciclo
        async def stop_after_one():
            await asyncio.sleep(0.1)
            engine.is_stimulating = False

        asyncio.create_task(stop_after_one())
        await engine.start_psychoanalytic_stimulation()

        # Verificar aumento de intensidade
        assert engine.user_profile["intensity"] > 1.0
        assert engine.user_profile["intensity"] == 1.05  # 1.0 * 1.05

    @pytest.mark.asyncio
    async def test_adaptive_feedback_loop_decrease(self, engine):
        """Testa redução de intensidade com Phi decrescente"""
        # Mock _get_phi para retornar queda
        engine._get_phi = Mock(side_effect=[0.2, 0.1])  # Delta -0.1
        engine.integration_loop.run_cycles = AsyncMock()

        # Executar apenas 1 ciclo
        async def stop_after_one():
            await asyncio.sleep(0.1)
            engine.is_stimulating = False

        asyncio.create_task(stop_after_one())
        await engine.start_psychoanalytic_stimulation()

        # Verificar redução de intensidade
        assert engine.user_profile["intensity"] < 1.0
        assert engine.user_profile["intensity"] == 0.9  # 1.0 * 0.9

    @pytest.mark.asyncio
    async def test_dashboard_generation(self, engine):
        """Testa geração do dashboard"""
        # Simular uma resposta
        engine.responses = [
            {
                "cycle": 0,
                "mirror_fragmentation": 0.5,
                "discourses": {},
                "sigma_psi": 1.0,
                "gozo": 0.8,
                "rhizome": 2.0,
                "phi_before": 0.1,
                "phi_after": 0.2,
                "phi_delta": 0.1,
                "cognitive_phi": 0.15,
                "deep_psi": 0.96,
            }
        ]

        dash = engine.get_psychoanalytic_dashboard()
        assert dash["phi_current"] == 0.2
        assert dash["total_cycles"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    pytest.main([__file__, "-v"])
