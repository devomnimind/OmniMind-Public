#!/usr/bin/env python3
"""
DEMONSTRAÇÃO: Como visualizar alertas do sistema de monitoramento

Execute este script para ver alertas em tempo real (requer backend rodando)
"""

import json
from pathlib import Path

import requests


def main():
    """Demonstração de alertas."""
    print("=" * 80)
    print("🎯 DEMONSTRAÇÃO: SISTEMA DE MONITORAMENTO & ALERTAS")
    print("=" * 80)
    print()

    api_url = "http://localhost:8000"

    # 1. Health check
    print("1️⃣  STATUS DO MONITOR")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/api/monitoring/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            cpu_val = data["cpu"]["current"]
            cpu_status = data["cpu"]["status"]
            mem_val = data["memory"]["current"]
            mem_status = data["memory"]["status"]
            disk_val = data["disk"]["current"]
            disk_status = data["disk"]["status"]
            print(f"✅ CPU:     {cpu_val:.1f}% ({cpu_status})")
            print(f"✅ Memória: {mem_val:.1f}% ({mem_status})")
            print(f"✅ Disco:   {disk_val:.1f}% ({disk_status})")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
    print()

    # 2. Alertas ativos
    print("2️⃣  ALERTAS ATIVOS (Críticos)")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/api/monitoring/alerts/active", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data["critical"]:
                for alert in data["critical"]:
                    severity = alert["severity"].upper()
                    title = alert["title"]
                    message = alert["message"]
                    context = json.dumps(alert["context"], indent=6)
                    print(f"🔴 [{severity}] {title}")
                    print(f"   Mensagem: {message}")
                    print(f"   Contexto: {context}")
                    print()
            else:
                print("✅ Nenhum alerta crítico no momento")
    except Exception as e:
        print(f"❌ Erro: {e}")
    print()

    # 3. Alertas recentes
    print("3️⃣  ÚLTIMOS 10 ALERTAS")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/api/monitoring/alerts/active", timeout=2)
        if response.status_code == 200:
            data = response.json()
            total = data["total"]
            print(f"Total de alertas: {total}")
            print()
            for i, alert in enumerate(data["recent"][-10:], 1):
                severity = alert["severity"].upper()
                title = alert["title"]
                timestamp = alert["timestamp"]
                print(f"{i}. [{severity:8}] {title:40} ({timestamp:.0f})")
    except Exception as e:
        print(f"❌ Erro: {e}")
    print()

    # 4. Status completo
    print("4️⃣  STATUS INTEGRADO")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/api/monitoring/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            level = data["monitor"].get("level", "N/A")
            snapshots = data["monitor"].get("snapshots_count", 0)
            total_alerts = data["alerts"].get("total", 0)
            critical_alerts = data["alerts"].get("critical", 0)
            print(f"Monitor Level:     {level}")
            print(f"Snapshots coletados: {snapshots}")
            print(f"Alertas totais:    {total_alerts}")
            print(f"Alertas críticos:  {critical_alerts}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    print()

    # 5. Arquivos de alertas
    print("5️⃣  HISTÓRICO DE ALERTAS (JSON)")
    print("-" * 80)
    alerts_dir = Path("data/alerts")
    if alerts_dir.exists():
        alert_files = sorted(alerts_dir.glob("alert_*.json"))[-5:]
        if alert_files:
            print("Últimos 5 alertas salvos:")
            for alert_file in alert_files:
                print(f"  • {alert_file.name}")
                try:
                    with open(alert_file) as f:
                        alert_data = json.load(f)
                        severity = alert_data["severity"].upper()
                        title = alert_data["title"]
                        print(f"    - {severity}: {title}")
                except Exception as e:
                    print(f"    ❌ Erro ao ler: {e}")
        else:
            print("Nenhum alerta salvo ainda")
    else:
        print(f"Diretório {alerts_dir} não existe")
    print()

    print("=" * 80)
    print("💡 PRÓXIMOS PASSOS:")
    print("=" * 80)
    print("1. Abra VS Code para receber notificações em tempo real")
    print("2. Monitore via API: curl http://localhost:8000/api/monitoring/status")
    print("3. Ver logs: tail -f logs/backend.log | grep monitor")
    print("4. Ver alertas salvos: cat data/alerts/alerts_index.json | jq")
    print()


if __name__ == "__main__":
    main()
