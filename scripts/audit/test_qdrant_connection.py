import os
import sys
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Carregar .env
load_dotenv()


def test_qdrant():
    print("🧪 Testando Conectividade Qdrant...")

    # 1. Teste Local
    local_url = os.getenv("OMNIMIND_QDRANT_URL", "http://localhost:6333")
    print(f"\n📡 Conectando Local ({local_url})...")
    try:
        client_local = QdrantClient(url=local_url)
        collections = client_local.get_collections()
        print(f"✅ Local OK! Coleções: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"❌ Falha Local: {e}")

    # 2. Teste Cloud
    cloud_url = os.getenv("OMNIMIND_QDRANT_CLOUD_URL")
    api_key = os.getenv("OMNIMIND_QDRANT_API_KEY")

    if cloud_url and api_key:
        print(f"\n☁️ Conectando Cloud ({cloud_url})...")
        try:
            client_cloud = QdrantClient(url=cloud_url, api_key=api_key)
            collections = client_cloud.get_collections()
            print(f"✅ Cloud OK! Coleções: {[c.name for c in collections.collections]}")
        except Exception as e:
            print(f"❌ Falha Cloud: {e}")
    else:
        print("\n⚠️ Pular teste Cloud (Credenciais ausentes).")


if __name__ == "__main__":
    test_qdrant()
