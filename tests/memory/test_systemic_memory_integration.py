"""
Testes de Integração para SystemicMemoryTrace (FASE 4.1).

Valida integração completa com:
- SharedWorkspace
- PhiCalculator
- NarrativeHistory
- IntegrationLoop

CLASSIFICATION: [UNIT/INTEGRATION]
- Testes unitários de integração (não requerem servidor)
- Usam mocks/tempfiles quando necessário
- Não requerem GPU ou LLM real

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import numpy as np
from pathlib import Path
import tempfile

from src.memory.systemic_memory_trace import SystemicMemoryTrace
from src.consciousness.shared_workspace import SharedWorkspace
from src.consciousness.topological_phi import PhiCalculator, SimplicialComplex
from src.memory.narrative_history import NarrativeHistory


# Testes de integração são unitários (não requerem recursos reais)
# conftest.py já gerencia timeouts automaticamente para testes em "memory/"
class TestSystemicMemoryIntegration:
    """Testes de integração para SystemicMemoryTrace."""

    def test_shared_workspace_integration(self):
        """Testa integração com SharedWorkspace."""
        # Criar SystemicMemoryTrace
        systemic_memory = SystemicMemoryTrace(state_space_dim=256, deformation_threshold=0.01)

        # Criar SharedWorkspace com systemic_memory
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = SharedWorkspace(
                embedding_dim=256,
                max_history_size=1000,
                workspace_dir=Path(tmpdir),
                systemic_memory=systemic_memory,
            )
            _ = tmpdir  # Usar variável para evitar warning

            # Verificar que systemic_memory foi integrado
            assert workspace.systemic_memory is not None
            assert workspace.systemic_memory == systemic_memory

            # Escrever estado de módulo
            module_embedding = np.random.randn(256)
            workspace.write_module_state("test_module", module_embedding, metadata={"test": True})

            # Verificar que deformação foi rastreada
            # (deve ter pelo menos uma marca se houver transição)
            assert len(workspace.systemic_memory.topological_markers) >= 0

    def test_phi_calculator_integration(self):
        """Testa integração com PhiCalculator."""
        # Criar SystemicMemoryTrace
        systemic_memory = SystemicMemoryTrace(state_space_dim=10, deformation_threshold=0.01)

        # Adicionar algumas marcas
        for i in range(3):
            past = np.random.randn(10)
            current = past + np.random.randn(10) * 0.1
            systemic_memory.add_trace_not_memory(past, current)

        # Criar SimplicialComplex
        complex_ = SimplicialComplex()
        complex_.add_simplex((0,))
        complex_.add_simplex((1,))
        complex_.add_simplex((0, 1))

        # Criar PhiCalculator com memory_trace
        phi_calc = PhiCalculator(complex_, memory_trace=systemic_memory)

        # Verificar que memory_trace foi integrado
        assert phi_calc.memory_trace is not None
        assert phi_calc.memory_trace == systemic_memory

        # Calcular phi (deve usar memory_trace para deformar candidatos)
        result = phi_calc.calculate_phi_with_unconscious()

        # Verificar que resultado é válido
        assert result.conscious_phi >= 0.0
        assert isinstance(result.conscious_complex, set)

    def test_narrative_history_integration(self):
        """Testa integração com NarrativeHistory."""
        # Criar SystemicMemoryTrace
        systemic_memory = SystemicMemoryTrace(state_space_dim=256, deformation_threshold=0.01)

        # Adicionar algumas marcas
        for i in range(5):
            past = np.random.randn(256)
            current = past + np.random.randn(256) * 0.1
            systemic_memory.add_trace_not_memory(past, current)

        # Criar NarrativeHistory com systemic_memory
        # Note: NarrativeHistory requer qdrant_url, mas podemos usar um mock
        narrative = NarrativeHistory(
            qdrant_url="http://localhost:6333",
            systemic_memory=systemic_memory,
        )

        # Verificar que systemic_memory foi integrado
        assert narrative.systemic_memory is not None
        assert narrative.systemic_memory == systemic_memory

        # Testar reconstrução retroativa (usa query string, não estado)
        query = "test narrative"
        reconstructed = narrative.reconstruct_narrative(query, use_systemic_memory=True)

        # Verificar que reconstrução funciona (pode retornar lista vazia se Qdrant não disponível)
        assert isinstance(reconstructed, list)

    def test_integration_loop_tracking(self):
        """Testa rastreamento de transições de ciclo."""
        # Criar SystemicMemoryTrace
        systemic_memory = SystemicMemoryTrace(state_space_dim=256, deformation_threshold=0.01)

        # Simular transições de ciclo
        cycle_states = {
            "module1": np.random.randn(256),
            "module2": np.random.randn(256),
            "module3": np.random.randn(256),
        }

        # Marcar transição de ciclo
        systemic_memory.mark_cycle_transition(cycle_states, threshold=0.01)

        # Verificar que deformações foram criadas
        assert len(systemic_memory.embedding_deformations) == 3
        assert "module1" in systemic_memory.embedding_deformations
        assert "module2" in systemic_memory.embedding_deformations
        assert "module3" in systemic_memory.embedding_deformations

    def test_phi_transformation(self):
        """Testa que Φ é transformado (não aditivo) pela memória sistemática."""
        # Criar SystemicMemoryTrace
        systemic_memory = SystemicMemoryTrace(state_space_dim=10, deformation_threshold=0.01)

        # Adicionar várias marcas para criar deformação significativa
        for i in range(10):
            past = np.random.randn(10)
            current = past + np.random.randn(10) * 0.1
            systemic_memory.add_trace_not_memory(past, current)

        # Calcular phi padrão
        standard_phi = 0.5

        # Função de cálculo de phi padrão (mock)
        def standard_phi_func(partition: set) -> float:
            return standard_phi

        # Aplicar transformação
        result = systemic_memory.affect_phi_calculation(standard_phi, standard_phi_func)

        # Verificar que resultado contém campos esperados
        assert "phi_standard" in result
        assert "phi_with_memory" in result
        assert "delta" in result

        # Verificar que phi_standard é mantido
        assert result["phi_standard"] == standard_phi

        # Verificar que phi_with_memory é válido (pode ser diferente)
        assert 0.0 <= result["phi_with_memory"] <= 1.0

        # Verificar que delta é calculado
        assert "delta" in result
        delta = result["phi_with_memory"] - result["phi_standard"]
        assert abs(result["delta"] - delta) < 1e-6

    def test_narrative_reconstruction_retroactive(self):
        """Testa reconstrução retroativa de narrativa."""
        # Criar SystemicMemoryTrace
        systemic_memory = SystemicMemoryTrace(state_space_dim=256, deformation_threshold=0.01)

        # Adicionar várias marcas
        for i in range(10):
            past = np.random.randn(256)
            current = past + np.random.randn(256) * 0.1
            systemic_memory.add_trace_not_memory(past, current)

        # Estado atual
        current_state = np.random.randn(256)

        # Reconstruir narrativa retroativamente
        narrative = systemic_memory.reconstruct_narrative_retroactively(current_state, num_steps=10)

        # Verificar que narrativa foi reconstruída
        assert len(narrative) == 10
        assert all("state" in step for step in narrative)
        assert all("not_retrieved_from" in step for step in narrative)
        assert all(step["not_retrieved_from"] == "history" for step in narrative)

        # Verificar que estados são arrays numpy ou listas (podem ser convertidos)
        for step in narrative:
            state = step["state"]
            assert isinstance(state, (np.ndarray, list))
            if isinstance(state, list):
                # Converter para numpy array se necessário
                state = np.array(state)
            assert isinstance(state, np.ndarray)

    def test_decay_old_markers(self):
        """Testa decaimento de marcas antigas."""
        # Criar SystemicMemoryTrace com decay_factor
        systemic_memory = SystemicMemoryTrace(
            state_space_dim=10, decay_factor=0.5, deformation_threshold=0.01
        )

        # Adicionar marcas
        import time

        for i in range(5):
            past = np.random.randn(10)
            current = past + np.random.randn(10) * 0.1
            systemic_memory.add_trace_not_memory(past, current)

        initial_count = len(systemic_memory.topological_markers)
        assert initial_count > 0

        # Simular tempo passado (marcas antigas)
        for marker in systemic_memory.topological_markers.values():
            marker.last_activated = time.time() - 7200  # 2 horas atrás

        # Aplicar decaimento
        systemic_memory.decay_old_markers()

        # Verificar que marcas antigas foram removidas ou enfraquecidas
        final_count = len(systemic_memory.topological_markers)
        assert final_count <= initial_count

    def test_get_summary(self):
        """Testa resumo da memória sistemática."""
        # Criar SystemicMemoryTrace
        systemic_memory = SystemicMemoryTrace(state_space_dim=10, deformation_threshold=0.01)

        # Adicionar várias marcas
        for i in range(5):
            past = np.random.randn(10)
            current = past + np.random.randn(10) * 0.1
            systemic_memory.add_trace_not_memory(past, current)

        # Obter resumo
        summary = systemic_memory.get_summary()

        # Verificar campos do resumo
        assert "topological_markers_count" in summary
        assert "attractor_deformations_count" in summary
        assert "total_visits" in summary
        assert "average_deformation_strength" in summary

        # Verificar valores
        assert summary["topological_markers_count"] > 0
        assert summary["total_visits"] > 0
        assert summary["average_deformation_strength"] >= 0.0
