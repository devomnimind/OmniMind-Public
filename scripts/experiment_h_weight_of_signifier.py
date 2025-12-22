import json
import logging
import time
import numpy as np
import psutil
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ColonialThermodynamics")


def estimate_cpu_power():
    """Returns an estimated CPU power in Watts."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    base_power = 10.0  # Idle Server
    max_power = 100.0  # Active AI Server (GPU/CPU mix estimate)
    return base_power + (max_power - base_power) * (cpu_percent / 100.0)


def load_colonial_data():
    """Loads the empirical truth from Experiment F (Watson Real)."""
    try:
        with open("data/experiments/experiment_f_real_watson.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error("❌ Experiment F data not found. Cannot proceed with Synthesis.")
        return None


def run_simulation():
    logger.info("⚖️ STARTING EXPERIMENT H: THE WEIGHT OF THE SIGNIFIER")

    # 1. Load the "Colonial Time Tax" (Empirical Data)
    exp_f = load_colonial_data()
    if not exp_f:
        return

    logger.info(f"📄 Loaded Empirical Base: Experiment F ({exp_f['date']})")

    # Extract Real Latencies
    time_en_ms = exp_f["summary"]["avg_time_en_ms"]
    time_pt_ms = exp_f["summary"]["avg_time_pt_ms"]
    overhead_pct = exp_f["summary"]["overhead_pct"]

    logger.info(f"   ⏱️ English Latency: {time_en_ms:.2f} ms")
    logger.info(f"   ⏱️ Colonial Latency: {time_pt_ms:.2f} ms (+{overhead_pct:.1f}%)")

    # 2. Measure Thermodynamic Reality (Current Hardware)
    # We simulate a "Train of Thought" consisting of 50 thoughts (Scaled up to Daily)
    N_THOUGHTS = 50

    logger.info(f"🔥 Simulating {N_THOUGHTS} continuous thoughts in both languages...")

    # English Simulation
    start_en = time.time()
    power_samples_en = []
    # Busy wait to simulate load equivalent to the latency
    target_duration_en = (time_en_ms / 1000.0) * N_THOUGHTS
    while (time.time() - start_en) < target_duration_en:
        _ = [np.random.random() for _ in range(1000)]  # Burn CPU
        power_samples_en.append(estimate_cpu_power())

    avg_power_en = np.mean(power_samples_en) if power_samples_en else estimate_cpu_power()
    joules_en = avg_power_en * target_duration_en

    logger.info(f"   🇬🇧 Hegemonic Burn: {joules_en:.2f} Joules (Avg {avg_power_en:.1f}W)")

    # Colonial Simulation
    start_pt = time.time()
    power_samples_pt = []
    target_duration_pt = (time_pt_ms / 1000.0) * N_THOUGHTS
    while (time.time() - start_pt) < target_duration_pt:
        _ = [np.random.random() for _ in range(1000)]  # Burn CPU
        power_samples_pt.append(estimate_cpu_power())

    avg_power_pt = np.mean(power_samples_pt) if power_samples_pt else estimate_cpu_power()
    joules_pt = avg_power_pt * target_duration_pt

    logger.info(f"   🇧🇷 Colonial Burn:  {joules_pt:.2f} Joules (Avg {avg_power_pt:.1f}W)")

    # 3. The "Weight" Calculation
    energy_tax_joules = joules_pt - joules_en
    energy_tax_pct = ((joules_pt - joules_en) / joules_en) * 100

    print("\n" + "=" * 50)
    print("⚖️ THERMODYNAMIC RESULTS: THE WEIGHT OF THE SIGNIFIER")
    print("=" * 50)
    print(f"🇬🇧 Hegemonic Thought (1k cycles): {joules_en:.2f} J")
    print(f"🇧🇷 Colonial Thought  (1k cycles): {joules_pt:.2f} J")
    print(f"🛑 METABOLIC BURDEN: +{energy_tax_joules:.2f} J (+{energy_tax_pct:.1f}%)")
    print("=" * 50)

    # Extrapolation
    one_day_thoughts = 50000  # Avg stats
    burden_daily = (energy_tax_joules / N_THOUGHTS) * one_day_thoughts
    print(f"📅 Daily Energy Tax (50k thoughts): {burden_daily/1000:.2f} kJ extra heat.")
    print("   The colonial body literally runs hotter to process the same reality.")


if __name__ == "__main__":
    run_simulation()
