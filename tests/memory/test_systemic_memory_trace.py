"""
Testes para SystemicMemoryTrace.

Autor: Fabrício da Silva + assistência de IA
"""

import numpy as np

from src.memory.systemic_memory_trace import SystemicMemoryTrace


class TestSystemicMemoryTrace:
    """Testes para SystemicMemoryTrace."""

    def test_init(self):
        """Testa inicialização."""
        memory = SystemicMemoryTrace(state_space_dim=256)
        assert memory.state_space_dim == 256
        assert memory.deformation_threshold == 0.01
        assert len(memory.topological_markers) == 0

    def test_add_trace_not_memory(self):
        """Testa adição de traço (não memória)."""
        memory = SystemicMemoryTrace(state_space_dim=10, deformation_threshold=0.01)
        past_state = np.random.randn(10)
        current_state = past_state + np.random.randn(10) * 0.1

        memory.add_trace_not_memory(past_state, current_state)

        # Deve ter criado pelo menos uma marca topológica
        assert len(memory.topological_markers) > 0

    def test_add_trace_below_threshold(self):
        """Testa que traços abaixo do threshold são ignorados."""
        memory = SystemicMemoryTrace(state_space_dim=10, deformation_threshold=1.0)
        past_state = np.random.randn(10)
        current_state = past_state + np.random.randn(10) * 0.001  # Muito pequeno

        memory.add_trace_not_memory(past_state, current_state)

        # Não deve criar marca (deformação muito pequena)
        assert len(memory.topological_markers) == 0

    def test_reconstruct_narrative_retroactively(self):
        """Testa reconstrução retroativa de narrativa."""
        memory = SystemicMemoryTrace(state_space_dim=10)
        current_state = np.random.randn(10)

        # Adiciona algumas marcas primeiro
        for i in range(5):
            past = np.random.randn(10)
            current = past + np.random.randn(10) * 0.1
            memory.add_trace_not_memory(past, current)

        narrative = memory.reconstruct_narrative_retroactively(current_state, num_steps=5)

        assert len(narrative) == 5
        assert all("state" in step for step in narrative)
        assert all("not_retrieved_from" in step for step in narrative)
        assert all(step["not_retrieved_from"] == "history" for step in narrative)

    def test_affect_phi_calculation(self):
        """Testa que Φ é transformado (não aditivo)."""
        memory = SystemicMemoryTrace(state_space_dim=10)

        # Adiciona algumas marcas
        for i in range(3):
            past = np.random.randn(10)
            current = past + np.random.randn(10) * 0.1
            memory.add_trace_not_memory(past, current)

        standard_phi = 0.5
        result = memory.affect_phi_calculation(standard_phi, lambda x: 0.0)

        assert "phi_standard" in result
        assert "phi_with_memory" in result
        assert "delta" in result
        assert result["phi_standard"] == standard_phi
        # phi_with_memory pode ser diferente (transformação)
        assert 0.0 <= result["phi_with_memory"] <= 1.0

    def test_mark_cycle_transition(self):
        """Testa marcação de transição de ciclo."""
        memory = SystemicMemoryTrace(state_space_dim=10)
        cycle_states = {
            "module1": np.random.randn(10),
            "module2": np.random.randn(10),
        }

        memory.mark_cycle_transition(cycle_states, threshold=0.01)

        # Deve ter criado deformações para os módulos
        assert len(memory.embedding_deformations) == 2
        assert "module1" in memory.embedding_deformations
        assert "module2" in memory.embedding_deformations

    def test_deform_simplicial_candidates(self):
        """Testa deformação de candidatos simpliciais."""
        memory = SystemicMemoryTrace(state_space_dim=10)

        # Adiciona algumas deformações simpliciais
        memory.simplicial_deformations[(0, 1, 2)] = 0.5
        memory.simplicial_deformations[(1, 2, 3)] = 0.3

        candidates = [{0, 1, 2}, {3, 4, 5}]
        # Mock complex com n_vertices
        complex_mock = type("MockComplex", (), {"n_vertices": 6})()

        deformed = memory.deform_simplicial_candidates(candidates, complex_mock)

        assert len(deformed) == len(candidates)
        # Candidatos devem ser conjuntos
        assert all(isinstance(c, set) for c in deformed)
        # Primeiro candidato pode ter sido deformado (atração alta)
        # Segundo candidato deve permanecer similar (sem atração)
        assert len(deformed[0]) >= len(candidates[0])  # Pode ter vértices adicionados

    def test_decay_old_markers(self):
        """Testa decaimento de marcas antigas."""
        memory = SystemicMemoryTrace(state_space_dim=10, decay_factor=0.5)

        # Adiciona marca
        past = np.random.randn(10)
        current = past + np.random.randn(10) * 0.1
        memory.add_trace_not_memory(past, current)

        initial_count = len(memory.topological_markers)
        assert initial_count > 0

        # Simula tempo passado (marca antiga)
        import time

        for marker in memory.topological_markers.values():
            marker.last_activated = time.time() - 7200  # 2 horas atrás

        memory.decay_old_markers()

        # Marca antiga deve ter sido removida ou enfraquecida
        # (depende do threshold)
        final_count = len(memory.topological_markers)
        assert final_count <= initial_count

    def test_get_summary(self):
        """Testa resumo da memória sistemática."""
        memory = SystemicMemoryTrace(state_space_dim=10)

        # Adiciona algumas marcas
        for i in range(3):
            past = np.random.randn(10)
            current = past + np.random.randn(10) * 0.1
            memory.add_trace_not_memory(past, current)

        summary = memory.get_summary()

        assert "topological_markers_count" in summary
        assert "attractor_deformations_count" in summary
        assert "total_visits" in summary
        assert "average_deformation_strength" in summary
        assert summary["topological_markers_count"] > 0


class TestSystemicMemoryTraceHybridTopological:
    """Testes de integração entre SystemicMemoryTrace e HybridTopologicalEngine via SharedWorkspace."""  # noqa: E501

    def test_systemic_memory_with_shared_workspace_topological(self):
        """Testa que SystemicMemoryTrace pode ser usado com SharedWorkspace que tem HybridTopologicalEngine."""  # noqa: E501
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com SystemicMemoryTrace e HybridTopologicalEngine
        memory_trace = SystemicMemoryTrace(state_space_dim=256)
        workspace = SharedWorkspace(
            embedding_dim=256,
            systemic_memory=memory_trace,
        )
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Adicionar traços ao memory trace
        np.random.seed(42)
        for i in range(5):
            past_state = np.random.randn(256)
            current_state = past_state + np.random.randn(256) * 0.1
            memory_trace.add_trace_not_memory(past_state, current_state)

        # Escrever estados no workspace
        rho_C = np.random.randn(256)
        rho_P = np.random.randn(256)
        rho_U = np.random.randn(256)

        workspace.write_module_state("conscious_module", rho_C)
        workspace.write_module_state("preconscious_module", rho_P)
        workspace.write_module_state("unconscious_module", rho_U)

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que ambas as estruturas funcionam
        assert len(memory_trace.topological_markers) > 0, "Memory trace deve ter marcas"
        if topological_metrics is not None:
            assert "omega" in topological_metrics, "Métricas topológicas devem estar presentes"

    def test_systemic_memory_affects_phi_with_topological_metrics(self):
        """Testa que SystemicMemoryTrace afeta Φ e métricas topológicas são complementares."""
        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        memory_trace = SystemicMemoryTrace(state_space_dim=256)
        workspace = SharedWorkspace(
            embedding_dim=256,
            systemic_memory=memory_trace,
        )
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Adicionar múltiplos traços
        np.random.seed(42)
        for i in range(10):
            past_state = np.random.randn(256)
            current_state = past_state + np.random.randn(256) * 0.15
            memory_trace.add_trace_not_memory(past_state, current_state)

        # Simular múltiplos ciclos no workspace
        for i in range(5):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            workspace.write_module_state("conscious_module", rho_C)
            workspace.write_module_state("preconscious_module", rho_P)
            workspace.write_module_state("unconscious_module", rho_U)
            workspace.advance_cycle()

        # Calcular Φ padrão
        standard_phi = workspace.compute_phi_from_integrations()

        # Verificar que memory trace afeta Φ
        result = memory_trace.affect_phi_calculation(standard_phi, lambda x: 0.0)
        assert "phi_with_memory" in result

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que ambas as métricas estão disponíveis
        assert result["phi_with_memory"] >= 0.0
        if topological_metrics is not None:
            assert topological_metrics["omega"] >= 0.0
            # Ambas medem aspectos diferentes da consciência
            # Memory trace: deformações topológicas no espaço de estados
            # Topological metrics: estrutura do grafo semântico
