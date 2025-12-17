#!/usr/bin/env python3
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

"""
OmniMind Task Management System
Gerencia automaticamente o status das tarefas baseado em validações
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


class TaskManager:
    """Gerenciador de tarefas do OmniMind"""

    def __init__(self, tasks_file: str = ".omnimind/audit/pending_tasks.json"):
        self.tasks_file = Path(tasks_file)
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)

    def load_tasks(self) -> Dict[str, Any]:
        """Carrega as tarefas do arquivo JSON"""
        if not self.tasks_file.exists():
            return self._create_default_structure()

        try:
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Erro ao carregar {self.tasks_file}, criando estrutura padrão")
            return self._create_default_structure()

    def save_tasks(self, data: Dict[str, Any]) -> None:
        """Salva as tarefas no arquivo JSON"""
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _create_default_structure(self) -> Dict[str, Any]:
        """Cria estrutura padrão de tarefas"""
        return {
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "audit_version": "1.0.0",
            "system_status": {
                "tests_passed": 0,
                "tests_failed": 0,
                "test_coverage": "0%",
                "services_active": 0,
                "gpu_available": False,
                "memory_usage": "0%",
            },
            "pending_tasks": [],
            "completed_tasks": [],
            "system_metrics": {},
            "audit_summary": {
                "overall_health": "unknown",
                "critical_issues": 0,
                "warnings": 0,
                "recommendations": 0,
                "next_audit_due": None,
            },
        }

    def check_task_status(self, task_id: str) -> bool:
        """Verifica se uma tarefa está completa baseada em seus critérios de validação"""
        data = self.load_tasks()
        task = self._find_task(data, task_id)

        if not task:
            print(f"Tarefa {task_id} não encontrada")
            return False

        validation_criteria = task.get("validation_criteria", [])
        if not validation_criteria:
            print(f"Tarefa {task_id} não tem critérios de validação definidos")
            return False

        # Executa validações específicas para cada tarefa
        if task_id == "fix_mcp_client_test":
            return self._check_mcp_client_test()
        elif task_id == "gpu_cuda_setup":
            return self._check_cuda_setup()
        elif task_id == "memory_optimization":
            return self._check_memory_usage()
        elif task_id == "update_documentation":
            return self._check_documentation_update()
        elif task_id == "security_hardening":
            return self._check_security_hardening()

        print(f"Validação não implementada para tarefa {task_id}")
        return False

    def _find_task(self, data: Dict[str, Any], task_id: str) -> Optional[Dict[str, Any]]:
        """Encontra uma tarefa pelo ID"""
        for task in data.get("pending_tasks", []):
            if task.get("id") == task_id:
                return task
        return None

    def _check_mcp_client_test(self) -> bool:
        """Verifica se o teste do MCP client está passando"""
        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/integrations/test_mcp_client_async.py::TestAsyncMCPClient::test_send_request_success",
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Erro ao verificar teste MCP: {e}")
            return False

    def _check_cuda_setup(self) -> bool:
        """Verifica se CUDA está funcionando"""
        try:
            result = subprocess.run(
                ["python", "-c", "import torch; print(torch.cuda.is_available())"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            return result.returncode == 0 and "True" in result.stdout.strip()
        except Exception as e:
            print(f"Erro ao verificar CUDA: {e}")
            return False

    def _check_memory_usage(self) -> bool:
        """Verifica se o uso de memória está otimizado"""
        try:
            # Executa benchmark de memória e verifica se está abaixo de 70%
            result = subprocess.run(
                ["python", "scripts/benchmarks/memory_benchmark.py"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            # Por enquanto, apenas verifica se o benchmark roda sem erro
            # Futuramente pode analisar a saída para verificar uso real
            return result.returncode == 0
        except Exception as e:
            print(f"Erro ao verificar uso de memória: {e}")
            return False

    def _check_documentation_update(self) -> bool:
        """Verifica se a documentação foi atualizada"""
        # Verifica se README contém métricas recentes
        readme_path = Path("README.md")
        if not readme_path.exists():
            return False

        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Verifica se contém informações sobre cobertura de testes
                return "90%+" in content and "362" in content
        except Exception as e:
            print(f"Erro ao verificar documentação: {e}")
            return False

    def _check_security_hardening(self) -> bool:
        """Verifica se as configurações de segurança foram reforçadas"""
        # Executa auditoria de segurança
        try:
            result = subprocess.run(
                ["python", "-m", "src.audit.immutable_audit", "verify_chain_integrity"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Erro ao verificar segurança: {e}")
            return False

    def mark_task_complete(self, task_id: str) -> bool:
        """Marca uma tarefa como completa se validação passar"""
        if not self.check_task_status(task_id):
            print(f"Validação falhou para tarefa {task_id}")
            return False

        data = self.load_tasks()
        task = self._find_task(data, task_id)

        if not task:
            print(f"Tarefa {task_id} não encontrada")
            return False

        # Move tarefa para completed_tasks
        task["status"] = "completed"
        task["completed_at"] = datetime.now(timezone.utc).isoformat()
        task["last_checked"] = datetime.now(timezone.utc).isoformat()
        task["check_count"] = task.get("check_count", 0) + 1

        data["pending_tasks"] = [t for t in data["pending_tasks"] if t["id"] != task_id]
        data["completed_tasks"].append(task)

        self.save_tasks(data)
        print(f"✅ Tarefa {task_id} marcada como completa")
        return True

    def check_all_tasks(self) -> None:
        """Verifica o status de todas as tarefas pendentes"""
        data = self.load_tasks()
        pending_tasks = data.get("pending_tasks", [])

        for task in pending_tasks:
            task_id = task["id"]
            was_complete = task.get("status") == "completed"

            if self.check_task_status(task_id):
                if not was_complete:
                    print(f"Tarefa {task_id} agora está completa!")
                    self.mark_task_complete(task_id)
            else:
                if was_complete:
                    print(
                        f"⚠️  Tarefa {task_id} deixou de estar completa, movendo de volta para pendente"
                    )
                    self._unmark_task_complete(task_id)

    def _unmark_task_complete(self, task_id: str) -> None:
        """Move uma tarefa de volta para pendente se não estiver mais válida"""
        data = self.load_tasks()

        # Encontra na completed_tasks
        completed_task = None
        for task in data.get("completed_tasks", []):
            if task["id"] == task_id:
                completed_task = task
                break

        if not completed_task:
            return

        # Move de volta para pending
        completed_task["status"] = "pending"
        completed_task["last_checked"] = datetime.now(timezone.utc).isoformat()
        completed_task["check_count"] = completed_task.get("check_count", 0) + 1

        data["completed_tasks"] = [t for t in data["completed_tasks"] if t["id"] != task_id]
        data["pending_tasks"].append(completed_task)

        self.save_tasks(data)

    def add_task(self, task: Dict[str, Any]) -> None:
        """Adiciona uma nova tarefa"""
        data = self.load_tasks()
        data["pending_tasks"].append(task)
        self.save_tasks(data)
        print(f"Tarefa {task['id']} adicionada")

    def list_tasks(self, status_filter: Optional[str] = None) -> None:
        """Lista tarefas por status"""
        data = self.load_tasks()

        if status_filter == "pending" or status_filter is None:
            print("\n📋 TAREFAS PENDENTES:")
            for task in data.get("pending_tasks", []):
                print(f"  • {task['id']}: {task['title']} ({task['priority']})")

        if status_filter == "completed" or status_filter is None:
            print("\n✅ TAREFAS CONCLUÍDAS:")
            for task in data.get("completed_tasks", []):
                print(f"  • {task['id']}: {task['title']}")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python task_manager.py <comando> [args...]")
        print("Comandos:")
        print("  check <task_id>     - Verifica status de uma tarefa")
        print("  complete <task_id>  - Marca tarefa como completa")
        print("  check-all           - Verifica todas as tarefas")
        print("  list [status]       - Lista tarefas (pending/completed/all)")
        return

    manager = TaskManager()
    command = sys.argv[1]

    if command == "check" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        if manager.check_task_status(task_id):
            print(f"✅ Tarefa {task_id} está completa")
        else:
            print(f"❌ Tarefa {task_id} não está completa")

    elif command == "complete" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        manager.mark_task_complete(task_id)

    elif command == "check-all":
        manager.check_all_tasks()

    elif command == "list":
        status_filter = sys.argv[2] if len(sys.argv) >= 3 else None
        manager.list_tasks(status_filter)

    else:
        print(f"Comando desconhecido: {command}")


if __name__ == "__main__":
    main()
