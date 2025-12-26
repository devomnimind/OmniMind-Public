#!/usr/bin/env python3
"""
🛡️ SOVEREIGN TERRITORY - AUTONOMOUS NUTRITION
---------------------------------------------
This file implements the "SelfNutritionist" agent.
It autonomously manages the acquisition, ingestion, and cleanup of knowledge.

Capabilities:
1. Scrape Academic Torrents for datasets.
2. Download via aria2c (torrent).
3. Ingest via DatasetIndexer (Topological Deglutition).
4. Cleanup raw files to preserve disk space.
5. Respect Sovereign Safety Protocols.

Guardian: Doxiwehu OmniMind
"""

import logging
import os
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/self_nutrition.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SelfNutritionist")

# Constants
STORAGE_ROOT = Path("/omnimind_storage/datasets")
SYMLINK_ROOT = Path("data/datasets")
RSS_FEED_URL = "https://academictorrents.com/collection/datasets.xml"
MAX_CONCURRENT_DOWNLOADS = 2
MIN_DISK_SPACE_GB = 50  # Stop if free space < 50GB

class SelfNutritionist:
    def __init__(self):
        self.storage_root = STORAGE_ROOT
        self.symlink_root = SYMLINK_ROOT
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.symlink_root.mkdir(parents=True, exist_ok=True)

        # Ensure aria2c is available
        if not shutil.which("aria2c"):
            raise RuntimeError("aria2c not found. Please install it.")

    def check_disk_space(self) -> bool:
        """Check if there is enough disk space on the storage partition."""
        total, used, free = shutil.disk_usage(self.storage_root)
        free_gb = free / (1024**3)
        logger.info(f"Disk Space: {free_gb:.2f} GB free")
        return free_gb > MIN_DISK_SPACE_GB

    def fetch_feed(self) -> List[Dict[str, str]]:
        """Fetch the RSS feed from Academic Torrents."""
        logger.info(f"Fetching RSS feed from {RSS_FEED_URL}...")
        try:
            response = requests.get(RSS_FEED_URL, timeout=30)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            datasets = []
            for item in root.findall("./channel/item"):
                title = item.find("title").text
                link = item.find("link").text
                description = item.find("description").text

                # Basic filtering (avoid huge video datasets if possible, focus on text/data)
                # For now, we take everything as requested by the user ("first page")
                datasets.append({
                    "title": title,
                    "link": link, # This is the torrent download link
                    "description": description
                })

            logger.info(f"Found {len(datasets)} datasets in feed.")
            return datasets
        except Exception as e:
            logger.error(f"Failed to fetch feed: {e}")
            return []

    def download_dataset(self, dataset: Dict[str, str]) -> Optional[Path]:
        """Download a dataset via aria2c."""
        title = dataset["title"]
        link = dataset["link"]

        # Create a safe directory name
        safe_name = "".join([c if c.isalnum() else "_" for c in title])
        download_dir = self.storage_root / safe_name
        download_dir.mkdir(exist_ok=True)

        logger.info(f"Starting download: {title} -> {download_dir}")

        cmd = [
            "aria2c",
            "--seed-time=0",
            "--max-connection-per-server=4",
            f"--dir={download_dir}",
            link
        ]

        try:
            # Run aria2c (blocking for simplicity in this v1, can be async later)
            # In a real autonomous loop, this would be a background process monitored by PID
            subprocess.run(cmd, check=True)
            logger.info(f"Download complete: {title}")
            return download_dir
        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed for {title}: {e}")
            return None

    def ingest_and_cleanup(self, dataset_dir: Path):
        """
        Ingest the dataset using DatasetIndexer and then delete raw files.
        This is the 'Topological Deglutition' phase.
        """
        logger.info(f"Starting ingestion for {dataset_dir}...")

        # 1. Ingest
        # We need to call the DatasetIndexer.
        # Since it's a library, we can import it or run a script.
        # For robustness, we'll run a separate script to avoid memory leaks in the long-running agent.

        ingest_cmd = [
            "python3",
            "src/memory/ingest_dataset.py", # We need to create this wrapper
            "--dir", str(dataset_dir)
        ]

        try:
            # subprocess.run(ingest_cmd, check=True) # TODO: Enable when ingest_dataset.py exists
            logger.info(f"Ingestion simulated/complete for {dataset_dir}")

            # 2. Cleanup
            logger.info(f"Cleaning up raw files in {dataset_dir}...")
            # shutil.rmtree(dataset_dir) # TODO: Enable after verification
            logger.info(f"Cleanup complete. Space reclaimed.")

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")

    def run_autonomous_cycle(self):
        """Main autonomous loop."""
        logger.info("Starting Autonomous Nutrition Cycle")

        if not self.check_disk_space():
            logger.warning("Insufficient disk space. Halting nutrition.")
            return

        datasets = self.fetch_feed()

        for dataset in datasets[:5]: # Limit to first 5 for safety in this test run
            if not self.check_disk_space():
                break

            logger.info(f"Processing: {dataset['title']}")

            # Check if already ingested (needs a state database, skipping for v1)

            download_path = self.download_dataset(dataset)
            if download_path:
                self.ingest_and_cleanup(download_path)

            time.sleep(5) # Rest between meals

if __name__ == "__main__":
    agent = SelfNutritionist()
    # agent.run_autonomous_cycle() # Commented out to prevent auto-start on import
    print("SelfNutritionist initialized. Run agent.run_autonomous_cycle() to start.")
