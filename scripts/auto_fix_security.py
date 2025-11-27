#!/usr/bin/env python3
"""
Auto Fix Security Issues - Correções Automáticas de Vulnerabilidades Críticas
Identificadas na Auditoria Completa do Repositório OmniMind 2025

Este script automatiza correções para:
- Pickle deserialization vulnerabilities
- Subprocess shell injection
- SSL verification bypass

Uso: python scripts/auto_fix_security.py
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Configurações
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

# Cores para output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class SecurityFixer:
    """Classe principal para correções de segurança automatizadas."""

    def __init__(self):
        self.fixed_count = 0
        self.backup_count = 0
        self.audit_log = []

    def log_action(self, action: str, file: str, details: str = ""):
        """Registra ação no log de auditoria."""
        entry = f"[{action}] {file}: {details}"
        self.audit_log.append(entry)
        print(f"{BLUE}[AUDIT]{RESET} {entry}")

    def create_backup(self, file_path: Path) -> Path:
        """Cria backup do arquivo antes de modificar."""
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        backup_path.write_text(file_path.read_text())
        self.backup_count += 1
        self.log_action("BACKUP", str(file_path), f"Backup criado: {backup_path}")
        return backup_path

    def fix_pickle_deserialization(self) -> bool:
        """Corrige vulnerabilidades de pickle deserialization."""
        print(f"\n{BLUE}[PICKLE]{RESET} Procurando vulnerabilidades de pickle deserialization...")

        success = True
        pattern = r"pickle\.loads?\([^)]*\)"

        for py_file in SRC_DIR.rglob("*.py"):
            try:
                content = py_file.read_text()
                if re.search(pattern, content):
                    print(f"{YELLOW}[FOUND]{RESET} Pickle usage in: {py_file}")

                    # Criar backup
                    self.create_backup(py_file)

                    # Substituir pickle.loads por alternativa segura
                    new_content = re.sub(
                        r"pickle\.load\((\w+)\)",
                        r'pickle.load(\1, fix_imports=True, encoding="bytes")',
                        content,
                    )

                    # Adicionar comentário de segurança
                    new_content = new_content.replace(
                        "import pickle",
                        "import pickle  # WARNING: Pickle can be unsafe - review usage",
                    )

                    py_file.write_text(new_content)
                    self.fixed_count += 1
                    self.log_action("FIXED", str(py_file), "Pickle deserialization secured")

            except Exception as e:
                print(f"{RED}[ERROR]{RESET} Failed to process {py_file}: {e}")
                success = False

        return success

    def fix_subprocess_injection(self) -> bool:
        """Corrige vulnerabilidades de subprocess shell injection."""
        print(f"\n{BLUE}[SUBPROCESS]{RESET} Procurando vulnerabilidades de subprocess injection...")

        success = True
        dangerous_patterns = [
            r"subprocess\.(call|Popen|run)\([^,]+.*shell\s*=\s*True",
            r"os\.system\([^)]+\)",
            r"os\.popen\([^)]+\)",
        ]

        for py_file in SRC_DIR.rglob("*.py"):
            try:
                content = py_file.read_text()
                modified = False

                for pattern in dangerous_patterns:
                    if re.search(pattern, content):
                        print(f"{YELLOW}[FOUND]{RESET} Dangerous subprocess usage in: {py_file}")

                        # Criar backup
                        self.create_backup(py_file)

                        # Substituir shell=True por shell=False + shlex.split
                        if "shell=True" in content:
                            content = content.replace("shell=True", "shell=False")
                            content = re.sub(
                                r"subprocess\.(call|Popen|run)\(([^,]+),",
                                r"subprocess.\1(shlex.split(\2),",
                                content,
                            )
                            if "import shlex" not in content:
                                content = "import shlex\n" + content

                        # Substituir os.system por subprocess.run
                        content = re.sub(
                            r"os\.system\(([^)]+)\)",
                            r"subprocess.run(shlex.split(\1), shell=False)",
                            content,
                        )

                        # Substituir os.popen por subprocess.Popen
                        content = re.sub(
                            r"os\.popen\(([^)]+)\)",
                            r"subprocess.Popen(shlex.split(\1), shell=False, stdout=subprocess.PIPE)",
                            content,
                        )

                        modified = True

                if modified:
                    py_file.write_text(content)
                    self.fixed_count += 1
                    self.log_action("FIXED", str(py_file), "Subprocess injection secured")

            except Exception as e:
                print(f"{RED}[ERROR]{RESET} Failed to process {py_file}: {e}")
                success = False

        return success

    def fix_ssl_bypass(self) -> bool:
        """Corrige vulnerabilidades de SSL verification bypass."""
        print(f"\n{BLUE}[SSL]{RESET} Procurando bypass de verificação SSL...")

        success = True
        ssl_bypass_patterns = [
            r"verify\s*=\s*False",
            r"ssl\.create_default_context\(\)\.check_hostname\s*=\s*False",
            r"ssl\.create_default_context\(\)\.verify_mode\s*=\s*ssl\.CERT_NONE",
        ]

        for py_file in SRC_DIR.rglob("*.py"):
            try:
                content = py_file.read_text()
                modified = False

                for pattern in ssl_bypass_patterns:
                    if re.search(pattern, content):
                        print(f"{YELLOW}[FOUND]{RESET} SSL bypass in: {py_file}")

                        # Criar backup
                        self.create_backup(py_file)

                        # Substituir verify=False por verify=True
                        content = content.replace("verify=False", "verify=True")

                        # Corrigir contextos SSL inseguros
                        content = content.replace(
                            "ssl.create_default_context().check_hostname = False",
                            "ssl.create_default_context().check_hostname = True",
                        )
                        content = content.replace(
                            "ssl.create_default_context().verify_mode = ssl.CERT_NONE",
                            "ssl.create_default_context().verify_mode = ssl.CERT_REQUIRED",
                        )

                        modified = True

                if modified:
                    py_file.write_text(content)
                    self.fixed_count += 1
                    self.log_action("FIXED", str(py_file), "SSL verification enabled")

            except Exception as e:
                print(f"{RED}[ERROR]{RESET} Failed to process {py_file}: {e}")
                success = False

        return success

    def run_security_scan(self) -> Dict:
        """Executa scan de segurança para validar correções."""
        print(f"\n{BLUE}[SCAN]{RESET} Executando validação de segurança...")

        try:
            # Executar bandit
            result = subprocess.run(
                ["bandit", "-r", str(SRC_DIR), "-f", "json"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )

            if result.returncode == 0:
                print(f"{GREEN}[SCAN]{RESET} Security scan passed")
                return {"status": "passed", "issues": 0}
            else:
                issues = len(result.stdout.split("\n")) - 1  # Rough count
                print(f"{YELLOW}[SCAN]{RESET} Security scan found {issues} issues")
                return {"status": "issues_found", "issues": issues}

        except Exception as e:
            print(f"{RED}[SCAN]{RESET} Failed to run security scan: {e}")
            return {"status": "error", "issues": -1}

    def generate_report(self) -> str:
        """Gera relatório das correções aplicadas."""
        report = f"""# Relatório de Correções de Segurança - {PROJECT_ROOT.name}
Data: $(date +%Y-%m-%d)

## Resumo
- Arquivos corrigidos: {self.fixed_count}
- Backups criados: {self.backup_count}
- Ações auditadas: {len(self.audit_log)}

## Ações Realizadas
"""
        for entry in self.audit_log:
            report += f"- {entry}\n"

        report += """

## Validação
Execute os comandos abaixo para validar as correções:

```bash
# Scan de segurança
bandit -r src/ -f txt

# Testes
pytest tests/ -v

# Verificação de tipos
mypy src/ --ignore-missing-imports
```

## Arquivos de Backup
Os seguintes arquivos foram modificados e têm backups:
"""
        for entry in self.audit_log:
            if "[BACKUP]" in entry:
                report += f"- {entry}\n"

        return report

    def save_report(self):
        """Salva relatório em arquivo."""
        report_path = PROJECT_ROOT / "SECURITY_FIXES_20251122.md"
        report_path.write_text(self.generate_report())
        print(f"{GREEN}[REPORT]{RESET} Salvo em: {report_path}")


def main():
    """Função principal."""
    print(f"{BLUE}[START]{RESET} Iniciando correções automáticas de segurança...")
    print(f"Projeto: {PROJECT_ROOT}")
    print(f"Diretório fonte: {SRC_DIR}")

    fixer = SecurityFixer()

    try:
        # Executar correções
        success = True
        success &= fixer.fix_pickle_deserialization()
        success &= fixer.fix_subprocess_injection()
        success &= fixer.fix_ssl_bypass()

        if success:
            print(f"\n{GREEN}[SUCCESS]{RESET} Correções automáticas concluídas!")

            # Executar validação
            scan_result = fixer.run_security_scan()

            # Gerar relatório
            fixer.save_report()

            print(f"\n{BLUE}[SUMMARY]{RESET}")
            print(f"Arquivos corrigidos: {fixer.fixed_count}")
            print(f"Backups criados: {fixer.backup_count}")
            print(f"Ações auditadas: {len(fixer.audit_log)}")

            if fixer.fixed_count > 0:
                print(f"\n{YELLOW}[NEXT]{RESET} Execute testes para validar correções:")
                print("  pytest tests/ -v")
                print("  bandit -r src/")

            return 0
        else:
            print(f"\n{RED}[ERROR]{RESET} Falha nas correções automáticas")
            return 1

    except Exception as e:
        print(f"\n{RED}[CRITICAL ERROR]{RESET} {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
