#!/usr/bin/env python3
"""
Simple MCP stress test - sem dependências complexas
Foca em HTTP requests diretos ao endpoint MCP
"""

import argparse
import asyncio
import time
from typing import Any, Dict

import aiohttp


class SimpleMCPStressTest:
    """Stress test simples para MCP endpoint."""

    def __init__(
        self,
        duration: int = 30,
        concurrent: int = 50,
        endpoint: str = "http://localhost:8000/mcp",
    ):
        self.duration = duration
        self.concurrent = concurrent
        self.endpoint = endpoint
        self.start_time: float = 0
        self.requests_completed = 0
        self.requests_failed = 0
        self.total_latency = 0.0
        self.latencies: list[float] = []

    async def single_request(self, session: aiohttp.ClientSession, request_id: int) -> bool:
        """Execute uma request MCP individual."""
        try:
            start = time.time()
            payload: Dict[str, Any] = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "thinking",
                "params": {"prompt": f"test-{request_id}", "max_tokens": 10},
            }

            async with session.post(
                self.endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                await resp.json()

            elapsed = time.time() - start
            self.total_latency += elapsed
            self.latencies.append(elapsed)
            self.requests_completed += 1
            return True
        except Exception:
            self.requests_failed += 1
            return False

    async def run_stress_test(self) -> None:
        """Execute stress test com requests concorrentes."""
        print(f"\n{'='*60}")
        print("🚀 MCP Stress Test Started (Simple)")
        print(f"{'='*60}")
        print(f"Duration: {self.duration}s")
        print(f"Concurrent: {self.concurrent}")
        print(f"Endpoint: {self.endpoint}")
        print(f"{'='*60}\n")

        self.start_time = time.time()
        request_id = 0

        connector = aiohttp.TCPConnector(limit=self.concurrent)
        timeout = aiohttp.ClientTimeout(total=self.duration + 10)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            while time.time() - self.start_time < self.duration:
                # Criar batch de requests concorrentes
                tasks = [
                    self.single_request(session, request_id + i) for i in range(self.concurrent)
                ]
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
                await asyncio.sleep(0.1)

        self._print_summary()

    def _print_summary(self) -> None:
        """Print relatório final."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        rps = self.requests_completed / elapsed if elapsed > 0 else 0
        avg_latency = (
            self.total_latency / self.requests_completed if self.requests_completed > 0 else 0
        )

        print(f"\n{'='*60}")
        print("📊 MCP Stress Test Results")
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
            p50 = sorted_latencies[p50_idx] if p50_idx < len(sorted_latencies) else 0
            p99 = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0
            print(f"P50 Latency: {p50*1000:.2f}ms")
            print(f"P99 Latency: {p99*1000:.2f}ms")

        print(f"{'='*60}\n")

        # Print interpretation
        print("📈 Latency Interpretation:")
        if avg_latency < 0.01:
            print("   ✅ < 10ms: Excellent! Systemd sufficient")
        elif avg_latency < 0.05:
            print("   🟡 10-50ms: Good, optimize Docker + Systemd")
        else:
            print(f"   ❌ > 50ms: LKM zero-copy recommended ({avg_latency*1000:.2f}ms)")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple MCP Stress Test Tool")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    parser.add_argument("--concurrent", type=int, default=50, help="Concurrent requests")
    parser.add_argument("--endpoint", default="http://localhost:8000/mcp", help="MCP endpoint")

    args = parser.parse_args()

    test = SimpleMCPStressTest(
        duration=args.duration, concurrent=args.concurrent, endpoint=args.endpoint
    )

    try:
        await test.run_stress_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stress test interrupted by user")
        test._print_summary()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
