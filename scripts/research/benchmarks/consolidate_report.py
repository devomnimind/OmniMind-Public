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

import json
import os
from datetime import datetime, UTC

BENCHMARK_FILES = {
    "system": "docs/reports/hardware_audit.json",
    "cpu": "docs/reports/benchmarks/cpu_benchmark.json",
    "gpu": "docs/reports/benchmarks/gpu_benchmark.json",
    "memory": "docs/reports/benchmarks/memory_benchmark.json",
    "disk": "docs/reports/benchmarks/disk_benchmark.json",
}


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as stream:
        return json.load(stream)


def create_markdown(report: dict) -> str:
    md = ["# Hardware Benchmark Report — OmniMind", ""]
    md.append(f"Data: {datetime.now(UTC).isoformat()}")
    md.append("")
    system = report.get("system_info", {})
    cpu = system.get("cpu", {})
    memory = system.get("memory", {})
    disk = system.get("disk", [])
    gpu = report.get("gpu", {})
    md.append("## Resumo Executivo")
    md.append("")
    md.append(f"- **CPU:** {cpu.get('physical_cores')} phys / {cpu.get('logical_cores')} log cores")
    md.append("- **Memória:** {:.1f} GB total".format(memory.get("total", 0) / (1024**3)))
    md.append("- **GPU:** {}".format(gpu.get("status", "N/A")))
    md.append("- **Disco:** {}".format(disk[0]["fstype"] if disk else "N/A"))
    md.append("")
    md.append("## Resultados de Benchmark")
    md.append("| Teste | Resultado | Unidade |")
    md.append("| --- | --- | --- |")
    cpu_data = report.get("cpu", {})
    md.append(f"| Loop 1M iterações | {cpu_data.get('loop_ms', 'N/A'):.2f} | ms |")
    md.append(f"| Operações matemáticas | {cpu_data.get('math_ms', 'N/A'):.2f} | ms |")
    md.append(f"| SHA-256 (hash) | {cpu_data.get('hash_ms', 'N/A'):.2f} | ms |")
    md.append(f"| Compressão (zlib) | {cpu_data.get('compression_ms', 'N/A'):.2f} | ms |")
    md.append(
        f"| Memory throughput | {report.get('memory', {}).get('memory_throughput_mb_s', ['N/A'])[0]:.2f} | MB/s |"
    )
    md.append(
        f"| Disk seq. write | {report.get('disk', {}).get('write_throughput_mb_s', 'N/A'):.2f} | MB/s |"
    )
    md.append(
        f"| Disk seq. read | {report.get('disk', {}).get('read_throughput_mb_s', 'N/A'):.2f} | MB/s |"
    )
    md.append(
        f"| Disk random | {report.get('disk', {}).get('random_access_mb_s', 'N/A'):.2f} | MB/s |"
    )
    md.append("")
    md.append("## Recomendações")
    md.append("")
    md.append(
        "- GPU está subutilizada ou indisponível; priorizar mais workloads CUDA caso seja confirmada a sustentabilidade."
    )
    md.append(
        "- CPU com headroom: considerar paralelizar loops críticos e usar vectores em numpy/torch."
    )
    md.append("- Memória em nível alto; usar caches em RAM para evitar re-loads.")
    md.append(
        "- Disco pode ser gargalo; cache parcial em memória e monitorar latência por I/O random."
    )
    md.append("")
    md.append("## Detalhes")
    md.append(json.dumps(report, indent=2))
    return "\n".join(md)


def main() -> None:
    report = {}
    for key, path in BENCHMARK_FILES.items():
        report[key if key != "system" else "system_info"] = load_json(path)
    with open("docs/reports/hardware_audit.json", "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    markdown = create_markdown(report)
    with open("docs/reports/HARDWARE_BENCHMARK_REPORT.md", "w", encoding="utf-8") as stream:
        stream.write(markdown)


if __name__ == "__main__":
    main()
