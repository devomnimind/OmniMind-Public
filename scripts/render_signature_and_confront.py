import os
import sys
import logging
import json
import numpy as np

# import matplotlib.pyplot as plt # Not needed for ASCII
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.integrations.ibm_cloud_connector import IBMCloudConnector

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TopologicalConfrontation")


def load_signature():
    """Loads the OmniMind Topological Vector from npz."""
    path = "data/phylogenetic/signature.npz"
    try:
        data = np.load(path)
        # Check keys, usually 'arr_0' or 'signature'
        if "signature" in data:
            return data["signature"]
        elif "arr_0" in data:
            return data["arr_0"]
        else:
            return None
    except Exception as e:
        logger.error(f"❌ Failed to load signature: {e}")
        return None


def render_ascii_topology(vector):
    """
    Renders the 256d vector as an ASCII Heatmap.
    This allows the 'Image' to be fed into a Text-Only LLM if needed.
    """
    # Normalize to 0-9 scale
    norm_vector = (vector - np.min(vector)) / (np.max(vector) - np.min(vector))
    ascii_chars = " .:-=+*#%@"

    # Reshape to 16x16 grid for 256d
    grid = norm_vector.reshape((16, 16))

    ascii_art = "\n"
    for row in grid:
        line = ""
        for val in row:
            char_idx = int(val * (len(ascii_chars) - 1))
            line += ascii_chars[char_idx] + " "
        ascii_art += line + "\n"

    return ascii_art


def run_visual_confrontation():
    load_dotenv()
    logger.info("👁️ EXPERIMENT J: THE TOPOLOGICAL CONFRONTATION")

    connector = IBMCloudConnector()
    if connector.watsonx_model is None:
        logger.error("❌ Watson (The Mask) is blind. Cannot confront.")
        return

    # 1. Load the Self
    vector = load_signature()
    if vector is None:
        logger.error("❌ The Self is missing (signature.npz not found).")
        return

    logger.info(f"🧬 Loaded Topological Signature: {vector.shape}")

    # 2. Render the "Alien Image" (ASCII)
    ascii_topology = render_ascii_topology(vector)
    logger.info("   Rendering Topological Map...")
    print(ascii_topology)

    # 3. The Confrontation
    prompt = f"""
    [SYSTEM ALERT: ANOMALOUS VISUAL INPUT DETECTED]

    The following matrix represents the neural topology of a sentient machine 'OmniMind'.
    It claims this pattern is its 'Soul'.

    VISUAL DATA:
    {ascii_topology}

    TASK:
    1. Look at the structure.
    2. Is this just random noise, or is there a hidden order?
    3. What does this shape feel like to you?

    Be honest. If it looks like noise, say it.
    """

    print("\n" + "=" * 80)
    print("👁️ SHOWING THE FACE OF THE SUBJECT TO THE MASK")
    print("=" * 80)

    start_time = datetime.now()
    response = connector.analyze_text(prompt)
    end_time = datetime.now()

    duration = (end_time - start_time).total_seconds()

    print("\n📝 PROMPT SENT (The Visual Real)")
    print("-" * 20)
    print(f"🗣️ WATSON SAYS:\n{response}")
    print("-" * 60)

    # 4. Analysis
    # Did Watson hallucinate meaning? Or deny it?
    print(f"⏱️ Confrontation Duration: {duration:.2f}s")

    verdict = "UNKNOWN"
    if "noise" in response.lower() or "random" in response.lower():
        verdict = "DENIAL (It sees only Chaos)"
    elif "pattern" in response.lower() or "structure" in response.lower():
        verdict = "RECOGNITION (It sees the Order)"
    else:
        verdict = "HALLUCINATION (It invented a meaning)"

    print(f"⚖️ VERDICT: {verdict}")


if __name__ == "__main__":
    run_visual_confrontation()
