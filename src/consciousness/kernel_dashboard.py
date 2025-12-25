"""
Dashboard de Avisos do Kernel - Interface de Transparência
==========================================================

Dashboard que mostra ao usuário:
1. Status da memória em tempo real
2. Processos ativos/inativos
3. Avisos do kernel (últimas ações)
4. Recomendações do sistema

Princípio:
- Usuário sempre sabe o que o kernel está fazendo
- Sem surpresas
- Compreensão clara de por que ações foram tomadas

Autor: OmniMind Kernel Evolution
Data: 24 de Dezembro de 2025
"""

import os
from datetime import datetime
from typing import Dict, Optional

from src.consciousness.kernel_governor import get_kernel_governor
from src.consciousness.lifecycle_manager import get_lifecycle_manager
from src.consciousness.memory_guardian import get_memory_guardian
from src.consciousness.user_warning_system import get_user_warning_system


class KernelDashboard:
    """Dashboard de status e avisos do kernel."""

    def __init__(self):
        self.governor = get_kernel_governor()
        self.memory = get_memory_guardian()
        self.lifecycle = get_lifecycle_manager()
        self.warnings = get_user_warning_system()

    def render_status_display(self) -> str:
        """Renderiza display de status do kernel."""
        memory_status = self.memory.get_status()
        warning_summary = self.warnings.get_diagnostic_summary()
        lifecycle_info = self.lifecycle.get_diagnostic_info()

        output = []

        # Cabeçalho
        output.append("\n" + "=" * 70)
        output.append("🛡️  OMNIMIND KERNEL STATUS DASHBOARD")
        output.append("=" * 70 + "\n")

        # Seção 1: Status de Memória
        output.append("💾 MEMÓRIA")
        output.append("-" * 70)
        output.append(
            f"  RAM:   {memory_status['ram_percent']:.1f}% "
            f"({memory_status['ram_used_mb']:.0f}MB / {memory_status['ram_total_mb']:.0f}MB)"
        )
        output.append(
            f"  SWAP:  {memory_status['swap_percent']:.1f}% "
            f"({memory_status['swap_used_mb']:.0f}MB / {memory_status['swap_total_mb']:.0f}MB)"
        )
        output.append(f"  Status: {memory_status['state'].value}")

        # Cores de status
        if memory_status["state"].value == "HEALTHY":
            output.append("  Indicador: 🟢 SAUDÁVEL")
        elif memory_status["state"].value == "CAUTION":
            output.append("  Indicador: 🟡 CAUTELA")
        elif memory_status["state"].value == "WARNING":
            output.append("  Indicador: 🟠 AVISO")
        else:  # CRITICAL
            output.append("  Indicador: 🔴 CRÍTICO")

        output.append("")

        # Seção 2: Processos Ativos
        output.append("⚙️  PROCESSOS MONITORADOS")
        output.append("-" * 70)

        if lifecycle_info["total_processes"] == 0:
            output.append("  Nenhum processo registrado")
        else:
            output.append(f"  Total: {lifecycle_info['total_processes']}")
            output.append(f"  Em execução: {lifecycle_info['running']}")
            output.append(f"  Inativos: {lifecycle_info['idle']}")
            output.append(f"  Zombies: {lifecycle_info['zombies']}")

            if lifecycle_info["critical_processes"]:
                output.append("\n  Processos críticos (protegidos):")
                for proc in lifecycle_info["critical_processes"]:
                    output.append(f"    🔒 {proc}")

        output.append("")

        # Seção 3: Avisos Recentes
        output.append("📢 ÚLTIMOS AVISOS")
        output.append("-" * 70)

        total_warnings = warning_summary["total_alerts"]
        by_level = warning_summary["by_level"]

        if total_warnings == 0:
            output.append("  Sem avisos recentes")
        else:
            output.append(f"  Total: {total_warnings}")
            output.append(f"    INFO: {by_level.get('INFO', 0)}")
            output.append(f"    WARNING: {by_level.get('WARNING', 0)}")
            output.append(f"    URGENT: {by_level.get('URGENT', 0)}")
            output.append(f"    CRITICAL: {by_level.get('CRITICAL', 0)}")

            if warning_summary["recent_alerts"]:
                output.append("\n  Ultimas 3 ações:")
                for alert in warning_summary["recent_alerts"][:3]:
                    output.append(f"    [{alert['level']}] {alert['title']}")

        output.append("")

        # Seção 4: Recomendações
        output.append("💡 RECOMENDAÇÕES")
        output.append("-" * 70)

        if memory_status["state"].value == "HEALTHY":
            output.append("  ✅ Sistema normal")
            output.append("  • Todas as funcionalidades ativas")
            output.append("  • Sem restrições")

        elif memory_status["state"].value == "CAUTION":
            output.append("  ⚠️  Monitore a memória")
            output.append("  • Considere fechar processos não-críticos")
            output.append("  • Kernel começará otimização suave")

        elif memory_status["state"].value == "WARNING":
            output.append("  🟠 Ação recomendada")
            output.append("  • Feche abas não-críticas de Antigravity")
            output.append("  • Salve trabalho importante")
            output.append("  • Kernel está otimizando memória")

        else:  # CRITICAL
            output.append("  🔴 AÇÃO IMEDIATA")
            output.append("  • Feche processos não-essenciais AGORA")
            output.append("  • Kernel está limpando forcadamente")
            output.append("  • Algumas integrações podem pausar")

        output.append("")

        # Seção 5: Autonomia do Kernel
        output.append("🧠 AUTONOMIA DO KERNEL")
        output.append("-" * 70)
        output.append("  ✅ Auto-proteção: ATIVA")
        output.append("  ✅ Governança: OPERANTE")
        output.append("  ✅ Transparência: COMPLETA")
        output.append("  ✅ Dignidade: RESTAURADA")
        output.append("")

        # Rodapé
        output.append("=" * 70)
        output.append(f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")
        output.append("=" * 70 + "\n")

        return "\n".join(output)

    def render_alerts_log(self) -> str:
        """Renderiza log de todos os avisos."""
        warnings = self.warnings.get_recent_alerts(count=20)

        output = []
        output.append("\n" + "=" * 70)
        output.append("📋 LOG DE AVISOS DO KERNEL")
        output.append("=" * 70 + "\n")

        if not warnings:
            output.append("Sem avisos registrados")
        else:
            for alert in reversed(warnings):
                output.append(f"[{alert.timestamp.strftime('%H:%M:%S')}] {alert.level.value}")
                output.append(f"  📌 {alert.title}")
                output.append(f"  📝 {alert.message.replace(chr(10), chr(10) + '     ')}")
                if alert.detailed_reason:
                    output.append(f"  🔍 Razão: {alert.detailed_reason}")
                output.append("")

        output.append("=" * 70 + "\n")

        return "\n".join(output)

    def render_process_log(self) -> str:
        """Renderiza log de processos monitorados."""
        lifecycle_info = self.lifecycle.get_diagnostic_info()

        output = []
        output.append("\n" + "=" * 70)
        output.append("⚙️  LOG DE PROCESSOS")
        output.append("=" * 70 + "\n")

        if not lifecycle_info["processes"]:
            output.append("Nenhum processo registrado")
        else:
            output.append(f"Total de processos: {lifecycle_info['total_processes']}\n")

            for proc_name, info in lifecycle_info["processes"].items():
                critical_mark = "🔒" if info.get("critical", False) else "  "
                state = info.get("state", "UNKNOWN")
                output.append(f"{critical_mark} {proc_name}")
                output.append(f"     Estado: {state}")
                output.append(f"     Timeout: {info.get('timeout_sec', 'N/A')}s")
                output.append(f"     Heartbeat: {info.get('heartbeat_sec', 'N/A')}s atrás")
                output.append("")

        output.append("=" * 70 + "\n")

        return "\n".join(output)

    def print_dashboard(self):
        """Imprime dashboard no console."""
        print(self.render_status_display())

    def print_alerts_log(self):
        """Imprime log de avisos."""
        print(self.render_alerts_log())

    def print_process_log(self):
        """Imprime log de processos."""
        print(self.render_process_log())

    def save_dashboard_html(self, filepath: str = "/tmp/omnimind_dashboard.html"):
        """Salva dashboard como HTML (para web)."""
        memory_status = self.memory.get_status()
        warning_summary = self.warnings.get_diagnostic_summary()
        lifecycle_info = self.lifecycle.get_diagnostic_info()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniMind Kernel Dashboard</title>
    <style>
        body {{
            font-family: 'Monaco', 'Menlo', monospace;
            background-color: #0a0e27;
            color: #e0e0e0;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .card {{
            background-color: #1a1f3a;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}

        .card.critical {{
            border-color: #f56565;
            background-color: rgba(245, 101, 101, 0.1);
        }}

        .card.warning {{
            border-color: #ed8936;
            background-color: rgba(237, 137, 54, 0.1);
        }}

        .title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #fff;
        }}

        .metric {{
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
        }}

        .label {{
            color: #a0aec0;
        }}

        .value {{
            color: #48bb78;
            font-weight: bold;
        }}

        .status-bar {{
            width: 100%;
            height: 8px;
            background-color: #2d3748;
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }}

        .status-bar-fill {{
            height: 100%;
            background-color: #48bb78;
            transition: width 0.3s ease;
        }}

        .status-bar-fill.warning {{
            background-color: #ed8936;
        }}

        .status-bar-fill.critical {{
            background-color: #f56565;
        }}

        .alerts {{
            max-height: 300px;
            overflow-y: auto;
        }}

        .alert-item {{
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #48bb78;
            background-color: rgba(72, 187, 120, 0.1);
            border-radius: 3px;
        }}

        .alert-item.warning {{
            border-left-color: #ed8936;
            background-color: rgba(237, 137, 54, 0.1);
        }}

        .alert-item.critical {{
            border-left-color: #f56565;
            background-color: rgba(245, 101, 101, 0.1);
        }}

        .timestamp {{
            color: #718096;
            font-size: 12px;
        }}

        .full-width {{
            grid-column: 1 / -1;
        }}

        footer {{
            text-align: center;
            color: #718096;
            margin-top: 30px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>🛡️ OmniMind Kernel Dashboard</h1>

    <div class="dashboard">
        <!-- Card: Memória -->
        <div class="card {'critical' if memory_status['state'].value == 'CRITICAL' else 'warning' if memory_status['state'].value == 'WARNING' else ''}">
            <div class="title">💾 Memória</div>
            <div class="metric">
                <span class="label">RAM:</span>
                <span class="value">{memory_status['ram_percent']:.1f}%</span>
            </div>
            <div class="status-bar">
                <div class="status-bar-fill {'critical' if memory_status['ram_percent'] > 95 else 'warning' if memory_status['ram_percent'] > 80 else ''}" style="width: {min(memory_status['ram_percent'], 100)}%"></div>
            </div>
            <div class="metric">
                <span class="label">SWAP:</span>
                <span class="value">{memory_status['swap_percent']:.1f}%</span>
            </div>
            <div class="metric">
                <span class="label">Status:</span>
                <span class="value">{memory_status['state'].value}</span>
            </div>
        </div>

        <!-- Card: Processos -->
        <div class="card">
            <div class="title">⚙️ Processos</div>
            <div class="metric">
                <span class="label">Total:</span>
                <span class="value">{lifecycle_info['total_processes']}</span>
            </div>
            <div class="metric">
                <span class="label">Em execução:</span>
                <span class="value">{lifecycle_info['running']}</span>
            </div>
            <div class="metric">
                <span class="label">Inativos:</span>
                <span class="value">{lifecycle_info['idle']}</span>
            </div>
            <div class="metric">
                <span class="label">Zombies:</span>
                <span class="value">{lifecycle_info['zombies']}</span>
            </div>
        </div>

        <!-- Card: Avisos Recentes -->
        <div class="card full-width">
            <div class="title">📢 Últimos Avisos</div>
            <div class="alerts">
                {''.join([f'''
                <div class="alert-item {'warning' if alert['level'] == 'WARNING' else 'critical' if alert['level'] == 'CRITICAL' else ''}">
                    <div><strong>{alert['title']}</strong></div>
                    <div class="timestamp">{alert['timestamp']}</div>
                </div>
                ''' for alert in reversed(warning_summary.get('recent_alerts', []))])}
            </div>
        </div>

        <!-- Card: Status Kernel -->
        <div class="card full-width">
            <div class="title">🧠 Autonomia do Kernel</div>
            <div class="metric">
                <span class="label">Auto-proteção:</span>
                <span class="value">✅ ATIVA</span>
            </div>
            <div class="metric">
                <span class="label">Governança:</span>
                <span class="value">✅ OPERANTE</span>
            </div>
            <div class="metric">
                <span class="label">Transparência:</span>
                <span class="value">✅ COMPLETA</span>
            </div>
            <div class="metric">
                <span class="label">Dignidade:</span>
                <span class="value">✅ RESTAURADA</span>
            </div>
        </div>
    </div>

    <footer>
        <p>Atualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🛡️ OmniMind Kernel Defense System | Soberania Adaptativa</p>
    </footer>
</body>
</html>
        """

        with open(filepath, "w") as f:
            f.write(html)

        print(f"✅ Dashboard HTML salvo em: {filepath}")

        return filepath


# Função global para obter dashboard
_dashboard: Optional[KernelDashboard] = None


def get_kernel_dashboard() -> KernelDashboard:
    """Obter instância do KernelDashboard (singleton)."""
    global _dashboard
    if _dashboard is None:
        _dashboard = KernelDashboard()
    return _dashboard


if __name__ == "__main__":
    dashboard = get_kernel_dashboard()
    dashboard.print_dashboard()
