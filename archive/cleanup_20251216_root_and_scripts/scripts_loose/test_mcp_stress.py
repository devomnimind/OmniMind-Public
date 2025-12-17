#!/usr/bin/env python3
"""
Script para stress-test MCP e coleta de métricas com eBPF.

Uso:
    python3 test_mcp_stress.py --duration 30 --concurrent 100

Requer bpftrace rodando em outro terminal:
    sudo bpftrace scripts/monitor_mcp_bpf.bt > /tmp/ebpf_output.txt
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Add src to path - absolute import from project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from src.integrations.mcp_client_async import AsyncMCPClient
except ImportError:
    # Fallback para relative import se executado de scripts/
    from integrations.mcp_client_async import AsyncMCPClient


class MCPStressTest:
    """Stress test para MCP com coleta de métricas."""

    def __init__(
        self, duration: int = 30, concurrent: int = 50, endpoint: str = "http://localhost:4321/mcp"
    ):
        self.duration = duration
        self.concurrent = concurrent
        self.endpoint = endpoint
        self.start_time = None
        self.requests_completed = 0
        self.requests_failed = 0
        self.total_latency = 0.0

    async def single_request(self, client: AsyncMCPClient, request_id: int) -> bool:
        """Execute uma request MCP individual."""
        try:
            start = time.time()
            await client.send_request(
                method="thinking", params={"prompt": f"test-{request_id}", "max_tokens": 10}
            )
            elapsed = time.time() - start
            self.total_latency += elapsed
            self.requests_completed += 1
            return True
        except Exception:
            self.requests_failed += 1
            return False

    async def run_stress_test(self) -> None:
        """Execute stress test com requests concorrentes."""
        print(f"\n{'='*60}")
        print("🚀 MCP Stress Test Started")
        print(f"{'='*60}")
        print(f"Duration: {self.duration}s")
        print(f"Concurrent: {self.concurrent}")
        print(f"Endpoint: {self.endpoint}")
        print(f"{'='*60}\n")

        self.start_time = time.time()
        request_id = 0

        async with AsyncMCPClient(endpoint=self.endpoint) as client:
            while time.time() - self.start_time < self.duration:
                # Criar batch de requests concorrentes
                tasks = [
                    self.single_request(client, request_id + i) for i in range(self.concurrent)
                ]
                request_id += self.concurrent

                await asyncio.gather(*tasks, return_exceptions=True)

                # Print progress
                elapsed = time.time() - self.start_time
                rps = self.requests_completed / elapsed if elapsed > 0 else 0
                print(
                    f"[{elapsed:6.1f}s] Completed: {self.requests_completed} | Failed: {self.requests_failed} | RPS: {rps:.1f}"
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
        print(
            f"Success Rate: {(self.requests_completed / (self.requests_completed + self.requests_failed) * 100 if (self.requests_completed + self.requests_failed) > 0 else 0):.1f}%"
        )
        print(f"Throughput: {rps:.1f} req/s")
        print(f"Avg Latency: {avg_latency*1000:.2f}ms")
        print(f"{'='*60}\n")

        # Print interpretation
        print("📈 Latency Interpretation:")
        if avg_latency < 0.01:
            print("   ✅ < 10ms: Excellent! Systemd sufficient")
        elif avg_latency < 0.05:
            print("   🟡 10-50ms: Good, optimize Docker + Systemd")
        else:
            print("   ❌ > 50ms: LKM zero-copy recommended")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Stress Test Tool")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    parser.add_argument("--concurrent", type=int, default=50, help="Concurrent requests")
    parser.add_argument("--endpoint", default="http://localhost:4321/mcp", help="MCP endpoint")

    args = parser.parse_args()

    test = MCPStressTest(duration=args.duration, concurrent=args.concurrent, endpoint=args.endpoint)

    try:
        await test.run_stress_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stress test interrupted by user")
        test._print_summary()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
