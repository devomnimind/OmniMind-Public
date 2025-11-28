import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List
import psutil

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
Agent Tools for OmniMind
Provides safe file operations, shell execution, and system monitoring.
"""


class FileOperations:
    """Safe file operations with path validation."""

    def __init__(self, allowed_dirs: List[str]):
        self.allowed_dirs = [os.path.expanduser(d) for d in allowed_dirs]

    def _validate_path(self, path: str) -> Path:
        """Ensure path is within allowed directories."""
        full_path = Path(os.path.expanduser(path)).resolve()

        for allowed in self.allowed_dirs:
            if str(full_path).startswith(str(Path(allowed).resolve())):
                return full_path

        raise PermissionError(f"Access denied: {path} not in allowed directories")

    def read_file(self, path: str) -> str:
        """Read file contents."""
        file_path = self._validate_path(path)

        if not file_path.exists():
            return f"Error: File not found: {path}"

        if not file_path.is_file():
            return f"Error: Not a file: {path}"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        file_path = self._validate_path(path)

        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return f"Successfully wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def list_files(self, path: str = ".") -> str:
        """List files in directory."""
        dir_path = self._validate_path(path)

        if not dir_path.exists():
            return f"Error: Directory not found: {path}"

        if not dir_path.is_dir():
            return f"Error: Not a directory: {path}"

        try:
            items = []
            for item in sorted(dir_path.iterdir()):
                item_type = "DIR" if item.is_dir() else "FILE"
                size = item.stat().st_size if item.is_file() else 0
                items.append(f"{item_type:5} {size:>10} {item.name}")

            return "\n".join(items) if items else "Empty directory"
        except Exception as e:
            return f"Error listing directory: {str(e)}"


class ShellExecutor:
    """Execute shell commands with whitelist and timeout."""

    def __init__(self, whitelist: List[str], timeout: int = 10):
        self.whitelist = whitelist
        self.timeout = timeout

    def execute(self, command: str) -> str:
        """Execute whitelisted command."""
        cmd_parts = command.strip().split()

        if not cmd_parts:
            return "Error: Empty command"

        base_cmd = cmd_parts[0]

        # Check whitelist
        if base_cmd not in self.whitelist:
            return f"Error: Command '{base_cmd}' not in whitelist: {self.whitelist}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"

            return output if output else "Command executed (no output)"

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout}s"
        except Exception as e:
            return f"Error executing command: {str(e)}"


class SystemMonitor:
    """Monitor system resources."""

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory
            mem = psutil.virtual_memory()
            mem_total_gb = mem.total / (1024**3)
            mem_used_gb = mem.used / (1024**3)
            mem_percent = mem.percent

            # GPU (if available)
            gpu_info = {}
            try:
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.used,memory.total,temperature.gpu,utilization.gpu",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    gpu_data = result.stdout.strip().split(",")
                    gpu_info = {
                        "name": gpu_data[0].strip(),
                        "memory_used_mb": int(gpu_data[1].strip()),
                        "memory_total_mb": int(gpu_data[2].strip()),
                        "temperature_c": int(gpu_data[3].strip()),
                        "utilization_percent": int(gpu_data[4].strip()),
                    }
            except Exception:
                gpu_info = {"available": False}

            return {
                "cpu": {"percent": cpu_percent, "count": cpu_count},
                "memory": {
                    "total_gb": round(mem_total_gb, 2),
                    "used_gb": round(mem_used_gb, 2),
                    "percent": mem_percent,
                },
                "gpu": gpu_info,
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def format_info(info: Dict[str, Any]) -> str:
        """Format system info as string."""
        lines = []

        if "error" in info:
            return f"Error: {info['error']}"

        lines.append("=== SYSTEM STATUS ===")

        # CPU
        cpu = info.get("cpu", {})
        lines.append(f"CPU: {cpu.get('percent', 0):.1f}% ({cpu.get('count', 0)} cores)")

        # Memory
        mem = info.get("memory", {})
        ram_used = mem.get("used_gb", 0)
        ram_total = mem.get("total_gb", 0)
        ram_percent = mem.get("percent", 0)
        ram_line = f"RAM: {ram_used:.1f}/{ram_total:.1f} GB " f"({ram_percent:.1f}%)"
        lines.append(ram_line)

        # GPU
        gpu = info.get("gpu", {})
        if gpu.get("available") is not False and "name" in gpu:
            lines.append(f"GPU: {gpu['name']}")
            lines.append(f"  VRAM: {gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB")
            lines.append(f"  Temp: {gpu['temperature_c']}°C")
            lines.append(f"  Util: {gpu['utilization_percent']}%")
        else:
            lines.append("GPU: Not available")

        return "\n".join(lines)
