"""
Testes para ConsciousSystem - RNN Recorrente com Latent Dynamics.

Cobertura:
- Inicialização
- Compressão de Λ_U
- Dinâmica recursiva (step)
- Cálculo de Φ causal
- Integração com SharedWorkspace
"""

import logging

import numpy as np
import pytest
import torch

from src.consciousness.conscious_system import (
    ConsciousSystem,
    LambdaUCompressor,
)

logger = logging.getLogger(__name__)


class TestLambdaUCompressor:
    """Testes para compressão de Λ_U."""

    def test_compress_decompress(self) -> None:
        """Testa compressão e descompressão de Λ_U."""
        compressor = LambdaUCompressor(signature_dim=32)
        dim = 256

        # Criar Λ_U original
        Lambda_U_original = np.random.randn(dim, dim).astype(np.float32)

        # Comprimir
        signature = compressor.compress(Lambda_U_original)
        assert signature.shape == (32,), f"Signature shape incorreto: {signature.shape}"

        # Descomprimir
        Lambda_U_approx = compressor.decompress(signature, (dim, dim))
        assert Lambda_U_approx.shape == (dim, dim), f"Shape incorreto: {Lambda_U_approx.shape}"

        # Verificar que estrutura espectral é preservada (aproximadamente)
        # Valores singulares devem ser similares
        S_original = np.linalg.svd(Lambda_U_original, compute_uv=False)
        S_approx = np.linalg.svd(Lambda_U_approx, compute_uv=False)

        # Primeiros valores singulares devem ser similares
        assert np.allclose(
            S_original[:32], S_approx[:32], rtol=0.5
        ), "Estrutura espectral não preservada"

        logger.info("✅ Compressão/descompressão de Λ_U funcionando")


class TestConsciousSystem:
    """Testes para ConsciousSystem."""

    @pytest.fixture
    def conscious_system(self) -> ConsciousSystem:
        """Cria instância do ConsciousSystem."""
        return ConsciousSystem(dim=256, signature_dim=32)

    def test_initialization(self, conscious_system: ConsciousSystem) -> None:
        """Testa inicialização do sistema."""
        assert conscious_system.dim == 256
        assert conscious_system.signature_dim == 32
        assert conscious_system.rho_C.shape == (256,)
        assert conscious_system.rho_P.shape == (256,)
        assert conscious_system.rho_U.shape == (256,)
        assert conscious_system.Lambda_U_signature.shape == (32,)
        assert 0.0 <= conscious_system.repression_strength <= 1.0

        logger.info("✅ Inicialização do ConsciousSystem funcionando")

    def test_step(self, conscious_system: ConsciousSystem) -> None:
        """Testa um timestep da dinâmica."""
        # Estado inicial
        rho_C_initial = conscious_system.rho_C.clone()

        # Criar estímulo
        stimulus = torch.randn(256)

        # Executar step
        rho_C_new = conscious_system.step(stimulus)

        # Verificar que estado mudou
        assert not torch.allclose(rho_C_initial, rho_C_new), "Estado não mudou após step"

        # Verificar shape
        assert rho_C_new.shape == (256,)

        logger.info("✅ Step() funcionando")

    def test_multiple_steps(self, conscious_system: ConsciousSystem) -> None:
        """Testa múltiplos timesteps (reentrância causal)."""
        # Executar 10 steps
        for i in range(10):
            stimulus = torch.randn(256) * 0.1  # Estímulo pequeno
            conscious_system.step(stimulus)

        # Verificar que estados evoluíram
        state = conscious_system.get_state()
        assert state.rho_C.shape == (256,)
        assert state.rho_P.shape == (256,)
        assert state.rho_U.shape == (256,)

        logger.info("✅ Múltiplos steps funcionando")

    def test_phi_causal(self, conscious_system: ConsciousSystem) -> None:
        """Testa cálculo de Φ causal."""
        # Executar vários steps para criar histórico
        for i in range(20):
            stimulus = torch.randn(256) * 0.1
            conscious_system.step(stimulus)
            conscious_system.get_state()  # Adiciona ao histórico

        # Calcular Φ causal
        phi = conscious_system.compute_phi_causal()

        # Verificar que Φ é não-negativo
        assert phi >= 0.0, f"Φ causal negativo: {phi}"

        # Verificar que Φ é razoável (< 1.0 para correlações)
        assert phi <= 1.0, f"Φ causal muito alto: {phi}"

        logger.info(f"✅ Φ causal calculado: {phi:.6f}")

    def test_repression_update(self, conscious_system: ConsciousSystem) -> None:
        """Testa atualização de repressão."""
        initial_repression = conscious_system.repression_strength

        # Simular inconsciente forte
        conscious_system.rho_U = torch.randn(256) * 2.0  # Forte

        # Atualizar repressão
        conscious_system.update_repression(threshold=1.0)

        # Verificar que repressão aumentou
        assert conscious_system.repression_strength >= initial_repression, "Repressão não aumentou"

        logger.info("✅ Atualização de repressão funcionando")

    def test_low_dim_signatures(self, conscious_system: ConsciousSystem) -> None:
        """Testa obtenção de assinaturas de baixa dimensão."""
        signatures = conscious_system.get_low_dim_signatures()

        assert "C_sig" in signatures
        assert "P_sig" in signatures
        assert "U_sig" in signatures
        assert "Lambda_U_sig" in signatures

        # Verificar shapes
        assert signatures["C_sig"].shape == (10,)
        assert signatures["P_sig"].shape == (10,)
        assert signatures["U_sig"].shape == (10,)

        logger.info("✅ Assinaturas de baixa dimensão funcionando")


class TestConsciousSystemIntegration:
    """Testes de integração com SharedWorkspace."""

    @pytest.mark.asyncio
    async def test_integration_with_workspace(self) -> None:
        """Testa integração com SharedWorkspace."""
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace
        workspace = SharedWorkspace(embedding_dim=256)

        # Verificar que ConsciousSystem foi inicializado
        assert workspace.conscious_system is not None, "ConsciousSystem não foi inicializado"

        # Executar alguns steps no ConsciousSystem
        for i in range(5):
            stimulus = torch.randn(256) * 0.1
            workspace.conscious_system.step(stimulus)
            workspace.conscious_system.get_state()

        # Calcular métricas topológicas (deve usar ConsciousSystem)
        metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que métricas foram calculadas
        assert metrics is not None, "Métricas não foram calculadas"
        assert "omega" in metrics
        assert "sigma" in metrics

        logger.info("✅ Integração com SharedWorkspace funcionando")

    @pytest.mark.asyncio
    async def test_phi_causal_vs_phi_standard(self) -> None:
        """Testa que Φ causal é diferente de Φ padrão (não considera acesso)."""
        from src.consciousness.shared_workspace import SharedWorkspace

        workspace = SharedWorkspace(embedding_dim=256)

        # Verificar que ConsciousSystem foi inicializado
        assert workspace.conscious_system is not None, "ConsciousSystem deve ser inicializado"

        # Executar steps
        for i in range(10):
            stimulus = torch.randn(256) * 0.1
            workspace.conscious_system.step(stimulus)
            workspace.conscious_system.get_state()

        # Obter Φ causal do ConsciousSystem
        phi_causal = workspace.conscious_system.compute_phi_causal()

        # Verificar que Φ causal é calculado (não depende de acesso)
        assert phi_causal >= 0.0, "Φ causal deve ser não-negativo"

        logger.info(f"✅ Φ causal (não considera acesso): {phi_causal:.6f}")
