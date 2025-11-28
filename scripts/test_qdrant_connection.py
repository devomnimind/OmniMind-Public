"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

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
