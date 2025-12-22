"""
OMNIMIND INFRASTRUCTURE SYNC (PHASE 78)
=======================================
Synchronizes the Local Brain with the Cloud Body.
1. Uploads all local experiment logs to IBM COS.
2. (Optional) Pushes semantic memory to Milvus.

Usage: python scripts/ops/sync_infrastructure.py
"""

import sys
import os
import glob
import logging

# Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.integrations.ibm_cloud_connector import IBMCloudConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniMindSync")


def sync_experiments():
    connector = IBMCloudConnector()

    if not connector.cos_client:
        logger.error("❌ Cloud Storage not connected. Aborting sync.")
        return

    logger.info("🚀 Starting Infrastructure Sync...")

    # 1. Sync Experiments
    data_dir = os.path.join(PROJECT_ROOT, "data/experiments")
    files = glob.glob(os.path.join(data_dir, "*.json"))

    logger.info(f"found {len(files)} experiment logs to sync.")

    success_count = 0
    for f in files:
        filename = os.path.basename(f)
        logger.info(f"   Uploading {filename}...")
        if connector.upload_log(f):
            success_count += 1

    logger.info(f"✅ Synced {success_count}/{len(files)} files to IBM COS.")

    # 2. Check Milvus
    if connector.milvus_connected:
        logger.info(
            "✅ Milvus is active. Semantic Memory sync ready (Not implemented in this script yet)."
        )
    else:
        logger.warning("⚠️ Milvus absent. Skipping vector sync.")


if __name__ == "__main__":
    sync_experiments()
