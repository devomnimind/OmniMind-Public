"""
Ollama On-Demand Process Manager.

Spawns Ollama subprocess when needed, kills when done.
Ensures Ollama is a child process of OmniMind, not a 24/7 systemd service.

Resource Management:
- GPU: Forced CPU-only via CUDA_VISIBLE_DEVICES=""
- CPU: Lower priority via nice -n 10
- Lifecycle: Automatic cleanup on parent exit via atexit

Author: OmniMind Team
Date: 2025-12-21
"""

import atexit
import logging
import os
import subprocess
import time
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaProcessManager:
    """
    On-demand Ollama process manager.

    Spawns Ollama as subprocess of OmniMind, NOT as systemd service.
    Automatically kills Ollama when OmniMind exits or after idle timeout.

    Usage:
        manager = OllamaProcessManager.get_instance()
        if manager.ensure_running():
            # Use Ollama API
            ...
        manager.check_idle_timeout()  # Call periodically
    """

    _instance: Optional["OllamaProcessManager"] = None
    _lock = Lock()

    def __init__(self) -> None:
        """Initialize the process manager (use get_instance instead)."""
        self.process: Optional[subprocess.Popen] = None
        self.port = int(os.getenv("OLLAMA_PORT", "11434"))
        self.host = os.getenv("OLLAMA_HOST", "127.0.0.1")
        self.idle_timeout = int(os.getenv("OLLAMA_IDLE_TIMEOUT", "300"))  # 5 min
        self.startup_timeout = int(os.getenv("OLLAMA_STARTUP_TIMEOUT", "30"))
        self.last_activity = 0.0
        self._spawn_lock = Lock()

        # Register cleanup on exit
        atexit.register(self._cleanup)
        logger.info(
            "🦙 [Ollama] ProcessManager initialized (port=%d, idle_timeout=%ds)",
            self.port,
            self.idle_timeout,
        )

    @classmethod
    def get_instance(cls) -> "OllamaProcessManager":
        """Get singleton instance of OllamaProcessManager."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def ensure_running(self) -> bool:
        """
        Ensure Ollama is running, spawn if needed.

        Returns:
            True if Ollama is running and healthy, False otherwise.
        """
        if self._is_healthy():
            self.last_activity = time.time()
            return True

        return self._spawn()

    def _spawn(self) -> bool:
        """
        Spawn Ollama subprocess with resource limits.

        Uses:
        - nice -n 10: Lower CPU priority
        - CUDA_VISIBLE_DEVICES="": Force CPU-only mode
        - start_new_session=True: Process group for clean kill

        Returns:
            True if spawned and healthy, False otherwise.
        """
        with self._spawn_lock:
            # Double-check after acquiring lock
            if self.process is not None and self.process.poll() is None:
                if self._is_healthy():
                    return True

            logger.info("🚀 [Ollama] Spawning subprocess...")

            # Environment: Force CPU-only
            env = os.environ.copy()
            env["CUDA_VISIBLE_DEVICES"] = ""
            env["OLLAMA_HOST"] = f"{self.host}:{self.port}"

            # Command with nice for lower CPU priority
            cmd = ["nice", "-n", "10", "/usr/local/bin/ollama", "serve"]

            try:
                self.process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )

                # Wait for startup with timeout
                for i in range(self.startup_timeout):
                    if self._is_healthy():
                        logger.info(
                            "✅ [Ollama] Ready (PID %d) after %ds",
                            self.process.pid,
                            i + 1,
                        )
                        self.last_activity = time.time()
                        return True
                    time.sleep(1)

                # Startup failed
                logger.error(
                    "❌ [Ollama] Failed to start within %ds",
                    self.startup_timeout,
                )
                self._kill()
                return False

            except FileNotFoundError:
                logger.error("❌ [Ollama] Binary not found: /usr/local/bin/ollama")
                return False
            except Exception as e:
                logger.error("❌ [Ollama] Spawn error: %s", e)
                return False

    def _is_healthy(self) -> bool:
        """
        Check if Ollama HTTP API is responding.

        Returns:
            True if Ollama responds to /api/tags, False otherwise.
        """
        try:
            import urllib.request

            req = urllib.request.Request(
                f"http://{self.host}:{self.port}/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _kill(self) -> None:
        """Terminate Ollama subprocess gracefully, then forcefully if needed."""
        if self.process is None:
            return

        pid = self.process.pid
        logger.info("🛑 [Ollama] Terminating (PID %d)...", pid)

        try:
            self.process.terminate()
            self.process.wait(timeout=5)
            logger.info("✅ [Ollama] Terminated gracefully")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ [Ollama] Force killing...")
            self.process.kill()
            self.process.wait(timeout=2)
            logger.info("✅ [Ollama] Killed")
        except Exception as e:
            logger.error("❌ [Ollama] Kill error: %s", e)
        finally:
            self.process = None

    def _cleanup(self) -> None:
        """
        Cleanup on process exit (atexit handler).
        Ensures Ollama dies when OmniMind dies.
        """
        if self.process is not None:
            logger.info("🧹 [Ollama] Cleanup on exit...")
            self._kill()

    def check_idle_timeout(self) -> None:
        """
        Kill Ollama if idle for too long.
        Call this periodically (e.g., every minute) from daemon loop.
        """
        if self.process is None:
            return

        if self.process.poll() is not None:
            # Process died unexpectedly
            logger.warning("⚠️ [Ollama] Process died unexpectedly")
            self.process = None
            return

        idle_time = time.time() - self.last_activity
        if idle_time > self.idle_timeout:
            logger.info(
                "💤 [Ollama] Idle for %.0fs (timeout=%ds), killing...",
                idle_time,
                self.idle_timeout,
            )
            self._kill()

    def get_status(self) -> dict:
        """
        Get current status of Ollama process.

        Returns:
            Dict with running, pid, idle_seconds, healthy keys.
        """
        running = self.process is not None and self.process.poll() is None
        return {
            "running": running,
            "pid": self.process.pid if running else None,
            "idle_seconds": time.time() - self.last_activity if running else None,
            "healthy": self._is_healthy() if running else False,
            "port": self.port,
            "cpu_only": True,  # Always CPU-only
        }


# Convenience function for quick access
def get_ollama_manager() -> OllamaProcessManager:
    """Get the singleton OllamaProcessManager instance."""
    return OllamaProcessManager.get_instance()
