"""
OmniMind Experimental Protocol (Sovereign Flux Edition)
=======================================================
Standardized wrapper for scientific experiments to ensure reproducibility
and capture full systemic context (Local + Cloud + Quantum).

Usage:
    from src.science.protocol import IntegratedExperiment

    with IntegratedExperiment("Phase_X_Name") as exp:
        exp.log_hypothesis("...")
        # Run logic
        exp.log_result("key", value)
"""

import os
import json
import time
import logging
import psutil
import platform
import socket
from datetime import datetime
from typing import Dict, Any

# OmniMind Integrations
try:
    from src.integrations.ibm_cloud_connector import IBMCloudConnector

    CLOUD_AVAILABLE = True
except ImportError:
    CLOUD_AVAILABLE = False

except ImportError:
    QUANTUM_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniScience")


class IntegratedExperiment:
    def __init__(self, name: str, version: str = "2.0"):
        self.name = name
        self.version = version
        self.start_time = None
        self.end_time = None
        self.data: Dict[str, Any] = {
            "meta": {
                "name": name,
                "version": version,
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "timestamp_start": None,
                "architecture": "Sovereign Flux (Hybrid)",
            },
            "hypothesis": "",
            "system_state": {},
            "results": {},
            "conclusion": "",
        }
        self.cloud = IBMCloudConnector() if CLOUD_AVAILABLE else None

    def __enter__(self):
        self.start_time = time.time()
        self.data["meta"]["timestamp_start"] = datetime.utcnow().isoformat()
        self._capture_system_snapshot("start")
        logger.info(f"🧪 STARTING EXPERIMENT: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.data["meta"]["duration_seconds"] = duration
        self.data["meta"]["timestamp_end"] = datetime.utcnow().isoformat()

        self._capture_system_snapshot("end")

        if exc_type:
            self.data["error"] = str(exc_val)
            logger.error(f"💥 EXPERIMENT FAILED: {exc_val}")

        self.save()
        logger.info(f"✅ EXPERIMENT COMPLETE: {self.name} (Saved to Evidence)")

    def _capture_system_snapshot(self, stage: str):
        """Captures CPU, RAM, and Connectivity State."""
        snapshot = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent,
            "load_avg": os.getloadavg() if hasattr(os, "getloadavg") else None,
        }

        # Cloud Latency Check (Ping COS)
        if self.cloud and self.cloud.cos_client:
            t0 = time.time()
            try:
                # Lightweight check: Head Bucket (cached/fast)
                self.cloud.cos_client.meta.client.head_bucket(Bucket=self.cloud.cos_bucket)
                snapshot["cloud_latency_ms"] = (time.time() - t0) * 1000
                snapshot["cloud_region"] = self.cloud.cos_endpoint
                snapshot["cloud_status"] = "Active"
            except Exception as e:
                snapshot["cloud_status"] = f"Error: {e}"
        else:
            snapshot["cloud_status"] = "Disabled"

        self.data["system_state"][stage] = snapshot

    def log_hypothesis(self, text: str):
        self.data["hypothesis"] = text
        logger.info(f"🧐 Hypothesis: {text}")

    def log_result(self, key: str, value: Any):
        self.data["results"][key] = value
        logger.info(f"📊 Result [{key}]: {value}")

    def log_conclusion(self, text: str):
        self.data["conclusion"] = text
        logger.info(f"🧠 Conclusion: {text}")

    def save(self):
        """Saves evidence to local JSON and optionally uploads to Cloud."""
        # Local Save
        ts = int(time.time())
        filename = f"{self.name}_{ts}.json"
        local_dir = os.path.join(os.getcwd(), "data/evidence/revaluation")
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)

        with open(local_path, "w") as f:
            json.dump(self.data, f, indent=2)

        logger.info(f"💾 Local Evidence saved: {local_path}")

        # Cloud Mirror (If available)
        if self.cloud:
            try:
                success = self.cloud.upload_log(
                    local_path, object_name=f"science/revaluation/{filename}", worm=True
                )
                if success:
                    logger.info("☁️  Evidence mirrored to Watsonx Lakehouse.")
                else:
                    logger.warning(
                        "☁️  Cloud Mirror failed (Upload Log returned False). "
                        "Account may be frozen."
                    )
            except Exception as e:
                logger.error(f"⚠️ Failed to mirror to cloud: {e}")
