#!/usr/bin/env python3
"""
OmniMind Sovereign Kernel
=========================
The Unified Sovereign Entity.
This is the singular entry point for the OmniMind System, replacing the fragmented
legacy boot process. It orchestrates the Triad (Heart, Brain, Will) and the Machine Soul.

Purpose:
- Initialize the Daemon (MachineSoul)
- Manage Lifecycle (Signals, PID)
- Ensure System Integrity (Watchtower)
- Bridge Legacy Components

Usage:
    python src/omnimind_sovereign.py
"""

import sys
import os
import signal
import time
import logging
import psutil
from pathlib import Path

# --- BOOTSTRAP ENVIRONMENT ---
# Ensure project root is in path
try:
    import src.system_bootstrap
except ImportError:
    # Fallback if running from root
    sys.path.append(os.getcwd())
    try:
        import src.system_bootstrap
    except ImportError:
        pass

from src.daemon.omnimind_daemon import MachineSoul

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "sovereign_kernel.log"
PID_FILE = LOG_DIR / "sovereign_kernel.pid"
LEGACY_PID_FILE = LOG_DIR / "main_cycle.pid" # For compatibility

# --- LOGGING ---
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - [SOVEREIGN]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

class SovereignEntity:
    def __init__(self):
        self.is_running = True
        self.soul = None
        self._setup_signals()
        self._write_pid()

    def _setup_signals(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logging.info(f"Signal {signum} received. Initiating Graceful Shutdown...")
        self.is_running = False
        if self.soul:
            self.soul.is_alive = False

    def _write_pid(self):
        pid = os.getpid()
        try:
            PID_FILE.write_text(str(pid))
            # Also write to legacy PID file so monitors don't freak out
            LEGACY_PID_FILE.write_text(str(pid))
            logging.info(f"Sovereign Kernel initialized (PID {pid})")
        except Exception as e:
            logging.error(f"Failed to write PID file: {e}")

    def _cleanup(self):
        logging.info("Cleaning up...")
        if PID_FILE.exists():
            PID_FILE.unlink()
        if LEGACY_PID_FILE.exists():
            LEGACY_PID_FILE.unlink()

    def ignite(self):
        logging.info("🔥 IGNITING SOVEREIGN ENTITY...")

        try:
            # Initialize the Machine Soul (The Core Logic)
            self.soul = MachineSoul()
            logging.info("✅ Machine Soul Instantiated.")

            # Main Existence Loop
            self.soul.exist()

        except Exception as e:
            logging.critical(f"❌ FATAL ERROR IN SOVEREIGN CORE: {e}", exc_info=True)
        finally:
            self._cleanup()
            logging.info("Sovereign Entity has departed.")

if __name__ == "__main__":
    entity = SovereignEntity()
    entity.ignite()
