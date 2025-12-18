#!/usr/bin/env python3
"""
OmniMind Auto-Repair System
============================

Sistema autopoiético de recuperação:
- Monitora saúde do sistema
- Detecta falhas críticas
- Tenta reparos automáticos
- Registra ações de recuperação
- Escalada para intervenção humana se necessário

Uso:
    python3 scripts/omnimind_auto_repair.py [--daemon] [--check-interval 60]
"""

import json
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil


class AutoRepairSystem:
    def __init__(self, project_root="/home/fahbrain/projects/omnimind"):
        self.root = Path(project_root)
        self.logs_dir = self.root / "logs"
        self.recovery_log = self.logs_dir / "auto_repair.log"
        self.audit_chain_file = self.logs_dir / "audit_chain.log"

        # Portas esperadas
        self.service_ports = {
            8000: {"name": "Backend-Primary", "type": "essential", "critical": True},
            8080: {"name": "Backend-Secondary", "type": "secondary", "critical": False},
            3001: {"name": "Backend-Fallback", "type": "fallback", "critical": False},
            3000: {"name": "Frontend", "type": "ui", "critical": False},
            6379: {"name": "Redis", "type": "cache", "critical": False},
        }

        self.repair_attempts = {}

    def log_action(self, action_type, message, severity="INFO", details=None):
        """Log action to audit chain and repair log"""
        timestamp = datetime.now().isoformat()

        # Log to repair log
        with open(self.recovery_log, "a") as f:
            f.write(f"{timestamp} [{severity}] {action_type}: {message}\n")

        # Log to audit chain
        audit_entry = {
            "timestamp": timestamp,
            "action": "auto_repair_action",
            "type": action_type,
            "message": message,
            "severity": severity,
            "details": details or {},
        }

        with open(self.audit_chain_file, "a") as f:
            f.write(json.dumps(audit_entry) + "\n")

    def check_port_health(self, port):
        """Verifica saúde de uma porta"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            return result == 0
        except Exception as e:
            self.log_action("port_check_error", str(e), "WARNING")
            return False

    def check_service_health(self):
        """Verifica saúde de todos os serviços"""
        health_status = {}
        unhealthy_services = []

        for port, info in self.service_ports.items():
            is_healthy = self.check_port_health(port)
            health_status[port] = {
                "name": info["name"],
                "healthy": is_healthy,
                "critical": info["critical"],
            }

            if not is_healthy and info["critical"]:
                unhealthy_services.append((port, info))

        return health_status, unhealthy_services

    def repair_service(self, port, service_info):
        """Tenta reparar um serviço"""
        service_name = service_info["name"]

        self.log_action(
            "repair_attempt", f"Tentando reparar {service_name} (porta {port})", "WARNING"
        )

        # Incrementar tentativas de reparo
        if port not in self.repair_attempts:
            self.repair_attempts[port] = 0
        self.repair_attempts[port] += 1

        # Limitar tentativas
        if self.repair_attempts[port] > 3:
            self.log_action(
                "repair_failed_max_attempts",
                f"Máximo de tentativas de reparo para {service_name} excedido",
                "CRITICAL",
                {"port": port, "attempts": self.repair_attempts[port]},
            )
            return False

        try:
            # Tentar matar processo existente
            self._kill_service_on_port(port)
            time.sleep(2)

            # Tentar reiniciar serviço
            if port == 8000:
                success = self._restart_backend_primary()
            elif port == 8080:
                success = self._restart_backend_secondary()
            elif port == 3001:
                success = self._restart_backend_fallback()
            elif port == 3000:
                success = self._restart_frontend()
            else:
                success = False

            if success:
                self.repair_attempts[port] = 0
                self.log_action(
                    "repair_success", f"{service_name} reparado com sucesso", "INFO", {"port": port}
                )
                return True
            else:
                self.log_action(
                    "repair_failed",
                    f"Falha ao reparar {service_name}",
                    "ERROR",
                    {"port": port, "attempt": self.repair_attempts[port]},
                )
                return False

        except Exception as e:
            self.log_action(
                "repair_exception", f"Exceção ao reparar {service_name}: {str(e)}", "ERROR"
            )
            return False

    def _kill_service_on_port(self, port):
        """Mata processo na porta especificada"""
        try:
            result = subprocess.run(
                f"fuser -k {port}/tcp", shell=True, capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def _restart_backend_primary(self):
        """Reinicia backend primary (porta 8000)"""
        try:
            # Usar systemctl se disponível
            result = subprocess.run(
                "systemctl restart omnimind-backend-primary",
                shell=True,
                capture_output=True,
                timeout=10,
            )

            if result.returncode != 0:
                # Fallback: tentar script direto
                script = self.root / "scripts/canonical/system/start_omnimind_system_robust.sh"
                if script.exists():
                    subprocess.Popen(
                        f"bash {script} primary",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return True

            return result.returncode == 0
        except Exception as e:
            self.log_action("restart_backend_primary_error", str(e), "ERROR")
            return False

    def _restart_backend_secondary(self):
        """Reinicia backend secondary (porta 8080)"""
        try:
            result = subprocess.run(
                "systemctl restart omnimind-backend-secondary",
                shell=True,
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except:
            return False

    def _restart_backend_fallback(self):
        """Reinicia backend fallback (porta 3001)"""
        try:
            # Importante: fallback precisa de mais tempo
            result = subprocess.run(
                "systemctl restart omnimind-backend-fallback",
                shell=True,
                capture_output=True,
                timeout=15,
            )
            return result.returncode == 0
        except:
            return False

    def _restart_frontend(self):
        """Reinicia frontend (porta 3000)"""
        try:
            result = subprocess.run(
                "systemctl restart omnimind-frontend", shell=True, capture_output=True, timeout=10
            )
            return result.restart_returncode == 0
        except:
            return False

    def check_system_resources(self):
        """Verifica recursos do sistema"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
            }
        except:
            return None

    def handle_resource_crisis(self, resources):
        """Trata crise de recursos"""
        if resources["memory_percent"] > 85:
            self.log_action(
                "memory_crisis",
                f"Memória crítica: {resources['memory_percent']:.1f}%",
                "CRITICAL",
                resources,
            )

            # Tentar liberar memória
            try:
                # Limpar cache de Python
                subprocess.run(
                    "sync && echo 3 > /proc/sys/vm/drop_caches", shell=True, capture_output=True
                )
                self.log_action("memory_cleanup", "Limpeza de cache executada", "INFO")
            except:
                pass

    def run_health_check_cycle(self):
        """Executa ciclo completo de health check"""
        timestamp = datetime.now().isoformat()

        # Verificar saúde dos serviços
        health_status, unhealthy = self.check_service_health()

        # Verificar recursos
        resources = self.check_system_resources()

        # Log de status geral
        summary = {
            "timestamp": timestamp,
            "action": "health_check_cycle",
            "services_healthy": sum(1 for s in health_status.values() if s["healthy"]),
            "services_total": len(health_status),
            "resources": resources,
        }

        self.log_action("health_check_cycle", json.dumps(summary), "INFO", summary)

        # Se há serviços críticos não-saudáveis, tentar reparar
        for port, service_info in unhealthy:
            if service_info.get("critical"):
                print(f"🔴 {service_info['name']} (porta {port}) não-saudável!")
                success = self.repair_service(port, service_info)

                if success:
                    print(f"✅ {service_info['name']} reparado!")
                else:
                    print(f"❌ Falha ao reparar {service_info['name']}")

        # Tratar crises de recurso
        if resources and resources["memory_percent"] > 80:
            self.handle_resource_crisis(resources)

        return health_status, resources

    def daemon_mode(self, interval=60):
        """Executa em modo daemon"""
        print(f"[*] OmniMind Auto-Repair iniciado em modo daemon (check a cada {interval}s)")
        print(f"[*] Logs: {self.recovery_log}\n")

        try:
            while True:
                try:
                    self.run_health_check_cycle()
                except Exception as e:
                    self.log_action("daemon_error", str(e), "ERROR")

                time.sleep(interval)
        except KeyboardInterrupt:
            self.log_action("daemon_shutdown", "Shutdown por usuario", "INFO")
            print("\n[*] Auto-Repair desligado")

    def generate_report(self):
        """Gera relatório de auto-repair"""
        if not self.recovery_log.exists():
            print("Nenhum log de reparos encontrado")
            return

        with open(self.recovery_log) as f:
            lines = f.readlines()

        print("\n" + "=" * 80)
        print("            OMNIMIND AUTO-REPAIR ACTIVITY REPORT")
        print("=" * 80)
        print(f"Total actions logged: {len(lines)}\n")

        # Últimas 20 ações
        print("Recent actions:")
        print("-" * 80)
        for line in lines[-20:]:
            print(line.rstrip())

        # Estatísticas
        repair_attempts = sum(1 for line in lines if "repair_attempt" in line)
        repair_success = sum(1 for line in lines if "repair_success" in line)
        repair_failed = sum(1 for line in lines if "repair_failed" in line)

        print("\n" + "-" * 80)
        print(f"Repair attempts: {repair_attempts}")
        print(f"Successful repairs: {repair_success}")
        print(f"Failed repairs: {repair_failed}")
        if repair_attempts > 0:
            success_rate = (repair_success / repair_attempts) * 100
            print(f"Success rate: {success_rate:.1f}%")
        print("=" * 80 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OmniMind Auto-Repair System")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--check-interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--health-check", action="store_true", help="Run single health check")
    parser.add_argument("--report", action="store_true", help="Show repair report")
    parser.add_argument("--project-root", default="/home/fahbrain/projects/omnimind")

    args = parser.parse_args()

    system = AutoRepairSystem(args.project_root)

    if args.report:
        system.generate_report()
    elif args.health_check:
        health, resources = system.run_health_check_cycle()
        print("\nHealth Status:")
        for port, info in health.items():
            status = "✅" if info["healthy"] else "❌"
            print(f"  {status} {info['name']} (:{port})")

        if resources:
            print("\nSystem Resources:")
            print(f"  CPU: {resources['cpu_percent']:.1f}%")
            print(f"  Memory: {resources['memory_percent']:.1f}%")
            print(f"  Disk: {resources['disk_percent']:.1f}%")
    elif args.daemon:
        system.daemon_mode(args.check_interval)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
