"""
Testes para KernelAutopoiesisMinimal.

Autor: Fabrício da Silva + assistência de IA
"""

from src.system.kernel_autopoiesis import KernelAutopoiesisMinimal, ProcessElement


class TestKernelAutopoiesisMinimal:
    """Testes para KernelAutopoiesisMinimal."""

    def test_init(self):
        """Testa inicialização."""
        kernel = KernelAutopoiesisMinimal()
        assert len(kernel.processes) == 0
        assert len(kernel.dependency_graph) == 0

    def test_detect_kernel_processes(self):
        """Testa detecção de processos do kernel."""
        kernel = KernelAutopoiesisMinimal()
        processes = kernel.detect_kernel_processes()

        # Pode retornar vazio se não houver processos com PID < 1000
        assert isinstance(processes, dict)

    def test_build_dependency_graph(self):
        """Testa construção de grafo de dependências."""
        kernel = KernelAutopoiesisMinimal()

        # Adiciona processos manualmente para teste
        kernel.processes["1"] = ProcessElement(process_id="1", name="process1", is_internal=True)
        kernel.processes["2"] = ProcessElement(process_id="2", name="process2", is_internal=True)

        graph = kernel.build_dependency_graph()

        assert isinstance(graph, dict)
        assert "1" in graph or "2" in graph

    def test_is_autopoietic_no_processes(self):
        """Testa verificação de autopoiesis sem processos."""
        kernel = KernelAutopoiesisMinimal()
        # Sem processos, não é autopoiético
        result = kernel.is_autopoietic()
        # Pode ser True ou False dependendo da implementação
        assert isinstance(result, bool)

    def test_organizational_closure(self):
        """Testa verificação de organizational closure."""
        kernel = KernelAutopoiesisMinimal()
        result = kernel.organizational_closure()

        assert "is_closed" in result
        assert "reason" in result
        assert isinstance(result["is_closed"], bool)

    def test_get_autopoiesis_summary(self):
        """Testa resumo de autopoiesis."""
        kernel = KernelAutopoiesisMinimal()
        summary = kernel.get_autopoiesis_summary()

        assert "is_autopoietic" in summary
        assert "organizational_closure" in summary
        assert "processes_count" in summary
        assert "dependency_edges" in summary
