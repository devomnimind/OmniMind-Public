"""Shared helpers for security playbook commands."""

import asyncio
import logging
import os
import shutil
import subprocess
from typing import List, Sequence, Set, TypedDict

logger = logging.getLogger(__name__)


class CommandResult(TypedDict):
    command: str
    returncode: int
    output: str


class CommandResultWithStatus(CommandResult, total=False):
    status: str
    reason: str


# Lista de comandos seguros permitidos para o OmniMind
SAFE_COMMANDS: Set[str] = {
    # Monitoramento básico (sem sudo)
    "ps",
    "top",
    "htop",
    "free",
    "df",
    "du",
    "uptime",
    "who",
    "w",
    "last",
    "netstat",
    "ss",
    "ip",
    "ifconfig",
    "route",
    "arp",
    "ping",
    "traceroute",
    "nslookup",
    "dig",
    "host",
    "curl",
    "wget",
    "lsof",
    "fuser",
    "pgrep",
    "pkill",
    "kill",
    "killall",
    "tail",
    "head",
    "cat",
    "echo",
    "grep",
    "awk",
    "sed",
    "sort",
    "uniq",
    "wc",
    "find",
    "locate",
    "which",
    "whereis",
    "type",
    "ls",
    "pwd",
    "cd",
    "mkdir",
    "rmdir",
    "touch",
    "stat",
    "file",
    "date",
    "cal",
    "bc",
    "expr",
    "seq",
    "shuf",
    "python",
    "python3",
    "pip",
    "pip3",
    "git",
    "hg",
    "svn",
    "tar",
    "gzip",
    "gunzip",
    "bzip2",
    "bunzip2",
    "xz",
    "unxz",
    "less",
    "more",
    "nano",
    "vim",
    "emacs",
    # Comandos sudo permitidos (NOPASSWD no sudoers)
    "sudo",
    # Ferramentas de segurança (quando disponíveis)
    "aide",
    "chkrootkit",
    "rkhunter",
    "lynis",
    "clamdscan",
    "ufw",
    "auditctl",
    "ausearch",
    "chattr",
    "systemctl",
    "journalctl",
    "iptables",
    "tc",
    "freshclam",
}

# Padrões proibidos em comandos
FORBIDDEN_PATTERNS: List[str] = [
    # Sistema crítico
    "reboot",
    "shutdown",
    "halt",
    "poweroff",
    "systemctl reboot",
    "systemctl poweroff",
    "init 0",
    "init 6",
    "telinit",
    # Modificação de sistema
    "rm -rf /",
    "rm -rf /*",
    "rm -rf /etc",
    "rm -rf /usr",
    "rm -rf /var",
    "dd if=",
    "mkfs",
    "fdisk",
    "parted",
    "mount",
    "umount",
    "fsck",
    "tune2fs",
    "chmod 777",
    "chown root",
    "chgrp root",
    # Rede perigosa
    "iptables -F",
    "iptables -X",
    "ufw --force disable",
    "ifdown",
    "ifup",
    "service networking restart",
    # Usuários e senhas
    "passwd",
    "usermod",
    "userdel",
    "useradd",
    "groupmod",
    "groupdel",
    "groupadd",
    "vipw",
    "vigr",
    # Kernel e módulos
    "modprobe",
    "rmmod",
    "insmod",
    "lsmod",
    "sysctl -w",
    "sysctl -p",
    # Logs (não pode deletar)
    "rm /var/log",
    "truncate /var/log",
    "> /var/log",
    # Cron e agendamento
    "crontab -r",
    "crontab -e",
    # Pacotes (não pode instalar/remover)
    "apt-get install",
    "apt-get remove",
    "apt-get purge",
    "yum install",
    "yum remove",
    "dnf install",
    "dnf remove",
    "pacman -S",
    "pacman -R",
    "emerge",
    "pip install",
    "pip uninstall",
    # Edição de arquivos críticos
    "vim /etc/passwd",
    "vim /etc/shadow",
    "vim /etc/sudoers",
    "nano /etc/passwd",
    "nano /etc/shadow",
    "nano /etc/sudoers",
]

# Diretórios proibidos para escrita/modificação
FORBIDDEN_PATHS: List[str] = [
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/lib",
    "/lib64",
    "/boot",
    "/sys",
    "/proc",
    "/dev",
    "/root",
    "/var/log",
    "/var/spool",
    "/var/mail",
]


def is_command_safe(command: Sequence[str]) -> bool:
    """
    Verifica se um comando é seguro para execução pelo OmniMind.

    Args:
        command: Lista de strings representando o comando

    Returns:
        True se o comando é seguro, False caso contrário
    """
    if not command:
        return False

    # Verificar se o comando base é permitido
    base_cmd = command[0]
    # Extrair nome do comando (ignora caminho completo)
    cmd_name = os.path.basename(base_cmd) if "/" in base_cmd else base_cmd

    if cmd_name not in SAFE_COMMANDS:
        logger.warning(f"Comando base não permitido: {base_cmd}")
        return False

    # Converter comando para string para análise de padrões
    cmd_str = " ".join(command)

    # Verificar padrões proibidos
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in cmd_str:
            logger.warning(f"Padrão proibido detectado: {pattern} em comando: {cmd_str}")
            return False

    # Verificar caminhos proibidos
    for path in FORBIDDEN_PATHS:
        if path in cmd_str and (
            "rm" in command or "mv" in command or "cp" in command or ">" in cmd_str
        ):
            logger.warning(f"Modificação em caminho proibido: {path} em comando: {cmd_str}")
            return False

    # Verificações específicas para sudo
    if cmd_name == "sudo":
        if len(command) < 2:
            return False

        # Verificar se é um comando sudo permitido
        sudo_cmd = command[1]
        sudo_cmd_name = os.path.basename(sudo_cmd) if "/" in sudo_cmd else sudo_cmd
        if sudo_cmd_name not in SAFE_COMMANDS:
            logger.warning(f"Comando sudo não permitido: {sudo_cmd}")
            return False

        # Verificar se usa -n (non-interactive) para comandos automatizados
        if "-n" not in command:
            logger.warning("Comandos sudo devem usar -n para modo não-interativo")
            return False

    return True


def validate_command_safety(command: Sequence[str]) -> CommandResultWithStatus:
    """
    Valida a segurança de um comando antes da execução.

    Args:
        command: Comando a ser validado

    Returns:
        Resultado da validação
    """
    if is_command_safe(command):
        return {
            "command": " ".join(command),
            "returncode": 0,
            "output": "Comando aprovado para execução",
            "status": "approved",
        }
    else:
        reason = "Comando contém operações proibidas ou não autorizadas"
        logger.error(f"Comando rejeitado: {' '.join(command)} - {reason}")
        return skipped_command(" ".join(command), reason)


def run_command(command: Sequence[str]) -> CommandResult:
    # Primeiro verificar se comando existe
    if not command or not shutil.which(command[0]):
        return {
            "command": " ".join(command) if command else "",
            "returncode": -1,
            "output": "command not available",
        }

    # Depois validar segurança
    validation = validate_command_safety(command)
    if validation.get("status") == "skipped":
        return {
            "command": " ".join(command) if command else "",
            "returncode": -1,
            "output": validation.get("reason", "Comando não autorizado"),
        }

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "output": result.stdout.strip(),
        }
    except subprocess.CalledProcessError as exc:
        # Check for interactive fallback
        allow_interactive = os.environ.get("OMNIMIND_INTERACTIVE", "false").lower() == "true"
        is_sudo_non_interactive = command[0] == "sudo" and "-n" in command

        if allow_interactive and is_sudo_non_interactive and shutil.which("pkexec"):
            try:
                # Construct pkexec command (remove sudo and -n)
                real_cmd = [c for c in command if c not in ["sudo", "-n"]]
                pkexec_cmd = ["pkexec"] + real_cmd
                logger.info("Escalating to interactive pkexec for: %s", real_cmd)

                # Increase timeout for user interaction
                result = subprocess.run(
                    pkexec_cmd, capture_output=True, text=True, check=True, timeout=300
                )
                return {
                    "command": " ".join(pkexec_cmd),
                    "returncode": result.returncode,
                    "output": result.stdout.strip(),
                }
            except Exception as pk_exc:
                logger.warning("pkexec fallback failed: %s", pk_exc)

        logger.warning("Command %s failed: %s", command, exc)
        return {
            "command": " ".join(command),
            "returncode": exc.returncode,
            "output": exc.output or exc.stderr or "",
        }


async def run_command_async(command: Sequence[str]) -> CommandResult:
    return await asyncio.to_thread(run_command, command)


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def skipped_command(command: str, reason: str) -> CommandResultWithStatus:
    """
    Cria um resultado de comando para quando uma operação é pulada.

    Args:
        command: Nome do comando que foi pulado
        reason: Razão pela qual foi pulado

    Returns:
        CommandResultWithStatus indicando que foi pulado
    """
    return {
        "command": command,
        "returncode": -1,
        "output": f"Skipped: {reason}",
        "status": "skipped",
        "reason": reason,
    }
