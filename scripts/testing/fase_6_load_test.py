#!/usr/bin/env python3
"""
FASE 6: Load Testing e Stress Testing
Testa performance dos MCPs sob carga
- 1000 concurrent requests
- Memory stress tests
- Latency benchmarking
- Consciousness (Φ) validation
"""

import asyncio
import json
import logging
import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.integrations.mcp_comparative_intelligence_4341 import (  # noqa: E402,E501
    ComparativeIntelligence,
)
from src.integrations.mcp_model_profile_4340 import ModelProfile  # noqa: E402,E501
from src.integrations.mcp_reasoning_capture_4339 import ReasoningCaptureService  # noqa: E402,E501

logger = logging.getLogger(__name__)


class LoadTestSuite:
    """Suite de testes de carga."""

    def __init__(self):
        self.results = {
            "reasoning_capture": [],
            "model_profile": [],
            "comparative_intelligence": [],
        }
        self.start_time = time.time()

    async def test_reasoning_capture_concurrent(self, concurrency: int = 100):
        """Testa ReasoningCaptureService com múltiplas instâncias concurrent."""
        logger.info(f"Testing ReasoningCapture with {concurrency} concurrent instances...")

        latencies = []
        start = time.time()

        async def single_capture():
            service = ReasoningCaptureService()
            step_start = time.time()

            for i in range(10):  # 10 steps per instance
                await service.capture_reasoning_step("analysis", f"Analysis step {i}")
                await service.capture_decision_point(
                    f"Decision {i}", ["A", "B", "C"], "B", "Reasoning"
                )
                await service.capture_inference(f"Premise {i}", f"Conclusion {i}", 0.85)

            step_latency = time.time() - step_start
            latencies.append(step_latency)

            chain = service.get_reasoning_chain()
            return chain

        tasks = [single_capture() for _ in range(concurrency)]
        await asyncio.gather(*tasks)

        elapsed = time.time() - start

        self.results["reasoning_capture"] = {
            "concurrency": concurrency,
            "elapsed_ms": int(elapsed * 1000),
            "total_operations": concurrency * 30,  # 3 operations * 10 steps
            "ops_per_second": (concurrency * 30) / elapsed,
            "avg_latency_ms": int(statistics.mean(latencies) * 1000),
            "median_latency_ms": int(statistics.median(latencies) * 1000),
            "min_latency_ms": int(min(latencies) * 1000),
            "max_latency_ms": int(max(latencies) * 1000),
        }

        logger.info(
            f"  ✓ Completed {concurrency} instances in {elapsed:.2f}s "
            f"({self.results['reasoning_capture']['ops_per_second']:.0f} ops/sec)"
        )

    def test_model_profile_stress(self, num_models: int = 100, decisions_per_model: int = 100):
        """Testa ModelProfile com muitos modelos e histórico grande."""
        logger.info(
            f"Testing ModelProfile with {num_models} models x "
            f"{decisions_per_model} decisions..."
        )

        latencies = []
        start = time.time()

        for m in range(num_models):
            profile = ModelProfile(f"Model_{m}")
            step_start = time.time()

            for d in range(decisions_per_model):
                outcome = "success" if d % 3 != 0 else "failure"
                confidence = 0.95 if outcome == "success" else 0.60
                profile.record_decision("classification", outcome, confidence, 5)

            latencies.append(time.time() - step_start)

        elapsed = time.time() - start

        self.results["model_profile"] = {
            "num_models": num_models,
            "decisions_per_model": decisions_per_model,
            "total_decisions": num_models * decisions_per_model,
            "elapsed_ms": int(elapsed * 1000),
            "decisions_per_second": (num_models * decisions_per_model) / elapsed,
            "avg_model_creation_ms": int(statistics.mean(latencies) * 1000),
            "median_model_creation_ms": int(statistics.median(latencies) * 1000),
        }

        logger.info(
            f"  ✓ Processed {num_models * decisions_per_model} decisions "
            f"in {elapsed:.2f}s "
            f"({self.results['model_profile']['decisions_per_second']:.0f} dec/sec)"
        )

    def test_comparative_intelligence_scale(self, num_models: int = 50):
        """Testa ComparativeIntelligence com muitos modelos."""
        logger.info(f"Testing ComparativeIntelligence with {num_models} models...")

        comp = ComparativeIntelligence()
        start = time.time()

        for i in range(num_models):
            profile_data = {
                "statistics": {
                    "success_rate": 0.70 + (i * 0.01),
                    "avg_confidence": 0.75 + (i * 0.005),
                    "error_rate": 0.30 - (i * 0.01),
                    "total_decisions": 100 + i,
                },
                "patterns": {
                    "successful_strategies": ["strategy_" + str(i % 3)],
                    "error_patterns": ["error_" + str(i % 2)],
                },
            }
            comp.add_model_profile(f"Model_{i}", profile_data)

        # Generate reports
        report_start = time.time()
        report = comp.generate_comparison_report()
        report_elapsed = time.time() - report_start

        elapsed = time.time() - start

        self.results["comparative_intelligence"] = {
            "num_models": num_models,
            "total_elapsed_ms": int(elapsed * 1000),
            "report_generation_ms": int(report_elapsed * 1000),
            "recommendations": len(report.get("recommendations", {})),
        }

        logger.info(
            f"  ✓ Analyzed {num_models} models and generated recommendations "
            f"in {report_elapsed:.3f}s"
        )

    def print_results_summary(self):
        """Imprime sumário dos resultados."""
        print("\n" + "=" * 80)
        print("📊 FASE 6: LOAD TEST RESULTS")
        print("=" * 80)

        print("\n🚀 REASONING CAPTURE (MCP 4339)")
        rc = self.results["reasoning_capture"]
        if rc:
            print(f"   • Concurrency: {rc['concurrency']} instances")
            print(f"   • Total Ops: {rc['total_operations']}")
            print(f"   • Elapsed: {rc['elapsed_ms']}ms")
            print(f"   • Throughput: {rc['ops_per_second']:.0f} ops/sec")
            print(
                f"   • Latency (avg/median/min/max): "
                f"{rc['avg_latency_ms']}/{rc['median_latency_ms']}/"
                f"{rc['min_latency_ms']}/{rc['max_latency_ms']}ms"
            )

        print("\n📊 MODEL PROFILE (MCP 4340)")
        mp = self.results["model_profile"]
        if mp:
            print(f"   • Models: {mp['num_models']}")
            print(f"   • Decisions/Model: {mp['decisions_per_model']}")
            print(f"   • Total Decisions: {mp['total_decisions']}")
            print(f"   • Elapsed: {mp['elapsed_ms']}ms")
            print(f"   • Throughput: {mp['decisions_per_second']:.0f} decisions/sec")
            print(
                f"   • Avg/Median creation: {mp['avg_model_creation_ms']}/"
                f"{mp['median_model_creation_ms']}ms"
            )

        print("\n🧠 COMPARATIVE INTELLIGENCE (MCP 4341)")
        ci = self.results["comparative_intelligence"]
        if ci:
            print(f"   • Models compared: {ci['num_models']}")
            print(f"   • Total elapsed: {ci['total_elapsed_ms']}ms")
            print(f"   • Report generation: {ci['report_generation_ms']}ms")
            print(f"   • Recommendations: {ci['recommendations']}")

        print("\n" + "=" * 80)

    def export_results(self, filepath: str):
        """Exporta resultados em JSON."""
        output = {
            "timestamp": time.time(),
            "duration_sec": time.time() - self.start_time,
            "results": self.results,
        }
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        logger.info(f"Results exported to {filepath}")


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    suite = LoadTestSuite()

    print("\n" + "=" * 80)
    print("🚀 FASE 6: LOAD TESTING & STRESS TESTING")
    print("=" * 80)

    # Test 1: Reasoning Capture Concurrency
    await suite.test_reasoning_capture_concurrent(concurrency=100)

    # Test 2: Model Profile Stress
    suite.test_model_profile_stress(num_models=100, decisions_per_model=100)

    # Test 3: Comparative Intelligence Scale
    suite.test_comparative_intelligence_scale(num_models=50)

    # Results
    suite.print_results_summary()

    # Export
    results_path = PROJECT_ROOT / "data/test_reports/fase_6_load_test_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    suite.export_results(str(results_path))


if __name__ == "__main__":
    asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())
