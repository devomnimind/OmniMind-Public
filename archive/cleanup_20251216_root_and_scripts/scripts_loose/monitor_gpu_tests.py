#!/usr/bin/env python3
"""
Monitor GPU durante testes de consciência.
Captura métricas em tempo real: GPU %, memória, temperatura, potência.
"""

import subprocess
import threading
import time
import json
from datetime import datetime
from pathlib import Path
import sys


class GPUMonitor:
    def __init__(self, output_file: str, interval: int = 5):
        self.output_file = Path(output_file)
        self.interval = interval
        self.running = False
        self.metrics = []
        self.thread = None

    def start(self):
        """Inicia monitoramento em thread de background."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"[MONITOR] GPU monitoring started → {self.output_file}")

    def stop(self):
        """Para monitoramento."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self._save_report()
        print(f"[MONITOR] GPU monitoring stopped")

    def _monitor_loop(self):
        """Loop de coleta de métricas."""
        while self.running:
            try:
                # Capturar dados via nvidia-smi
                cmd = [
                    "nvidia-smi",
                    "--query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit",
                    "--format=csv,nounits,noheader",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    for line in lines:
                        if line.strip():
                            parts = [x.strip() for x in line.split(",")]

                            # Função helper para converter com fallback
                            def safe_float(val, default=0.0):
                                try:
                                    # Remove '[N/A]' e valores inválidos
                                    val_clean = str(val).replace("[N/A]", "0").strip()
                                    return float(val_clean) if val_clean else default
                                except (ValueError, AttributeError):
                                    return default

                            metric = {
                                "timestamp": datetime.now().isoformat(),
                                "gpu_id": parts[0],
                                "utilization_gpu": safe_float(parts[1]),
                                "memory_used_mb": safe_float(parts[2]),
                                "memory_total_mb": safe_float(parts[3]),
                                "temperature_c": safe_float(parts[4]),
                                "power_draw_w": safe_float(parts[5]) if len(parts) > 5 else 0,
                                "power_limit_w": safe_float(parts[6]) if len(parts) > 6 else 0,
                            }
                            self.metrics.append(metric)

                            # Print real-time (evitar divisão por zero)
                            mem_total = (
                                metric["memory_total_mb"] if metric["memory_total_mb"] > 0 else 1
                            )
                            print(
                                f"[GPU {metric['gpu_id']}] "
                                f"Util: {metric['utilization_gpu']:.0f}% | "
                                f"Mem: {metric['memory_used_mb']:.0f}/{mem_total:.0f}MB | "
                                f"Temp: {metric['temperature_c']:.1f}°C | "
                                f"Power: {metric['power_draw_w']:.1f}W"
                            )
            except Exception as e:
                print(f"[MONITOR ERROR] {e}")

            time.sleep(self.interval)

    def _save_report(self):
        """Salva relatório em JSON."""
        if not self.metrics:
            print("[MONITOR] No metrics collected")
            return

        # Estatísticas
        if self.metrics:
            utils = [m["utilization_gpu"] for m in self.metrics]
            mems = [m["memory_used_mb"] for m in self.metrics]
            temps = [m["temperature_c"] for m in self.metrics]
            powers = [m["power_draw_w"] for m in self.metrics]

            report = {
                "total_samples": len(self.metrics),
                "duration_seconds": len(self.metrics) * self.interval,
                "gpu_utilization": {
                    "min": min(utils),
                    "max": max(utils),
                    "avg": sum(utils) / len(utils),
                },
                "memory_mb": {
                    "min": min(mems),
                    "max": max(mems),
                    "avg": sum(mems) / len(mems),
                },
                "temperature_c": {
                    "min": min(temps),
                    "max": max(temps),
                    "avg": sum(temps) / len(temps),
                },
                "power_w": {
                    "min": min(powers),
                    "max": max(powers),
                    "avg": sum(powers) / len(powers),
                },
                "samples": self.metrics,
            }

            # Salvar JSON
            json_file = self.output_file.with_suffix(".json")
            with open(json_file, "w") as f:
                json.dump(report, f, indent=2)

            # Salvar txt resumido
            with open(self.output_file, "w") as f:
                f.write("GPU Monitor Report\n")
                f.write("==================\n")
                f.write(f"Total samples: {report['total_samples']}\n")
                f.write(f"Duration: {report['duration_seconds']}s\n")
                f.write("\nGPU Utilization:\n")
                f.write(f"  Min: {report['gpu_utilization']['min']:.0f}%\n")
                f.write(f"  Max: {report['gpu_utilization']['max']:.0f}%\n")
                f.write(f"  Avg: {report['gpu_utilization']['avg']:.0f}%\n")
                f.write("\nMemory (MB):\n")
                f.write(f"  Min: {report['memory_mb']['min']:.0f}\n")
                f.write(f"  Max: {report['memory_mb']['max']:.0f}\n")
                f.write(f"  Avg: {report['memory_mb']['avg']:.0f}\n")
                f.write("\nTemperature (°C):\n")
                f.write(f"  Min: {report['temperature_c']['min']:.1f}\n")
                f.write(f"  Max: {report['temperature_c']['max']:.1f}\n")
                f.write(f"  Avg: {report['temperature_c']['avg']:.1f}\n")
                f.write("\nPower (W):\n")
                f.write(f"  Min: {report['power_w']['min']:.1f}\n")
                f.write(f"  Max: {report['power_w']['max']:.1f}\n")
                f.write(f"  Avg: {report['power_w']['avg']:.1f}\n")

            print(f"[MONITOR] Report saved → {self.output_file}")
            print(f"[MONITOR] Details → {json_file}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "gpu_monitor.txt"
    monitor = GPUMonitor(output)
    monitor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MONITOR] Stopping...")
        monitor.stop()
