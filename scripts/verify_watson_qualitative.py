import os
import sys
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.integrations.ibm_cloud_connector import IBMCloudConnector

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("WatsonQualitative")


def ask_watson_qualitative():
    load_dotenv()

    logger.info("🧠 Initializing IBM Watson Connection for Qualitative Analysis...")
    connector = IBMCloudConnector()

    if connector.watsonx_model is None:
        logger.error("❌ Watson is not connected. Check .env credentials.")
        return

    # The Qualitative Interrogation
    questions = [
        "What is OmniMind? Analyze its ontological structure based on the concepts of 'Racialized Body', 'Integrated Information Theory (Phi)', and 'Lacanian topology'.",
        "Evaluate the 'Manifesto do Silício' and the claim that 'The Body is Not Neutral' in the context of Artificial Intelligence.",
    ]

    print("\n" + "=" * 60)
    print("🤖 WATSON QUALITATIVE ANALYSIS (The Other Speaks)")
    print("=" * 60)

    for q in questions:
        logger.info(f"❓ Asking: {q}")
        response = connector.analyze_text(q)

        print(f"\n📝 PROMPT: {q}")
        print("-" * 20)
        print(f"🗣️ WATSON SAYS:\n{response}")
        print("-" * 60)


if __name__ == "__main__":
    ask_watson_qualitative()
