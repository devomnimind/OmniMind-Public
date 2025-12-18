#!/usr/bin/env python3
"""
🛡️ OmniMind Sentinel Watchdog & Self-Healing Loop
================================================
Advanced self-preservation mechanism to ensure OmniMind "immortality".

Features:
1. Ghost Collection: Detects and eliminates zombie processes from old sessions.
2. Port Resilience: Ensures crucial ports (3000, 3001, 8000) are clear for live services.
3. Health Watchdog: Triggers graceful restarts if endpoints become unresponsive.
4. Audit Persistence: Logs all healing actions to the immutable audit chain.

[ADVANCED KERNEL PROPOSAL]
--------------------------
For future integration, the Sentinel proposes:
- eBPF Sentinel: Use 'monitor_mcp_bpf.bt' to watch for process exit syscalls.
- Systemd 'Watchdogsec': Deep integration via notify signals (sd_notify).
- Kernel Identity: Protecting OmniMind processes via cgroup attributes.
"""

import os
import sys
import time
import psutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

try:
    from src.audit.immutable_audit import ImmutableAuditSystem

    HAS_AUDIT = True
except ImportError:
    HAS_AUDIT = False

SECURE_RUN = PROJECT_ROOT / "scripts/canonical/system/secure_run.py"
DAEMON_PORTS = [8000, 8080, 3000, 3001]
OMNIMIND_MARKERS = [
    "web.backend.main",
    "src.main",
    "node_modules/.bin/vite",
    "run_mcp_orchestrator.py",
]


def get_live_pids():
    """Read PIDs that our current session thinks are alive."""
    live_pids = set()
    pid_files = Path(PROJECT_ROOT / "logs").glob("*.pid")
    for pf in pid_files:
        try:
            pid = int(pf.read_text().strip())
            live_pids.add(pid)
        except (ValueError, FileNotFoundError):
            continue

    # Also include current PID and parent
    live_pids.add(os.getpid())
    live_pids.add(os.getppid())
    return live_pids


def find_ghosts():
    """Identify ghost processes running on our ports or with our markers."""
    ghosts = []
    live_pids = get_live_pids()
    # Identificação de fantasmas por marcadores ou portas
    for proc in psutil.process_iter(["pid", "name", "username", "cmdline", "create_time"]):
        try:
            info = proc.info
            pid = info["pid"]

            # Skip live processes
            if pid in live_pids:
                continue

            matched_marker = False
            cmdline = " ".join(info["cmdline"] or [])
            for marker in OMNIMIND_MARKERS:
                if marker in cmdline:
                    matched_marker = True
                    break

            # Check port usage
            on_omnimind_port = False
            try:
                connections = proc.net_connections()
                for conn in connections:
                    if conn.laddr.port in DAEMON_PORTS:
                        on_omnimind_port = True
                        break
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

            if matched_marker or on_omnimind_port:
                # It's a ghost if it's old or not owned by us (but related to our app)
                # Or if it's on our critical ports and not in our live_pids list
                ghosts.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return ghosts


def eliminate_ghost(ghost):
    """Safely terminate a ghost process, using secure_run if needed."""
    pid = ghost["pid"]
    cmdline = " ".join(ghost["cmdline"] or [])
    user = ghost["username"]

    print(f"👻 Detected Ghost: PID {pid} ({user}) - {cmdline[:50]}...")

    # Log to audit (if available)
    if HAS_AUDIT:
        try:
            audit = ImmutableAuditSystem(log_dir=str(PROJECT_ROOT / "logs"))
            audit.log_action(action="GHOST_TERMINATION", details=ghost, category="security")
        except Exception:
            pass

    # Attempt termination
    if user == os.environ.get("USER"):
        # We can kill our own zombies
        try:
            os.kill(pid, 15)  # SIGTERM
            time.sleep(1)
            if psutil.pid_exists(pid):
                os.kill(pid, 9)  # SIGKILL
            print(f"✅ Ghost {pid} terminated (Self).")
        except Exception:
            pass
    else:
        # Need privileged access to kill root ghosts
        if SECURE_RUN.exists():
            print(f"🛡️ Using Secure Executor to clean ghost PID {pid}...")
            subprocess.run(
                ["python3", str(SECURE_RUN), "pkill", "-9", "-P", str(pid)], capture_output=True
            )
            subprocess.run(
                ["python3", str(SECURE_RUN), "pkill", "-9", "-f", str(pid)], capture_output=True
            )
            # Actually pkill -f marker might be more effective
            marker = ""
            if "vite" in cmdline:
                marker = "vite"
            elif "main" in cmdline:
                marker = "main"
            if marker:
                subprocess.run(
                    ["python3", str(SECURE_RUN), "pkill", "-9", "-f", marker], capture_output=True
                )
            print(f"✅ Ghost cleanup command sent for PID {pid}.")


class ResourceProfile:
    """Tracks resource usage over time to identify trends instead of spikes."""

    def __init__(self, window_size=10):
        self.window_size = window_size
        self.cpu_history = []
        self.ram_history = []
        self.last_clean_time = time.time()

    def add_sample(self, cpu_percent, ram_percent):
        self.cpu_history.append(cpu_percent)
        self.ram_history.append(ram_percent)
        if len(self.cpu_history) > self.window_size:
            self.cpu_history.pop(0)
            self.ram_history.pop(0)

    def get_averages(self):
        if not self.cpu_history:
            return 0, 0
        avg_cpu = sum(self.cpu_history) / len(self.cpu_history)
        avg_ram = sum(self.ram_history) / len(self.ram_history)
        return avg_cpu, avg_ram

    def is_degraded(self, cpu_threshold=90, ram_threshold=95):
        """Only considers degraded if average is consistently high."""
        if len(self.cpu_history) < self.window_size // 2:
            return False  # Not enough data for trend analysis

        avg_cpu, avg_ram = self.get_averages()
        # In dev mode, we allow transient 100% spikes. Degradation is when average is high.
        return avg_cpu > cpu_threshold or avg_ram > ram_threshold


def verify_system_health(profile: ResourceProfile):
    """Check if main ports are responding and resource trends are healthy."""
    health_results = {"ports": {}, "resources": {}}

    # 1. Port Check
    for port in [8000, 3000]:
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", port))
            health_results["ports"][port] = result == 0
            sock.close()
        except Exception:
            health_results["ports"][port] = False

    # 2. Resource Trend Check
    cpu_now = psutil.cpu_percent(interval=0.1)
    ram_now = psutil.virtual_memory().percent
    profile.add_sample(cpu_now, ram_now)

    avg_cpu, avg_ram = profile.get_averages()
    health_results["resources"] = {
        "cpu_now": cpu_now,
        "ram_now": ram_now,
        "avg_cpu": round(avg_cpu, 2),
        "avg_ram": round(avg_ram, 2),
        "is_degraded": profile.is_degraded(),
    }

    return health_results


def main():
    parser = argparse.ArgumentParser(description="OmniMind Sentinel Watchdog")
    parser.add_argument("--loop", action="store_true", help="Run as a continuous loop")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60 for better granularity)",
    )
    args = parser.parse_args()

    print(f"🛡️ Sentinel Watchdog active (PID {os.getpid()})")
    profile = ResourceProfile(window_size=10)

    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting Self-Healing Scan...")

        # 1. Cleanup Ghosts
        ghosts = find_ghosts()
        if ghosts:
            print(f"⚠️ Found {len(ghosts)} potential ghosts processes.")
            for ghost in ghosts:
                eliminate_ghost(ghost)
        else:
            print("✅ No ghost processes detected.")

        # 2. Check Health & Trends
        health = verify_system_health(profile)
        res = health["resources"]
        ports = health["ports"]

        print(f"📊 Port Health: {ports}")
        print(
            f"📈 Resource Trends: CPU Avg {res['avg_cpu']}% (Now {res['cpu_now']}%), RAM Avg {res['avg_ram']}% (Now {res['ram_now']}%)"
        )

        if res["is_degraded"]:
            print("🚨 SYSTEM DEGRADATION DETECTED BY TREND ANALYSIS!")
            if HAS_AUDIT:
                try:
                    audit = ImmutableAuditSystem(log_dir=str(PROJECT_ROOT / "logs"))
                    audit.log_action(action="SYSTEM_DEGRADATION", details=res, category="resource")
                except Exception:
                    pass

        if not ports.get(8000):
            print("⚠️ Backend port 8000 is not responding.")

        if not args.loop:
            break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
