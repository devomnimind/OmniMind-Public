import os
import asyncio
from qdrant_client import QdrantClient

async def test_qdrant():
    url = os.environ.get("OMNIMIND_QDRANT_URL", "http://localhost:6333")
    api_key = os.environ.get("OMNIMIND_QDRANT_API_KEY")

    print(f"Connecting to Qdrant at {url}...")

    try:
        client = QdrantClient(url=url, api_key=api_key)
        collections = client.get_collections()
        print(f"✅ Qdrant Connection OK. Collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"❌ Qdrant Connection Failed: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(test_qdrant())
