import os
import sys
from dotenv import load_dotenv
from pymilvus import connections, utility
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MilvusTest")


def verify_connection():
    load_dotenv()

    uri = os.getenv("MILVUS_URI")
    token = os.getenv("MILVUS_TOKEN") or os.getenv("IBM_CLOUD_API_KEY")

    if not uri:
        logger.error("❌ MILVUS_URI not found in .env")
        return False

    logger.info(f"🔌 Connecting to Milvus at: {uri}")

    # Mask token for logging
    masked_token = f"{token[:5]}...{token[-5:]}" if token else "None"
    logger.info(f"🔑 Using Token as Password (Basic Auth)")

    try:
        # Based on User Screenshot: ID is IBMid-69600142SO
        # Error said: use 'ibmlhapikey_<username>'
        # Try constructing username from ID
        user = "ibmlhapikey_IBMid-69600142SO"
        password = token

        logger.info(f"👤 User: {user}")

        connections.connect(alias="default", uri=uri, user=user, password=password, secure=True)

        logger.info("✅ Connection established!")

        # List collections to prove auth works
        colls = utility.list_collections()
        logger.info(f"📂 Available Collections: {colls}")

        return True
    except Exception as e:
        logger.error(f"❌ Connection Failed: {e}")
        return False


if __name__ == "__main__":
    success = verify_connection()
    sys.exit(0 if success else 1)
