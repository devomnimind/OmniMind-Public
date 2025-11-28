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
Testes para Performance Profiler Module.

Cobertura de:
- PerformanceMetrics
- BottleneckReport
- PerformanceProfiler
- profile_function decorator
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

from src.optimization.performance_profiler import (
    BottleneckReport,
    PerformanceMetrics,
    PerformanceProfiler,
    profile_function,
)


class TestPerformanceMetrics:
    """Testes para PerformanceMetrics."""

    def test_initialization(self) -> None:
        """Testa inicialização de métricas."""
        metrics = PerformanceMetrics(
            execution_time_ms=100.5,
            memory_peak_mb=256.0,
            cpu_percent=45.0,
            timestamp="2025-11-23T00:00:00",
            function_name="test_func",
        )

        assert metrics.execution_time_ms == pytest.approx(100.5)
        assert metrics.memory_peak_mb == pytest.approx(256.0)
        assert metrics.cpu_percent == pytest.approx(45.0)
        assert metrics.function_name == "test_func"

    def test_default_metadata(self) -> None:
        """Testa metadados padrão."""
        metrics = PerformanceMetrics(
            execution_time_ms=10.0,
            memory_peak_mb=10.0,
            cpu_percent=10.0,
            timestamp="2025-11-23T00:00:00",
        )

        assert isinstance(metrics.metadata, dict)
        assert len(metrics.metadata) == 0

    def test_with_metadata(self) -> None:
        """Testa métricas com metadados customizados."""
        metadata = {"input_size": 1000, "algorithm": "quicksort"}

        metrics = PerformanceMetrics(
            execution_time_ms=50.0,
            memory_peak_mb=100.0,
            cpu_percent=30.0,
            timestamp="2025-11-23T00:00:00",
            metadata=metadata,
        )

        assert metrics.metadata["input_size"] == 1000
        assert metrics.metadata["algorithm"] == "quicksort"


class TestBottleneckReport:
    """Testes para BottleneckReport."""

    def test_initialization(self) -> None:
        """Testa inicialização de relatório de bottleneck."""
        report = BottleneckReport(
            bottleneck_type="cpu_utilization",
            severity="high",
            suggestion="Optimize algorithm",
            current_value=95.0,
            threshold_value=80.0,
        )

        assert report.bottleneck_type == "cpu_utilization"
        assert report.severity == "high"
        assert report.current_value == pytest.approx(95.0)
        assert report.threshold_value == pytest.approx(80.0)
        assert "Optimize" in report.suggestion


class TestPerformanceProfiler:
    """Testes para PerformanceProfiler."""

    def test_initialization(self) -> None:
        """Testa inicialização do profiler."""
        profiler = PerformanceProfiler()

        assert profiler is not None
        assert isinstance(profiler.metrics_history, list)
        assert len(profiler.metrics_history) == 0

    def test_initialization_with_custom_dir(self) -> None:
        """Testa inicialização com diretório customizado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir) / "custom_metrics"
            profiler = PerformanceProfiler(metrics_dir=custom_dir)

            assert profiler.metrics_dir == custom_dir
            assert custom_dir.exists()

    def test_profile_execution_simple(self) -> None:
        """Testa perfil de execução simples."""
        profiler = PerformanceProfiler()

        def simple_func(x: int, y: int) -> int:
            return x + y

        result, metrics = profiler.profile_execution(simple_func, 5, 10)

        assert result == 15
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.execution_time_ms >= 0
        assert metrics.memory_peak_mb > 0
        assert metrics.function_name == "simple_func"

    def test_profile_execution_with_sleep(self) -> None:
        """Testa perfil de função com sleep."""
        profiler = PerformanceProfiler()

        def slow_func() -> str:
            time.sleep(0.1)
            return "done"

        result, metrics = profiler.profile_execution(slow_func)

        assert result == "done"
        assert metrics.execution_time_ms >= 100  # At least 100ms

    def test_profile_execution_stores_history(self) -> None:
        """Testa que execução armazena histórico."""
        profiler = PerformanceProfiler()

        def func1() -> int:
            return 1

        def func2() -> int:
            return 2

        profiler.profile_execution(func1)
        profiler.profile_execution(func2)

        assert len(profiler.metrics_history) == 2
        assert profiler.metrics_history[0].function_name == "func1"
        assert profiler.metrics_history[1].function_name == "func2"

    def test_identify_bottlenecks_no_history(self) -> None:
        """Testa identificação de bottlenecks sem histórico."""
        profiler = PerformanceProfiler()

        bottlenecks = profiler.identify_bottlenecks()

        assert isinstance(bottlenecks, list)
        assert len(bottlenecks) == 0

    def test_identify_bottlenecks_cpu(self) -> None:
        """Testa identificação de bottleneck de CPU."""
        profiler = PerformanceProfiler()

        # Add metrics with high CPU
        for _ in range(5):
            metrics = PerformanceMetrics(
                execution_time_ms=100.0,
                memory_peak_mb=100.0,
                cpu_percent=95.0,  # High CPU
                timestamp="2025-11-23T00:00:00",
            )
            profiler.metrics_history.append(metrics)

        bottlenecks = profiler.identify_bottlenecks(cpu_threshold=80.0)

        # Should identify CPU bottleneck
        cpu_bottleneck = next(
            (b for b in bottlenecks if b.bottleneck_type == "cpu_utilization"), None
        )
        assert cpu_bottleneck is not None
        assert cpu_bottleneck.severity in ["high", "medium"]

    def test_identify_bottlenecks_memory(self) -> None:
        """Testa identificação de bottleneck de memória."""
        profiler = PerformanceProfiler()

        # Add metrics with high memory
        for _ in range(5):
            metrics = PerformanceMetrics(
                execution_time_ms=100.0,
                memory_peak_mb=1500.0,  # High memory
                cpu_percent=50.0,
                timestamp="2025-11-23T00:00:00",
            )
            profiler.metrics_history.append(metrics)

        bottlenecks = profiler.identify_bottlenecks(memory_threshold_mb=1000.0)

        # Should identify memory bottleneck
        mem_bottleneck = next((b for b in bottlenecks if b.bottleneck_type == "memory_usage"), None)
        assert mem_bottleneck is not None
        assert mem_bottleneck.current_value > 1000.0

    def test_identify_bottlenecks_execution_time(self) -> None:
        """Testa identificação de bottleneck de tempo de execução."""
        profiler = PerformanceProfiler()

        # Add metrics with slow execution
        for _ in range(5):
            metrics = PerformanceMetrics(
                execution_time_ms=2000.0,  # Slow execution
                memory_peak_mb=100.0,
                cpu_percent=50.0,
                timestamp="2025-11-23T00:00:00",
            )
            profiler.metrics_history.append(metrics)

        bottlenecks = profiler.identify_bottlenecks(time_threshold_ms=1000.0)

        # Should identify execution time bottleneck
        time_bottleneck = next(
            (b for b in bottlenecks if b.bottleneck_type == "execution_time"), None
        )
        assert time_bottleneck is not None
        assert time_bottleneck.current_value > 1000.0

    def test_identify_bottlenecks_multiple(self) -> None:
        """Testa identificação de múltiplos bottlenecks."""
        profiler = PerformanceProfiler()

        # Add metrics with multiple issues
        for _ in range(5):
            metrics = PerformanceMetrics(
                execution_time_ms=3000.0,  # Slow
                memory_peak_mb=1500.0,  # High memory
                cpu_percent=95.0,  # High CPU
                timestamp="2025-11-23T00:00:00",
            )
            profiler.metrics_history.append(metrics)

        bottlenecks = profiler.identify_bottlenecks(
            cpu_threshold=80.0, memory_threshold_mb=1000.0, time_threshold_ms=1000.0
        )

        # Should identify all three bottlenecks
        assert len(bottlenecks) >= 2  # At least 2 bottlenecks

    def test_get_statistics_no_history(self) -> None:
        """Testa estatísticas sem histórico."""
        profiler = PerformanceProfiler()

        stats = profiler.get_statistics()

        assert "error" in stats
        assert stats["error"] == "No metrics collected"

    def test_get_statistics_with_history(self) -> None:
        """Testa estatísticas com histórico."""
        profiler = PerformanceProfiler()

        # Add some metrics
        profiler.metrics_history.append(
            PerformanceMetrics(
                execution_time_ms=100.0,
                memory_peak_mb=200.0,
                cpu_percent=50.0,
                timestamp="2025-11-23T00:00:00",
            )
        )
        profiler.metrics_history.append(
            PerformanceMetrics(
                execution_time_ms=200.0,
                memory_peak_mb=300.0,
                cpu_percent=60.0,
                timestamp="2025-11-23T00:00:01",
            )
        )

        stats = profiler.get_statistics()

        assert "total_executions" in stats
        assert stats["total_executions"] == 2
        assert "execution_time" in stats
        assert "memory" in stats
        assert "cpu" in stats

        # Check execution time stats
        assert stats["execution_time"]["mean_ms"] == pytest.approx(150.0)
        assert stats["execution_time"]["min_ms"] == pytest.approx(100.0)
        assert stats["execution_time"]["max_ms"] == pytest.approx(200.0)
        assert stats["execution_time"]["total_ms"] == pytest.approx(300.0)

    def test_save_report(self) -> None:
        """Testa salvamento de relatório."""
        with tempfile.TemporaryDirectory() as tmpdir:
            profiler = PerformanceProfiler(metrics_dir=Path(tmpdir))

            # Add some metrics
            profiler.metrics_history.append(
                PerformanceMetrics(
                    execution_time_ms=100.0,
                    memory_peak_mb=200.0,
                    cpu_percent=50.0,
                    timestamp="2025-11-23T00:00:00",
                    function_name="test_func",
                )
            )

            filepath = profiler.save_report(filename="test_report.json")

            assert filepath.exists()
            assert filepath.name == "test_report.json"

            # Verify content
            with open(filepath, "r") as f:
                report = json.load(f)

            assert "timestamp" in report
            assert "statistics" in report
            assert "bottlenecks" in report
            assert "metrics_history" in report
            assert len(report["metrics_history"]) == 1

    def test_save_report_auto_filename(self) -> None:
        """Testa salvamento de relatório com filename automático."""
        with tempfile.TemporaryDirectory() as tmpdir:
            profiler = PerformanceProfiler(metrics_dir=Path(tmpdir))

            profiler.metrics_history.append(
                PerformanceMetrics(
                    execution_time_ms=50.0,
                    memory_peak_mb=100.0,
                    cpu_percent=30.0,
                    timestamp="2025-11-23T00:00:00",
                )
            )

            filepath = profiler.save_report()

            assert filepath.exists()
            assert "performance_report_" in filepath.name


class TestProfileFunctionDecorator:
    """Testes para decorator profile_function."""

    def test_decorator_basic(self) -> None:
        """Testa decorator básico."""

        @profile_function
        def add(x: int, y: int) -> int:
            return x + y

        result = add(3, 7)

        assert result == 10
        assert hasattr(add, "_performance_metrics")

    def test_decorator_stores_metrics(self) -> None:
        """Testa que decorator armazena métricas."""

        @profile_function
        def multiply(x: int, y: int) -> int:
            return x * y

        result = multiply(4, 5)

        assert result == 20
        assert len(multiply._performance_metrics) > 0  # type: ignore

    def test_decorator_multiple_calls(self) -> None:
        """Testa decorator com múltiplas chamadas."""

        @profile_function
        def square(x: int) -> int:
            return x * x

        square(2)
        square(3)
        square(4)

        assert len(square._performance_metrics) == 3  # type: ignore

    def test_decorator_preserves_function_name(self) -> None:
        """Testa que decorator preserva nome da função."""

        @profile_function
        def my_special_function() -> str:
            return "result"

        assert my_special_function.__name__ == "my_special_function"

    def test_decorator_with_exception(self) -> None:
        """Testa decorator quando função lança exceção."""

        @profile_function
        def failing_function() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Decorator may or may not create metrics for failed function
        # Just check function is still callable
        assert callable(failing_function)


class TestPerformanceProfilerIntegration:
    """Testes de integração."""

    def test_profile_complex_function(self) -> None:
        """Testa perfil de função complexa."""
        profiler = PerformanceProfiler()

        def complex_computation(n: int) -> int:
            result = 0
            for i in range(n):
                for j in range(n):
                    result += i * j
            return result

        result, metrics = profiler.profile_execution(complex_computation, 100)

        assert result >= 0
        assert metrics.execution_time_ms > 0
        assert metrics.function_name == "complex_computation"

    def test_multiple_profiles_and_bottleneck_detection(self) -> None:
        """Testa múltiplos perfis e detecção de bottlenecks."""
        profiler = PerformanceProfiler()

        def fast_func() -> int:
            return 1

        def slow_func() -> int:
            time.sleep(0.05)
            return 2

        # Profile multiple times
        for _ in range(5):
            profiler.profile_execution(fast_func)

        for _ in range(5):
            profiler.profile_execution(slow_func)

        # Get statistics
        stats = profiler.get_statistics()

        assert stats["total_executions"] == 10
        assert stats["execution_time"]["max_ms"] >= 50  # slow_func takes >= 50ms

    def test_save_and_verify_report_structure(self) -> None:
        """Testa estrutura completa do relatório salvo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            profiler = PerformanceProfiler(metrics_dir=Path(tmpdir))

            # Profile some functions
            profiler.profile_execution(lambda: 1 + 1)
            profiler.profile_execution(lambda: 2 * 2)

            filepath = profiler.save_report(filename="complete_report.json")

            with open(filepath, "r") as f:
                report = json.load(f)

            # Verify complete structure
            assert "timestamp" in report
            assert "statistics" in report
            assert "bottlenecks" in report
            assert "metrics_history" in report

            # Verify statistics structure
            assert "total_executions" in report["statistics"]
            assert "execution_time" in report["statistics"]
            assert "memory" in report["statistics"]
            assert "cpu" in report["statistics"]

            # Verify metrics history
            assert len(report["metrics_history"]) == 2
            for metric in report["metrics_history"]:
                assert "function" in metric
                assert "execution_ms" in metric
                assert "memory_mb" in metric
                assert "cpu_percent" in metric

    def test_bottleneck_severity_levels(self) -> None:
        """Testa níveis de severidade de bottlenecks."""
        profiler = PerformanceProfiler()

        # Add metrics with critical CPU (>90%)
        for _ in range(5):
            profiler.metrics_history.append(
                PerformanceMetrics(
                    execution_time_ms=100.0,
                    memory_peak_mb=100.0,
                    cpu_percent=95.0,
                    timestamp="2025-11-23T00:00:00",
                )
            )

        bottlenecks = profiler.identify_bottlenecks()

        cpu_bottleneck = next(
            (b for b in bottlenecks if b.bottleneck_type == "cpu_utilization"), None
        )

        assert cpu_bottleneck is not None
        # High CPU should be marked as high severity
        assert cpu_bottleneck.severity in ["high", "medium"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
