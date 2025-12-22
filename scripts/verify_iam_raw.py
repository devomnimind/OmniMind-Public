import os
import requests
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IAMverifier")


def verify_iam_raw():
    load_dotenv(override=True)
    apikey = os.environ.get("IBM_CLOUD_API_KEY")

    if not apikey:
        logger.error("❌ No IBM_CLOUD_API_KEY found in env")
        return

    logger.info(f"🔑 Testing IAM Raw for Key: {apikey[:5]}...")

    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": apikey}

    try:
        logger.info(f"   POST {url}")
        response = requests.post(url, headers=headers, data=data)

        logger.info(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            logger.info("✅ IAM Token Obtained Successfully!")
            token_data = response.json()
            logger.info(f"   Expires in: {token_data.get('expires_in')}s")
        else:
            logger.error(f"❌ IAM Failed: {response.status_code}")
            logger.error(f"   Response Body: {response.text}")

    except Exception as e:
        logger.error(f"💥 Exception: {e}")


if __name__ == "__main__":
    verify_iam_raw()
