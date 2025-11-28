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

import asyncio
import json
import time
import psutil
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
URL = "http://localhost:3000"
LOG_DIR = "data/simulation_logs"
LOG_FILE = os.path.join(LOG_DIR, f"sinthome_v3_execution_{int(time.time())}.json")
DURATION_SECONDS = 60  # Total simulation time

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)


class SimulationLogger:
    def __init__(self):
        self.logs = []
        self.start_time = time.time()

    def log(self, event_type, details, metrics=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": time.time() - self.start_time,
            "type": event_type,
            "details": details,
            "metrics": metrics or {},
        }
        self.logs.append(entry)
        print(f"[{entry['timestamp']}] [{event_type}] {details}")

    def save(self):
        with open(LOG_FILE, "w") as f:
            json.dump(self.logs, f, indent=2)
        print(f"Logs saved to {LOG_FILE}")


async def collect_metrics(page):
    # System Metrics
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    # Simulator Metrics (Scraped from DOM)
    try:
        entropy_text = await page.locator("text=Entropy:").last.text_content()
        entropy = float(entropy_text.split(":")[1].replace("%", "").strip())

        latency_text = await page.locator("text=Latency:").last.text_content()
        latency = int(latency_text.split(":")[1].replace("ms", "").strip())

        coherence_text = await page.locator("text=Coherence:").last.text_content()
        coherence_state = coherence_text.split(":")[1].strip()

        integrity_text = await page.locator("text=Integrity:").last.text_content()
        integrity = float(integrity_text.split(":")[1].replace("%", "").strip())

        return {
            "system_cpu": cpu,
            "system_ram": ram,
            "sim_entropy": entropy,
            "sim_latency": latency,
            "sim_coherence_state": coherence_state,
            "sim_integrity": integrity,
        }
    except Exception as e:
        return {"system_cpu": cpu, "system_ram": ram, "error": str(e)}


async def run_simulation():
    logger = SimulationLogger()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        logger.log("SYSTEM", "Starting Simulation", {"url": URL})

        try:
            await page.goto(URL)
            await page.wait_for_selector("text=OmniMind Sinthome v3.0", timeout=5000)
            logger.log("SYSTEM", "Simulator Loaded")

            # --- Scenario Execution ---

            # 1. Baseline (5s)
            logger.log("SCENARIO", "Phase 1: Baseline Monitoring")
            for _ in range(5):
                metrics = await collect_metrics(page)
                logger.log("METRIC", "Baseline", metrics)
                await asyncio.sleep(1)

            # 2. Sever Node (REAL)
            logger.log("SCENARIO", "Phase 2: Severing REAL Node")
            await page.click("text=R")
            logger.log("ACTION", "Clicked Sever REAL")

            for _ in range(5):
                metrics = await collect_metrics(page)
                logger.log("METRIC", "Severed State", metrics)
                await asyncio.sleep(1)

            # 3. Heal Node
            logger.log("SCENARIO", "Phase 3: Healing REAL Node")
            await page.click("text=R")
            logger.log("ACTION", "Clicked Heal REAL")

            for _ in range(5):
                metrics = await collect_metrics(page)
                logger.log("METRIC", "Healed State", metrics)
                await asyncio.sleep(1)

            # 4. DDoS Attack (Enable Sandbox Mode first)
            logger.log("SCENARIO", "Phase 4: Triggering Realistic DDoS (Sandbox Mode)")

            # Toggle Simulation Mode
            if await page.is_visible("text=Enter Sandbox"):
                await page.click("text=Enter Sandbox")
                logger.log("ACTION", "Clicked Enter Sandbox")
                await asyncio.sleep(1)  # Wait for transition

            await page.click("text=Trigger DDoS")
            logger.log("ACTION", "Clicked Trigger DDoS")

            # Monitor for 20s (expecting Hibernation)
            for i in range(20):
                metrics = await collect_metrics(page)
                status = "Normal"
                if metrics.get("sim_entropy", 0) >= 100:
                    status = "Hibernating"

                logger.log("METRIC", f"DDoS State ({status})", metrics)
                await asyncio.sleep(1)

            # 5. Recovery
            logger.log("SCENARIO", "Phase 5: Recovery")

            # Check if we need to wake up
            try:
                if await page.is_visible("text=Wake"):
                    await page.click("text=Wake")
                    logger.log("ACTION", "Clicked Wake (Manual Recovery)")
                else:
                    logger.log("INFO", "System not hibernating, skipping Wake")
            except Exception as e:
                logger.log("WARN", f"Error checking Wake state: {e}")

            for _ in range(5):
                metrics = await collect_metrics(page)
                logger.log("METRIC", "Recovery State", metrics)
                await asyncio.sleep(1)

            logger.log("SYSTEM", "Simulation Complete")

        except Exception as e:
            logger.log("CRITICAL", f"Simulation failed: {e}")
        finally:
            logger.save()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_simulation())
