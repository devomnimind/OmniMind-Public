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
OmniMind System Diagnostic Tool

Automated system health checks and diagnostics for OmniMind.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class DiagnosticTool:
    """Automated diagnostic tool for OmniMind system."""

    def __init__(self) -> None:
        """Initialize diagnostic tool."""
        self.results: Dict[str, Any] = {
            "system": {},
            "dependencies": {},
            "services": {},
            "configuration": {},
            "performance": {},
            "issues": [],
            "recommendations": [],
        }
        self.omnimind_root = Path(__file__).parent.parent

    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete system diagnostic."""
        print("🔍 Running full OmniMind system diagnostic...\n")

        self.check_system()
        self.check_dependencies()
        self.check_configuration()
        self.check_services()
        self.check_permissions()
        self.check_gpu()
        self.check_performance()

        return self.results

    def run_quick_diagnostic(self) -> Dict[str, Any]:
        """Run quick health check."""
        print("⚡ Running quick health check...\n")

        self.check_system()
        self.check_dependencies()
        self.check_services()

        return self.results

    def check_system(self) -> None:
        """Check system information."""
        print("📋 Checking system information...")

        self.results["system"] = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
        }

        # Check Python version
        version = tuple(map(int, platform.python_version().split(".")))
        if version < (3, 11):
            self.results["issues"].append(
                f"Python version {platform.python_version()} is too old. "
                "Recommended: Python 3.12.8"
            )
            self.results["recommendations"].append("Upgrade Python to 3.12.8 using pyenv")
        elif version >= (3, 13):
            self.results["issues"].append(
                f"Python version {platform.python_version()} may have "
                "compatibility issues. Recommended: Python 3.12.8"
            )
            self.results["recommendations"].append(
                "Downgrade Python to 3.12.8 for best compatibility"
            )

        print(f"  ✓ OS: {self.results['system']['os']}")
        print(f"  ✓ Python: {self.results['system']['python_version']}")

    def check_dependencies(self) -> None:
        """Check required dependencies."""
        print("\n📦 Checking dependencies...")

        required_packages = [
            "fastapi",
            "uvicorn",
            "pytest",
            "langchain",
            "qdrant-client",
            "pydantic",
            "psutil",
        ]

        installed = {}
        missing = []

        for package in required_packages:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", package],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    version = None
                    for line in result.stdout.split("\n"):
                        if line.startswith("Version:"):
                            version = line.split(":")[1].strip()
                            break
                    installed[package] = version
                    print(f"  ✓ {package}: {version}")
                else:
                    missing.append(package)
                    print(f"  ✗ {package}: NOT INSTALLED")
            except Exception as e:
                print(f"  ⚠ Error checking {package}: {e}")

        self.results["dependencies"]["installed"] = installed
        self.results["dependencies"]["missing"] = missing

        if missing:
            self.results["issues"].append(f"Missing packages: {', '.join(missing)}")
            self.results["recommendations"].append("Run: pip install -r requirements.txt")

    def check_configuration(self) -> None:
        """Check configuration files."""
        print("\n⚙️  Checking configuration...")

        required_configs = [
            "config/agent_config.yaml",
            "config/omnimind.yaml",
            ".env.template",
        ]

        for config_path in required_configs:
            full_path = self.omnimind_root / config_path
            if full_path.exists():
                print(f"  ✓ {config_path}")
                self.results["configuration"][config_path] = "present"
            else:
                print(f"  ✗ {config_path}: MISSING")
                self.results["configuration"][config_path] = "missing"
                self.results["issues"].append(f"Missing config file: {config_path}")

        # Check auth file
        auth_file = self.omnimind_root / "config" / "dashboard_auth.json"
        if auth_file.exists():
            print(f"  ✓ dashboard_auth.json")
            self.results["configuration"]["auth"] = "configured"
        else:
            print(f"  ⚠ dashboard_auth.json: Will be auto-generated")
            self.results["configuration"]["auth"] = "auto-generate"

    def check_services(self) -> None:
        """Check service availability."""
        print("\n🔌 Checking services...")

        # Check if backend server is running
        try:
            import requests

            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("  ✓ Backend server: RUNNING")
                self.results["services"]["backend"] = "running"
            else:
                print(f"  ⚠ Backend server: HTTP {response.status_code}")
                self.results["services"]["backend"] = "error"
        except Exception:
            print("  ✗ Backend server: NOT RUNNING")
            self.results["services"]["backend"] = "stopped"
            self.results["recommendations"].append(
                "Start backend: source scripts/start_dashboard.sh"
            )

        # Check Qdrant
        try:
            import requests

            response = requests.get("http://localhost:6333/health", timeout=2)
            if response.status_code == 200:
                print("  ✓ Qdrant: RUNNING")
                self.results["services"]["qdrant"] = "running"
            else:
                print(f"  ⚠ Qdrant: HTTP {response.status_code}")
                self.results["services"]["qdrant"] = "error"
        except Exception:
            print("  ✗ Qdrant: NOT RUNNING")
            self.results["services"]["qdrant"] = "stopped"
            self.results["recommendations"].append("Start Qdrant: docker-compose up -d qdrant")

    def check_permissions(self) -> None:
        """Check file permissions."""
        print("\n🔐 Checking permissions...")

        # Check logs directory
        logs_dir = self.omnimind_root / "logs"
        if logs_dir.exists():
            if os.access(logs_dir, os.W_OK):
                print("  ✓ logs/ directory: WRITABLE")
                self.results["permissions"]["logs"] = "ok"
            else:
                print("  ✗ logs/ directory: NOT WRITABLE")
                self.results["permissions"]["logs"] = "error"
                self.results["issues"].append("logs/ directory not writable")
                self.results["recommendations"].append("Fix: chmod -R u+w logs/")
        else:
            logs_dir.mkdir(parents=True, exist_ok=True)
            print("  ✓ logs/ directory: CREATED")

        # Check data directory
        data_dir = self.omnimind_root / "data"
        if data_dir.exists():
            if os.access(data_dir, os.W_OK):
                print("  ✓ data/ directory: WRITABLE")
                self.results["permissions"]["data"] = "ok"
            else:
                print("  ✗ data/ directory: NOT WRITABLE")
                self.results["permissions"]["data"] = "error"
                self.results["issues"].append("data/ directory not writable")
        else:
            data_dir.mkdir(parents=True, exist_ok=True)
            print("  ✓ data/ directory: CREATED")

    def check_gpu(self) -> None:
        """Check GPU/CUDA availability."""
        print("\n🎮 Checking GPU/CUDA...")

        try:
            import torch

            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
                cuda_version = torch.version.cuda
                print(f"  ✓ CUDA: AVAILABLE")
                print(f"  ✓ GPU: {gpu_name}")
                print(f"  ✓ CUDA Version: {cuda_version}")
                self.results["performance"]["cuda"] = {
                    "available": True,
                    "device": gpu_name,
                    "version": cuda_version,
                }
            else:
                print("  ⚠ CUDA: NOT AVAILABLE (CPU-only mode)")
                self.results["performance"]["cuda"] = {"available": False}
                self.results["recommendations"].append(
                    "For GPU acceleration, ensure NVIDIA drivers and CUDA are installed"
                )
        except ImportError:
            print("  ⚠ PyTorch not installed")
            self.results["performance"]["cuda"] = {"available": False}
        except Exception as e:
            print(f"  ⚠ Error checking GPU: {e}")
            self.results["performance"]["cuda"] = {"available": False, "error": str(e)}

    def check_performance(self) -> None:
        """Check system performance metrics."""
        print("\n⚡ Checking performance...")

        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            print(f"  ✓ CPU Usage: {cpu_percent:.1f}%")
            print(
                f"  ✓ Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)"
            )
            print(
                f"  ✓ Disk Usage: {disk.percent:.1f}% ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)"
            )

            self.results["performance"]["cpu_percent"] = cpu_percent
            self.results["performance"]["memory_percent"] = memory.percent
            self.results["performance"]["disk_percent"] = disk.percent

            # Warnings
            if cpu_percent > 80:
                self.results["issues"].append("High CPU usage detected")
                self.results["recommendations"].append(
                    "Consider reducing concurrent tasks or upgrading hardware"
                )

            if memory.percent > 80:
                self.results["issues"].append("High memory usage detected")
                self.results["recommendations"].append(
                    "Consider increasing RAM or reducing batch sizes"
                )

            if disk.percent > 80:
                self.results["issues"].append("Low disk space")
                self.results["recommendations"].append(
                    "Clear old logs and cache: rm -rf logs/*.log.* ~/.cache/huggingface"
                )

        except ImportError:
            print("  ⚠ psutil not installed (performance check skipped)")

    def generate_report(self, output_file: str = "diagnostic_report.json") -> None:
        """Generate diagnostic report."""
        logs_dir = self.omnimind_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        output_path = logs_dir / output_file

        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Diagnostic report saved: {output_path}")

    def print_summary(self) -> None:
        """Print diagnostic summary."""
        print("\n" + "=" * 60)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 60)

        # Issues
        if self.results["issues"]:
            print("\n⚠️  ISSUES FOUND:")
            for issue in self.results["issues"]:
                print(f"  • {issue}")
        else:
            print("\n✅ No issues found!")

        # Recommendations
        if self.results["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"  • {rec}")

        print("\n" + "=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OmniMind System Diagnostic Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--full", action="store_true", help="Run full diagnostic (default)")
    parser.add_argument("--quick", action="store_true", help="Run quick health check")
    parser.add_argument("--check-system", action="store_true", help="Check system information only")
    parser.add_argument("--check-dependencies", action="store_true", help="Check dependencies only")
    parser.add_argument("--check-config", action="store_true", help="Check configuration only")
    parser.add_argument("--check-services", action="store_true", help="Check services only")
    parser.add_argument("--check-permissions", action="store_true", help="Check permissions only")
    parser.add_argument("--check-gpu", action="store_true", help="Check GPU/CUDA only")
    parser.add_argument("--check-performance", action="store_true", help="Check performance only")
    parser.add_argument(
        "--output", type=str, default="diagnostic_report.json", help="Output file name"
    )
    parser.add_argument(
        "--system-info",
        action="store_true",
        help="Print system info for bug reports",
    )

    args = parser.parse_args()

    diagnostic = DiagnosticTool()

    # Run specific checks if requested
    if args.check_system:
        diagnostic.check_system()
    elif args.check_dependencies:
        diagnostic.check_dependencies()
    elif args.check_config:
        diagnostic.check_configuration()
    elif args.check_services:
        diagnostic.check_services()
    elif args.check_permissions:
        diagnostic.check_permissions()
    elif args.check_gpu:
        diagnostic.check_gpu()
    elif args.check_performance:
        diagnostic.check_performance()
    elif args.quick:
        diagnostic.run_quick_diagnostic()
    elif args.system_info:
        diagnostic.check_system()
        print(json.dumps(diagnostic.results["system"], indent=2))
        return
    else:
        # Default: run full diagnostic
        diagnostic.run_full_diagnostic()

    # Print summary
    diagnostic.print_summary()

    # Generate report
    diagnostic.generate_report(args.output)


if __name__ == "__main__":
    main()
