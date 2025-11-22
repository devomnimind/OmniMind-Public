"""
Performance Benchmarks para Módulos OmniMind.

Benchmarks de performance para:
- Free Energy Lacanian
- Freudian Metapsychology  
- MCP Agentic Client
- Discourse Discovery
- Agentic IDE

Author: OmniMind Development Team
Date: November 2025
License: MIT
"""

from __future__ import annotations

from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import time
import statistics
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """
    Resultado de benchmark.
    
    Attributes:
        name: Nome do benchmark
        iterations: Número de iterações
        mean_time: Tempo médio (segundos)
        std_time: Desvio padrão do tempo
        min_time: Tempo mínimo
        max_time: Tempo máximo
        throughput: Operações por segundo
        memory_mb: Memória usada (MB)
    """
    name: str
    iterations: int
    mean_time: float
    std_time: float
    min_time: float
    max_time: float
    throughput: float
    memory_mb: float = 0.0


class PerformanceBenchmark:
    """
    Sistema de benchmarks de performance.
    """
    
    def __init__(self) -> None:
        """Inicializa benchmark system."""
        self.results: List[BenchmarkResult] = []
        
        logger.info("Performance benchmark system initialized")
    
    def benchmark(
        self,
        name: str,
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 10
    ) -> BenchmarkResult:
        """
        Executa benchmark de função.
        
        Args:
            name: Nome do benchmark
            func: Função a testar
            iterations: Número de iterações
            warmup: Iterações de aquecimento
            
        Returns:
            Resultado do benchmark
        """
        # Warmup
        for _ in range(warmup):
            func()
        
        # Benchmark
        times: List[float] = []
        
        for _ in range(iterations):
            start = time.time()
            func()
            end = time.time()
            times.append(end - start)
        
        # Estatísticas
        mean_time = statistics.mean(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0.0
        min_time = min(times)
        max_time = max(times)
        throughput = 1.0 / mean_time if mean_time > 0 else 0.0
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            mean_time=mean_time,
            std_time=std_time,
            min_time=min_time,
            max_time=max_time,
            throughput=throughput
        )
        
        self.results.append(result)
        
        logger.info(
            f"Benchmark '{name}': {mean_time*1000:.2f}ms avg, "
            f"{throughput:.2f} ops/sec"
        )
        
        return result
    
    def benchmark_free_energy_lacanian(self) -> BenchmarkResult:
        """
        Benchmark do módulo Free Energy Lacanian.
        
        Returns:
            Resultado do benchmark
        """
        try:
            import torch
            from src.lacanian.free_energy_lacanian import ActiveInferenceAgent
            
            # Reduced dimensions for faster benchmarking
            # Production values: sensory_dim=128, symbolic_dim=256, imaginary_dim=512
            # Benchmark values: 50% reduction to enable rapid iteration
            agent = ActiveInferenceAgent(
                sensory_dim=64,
                symbolic_dim=128,
                imaginary_dim=256
            )
            
            def run_inference():
                sensory_data = torch.randn(1, 64)
                outputs = agent(sensory_data)
                fe_state = agent.compute_free_energy(sensory_data, outputs)
                desire = agent.compute_desire(fe_state)
                return desire
            
            return self.benchmark(
                "Free Energy Lacanian - Active Inference",
                run_inference,
                iterations=50
            )
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return BenchmarkResult(
                name="Free Energy Lacanian - Active Inference",
                iterations=0,
                mean_time=0.0,
                std_time=0.0,
                min_time=0.0,
                max_time=0.0,
                throughput=0.0
            )
    
    def benchmark_freudian_metapsychology(self) -> BenchmarkResult:
        """
        Benchmark do módulo Freudian Metapsychology.
        
        Returns:
            Resultado do benchmark
        """
        try:
            from src.lacanian.freudian_metapsychology import (
                FreudianMind,
                Action
            )
            
            mind = FreudianMind()
            
            actions = [
                Action("a1", 0.8, 0.3, 0.5),
                Action("a2", 0.4, 0.6, 0.8),
                Action("a3", 0.6, 0.4, -0.2)
            ]
            
            reality_context = {'time_available': 2.0}
            
            def run_decision():
                chosen_action, resolution = mind.act(actions, reality_context)
                return resolution
            
            return self.benchmark(
                "Freudian Metapsychology - Conflict Resolution",
                run_decision,
                iterations=100
            )
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return BenchmarkResult(
                name="Freudian Metapsychology - Conflict Resolution",
                iterations=0,
                mean_time=0.0,
                std_time=0.0,
                min_time=0.0,
                max_time=0.0,
                throughput=0.0
            )
    
    def benchmark_discourse_discovery(self) -> BenchmarkResult:
        """
        Benchmark do módulo Discourse Discovery.
        
        Returns:
            Resultado do benchmark
        """
        try:
            from src.lacanian.discourse_discovery import LacanianDiscourseAnalyzer
            
            analyzer = LacanianDiscourseAnalyzer()
            
            text = (
                "Você deve seguir as regras estabelecidas. "
                "É uma ordem clara e deve ser cumprida."
            )
            
            def run_analysis():
                result = analyzer.analyze_text(text)
                return result
            
            return self.benchmark(
                "Discourse Discovery - Text Analysis",
                run_analysis,
                iterations=100
            )
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return BenchmarkResult(
                name="Discourse Discovery - Text Analysis",
                iterations=0,
                mean_time=0.0,
                std_time=0.0,
                min_time=0.0,
                max_time=0.0,
                throughput=0.0
            )
    
    def benchmark_mcp_agentic_client(self) -> BenchmarkResult:
        """
        Benchmark do módulo MCP Agentic Client.
        
        Returns:
            Resultado do benchmark
        """
        try:
            from src.integrations.mcp_agentic_client import MCPAgenticClient
            
            client = MCPAgenticClient(agent_id="benchmark_agent")
            
            code = """
x = 10
y = 20
result = x + y
"""
            
            def run_execution():
                execution_result = client.execute_agentic_code(code)
                return execution_result
            
            return self.benchmark(
                "MCP Agentic Client - Code Execution",
                run_execution,
                iterations=50
            )
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return BenchmarkResult(
                name="MCP Agentic Client - Code Execution",
                iterations=0,
                mean_time=0.0,
                std_time=0.0,
                min_time=0.0,
                max_time=0.0,
                throughput=0.0
            )
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """
        Executa todos os benchmarks.
        
        Returns:
            Lista de resultados
        """
        print("=" * 70)
        print("PERFORMANCE BENCHMARKS - OmniMind Modules")
        print("=" * 70)
        print()
        
        benchmarks = [
            self.benchmark_free_energy_lacanian,
            self.benchmark_freudian_metapsychology,
            self.benchmark_discourse_discovery,
            self.benchmark_mcp_agentic_client
        ]
        
        results = []
        
        for benchmark_func in benchmarks:
            try:
                result = benchmark_func()
                results.append(result)
                
                print(f"{result.name}")
                print(f"  Iterations: {result.iterations}")
                print(f"  Mean time: {result.mean_time * 1000:.2f} ms")
                print(f"  Std dev: {result.std_time * 1000:.2f} ms")
                print(f"  Min time: {result.min_time * 1000:.2f} ms")
                print(f"  Max time: {result.max_time * 1000:.2f} ms")
                print(f"  Throughput: {result.throughput:.2f} ops/sec")
                print()
                
            except Exception as e:
                logger.error(f"Benchmark failed: {e}")
        
        return results
    
    def save_results(self, output_path: Path) -> None:
        """
        Salva resultados em arquivo.
        
        Args:
            output_path: Path do arquivo de saída
        """
        import json
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'timestamp': time.time(),
            'benchmarks': [
                {
                    'name': r.name,
                    'iterations': r.iterations,
                    'mean_time_ms': r.mean_time * 1000,
                    'std_time_ms': r.std_time * 1000,
                    'min_time_ms': r.min_time * 1000,
                    'max_time_ms': r.max_time * 1000,
                    'throughput_ops_sec': r.throughput,
                    'memory_mb': r.memory_mb
                }
                for r in self.results
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Benchmark results saved to {output_path}")


def main() -> None:
    """Executa benchmarks."""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    
    # Salva resultados
    output_path = Path("data/benchmarks/performance_results.json")
    benchmark.save_results(output_path)
    
    print(f"Results saved to: {output_path}")
    print()
    
    # Resumo
    print("SUMMARY")
    print("=" * 70)
    print(f"Total benchmarks: {len(results)}")
    
    successful = [r for r in results if r.iterations > 0]
    if successful:
        mean_times = [r.mean_time for r in successful]
        print(f"Average execution time: {statistics.mean(mean_times) * 1000:.2f} ms")
        print(f"Fastest module: {min(successful, key=lambda r: r.mean_time).name}")
        print(f"Slowest module: {max(successful, key=lambda r: r.mean_time).name}")
    
    print()


if __name__ == "__main__":
    main()
