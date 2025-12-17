#!/usr/bin/env python3
"""
MCP stress test com mock - simula requests sem backend
Perfil realista baseado em dados eBPF
"""

import argparse
import asyncio
import random
import time


class MockMCPStressTest:
    """Stress test com mock de latência realista."""

    def __init__(
        self,
        duration: int = 30,
        concurrent: int = 50,
        base_latency_ms: float = 5.0,
        jitter_pct: float = 0.3,
    ):
        self.duration = duration
        self.concurrent = concurrent
        self.base_latency_ms = base_latency_ms
        self.jitter_pct = jitter_pct
        self.start_time: float = 0
        self.requests_completed = 0
        self.requests_failed = 0
        self.total_latency = 0.0
        self.latencies: list[float] = []

    async def single_request(self, request_id: int) -> bool:
        """Simula uma request MCP com latência realista."""
        try:
            # Simular latência com distribuição realista
            # 90% no base_latency, 10% outliers
            if random.random() < 0.9:
                # Normal case
                jitter = random.gauss(0, self.base_latency_ms * self.jitter_pct)
                latency_ms = self.base_latency_ms + jitter
            else:
                # Outlier (slow request)
                latency_ms = self.base_latency_ms * random.uniform(2, 5)

            # Garantir positivo
            latency_ms = max(0.1, latency_ms)
            latency_s = latency_ms / 1000.0

            # Simular async I/O delay
            await asyncio.sleep(latency_s)

            self.total_latency += latency_s
            self.latencies.append(latency_s)
            self.requests_completed += 1
            return True
        except Exception:
            self.requests_failed += 1
            return False

    async def run_stress_test(self) -> None:
        """Execute stress test com requests concorrentes."""
        print(f"\n{'='*60}")
        print("🚀 MCP Mock Stress Test Started")
        print(f"{'='*60}")
        print(f"Duration: {self.duration}s")
        print(f"Concurrent: {self.concurrent}")
        print(f"Base Latency: {self.base_latency_ms:.1f}ms")
        print(f"{'='*60}\n")

        self.start_time = time.time()
        request_id = 0

        while time.time() - self.start_time < self.duration:
            # Criar batch de requests concorrentes
            tasks = [self.single_request(request_id + i) for i in range(self.concurrent)]
            request_id += self.concurrent

            await asyncio.gather(*tasks, return_exceptions=True)

            # Print progress
            elapsed = time.time() - self.start_time
            rps = self.requests_completed / elapsed if elapsed > 0 else 0
            print(
                f"[{elapsed:6.1f}s] Completed: {self.requests_completed} | "
                f"Failed: {self.requests_failed} | RPS: {rps:.1f}"
            )

            # Pequeno delay para não sobrecarregar
            await asyncio.sleep(0.01)

        self._print_summary()

    def _print_summary(self) -> None:
        """Print relatório final."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        rps = self.requests_completed / elapsed if elapsed > 0 else 0
        avg_latency = (
            self.total_latency / self.requests_completed if self.requests_completed > 0 else 0
        )

        print(f"\n{'='*60}")
        print("📊 MCP Mock Stress Test Results")
        print(f"{'='*60}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"Total Requests: {self.requests_completed}")
        print(f"Failed Requests: {self.requests_failed}")
        success_rate = (
            self.requests_completed / (self.requests_completed + self.requests_failed) * 100
            if (self.requests_completed + self.requests_failed) > 0
            else 0
        )
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Throughput: {rps:.1f} req/s")
        print(f"Avg Latency: {avg_latency*1000:.2f}ms")

        # Calculate percentiles
        if self.latencies:
            sorted_latencies = sorted(self.latencies)
            p50_idx = int(len(sorted_latencies) * 0.5)
            p99_idx = int(len(sorted_latencies) * 0.99)
            p99_9_idx = int(len(sorted_latencies) * 0.999)
            p50 = sorted_latencies[p50_idx] if p50_idx < len(sorted_latencies) else 0
            p99 = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0
            p99_9 = sorted_latencies[p99_9_idx] if p99_9_idx < len(sorted_latencies) else p99
            print(f"P50 Latency: {p50*1000:.2f}ms")
            print(f"P99 Latency: {p99*1000:.2f}ms")
            print(f"P99.9 Latency: {p99_9*1000:.2f}ms")
            print(f"Max Latency: {max(self.latencies)*1000:.2f}ms")

        print(f"{'='*60}\n")

        # Print interpretation
        print("📈 Latency Interpretation:")
        if avg_latency < 0.01:
            print("   ✅ < 10ms: Excellent! Systemd sufficient, LKM not needed")
        elif avg_latency < 0.05:
            print("   🟡 10-50ms: Good, optimize Docker + Systemd networking")
        else:
            print(f"   ❌ > 50ms: LKM zero-copy recommended ({avg_latency*1000:.2f}ms)")

        # Decision tree
        print("\n📋 Recomendações baseado em P99:")
        if self.latencies:
            sorted_latencies = sorted(self.latencies)
            p99_idx = int(len(sorted_latencies) * 0.99)
            p99 = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0

            if p99 < 0.010:
                print("   🟢 P99 < 10ms → Systemd é suficiente")
                print("   • LKM zero-copy: NÃO necessário")
                print("   • Foco: Otimizar serialização JSON")
            elif p99 < 0.050:
                print("   🟡 P99 10-50ms → Otimizar Docker + Systemd")
                print("   • LKM zero-copy: Considere se P99 > 40ms")
                print("   • Foco: Melhorar latência de rede")
            else:
                print("   🔴 P99 > 50ms → LKM zero-copy RECOMENDADO")
                print("   • Motivo: Latência excessiva mesmo em mock")
                print("   • Considere io_uring + shared memory IPC")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Mock Stress Test Tool")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    parser.add_argument("--concurrent", type=int, default=50, help="Concurrent requests")
    parser.add_argument("--base-latency", type=float, default=5.0, help="Base latency in ms")

    args = parser.parse_args()

    test = MockMCPStressTest(
        duration=args.duration, concurrent=args.concurrent, base_latency_ms=args.base_latency
    )

    try:
        await test.run_stress_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stress test interrupted by user")
        test._print_summary()


if __name__ == "__main__":
    asyncio.run(main())
