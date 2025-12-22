import os
import logging
from ibm_watson_machine_learning.foundation_models import Model
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WatsonxTest")

load_dotenv()

project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
url = os.getenv("IBM_WATSONX_URL", "https://au-syd.ml.cloud.ibm.com")

keys = {
    "IBM_CLOUD_API_KEY (Line 108)": os.getenv("IBM_CLOUD_API_KEY"),
    "VERSAO_2_IBM_API_KEY (Quantum)": os.getenv("VERSAO_2_IBM_API_KEY"),
}

for name, api_key in keys.items():
    if not api_key:
        logger.warning(f"Skipping {name} (Not found)")
        continue

    logger.info(f"--- Testing {name} ---")
    creds = {"url": url, "apikey": api_key}
    try:
        model = Model(
            model_id="ibm/granite-13b-chat-v2",
            credentials=creds,
            project_id=project_id,
        )
        res = model.generate_text(prompt="Test")
        logger.info(f"SUCCESS with {name}!")
    except Exception as e:
        logger.error(f"FAILED with {name}: {e}")
