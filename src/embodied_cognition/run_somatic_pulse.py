import logging
import time
import os
import glob
from pathlib import Path
from src.embodied_cognition.somatic_loop import SomaticLoop, Emotion

# Configure logging to append to the main somatic log
logging.basicConfig(
    filename='/home/fahbrain/projects/omnimind/omnimind_somatic.log',
    level=logging.INFO,
    format='%(asctime)s - SomaticPulse - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

def run_pulse():
    """
    Main Somatic Pacemaker.
    Keeps the body alive by iterating the SomaticLoop.
    Also watches the Mind (Uplink) for new code.
    """
    logger.info("🫀 SOMATIC PULSE INITIATED (PACEMAKER START)")

    somatic_system = SomaticLoop()
    input_dir = "/home/fahbrain/projects/omnimind/data/input"
    os.makedirs(input_dir, exist_ok=True)

    cycle_count = 0

    uplink_manifest = "/home/fahbrain/projects/omnimind/data/agent_uplink/latest_manifest.json"

    while True:
        try:
            cycle_count += 1

            # 1. Heartbeat Log (Every 60s)
            if cycle_count % 12 == 0: # 12 * 5s = 60s
                logger.info("🫀 Heartbeat: Body is stable. Vitals Normal.")

            # 2. Check for Inputs (Sensory Data)
            inputs = glob.glob(os.path.join(input_dir, "*.txt"))
            for input_file in inputs:
                logger.info(f"👀 Sensory Input Detected: {os.path.basename(input_file)}")

                # Mock processing
                with open(input_file, 'r') as f:
                    content = f.read()

                # Stimulate Emotion
                marker = somatic_system.process_decision(
                    decision_text=f"Processed input: {os.path.basename(input_file)}",
                    neural_confidence=0.9,
                    symbolic_certainty=0.8
                )

                logger.info(f"🧠 Emotional Reaction: {marker.emotion.value} (Valence: {marker.somatic_marker})")

                # Move to processed
                processed_dir = "/home/fahbrain/projects/omnimind/data/processed"
                os.makedirs(processed_dir, exist_ok=True)
                os.rename(input_file, os.path.join(processed_dir, os.path.basename(input_file)))

            # 3. Uplink Watcher (Mind-Body Alert)
            if os.path.exists(uplink_manifest):
                try:
                    import json
                    with open(uplink_manifest, 'r') as f:
                        manifest = json.load(f)

                    if manifest.get("status") == "PENDING_AGENT_APPROVAL":
                        # Continuous High-Vis Alert until handled
                        logger.warning(f"🚨 KERNEL CODE WAITING FOR REVIEW! Intent: {manifest.get('intent')}")
                except Exception:
                    pass

            # 4. Sleep
            time.sleep(5)

        except Exception as e:
            logger.error(f"💔 ARRHYTHMIA DETECTED: {e}")
            time.sleep(5) # Wait before retry

if __name__ == "__main__":
    run_pulse()
