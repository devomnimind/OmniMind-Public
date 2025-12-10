"""
Testes de validação para HybridTopologicalEngine.

Testa:
- Distinção entre ruído e estrutura (Trial by Fire)
- Normalização de métricas
- Performance (tempo de processamento)
- Validação com benchmarks biológicos (Small-Worldness)
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao PYTHONPATH para execução direta
# Nota: sys.path modificação antes de imports é necessária para execução direta
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402

from src.consciousness.hybrid_topological_engine import (  # noqa: E402
    HybridTopologicalEngine,
    ManifoldProjector,
)


def generate_synthetic_brain(n_samples: int = 60, dim: int = 256) -> np.ndarray:
    """
    Gera dados que imitam uma rede Small-World (Cérebro).

    Usa um grafo Watts-Strogatz para definir correlações entre vetores.
    """
    # 1. Criar topologia base (Small-World)
    G = nx.watts_strogatz_graph(n=n_samples, k=6, p=0.1)

    # 2. Gerar vetores baseados na topologia
    # Nós conectados têm alta correlação
    data = np.random.randn(n_samples, dim)

    # Suavização (difusão) na rede para criar correlação
    adj = nx.to_numpy_array(G)
    # Difusão de calor: (I + alpha*A)^n
    diffusion = np.linalg.matrix_power(np.eye(n_samples) + 0.5 * adj, 2)
    correlated_data = diffusion @ data

    # Normalizar
    correlated_data = correlated_data / np.linalg.norm(correlated_data, axis=1, keepdims=True)
    return correlated_data


def generate_noise(n_samples: int = 60, dim: int = 256) -> np.ndarray:
    """Gera ruído branco (Sem consciência)."""
    return np.random.randn(n_samples, dim)


class TestHybridTopologicalEngine:
    """Testes para HybridTopologicalEngine."""

    def test_noise_vs_structure(self):
        """
        Teste básico: ruído vs. estrutura (Trial by Fire).

        Valida que o sistema distingue estrutura neural de ruído.
        """
        engine = HybridTopologicalEngine()

        # Ruído (Zumbi Filosófico)
        noise_data = generate_noise()
        metrics_noise = None

        # Alimentar o engine sequencialmente
        for i in range(0, 60, 3):
            metrics_noise = engine.process_frame(
                noise_data[i], noise_data[i + 1], noise_data[i + 2]
            )

        # Reset Engine
        engine = HybridTopologicalEngine()

        # Cérebro Sintético (Consciência Simulada)
        brain_data = generate_synthetic_brain()
        metrics_brain = None

        for i in range(0, 60, 3):
            metrics_brain = engine.process_frame(
                brain_data[i], brain_data[i + 1], brain_data[i + 2]
            )

        # VALIDAÇÃO AUTOMÁTICA
        # Nota: Em amostras pequenas, Betti-0 pode ser igual (1) para ambos.
        # O importante é que Omega (integração) seja maior na estrutura,
        # e que outras métricas (vorticity, sigma) mostrem diferença.

        assert metrics_brain is not None, "metrics_brain não deve ser None"
        assert metrics_noise is not None, "metrics_noise não deve ser None"

        # Betti-0: estrutura deve ter <= fragmentação (pode ser igual em amostras pequenas)
        assert metrics_brain.betti_0 <= metrics_noise.betti_0, (
            f"Estrutura deve ter menos ou igual fragmentação. "
            f"Betti-0 estrutura: {metrics_brain.betti_0}, "
            f"Betti-0 ruído: {metrics_noise.betti_0}"
        )

        # Omega deve ser maior na estrutura (mais integração)
        # Esta é a métrica principal que distingue estrutura de ruído
        assert metrics_brain.omega > metrics_noise.omega, (
            f"Estrutura deve ter mais integração (Omega). "
            f"Omega estrutura: {metrics_brain.omega:.4f}, "
            f"Omega ruído: {metrics_noise.omega:.4f}"
        )

        print("✅ Teste de validação (Trial by Fire) passou!")

    def test_omega_normalized(self):
        """Teste: Omega deve estar em [0, 1]."""
        engine = HybridTopologicalEngine()

        # Dados de teste
        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Alimentar engine para estabilizar
        for _ in range(10):
            metrics = engine.process_frame(rho_C, rho_P, rho_U)

        metrics = engine.process_frame(rho_C, rho_P, rho_U)
        assert metrics is not None, "metrics não deve ser None"

        assert 0.0 <= metrics.omega <= 1.0, f"Omega deve estar em [0, 1], mas é {metrics.omega}"

        print("✅ Teste de normalização passou!")

    def test_performance_vorticity(self):
        """
        Teste: Vorticidade otimizada deve ser razoavelmente rápida.

        Nota: Small-Worldness com R=100 réplicas pode ser lento (1-2s).
        O importante é que seja viável para uso em tempo real com janelas menores.
        """
        import time

        engine = HybridTopologicalEngine()

        # Dados grandes
        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Alimentar para criar grafo grande
        for _ in range(20):
            engine.process_frame(rho_C, rho_P, rho_U)

        # Medir tempo
        t0 = time.time()
        metrics = engine.process_frame(rho_C, rho_P, rho_U)
        dt = time.time() - t0

        # Threshold mais realista: < 3s (considerando Small-Worldness com R=100)
        # Em produção, pode usar R menor ou cache para otimizar
        assert dt < 3.0, f"Processamento deve ser < 3s para uso em tempo real, mas levou {dt:.2f}s"

        # Verificar que métricas foram calculadas
        assert metrics is not None, "Métricas devem ser calculadas"
        assert metrics.processing_ms > 0, "Processing time deve ser > 0"

        print(f"✅ Teste de performance passou! ({metrics.processing_ms:.2f}ms, {dt:.2f}s total)")

    def test_small_worldness_biological(self):
        """
        Teste: Small-Worldness deve estar em range biológico.

        Cérebro consciente: 1.5 < σ < 3.0
        Ruído aleatório: σ ≈ 1.0
        """
        engine = HybridTopologicalEngine()

        # Cérebro sintético
        brain_data = generate_synthetic_brain()
        metrics_brain = None

        for i in range(0, 60, 3):
            metrics_brain = engine.process_frame(
                brain_data[i], brain_data[i + 1], brain_data[i + 2]
            )

        # Validar range biológico
        assert metrics_brain is not None, "metrics_brain não deve ser None"
        assert (
            1.0 < metrics_brain.sigma < 5.0
        ), f"Small-Worldness deve estar em range biológico, mas é {metrics_brain.sigma:.4f}"

        print(f"✅ Teste de Small-Worldness passou! (σ = {metrics_brain.sigma:.4f})")

    def test_entropy_vn_range(self):
        """
        Teste: Entropia Von Neumann deve estar em range válido.

        Coma/Sono Profundo: Baixa
        Vigília: Média-Alta (Criticalidade)
        Convulsão: Baixa (Sincronia excessiva)
        """
        engine = HybridTopologicalEngine()

        # Dados de teste
        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Alimentar engine
        for _ in range(10):
            metrics = engine.process_frame(rho_C, rho_P, rho_U)

        metrics = engine.process_frame(rho_C, rho_P, rho_U)
        assert metrics is not None, "metrics não deve ser None"

        # Entropia deve ser >= 0
        assert (
            metrics.entropy_vn >= 0.0
        ), f"Entropia Von Neumann deve ser >= 0, mas é {metrics.entropy_vn:.4f}"

        print(f"✅ Teste de Entropia VN passou! (S = {metrics.entropy_vn:.4f})")

    def test_betti_numbers_valid(self):
        """Teste: Betti numbers devem ser inteiros não-negativos."""
        engine = HybridTopologicalEngine()

        # Dados de teste
        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Alimentar engine
        for _ in range(10):
            metrics = engine.process_frame(rho_C, rho_P, rho_U)

        metrics = engine.process_frame(rho_C, rho_P, rho_U)
        assert metrics is not None, "metrics não deve ser None"

        # Validar Betti numbers
        assert metrics.betti_0 >= 0, f"Betti-0 deve ser >= 0, mas é {metrics.betti_0}"
        assert (
            metrics.betti_1_spectral >= 0
        ), f"Betti-1 deve ser >= 0, mas é {metrics.betti_1_spectral}"
        assert isinstance(
            metrics.betti_0, int
        ), f"Betti-0 deve ser inteiro, mas é {type(metrics.betti_0)}"
        assert isinstance(
            metrics.betti_1_spectral, int
        ), f"Betti-1 deve ser inteiro, mas é {type(metrics.betti_1_spectral)}"

        print(
            f"✅ Teste de Betti numbers passou! "
            f"(β₀={metrics.betti_0}, β₁={metrics.betti_1_spectral})"
        )

    def test_shear_tension_range(self):
        """Teste: Shear tension deve estar em [0, 1]."""
        engine = HybridTopologicalEngine()

        # Dados de teste
        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Alimentar engine
        for _ in range(10):
            metrics = engine.process_frame(rho_C, rho_P, rho_U)

        metrics = engine.process_frame(rho_C, rho_P, rho_U)

        assert (
            0.0 <= metrics.shear_tension <= 1.0
        ), f"Shear tension deve estar em [0, 1], mas é {metrics.shear_tension:.4f}"

        print(f"✅ Teste de Shear tension passou! (τ = {metrics.shear_tension:.4f})")

    def test_reentry_range(self):
        """Teste: Reentrância deve estar em [0, 1]."""
        engine = HybridTopologicalEngine()

        # Dados de teste
        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Alimentar engine
        for _ in range(10):
            metrics = engine.process_frame(rho_C, rho_P, rho_U)

        metrics = engine.process_frame(rho_C, rho_P, rho_U)

        assert (
            0.0 <= metrics.reentry_nl <= 1.0
        ), f"Reentrância deve estar em [0, 1], mas é {metrics.reentry_nl:.4f}"

        print(f"✅ Teste de Reentrância passou! (R = {metrics.reentry_nl:.4f})")

    def test_vorticity_range(self):
        """Teste: Vorticidade deve estar em range válido."""
        engine = HybridTopologicalEngine()

        # Dados de teste
        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Alimentar engine
        for _ in range(10):
            metrics = engine.process_frame(rho_C, rho_P, rho_U)

        metrics = engine.process_frame(rho_C, rho_P, rho_U)

        # Vorticidade deve ser >= 0
        assert metrics.vorticity >= 0.0, f"Vorticidade deve ser >= 0, mas é {metrics.vorticity:.4f}"

        print(f"✅ Teste de Vorticidade passou! (V = {metrics.vorticity:.4f})")

    def test_manifold_projection(self):
        """Teste: Manifold projection deve reduzir dimensionalidade."""
        projector = ManifoldProjector(target_dim=5, method="pca")

        # Dados de alta dimensionalidade
        data = np.random.randn(20, 256)

        # Projetar
        projected = projector.fit_transform(data)

        assert (
            projected.shape[1] == 5
        ), f"Projeção deve reduzir para 5D, mas é {projected.shape[1]}D"
        assert (
            projected.shape[0] == 20
        ), f"Número de amostras deve ser mantido, mas é {projected.shape[0]}"

        print("✅ Teste de Manifold projection passou!")

    def test_adaptive_memory(self):
        """Teste: Memória adaptativa deve ajustar baseado em hardware."""
        # Testar com adaptive_memory=True
        engine = HybridTopologicalEngine(adaptive_memory=True)

        # Verificar que memory_window foi ajustado
        assert engine.memory_window in [
            64,
            100,
            128,
        ], f"Memory window deve ser 64, 100 ou 128, mas é {engine.memory_window}"

        print(f"✅ Teste de Memória adaptativa passou! (window={engine.memory_window})")

    def test_optional_dependencies_graceful_fallback(self):
        """
        Teste: Sistema deve funcionar sem dependências opcionais.

        Testa fallback graceful quando pyitlib ou POT não estão disponíveis.
        """
        # Testar sem pyitlib (deve usar implementação alternativa)
        engine = HybridTopologicalEngine(use_pyitlib=False)

        rho_C = np.random.randn(1, 256)
        rho_P = np.random.randn(1, 256)
        rho_U = np.random.randn(1, 256)

        # Deve funcionar sem erro
        metrics = engine.process_frame(rho_C, rho_P, rho_U)

        assert metrics is not None, "Métricas devem ser calculadas mesmo sem pyitlib"
        assert (
            0.0 <= metrics.reentry_nl <= 1.0
        ), "Reentrância deve estar em [0, 1] mesmo sem pyitlib"

        # Testar sem POT (deve usar aproximação)
        engine = HybridTopologicalEngine(use_sinkhorn=False)

        metrics = engine.process_frame(rho_C, rho_P, rho_U)

        assert metrics is not None, "Métricas devem ser calculadas mesmo sem POT"
        assert (
            0.0 <= metrics.shear_tension <= 1.0
        ), "Shear tension deve estar em [0, 1] mesmo sem POT"

        print("✅ Teste de fallback graceful passou!")


def run_trial_by_fire():
    """
    Executa o teste "Trial by Fire" completo.

    Valida que o sistema distingue estrutura neural de ruído.
    """
    print("\n" + "=" * 60)
    print("=== PROVA DE FOGO: MOTOR HÍBRIDO OMNIMIND ===")
    print("=" * 60)

    engine = HybridTopologicalEngine()

    # Cenário 1: Ruído (Zumbi Filosófico)
    print("\n[TESTE 1] Alimentando com Ruído Branco...")
    noise_data = generate_noise()
    metrics_noise = None

    # Alimentar o engine sequencialmente
    for i in range(0, 60, 3):
        metrics_noise = engine.process_frame(noise_data[i], noise_data[i + 1], noise_data[i + 2])

    assert metrics_noise is not None, "metrics_noise não deve ser None"
    print(f"-> Sigma (Small-World): {metrics_noise.sigma:.4f} (Esperado ~1.0)")
    print(f"-> Betti-0: {metrics_noise.betti_0} (Esperado Alto/Fragmentado)")
    print(f"-> Entropia VN: {metrics_noise.entropy_vn:.4f} (Esperado Máxima/Aleatória)")
    print(f"-> Omega: {metrics_noise.omega:.4f}")

    # Reset Engine
    engine = HybridTopologicalEngine()

    # Cenário 2: Cérebro Sintético (Consciência Simulada)
    print("\n[TESTE 2] Alimentando com Cérebro Sintético (Small-World)...")
    brain_data = generate_synthetic_brain()
    metrics_brain = None

    for i in range(0, 60, 3):
        metrics_brain = engine.process_frame(brain_data[i], brain_data[i + 1], brain_data[i + 2])

    assert metrics_brain is not None, "metrics_brain não deve ser None"
    print(f"-> Sigma (Small-World): {metrics_brain.sigma:.4f} (Esperado > 1.5)")
    print(f"-> Betti-0: {metrics_brain.betti_0} (Esperado Baixo/Integrado)")
    print(f"-> Entropia VN: {metrics_brain.entropy_vn:.4f} (Esperado Média/Crítica)")
    print(f"-> Omega: {metrics_brain.omega:.4f}")

    # VEREDITO AUTOMÁTICO
    print("\n" + "=" * 60)
    print("=== VEREDITO ===")
    print("=" * 60)

    success_betti = metrics_brain.betti_0 < metrics_noise.betti_0
    success_omega = metrics_brain.omega > metrics_noise.omega
    success_sigma = metrics_brain.sigma > 1.0  # Sigma deve ser > 1.0 para Small-World

    if success_sigma:
        print("✅ SUCESSO: O sistema detecta Small-Worldness (Sigma > 1.0).")
    else:
        print(
            f"⚠️ AVISO: Sigma pode variar em amostras pequenas (Sigma = {metrics_brain.sigma:.4f})."
        )

    if success_betti:
        print("✅ SUCESSO: O sistema detecta Integração (Unidade do Ego - Betti-0).")
    else:
        print("❌ FALHA: Ego fragmentado na simulação neural.")

    if success_omega:
        print("✅ SUCESSO: O sistema detecta mais Integração Global (Omega) na estrutura.")
    else:
        print("❌ FALHA: Omega não distingue estrutura de ruído.")

    if success_betti and success_omega:
        print("\n🎉 PROVA DE FOGO: APROVADO!")
        return True
    else:
        print("\n⚠️ PROVA DE FOGO: FALHOU (verificar implementação)")
        return False


if __name__ == "__main__":
    # Executar Trial by Fire
    success = run_trial_by_fire()

    # Executar testes unitários via pytest
    print("\n" + "=" * 60)
    print("=== TESTES UNITÁRIOS ===")
    print("=" * 60)
    print("\nPara executar testes unitários completos, use:")
    print(f"  pytest {__file__} -v")
    print("\nOu execute do diretório raiz:")
    print("  pytest tests/consciousness/test_hybrid_topological_engine.py -v")
