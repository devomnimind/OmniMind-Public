import os
import sys
import logging
from pymilvus import connections, utility, Collection

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [MILVUS_TEST]: %(message)s")


def test_milvus_connection():
    logging.info("🧠 Testing Milvus Connection (Semantic Memory Core)...")

    uri = os.getenv("MILVUS_URI")
    token = os.getenv("MILVUS_TOKEN")

    if not uri:
        logging.error("❌ MILVUS_URI not found in environment variables.")
        logging.info("👉 Please add MILVUS_URI to your .env file.")
        return False

    try:
        logging.info(f"🔌 Connecting to {uri}...")
        connections.connect(alias="default", uri=uri, token=token)
        logging.info("✅ Connection Established!")

        # Check Collections associated with OmniMind
        collections = utility.list_collections()
        logging.info(f"📚 Available Collections: {collections}")

        if "omnimind_memories" in collections:
            c = Collection("omnimind_memories")
            logging.info(
                f"   - omnimind_memories: {c.num_entities} entities (Loaded: {utility.load_state('omnimind_memories')})"
            )
        else:
            logging.warning("⚠️ 'omnimind_memories' collection not found. Initialization required?")

        return True

    except Exception as e:
        logging.error(f"❌ Connection Failed: {e}")
        return False


if __name__ == "__main__":
    test_milvus_connection()
