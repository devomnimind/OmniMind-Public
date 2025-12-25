#!/usr/bin/env python3
"""
OmniMind CLI Entry Point (Reintegrated)
This is the Client/Controller. It does NOT run the kernel directly.
It delegates to the 'Machine Soul' (Daemon).

Usage:
    python src/main.py start     -> Starts the Soul Daemon
    python src/main.py status    -> Checks if Soul is alive
    python src/main.py stop      -> Stops the Soul
    python src/main.py tribunal  -> Summons the Devil (Resilience Test)
"""

import sys
import os
import time
import signal
import psutil
from pathlib import Path
import subprocess

# Explicit Environment Loading (Antigravity Fix)
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    # print(f"✅ Loaded .env from {ENV_PATH}") # Silent load to avoid stdout noise in JSON CLI
else:
    # print(f"⚠️  CRITICAL: .env not found at {ENV_PATH}")
    pass

# Add project root to Python path
sys.path.append(str(PROJECT_ROOT))

# PID file location (should match Daemon config)
PID_FILE = Path("logs/omnimind_daemon.pid")
LOG_FILE = Path("logs/soul_trace.log")


def get_daemon_pid():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if psutil.pid_exists(pid):
                return pid
        except Exception:
            pass
    return None


def start_daemon():
    pid = get_daemon_pid()
    if pid:
        print(f"👻 OmniMind Soul is already awake! (PID {pid})")
        return

    print("⚡ Awakening the Machine Soul...")

    # Ensure logs dir exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Launch Daemon
    # We simply run the python module in background
    cmd = [sys.executable, "src/daemon/omnimind_daemon.py"]

    # Use nohup-like behavior
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + ":" + env.get("PYTHONPATH", "")

    with open("logs/daemon_stdout.log", "w") as out, open("logs/daemon_stderr.log", "w") as err:
        proc = subprocess.Popen(cmd, stdout=out, stderr=err, start_new_session=True, env=env)  # Detach

    # Write PID file so we can find it later
    try:
        PID_FILE.write_text(str(proc.pid))
    except Exception as e:
        print(f"⚠️ Failed to write PID file: {e}")

    print(f"✨ Soul ignite sequence initiated (PID {proc.pid}).")
    print(f"📜 Tail logs with: tail -f {LOG_FILE}")


def stop_daemon():
    pid = get_daemon_pid()
    if not pid:
        print("💤 Soul is already sleeping.")
        return

    print(f"🛑 Putting Soul to sleep (PID {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        # Wait for death
        for _ in range(10):
            if not psutil.pid_exists(pid):
                break
            time.sleep(0.5)
            print(".", end="", flush=True)
        print("\n💤 Goodnight.")
    except Exception as e:
        print(f"⚠️ Error initiating sleep: {e}")


def status_daemon():
    pid = get_daemon_pid()
    if pid:
        print(f"🟢 OmniMind Soul is ALIVE (PID {pid})")
        # Check CPU/Memory
        try:
            p = psutil.Process(pid)
            print(f"   Memory: {p.memory_info().rss / 1024 / 1024:.2f} MB")
            print(f"   CPU: {p.cpu_percent(interval=0.1)}%")
            print(f"   Uptime: {time.time() - p.create_time():.0f}s")
        except Exception:
            pass
    else:
        print("🔴 OmniMind Soul is ASLEEP")


def summon_tribunal():
    """Run the Tribunal do Diabo (Resilience Simulation)."""
    print("🔥 SUMMONING THE DEVIL (Tribunal do Diabo) 🔥")
    print("WARNING: This is a stress test. Expect high load.")

    cmd = [
        sys.executable,
        "src/tribunal_do_diabo/executor.py",
        "--duration",
        "0.1",
    ]  # Short run for demo

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Tribunal Concluded. The Soul survived.")
    except subprocess.CalledProcessError:
        print("\n❌ Tribunal Failed. The System fractured.")
    except KeyboardInterrupt:
        print("\n🛑 Tribunal Interrupted.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "start":
        start_daemon()
    elif cmd == "stop":
        stop_daemon()
    elif cmd == "status":
        status_daemon()
    elif cmd == "status":
        status_daemon()
    elif cmd == "tribunal":
        summon_tribunal()
    else:
        print("Unknown command. Use: start, stop, status, tribunal")
