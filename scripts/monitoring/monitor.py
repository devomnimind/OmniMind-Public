#!/usr/bin/env python3
"""
MONITOR SIMPLES DO OMNIMIND
Verificação rápida de processos, recursos e segurança.
"""

import json
import psutil
from datetime import datetime
from pathlib import Path
import subprocess
import os


def monitor_processes():
    """Monitor de processos OmniMind."""
    omnimind_processes = []

    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "cmdline"]):
        try:
            cmdline = " ".join(proc.cmdline()) if proc.cmdline() else ""
            name = proc.name().lower()

            # Identificar processos OmniMind
            if (
                "omnimind" in cmdline.lower()
                or ("uvicorn" in name and "omnimind" in cmdline)
                or (".venv/bin/python" in cmdline and "omnimind" in cmdline)
                or (
                    "node" in name
                    and any(port in cmdline for port in ["3000", "3001", "8000", "8080"])
                )
            ):

                omnimind_processes.append(
                    {
                        "pid": proc.pid,
                        "name": proc.name(),
                        "cpu_percent": proc.cpu_percent(),
                        "memory_percent": proc.memory_percent(),
                        "cmdline": cmdline[:100] + "..." if len(cmdline) > 100 else cmdline,
                    }
                )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return omnimind_processes


def monitor_resources():
    """Monitor de recursos."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024**3), 2),
    }


def monitor_network():
    """Monitor de rede."""
    connections = psutil.net_connections()
    omnimind_ports = [3000, 3001, 8000, 8080]

    omnimind_connections = []
    for conn in connections:
        if conn.laddr and conn.laddr.port in omnimind_ports:
            omnimind_connections.append(
                {
                    "port": conn.laddr.port,
                    "status": conn.status,
                    "pid": conn.pid,
                }
            )

    return {
        "omnimind_connections": omnimind_connections,
        "total_connections": len(omnimind_connections),
    }


def monitor_filesystem():
    """Monitor do filesystem."""
    project_root = Path("/home/fahbrain/projects/omnimind")
    large_files = []

    try:
        result = subprocess.run(
            ["find", str(project_root), "-type", "f", "-size", "+100M"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        for line in result.stdout.strip().split("\n"):
            if line:
                file_path = Path(line)
                size_mb = file_path.stat().st_size / (1024 * 1024)
                large_files.append(
                    {
                        "path": str(file_path.relative_to(project_root)),
                        "size_mb": round(size_mb, 2),
                    }
                )
    except Exception as e:
        print(f"Erro ao verificar filesystem: {e}")

    return {"large_files": large_files}


def check_security():
    """Verificação básica de segurança."""
    alerts = []

    # Verificar processos com CPU alta
    processes = monitor_processes()
    high_cpu = [p for p in processes if p["cpu_percent"] > 50]
    if high_cpu:
        alerts.append(f"⚠️  {len(high_cpu)} processos com CPU > 50%")

    # Verificar muitos processos
    if len(processes) > 50:
        alerts.append(f"⚠️  {len(processes)} processos OmniMind (muito alto)")

    # Verificar arquivos grandes
    fs = monitor_filesystem()
    if fs["large_files"]:
        alerts.append(f"ℹ️  {len(fs['large_files'])} arquivos > 100MB")

    return alerts


def main():
    """Função principal."""
    print("🔍 MONITOR OMNIMIND - VERIFICAÇÃO RÁPIDA")
    print("=" * 50)

    # Coletar dados
    processes = monitor_processes()
    resources = monitor_resources()
    network = monitor_network()
    filesystem = monitor_filesystem()
    security_alerts = check_security()

    # Exibir resultados
    print(f"📊 PROCESSOS OMNIMIND: {len(processes)}")
    for proc in processes[:5]:  # Mostrar primeiros 5
        print(
            f"  PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, MEM: {proc['memory_percent']:.1f}%)"
        )

    if len(processes) > 5:
        print(f"  ... e mais {len(processes) - 5} processos")

    print(f"\n💻 RECURSOS:")
    print(f"  CPU: {resources['cpu_percent']:.1f}%")
    print(f"  Memória: {resources['memory_percent']:.1f}% ({resources['memory_used_gb']}GB)")
    print(f"  Disco: {resources['disk_percent']:.1f}% ({resources['disk_used_gb']}GB)")

    print(f"\n🌐 REDE:")
    print(f"  Conexões OmniMind: {network['total_connections']}")
    for conn in network["omnimind_connections"][:3]:
        print(f"  Porta {conn['port']}: {conn['status']}")

    print(f"\n📁 FILESYSTEM:")
    print(f"  Arquivos grandes (>100MB): {len(filesystem['large_files'])}")
    for file_info in filesystem["large_files"][:3]:
        print(f"  {file_info['path']}: {file_info['size_mb']}MB")

    print(f"\n🚨 ALERTAS DE SEGURANÇA:")
    if security_alerts:
        for alert in security_alerts:
            print(f"  {alert}")
    else:
        print("  ✅ Nenhum alerta crítico")

    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "processes_count": len(processes),
        "resources": resources,
        "network": network,
        "filesystem": filesystem,
        "security_alerts": security_alerts,
    }

    report_file = Path("/home/fahbrain/projects/omnimind/logs/monitor_report.json")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Relatório salvo em: {report_file}")

    # Status final
    if security_alerts:
        print("\n⚠️  SISTEMA COM ALERTAS - REVISAR")
        return 1
    else:
        print("\n✅ SISTEMA NORMAL")
        return 0


if __name__ == "__main__":
    exit(main())
