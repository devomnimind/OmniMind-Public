# src/autopoietic/sandbox.py
"""Sandboxing system for autopoietic component execution.

Provides secure execution environment for auto-generated components,
preventing system compromise and ensuring controlled testing.
"""

from __future__ import annotations

import logging
import os
import resource
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SandboxError(Exception):
    """Raised when sandbox execution fails."""

    pass


class AutopoieticSandbox:
    """Secure sandbox for executing autopoietic components.

    Provides resource limits, timeout controls, and isolated execution
    to prevent system compromise by auto-generated code.
    """

    def __init__(
        self,
        max_memory_mb: int = 100,
        max_cpu_time_seconds: int = 30,
        max_file_size_kb: int = 1024,
        temp_dir: Optional[Path] = None,
    ):
        """Initialize sandbox with security limits.

        Args:
            max_memory_mb: Maximum memory usage in MB
            max_cpu_time_seconds: Maximum CPU time in seconds
            max_file_size_kb: Maximum file size that can be created
            temp_dir: Custom temporary directory (auto-created if None)
        """
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time_seconds = max_cpu_time_seconds
        self.max_file_size_kb = max_file_size_kb
        self.temp_dir = temp_dir or Path(tempfile.mkdtemp(prefix="autopoiesis_sandbox_"))
        self._logger = logger.getChild(self.__class__.__name__)

        # Create sandbox directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self._logger.info("🛡️ Sandbox initialized at %s", self.temp_dir)

    def validate_component(self, component_code: str) -> bool:
        """Validate component code for security before execution.

        Args:
            component_code: Python code to validate

        Returns:
            True if code passes security checks
        """
        dangerous_patterns = [
            "import os",
            "import subprocess",
            "import sys",
            "os.system",
            "subprocess.call",
            "subprocess.run",
            "eval(",
            "exec(",
            "__import__(",
            "open(",
            "file(",
            "input(",
            "import shutil",
            "import socket",
        ]

        for pattern in dangerous_patterns:
            if pattern in component_code:
                self._logger.error("🚨 Dangerous pattern detected: %s", pattern)
                return False

        # Check for security signature
        if "modulo_autopoiesis_data_" not in component_code:
            self._logger.error("🚨 Missing security signature in component")
            return False

        if "_generated_in_sandbox = True" not in component_code:
            self._logger.error("🚨 Component not marked as sandbox-generated")
            return False

        self._logger.info("✅ Component passed security validation")
        return True

    def execute_component(self, component_code: str, component_name: str) -> Dict[str, Any]:
        """Execute component in sandbox environment.

        Args:
            component_code: Python code to execute
            component_name: Name of the component

        Returns:
            Dict with execution results

        Raises:
            SandboxError: If execution fails or violates security
        """
        if not self.validate_component(component_code):
            raise SandboxError("Component failed security validation")

        # Create temporary file for component
        component_file = self.temp_dir / f"{component_name}.py"
        with component_file.open("w") as f:
            f.write(component_code)

        # Create test script
        test_script = self.temp_dir / "test_execution.py"
        test_content = f"""
import sys
sys.path.insert(0, '{self.temp_dir}')

try:
    # Import and instantiate component
    from {component_name} import *

    # Get the class (assuming it's the only class in the module)
    classes = [obj for name, obj in globals().items() if isinstance(obj, type)]
    if not classes:
        print("ERROR: No class found in component")
        sys.exit(1)

    component_class = classes[0]
    instance = component_class()

    # Verify security markers
    if not hasattr(instance, '_security_signature'):
        print("ERROR: Missing security signature")
        sys.exit(1)

    if not hasattr(instance, '_generated_in_sandbox'):
        print("ERROR: Missing sandbox marker")
        sys.exit(1)

    print(f"SUCCESS: Component {{component_class.__name__}} instantiated securely")
    print(f"Security signature: {{instance._security_signature}}")
    print(f"Sandbox generated: {{instance._generated_in_sandbox}}")

except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        with test_script.open("w") as f:
            f.write(test_content)

        result = {
            "success": False,
            "output": "",
            "error": "",
            "execution_time": 0.0,
            "security_validated": True,
        }

        try:
            with self.execution_context():
                start_time = time.time()

                # Execute with timeout
                # Passar variáveis de ambiente CUDA para o subprocesso
                cuda_env = os.environ.copy()
                cuda_vars = {
                    "CUDA_LAUNCH_BLOCKING": os.environ.get("CUDA_LAUNCH_BLOCKING", "1"),
                    "PYTORCH_CUDA_ALLOC_CONF": os.environ.get(
                        "PYTORCH_CUDA_ALLOC_CONF",
                        "max_split_size_mb:32,garbage_collection_threshold:0.8",
                    ),
                    "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "1"),
                    "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS", "1"),
                    "NUMEXPR_NUM_THREADS": os.environ.get("NUMEXPR_NUM_THREADS", "1"),
                    "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS", "1"),
                    "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "0"),
                    "TORCH_USE_CUDA_DSA": os.environ.get("TORCH_USE_CUDA_DSA", "1"),
                    "PYTORCH_NO_CUDA_MEMORY_CACHING": os.environ.get(
                        "PYTORCH_NO_CUDA_MEMORY_CACHING", "1"
                    ),
                }
                cuda_env.update(cuda_vars)

                process = subprocess.Popen(
                    [sys.executable, str(test_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.temp_dir,
                    env=cuda_env,  # Passar ambiente CUDA
                )

                try:
                    stdout, stderr = process.communicate(timeout=self.max_cpu_time_seconds)
                    execution_time = time.time() - start_time

                    result.update(
                        {
                            "success": process.returncode == 0,
                            "output": stdout,
                            "error": stderr,
                            "execution_time": execution_time,
                        }
                    )

                    if process.returncode == 0:
                        self._logger.info(
                            "✅ Component executed successfully in sandbox (%.2fs)",
                            execution_time,
                        )
                    else:
                        self._logger.error("❌ Component execution failed: %s", stderr)

                except subprocess.TimeoutExpired:
                    process.kill()
                    result.update(
                        {
                            "success": False,
                            "error": f"Execution timeout after {self.max_cpu_time_seconds}s",
                            "execution_time": self.max_cpu_time_seconds,
                        }
                    )
                    self._logger.error("🚨 Component execution timed out")

        except Exception as e:
            result.update(
                {
                    "success": False,
                    "error": str(e),
                }
            )
            self._logger.error("🚨 Sandbox execution error: %s", e)

        return result

    @contextmanager
    def execution_context(self):
        """Context manager for safe component execution."""
        old_cwd = os.getcwd()
        try:
            # Change to sandbox directory
            os.chdir(self.temp_dir)

            # Set resource limits
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.max_cpu_time_seconds, self.max_cpu_time_seconds),
            )
            resource.setrlimit(
                resource.RLIMIT_AS,
                (self.max_memory_mb * 1024 * 1024, self.max_memory_mb * 1024 * 1024),
            )
            resource.setrlimit(
                resource.RLIMIT_FSIZE,
                (self.max_file_size_kb * 1024, self.max_file_size_kb * 1024),
            )

            # Set restrictive umask
            old_umask = os.umask(0o077)

            self._logger.info("🛡️ Entered sandbox execution context")
            yield

        except Exception as e:
            self._logger.error("🚨 Sandbox execution error: %s", e)
            raise SandboxError(f"Sandbox execution failed: {e}")
        finally:
            # Restore original state
            os.chdir(old_cwd)
            os.umask(old_umask)
            self._logger.info("🛡️ Exited sandbox execution context")

    def cleanup(self):
        """Clean up sandbox resources."""
        try:
            import shutil

            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self._logger.info("🧹 Sandbox cleaned up: %s", self.temp_dir)
        except Exception as e:
            self._logger.error("Failed to cleanup sandbox: %s", e)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


def create_secure_sandbox(**kwargs) -> AutopoieticSandbox:
    """Factory function for creating secure sandbox instances.

    Returns:
        Configured AutopoieticSandbox with security defaults
    """
    return AutopoieticSandbox(
        max_memory_mb=50,  # Conservative memory limit
        max_cpu_time_seconds=10,  # Short execution time
        max_file_size_kb=100,  # Small file creation limit
        **kwargs,
    )
