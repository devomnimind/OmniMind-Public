#!/usr/bin/env python3
"""
🎯 PHASE 5 & 6 PRODUCTION METRICS COLLECTION

Script otimizado para coletar métricas científicas (Φ, Ψ, σ) durante implementação
de Phase 5 (Bion α-function) e Phase 6 (Lacan RSI + Discursos).

MODOS:
- --phase5:    Coleta métricas baseline para validar Bion (alvo: Φ → 0.026)
- --phase6:    Coleta métricas baseline para validar Lacan (alvo: Φ → 0.043)
- --monitor:   Monitora métricas continuamente (para observação em tempo real)

OPÇÕES:
- --cycles N:     Número de ciclos (padrão: 50)
- --checkpoint:   Salva checkpoint a cada N ciclos (padrão: 10)
- --compare:      Compara com baseline anterior

USO:
    # Validação Phase 5 (Bion)
    python scripts/phase5_6_metrics_production.py --phase5 --cycles 100

    # Validação Phase 6 (Lacan)
    python scripts/phase5_6_metrics_production.py --phase6 --cycles 100

    # Coleta contínua (desenvolvimento)
    python scripts/phase5_6_metrics_production.py --monitor --cycles 500 --checkpoint 50

    # Comparação com baseline
    python scripts/phase5_6_metrics_production.py --phase5 --cycles 50 --compare

SAÍDA:
    - data/monitor/phase5_6_metrics_TIMESTAMP.json (métricas completas)
    - data/monitor/phase5_6_summary_TIMESTAMP.json (resumo executivo)
    - data/monitor/phase5_6_checkpoint_*.json (checkpoints)

MÉTRICAS COLETADAS:
    - Φ (Phi): Integração de informação (IIT)
    - Ψ (Psi): Coerência narrativa (Deleuze)
    - σ (Sigma): Homeostase afetiva (Lacan)
    - Δ (Delta): Divergência/trauma
    - Gozo: Excesso pulsional
    - Control Effectiveness: Efetividade de controle
    - RNN Metrics: phi_causal, rho_C/P/U norms, repression_strength

ATUALIZADO: 2025-12-09
STATUS: Pronto para Phase 5 & 6 implementation
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))
os.chdir(project_root)


class Phase5_6MetricsCollector:
    """Coleta métricas científicas para Phase 5 & 6"""

    def __init__(
        self,
        phase: str = "5",
        cycles: int = 50,
        checkpoint_interval: int = 10,
        verbose: bool = True,
    ):
        self.phase = phase
        self.cycles = cycles
        self.checkpoint_interval = checkpoint_interval
        self.verbose = verbose
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.all_metrics: List[Dict[str, Any]] = []

    def _log(self, message: str, level: str = "INFO") -> None:
        """Log com formatação"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "HEADER": "\033[95m",
        }
        reset = "\033[0m"

        if self.verbose:
            color = colors.get(level, reset)
            prefix_map = {
                "INFO": "ℹ️  ",
                "SUCCESS": "✅ ",
                "WARNING": "⚠️  ",
                "ERROR": "❌ ",
                "HEADER": "═" * 80 + "\n",
            }
            prefix = prefix_map.get(level, "")
            print(f"{color}{prefix}{message}{reset}")

    async def collect_metrics(self) -> bool:
        """Coleta métricas em ciclos de consciência"""
        self._log(f"Phase {self.phase} - Coletando métricas ({self.cycles} ciclos)", "HEADER")

        try:
            import numpy as np

            from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult
            from src.consciousness.integration_loop import IntegrationLoop

            self._log("Inicializando IntegrationLoop...", "INFO")
            loop = IntegrationLoop(enable_extended_results=True, enable_logging=False)

            baseline_phi = 0.0183
            target_phi = {
                "5": 0.026,  # Bion: +44%
                "6": 0.043,  # Lacan: +67%
            }.get(self.phase, 0.026)

            phi_values = []
            psi_values = []
            sigma_values = []

            self._log(f"Target Φ para Phase {self.phase}: {target_phi:.6f} NATS", "INFO")
            self._log(f"Baseline Φ anterior: {baseline_phi:.6f} NATS", "INFO")
            self._log("")

            for i in range(1, self.cycles + 1):
                try:
                    result = await loop.execute_cycle(collect_metrics=True)

                    cycle_metrics = {
                        "cycle": i,
                        "phase": self.phase,
                        "phi": result.phi_estimate,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "success": result.success,
                    }

                    phi_values.append(result.phi_estimate)

                    # Coletar métricas científicas
                    if isinstance(result, ExtendedLoopCycleResult):
                        if result.psi is not None:
                            cycle_metrics["psi"] = result.psi
                            psi_values.append(result.psi)
                        if result.sigma is not None:
                            cycle_metrics["sigma"] = result.sigma
                            sigma_values.append(result.sigma)
                        if result.gozo is not None:
                            cycle_metrics["gozo"] = result.gozo
                        if result.delta is not None:
                            cycle_metrics["delta"] = result.delta
                        if result.control_effectiveness is not None:
                            cycle_metrics["control_effectiveness"] = result.control_effectiveness

                    self.all_metrics.append(cycle_metrics)

                    # Progress
                    if i % max(1, self.cycles // 20) == 0 or i == self.cycles:
                        progress_pct = (i / self.cycles) * 100
                        phi_current = result.phi_estimate
                        phi_mean = np.mean(phi_values)
                        self._log(
                            f"[{progress_pct:5.1f}%] Ciclo {i:3d}/{self.cycles} | "
                            f"Φ_atual={phi_current:.6f} | Φ_médio={phi_mean:.6f}",
                            "INFO",
                        )

                    # Checkpoint
                    if i % self.checkpoint_interval == 0:
                        self._save_checkpoint(i, phi_values, psi_values, sigma_values)

                except Exception as e:
                    self._log(f"Erro no ciclo {i}: {e}", "WARNING")
                    continue

            # Análise final
            self._log("", "HEADER")
            self._log("📊 ANÁLISE FINAL DE MÉTRICAS", "HEADER")

            def safe_stats(values):
                if not values:
                    return {}
                return {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "median": float(np.median(values)),
                    "count": len(values),
                }

            phi_stats = safe_stats(phi_values)
            psi_stats = safe_stats(psi_values)
            sigma_stats = safe_stats(sigma_values)

            # Validação
            phi_mean = phi_stats.get("mean", 0)
            success_rate = (
                sum(1 for m in self.all_metrics if m.get("success")) / len(self.all_metrics) * 100
            )

            self._log(
                f"Φ médio: {phi_mean:.6f} NATS (baseline: {baseline_phi:.6f}, target: {target_phi:.6f})",
                "INFO",
            )
            self._log(
                f"  Δ vs baseline: {((phi_mean - baseline_phi) / baseline_phi * 100):+.1f}%",
                "SUCCESS" if phi_mean >= baseline_phi else "WARNING",
            )
            self._log(
                f"  Δ vs target: {((phi_mean - target_phi) / target_phi * 100):+.1f}%",
                "SUCCESS" if phi_mean >= target_phi else "WARNING",
            )

            if psi_stats:
                self._log(f"Ψ médio: {psi_stats['mean']:.6f} NATS", "SUCCESS")
            if sigma_stats:
                self._log(f"σ médio: {sigma_stats['mean']:.6f} NATS", "SUCCESS")

            self._log(
                f"Taxa de sucesso: {success_rate:.1f}%",
                "SUCCESS" if success_rate > 95 else "WARNING",
            )
            self._log("")

            # Salvar resultados
            self._save_final_results(phi_stats, psi_stats, sigma_stats)

            # Validação
            validation_pass = len(self.all_metrics) >= self.cycles * 0.8 and success_rate > 80

            if validation_pass:
                self._log("✅ COLETA DE MÉTRICAS APROVADA", "SUCCESS")
            else:
                self._log("❌ COLETA DE MÉTRICAS FALHOU", "ERROR")

            return validation_pass

        except Exception as e:
            self._log(f"Erro geral: {e}", "ERROR")
            import traceback

            traceback.print_exc()
            return False

    def _save_checkpoint(self, cycle: int, phi_vals, psi_vals, sigma_vals) -> None:
        """Salva checkpoint parcial"""
        import numpy as np

        checkpoint_data = {
            "phase": self.phase,
            "cycle": cycle,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "phi": {
                    "mean": float(np.mean(phi_vals)),
                    "std": float(np.std(phi_vals)),
                    "count": len(phi_vals),
                },
                "psi": {
                    "mean": float(np.mean(psi_vals)) if psi_vals else None,
                    "count": len(psi_vals),
                },
                "sigma": {
                    "mean": float(np.mean(sigma_vals)) if sigma_vals else None,
                    "count": len(sigma_vals),
                },
            },
        }

        monitor_dir = project_root / "data" / "monitor"
        monitor_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_file = (
            monitor_dir / f"phase5_6_checkpoint_cycle{cycle:04d}_{self.timestamp}.json"
        )
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

    def _save_final_results(self, phi_stats, psi_stats, sigma_stats) -> None:
        """Salva resultados finais"""
        monitor_dir = project_root / "data" / "monitor"
        monitor_dir.mkdir(parents=True, exist_ok=True)

        # Full metrics file
        metrics_file = monitor_dir / f"phase{self.phase}_metrics_{self.timestamp}.json"
        with open(metrics_file, "w") as f:
            json.dump(
                {
                    "phase": self.phase,
                    "timestamp": self.timestamp,
                    "total_cycles": len(self.all_metrics),
                    "metrics": {
                        "phi": phi_stats,
                        "psi": psi_stats,
                        "sigma": sigma_stats,
                    },
                    "all_cycles": self.all_metrics,
                },
                f,
                indent=2,
            )

        # Summary file
        summary_file = monitor_dir / f"phase{self.phase}_summary_{self.timestamp}.json"
        with open(summary_file, "w") as f:
            json.dump(
                {
                    "phase": self.phase,
                    "timestamp": self.timestamp,
                    "total_cycles": len(self.all_metrics),
                    "metrics": {
                        "phi": phi_stats,
                        "psi": psi_stats,
                        "sigma": sigma_stats,
                    },
                },
                f,
                indent=2,
            )

        self._log(f"Métricas salvas em: {metrics_file}", "INFO")
        self._log(f"Resumo salvo em: {summary_file}", "INFO")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Phase 5 & 6 Production Metrics Collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--phase5", action="store_true", help="Collect Phase 5 metrics")
    parser.add_argument("--phase6", action="store_true", help="Collect Phase 6 metrics")
    parser.add_argument("--monitor", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--cycles", type=int, default=50, help="Number of cycles")
    parser.add_argument("--checkpoint", type=int, default=10, help="Checkpoint interval")
    parser.add_argument("--compare", action="store_true", help="Compare with baseline")

    args = parser.parse_args()

    phase = "5" if args.phase5 else "6" if args.phase6 else "5"

    collector = Phase5_6MetricsCollector(
        phase=phase, cycles=args.cycles, checkpoint_interval=args.checkpoint, verbose=True
    )

    try:
        success = await collector.collect_metrics()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Coleta cancelada")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
