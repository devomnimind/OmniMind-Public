import sys
import os
import logging
from ibm_watson_machine_learning import APIClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WatsonxDebug")


import requests


def get_iam_token(apikey):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": apikey}
    try:
        res = requests.post(url, headers=headers, data=data)
        if res.status_code == 200:
            return res.json()["access_token"]
        else:
            logger.error(f"❌ Manual IAM Fail: {res.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Maunal IAM Error: {e}")
        return None


def debug_direct():
    url = os.environ.get("IBM_WATSONX_URL")
    project_id = os.environ.get("IBM_WATSONX_PROJECT_ID")
    apikey = os.environ.get("IBM_CLOUD_API_KEY")

    if not url or not apikey:
        logger.error("❌ Missing params")
        return

    logger.info(f"🔍 DEBUGGING WML - HYBRID AUTH MODE")
    logger.info(f"   URL: {url}")

    # 1. Fetch Token Manually
    logger.info("   1. Fetching IAM Token manually...")
    token = get_iam_token(apikey)

    if not token:
        logger.error("   ❌ Failed to get token manually.")
        return
    logger.info("   ✅ Token obtained.")

    # 2. Init Client with Token
    creds = {
        "url": url,
        "token": token,
        "instance_id": "openshift",  # Bylaws for CP4D interaction often require this dummy
        "version": "4.8",  # Dummy version to force proper logic path if needed
    }
    # Note: For Cloud, usually just url/token is enough. Let's try minimal first.
    creds = {"url": url, "token": token}

    try:
        logger.info("   2. Instantiating APIClient with Token...")
        client = APIClient(creds)
        logger.info("   ✅ APIClient instantiated.")

        logger.info(f"   3. Setting Project {project_id}...")
        client.set.default_project(project_id)

        # logger.info("   3. Listing Projects to verify access scope...")
        # try:
        #    client.projects.list(limit=5)
        #    logger.info("   ✅ Listing Projects Succeeded.")
        # except Exception as e_list:
        #    logger.error(f"   ❌ Listing Projects Failed: {e_list}")

        details = client.service_instance.get_details()
        logger.info(f"   ✅ SUCCESS! Service Name: {details.get('entity', {}).get('name')}")

    except Exception as e:
        logger.error(f"💥 CLIENT FAIL: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"   Response Text: {e.response.text}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(override=True)
    debug_direct()
