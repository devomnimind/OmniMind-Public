#!/usr/bin/env python3
"""
OmniMind Security Agent
Sistema autonomo de monitoramento, deteccao e resposta
"""

import os
import subprocess
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class SecurityAgent:
    """Agente autonomo de seguranca"""
    
    def __init__(self):
        """Inicializa agente de seguranca"""
        self.event_history = []
        self.incident_log = []
        self.tools_available = self._check_tools()
        
        logger.info("Security Agent inicializado")
    
    def _check_tools(self) -> Dict[str, bool]:
        """Verifica ferramentas disponíveis"""
        tools = {}
        for tool in ["auditctl", "aide", "chkrootkit", "rkhunter"]:
            try:
                subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    timeout=2
                )
                tools[tool] = True
            except:
                tools[tool] = False
        
        return tools
    
    def monitor_processes(self):
        """Monitora processos do sistema"""
        suspicious_names = [
            "nmap", "nikto", "sqlmap", "nc", "ncat", "/dev/tcp"
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                for suspect in suspicious_names:
                    if suspect.lower() in cmdline.lower():
                        logger.warning(
                            f"Processo suspeito: {proc.info['name']} "
                            f"(PID: {proc.info['pid']})"
                        )
                        return {
                            "type": "suspicious_process",
                            "pid": proc.info['pid'],
                            "name": proc.info['name']
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return None
    
    def monitor_network(self):
        """Monitora conexoes de rede"""
        suspicious_ports = [4444, 5555, 6666, 7777, 8888]
        
        try:
            for conn in psutil.net_connections():
                if conn.raddr and conn.raddr[1] in suspicious_ports:
                    logger.warning(
                        f"Conexao suspeita: {conn.laddr} -> {conn.raddr}"
                    )
                    return {
                        "type": "suspicious_connection",
                        "local": str(conn.laddr),
                        "remote": str(conn.raddr)
                    }
        except Exception as e:
            logger.error(f"Erro ao verificar rede: {e}")
        
        return None
    
    def check_file_integrity(self):
        """Verifica integridade de arquivos"""
        if not self.tools_available.get("aide"):
            return None
        
        try:
            result = subprocess.run(
                ["sudo", "aide", "--check"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if "added" in result.stdout or "changed" in result.stdout:
                logger.warning("Mudancas de arquivo detectadas!")
                return {
                    "type": "file_integrity",
                    "details": result.stdout[:200]
                }
        except Exception as e:
            logger.error(f"Erro ao verificar AIDE: {e}")
        
        return None
    
    def respond_to_threat(self, threat: Dict):
        """Responde a ameaca detectada"""
        threat_type = threat.get("type")
        
        if threat_type == "suspicious_process":
            pid = threat.get("pid")
            try:
                os.kill(int(pid), 9)
                logger.warning(f"Processo {pid} eliminado")
            except:
                pass
        
        elif threat_type == "suspicious_connection":
            remote_ip = threat.get("remote", "").split(":")[0]
            try:
                subprocess.run(
                    f"sudo ufw deny from {remote_ip}",
                    shell=True,
                    capture_output=True
                )
                logger.warning(f"IP bloqueado: {remote_ip}")
            except:
                pass
    
    def generate_report(self) -> str:
        """Gera relatorio de seguranca"""
        
        report = f"""
╔════════════════════════════════════════════════════════╗
║         RELATORIO DE SEGURANCA OMNIMIND
║         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╚════════════════════════════════════════════════════════╝

EVENTOS DETECTADOS: {len(self.event_history)}
INCIDENTES: {len(self.incident_log)}

FERRAMENTAS DISPONÍVEIS:
"""
        
        for tool, available in self.tools_available.items():
            status = "Disponivel" if available else "Nao disponivel"
            report += f"  {tool}: {status}
"
        
        return report