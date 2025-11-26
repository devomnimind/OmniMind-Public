import asyncio
import gzip
import json
import os
import shutil
from datetime import datetime, timedelta
from typing import Any, Dict

import psutil

# Configuration
LOG_DIR = "data/long_term_logs"
METRICS_FILE = os.path.join(LOG_DIR, "omnimind_metrics.jsonl")
HEARTBEAT_FILE = os.path.join(LOG_DIR, "heartbeat.status")
ROTATION_AGE_HOURS = 24

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)


class ObserverService:
    def __init__(self):
        self.running = True
        self.last_rotation = datetime.now()

    def log_metric(self, metric_type: str, data: Dict[str, Any]):
        """Append a metric entry to the JSONL file."""
        entry = {"timestamp": datetime.now().isoformat(), "type": metric_type, "data": data}
        with open(METRICS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def update_heartbeat(self):
        """Update the heartbeat file with current status."""
        status = {
            "last_beat": datetime.now().isoformat(),
            "status": "ALIVE",
            "pid": os.getpid(),
            "system_cpu": psutil.cpu_percent(),
            "system_ram": psutil.virtual_memory().percent,
        }
        with open(HEARTBEAT_FILE, "w") as f:
            json.dump(status, f)

    def rotate_logs(self):
        """Compress logs older than ROTATION_AGE_HOURS."""
        now = datetime.now()
        if (now - self.last_rotation) < timedelta(hours=1):
            return  # Check at most once per hour

        print(f"[{now.isoformat()}] Checking for log rotation...")

        # In a real scenario, we would rotate the main file.
        # Here we simulate by checking if the file is too large or old.
        # For simplicity, we'll just compress the current file if it exists and start new.
        # Ideally, we'd rename metrics.jsonl -> metrics_DATE.jsonl then compress.

        if os.path.exists(METRICS_FILE):
            # Check file creation time or size
            # For this MVP, let's rotate daily based on self.last_rotation logic
            # But since we just started, let's implement a 'force rotate' if file > 100MB

            file_size_mb = os.path.getsize(METRICS_FILE) / (1024 * 1024)
            if file_size_mb > 100 or (now - self.last_rotation) > timedelta(
                hours=ROTATION_AGE_HOURS
            ):
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                archive_name = os.path.join(LOG_DIR, f"metrics_{timestamp}.jsonl.gz")

                with open(METRICS_FILE, "rb") as f_in:
                    with gzip.open(archive_name, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Clear the original file
                open(METRICS_FILE, "w").close()
                print(f"Rotated logs to {archive_name}")
                self.last_rotation = now

    async def run(self):
        print("OmniMind Observer Service Started.")
        print(f"Logging to {LOG_DIR}")

        while self.running:
            try:
                # 1. Heartbeat
                self.update_heartbeat()

                # 2. Collect System Metrics (The Body)
                sys_metrics = {
                    "cpu": psutil.cpu_percent(),
                    "memory": psutil.virtual_memory().percent,
                    "disk": psutil.disk_usage("/").percent,
                }
                self.log_metric("SYSTEM_HEALTH", sys_metrics)

                # 3. Log Rotation Check
                self.rotate_logs()

                # 4. Wait
                await asyncio.sleep(60)  # 1 minute interval

            except Exception as e:
                print(f"Observer Error: {e}")
                self.log_metric("ERROR", {"message": str(e)})
                await asyncio.sleep(60)


if __name__ == "__main__":
    service = ObserverService()
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        print("Observer Service Stopped.")
